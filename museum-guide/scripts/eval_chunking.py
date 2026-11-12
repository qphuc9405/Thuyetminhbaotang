#!/usr/bin/env python3
"""Đánh giá ảnh hưởng chunk size / overlap tới retrieval. Ghi docs/CHUNKING_EVALUATION.md.
Chỉ dùng retrieval cục bộ (không gọi LLM/TTS)."""
from __future__ import annotations

import json
import sqlite3
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend")); sys.path.insert(0, str(ROOT / "scripts"))
from app.services.chunker import build_paragraphs, make_chunks  # noqa: E402
from app.services.retrieval_service import RetrievalIndex  # noqa: E402
from app.services.text_utils import fold  # noqa: E402
from run_retrieval_eval import evaluate  # noqa: E402

CONFIGS = [("S-low", 400, 0), ("S-mid", 400, 80), ("M-low", 900, 0), ("M-mid", 900, 150), ("L-low", 1600, 0), ("L-mid", 1600, 250)]


def build_chunks(max_chars: int, overlap: int, db: sqlite3.Connection, external: list[dict]) -> list[dict]:
    rows = db.execute("select pdf_page,printed_page,chapter_id,ocr_text,needs_review,is_blank from pages order by printed_page").fetchall()
    from build_knowledge_base import STRUCTURAL_PAGES
    pages = [dict(pdf_page=r[0], printed_page=r[1], chapter_id=r[2], ocr_text=r[3], needs_review=bool(r[4]), is_blank=bool(r[5]) or r[1] in STRUCTURAL_PAGES) for r in rows]
    paras, _ = build_paragraphs(pages)
    specs = make_chunks(paras, max_chars=max_chars, overlap_chars=overlap)
    ch_title = {r[0]: r[1] for r in db.execute("select chapter_id,title_vi from chapters")}
    out = []
    for n, c in enumerate(specs, 1):
        out.append(dict(chunk_id=f"B{n:04d}", source_id="SRC001", source_type="BOOK", language="vi", chapter=ch_title.get(c.chapter_id), chapter_id=c.chapter_id, section=c.section,
                        keywords=[], folded=fold(c.text), content=c.text, printed_page=c.printed_page, printed_page_end=c.printed_page_end))
    return out + external


def main() -> None:
    db = sqlite3.connect(ROOT / "data/museum.db")
    db.row_factory = None
    cols = [r[1] for r in db.execute("pragma table_info(chunks)")]
    ext = [dict(zip(cols, r)) for r in db.execute("select * from chunks where source_id!='SRC001'")]
    items = json.loads((ROOT / "tests/evaluation/rag_test_dataset.json").read_text(encoding="utf-8"))["items"]
    rows = []
    for name, mc, ov in CONFIGS:
        chunks = build_chunks(mc, ov, db, ext)
        t0 = time.perf_counter(); idx = RetrievalIndex(chunks); t_idx = time.perf_counter() - t0
        res = evaluate(idx, items, 0.5, 0.06)
        a = res["aggregate"]
        # độ đầy đủ context: tỉ lệ từ khoá kỳ vọng xuất hiện trong top-5 gộp lại
        comp = []
        dup = []
        for it in items:
            if not it["answerable"] or not it["expected_keywords"]:
                continue
            hits, _ = idx.search(it["question"], k=5)
            blob = fold(" ".join(idx.chunk(h.chunk_id)["content"] for h in hits))
            kws = [fold(k) for k in it["expected_keywords"]]
            comp.append(sum(1 for k in kws if k in blob) / len(kws))
            txts = [idx.chunk(h.chunk_id)["folded"] for h in hits]
            pairs = [(i, j) for i in range(len(txts)) for j in range(i + 1, len(txts)) if set(txts[i].split()[-12:]) & set(txts[j].split()[:12]) and idx.chunk(hits[i].chunk_id)["source_id"] == idx.chunk(hits[j].chunk_id)["source_id"] and abs((idx.chunk(hits[i].chunk_id)["printed_page"] or 0) - (idx.chunk(hits[j].chunk_id)["printed_page"] or 0)) <= 1]
            dup.append(len(pairs))
        rows.append(dict(config=name, max_chars=mc, overlap=ov, n_chunks=len(chunks), avg_len=round(statistics.mean(len(c["content"]) for c in chunks if c["source_id"] == "SRC001")),
                         recall5=a["recall@5"], precision5=a["precision@5"], hit5=a["hit@5"], mrr=a["MRR"], ndcg5=a["ndcg@5"], ctx_complete=statistics.mean(comp), adjacent_dup=statistics.mean(dup),
                         lat_ms=a["latency_ms_mean"], index_s=t_idx))
    best = max(rows, key=lambda r: (round(r["hit5"] + r["recall5"] + r["mrr"], 3)))
    md = ["# Đánh giá chunking (kích thước & overlap)", "", f"_Sinh tự động bởi `scripts/eval_chunking.py` trên {len(items)} câu hỏi của `tests/evaluation/rag_test_dataset.json` (30 trả lời được + 8 ngoài kho)._", "",
          "Retrieval: hybrid BM25 + char-TF-IDF (không dense embedding, xem README). Quan hệ liên quan dựa trên TRANG IN kỳ vọng nên độc lập với kích thước chunk.", "",
          "| Cấu hình | max_chars | overlap | #chunk | độ dài TB | Recall@5 | Precision@5 | Hit@5 | MRR | NDCG@5 | Đủ từ khoá context (top-5) | Cặp chunk kề trùng/câu | ms/truy vấn |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        md.append(f"| {r['config']} | {r['max_chars']} | {r['overlap']} | {r['n_chunks']} | {r['avg_len']} | {r['recall5']:.3f} | {r['precision5']:.3f} | {r['hit5']:.3f} | {r['mrr']:.3f} | {r['ndcg5']:.3f} | {r['ctx_complete']:.3f} | {r['adjacent_dup']:.2f} | {r['lat_ms']:.1f} |")
    md += ["", f"**Cấu hình có tổng (Hit@5 + Recall@5 + MRR) cao nhất:** `{best['config']}` (max_chars={best['max_chars']}, overlap={best['overlap']}).", "",
           "## Cách đọc & giới hạn", "- 'Đủ từ khoá context' = tỉ lệ từ khoá kỳ vọng xuất hiện trong văn bản của top-5 gộp lại (đại diện cho độ đầy đủ của context, không phải chất lượng câu trả lời).",
           "- 'Cặp chunk kề trùng' đếm các cặp chunk trong top-5 nằm ở trang kề nhau và chia sẻ từ ở biên (hệ quả của overlap).",
           "- Bộ câu hỏi nhỏ (38 câu) và thuộc cùng bộ dùng để tinh chỉnh retrieval, nên chênh lệch nhỏ giữa các cấu hình KHÔNG có ý nghĩa thống kê; cần bộ câu hỏi lớn hơn, được chuyên gia lịch sử duyệt, trước khi kết luận cứng.",
           "- Chunk lớn làm tăng khả năng chứa đủ thông tin nhưng giảm độ chính xác định vị trang và tăng token gửi LLM; chunk nhỏ ngược lại."]
    (ROOT / "docs/CHUNKING_EVALUATION.md").write_text("\n".join(md), encoding="utf-8")
    (ROOT / "docs/chunking_eval_results.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
    print("\n".join(md[6:6 + len(rows) + 3]))
    print("BEST:", best["config"])


if __name__ == "__main__":
    main()
