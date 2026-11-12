#!/usr/bin/env python3
"""Đánh giá RETRIEVAL (không gọi LLM/TTS, không tốn quota) trên tests/evaluation/rag_test_dataset.json.
Metric: Recall@K, Precision@K, MRR, HitRate@K, NDCG@K (K=3,5,10) + Abstention (cổng bằng chứng) + latency.
Nhãn liên quan:
  - chunk của sách: liên quan nếu khoảng trang in của chunk giao với expected_pages (và source nằm trong expected_source_ids);
  - chunk văn kiện ngoài: liên quan nếu chunk_id ∈ expected_chunk_ids (hoặc source ∈ expected_source_ids khi không có expected_chunk_ids).
Recall@K tính trên "đơn vị kỳ vọng": mỗi trang kỳ vọng (sách) hoặc mỗi chunk kỳ vọng (văn kiện ngoài)."""
from __future__ import annotations

import json
import math
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))
from app.database import repository as R  # noqa: E402
from app.database.database import get_engine, session_scope  # noqa: E402
from app.services.rag_service import evidence_ok  # noqa: E402
from app.services.retrieval_service import RetrievalIndex  # noqa: E402

KS = (3, 5, 10)


SOURCE_AWARE = False  # bật bằng --source-aware: bài viết bổ sung (SECONDARY_ARTICLE) chứa ĐỦ mọi must_include của câu cũng tính là liên quan


def _fold(s: str) -> str:
    from app.services.text_utils import fold
    return fold(s)


def is_rel(c: dict, it: dict) -> bool:
    if c["chunk_id"] in it["expected_chunk_ids"]:
        return True
    if SOURCE_AWARE and c["source_type"] in ("SECONDARY_ARTICLE", "WEB_ARTICLE") and it.get("must_include"):
        body = _fold(c["content"])
        if all(_fold(k) in body for k in it["must_include"]):
            return True
    if c["source_id"] not in it["expected_source_ids"]:
        return False
    if c["source_id"] == "SRC001":
        pg = it["expected_pages"]
        if not pg:
            return False
        a, b = c["printed_page"], c["printed_page_end"] or c["printed_page"]
        return any(a <= p <= b for p in pg)
    return not it["expected_chunk_ids"]  # văn kiện ngoài không chỉ định chunk: nguồn đúng là đủ


def units_covered(hits_chunks: list[dict], it: dict) -> tuple[int, int]:
    units = [("p", p) for p in it["expected_pages"]] + [("c", x) for x in it["expected_chunk_ids"]]
    if not units:
        return 0, 0
    got = 0
    for kind, v in units:
        for c in hits_chunks:
            if (kind == "c" and c["chunk_id"] == v) or (kind == "p" and c["source_id"] == "SRC001" and c["printed_page"] <= v <= (c["printed_page_end"] or c["printed_page"])):
                got += 1; break
    return got, len(units)


def evaluate(index: RetrievalIndex, items: list[dict], min_cov: float, min_cos: float, k_ret: int = 10) -> dict:
    rows, lat = [], []
    for it in items:
        t0 = time.perf_counter()
        hits, qp = index.search(it["question"], k=k_ret)
        lat.append((time.perf_counter() - t0) * 1000)
        chunks = [index.chunk(h.chunk_id) for h in hits]
        gate = evidence_ok(hits, min_cov=min_cov, min_cos=min_cos, unknown_entities=qp.get("unknown_entities"))
        row = {"test_id": it["test_id"], "question": it["question"], "answerable": it["answerable"], "gate_pass": gate, "category": it["category"], "unknown_entities": qp.get("unknown_entities")}
        if it["answerable"]:
            rel = [is_rel(c, it) for c in chunks]
            row["top"] = [(c["chunk_id"], c["printed_page"], r) for c, r in zip(chunks[:5], rel)]
            for K in KS:
                top = chunks[:K]; rr = rel[:K]
                got, tot = units_covered(top, it)
                row[f"recall@{K}"] = got / tot if tot else 0.0
                row[f"precision@{K}"] = sum(rr) / K
                row[f"hit@{K}"] = float(any(rr))
                dcg = sum(1 / math.log2(i + 2) for i, r in enumerate(rr) if r)
                n_rel_total = max(1, min(K, sum(rel) if sum(rel) else 1))
                idcg = sum(1 / math.log2(i + 2) for i in range(min(K, max(1, sum(rel)))))
                row[f"ndcg@{K}"] = dcg / idcg if idcg else 0.0
            first = next((i for i, r in enumerate(rel) if r), None)
            row["rr"] = 1 / (first + 1) if first is not None else 0.0
        rows.append(row)
    ans = [r for r in rows if r["answerable"]]
    un = [r for r in rows if not r["answerable"]]
    agg = {f"{m}@{K}": statistics.mean(r[f"{m}@{K}"] for r in ans) for K in KS for m in ("recall", "precision", "hit", "ndcg")}
    agg["MRR"] = statistics.mean(r["rr"] for r in ans)
    agg["abstention_accuracy"] = sum(not r["gate_pass"] for r in un) / len(un) if un else None
    agg["answerable_pass_gate_rate"] = sum(r["gate_pass"] for r in ans) / len(ans)
    agg["latency_ms_mean"] = statistics.mean(lat); agg["latency_ms_p95"] = sorted(lat)[int(0.95 * len(lat)) - 1]
    agg["n_answerable"], agg["n_unanswerable"] = len(ans), len(un)
    return {"aggregate": agg, "rows": rows}


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=str(ROOT / "data/museum.db"))
    ap.add_argument("--dataset", default=str(ROOT / "tests/evaluation/rag_test_dataset.json"))
    ap.add_argument("--out", default=str(ROOT / "docs/retrieval_eval_results.json"))
    ap.add_argument("--source-aware", action="store_true")
    args = ap.parse_args()
    global SOURCE_AWARE
    SOURCE_AWARE = args.source_aware
    get_engine(f"sqlite:///{Path(args.db).resolve()}")
    with session_scope() as db:
        chunks = R.load_chunks(db)
    index = RetrievalIndex(chunks)
    items = json.loads(Path(args.dataset).read_text(encoding="utf-8"))["items"]
    res = evaluate(index, items, min_cov=0.5, min_cos=0.06)
    res["config"] = {"source_aware_relevance": SOURCE_AWARE, "backend": index.backend, "min_cov": 0.5, "min_cos": 0.06, "top_k": 10, "n_chunks": len(chunks)}
    out = Path(args.out)
    out.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    a = res["aggregate"]
    print(json.dumps({k: (round(v, 3) if isinstance(v, float) else v) for k, v in a.items()}, indent=1))
    print("\nCâu hỏi KHÔNG có hit@5:")
    for r in res["rows"]:
        if r["answerable"] and r["hit@5"] == 0:
            print(" ", r["test_id"], r["question"][:70], "| top:", r["top"][:3])
    print("Abstention sai:", [r["test_id"] for r in res["rows"] if (not r["answerable"] and r["gate_pass"])], "| answerable bị chặn:", [r["test_id"] for r in res["rows"] if (r["answerable"] and not r["gate_pass"])])


if __name__ == "__main__":
    main()
