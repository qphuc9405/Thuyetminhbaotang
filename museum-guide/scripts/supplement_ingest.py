"""Nạp ĐỢT BỔ SUNG NGUỒN (3 bài viết + Archive_4.zip) vào KB đang có — gọi từ build_knowledge_base.py.

Không thay đổi/không xoá dữ liệu cũ: chỉ THÊM nguồn, chunk, ảnh, sự kiện, quan hệ; với ảnh cũ trùng lặp chỉ gán thêm
nhóm trùng (duplicate_group) và quan hệ.
"""
from __future__ import annotations

import hashlib
import re
import unicodedata
from pathlib import Path

import imagehash
from PIL import Image as PILImage

import curation_supplement as CS
from app.database import models as M
from app.services.glossary import GLOSSARY
from app.services.text_utils import fold

MAX_CHARS = 900
_SENT = re.compile(r"(?<=[.!?…”\"])\s+(?=[A-ZÀ-Ỵ“\"(])")


def nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s)


def _split_long(text: str, max_chars: int = MAX_CHARS) -> list[str]:
    if len(text) <= max_chars:
        return [text]
    sents, out, cur = _SENT.split(text), [], ""
    for s in sents:
        if cur and len(cur) + 1 + len(s) > max_chars:
            out.append(cur); cur = s
        else:
            cur = f"{cur} {s}".strip()
    if cur:
        out.append(cur)
    return out


def parse_doc(root: Path, src: str, fname: str, headings: dict, caption_lines: set) -> list[dict]:
    """Chunk theo đoạn (mỗi dòng không rỗng = 1 đoạn), gộp tới ~900 ký tự trong cùng mục; đoạn dài cắt theo câu.
    Chú thích ảnh giữ lại dưới dạng '[Chú thích ảnh trong bài: …]' trong chunk kế tiếp. Mỗi chunk lưu dải số dòng gốc."""
    lines = (root / CS.DOC_DIR / fname).read_text(encoding="utf-8").splitlines()
    heading = None
    units: list[tuple[int, int, str, str, bool]] = []  # (line_a, line_b, heading, text, is_caption)
    i = 0
    while i < len(lines):
        ln, raw = i + 1, lines[i].strip()
        if not raw:
            i += 1; continue
        if ln in headings:
            heading = headings[ln]
            if len(raw) < 120:  # dòng tiêu đề: giữ văn bản gốc làm dòng đầu của đoạn kế tiếp
                units.append((ln, ln, heading, raw, False)); i += 1; continue
        if ln in caption_lines:
            a, txt = ln, raw
            while i + 1 < len(lines) and (i + 2) in caption_lines and lines[i + 1].strip():  # chú thích nhiều dòng
                i += 1; txt += " " + lines[i].strip()
            units.append((a, i + 1, heading, f"[Chú thích ảnh trong bài: {txt}]", True)); i += 1; continue
        units.append((ln, ln, heading, raw, False)); i += 1
    chunks, cur = [], None

    def flush():
        nonlocal cur
        if cur and cur["units"]:
            chunks.append(cur)
        cur = None

    for u in units:
        a, b, h, text, is_cap = u
        if len(text) > MAX_CHARS:
            flush()
            for k, piece in enumerate(_split_long(text)):
                chunks.append({"units": [(a, b, h, piece, False)], "heading": h, "part": k + 1})
            continue
        if is_cap or cur is None or cur["heading"] != h or len(cur["text"]) + len(text) + 2 > MAX_CHARS:
            flush(); cur = {"units": [], "heading": h, "text": "", "part": None}
        cur["units"].append(u); cur["text"] = (cur["text"] + "\n" + text).strip()
    flush()
    out = []
    for c in chunks:
        a, b = c["units"][0][0], c["units"][-1][1]
        text = "\n".join(u[3] for u in c["units"])
        cid = f"{src}-L{a:03d}" + (f"-{c['part']}" if c["part"] else "")
        caps = [(u[0], u[1], u[3]) for u in c["units"] if u[4]]
        out.append(dict(chunk_id=cid, line_a=a, line_b=b, heading=c["heading"], text=text, captions=caps))
    return out


def add_supplement(s, *, root: Path, page_text: dict, book_chunks: list, report: dict, context_by_topic: dict, squash) -> dict:
    stats: dict = {}
    src_by_id = {d["source_id"]: d for d in CS.SOURCES}
    for d in CS.SOURCES:
        s.add(M.Source(**d))
    s.flush()

    # ---------- 1) tài liệu text → chunk có vị trí dòng
    line_to_chunk: dict[tuple[str, int], str] = {}
    caption_to_chunk: dict[tuple[str, int], str] = {}
    doc_rows: dict[str, M.Chunk] = {}
    n_doc = {}
    for src, fname, headings, caps in CS.DOCS:
        sd = src_by_id[src]
        specs = parse_doc(root, src, fname, headings, caps)
        n_doc[src] = len(specs)
        for c in specs:
            folded = fold(c["text"])
            kws = [vi[0] for key, vi, en, zh in GLOSSARY if any(fold(t) in folded for t in vi if len(t) > 3)][:8]
            row = M.Chunk(chunk_id=c["chunk_id"], source_id=src, source_title=sd["title"], source_type=sd["source_type"], language="vi",
                          title=(c["heading"] or sd["title"])[:200], category="supplement_article", chapter_id=None, chapter=None, section=c["heading"],
                          provision=f"dòng {c['line_a']}" + (f"–{c['line_b']}" if c["line_b"] != c["line_a"] else ""), content=c["text"], folded=folded,
                          event_date=None, image_ids=[], keywords=kws, confidence="medium", verification_status="secondary_unverified",
                          needs_review=False, config_id=f"supp_para{MAX_CHARS}")
            s.add(row); doc_rows[row.chunk_id] = row
            for ln in range(c["line_a"], c["line_b"] + 1):
                line_to_chunk.setdefault((src, ln), row.chunk_id)
            for a, b, _ in c["captions"]:
                for ln in range(a, b + 1):
                    caption_to_chunk[(src, ln)] = row.chunk_id
    s.flush()
    stats["doc_chunks"] = n_doc

    def book_chunk_for(page: int):
        for c in book_chunks:
            if c.printed_page <= page <= (c.printed_page_end or c.printed_page):
                return c.chunk_id
        return None

    def loc_chunk(src, page, line):
        if src.startswith("WX"):
            return src
        return book_chunk_for(page) if src == "SRC001" else line_to_chunk.get((src, line))

    # ---------- 1b) nguồn web: bản ghi diễn giải ngắn (không chép nguyên văn)
    import curation_exhibits as CE
    import curation_topics as CT
    for d in CS.WEB_SOURCES + CE.WEB_SOURCES_2 + CT.WEB_SOURCES_3:
        s.add(M.Source(**d))
    s.flush()
    wsrc = {d["source_id"]: d for d in CS.WEB_SOURCES}
    for cid, sid, title, content in CS.WEB_RECORDS:
        sd = wsrc[sid]
        s.add(M.Chunk(chunk_id=cid, source_id=sid, source_title=sd["title"], source_type="WEB_ARTICLE", language="vi", title=title, category="web_article",
                      chapter_id=None, chapter=None, section=None, provision=f"{sd['publisher']}, {sd['document_date']}", content=content, folded=fold(content),
                      event_date=None, image_ids=[], keywords=[], confidence="medium", verification_status=sd["verification_status"], needs_review=False, config_id="web_paraphrase"))
    s.flush()
    stats["web_records"] = len(CS.WEB_RECORDS)

    # ---------- 2) ghi chú đối chiếu nguồn (xung đột) → bản ghi + quan hệ
    note_src = src_by_id["NOTE01"]
    for nid, title, content, locs, ev in CS.CONFLICTS:
        s.add(M.Chunk(chunk_id=nid, source_id="NOTE01", source_title=note_src["title"], source_type="CURATOR_NOTE", language="vi", title=title,
                      category="source_discrepancy", chapter_id=None, chapter=None, section=None, provision="ghi chú đối chiếu", content=content, folded=fold(content),
                      event_date=None, image_ids=[], keywords=["đối chiếu nguồn"], confidence="medium", verification_status="cross_checked_against_ocr_and_text",
                      needs_review=False, config_id="curator_note"))
        seen = set()
        for src, page, line in locs:
            # kiểm tra số dòng/trang trích dẫn tồn tại thật
            if src == "SRC001" and not page_text.get(page):
                report["warnings"].append(f"{nid}: trang in {page} không có OCR")
            cid = loc_chunk(src, page, line)
            if cid is None:
                report["warnings"].append(f"{nid}: không tìm thấy chunk cho {src} {page or ''}{line or ''}")
                continue
            if cid in seen:
                continue
            seen.add(cid)
            s.add(M.Relation(from_type="chunk", from_id=nid, to_type="chunk", to_id=cid, relation="compares_source",
                             basis=(f"trang in {page}" if page else f"{src} dòng {line}"), confidence="high"))
        if ev:
            s.add(M.Relation(from_type="chunk", from_id=nid, to_type="event", to_id=ev, relation="discusses_discrepancy", basis="đối chiếu niên đại/số liệu", confidence="high"))
    stats["conflict_notes"] = len(CS.CONFLICTS)

    # ---------- 3) sự kiện mới (chỉ trong 1954–1967)
    import curation_kb as CK
    for (eid, date_iso, label, vi, en, zh, svi, sen, page, anchor, topics) in CS.EVENTS_BOOK:
        txt = page_text.get(page, "")
        ok = squash(anchor) in squash(txt)
        flat = " ".join(txt.split()); idx = flat.find(anchor)
        snippet = flat[max(0, idx - 80): idx + 220] if ok and idx >= 0 else ""
        if not ok:
            report["warnings"].append(f"{eid}: anchor '{anchor}' không tìm thấy ở trang in {page}")
        s.add(M.Event(event_id=eid, date_iso=date_iso, date_label=label, title_vi=vi, title_en=en, title_zh=zh, summary_vi=svi, summary_en=sen,
                      period=CK.period_of(date_iso), source_id="SRC001", printed_page=page, evidence_snippet=snippet,
                      verification_status="anchor_verified_in_ocr" if ok else "anchor_not_found", topic_ids=topics))
        bc = book_chunk_for(page)
        if bc:
            s.add(M.Relation(from_type="event", from_id=eid, to_type="chunk", to_id=bc, relation="evidenced_by", basis=f"trang in {page}", confidence="high"))
        for t in topics:
            s.add(M.Relation(from_type="event", from_id=eid, to_type="topic", to_id=t, relation="belongs_to", basis="biên soạn theo chương", confidence="high"))
    for (eid, date_iso, label, vi, en, zh, svi, sen, src, prov, topics, evid) in CS.EVENTS_SUPP:
        first = line_to_chunk.get(evid[0])
        snippet = doc_rows[first].content[:260] if first else ""
        s.add(M.Event(event_id=eid, date_iso=date_iso, date_label=label, title_vi=vi, title_en=en, title_zh=zh, summary_vi=svi, summary_en=sen,
                      period=CK.period_of(date_iso), source_id=src, printed_page=None, provision=prov, evidence_snippet=snippet,
                      verification_status="secondary_sources_agree_unverified", topic_ids=topics))
        for (es, ln) in evid:
            cid = line_to_chunk.get((es, ln))
            if cid:
                s.add(M.Relation(from_type="event", from_id=eid, to_type="chunk", to_id=cid, relation="evidenced_by", basis=f"{es} dòng {ln}", confidence="medium"))
        for t in topics:
            s.add(M.Relation(from_type="event", from_id=eid, to_type="topic", to_id=t, relation="belongs_to", basis="biên soạn theo chủ đề", confidence="medium"))
    s.flush()
    stats["events_added"] = len(CS.EVENTS_BOOK) + len(CS.EVENTS_SUPP)

    # ---------- 4) ảnh Archive_4
    img_dir = root / CS.IMG_DIR
    files = {nfc(p.name): p for p in img_dir.iterdir() if p.is_file()}
    assert len(files) == len(CS.IMAGES) == 16, (len(files), len(CS.IMAGES))
    added = []
    for cur in CS.IMAGES:
        p = files[cur["key"]]
        b = p.read_bytes()
        with PILImage.open(p) as im:
            w, h, fmt = im.size[0], im.size[1], im.format
            ph = str(imagehash.phash(im.convert("RGB")))
        cap_text, cap_status, cap_src = None, None, cur.get("caption")
        if cap_src:
            src, lns = cap_src
            raw = (root / CS.DOC_DIR / next(f for sid, f, *_ in CS.DOCS if sid == src)).read_text(encoding="utf-8").splitlines()
            cap_text = " ".join(raw[ln - 1].strip() for ln in lns)
            # kiểm tra: chú thích trong bài trùng tên file (bỏ dấu câu/khoảng trắng)
            same = squash(cap_text).rstrip(".") == squash(cur["key"].rsplit(".", 1)[0]).rstrip(".")
            if not same:
                report["warnings"].append(f"{cur['id']}: chú thích {src} dòng {lns} không trùng tên file")
            cap_status = f"document_caption:{src}:dòng {'-'.join(map(str, lns))}" + (":matches_filename" if same else "")
        topics = cur["topics"]
        ctx_parts = []
        if cap_src:
            ctx_parts.append(f"Ảnh có chú thích trong bài {cap_src[0]} ({src_by_id[cap_src[0]]['author']}, dòng {', '.join(map(str, cap_src[1]))}): \"{cap_text}\" – chú thích của một bài báo thứ cấp, chưa đối chiếu hồ sơ gốc của ảnh.")
        ctx_parts += [context_by_topic[t] for t in topics if t in context_by_topic]
        ctx_parts.append(cur["notes"])
        ctx = " ".join(ctx_parts)
        wm = cur.get("wm", [])
        kws = sorted(set([CS.TOPIC_LABELS_EXTRA.get(t, t) for t in topics]) | set(cur["objects"]) | set(v for v in cur["visible_text"][:3] if len(v) < 60))
        basis = {"title": "filename", "fn_title": "filename", "visual_description": "visual_inspection", "visible_text": "visual_inspection",
                 "location": "document_caption+filename" if cap_src else "filename", "time_period": "document_caption+filename" if cap_src else "filename_or_visual",
                 "people_description": "visual_inspection (không nhận dạng người)", "topics": "filename+visual_inspection", "historical_context": "book/doc passages on the topic (không phải xác minh ảnh)"}
        slug_words = re.sub(r"[_\-]+", " ", cur["key"].rsplit(".", 1)[0])
        search_text = fold(" ".join([cur["fn_title"], slug_words, *cur["title"], cur["visual"], " ".join(cur["visible_text"]), " ".join(cur["objects"]), " ".join(kws), cap_text or "", ctx]))
        source = f"Archive_4.zip (nguồn gốc ảnh chưa xác định)" + (f"; có chú thích ảnh trong bài {cap_src[0]}" if cap_src else "") + ("; " + "; ".join(wm) if wm else "")
        row = M.Image(image_id=cur["id"], kind=cur["kind"], source_id="SRC006", filename=p.name, image_path=str(p.relative_to(root)), filename_title=cur["fn_title"],
                      metadata_basis=basis, title=cur["title"][0], title_en=cur["title"][1], title_zh=cur["title"][2], visual_description=cur["visual"],
                      historical_context=ctx, location=cur["location"], location_confidence=cur["loc_conf"], time_period=cur["time_period"], estimated_date="Chưa xác định",
                      main_objects=cur["objects"], visible_text=cur["visible_text"], people_description=cur["people"], historical_significance="Chưa xác định",
                      related_events=[e for e, _, _ in cur["events"]], related_book_topics=topics,
                      related_book_pages=[dict(start=a, end=b2, link_type=lt) for a, b2, lt in cur["book_pages"]], keywords=kws, source=source, watermarks=wm,
                      rights_status="Chưa xác định", confidence_level=cur["conf"], verification_notes=cur["notes"], duplicate_group=None, similar_scene_group=None,
                      sha256=hashlib.sha256(b).hexdigest(), phash=ph, width=w, height=h, file_format=fmt, caption=cap_text, caption_status=cap_status,
                      in_gallery=True, search_text=search_text)
        s.add(row); added.append(row)
    s.flush()

    # quan hệ ảnh mới: chú thích trong bài, sự kiện, trùng/cùng cảnh với ảnh cũ
    n_rel = 0
    for cur in CS.IMAGES:
        iid = cur["id"]
        if cur.get("caption"):
            src, lns = cur["caption"]
            cid = caption_to_chunk.get((src, lns[0]))
            if cid:
                s.add(M.Relation(from_type="image", from_id=iid, to_type="chunk", to_id=cid, relation="captioned_in_document",
                                 basis="document_caption", confidence="medium")); n_rel += 1
                ch = s.get(M.Chunk, cid)
                ch.image_ids = list(ch.image_ids or []) + [iid]
                # ảnh trong bài nằm GIỮA hai đoạn: không biết chắc minh hoạ đoạn trước hay sau -> nối cả hai (độ tin cậy thấp)
                prev = next((line_to_chunk[(src, l)] for l in range(lns[0] - 1, 0, -1) if (src, l) in line_to_chunk and line_to_chunk[(src, l)] != cid), None)
                nxt = line_to_chunk.get((src, lns[-1] + 2))
                for adj, side in ((prev, "trước"), (nxt, "sau")):
                    if adj and adj != cid:
                        s.add(M.Relation(from_type="image", from_id=iid, to_type="chunk", to_id=adj, relation="adjacent_text_in_document",
                                         basis=f"document_caption_adjacent (đoạn {side} chú thích)", confidence="low")); n_rel += 1
            else:
                report["warnings"].append(f"{iid}: không tìm thấy chunk chứa chú thích {src} dòng {lns}")
        for src, ln, basis in cur.get("doc_links", []):
            cids = [cid for (s2, l2), cid in line_to_chunk.items() if s2 == src and l2 == ln]
            if not cids:
                report["warnings"].append(f"{iid}: không có chunk cho {src} dòng {ln}"); continue
            s.add(M.Relation(from_type="image", from_id=iid, to_type="chunk", to_id=cids[0], relation="topic_corroborated_by_document",
                             basis=f"{src} dòng {ln}: {basis}", confidence="low")); n_rel += 1
        for eid, rel, basis in cur["events"]:
            s.add(M.Relation(from_type="image", from_id=iid, to_type="event", to_id=eid, relation=rel, basis=basis, confidence="low")); n_rel += 1
        if cur.get("dup_of"):
            other, rel, basis = cur["dup_of"]
            s.add(M.Relation(from_type="image", from_id=iid, to_type="image", to_id=other, relation=rel, basis=basis, confidence="high" if rel.startswith("variant") else "medium")); n_rel += 1
            if rel.startswith("variant"):
                g = f"DUP-S{other[3:]}"
                for x in (iid, other):
                    r = s.get(M.Image, x); r.duplicate_group = r.duplicate_group or g
        for other, rel, basis in cur.get("scene_with", []):
            s.add(M.Relation(from_type="image", from_id=iid, to_type="image", to_id=other, relation=rel, basis=basis, confidence="medium" if "SIFT" in basis else "low")); n_rel += 1
    # Archive 3.zip lồng bên trong: 10 bản trùng byte – ghi nhận trong báo cáo (không tạo bản ghi trùng)
    stats.update(images_added=len(added), image_relations_added=n_rel, nested_archive3_duplicates=10, macosx_skipped=16)
    s.flush()
    return stats


def build_anecdotes(*, root: Path, page_text: dict, squash, report: dict, sources: dict) -> list[dict]:
    """Mục "Những mẩu chuyện thú vị": kiểm tra anchor từng trích dẫn (OCR trang in / đúng dòng tệp gốc) rồi xuất JSON."""
    import curation_anecdotes as CA
    doc_lines = {sid: (root / CS.DOC_DIR / f).read_text(encoding="utf-8").splitlines() for sid, f, *_ in CS.DOCS}
    web_rec = {sid: cid for cid, sid, *_ in CS.WEB_RECORDS}
    out = []
    for a in CA.ANECDOTES:
        cites = []
        for src, page, line, anchor in a["cites"]:
            sd = sources[src]
            if src == "SRC001":
                ok = squash(anchor) in squash(page_text.get(page, ""))
                c = {"printed_page": page, "provision": None}
            elif src in doc_lines:
                ok = squash(anchor) in squash(doc_lines[src][line - 1]) if 0 < line <= len(doc_lines[src]) else False
                c = {"printed_page": None, "provision": f"dòng {line}"}
            else:  # bài báo web: không kiểm tra tự động (đã đọc ngày truy cập), trỏ tới bản ghi diễn giải
                ok = None
                c = {"printed_page": None, "provision": f"{sd.get('publisher') or ''}, {sd.get('document_date') or ''}".strip(", "), "url": sd.get("url"), "record_id": web_rec.get(src)}
            if ok is False:
                report["warnings"].append(f"anecdote {a['id']}: anchor '{anchor}' không có ở {src} {page or line}")
            cites.append({"source_id": src, "source_title": sd["title"], "source_type": sd["source_type"], "verified_anchor": ok, **c})
        out.append({"id": a["id"], "period": a["period"], "topic_id": a["topic"], "image_ids": a["images"], "notes": a["notes"],
                    "title": dict(zip(("vi", "en", "zh"), a["title"])), "teaser": dict(zip(("vi", "en", "zh"), a["teaser"])),
                    "body": dict(zip(("vi", "en", "zh"), a["body"])), "citations": cites,
                    "note": "Văn kể do nhóm biên soạn từ các nguồn được trích; bản en/zh là bản dịch của nhóm phát triển."})
    return out


def build_exhibits_and_zones(s, *, root: Path, page_text: dict, squash, report: dict, sources: dict, anecdotes: list) -> tuple[list, dict]:
    """Gian trưng bày + nội dung các khu vực bản đồ. Kiểm tra anchor như mẩu chuyện."""
    import curation_exhibits as CE
    import curation_hall as CH
    doc_lines = {sid: (root / CS.DOC_DIR / f).read_text(encoding="utf-8").splitlines() for sid, f, *_ in CS.DOCS}

    def cite(src, page, line, anchor):
        sd = sources[src]
        ok, c = None, {}
        if src == "SRC001":
            ok = squash(anchor) in squash(page_text.get(page, "")) if anchor else None
            c = {"printed_page": page, "provision": None}
        elif src in doc_lines:
            ok = bool(anchor) and 0 < line <= len(doc_lines[src]) and squash(anchor) in squash(doc_lines[src][line - 1])
            c = {"printed_page": None, "provision": f"dòng {line}"}
        else:
            c = {"printed_page": None, "provision": ", ".join(x for x in (sd.get("publisher"), sd.get("document_date")) if x), "url": sd.get("url")}
        if ok is False:
            report["warnings"].append(f"exhibit/zone: anchor '{anchor}' không có ở {src} {page or line}")
        return {"source_id": src, "source_title": sd["title"], "source_type": sd["source_type"], "verified_anchor": ok, **c}

    def img(iid):
        im = s.get(M.Image, iid)
        if im is None:
            report["warnings"].append(f"exhibit: thiếu ảnh {iid}")
            return None
        en, zh = im.title_en, im.title_zh
        if not en and iid in CH.BKFIG_TITLES:
            en, zh = CH.BKFIG_TITLES[iid]
        return {"image_id": iid, "title": im.title, "title_en": en, "title_zh": zh, "caption": im.caption, "kind": im.kind, "time_period": im.time_period,
                "image_url": f"/api/images/{iid}/file", "medium_url": f"/api/images/{iid}/file?size=medium", "thumb_url": f"/api/images/{iid}/file?size=thumb"}

    exhibits, used = [], set()
    for e in CE.EXHIBITS:
        ims = [x for x in (img(i) for i in [e["image"], *e.get("alt_images", [])]) if x]
        used.update(i["image_id"] for i in ims[:1])
        exhibits.append({"id": e["id"], "group": e["group"], "group_title": CE.GROUPS[e["group"]], "title": e["title"], "image": ims[0], "images": ims,
                         "paragraphs": e["paras"], "citations": [cite(*c) for c in e["cites"]], "curated": True})
    # các ảnh còn lại: thuyết minh lấy từ metadata đã biên soạn (mô tả hình ảnh + bối cảnh có nguồn)
    topic_group = {"loudspeakers": "dau-loa", "broadcast": "dau-loa", "flagpoles": "la-co", "postcard": "doi-song", "police": "doi-song", "implementation": "doi-song",
                   "memorial_site": "ngay-nay", "tongtriet": "doi-song", "late": "doi-song"}
    rows = s.query(M.Image).filter(M.Image.in_gallery.is_(True)).order_by(M.Image.image_id).all()
    seen_dup = set()
    for im in rows:
        if im.image_id in used or im.image_id in ("BKFIG01", "BKFIG14", "BKFIG15"):
            continue
        if im.duplicate_group:
            if im.duplicate_group in seen_dup:
                continue
            seen_dup.add(im.duplicate_group)
        topics = im.related_book_topics or []
        g = next((topic_group[t] for t in topics if t in topic_group), "ngay-nay" if im.kind == "contemporary_photo" else "gioi-tuyen")
        paras = [im.visual_description]
        if im.historical_context:
            paras.append(im.historical_context)
        cites = [{"source_id": im.source_id or "SRC002", "source_title": (sources.get(im.source_id or "SRC002") or {}).get("title", ""), "source_type": "ARCHIVAL_PHOTO" if im.kind != "book_figure" else "BOOK",
                  "printed_page": im.printed_page, "provision": None, "verified_anchor": None}]
        exhibits.append({"id": im.image_id.lower(), "group": g, "group_title": CE.GROUPS[g], "title": im.title, "image": img(im.image_id), "images": [img(im.image_id)],
                         "paragraphs": paras, "citations": cites, "curated": False, "time_period": im.time_period})

    by_id = {a["id"]: a for a in anecdotes}
    events = {e.event_id: e for e in s.query(M.Event).all()}

    def ev(eid):
        e = events[eid]
        return {"event_id": eid, "date_label": e.date_label, "title": e.title_vi, "summary": e.summary_vi, "printed_page": e.printed_page,
                "title_i18n": {"vi": e.title_vi, "en": e.title_en, "zh": e.title_zh},
                "summary_i18n": {"vi": e.summary_vi, "en": e.summary_en, "zh": CH.EVENT_SUMMARY_ZH.get(eid) or e.summary_en},
                "source_id": e.source_id, "source_title": sources[e.source_id]["title"]}

    zones = {
        "bridge": {"kind": "story", "title": "Cầu Hiền Lương", "events": [ev(x) for x in CE.BRIDGE_EVENTS], "stories": [by_id[x] for x in CE.BRIDGE_ANECDOTES],
                   "images": [x for x in (img(i) for i in CE.BRIDGE_IMAGES) if x]},
        "flag": {"kind": "story", "title": "Kỳ đài Hiền Lương", "events": [ev(x) for x in CE.FLAG_EVENTS], "stories": [by_id[x] for x in CE.FLAG_ANECDOTES],
                 "images": [x for x in (img(i) for i in CE.FLAG_IMAGES) if x]},
        "museum": {"kind": "exhibition", "title": "Nhà trưng bày Vĩ tuyến 17", "groups": CE.GROUPS, "n_exhibits": len(exhibits)},
    }
    for zid, p in CE.PLACES.items():
        cs = []
        for c in p["cites"]:
            if ":" in c:
                src, page, anchor = c.split(":", 2)
                cs.append(cite(src, int(page), None, anchor))
            else:
                cs.append(cite(c, None, None, None))
        tr = CH.PLACES_I18N.get(zid, {})
        zones[zid] = {"kind": "place", "title": p["title"], "subtitle": p["subtitle"], "paragraphs": p["paras"], "citations": cs,
                      "title_i18n": {"vi": p["title"], **tr.get("title", {})}, "subtitle_i18n": {"vi": p["subtitle"], **tr.get("subtitle", {})},
                      "paragraphs_i18n": {"vi": p["paras"], **tr.get("paras", {})},
                      "local_images": [{"url": u, "title": t, "credit": cr} for u, t, cr in p["images"]]}
    # ---- Nhà trưng bày số: hiện vật click được trên ảnh phòng (vi/en/zh)
    ex_by_id = {e["id"]: e for e in exhibits}
    hall = []
    for h in CH.HALL:
        cs = []
        for eid in h["exhibits"]:
            if eid not in ex_by_id:
                report["warnings"].append(f"hall {h['id']}: thiếu hiện vật {eid}")
                continue
            cs.extend(ex_by_id[eid]["citations"])
        cs.extend(cite(*c) for c in h["cites"])
        seen, uniq = set(), []
        for c in cs:
            k = (c["source_id"], c.get("printed_page"), c.get("provision"))
            if k not in seen:
                seen.add(k); uniq.append(c)
        for lang in ("vi", "en", "zh"):
            if len(h["paras"][lang]) != len(h["paras"]["vi"]):
                report["warnings"].append(f"hall {h['id']}: số đoạn {lang} khác vi")
        hall.append({"id": h["id"], "x": h["x"], "y": h["y"], "zoom": h["zoom"], "side": h.get("side", "r"), "label": dict(zip(("vi", "en", "zh"), h["label"])),
                     "paragraphs": h["paras"], "citations": uniq, "images": [x for x in (img(i) for i in h["images"]) if x],
                     "documented": bool(uniq)})
    zones["museum"]["hall"] = {"background": "/museum-hall.webp", "width": 1672, "height": 736, "items": hall,
                               "greeting": CH.GREETING, "note": CH.HALL_NOTE,
                               "translation_note": "Bản en/zh là bản dịch của nhóm phát triển."}
    zones["museum"]["topics"] = build_topics(cite=cite, img=img, ex_by_id=ex_by_id, hall=hall, sources=sources, report=report)
    return exhibits, zones


def build_topics(*, cite, img, ex_by_id, hall, sources, report) -> dict:
    """Nhà trưng bày theo 4 chủ đề: phòng chính + trang chủ đề (vi/en/zh, nguồn, nhãn cần bổ sung nguồn)."""
    import curation_topics as CT
    hall_by_id = {h["id"]: h for h in hall}
    L = ("vi", "en", "zh")

    def tri(t):
        return dict(zip(L, t))

    def uniq(cs):
        seen, out = set(), []
        for c in cs:
            k = (c["source_id"], c.get("printed_page"), c.get("provision"))
            if k not in seen:
                seen.add(k); out.append(c)
        return out

    def web_link(sid):
        sd = sources[sid]
        return {"source_id": sid, "title": sd["title"], "publisher": sd["publisher"], "url": sd["url"], "access_status": sd["access_status"]}

    def item(t, it):
        base = hall_by_id.get(it.get("reuse")) if it.get("reuse") else None
        if it.get("reuse") and base is None:
            report["warnings"].append(f"topic {it['id']}: không thấy hall {it['reuse']}")
        cs = []
        for eid in it.get("exhibits", []):
            if eid not in ex_by_id:
                report["warnings"].append(f"topic {it['id']}: thiếu hiện vật {eid}")
                continue
            cs.extend(ex_by_id[eid]["citations"])
        cs.extend(cite(*c) for c in it.get("cites", []))
        cs.extend(cite(w, None, None, None) for w in it.get("web", []))
        if base:
            cs = base["citations"] + cs
        paras = it.get("paras") or (base["paragraphs"] if base else None)
        if not paras:
            report["warnings"].append(f"topic {it['id']}: không có lời kể")
            paras = {l: [] for l in L}
        for l in L:
            if len(paras[l]) != len(paras["vi"]):
                report["warnings"].append(f"topic {it['id']}: số đoạn {l} khác vi")
        ims = [x for x in (img(i) for i in it.get("images", [])) if x]
        if base and not ims:
            ims = base["images"]
        cs = uniq(cs)
        return {"id": it["id"], "label": tri(it["label"]), "paragraphs": paras, "citations": cs, "images": ims,
                "room": list(it["room"]) if it.get("room") else None, "scene": list(it["scene"]) if it.get("scene") else None,
                "needs_source": bool(it.get("needs_source")), "needs_note": it.get("needs"),
                "links": [web_link(w) for w in it.get("links", [])], "documented": bool(cs)}

    topics = []
    for t in CT.TOPICS:
        items = [item(t, it) for it in t["items"]]
        topics.append({"id": t["id"], "no": t["no"], "short": tri(t["short"]), "title": tri(t["title"]), "subtitle": tri(t["subtitle"]),
                       "room": list(t["room"]), "focus": list(t["focus"]), "scene": t.get("scene"), "items": items,
                       "cover": next((i["images"][0] for i in items if i["images"]), None)})
    intro = CT.INTRO
    intro_out = {"id": intro["id"], "label": tri(intro["label"]), "room": list(intro["room"]), "focus": list(intro["focus"]),
                 "paragraphs": intro["paras"], "citations": uniq([c for e in intro["exhibits"] if e in ex_by_id for c in ex_by_id[e]["citations"]] + [cite(*c) for c in intro["cites"]]),
                 "images": [x for x in (img(i) for i in ("IMG035", "IMG024")) if x]}
    return {"background": "/museum-room.webp", "width": 1672, "height": 725, "intro": intro_out, "topics": topics,
            "artifacts": [{"id": a["id"], "topic": a["topic"], "room": list(a["room"]), "label": tri(a["label"])} for a in CT.ROOM_ARTIFACTS],
            "needs_label": CT.NEEDS_NOTE, "note": "Phòng và hiện vật vẽ trong ảnh là hình minh hoạ; bản en/zh do nhóm phát triển dịch."}
