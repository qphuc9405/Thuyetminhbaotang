#!/usr/bin/env python3
"""Phát hiện hình minh hoạ (ảnh, bản đồ, bảng-ảnh) nằm *trong* trang scan.

Vì PDF này là scan (mỗi trang PDF = 1 ảnh nhúng nguyên spread), PyMuPDF get_images() chỉ thấy
ảnh nguyên trang. Do đó phải phân tích layout từng nửa trang:
  1. Tạo mask "ink" (pixel tối) -> đóng hình thái học để gộp thành khối.
  2. Với từng khối đủ lớn, đo tỉ lệ diện tích được phủ bởi box từ OCR có confidence cao.
     Khối chữ -> tỉ lệ phủ cao; khối ảnh -> tỉ lệ phủ thấp.
  3. Khối ảnh được crop từ ảnh scan gốc (không sửa ảnh gốc) -> data/images/book/FIG_xxx.png
  4. Caption: các dòng OCR ngay dưới (hoặc trên) hình.

Kết quả: data/processed/book_figures.json  (ứng viên - cần verify bằng mắt, xem docs).
"""
from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
OCR_DIR = ROOT / "data/processed/ocr"
OUT_DIR = ROOT / "data/images/book"
OUT_JSON = ROOT / "data/processed/book_figures.json"

MIN_W, MIN_H = 110, 70          # px trên ảnh scan gốc
MAX_TEXT_COVER = 0.30            # tối đa tỉ lệ diện tích bị chữ OCR phủ
CONF_TEXT = 55


def half_boxes(img_w: int, half: dict, side: str):
    off = 0 if side == "left" else img_w // 2
    for w in half["words"]:
        if w["conf"] >= CONF_TEXT and len(w["text"]) >= 1:
            yield (off + w["x"], w["y"], off + w["x"] + w["w"], w["y"] + w["h"])


def detect_page(rec: dict, img: np.ndarray) -> list[dict]:
    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ink = (gray < 190).astype(np.uint8)
    # bỏ viền/bóng gáy: vùng 4% mép trên/dưới và 3% quanh gáy (giữa)
    ink[: int(h * 0.04)] = 0
    ink[int(h * 0.94):] = 0
    mid = w // 2
    ink[:, mid - int(w * 0.03): mid + int(w * 0.03)] = 0
    ink[:, : int(w * 0.03)] = 0
    ink[:, int(w * 0.97):] = 0
    # che chữ có confidence cao
    textmask = np.zeros_like(ink)
    for side in ("left", "right"):
        for (x0, y0, x1, y1) in half_boxes(w, rec["halves"][side], side):
            cv2.rectangle(textmask, (int(x0) - 2, int(y0) - 2), (int(x1) + 2, int(y1) + 2), 1, -1)
    # dilate text mask để xoá hẳn khối chữ (kể cả dấu)
    textmask_d = cv2.dilate(textmask, np.ones((5, 5), np.uint8))
    residual = ink.copy()
    residual[textmask_d > 0] = 0
    # gộp thành khối
    k = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
    closed = cv2.morphologyEx(residual, cv2.MORPH_CLOSE, k)
    closed = cv2.dilate(closed, np.ones((5, 5), np.uint8))
    n, lab, stats, _ = cv2.connectedComponentsWithStats(closed, 8)
    figs = []
    for i in range(1, n):
        x, y, bw, bh, area = stats[i]
        if bw < MIN_W or bh < MIN_H:
            continue
        box_mask = np.zeros_like(ink)
        box_mask[y:y + bh, x:x + bw] = 1
        cover = float((textmask * box_mask).sum()) / float(bw * bh)
        ink_density = float((ink * box_mask).sum()) / float(bw * bh)
        if cover > MAX_TEXT_COVER or ink_density < 0.04:
            continue
        figs.append({"bbox": [int(x), int(y), int(bw), int(bh)],
                     "text_cover": round(cover, 3), "ink_density": round(ink_density, 3)})
    # gộp các hộp chồng lấn/gần nhau
    merged = True
    while merged:
        merged = False
        for a in range(len(figs)):
            for b in range(a + 1, len(figs)):
                ax, ay, aw, ah = figs[a]["bbox"]
                bx, by, bw_, bh_ = figs[b]["bbox"]
                if ax < bx + bw_ + 12 and bx < ax + aw + 12 and ay < by + bh_ + 12 and by < ay + ah + 12:
                    x0, y0 = min(ax, bx), min(ay, by)
                    x1, y1 = max(ax + aw, bx + bw_), max(ay + ah, by + bh_)
                    figs[a] = {"bbox": [x0, y0, x1 - x0, y1 - y0],
                               "text_cover": min(figs[a]["text_cover"], figs[b]["text_cover"]),
                               "ink_density": max(figs[a]["ink_density"], figs[b]["ink_density"])}
                    figs.pop(b)
                    merged = True
                    break
            if merged:
                break
    return [f for f in figs if f["bbox"][2] >= MIN_W and f["bbox"][3] >= MIN_H]


def caption_for(rec: dict, bbox: list[int], img_w: int) -> str:
    x, y, bw, bh = bbox
    side = "left" if (x + bw / 2) < img_w // 2 else "right"
    off = 0 if side == "left" else img_w // 2
    lines: dict[tuple, list] = {}
    for wd in rec["halves"][side]["words"]:
        cx = off + wd["x"] + wd["w"] / 2
        if x - 20 <= cx <= x + bw + 20 and (y + bh - 4) <= wd["y"] <= (y + bh + 38):
            lines.setdefault((wd["block"], wd["par"], wd["line"]), []).append(wd)
    out = []
    for k in sorted(lines, key=lambda k: min(w["y"] for w in lines[k])):
        out.append(" ".join(w["text"] for w in sorted(lines[k], key=lambda w: w["x"])))
    return " ".join(out).strip()


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    results = []
    for p in range(1, 131):
        rec = json.loads((OCR_DIR / f"page_{p:03d}.json").read_text(encoding="utf-8"))
        img = cv2.imread(str(ROOT / rec["page_image"]))
        for j, f in enumerate(detect_page(rec, img), 1):
            x, y, bw, bh = f["bbox"]
            pad = 4
            crop = img[max(0, y - pad): y + bh + pad, max(0, x - pad): x + bw + pad]
            fid = f"FIG_P{p:03d}_{j}"
            path = OUT_DIR / f"{fid}.png"
            cv2.imwrite(str(path), crop)
            side = "left" if (x + bw / 2) < img.shape[1] // 2 else "right"
            printed = 2 * p - 1 if side == "left" else 2 * p
            results.append({
                "figure_id": fid, "pdf_page": p, "printed_page": printed, "side": side,
                "bbox_xywh": f["bbox"], "page_size": [img.shape[1], img.shape[0]],
                "width": crop.shape[1], "height": crop.shape[0], "format": "png",
                "text_cover": f["text_cover"], "ink_density": f["ink_density"],
                "caption_ocr": caption_for(rec, f["bbox"], img.shape[1]),
                "image_path": str(path.relative_to(ROOT)),
                "status": "candidate_needs_visual_check",
            })
    OUT_JSON.write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(results)} ứng viên hình -> {OUT_JSON}")
    for r in results:
        print(r["figure_id"], r["printed_page"], r["bbox_xywh"], r["text_cover"], r["ink_density"], "|", r["caption_ocr"][:80])


if __name__ == "__main__":
    main()
