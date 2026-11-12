"""Kiểm thử ĐỢT BỔ SUNG NGUỒN 2026-10-31: 3 bài viết (SRC003–SRC005), Archive_4.zip (SRC006), ghi chú đối chiếu (NOTE01).
LLM được giả lập (MockTransport) – không tốn quota."""
from __future__ import annotations

import json
import re
import sqlite3
import unicodedata

import pytest

from tests.conftest import ROOT, llm_json

SUPP_IMAGES = [f"IMG{n:03d}" for n in range(35, 51)]


@pytest.fixture(scope="module")
def db():
    c = sqlite3.connect(ROOT / "data/museum.db"); c.row_factory = sqlite3.Row
    yield c; c.close()


def chat(client, msg, lang="vi", sid="sup"):
    return client.post("/api/chat", json={"message": msg, "language": lang, "session_id": sid})


# ---------------- dữ liệu nguồn
def test_sources_registered_with_metadata(db):
    s = {r["source_id"]: r for r in db.execute("select * from sources")}
    for sid in ("SRC001", "SRC002", "DOC001", "REF001"):  # nguồn cũ vẫn còn
        assert sid in s
    assert s["SRC003"]["author"] == "Minh Vượng" and s["SRC003"]["source_type"] == "SECONDARY_ARTICLE"
    assert "oral_testimony" in s["SRC004"]["classification"]
    assert s["SRC006"]["source_type"] == "ARCHIVAL_PHOTO" and "Archive_4.zip" in s["SRC006"]["title"]
    assert s["NOTE01"]["source_type"] == "CURATOR_NOTE"
    for sid in ("SRC003", "SRC004", "SRC005"):
        assert s[sid]["url"] is None and "Chưa xác định" in s[sid]["publisher"]  # không bịa URL/nhà xuất bản
    assert (ROOT / "data/raw/Archive_4.zip").is_file()  # giữ ZIP gốc


def test_doc_chunks_cover_every_line_with_position(db):
    files = {"SRC003": "bcb09328", "SRC004": "3fc2987b", "SRC005": "01abc224"}
    sq = lambda x: re.sub(r"\s+", "", x)  # noqa: E731
    for sid, f in files.items():
        rows = db.execute("select chunk_id, provision, content from chunks where source_id=?", (sid,)).fetchall()
        assert rows and all(re.match(r"dòng \d+", r["provision"]) for r in rows)
        blob = sq("".join(r["content"] for r in rows))
        for ln in (ROOT / f"data/raw/supplement_docs/{f}-attachment.txt").read_text(encoding="utf-8").splitlines():
            if ln.strip():
                assert sq(ln) in blob, (sid, ln[:50])
        assert max(len(r["content"]) for r in rows) <= 900


def test_supplement_images_complete_and_filenames_preserved(db):
    rows = {r["image_id"]: r for r in db.execute("select * from images where source_id='SRC006'")}
    assert sorted(rows) == SUPP_IMAGES
    on_disk = {p.name for p in (ROOT / "data/raw/archive4").iterdir()}
    for r in rows.values():
        assert r["filename"] in on_disk and (ROOT / r["image_path"]).is_file()  # tên file gốc (NFD, khoảng trắng) giữ nguyên
        assert r["filename_title"] and json.loads(r["metadata_basis"])["title"] == "filename"
        assert json.loads(r["metadata_basis"])["visual_description"] == "visual_inspection"
        assert len(r["visual_description"]) > 60 and r["sha256"] and r["phash"]
        # không tự gán niên đại: hoặc chưa xác định, hoặc ghi rõ căn cứ (tên file/chú thích/ảnh màu thời nay)
        assert r["estimated_date"] == "Chưa xác định"
        assert re.search(r"Chưa xác định|chưa xác minh|chú thích|Thời nay", r["time_period"]), r["image_id"]
        assert "tên file" not in (r["title"] + r["time_period"] + r["location"] + r["people_description"]).lower()  # bỏ cụm "theo tên file" khỏi nội dung hiển thị
        assert re.search(r"không xác định|chưa xác minh|Không có người|Không thấy người", r["people_description"]), r["image_id"]
    assert len(list((ROOT / "data/raw/archive2").glob("*.jpg"))) == 34  # ảnh cũ còn nguyên


def test_filename_matches_document_caption_for_nine_images(db):
    rows = db.execute("select image_id, filename, caption, caption_status from images where caption_status like 'document_caption:SRC003%'").fetchall()
    assert len(rows) == 9 and all(r["caption_status"].endswith(":matches_filename") for r in rows)
    for r in rows:
        rel = db.execute("select to_id from relations where from_id=? and relation='captioned_in_document'", (r["image_id"],)).fetchone()
        ch = db.execute("select image_ids, source_id from chunks where chunk_id=?", (rel["to_id"],)).fetchone()
        assert ch["source_id"] == "SRC003" and r["image_id"] in json.loads(ch["image_ids"])
        assert unicodedata.normalize("NFC", r["caption"]).rstrip(". ")[:20] in unicodedata.normalize("NFC", r["filename"])


def test_duplicates_recorded_not_deleted(db):
    g = db.execute("select image_id from images where duplicate_group='DUP-S024' order by 1").fetchall()
    assert [r[0] for r in g] == ["IMG024", "IMG036"]
    rel = {(r["from_id"], r["to_id"], r["relation"]) for r in db.execute("select * from relations where from_type='image' and to_type='image' and from_id like 'IMG0%'")}
    assert ("IMG042", "IMG030", "likely_same_photograph") in rel
    assert ("IMG039", "IMG004", "same_scene_different_frame") in rel


def test_conflict_notes_link_both_sides(db):
    notes = db.execute("select chunk_id, content from chunks where source_type='CURATOR_NOTE'").fetchall()
    assert len(notes) == 11
    for n in notes:
        tgt = db.execute("select c.source_id from relations r join chunks c on c.chunk_id=r.to_id where r.from_id=? and r.relation='compares_source'", (n["chunk_id"],)).fetchall()
        assert len({t[0] for t in tgt}) >= 2, n["chunk_id"]
    n1 = next(n for n in notes if n["chunk_id"] == "NOTE-01")["content"]
    assert "9-1966" in n1 and "2/8/1967" in n1 and "không kết luận" in n1


def test_new_events_verified(db):
    ev = {r["event_id"]: r for r in db.execute("select * from events where event_id in ('EV29','EV-S01')")}
    assert ev["EV29"]["verification_status"] == "anchor_verified_in_ocr" and ev["EV29"]["printed_page"] == 116
    assert ev["EV-S01"]["source_id"] == "SRC005" and ev["EV-S01"]["period"] == "1956-1967"


# ---------------- truy xuất
@pytest.mark.parametrize("q,expect_src,expect_text", [
    ("O Nhạn là ai?", "SRC003", "O Nhạn"),
    ("Trạm tăng âm của hệ thống loa đặt cách cầu bao xa?", "SRC005", "trạm tăng âm"),
    ("Bà Nguyễn Thị Hương kể gì về việc sơn cầu?", "SRC004", "Nguyễn Thị Hương"),
    ("Vì sao sông Minh Lương đổi tên thành Hiền Lương?", "SRC003", "Minh Mạng"),
])
def test_retrieval_finds_new_documents(index_and_chunks, q, expect_src, expect_text):
    ix, _ = index_and_chunks
    hits, _ = ix.search(q, k=5)
    assert any(ix.chunk(h.chunk_id)["source_id"] == expect_src and expect_text.lower() in ix.chunk(h.chunk_id)["content"].lower() for h in hits)


def test_curator_note_attached_not_crowding(index_and_chunks):
    ix, _ = index_and_chunks
    hits, _ = ix.search("Cầu Hiền Lương bị đánh sập năm nào?", k=6)
    ids = [h.chunk_id for h in hits]
    assert "NOTE-01" in ids and ids.index("NOTE-01") == len(ids) - 1  # gắn cuối, không chiếm suất top-k
    assert sum(1 for i in ids if i.startswith("NOTE")) == 1


@pytest.mark.parametrize("q,expected", [
    ("O Nhạn phát thanh viên Đài Truyền thanh Vĩnh Linh", "IMG043"), ("cầu Hiền Lương bị bom Mỹ đánh sập năm 1967", "IMG037"),
    ("toàn cảnh cầu Hiền Lương ngày 2-9-1959", "IMG044"), ("1954 Geneva Conference", "IMG035"), ("cột cờ tại cầu Hiền Lương ngày nay", "IMG040"),
])
def test_image_search_by_filename_content(client, q, expected):
    j = client.get("/api/images", params={"q": q}).json()
    assert expected in [i["image_id"] for i in j["items"]]


# ---------------- API & chat (LLM giả lập)
def test_image_detail_shows_filename_basis_and_document_caption(client):
    d = client.get("/api/images/IMG043").json()
    assert d["filename_title"].startswith("O Nhạn") and d["metadata_basis"]["title"] == "filename" and d["title"].startswith("O Nhạn")
    p0 = d["related_passages"][0]
    assert p0["relation"] == "captioned_in_document" and p0["source_id"] == "SRC003" and p0["provision"].startswith("dòng 62")
    assert client.get("/api/images/IMG046/file?size=thumb").status_code == 200  # ảnh .webp
    assert client.get("/api/images/IMG036/file").status_code == 200  # tên file có dấu + khoảng trắng


def test_documents_endpoint_counts(client):
    docs = {d["source_id"]: d for d in client.get("/api/documents").json()["items"]}
    assert docs["SRC003"]["n_chunks"] == 24 and docs["SRC004"]["n_chunks"] == 14 and docs["SRC005"]["n_chunks"] == 15
    assert docs["SRC006"]["n_images"] == 16 and docs["SRC002"]["n_images"] == 34 and docs["NOTE01"]["n_chunks"] == 11


def test_chat_answers_from_new_article_with_image(client):
    # LLM giả lập trích mọi nhãn: kiểm tra đoạn của SRC003 có trong ngữ cảnh và được trả về như nguồn (hạng của nó không cố định)
    client.fake.llm_script.append(llm_json("Theo bài viết, O Nhạn là phát thanh viên chính của Đài Truyền thanh Vĩnh Linh [S1][S2][S3][S4][S5][S6].",
                                           used=("S1", "S2", "S3", "S4", "S5", "S6"), images=("I1",)))
    j = chat(client, "O Nhạn là ai?").json()
    assert j["mode"] == "llm" and not j["insufficient_evidence"]
    src = {s["source_id"]: s for s in j["sources"]}
    assert "SRC003" in src and src["SRC003"]["source_type"] == "SECONDARY_ARTICLE" and src["SRC003"]["provision"].startswith("dòng")
    assert "IMG043" in [i["image_id"] for i in j["images"]]
    prompt = client.fake.llm_calls[-1]["body"]["messages"]
    ctx = "\n".join(m["content"] for m in prompt)
    assert "chú thích trong bài SRC003" in ctx and "mô tả đi kèm ảnh (CHƯA xác minh" in ctx and "SECONDARY_ARTICLE" in ctx


def test_chat_context_combines_book_articles_and_images(client):
    client.fake.llm_script.append(llm_json("Theo sách và các bài viết [S1][S2][S3][S4][S5][S6]…", used=("S1", "S2", "S3", "S4", "S5", "S6")))
    j = chat(client, "Hệ thống loa phát thanh ở bờ Bắc cầu Hiền Lương gồm những gì và đấu loa kéo dài đến khi nào?").json()
    types = {s["source_type"] for s in j["sources"]}
    assert {"BOOK", "SECONDARY_ARTICLE"} <= types and len({s["source_id"] for s in j["sources"]}) >= 2
    assert len(j["images"]) >= 1


def test_chat_conflict_question_gets_curator_note_in_context(client):
    client.fake.llm_script.append(llm_json("Các nguồn khác nhau: sách ghi 9-1966 [S1], bài viết ghi 1967 [S2].", used=("S1", "S2")))
    chat(client, "Cầu Hiền Lương bị đánh sập năm nào?")
    ctx = "\n".join(m["content"] for m in client.fake.llm_calls[-1]["body"]["messages"])
    assert "NOTE01" in ctx and "CURATOR_NOTE" in ctx and "9-1966" in ctx
    assert "do not pick a winner" in ctx  # quy tắc trong system prompt


def test_timeline_has_only_images_and_new_events(client):
    items = {e["event_id"]: e for e in client.get("/api/timeline").json()["items"]}
    assert "EV29" in items and "EV-S01" in items
    assert {i["image_id"] for i in items["EV26"]["images"]} >= {"IMG037"}
    assert all(i["image_id"].startswith(("IMG", "BKFIG")) for e in items.values() for i in e["images"])


# ---------------- nguồn web + mẩu chuyện thú vị
def test_web_sources_paraphrased_with_url(db):
    rows = db.execute("select s.source_id, s.url, s.document_date, c.chunk_id, c.content from sources s join chunks c on c.source_id=s.source_id where s.source_type='WEB_ARTICLE'").fetchall()
    assert {r["source_id"] for r in rows} == {"WEB001", "WEB002", "WEB003", "WEB004"}
    for r in rows:
        assert r["url"].startswith("https://") and "Diễn giải của nhóm phát triển" in r["content"]  # không chép nguyên văn


def test_anecdotes_endpoint_all_citations_verified(client):
    j = client.get("/api/anecdotes").json()
    items = j["items"]
    assert len(items) == 10 and {"cau-hai-mau", "choi-co", "dau-loa", "loa-500w", "dem-2-8-1967"} <= {a["id"] for a in items}
    for a in items:
        assert all(a["title"][l] and a["teaser"][l] and a["body"][l] for l in ("vi", "en", "zh"))
        assert a["images"] and all(im["image_url"].startswith("/api/images/") for im in a["images"])
        assert len(a["citations"]) >= 3
        for c in a["citations"]:
            if c["source_type"] == "WEB_ARTICLE":
                assert c["verified_anchor"] is None and c["url"].startswith("https://")
            else:
                assert c["verified_anchor"] is True, (a["id"], c)
    loa = next(a for a in items if a["id"] == "loa-500w")
    assert [n["chunk_id"] for n in loa["notes_detail"]] == ["NOTE-09"]  # chuyện có nguồn mâu thuẫn trỏ tới ghi chú đối chiếu


def test_no_filename_phrase_in_visible_image_text(client):
    for iid in SUPP_IMAGES:
        d = client.get(f"/api/images/{iid}").json()
        visible = " ".join([d["title"], d["title_en"] or "", d["location"], d["time_period"], d["people_description"], d["historical_context"]]).lower()
        assert "theo tên file" not in visible and "per filename" not in visible and "据文件名" not in visible, iid


# ---------------- gian trưng bày + khu vực bản đồ (cho giao diện Thuyetminhbaotang)
def test_exhibits_endpoint(client):
    j = client.get("/api/exhibits").json()
    items = j["items"]
    assert j["total"] == len(items) >= 50
    curated = [e for e in items if e["curated"]]
    assert len(curated) >= 15 and {"me-vinh-linh-va-co", "loa-500w", "cau-hai-mau", "o-nhan"} <= {e["id"] for e in curated}
    for e in curated:
        assert e["image"]["image_url"].startswith("/api/images/") and len(e["paragraphs"]) >= 2
        for c in e["citations"]:
            assert c["verified_anchor"] in (True, None), (e["id"], c)  # sách/bài viết phải khớp neo; web = None
    assert len({e["image"]["image_id"] for e in items}) == len(items)  # mỗi hiện vật một ảnh chính khác nhau
    assert client.get("/api/exhibits", params={"group": "la-co"}).json()["total"] >= 3


def test_zone_endpoints(client):
    b = client.get("/api/zones/bridge").json()
    assert b["kind"] == "story" and len(b["stories"]) == 4 and len(b["events"]) >= 8 and b["images"]
    f = client.get("/api/zones/flag").json()
    assert {s["id"] for s in f["stories"]} == {"choi-co", "nguoi-may-co", "me-diem", "dem-2-8-1967"}
    for z in ("monument", "union"):
        d = client.get(f"/api/zones/{z}").json()
        assert d["kind"] == "place" and len(d["paragraphs"]) >= 2 and d["local_images"]
        assert any(c["source_type"] == "WEB_ARTICLE" and c["url"].startswith("https://") for c in d["citations"])
    u = client.get("/api/zones/union").json()
    assert any(c["source_id"] == "SRC001" and c["verified_anchor"] is True for c in u["citations"])
    assert client.get("/api/zones/khong-co").status_code == 404


def test_museum_hall_items_trilingual_and_cited(client):
    """Nhà trưng bày số: 15 hiện vật bấm được, đủ vi/en/zh, mỗi hiện vật có nguồn, không có anchor kiểm tra thất bại."""
    h = client.get("/api/zones/museum").json()["hall"]
    assert h["background"] == "/museum-hall.webp" and h["width"] == 1672 and h["height"] == 736
    items = h["items"]
    assert len(items) == 15 and len({i["id"] for i in items}) == 15
    for lang in ("vi", "en", "zh"):
        assert h["greeting"][lang] and h["note"][lang]
    for it in items:
        assert 0 < it["x"] < 100 and 0 < it["y"] < 100 and 1 <= it["zoom"] <= 3 and it["side"] in ("l", "r")
        assert all(it["label"][l] for l in ("vi", "en", "zh"))
        n = len(it["paragraphs"]["vi"])
        assert n >= 2 and all(len(it["paragraphs"][l]) == n for l in ("en", "zh")), it["id"]
        assert it["citations"], it["id"]
        assert all(c["verified_anchor"] is not False for c in it["citations"]), it["id"]
        for im in it["images"]:
            assert im["image_url"].startswith("/api/images/") and im["title_en"] and im["title_zh"], (it["id"], im["image_id"])
    # hiện vật trong không gian minh hoạ phải ghi rõ là minh hoạ; giới tuyến là tạm thời, không phải biên giới
    by = {i["id"]: i for i in items}
    assert "tạm thời" in " ".join(by["ban-do"]["paragraphs"]["vi"]) and "không phải biên giới" in " ".join(by["ban-do"]["paragraphs"]["vi"])
    assert "không phải mốc biên giới" in " ".join(by["cot-moc"]["paragraphs"]["vi"])
    for k in ("lien-lac", "huan-chuong", "cong-an", "hanh-ly", "cot-moc", "khanh-tiet", "sum-hop"):
        assert "minh hoạ" in " ".join(by[k]["paragraphs"]["vi"]), k
    # chỗ hai nguồn ghi khác nhau thì nêu cả hai
    assert "50W" in " ".join(by["ngoi-sao"]["paragraphs"]["vi"]) and "500W" in " ".join(by["ngoi-sao"]["paragraphs"]["vi"])


def test_zone_translations(client):
    b = client.get("/api/zones/bridge").json()
    for e in b["events"]:
        assert all(e["title_i18n"][l] for l in ("vi", "en", "zh")) and all(e["summary_i18n"][l] for l in ("vi", "en", "zh"))
    for z in ("monument", "union"):
        d = client.get(f"/api/zones/{z}").json()
        n = len(d["paragraphs_i18n"]["vi"])
        assert all(len(d["paragraphs_i18n"][l]) == n for l in ("en", "zh"))
        assert all(d["title_i18n"][l] and d["subtitle_i18n"][l] for l in ("vi", "en", "zh"))


def test_museum_topics_four_topics_sourced(client):
    """Nhà trưng bày theo 4 chủ đề của nhóm: đủ chủ đề, đủ vi/en/zh, có nguồn hoặc gắn nhãn 'cần bổ sung nguồn'."""
    t = client.get("/api/zones/museum").json()["topics"]
    assert t["background"] == "/museum-room.webp" and t["height"] == 725
    tops = t["topics"]
    assert [x["id"] for x in tops] == ["topic-1", "topic-2", "topic-3", "topic-4"]
    assert "Giơ-ne-vơ" in tops[0]["title"]["vi"] and "1972" in tops[3]["title"]["vi"]
    assert set(t["needs_label"]) == {"vi", "en", "zh"}
    ids = set()
    for tp in tops:
        for l in ("vi", "en", "zh"):
            assert tp["title"][l] and tp["short"][l] and tp["subtitle"][l]
        for it in tp["items"]:
            assert it["id"] not in ids; ids.add(it["id"])
            n = len(it["paragraphs"]["vi"])
            assert n >= 2 and all(len(it["paragraphs"][l]) == n for l in ("en", "zh")), it["id"]
            assert all(c.get("verified_anchor") is not False for c in it["citations"]), it["id"]
            # hoặc có nguồn, hoặc được gắn nhãn cần bổ sung nguồn (kèm ghi chú 3 thứ tiếng)
            assert it["citations"] or it["needs_source"], it["id"]
            if it["needs_source"]:
                assert all(it["needs_note"][l] for l in ("vi", "en", "zh")), it["id"]
            for w in it["citations"]:
                if w["source_type"] == "WEB_ARTICLE":
                    assert w["url"].startswith("https://"), it["id"]
    # các hiện vật chưa có tư liệu phải gắn nhãn
    for k in ("thong-hanh", "luc-luong", "dia-dao", "choi-son", "thu-tu", "do-du-kich", "hoang-thi-cham", "tai-thiet", "nhat-ky"):
        assert k in ids
        assert next(i for tp in tops for i in tp["items"] if i["id"] == k)["needs_source"], k
    # 267 là tổng số cờ đã dùng, không phải số cờ bị xé
    co = next(i for i in tops[2]["items"] if i["id"] == "choi-co")
    assert "267" in " ".join(co["paragraphs"]["vi"]) and "không nói cả 267" in " ".join(co["paragraphs"]["vi"])
    # giấy thông hành: đúng thuật ngữ, trang 48
    th = next(i for i in tops[0]["items"] if i["id"] == "thong-hanh")
    assert any(c.get("printed_page") == 48 for c in th["citations"])
    assert {a["topic"] for a in t["artifacts"]} <= {x["id"] for x in tops}
