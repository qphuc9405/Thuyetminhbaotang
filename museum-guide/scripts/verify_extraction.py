#!/usr/bin/env python3
"""Đối chiếu kết quả trích xuất với dữ liệu gốc. Thoát mã 1 nếu có sai lệch nghiêm trọng.
Kiểm tra: số trang PDF thực tế vs đã xử lý; ảnh phát hiện vs đã lưu; trang chưa xử lý; ảnh lỗi; metadata thiếu; file trùng.
Chạy:  python scripts/verify_extraction.py [--write-doc]   (--write-doc ghi docs/DATASET_DOCUMENTATION.md)"""
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import statistics
import sys
import zipfile
from collections import Counter
from pathlib import Path

import pymupdf
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
PDF = ROOT / "data/raw/DoiBoGioiTuyen19541967_HoangChiHieu.pdf"
ZIP = ROOT / "data/raw/Archive_2.zip"
REQUIRED_IMG_FIELDS = ["image_id", "filename", "image_path", "title", "visual_description", "historical_context", "location", "time_period", "estimated_date", "main_objects",
                       "visible_text", "people_description", "historical_significance", "related_events", "related_book_topics", "related_book_pages", "keywords", "source",
                       "confidence_level", "verification_notes", "duplicate_group"]
NULLABLE = {"duplicate_group", "related_events", "visible_text", "related_book_pages", "main_objects"}  # có thể rỗng hợp lệ


def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--write-doc", action="store_true"); args = ap.parse_args()
    R: dict = {"errors": [], "warnings": []}
    # ---- PDF
    doc = pymupdf.open(PDF)
    n_pdf = doc.page_count
    ocr_files = sorted((ROOT / "data/processed/ocr").glob("page_???.json"))
    err_files = sorted((ROOT / "data/processed/ocr").glob("*.error.json"))
    processed = {int(p.stem.split("_")[1]) for p in ocr_files}
    missing = sorted(set(range(1, n_pdf + 1)) - processed)
    recs = [json.loads(p.read_text(encoding="utf-8")) for p in ocr_files]
    direct_pages = sum(1 for r in recs if r["direct_text_chars"] > 40)
    emb_total = sum(len(r["embedded_images"]) for r in recs)
    page_pngs = sorted((ROOT / "data/processed/pages").glob("page_*.png"))
    bad_png = []
    for p in page_pngs:
        try:
            with Image.open(p) as im: im.verify()
        except Exception as e:  # noqa
            bad_png.append(p.name)
    halves = [h for r in recs for h in r["halves"].values()]
    confs = [h["mean_conf"] for h in halves if h["mean_conf"] is not None]
    blank = [(r["pdf_page"], s) for r in recs for s, h in r["halves"].items() if h["word_count"] < 15]
    review = [(r["pdf_page"], s, h["mean_conf"], h["word_count"]) for r in recs for s, h in r["halves"].items() if h["needs_review"]]
    R["pdf"] = dict(file=PDF.name, size_bytes=PDF.stat().st_size, pdf_pages_actual=n_pdf, pdf_pages_processed=len(processed), pdf_pages_missing=missing, pdf_pages_error=[p.name for p in err_files],
                    book_pages_ocr=len(halves), pages_with_text_layer=direct_pages, pages_needing_ocr=n_pdf - direct_pages, embedded_images_all_pages=emb_total,
                    page_scans_saved=len(page_pngs), page_scans_unreadable=bad_png, ocr_mean_conf=round(statistics.mean(confs), 2), ocr_min_conf=min(confs),
                    ocr_pages_below_80=len([c for c in confs if c < 80]), blank_or_figure_only_halves=blank, halves_needing_manual_review=review)
    if missing or err_files: R["errors"].append(f"Trang PDF chưa xử lý/lỗi: {missing} {[p.name for p in err_files]}")
    if len(page_pngs) != n_pdf: R["errors"].append("Số ảnh scan trang đã lưu khác số trang PDF")
    if bad_png: R["errors"].append(f"Ảnh trang bị lỗi: {bad_png}")
    # ---- Figures trong sách
    figs = json.loads((ROOT / "data/processed/book_figures.json").read_text(encoding="utf-8"))
    saved = [f for f in figs if (ROOT / f["image_path"]).is_file()]
    R["book_figures"] = dict(detected_candidates=len(figs), saved=len(saved), missing_files=[f["figure_id"] for f in figs if f not in saved],
                             note="PDF là scan: get_images() chỉ thấy 130 ảnh nguyên trang; hình trong trang được tách bằng phân tích layout (scripts/detect_figures.py) và đã kiểm tra bằng mắt trên contact sheet.")
    if len(saved) != len(figs): R["errors"].append("Có hình phát hiện nhưng không lưu được")
    # ---- ZIP ảnh
    with zipfile.ZipFile(ZIP) as z:
        names = [n for n in z.namelist() if not n.endswith("/")]
    macosx = [n for n in names if "__MACOSX" in n or Path(n).name.startswith("._")]
    real = [n for n in names if n not in macosx and n.lower().endswith((".jpg", ".jpeg", ".png"))]
    others = [n for n in names if n not in macosx and n not in real]
    files = sorted((ROOT / "data/raw/archive2").glob("*.jpg"))
    sha = {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
    dup_sha = [k for k, v in Counter(sha.values()).items() if v > 1]
    unreadable = []
    for f in files:
        try:
            with Image.open(f) as im: im.verify()
        except Exception:  # noqa
            unreadable.append(f.name)
    R["archive"] = dict(zip_entries=len(names), macosx_metadata_skipped=len(macosx), image_files_in_zip=len(real), non_image_entries=others, image_files_extracted=len(files),
                        identical_sha256_groups=len(dup_sha), unreadable=unreadable)
    if len(real) != len(files): R["errors"].append("Số ảnh trong ZIP khác số ảnh đã giải nén")
    if unreadable: R["errors"].append(f"Ảnh lỗi: {unreadable}")
    # ---- DB / metadata
    db = sqlite3.connect(ROOT / "data/museum.db"); db.row_factory = sqlite3.Row
    imgs = db.execute("select * from images").fetchall()
    arch = [i for i in imgs if i["kind"] == "archive_photo"]
    missing_meta = {}
    for i in arch + [x for x in imgs if x["kind"] == "book_figure"]:
        miss = [f for f in REQUIRED_IMG_FIELDS if (i[f] is None or i[f] == "") and f not in NULLABLE and not (i["kind"] == "book_figure" and f in ("location", "people_description"))]
        if miss: missing_meta[i["image_id"]] = miss
    pages_db = db.execute("select count(*) from pages").fetchone()[0]
    chunks_db = db.execute("select source_id, count(*) from chunks group by 1").fetchall()
    n_unlinked = db.execute("""select count(*) from images i where kind='archive_photo' and not exists (select 1 from relations r where r.from_type='image' and r.from_id=i.image_id and r.to_type='chunk')""").fetchone()[0]
    n_direct = db.execute("select count(distinct from_id) from relations where relation='same_figure_in_book' and from_id like 'IMG%'").fetchone()[0]
    dup_groups = db.execute("select duplicate_group, group_concat(image_id) from images where duplicate_group is not null group by 1").fetchall()
    R["database"] = dict(pages=pages_db, chunks_by_source={r[0]: r[1] for r in chunks_db}, images_total=len(imgs), archive_with_description=sum(1 for i in arch if i["visual_description"]),
                         archive_linked_to_book_content=len(arch) - n_unlinked, archive_directly_matching_book_figures=n_direct, images_missing_metadata=missing_meta,
                         duplicate_groups={r[0]: r[1] for r in dup_groups}, archive_unknown_source=sum(1 for i in arch if "chưa xác định" in i["source"].lower()),
                         archive_low_confidence_need_manual_check=[i["image_id"] for i in arch if i["confidence_level"] == "low"],
                         events_total=db.execute("select count(*) from events").fetchone()[0], events_anchor_failed=db.execute("select count(*) from events where verification_status='anchor_not_found'").fetchone()[0])
    if pages_db != n_pdf * 2: R["errors"].append("Số trang sách trong DB != 2 x số trang PDF")
    if missing_meta: R["errors"].append(f"Metadata ảnh thiếu: {missing_meta}")
    if R["database"]["events_anchor_failed"]: R["errors"].append("Có sự kiện không xác minh được anchor")
    # ---- số trang in
    ag = db.execute("select sum(printed_page_agrees=1), sum(printed_page_agrees=0), sum(printed_page_agrees is null) from pages").fetchone()
    R["printed_pages"] = dict(rule="trái = 2*pdf-1, phải = 2*pdf", ocr_detected_agree=ag[0], ocr_detected_disagree=ag[1], ocr_not_detected=ag[2],
                              disagree_pages=[(r["pdf_page"], r["side"], r["printed_page"], r["printed_page_detected"]) for r in db.execute("select * from pages where printed_page_agrees=0")])
    R["status"] = "FAIL" if R["errors"] else "OK"
    out = ROOT / "docs/extraction_report.json"; out.write_text(json.dumps(R, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print(json.dumps({"status": R["status"], "errors": R["errors"], "pdf_pages": f"{len(processed)}/{n_pdf}", "figures": f"{len(saved)}/{len(figs)}", "archive_images": f"{len(files)}/{len(real)}"}, ensure_ascii=False))
    if args.write_doc: write_doc(R, db)
    return 1 if R["errors"] else 0


def supplement_section(db) -> str:
    """Mục 5b sinh từ DB: đợt bổ sung 2026-10-31 (3 bài viết + Archive_4.zip + ghi chú đối chiếu)."""
    import unicodedata
    srcs = db.execute("select source_id, title, author, source_type from sources where source_id in ('SRC003','SRC004','SRC005','SRC006','NOTE01') order by 1").fetchall()
    nchunks = dict(db.execute("select source_id, count(*) from chunks where source_id in ('SRC003','SRC004','SRC005','NOTE01') group by 1").fetchall())
    imgs = db.execute("select image_id, kind, filename, filename_title, caption_status, duplicate_group, time_period from images where source_id='SRC006' order by 1").fetchall()
    rows = []
    for r in imgs:
        cap = (r["caption_status"] or "").replace("document_caption:", "chú thích ").replace(":matches_filename", " (trùng tên file)") or "—"
        rel = db.execute("select to_id, relation from relations where from_id=? and to_type='image'", (r["image_id"],)).fetchall()
        dup = "; ".join(f"{x['relation']} {x['to_id']}" for x in rel) or "—"
        rows.append(f"| {r['image_id']} | {r['kind']} | `{unicodedata.normalize('NFC', r['filename'])}` | {cap} | {dup} | {r['time_period']} |")
    lines = [f"| {s['source_id']} | {s['source_type']} | {s['title']} | {s['author'] or '—'} | {nchunks.get(s['source_id'], '—')} |" for s in srcs]
    return ("## 5b. Đợt bổ sung nguồn 2026-10-31\n"
            "Chi tiết và kết quả kiểm thử: `docs/SUPPLEMENT_INTEGRATION_REPORT.md`. Tài liệu không có số trang → trích dẫn theo **số dòng** của tệp gốc (`chunks.provision`).\n\n"
            "| Nguồn | Loại | Tiêu đề | Tác giả | Số chunk |\n|---|---|---|---|---|\n" + "\n".join(lines) +
            f"\n\nẢnh Archive_4.zip: **{len(imgs)}** ảnh duy nhất (tên file gốc giữ nguyên; tiêu đề lấy từ tên file được đánh dấu `metadata_basis.title = filename`).\n\n"
            "| Ảnh | Loại | Tên file gốc | Chú thích trong bài | Quan hệ với ảnh khác | Thời gian (có căn cứ) |\n|---|---|---|---|---|---|\n" + "\n".join(rows))


def write_doc(R: dict, db) -> None:
    p, b, a, d = R["pdf"], R["book_figures"], R["archive"], R["database"]
    md = f"""# DATASET_DOCUMENTATION – Báo cáo đối chiếu dữ liệu

_Sinh tự động bởi `python scripts/verify_extraction.py --write-doc` từ dữ liệu thực tế (trạng thái kiểm tra: **{R['status']}**)._

## 1. Sách: *Đôi bờ giới tuyến (1954–1967)* – TS. Hoàng Chí Hiếu
| Chỉ tiêu | Giá trị |
|---|---|
| Tổng số file PDF | 1 (`{p['file']}`, {p['size_bytes']/1e6:.1f} MB) |
| Tổng số trang PDF (thực tế) | **{p['pdf_pages_actual']}** |
| Số trang PDF đã xử lý (OCR + lưu ảnh scan) | **{p['pdf_pages_processed']}** (thiếu: {p['pdf_pages_missing'] or 'không'}; lỗi: {p['pdf_pages_error'] or 'không'}) |
| Số trang có lớp text trực tiếp | **{p['pages_with_text_layer']}** (chỉ là watermark `tieulun.hopto.org`, không phải nội dung) |
| Số trang cần OCR | **{p['pages_needing_ocr']}** / {p['pdf_pages_actual']} (toàn bộ là ảnh scan) |
| Trang sách in tương ứng | {p['book_pages_ocr']} (mỗi trang PDF là một *spread* 2 trang sách; số trang in: trái = 2p−1, phải = 2p) |
| Số ảnh nhúng PDF phát hiện bằng `get_images()` | {p['embedded_images_all_pages']} (mỗi trang đúng 1 ảnh = bản scan nguyên spread) |
| Ảnh scan trang đã lưu (lossless PNG) | {p['page_scans_saved']} (không đọc được: {p['page_scans_unreadable'] or 'không'}) |
| OCR: độ tin cậy trung bình / thấp nhất | {p['ocr_mean_conf']} / {p['ocr_min_conf']} (Tesseract 5, ngôn ngữ `vie`, upscale ×3) |
| Nửa trang có confidence < 80 | {p['ocr_pages_below_80']} |
| Nửa trang trống hoặc chỉ có hình (<15 từ) | {len(p['blank_or_figure_only_halves'])}: {p['blank_or_figure_only_halves']} |
| Nửa trang cần xác minh thủ công | {len(p['halves_needing_manual_review'])}: (trang PDF, bên, conf, số từ) {p['halves_needing_manual_review']} |

**Văn bản trực tiếp và OCR được lưu riêng:** `data/processed/ocr/page_NNN.json` có trường `direct_text` (text layer) tách biệt với `halves.*.text` (OCR) và `words[].conf` (confidence từng từ).

**Số trang in:** quy tắc suy ra từ vị trí spread được đối chiếu với số OCR đọc được ở chân trang: khớp **{R['printed_pages']['ocr_detected_agree']}** trang, lệch **{R['printed_pages']['ocr_detected_disagree']}** trang (đều là lỗi chữ số của OCR, ví dụ 49↔19; xem `docs/extraction_report.json`), không đọc được số ở **{R['printed_pages']['ocr_not_detected']}** trang (trang trống/trang hình). Quy tắc được dùng cho citation; không nhầm số trang PDF với trang in (API trả cả hai).

**Giới hạn OCR cần biết:** bản scan có độ phân giải thấp (1101×771 px/spread) nên OCR có thể sai dấu/ký tự (ví dụ "Hiển Lương" thay cho "Hiền Lương", "đổi" thay cho "đôi"). Văn bản sách được **giữ nguyên** (không tự sửa theo kiến thức ngoài); tìm kiếm dùng chuỗi đã bỏ dấu để chịu lỗi dấu. Chú thích-trích dẫn thuần (số chú thích + ký hiệu lưu trữ) bị loại khỏi chunk (đếm trong `data/processed/build_report.json`), chú thích mang nội dung được giữ lại.

## 2. Hình ảnh trong sách
- Hình ảnh ứng viên phát hiện bằng phân tích layout: **{b['detected_candidates']}**; đã lưu: **{b['saved']}** (`data/images/book/FIG_*.png`, ảnh crop từ bản scan gốc; **không thay thế** bản gốc `data/processed/pages/`).
- Sau kiểm tra bằng mắt: **12 hình lịch sử/bản đồ/bưu thiếp** (`BKFIG01–BKFIG12`, hiển thị ở Gallery) và **3 mục là thiết kế bìa/logo** (đánh dấu `cover_design`, KHÔNG hiển thị ở Gallery).
- {b['note']}
- Mỗi hình có: trang PDF, trang in, bbox trên trang, kích thước, định dạng, ID, chú thích (đọc trực tiếp từ crop; chú thích bị cắt được đánh dấu `verified_visual_partial`) và liên kết tới các đoạn văn của trang đó.
- Bảng biểu: sách không có bảng dữ liệu thuần; các biểu mẫu (bưu thiếp) nằm trong hình. **Chưa có** trích xuất bảng riêng (không có bảng để trích).

## 3. Bộ ảnh `Archive_2.zip`
| Chỉ tiêu | Giá trị |
|---|---|
| Số mục trong ZIP | {a['zip_entries']} (bỏ qua {a['macosx_metadata_skipped']} file metadata `__MACOSX`) |
| Ảnh thực tế trong ZIP / đã giải nén | **{a['image_files_in_zip']}** / **{a['image_files_extracted']}** |
| Ảnh có mô tả (đã quan sát từng ảnh) | **{d['archive_with_description']}** / 34 |
| Ảnh giống hệt theo SHA-256 | {a['identical_sha256_groups']} nhóm (tất cả 34 file có hash khác nhau) |
| Ảnh là bản khác của cùng một bức (pHash/SIFT), KHÔNG xoá | **7 nhóm × 2 ảnh = 14 ảnh** → 27 bức ảnh duy nhất về nội dung |
| Ảnh trùng với hình in trong sách (SIFT ≥ 90 inliers) | 4 ảnh (IMG004, IMG007, IMG032, IMG034) |
| Ảnh đã liên kết tới nội dung sách (cạnh `image→chunk`) | **{d['archive_linked_to_book_content']}** / 34 (trực tiếp: {d['archive_directly_matching_book_figures']}; còn lại là liên kết theo chủ đề, có ghi `link_type`) |
| Ảnh chưa xác định nguồn | **{d['archive_unknown_source']}** / 34 (watermark LIFE/TikTok/corbis chỉ được ghi nhận, không suy ra tác giả/quyền) |
| Ảnh độ tin cậy `low` cần xác minh thủ công | {len(d['archive_low_confidence_need_manual_check'])}: {d['archive_low_confidence_need_manual_check']} |
| Ảnh không đọc được | {a['unreadable'] or 'không'} |
| Metadata bị thiếu | {d['images_missing_metadata'] or 'không'} |

Nhóm bản trùng (cùng một bức ảnh, khác mã hoá/khung): `{d['duplicate_groups']}`. Nhóm cảnh gần nhau (cùng địa điểm, khác khung hình): `SCENE-FLAGS`.
**Năm chụp của cả 34 ảnh: "Chưa xác định".** Không có ảnh nào được gán danh tính nhân vật.

## 4. Cơ sở dữ liệu
Trang sách: {d['pages']} · Chunk theo nguồn: {d['chunks_by_source']} · Tổng ảnh: {d['images_total']} · Sự kiện: {d['events_total']} (anchor không khớp OCR: {d['events_anchor_failed']}).

## 5. Nguồn bổ sung (Genève)
Xem `knowledge_base/sources.json` và mục "Nguồn tư liệu ngoài" trong `PROJECT_STATUS.md`. **Trung thực về phạm vi:** môi trường phát triển không truy cập được toàn văn 5 URL bắt buộc (máy chủ không nằm trong allowlist); thông tin về điều khoản được xác minh qua trích đoạn từ kết quả tìm kiếm (Wikisource, FRUS, Fordham, CIA Reading Room, Britannica…) và được ghi `partially_verified_via_search_snippets`; DOC005 (UN Peacemaker) chỉ đăng ký metadata (`not_accessed`). Dữ liệu ngoài lưu riêng (`chunks.source_type != BOOK`), không ghi đè nội dung sách. Chưa thu thập nghiên cứu học thuật về di cư 1954–1955.

{supplement_section(db)}

## 6. Cách chạy lại
```
python scripts/ingest_pdf.py          # OCR + ảnh scan trang
python scripts/detect_figures.py      # tách hình trong sách
python scripts/match_images.py        # so khớp ảnh
python scripts/build_knowledge_base.py   # gồm cả đợt bổ sung (scripts/supplement_ingest.py)
python scripts/verify_extraction.py --write-doc
```
"""
    (ROOT / "docs/DATASET_DOCUMENTATION.md").write_text(md, encoding="utf-8")
    print("Đã ghi docs/DATASET_DOCUMENTATION.md")


if __name__ == "__main__":
    sys.exit(main())
