#!/usr/bin/env python3
"""Dựng Knowledge Base: nạp sách (OCR) + ảnh + sự kiện + văn kiện ngoài vào SQLite và xuất JSON.

Chạy (từ thư mục dự án):  python scripts/build_knowledge_base.py [--db data/museum.db] [--max-chars 900 --overlap 150]
Điều kiện: đã chạy scripts/ingest_pdf.py, scripts/detect_figures.py, scripts/match_images.py.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT / "scripts"))

import imagehash  # noqa: E402
from PIL import Image as PILImage  # noqa: E402

import curation_images as CI  # noqa: E402
import curation_kb as CK  # noqa: E402
import supplement_ingest as SUPP  # noqa: E402
from app.database import models as M  # noqa: E402
from app.database.database import Base, get_engine, session_scope  # noqa: E402
from app.services.chunker import build_paragraphs, make_chunks  # noqa: E402
from app.services.glossary import GLOSSARY  # noqa: E402
from app.services.text_utils import detect_language, fold  # noqa: E402

KB_DIR = ROOT / "knowledge_base"
OCR_DIR = ROOT / "data/processed/ocr"
# Trang cấu trúc (bìa, trang tên sách, trang ngăn Phần 1/2, MỤC LỤC, bìa sau): giữ trong bảng pages nhưng KHÔNG đưa vào chunk
# (mục lục chứa tên mọi chương nên sẽ làm nhiễu retrieval).
STRUCTURAL_PAGES = set(range(1, 5)) | {13, 14, 57, 58} | set(range(257, 261))
SRC_BOOK = "SRC001"
SRC_PHOTO = "SRC002"


def squash(s: str) -> str:
    return "".join(fold(s).split())


CONTEXT_BY_TOPIC = {
    "bridge": "Theo sách (tr.183–184), cầu Hiền Lương ở Km735 Quốc lộ 1; sau Hiệp định Genève (21-7-1954) cầu bị chia đôi, mỗi bên dài 89 m; sau tháng 7-1956 cầu trở thành 'chứng nhân' của sự chia cắt đất nước. Sách (tr.185–186) kể cuộc 'chiến sơn cầu' (11-1958 – 1-1959) khiến cầu có hai màu.",
    "flagpoles": "Theo sách (tr.187–192), tại đầu cầu Hiền Lương hai bên thi nhau nâng cao cột cờ: lá cờ đỏ sao vàng của phía Bắc và lá cờ vàng ba sọc đỏ của phía Nam; năm 1961 phía Nam nâng cột lên 35 m, năm 1962 phía Bắc dựng trụ 38,6 m và phía Nam không nâng thêm; cột cờ bị đánh gãy ngày 2-8-1967.",
    "banner_diem": "Hình in tương ứng trong sách (tr.81) có chú thích 'Âm mưu chia cắt đất nước của Ngô Đình Diệm' thuộc chương nói về cuộc đấu tranh thực hiện Hiệp định Genève ở khu phi quân sự (7/1954–7/1956 là phạm vi chương).",
    "gate": "Sách (tr.188) nhắc việc năm 1962 sửa lại 'cổng chào' và đồn công an Hiền Lương bị hư hoại do bão. Ảnh không cho phép gắn với năm cụ thể.",
    "police": "Sách có chương về công tác tranh thủ cảnh sát Sài Gòn của đồn công an Cửa Tùng, Hiền Lương (tr.97–108) và chương về lực lượng công an bảo vệ giới tuyến (tr.59–68). Ảnh không cho biết các nhân vật thuộc bên nào.",
    "loudspeakers": "Sách có chương 'Hệ thống phát thanh tại khu phi quân sự – Vĩ tuyến 17 những năm 1956–1962' (tr.109–142), mô tả cuộc 'đấu loa' hai bờ Bến Hải.",
    "demarcation": "Giới tuyến quân sự tạm thời được nêu ở Chương I, Điều 1 của Hiệp định đình chỉ chiến sự 20-7-1954 (DOC001); Tuyên bố cuối cùng 21-7-1954 (đoạn 6) nói đường phân định là tạm thời, không phải ranh giới chính trị hay lãnh thổ (DOC002) — nguồn ngoài, chưa đọc toàn văn.",
    "slogan_wall": "Chưa tìm thấy đoạn sách tương ứng trực tiếp với khẩu hiệu/tranh tường này nên không gán bối cảnh lịch sử cụ thể.",
}
SIGNIF_BY_TOPIC = {
    "bridge": "Theo sách (tr.183), cầu Hiền Lương là biểu tượng của nỗi đau chia cắt và khát vọng thống nhất đất nước.",
    "flagpoles": "Theo sách (tr.192), quá trình xây dựng và bảo vệ cột cờ là cuộc đấu tranh mang tầm vóc chính trị (đây là đánh giá của sách).",
}


def load_pages():
    rows = []
    for p in range(1, 131):
        r = json.loads((OCR_DIR / f"page_{p:03d}.json").read_text(encoding="utf-8"))
        for side in ("left", "right"):
            h = r["halves"][side]
            printed = 2 * p - 1 if side == "left" else 2 * p
            det = h["printed_page_detected"]["value"]
            rows.append(dict(pdf_page=p, side=side, printed_page=printed, detected=det, agrees=(None if det is None else det == printed),
                             text=h["text"], word_count=h["word_count"], conf=h["mean_conf"], low=h["low_conf_words"],
                             needs_review=h["needs_review"], blank=h["word_count"] < 15, direct=r["direct_text"] if side == "left" else "",
                             image=r["page_image"]))
    return rows


def chapter_of(printed: int):
    for c in CK.CHAPTERS:
        if c[4] <= printed <= c[5]:
            return c[0]
    return None


def build(args) -> dict:
    db_path = Path(args.db).resolve()
    if db_path.exists():
        db_path.unlink()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    engine = get_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)
    report: dict = {"warnings": []}

    pages = load_pages()
    for pg in pages:
        pg["chapter_id"] = chapter_of(pg["printed_page"])

    with session_scope() as s:
        # --- sources, chapters, topics
        for d in CK.SOURCES:
            s.add(M.Source(**d))
        for (cid, vi, en, zh, a, b, part, period, topic) in CK.CHAPTERS:
            s.add(M.Chapter(chapter_id=cid, order=int(cid[1:]), part=part, title_vi=vi, title_en=en, title_zh=zh, printed_start=a, printed_end=b, topic_id=topic, period_scope=period))
        chap_by_id = {c[0]: c for c in CK.CHAPTERS}
        for i, (tid, vi, en, zh, desc, chs) in enumerate(CK.TOPICS):
            starts = [chap_by_id[c][4] for c in chs]; ends = [chap_by_id[c][5] for c in chs]
            s.add(M.Topic(topic_id=tid, order=i, title_vi=vi, title_en=en, title_zh=zh, description_vi=desc, chapter_ids=chs, printed_start=min(starts), printed_end=max(ends)))
        s.flush()

        # --- pages
        for pg in pages:
            s.add(M.Page(source_id=SRC_BOOK, pdf_page=pg["pdf_page"], side=pg["side"], printed_page=pg["printed_page"], printed_page_detected=pg["detected"],
                         printed_page_agrees=pg["agrees"], chapter_id=pg["chapter_id"], ocr_text=pg["text"], direct_text=pg["direct"], word_count=pg["word_count"],
                         ocr_mean_conf=pg["conf"], low_conf_words=pg["low"], needs_review=pg["needs_review"], is_blank=pg["blank"], page_image=pg["image"]))
        # --- chunks từ sách
        ordered = [dict(pdf_page=p["pdf_page"], printed_page=p["printed_page"], chapter_id=p["chapter_id"], ocr_text=p["text"], needs_review=p["needs_review"], is_blank=(p["blank"] or p["printed_page"] in STRUCTURAL_PAGES)) for p in pages]
        paras, pstats = build_paragraphs(ordered)
        specs = make_chunks(paras, max_chars=args.max_chars, overlap_chars=args.overlap)
        report["paragraph_stats"] = pstats
        report["n_paragraphs"] = len(paras)
        report["structural_pages_excluded_from_chunks"] = sorted(STRUCTURAL_PAGES)
        chunk_rows = []
        for n, c in enumerate(specs, 1):
            ch = chap_by_id.get(c.chapter_id)
            folded = fold(c.text)
            kws = []
            for key, vi, en, zh in GLOSSARY:
                if any(fold(t) in folded for t in vi if len(t) > 3):
                    kws.append(vi[0])
            cid = f"{SRC_BOOK}-{n:04d}"
            row = M.Chunk(chunk_id=cid, source_id=SRC_BOOK, source_title="Đôi bờ giới tuyến (1954–1967)", source_type="BOOK", language="vi",
                          title=(c.section or (ch[1] if ch else "Sách"))[:200], category=(ch[8] if ch else "book"), chapter_id=c.chapter_id, chapter=(ch[1] if ch else None),
                          section=c.section, pdf_page=c.pdf_page, pdf_page_end=c.pdf_page_end, printed_page=c.printed_page, printed_page_end=c.printed_page_end,
                          content=c.text, folded=folded, image_ids=[], keywords=kws[:8], confidence="medium", verification_status="ocr_unverified",
                          needs_review=c.needs_review, config_id=f"c{args.max_chars}o{args.overlap}")
            chunk_rows.append(row); s.add(row)
        # --- chunks từ văn kiện ngoài
        for (kid, src, lang, title, content, prov, date, ver) in CK.EXTERNAL_RECORDS:
            sd = next(x for x in CK.SOURCES if x["source_id"] == src)
            s.add(M.Chunk(chunk_id=kid, source_id=src, source_title=sd["title"], source_type=sd["source_type"], language=lang, title=title, category="geneva_documents",
                          chapter_id=None, chapter=None, section=None, provision=prov, content=content, folded=fold(content), event_date=date, image_ids=[],
                          keywords=[], confidence="medium", verification_status=ver, needs_review=False, config_id="external"))
        s.flush()

        # --- sự kiện (kiểm tra anchor trong OCR)
        page_text = {p["printed_page"]: p["text"] for p in pages}
        ev_rows = []
        for (eid, date_iso, label, vi, en, zh, svi, sen, page, anchor, topics) in CK.EVENTS:
            txt = page_text.get(page, "")
            ok = squash(anchor) in squash(txt)
            snippet = ""
            if ok:
                flat = " ".join(txt.split()); f2 = fold(flat)
                idx = f2.find(fold(anchor)) if fold(anchor) in f2 else max(0, f2.find(anchor.replace("thang", "tháng")))
                snippet = flat[max(0, idx - 80): idx + 220] if idx >= 0 else flat[:260]
            else:
                report["warnings"].append(f"{eid}: anchor '{anchor}' không tìm thấy ở trang in {page}")
            ev = M.Event(event_id=eid, date_iso=date_iso, date_label=label, title_vi=vi, title_en=en, title_zh=zh, summary_vi=svi, summary_en=sen,
                         period=CK.period_of(date_iso), source_id=SRC_BOOK, printed_page=page, evidence_snippet=snippet,
                         verification_status="anchor_verified_in_ocr" if ok else "anchor_not_found", topic_ids=topics)
            ev_rows.append(ev); s.add(ev)
        for (eid, date_iso, label, vi, en, zh, svi, sen, src, prov, topics) in CK.EXT_EVENTS:
            s.add(M.Event(event_id=eid, date_iso=date_iso, date_label=label, title_vi=vi, title_en=en, title_zh=zh, summary_vi=svi, summary_en=sen,
                          period=CK.period_of(date_iso), source_id=src, printed_page=None, provision=prov,
                          evidence_snippet="(diễn giải từ văn kiện, xem bản ghi KX001–KX004)", verification_status="partially_verified_via_search_snippets", topic_ids=topics))
        s.flush()

        # --- quan hệ sự kiện -> chunk bằng chứng, sự kiện -> chủ đề
        for ev in ev_rows:
            cand = [c for c in chunk_rows if c.printed_page <= ev.printed_page <= (c.printed_page_end or c.printed_page) and squash(ev.date_label.split("/")[-1])[:4] in squash(c.content)]
            if not cand:
                cand = [c for c in chunk_rows if c.printed_page <= ev.printed_page <= (c.printed_page_end or c.printed_page)]
            for c in cand[:2]:
                s.add(M.Relation(from_type="event", from_id=ev.event_id, to_type="chunk", to_id=c.chunk_id, relation="evidenced_by", basis=f"trang in {ev.printed_page}", confidence="high"))
            for t in ev.topic_ids:
                s.add(M.Relation(from_type="event", from_id=ev.event_id, to_type="topic", to_id=t, relation="belongs_to", basis="biên soạn theo chương", confidence="high"))
        for kid in ("KX001", "KX002", "KX003", "KX004", "KX005", "KX006", "KX010"):
            s.add(M.Relation(from_type="event", from_id="EV-X01" if kid in ("KX001", "KX002", "KX003", "KX004") else "EV05", to_type="chunk", to_id=kid, relation="documented_by_external_source", basis="văn kiện Genève", confidence="medium"))
        s.flush()

        # --- ảnh lưu trữ (ZIP)
        arch_dir = ROOT / "data/raw/archive2"
        files = sorted(arch_dir.glob("*.jpg"))
        assert len(files) == len(CI.IMAGES) == 34, (len(files), len(CI.IMAGES))
        matches = json.loads((ROOT / "data/processed/image_matches.json").read_text())
        arch_ids = {}
        for f, cur in zip(files, CI.IMAGES):
            iid = f"IMG{cur['idx']:03d}"
            arch_ids[f.name] = iid
            b = f.read_bytes()
            im = PILImage.open(f)
            topics = cur["topics"]
            ctx = " ".join(CONTEXT_BY_TOPIC[t] for t in topics if t in CONTEXT_BY_TOPIC)
            ctx += " Ảnh không có đủ bằng chứng để gắn với một sự kiện hay năm cụ thể." if ctx else "Chưa xác định."
            signif = " ".join(SIGNIF_BY_TOPIC[t] for t in topics if t in SIGNIF_BY_TOPIC) or "Chưa xác định."
            wm = [CI.WM[w] for w in cur.get("wm", [])]
            kws = sorted(set(CI.TOPIC_LABELS[t] for t in topics) | set(cur["objects"]) | set(cur["visible_text"][:3]))
            search_text = fold(" ".join([cur["title"][0], cur["title"][1], cur["title"][2], cur["visual"], " ".join(cur["visible_text"]), " ".join(cur["objects"]), " ".join(kws), ctx]))
            s.add(M.Image(image_id=iid, kind="archive_photo", source_id=SRC_PHOTO, filename=f.name, image_path=str(f.relative_to(ROOT)), title=cur["title"][0], title_en=cur["title"][1], title_zh=cur["title"][2],
                          visual_description=cur["visual"], historical_context=ctx, location=cur["location"], location_confidence=cur["loc_conf"],
                          time_period="Chưa xác định", estimated_date="Chưa xác định", main_objects=cur["objects"], visible_text=cur["visible_text"],
                          people_description=cur["people"], historical_significance=signif, related_events=[], related_book_topics=topics,
                          related_book_pages=[dict(start=a, end=b2, link_type=lt) for a, b2, lt in cur["pages"]], keywords=kws,
                          source="Archive_2.zip (nguồn gốc ảnh chưa xác định); " + "; ".join(wm), watermarks=wm, rights_status="Chưa xác định",
                          confidence_level=cur["conf"], verification_notes=cur["notes"], duplicate_group=cur.get("dup"), similar_scene_group=cur.get("scene"),
                          sha256=hashlib.sha256(b).hexdigest(), phash=str(imagehash.phash(im)), width=im.size[0], height=im.size[1], file_format=im.format,
                          caption=None, caption_status=None, in_gallery=True, search_text=search_text))
        s.flush()

        # --- hình trong sách
        figs = json.loads((ROOT / "data/processed/book_figures.json").read_text(encoding="utf-8"))
        book_ids = {}
        for k, fg in enumerate(sorted(figs, key=lambda x: (x["pdf_page"], x["figure_id"])), 1):
            cur = CK.BOOK_FIGURES[fg["figure_id"]]
            iid = f"BKFIG{k:02d}"
            book_ids[fg["figure_id"]] = iid
            ap = ROOT / fg["image_path"]
            b = ap.read_bytes()
            im = PILImage.open(ap)
            pg_ref = fg["printed_page"]
            ctxt = cur["context"]
            topics = cur["topics"]
            search_text = fold(" ".join([cur["title"], cur["visual"], cur["caption"], ctxt]))
            truncated = "cắt" in cur["caption"] or "chưa đầy đủ" in cur["caption"]
            s.add(M.Image(image_id=iid, kind=cur["kind"], source_id=SRC_BOOK, filename=ap.name, image_path=fg["image_path"], title=cur["title"], title_en=None, title_zh=None,
                          visual_description=cur["visual"], historical_context=ctxt, location="Theo chú thích sách" if cur["caption"] else "Không áp dụng",
                          location_confidence="medium", time_period="Theo chú thích sách (nếu có)" if cur["caption"] else "Không áp dụng", estimated_date="Chưa xác định",
                          main_objects=[], visible_text=[], people_description="", historical_significance="Chưa xác định", related_events=[], related_book_topics=topics,
                          related_book_pages=[dict(start=pg_ref, end=pg_ref, link_type="printed_in_book")], keywords=[CI.TOPIC_LABELS.get(t, t) for t in topics],
                          source=f"Sách 'Đôi bờ giới tuyến', trang PDF {fg['pdf_page']}, trang in {pg_ref} (ảnh crop từ bản scan)", watermarks=[], rights_status="Chưa xác định",
                          confidence_level="high" if cur["caption"] and not truncated else "medium",
                          verification_notes="Hình do bộ phát hiện layout tách từ trang scan (data/processed/book_figures.json), đã kiểm tra bằng mắt; caption đọc trực tiếp từ crop" + ("; caption bị cắt trong OCR/crop" if truncated else ""),
                          duplicate_group=None, similar_scene_group=None, sha256=hashlib.sha256(b).hexdigest(), phash=str(imagehash.phash(im)), width=im.size[0], height=im.size[1],
                          file_format="PNG", pdf_page=fg["pdf_page"], printed_page=pg_ref, bbox=fg["bbox_xywh"], caption=cur["caption"] or None,
                          caption_status=("verified_visual_partial" if truncated else "verified_visual") if cur["caption"] else None,
                          in_gallery=(cur["kind"] == "book_figure"), search_text=search_text))
        s.flush()

        # --- ĐỢT BỔ SUNG 2026-10-31: 3 bài viết + Archive_4.zip (chỉ thêm, không sửa dữ liệu cũ)
        report["supplement"] = SUPP.add_supplement(s, root=ROOT, page_text={p["printed_page"]: p["text"] for p in pages}, book_chunks=chunk_rows,
                                                   report=report, context_by_topic=CONTEXT_BY_TOPIC, squash=squash)

        # --- quan hệ ảnh: trang sách (chunk), chủ đề, trùng lặp, khớp với hình sách
        all_images = s.query(M.Image).all()
        for im in all_images:
            for lp in im.related_book_pages:
                for c in chunk_rows:
                    if c.printed_page <= lp["end"] and (c.printed_page_end or c.printed_page) >= lp["start"]:
                        rel = "same_figure_in_book" if lp["link_type"] in ("direct_match_book_figure", "printed_in_book") else "topic_corroborated_by"
                        s.add(M.Relation(from_type="image", from_id=im.image_id, to_type="chunk", to_id=c.chunk_id, relation=rel,
                                         basis=lp["link_type"], confidence="high" if lp["link_type"] != "topic_corroborated" else "low"))
                        if im.in_gallery and lp["link_type"] in ("direct_match_book_figure", "printed_in_book") and im.image_id not in c.image_ids:
                            c.image_ids = list(c.image_ids) + [im.image_id]
            for t in im.related_book_topics:
                s.add(M.Relation(from_type="image", from_id=im.image_id, to_type="topic", to_id=t, relation="depicts_topic", basis="nội dung nhìn thấy", confidence=im.confidence_level))
        by_dup: dict[str, list[str]] = {}
        by_scene: dict[str, list[str]] = {}
        for im in all_images:
            if im.duplicate_group: by_dup.setdefault(im.duplicate_group, []).append(im.image_id)
            if im.similar_scene_group: by_scene.setdefault(im.similar_scene_group, []).append(im.image_id)
        for g, ids in by_dup.items():
            if g.startswith("DUP-S"):  # nhóm của đợt bổ sung: quan hệ đã ghi kèm căn cứ SIFT trong supplement_ingest
                continue
            for i, a in enumerate(ids):
                for b in ids[i + 1:]:
                    s.add(M.Relation(from_type="image", from_id=a, to_type="image", to_id=b, relation="variant_of_same_photograph", basis=f"nhóm {g}: pHash/SIFT", confidence="high"))
        for g, ids in by_scene.items():
            for i, a in enumerate(ids):
                for b in ids[i + 1:]:
                    s.add(M.Relation(from_type="image", from_id=a, to_type="image", to_id=b, relation="same_scene_different_frame", basis=f"nhóm {g}", confidence="medium"))
        # khớp ảnh ZIP <-> hình sách (SIFT >= 150)
        for a, b, n in matches["archive_vs_book"]:
            if n >= 90:
                fid = b.split(".png")[0]; fid = "_".join(fid.split("_")[:3])
                if a in arch_ids and fid in book_ids:
                    s.add(M.Relation(from_type="image", from_id=arch_ids[a], to_type="image", to_id=book_ids[fid], relation="same_photograph_as_book_figure", basis=f"SIFT RANSAC inliers={n}", confidence="high" if n >= 150 else "medium"))
        # ảnh <-> sự kiện: chỉ khi chú thích sách trực tiếp liên quan
        for iid in (book_ids["FIG_P094_1"], "IMG034", "IMG004"):  # (sửa lỗi cũ: từng gắn nhầm BKFIG10 = bưu thiếp)
            s.add(M.Relation(from_type="image", from_id=iid, to_type="event", to_id="EV19", relation="illustrates", basis="chú thích sách tr.187 'Cây cầu Hiền Lương có hai màu'; SIFT", confidence="medium"))
            im = s.get(M.Image, iid)
            if im: im.related_events = ["EV19"]
        for eid, (ref, rel) in CK.EVENT_ILLUSTRATIONS.items():
            iid = book_ids.get(ref, ref)
            basis = ("chú thích hình trong sách thuộc chương của sự kiện" if rel == "illustrates"
                     else "ảnh minh hoạ cùng chủ đề/địa điểm – KHÔNG phải ảnh chụp tại sự kiện")
            s.add(M.Relation(from_type="image", from_id=iid, to_type="event", to_id=eid, relation=rel, basis=basis, confidence="medium" if rel == "illustrates" else "low"))
        # --- câu chuyện trang chủ: kiểm tra anchor từng trích dẫn trang sách
        story_out = []
        for ch in CK.STORY:
            cites = []
            for src, page, prov, anchor in ch["cites"]:
                ok = True
                if page is not None:
                    ok = squash(anchor) in squash(page_text.get(page, ""))
                    if not ok:
                        report["warnings"].append(f"story {ch['id']}: anchor '{anchor}' không có ở trang in {page}")
                sd = next(x for x in CK.SOURCES if x["source_id"] == src)
                cites.append({"source_id": src, "source_title": sd["title"], "source_type": sd["source_type"], "printed_page": page, "provision": prov, "verified_anchor": ok})
            img_id = book_ids.get(ch["image"], ch["image"])
            story_out.append({"id": ch["id"], "period": ch["period"], "image_id": img_id, "topic_id": ch["topic"], "timeline_period": ch["timeline"],
                              "title": dict(zip(("vi", "en", "zh"), ch["title"])), "lead": dict(zip(("vi", "en", "zh"), ch["lead"])),
                              "body": dict(zip(("vi", "en", "zh"), ch["body"])), "citations": cites,
                              "note": "Văn dẫn chuyện do nhóm biên soạn từ các trang được trích; bản en/zh là bản dịch của nhóm phát triển."})
        KB_DIR.mkdir(exist_ok=True)
        (KB_DIR / "story.json").write_text(json.dumps(story_out, ensure_ascii=False, indent=1), encoding="utf-8")
        # --- mẩu chuyện thú vị (đợt bổ sung): kiểm tra anchor trích dẫn
        all_src = {x.source_id: {c.name: getattr(x, c.name) for c in M.Source.__table__.columns} for x in s.query(M.Source).all()}
        anecdotes = SUPP.build_anecdotes(root=ROOT, page_text=page_text, squash=squash, report=report, sources=all_src)
        (KB_DIR / "anecdotes.json").write_text(json.dumps(anecdotes, ensure_ascii=False, indent=1), encoding="utf-8")
        report["n_anecdotes"] = len(anecdotes)
        exhibits, zones = SUPP.build_exhibits_and_zones(s, root=ROOT, page_text=page_text, squash=squash, report=report, sources=all_src, anecdotes=anecdotes)
        (KB_DIR / "exhibits.json").write_text(json.dumps(exhibits, ensure_ascii=False, indent=1), encoding="utf-8")
        (KB_DIR / "zones.json").write_text(json.dumps(zones, ensure_ascii=False, indent=1), encoding="utf-8")
        report["n_exhibits"] = len(exhibits)
        s.flush()

        # --- báo cáo
        n_pages = len(pages)
        report.update(
            pdf_pages=130, book_pages=n_pages, blank_pages=sum(p["blank"] for p in pages), review_pages=sum(p["needs_review"] for p in pages),
            printed_detect_agree=sum(1 for p in pages if p["agrees"] is True), printed_detect_disagree=sum(1 for p in pages if p["agrees"] is False),
            printed_detect_none=sum(1 for p in pages if p["agrees"] is None), n_chunks_book=len(specs), n_chunks_external=len(CK.EXTERNAL_RECORDS),
            n_events=len(CK.EVENTS) + len(CK.EXT_EVENTS) + report["supplement"]["events_added"], n_images=len(all_images), chunk_config=dict(max_chars=args.max_chars, overlap=args.overlap),
            avg_chunk_chars=round(sum(len(c.text) for c in specs) / len(specs), 1),
        )

    # --- xuất JSON (kho tri thức dạng file, dễ audit/diff)
    KB_DIR.mkdir(exist_ok=True)
    from sqlalchemy import select
    with session_scope() as s:
        def dump(model, name, skip=()):
            rows = s.scalars(select(model)).all()
            out = [{c.name: getattr(r, c.name) for c in model.__table__.columns if c.name not in skip} for r in rows]
            (KB_DIR / f"{name}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
            return len(out)
        report["exported"] = {
            "sources": dump(M.Source, "sources"), "chapters": dump(M.Chapter, "chapters"), "topics": dump(M.Topic, "topics"),
            "pages": dump(M.Page, "pages", skip=("direct_text",)), "chunks": dump(M.Chunk, "chunks", skip=("folded",)),
            "images": dump(M.Image, "images", skip=("search_text",)), "events": dump(M.Event, "events"), "relations": dump(M.Relation, "relations"),
        }
    (ROOT / "data/processed/build_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    return report


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=str(ROOT / "data/museum.db"))
    ap.add_argument("--max-chars", type=int, default=900)
    ap.add_argument("--overlap", type=int, default=150)
    rep = build(ap.parse_args())
    print(json.dumps(rep, ensure_ascii=False, indent=1))
    if rep["warnings"]:
        print("CẢNH BÁO:", *rep["warnings"], sep="\n  ")
