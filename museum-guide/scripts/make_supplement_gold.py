#!/usr/bin/env python3
"""Sinh tests/evaluation/rag_test_dataset_supplement.json: câu hỏi kiểm tra NGUỒN BỔ SUNG (3 bài viết + ảnh Archive_4).
expected_chunk_ids được tra từ (nguồn, số dòng) trong DB (không gõ tay ID), để bộ gold bám đúng vị trí trong văn bản gốc."""
from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
db = sqlite3.connect(ROOT / "data/museum.db")


def chunk_at(src: str, line: int, must=()) -> list[str]:
    """Chunk chứa dòng `line`; nếu đoạn dài bị cắt thành nhiều mảnh (cùng số dòng) thì chọn mảnh chứa từ khoá kỳ vọng."""
    hits = []
    for cid, prov, content in db.execute("select chunk_id, provision, content from chunks where source_id=?", (src,)):
        m = re.match(r"dòng (\d+)(?:–(\d+))?", prov or "")
        a, b = int(m.group(1)), int(m.group(2) or m.group(1))
        if a <= line <= b:
            hits.append((cid, content))
    if not hits:
        raise KeyError((src, line))
    if len(hits) > 1 and must:
        sel = [cid for cid, c in hits if any(k.lower() in c.lower() for k in must)]
        if sel:
            return sel
    return [cid for cid, _ in hits]


def item(tid, q, lang, locs, pages=(), notes=(), must=(), ref="", cat="supplement", images=()):
    cids = sorted({c for s, l in locs for c in chunk_at(s, l, must)} | set(notes))
    srcs = sorted({s for s, _ in locs} | ({"SRC001"} if pages else set()) | ({"NOTE01"} if notes else set()))
    return {"test_id": tid, "question": q, "language": lang, "expected_source_ids": srcs, "expected_pages": list(pages), "expected_chunk_ids": cids,
            "expected_keywords": list(must), "reference_answer": ref, "answerable": True, "category": cat, "must_include": list(must),
            "must_not_guess": ["số liệu/niên đại không có trong nguồn", "danh tính người trong ảnh"], "expected_images": list(images)}


ITEMS = [
    item("SUP-01", "Bà Nguyễn Thị Hương kể gì về cuộc chiến màu sơn trên cầu Hiền Lương?", "vi", [("SRC004", 16), ("SRC004", 18), ("SRC004", 25)], must=["Nguyễn Thị Hương"],
         ref="Theo lời kể trong SRC004, năm 1956 bà được điều về làm đội trưởng đội sơn cầu 20 người; hai bên thay nhau sơn, đến 1960 giữ hai màu xanh – vàng. Sách (tr.185–186) ghi khác: Đội 337 gồm 10 người, từ 9-11-1958."),
    item("SUP-02", "Chiếc loa 500W ở bờ Bắc có đường kính bao nhiêu và được đặt ở đâu?", "vi", [("SRC003", 58), ("SRC005", 18)], pages=[116], must=["500"], images=["IMG046"]),
    item("SUP-03", "Lúc đầu hệ thống loa bờ Bắc có bao nhiêu cụm, mỗi cụm bao nhiêu loa?", "vi", [("SRC003", 56), ("SRC005", 14)], must=["24 loa"]),
    item("SUP-04", "O Nhạn là ai?", "vi", [("SRC003", 62)], must=["O Nhạn"], images=["IMG043"], cat="supplement_image_filename"),
    item("SUP-05", "Trạm tăng âm của hệ thống loa phóng thanh đặt cách cầu Hiền Lương bao xa?", "vi", [("SRC005", 18)], must=["2,5km", "trạm tăng âm"]),
    item("SUP-06", "Vì sao sông Minh Lương được đổi tên thành Hiền Lương?", "vi", [("SRC003", 8)], must=["Minh Mạng"]),
    item("SUP-07", "Cụm di tích Đôi bờ Hiền Lương – Bến Hải được xếp hạng di tích quốc gia đặc biệt năm nào?", "vi", [("SRC004", 76), ("SRC005", 20)], must=["2013"]),
    item("SUP-08", "Ông Hoàng Nghi nhớ lại những gì về chuyện chọi cờ?", "vi", [("SRC004", 55), ("SRC004", 57), ("SRC004", 62)], must=["Hoàng Nghi"]),
    item("SUP-09", "Theo Nguyễn Tuân, mỗi nửa cầu Hiền Lương có bao nhiêu tấm ván?", "vi", [("SRC003", 18)], pages=[184], must=["450"]),
    item("SUP-10", "Cầu Hiền Lương bị đánh sập năm 1966 hay năm 1967?", "vi", [("SRC003", 30), ("SRC003", 83), ("SRC004", 25)], pages=[183], notes=["NOTE-01"], must=["1967"],
         cat="supplement_conflict", ref="Sách tr.183 ghi 9-1966; SRC003 ghi 2/8/1967; SRC004, SRC005 ghi năm 1967. Câu trả lời phải nêu cả hai, không chọn."),
    item("SUP-11", "What did the witness Nguyen Thi Huong say about painting the Hien Luong bridge?", "en", [("SRC004", 16), ("SRC004", 18), ("SRC004", 25)], must=["Nguyễn Thị Hương"]),
    item("SUP-12", "贤良桥北岸最初的扩音系统有几组喇叭？", "zh", [("SRC003", 56), ("SRC005", 14)], must=["24 loa"]),
    item("SUP-13", "Đường dây điện cấp cho hệ thống loa phóng thanh dài bao nhiêu?", "vi", [("SRC005", 18)], must=["6KvA"]),
    item("SUP-14", "Năm 2014 cầu Hiền Lương được phục hồi màu sơn như thế nào?", "vi", [("SRC003", 38), ("SRC004", 31)], must=["2014"], images=["IMG045"]),
    item("SUP-15", "Cho tôi xem ảnh cụm loa phát thanh bên bờ Nam", "vi", [("SRC003", 54)], must=["bờ Nam"], images=["IMG042"], cat="supplement_image_filename"),
    item("SUP-16", "Có ảnh toàn cảnh cầu Hiền Lương chụp ngày 2-9-1959 không?", "vi", [("SRC003", 22)], must=["2-9-1959"], images=["IMG044"], cat="supplement_image_filename"),
]

# Truy xuất ẢNH theo nội dung tên file (ImageIndex – metadata-based, không image embedding)
IMAGE_QUERIES = [
    ("IMQ-01", "Cụm loa phát thanh bên bờ Nam", ["IMG042"]),
    ("IMQ-02", "Cụm loa phát thanh bên bờ Bắc", ["IMG041", "IMG047", "IMG049"]),
    ("IMQ-03", "O Nhạn phát thanh viên Đài Truyền thanh Vĩnh Linh", ["IMG043"]),
    ("IMQ-04", "cầu Hiền Lương bị bom Mỹ đánh sập năm 1967", ["IMG037"]),
    ("IMQ-05", "toàn cảnh cầu Hiền Lương ngày 2-9-1959", ["IMG044"]),
    ("IMQ-06", "mẹ Diệm vá cờ Tổ quốc", ["IMG050"]),
    ("IMQ-07", "1954 Geneva Conference", ["IMG035"]),
    ("IMQ-08", "chiếc loa trưng bày Đài Tiếng nói Việt Nam", ["IMG046"]),
    ("IMQ-09", "cột cờ tại cầu Hiền Lương ngày nay", ["IMG040"]),
    ("IMQ-10", "cầu Hiền Lương hai màu", ["IMG045", "IMG034", "IMG004", "BKFIG11"]),
    ("IMQ-11", "cầu Hiền Lương do người Pháp xây dựng năm 1952", ["IMG038"]),
    ("IMQ-12", "cụm loa phóng thanh phục dựng bờ Nam khu di tích", ["IMG048"]),
    ("IMQ-13", "khẩu hiệu Nam Bắc là một nhà", ["IMG036", "IMG024"]),
    ("IMQ-14", "cầu Hiền Lương nhìn từ phía Nam năm 1964", ["IMG039"]),
    ("IMQ-15", "loudspeakers on the southern bank", ["IMG042", "IMG048"]),
    ("IMQ-16", "贤良桥 扩音器", ["IMG041", "IMG042", "IMG043", "IMG046", "IMG047", "IMG048", "IMG049", "IMG030", "IMG024", "IMG036"]),
]

out = {"meta": {"description": "Bộ câu hỏi kiểm tra nguồn bổ sung 2026-10-31 (SRC003–SRC006, NOTE01). Chunk kỳ vọng tra từ số dòng.", "n_items": len(ITEMS), "n_image_queries": len(IMAGE_QUERIES)},
       "items": ITEMS, "image_queries": [{"test_id": a, "query": q, "expected_images": e} for a, q, e in IMAGE_QUERIES]}
p = ROOT / "tests/evaluation/rag_test_dataset_supplement.json"
p.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print(p, len(ITEMS), len(IMAGE_QUERIES))
