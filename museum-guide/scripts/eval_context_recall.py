#!/usr/bin/env python3
"""Context Recall: tỉ lệ 'đơn vị kỳ vọng' (trang in / chunk) có mặt trong CONTEXT thực sự gửi LLM.
So sánh pipeline cũ (top-6, không mở rộng) và pipeline mới (hồ sơ câu hỏi + đoạn liền kề). Không gọi LLM."""
import json, statistics, sys
from collections import defaultdict
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend")); sys.path.insert(0, str(ROOT / "scripts"))
from app.database import repository as R
from app.database.database import get_engine, session_scope
from app.services.answer_profiles import classify
from app.services.retrieval_service import RetrievalIndex
from run_retrieval_eval import units_covered

get_engine(f"sqlite:///{ROOT / 'data/museum.db'}")
with session_scope() as db: chunks = R.load_chunks(db)
ix = RetrievalIndex(chunks)
items = [x for x in json.loads((ROOT / "tests/evaluation/rag_test_dataset.json").read_text(encoding="utf-8"))["items"] if x["answerable"] and (x["expected_pages"] or x["expected_chunk_ids"])]
res = defaultdict(lambda: {"old": [], "new": [], "n_old": [], "n_new": [], "chars_new": []})
for it in items:
    p = classify(it["question"])
    h_old, _ = ix.search(it["question"], k=6); c_old = [ix.chunk(h.chunk_id) for h in h_old]
    h_new, _ = ix.search(it["question"], k=max(6, p.top_k)); c_new = ix.expand_with_neighbors([ix.chunk(h.chunk_id) for h in h_new], n_top=p.expand) if p.expand else [ix.chunk(h.chunk_id) for h in h_new]
    acc, size = [], 0
    for c in c_new:  # mô phỏng giới hạn ký tự context của hồ sơ
        size += len(c["content"]) + 200
        if size > p.max_context and acc: break
        acc.append(c)
    for k, cs in (("old", c_old), ("new", acc)):
        g, t = units_covered(cs, it); res[p.kind][k].append(g / t)
    res[p.kind]["n_old"].append(len(c_old)); res[p.kind]["n_new"].append(len(acc)); res[p.kind]["chars_new"].append(sum(len(c["content"]) for c in acc))
out = {}
allo, alln = [], []
for kind, d in res.items():
    out[kind] = {"n_questions": len(d["old"]), "context_recall_old": round(statistics.mean(d["old"]), 3), "context_recall_new": round(statistics.mean(d["new"]), 3),
                 "chunks_old": round(statistics.mean(d["n_old"]), 1), "chunks_new": round(statistics.mean(d["n_new"]), 1), "context_chars_new": int(statistics.mean(d["chars_new"]))}
    allo += d["old"]; alln += d["new"]
out["ALL"] = {"n_questions": len(allo), "context_recall_old": round(statistics.mean(allo), 3), "context_recall_new": round(statistics.mean(alln), 3)}
(ROOT / "docs/context_recall_results.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
print(json.dumps(out, ensure_ascii=False, indent=1))
