"""RET-*, PDF-*, IMG-*, bảo mật dữ liệu: kiểm tra trên KB thật đã dựng."""
import json
import re
import sqlite3
from pathlib import Path

import pytest

from app.core.security import safe_join
from app.core.logging import redact

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def db():
    c = sqlite3.connect(ROOT / "data/museum.db"); c.row_factory = sqlite3.Row
    yield c; c.close()


def pages_of(index, q, k=5, flt=None):
    hits, _ = index.search(q, k=k, flt=flt)
    return [(index.chunk(h.chunk_id)["printed_page"], index.chunk(h.chunk_id)["printed_page_end"] or index.chunk(h.chunk_id)["printed_page"]) for h in hits], hits


def has_page(pgs, p):
    return any(a is not None and a <= p <= b for a, b in pgs)  # bản ghi bài viết/văn kiện không có trang in


def test_ret01_exact_term(index_and_chunks):
    ix, _ = index_and_chunks
    pg, _ = pages_of(ix, "Đội sơn cầu 337")
    assert has_page(pg, 185)


def test_ret04_place_name(index_and_chunks):
    ix, _ = index_and_chunks
    pg, _ = pages_of(ix, "Trung Giã Thái Nguyên")
    assert has_page(pg, 44)


def test_ret06_date_query(index_and_chunks):
    ix, _ = index_and_chunks
    pg, _ = pages_of(ix, "ngày 2-8-1967 cột cờ bị đánh gãy")
    assert has_page(pg, 191)


def test_ret07_multilingual(index_and_chunks):
    ix, _ = index_and_chunks
    pg_en, _ = pages_of(ix, "painting the bridge two colors 1959")
    assert any(has_page(pg_en, p) for p in (185, 186, 187))
    pg_zh, hits_zh = pages_of(ix, "贤良桥 旗杆 38.6米")
    # sau đợt bổ sung, bài SRC003 (dòng 77, nêu đúng trụ cờ 38,6 m) có thể xếp trên trang sách: top-5 phải chứa thông tin 38,6 m,
    # và trang sách 188–189 vẫn phải nằm trong top-10
    assert any(has_page(pg_zh, p) for p in (188, 189)) or any("38,6" in ix.chunk(h.chunk_id)["content"] for h in hits_zh)
    pg_zh10, _ = pages_of(ix, "贤良桥 旗杆 38.6米", k=10)
    assert any(has_page(pg_zh10, p) for p in (188, 189))


def test_ret09_irrelevant_returns_low_coverage(index_and_chunks):
    ix, _ = index_and_chunks
    hits, qp = ix.search("Who won the 2018 football world cup?", k=3)
    assert all(h.coverage < 0.2 for h in hits)


def test_ret10_metadata_filter(index_and_chunks):
    ix, _ = index_and_chunks
    hits, _ = ix.search("Geneva Final Declaration provisional boundary", k=5, flt={"source_types": ["HISTORICAL_DOCUMENT"]})
    assert hits and all(ix.chunk(h.chunk_id)["source_type"] == "HISTORICAL_DOCUMENT" for h in hits)
    hits, _ = ix.search("cột cờ", k=5, flt={"printed_from": 187, "printed_to": 192, "source_ids": ["SRC001"]})
    assert hits and all((ix.chunk(h.chunk_id)["printed_page_end"] or ix.chunk(h.chunk_id)["printed_page"]) >= 187 and ix.chunk(h.chunk_id)["printed_page"] <= 192 for h in hits)


def test_ret13_14_page_and_chapter_metadata(index_and_chunks):
    ix, chunks = index_and_chunks
    for c in chunks:
        if c["source_id"] == "SRC001":
            assert c["printed_page"] and c["pdf_page"], c["chunk_id"]
            assert c["chapter_id"], c["chunk_id"]  # trang cấu trúc (bìa, ngăn phần, mục lục) đã bị loại khỏi chunk
            assert c["printed_page"] in (2 * c["pdf_page"] - 1, 2 * c["pdf_page"]) or c["printed_page"] <= 2 * c["pdf_page_end"]
        assert c["source_title"] and c["source_type"] and c["verification_status"]


def test_ret11_hybrid_components_present(index_and_chunks):
    ix, _ = index_and_chunks
    _, hits = pages_of(ix, "cột cờ Hiền Lương")
    assert {"bm25_orig", "bm25_exp", "char_tfidf", "phrase"} <= set(hits[0].components)


def test_ret15_image_retrieval_metadata_based(index_and_chunks):
    from app.database import repository as R
    from app.database.database import session_scope
    from app.services.retrieval_service import ImageIndex
    with session_scope() as d:
        imgs = R.load_images(d)
    ii = ImageIndex(imgs)
    res = ii.search("loa phóng thanh", k=3, min_coverage=0.5)
    assert res and any("loudspeakers" in r[0]["related_book_topics"] for r in res)
    res2 = ii.search("Nam Bắc một nhà", k=3, min_coverage=0.0)
    assert res2


# ---------- PDF-* ----------
def test_pdf01_02_all_pages_processed(db):
    assert db.execute("select count(distinct pdf_page) from pages").fetchone()[0] == 130
    assert db.execute("select count(*) from pages").fetchone()[0] == 260
    assert not list((ROOT / "data/processed/ocr").glob("*.error.json"))


def test_pdf08_09_page_order_and_printed_numbers(db):
    rows = db.execute("select pdf_page, side, printed_page from pages order by id").fetchall()
    for r in rows:
        assert r["printed_page"] == (2 * r["pdf_page"] - 1 if r["side"] == "left" else 2 * r["pdf_page"])
    agree = db.execute("select sum(printed_page_agrees=1), sum(printed_page_agrees=0) from pages").fetchone()
    assert agree[0] / (agree[0] + agree[1]) > 0.9  # số in OCR khớp suy luận >90% trên các trang đọc được


def test_pdf03_11_ocr_marks_uncertainty(db):
    low = db.execute("select count(*) from pages where needs_review=1").fetchone()[0]
    assert low >= 1
    assert db.execute("select count(*) from pages where ocr_mean_conf is null and is_blank=0").fetchone()[0] == 0


def test_pdf10_event_anchors_verified(db):
    assert db.execute("select count(*) from events where verification_status='anchor_not_found'").fetchone()[0] == 0


# ---------- IMG-* ----------
REQ = ["image_id", "filename", "image_path", "title", "visual_description", "historical_context", "location", "time_period", "estimated_date", "main_objects", "visible_text",
       "people_description", "historical_significance", "related_events", "related_book_topics", "related_book_pages", "keywords", "source", "confidence_level", "verification_notes", "duplicate_group"]


def test_img01_02_03_metadata_complete(db):
    rows = db.execute("select * from images where source_id='SRC002'").fetchall()  # bộ Archive_2 gốc (không đổi sau đợt bổ sung)
    assert len(rows) == 34
    for r in rows:
        assert (ROOT / r["image_path"]).is_file()
        for f in REQ:
            assert f in r.keys()
        assert len(r["visual_description"]) > 40 and r["verification_notes"] and r["sha256"] and r["phash"]


def test_img04_10_no_invented_dates_or_identities(db):
    for r in db.execute("select image_id, estimated_date, time_period, people_description, historical_context from images where source_id='SRC002'"):
        assert r["estimated_date"] == "Chưa xác định" and r["time_period"] == "Chưa xác định", r["image_id"]
        assert re.search(r"không xác định|không rõ|không có người|không phải người thật", r["people_description"], re.I), r["image_id"]
        assert not re.search(r"\b(Hồ Chí Minh|Ngô Đình Diệm|Westmoreland)\b", r["people_description"])  # không gán tên người trong ảnh


def test_img08_09_duplicates_recorded_not_deleted(db):
    assert len(list((ROOT / "data/raw/archive2").glob("*.jpg"))) == 34
    groups = db.execute("select duplicate_group, count(*) c from images where duplicate_group is not null and kind='archive_photo' group by 1").fetchall()
    # DUP-S024: IMG036 (Archive_4) là cùng bức ảnh với IMG024 (Archive_2) – cả hai được giữ
    assert {g[0]: g[1] for g in groups} == {"DUP-A": 2, "DUP-B": 2, "DUP-C": 2, "DUP-D": 2, "DUP-E": 2, "DUP-F": 2, "DUP-G": 2, "DUP-S024": 2}
    assert db.execute("select count(*) from relations where relation='variant_of_same_photograph'").fetchone()[0] == 8
    assert db.execute("select count(*) from relations where relation='same_photograph_as_book_figure'").fetchone()[0] >= 3


def test_img06_07_book_figures_have_page_and_caption(db):
    figs = db.execute("select * from images where kind='book_figure'").fetchall()
    assert len(figs) == 12
    for f in figs:
        assert f["pdf_page"] and f["printed_page"] and f["bbox"] and f["caption"] and f["width"] > 100
    assert db.execute("select count(*) from images where kind='cover_design' and in_gallery=1").fetchone()[0] == 0


def test_macosx_metadata_excluded():
    assert not any("__MACOSX" in str(p) for p in (ROOT / "data/raw/archive2").rglob("*"))


# ---------- Bảo mật ----------
def test_safe_join_blocks_traversal(tmp_path):
    with pytest.raises(ValueError):
        safe_join(tmp_path, "../../etc/passwd")
    assert safe_join(tmp_path, "a/b.png").is_relative_to(tmp_path.resolve())


def test_log_redaction():
    s = redact("Authorization: Bearer abcdef1234567890xyz and xi-api-key: sk_abcdefghijk123456 api_key=SUPERSECRET123456")
    assert "abcdef1234567890xyz" not in s and "SUPERSECRET123456" not in s and "sk_abcdefghijk" not in s


def test_no_secrets_in_repository():
    pat = re.compile(r"(sk_[A-Za-z0-9]{20,}|[0-9a-f]{32}\.[A-Za-z0-9_\-]{20,}|(?i:api[_-]?key)\s*=\s*['\"]?[A-Za-z0-9]{24,})")
    bad = []
    for p in ROOT.rglob("*"):
        if p.is_file() and p.suffix in {".py", ".ts", ".tsx", ".json", ".md", ".yml", ".example", ".env", ".html"} and "node_modules" not in p.parts and ".git" not in p.parts and "data" not in p.parts[len(ROOT.parts):][:1]:
            try:
                t = p.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            if p.name == "test_retrieval_and_data.py":
                continue
            if pat.search(t):
                bad.append(str(p))
    assert not bad, bad
    assert not (ROOT / "backend/.env").exists()
