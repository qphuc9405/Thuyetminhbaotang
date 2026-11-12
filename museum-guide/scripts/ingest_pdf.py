#!/usr/bin/env python3
"""Bước 1 của ingestion: trích xuất toàn bộ trang PDF.

Với file "Đôi bờ giới tuyến" (PDF scan, mỗi trang PDF là một *spread* gồm 2 trang sách):
  - Lưu ảnh scan gốc của từng trang PDF (lossless) -> data/processed/pages/page_NNN.png
  - Thử trích text trực tiếp (PyMuPDF) và ghi riêng (khác với OCR)
  - Tách spread thành trang trái / trang phải, OCR bằng Tesseract (vie), lưu confidence từng từ
  - Ghi nhận mọi ảnh nhúng PDF (get_images) -> data/processed/pdf_embedded_images.json
  - Kết quả mỗi trang PDF -> data/processed/ocr/page_NNN.json

Chạy:  python scripts/ingest_pdf.py [--pdf PATH] [--workers 2] [--scale 3] [--force]
Có thể chạy lại: trang đã có JSON sẽ được bỏ qua (trừ khi --force).
"""
from __future__ import annotations

import argparse
import io
import json
import os
import re
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

os.environ.setdefault("OMP_THREAD_LIMIT", "1")

import pymupdf  # noqa: E402
import pytesseract  # noqa: E402
from PIL import Image  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PDF = ROOT / "data/raw/DoiBoGioiTuyen19541967_HoangChiHieu.pdf"
PAGES_DIR = ROOT / "data/processed/pages"
OCR_DIR = ROOT / "data/processed/ocr"

LOW_CONF_WORD = 60  # từ có conf < 60 bị coi là không chắc chắn
LOW_CONF_PAGE = 80  # trang có conf trung bình < 80 cần xác minh thủ công


def _page_image(doc: pymupdf.Document, page: pymupdf.Page) -> Image.Image:
    """Lấy ảnh scan gốc nhúng trong trang (độ phân giải gốc); nếu không có thì render 200dpi."""
    imgs = page.get_images(full=True)
    if imgs:
        # chọn ảnh có diện tích lớn nhất
        best = max(imgs, key=lambda i: i[2] * i[3])
        pix = pymupdf.Pixmap(doc, best[0])
        if pix.n - pix.alpha >= 4:  # CMYK -> RGB
            pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
        return Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
    pix = page.get_pixmap(dpi=200)
    return Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")


def _ocr_half(img: Image.Image, scale: int, psm: int = 4) -> dict:
    gray = img.convert("L")
    big = gray.resize((gray.width * scale, gray.height * scale), Image.LANCZOS)
    data = pytesseract.image_to_data(
        big, lang="vie", config=f"--psm {psm}", output_type=pytesseract.Output.DICT
    )
    words = []
    lines: dict[tuple, list] = {}
    for i, txt in enumerate(data["text"]):
        txt = (txt or "").strip()
        conf = float(data["conf"][i])
        if not txt or conf < 0:
            continue
        w = {
            "text": txt,
            "conf": conf,
            "x": data["left"][i] / scale,
            "y": data["top"][i] / scale,
            "w": data["width"][i] / scale,
            "h": data["height"][i] / scale,
            "block": data["block_num"][i],
            "par": data["par_num"][i],
            "line": data["line_num"][i],
        }
        words.append(w)
        lines.setdefault((w["block"], w["par"], w["line"]), []).append(w)
    # dựng text theo đoạn
    out_lines = []
    last_par = None
    for key in sorted(lines, key=lambda k: (min(x["y"] for x in lines[k]), k)):
        ws = sorted(lines[key], key=lambda x: x["x"])
        par = (key[0], key[1])
        if last_par is not None and par != last_par:
            out_lines.append("")
        last_par = par
        out_lines.append(" ".join(x["text"] for x in ws))
    text = "\n".join(out_lines).strip()
    confs = [w["conf"] for w in words]
    return {
        "text": text,
        "word_count": len(words),
        "mean_conf": round(sum(confs) / len(confs), 2) if confs else None,
        "low_conf_words": sum(1 for c in confs if c < LOW_CONF_WORD),
        "words": words,
    }


def _detect_printed_page(half: dict, height: float) -> dict:
    """Tìm số trang in: token toàn chữ số nằm ở ~12% dưới cùng của trang."""
    cands = []
    for w in half["words"]:
        if w["y"] > height * 0.86 and re.fullmatch(r"\d{1,3}", w["text"]):
            cands.append((w["conf"], int(w["text"])))
    if not cands:
        return {"value": None, "conf": None}
    conf, val = max(cands)
    return {"value": val, "conf": conf}


def process_page(args: tuple) -> dict:
    pdf_path, idx, scale, force = args
    pno = idx + 1
    out_json = OCR_DIR / f"page_{pno:03d}.json"
    if out_json.exists() and not force:
        return {"pdf_page": pno, "status": "skipped"}
    t0 = time.time()
    try:
        doc = pymupdf.open(pdf_path)
        page = doc[idx]
        direct = page.get_text().strip()
        embedded = [
            {"xref": i[0], "width": i[2], "height": i[3], "colorspace": i[5], "filter": i[8]}
            for i in page.get_images(full=True)
        ]
        img = _page_image(doc, page)
        PAGES_DIR.mkdir(parents=True, exist_ok=True)
        img_path = PAGES_DIR / f"page_{pno:03d}.png"
        img.save(img_path)
        w, h = img.size
        mid = w // 2
        halves = {"left": img.crop((0, 0, mid, h)), "right": img.crop((mid, 0, w, h))}
        result_halves = {}
        for side, him in halves.items():
            r = _ocr_half(him, scale)
            pp = _detect_printed_page(r, h)
            r["printed_page_detected"] = pp
            r["needs_review"] = bool(
                r["mean_conf"] is None or r["mean_conf"] < LOW_CONF_PAGE or r["word_count"] < 15
            )
            result_halves[side] = r
        rec = {
            "pdf_page": pno,
            "image_size": [w, h],
            "page_image": str(img_path.relative_to(ROOT)),
            "direct_text": direct,
            "direct_text_chars": len(direct),
            "embedded_images": embedded,
            "ocr_engine": f"tesseract {pytesseract.get_tesseract_version()} lang=vie psm=4 scale={scale}",
            "halves": result_halves,
            "elapsed_s": round(time.time() - t0, 1),
            "status": "ok",
        }
        out_json.write_text(json.dumps(rec, ensure_ascii=False), encoding="utf-8")
        return {"pdf_page": pno, "status": "ok", "elapsed": rec["elapsed_s"]}
    except Exception as e:  # ghi lỗi để verify_extraction báo cáo
        err = {"pdf_page": pno, "status": "error", "error": repr(e)}
        (OCR_DIR / f"page_{pno:03d}.error.json").write_text(json.dumps(err), encoding="utf-8")
        return err


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", default=str(DEFAULT_PDF))
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--scale", type=int, default=3)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--pages", help="vd 1-10 (tuỳ chọn, để thử)")
    a = ap.parse_args()

    OCR_DIR.mkdir(parents=True, exist_ok=True)
    doc = pymupdf.open(a.pdf)
    n = doc.page_count
    idxs = list(range(n))
    if a.pages:
        lo, hi = [int(x) for x in a.pages.split("-")]
        idxs = list(range(lo - 1, hi))
    emb_all = {
        p + 1: [{"xref": i[0], "width": i[2], "height": i[3]} for i in doc[p].get_images(full=True)]
        for p in range(n)
    }
    (ROOT / "data/processed/pdf_embedded_images.json").write_text(
        json.dumps(emb_all, indent=1), encoding="utf-8"
    )
    print(f"PDF: {a.pdf}  pages={n}  processing={len(idxs)}", flush=True)
    jobs = [(a.pdf, i, a.scale, a.force) for i in idxs]
    done = 0
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=a.workers) as ex:
        for res in ex.map(process_page, jobs):
            done += 1
            if done % 5 == 0 or res["status"] == "error":
                print(f"[{done}/{len(jobs)}] last={res} elapsed={time.time()-t0:.0f}s", flush=True)
    print("DONE", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
