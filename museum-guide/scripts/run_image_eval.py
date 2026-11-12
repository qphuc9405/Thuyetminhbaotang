#!/usr/bin/env python3
"""Đánh giá TRUY XUẤT ẢNH theo metadata (không image embedding) trên tests/evaluation/rag_test_dataset_supplement.json:
 (1) ImageIndex.search trực tiếp với truy vấn lấy từ nội dung tên file;
 (2) ảnh mà PIPELINE chat chọn (RagService._pick_images trên chunk truy xuất) cho các câu hỏi có expected_images.
Không gọi LLM/TTS."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))
from app.config import Settings  # noqa: E402
from app.database import repository as R  # noqa: E402
from app.database.database import get_engine, session_scope  # noqa: E402
from app.services.answer_profiles import classify  # noqa: E402
from app.services.rag_service import RagService  # noqa: E402
from app.services.retrieval_service import ImageIndex, RetrievalIndex  # noqa: E402


def main() -> None:
    get_engine(f"sqlite:///{ROOT / 'data/museum.db'}")
    with session_scope() as db:
        chunks, images, links = R.load_chunks(db), R.load_images(db), R.chunk_image_links(db)
    ix, iix = RetrievalIndex(chunks), ImageIndex(images)
    by_id = {i["image_id"]: i for i in images}
    rag = RagService(Settings(), ix, iix, llm=None, images_by_id=by_id, chunk_image_links=links)
    ds = json.loads((ROOT / "tests/evaluation/rag_test_dataset_supplement.json").read_text(encoding="utf-8"))
    rows, h1, h3, rr = [], 0, 0, 0.0
    for q in ds["image_queries"]:
        got = [im["image_id"] for im, _, _ in iix.search(q["query"], k=5, min_coverage=0.0)]
        ranks = [i + 1 for i, g in enumerate(got) if g in q["expected_images"]]
        r = ranks[0] if ranks else None
        h1 += r == 1; h3 += bool(r and r <= 3); rr += 1 / r if r else 0
        rows.append({"test_id": q["test_id"], "query": q["query"], "expected": q["expected_images"], "top5": got, "first_rank": r})
    n = len(ds["image_queries"])
    pipe = []
    for it in ds["items"]:
        if not it.get("expected_images"):
            continue
        prof = classify(it["question"])
        hits, _ = ix.search(it["question"], k=max(rag.s.retrieval_top_k, prof.top_k))
        picked = [im["image_id"] for im in rag._pick_images([ix.chunk(h.chunk_id) for h in hits], it["question"])]
        pipe.append({"test_id": it["test_id"], "question": it["question"], "expected": it["expected_images"], "picked": picked,
                     "hit": any(e in picked for e in it["expected_images"])})
    agg = {"image_index": {"n": n, "hit@1": round(h1 / n, 3), "hit@3": round(h3 / n, 3), "MRR@5": round(rr / n, 3)},
           "pipeline": {"n": len(pipe), "hit_rate": round(sum(p["hit"] for p in pipe) / len(pipe), 3)}}
    (ROOT / "docs/image_eval_results.json").write_text(json.dumps({"aggregate": agg, "image_index_rows": rows, "pipeline_rows": pipe}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(agg, indent=1))
    for r in rows:
        if r["first_rank"] != 1:
            print("  IMG", r["test_id"], r["query"], "->", r["top5"], "rank", r["first_rank"])
    for p in pipe:
        print("  PIPE", p["test_id"], "OK" if p["hit"] else "MISS", p["picked"])


if __name__ == "__main__":
    main()
