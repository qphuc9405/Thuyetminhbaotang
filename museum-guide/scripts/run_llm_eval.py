#!/usr/bin/env python3
"""Đánh giá câu trả lời THẬT của hệ thống (cần backend đang chạy với OLLAMA_API_KEY). TỐN QUOTA – không chạy trong unit test.

    python scripts/run_llm_eval.py --base http://localhost:8000 [--limit 10]

Ghi: docs/llm_eval/traces.jsonl (mỗi câu: câu hỏi, câu trả lời, nguồn, chế độ, cảnh báo, thời gian),
     docs/llm_eval/summary.json (chỉ số tự động), docs/llm_eval/human_rating.csv (phiếu chấm tay).
Chỉ số tự động (proxy, không phải chân lý):
  - citation_page_accuracy: tỉ lệ nguồn được trích có trang/chunk thuộc kỳ vọng (câu trả lời được)
  - completeness_keywords: tỉ lệ must_include xuất hiện trong câu trả lời
  - abstention_accuracy: câu không có đáp án -> insufficient_evidence; câu có đáp án -> không từ chối
  - language_match: ngôn ngữ câu trả lời = ngôn ngữ câu hỏi
  - words theo hồ sơ câu hỏi; tỉ lệ có cảnh báo (ungrounded_years, no_valid_citations, short_answer)
Faithfulness / Naturalness / Readability / must_not_guess: chấm TAY trong human_rating.csv (thang 1–5).
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import statistics
import sys
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))
from app.services.text_utils import detect_language, fold  # noqa: E402


def page_ok(s: dict, it: dict) -> bool:
    if s["chunk_id"] in it["expected_chunk_ids"]:
        return True
    if s["source_id"] == "SRC001" and it["expected_pages"] and s["printed_page"] is not None:
        a, b = s["printed_page"], s["printed_page_end"] or s["printed_page"]
        return any(a - 1 <= p <= b + 1 for p in it["expected_pages"])
    return s["source_id"] in it["expected_source_ids"] and not it["expected_chunk_ids"] and s["source_id"] != "SRC001"


def main() -> None:
    ap = argparse.ArgumentParser(); ap.add_argument("--base", default="http://localhost:8000"); ap.add_argument("--limit", type=int, default=0); a = ap.parse_args()
    items = json.loads((ROOT / "tests/evaluation/rag_test_dataset.json").read_text(encoding="utf-8"))["items"]
    if a.limit: items = items[: a.limit]
    out = ROOT / "docs/llm_eval"; out.mkdir(parents=True, exist_ok=True)
    h = httpx.get(a.base + "/api/health", timeout=10).json()
    if not h["llm"]["configured"]:
        sys.exit("LLM chưa cấu hình (OLLAMA_API_KEY). Dừng để không tạo số liệu giả.")
    rows = []
    with (out / "traces.jsonl").open("w", encoding="utf-8") as f:
        for it in items:
            t0 = time.perf_counter()
            r = httpx.post(a.base + "/api/chat", json={"message": it["question"], "language": "auto", "session_id": "eval-" + it["test_id"]}, timeout=180).json()
            dt = time.perf_counter() - t0
            ans = r.get("answer", "")
            rec = {"test_id": it["test_id"], "question": it["question"], "category": it["category"], "answerable": it["answerable"], "latency_s": round(dt, 2), "model": h["llm"]["model"],
                   "mode": r.get("mode"), "profile": r.get("retrieval", {}).get("profile"), "answer": ans, "sources": r.get("sources", []), "warnings": r.get("warnings", []),
                   "insufficient": r.get("insufficient_evidence"), "words": len(re.findall(r"\w+", ans))}
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            cited = [s for s in rec["sources"] if s.get("cited")]
            rec["cit_acc"] = (sum(page_ok(s, it) for s in cited) / len(cited)) if (cited and it["answerable"]) else None
            mi = it.get("must_include") or []
            rec["kw"] = (sum(1 for k in mi if fold(k) in fold(ans)) / len(mi)) if mi else None
            rec["abst_ok"] = (bool(rec["insufficient"]) == (not it["answerable"]))
            rec["lang_ok"] = detect_language(ans) == it["language"] if ans else False
            rows.append(rec)
            print(it["test_id"], rec["mode"], rec["profile"], rec["words"], "w", f"{dt:.1f}s", rec["warnings"][:2])
    def mean(xs): xs = [x for x in xs if x is not None]; return round(statistics.mean(xs), 3) if xs else None
    ans_rows = [x for x in rows if x["answerable"]]
    summary = {"n": len(rows), "model": h["llm"]["model"], "citation_page_accuracy": mean([x["cit_acc"] for x in ans_rows]), "completeness_keywords": mean([x["kw"] for x in ans_rows]),
               "abstention_accuracy": mean([float(x["abst_ok"]) for x in rows]), "language_match": mean([float(x["lang_ok"]) for x in rows]), "latency_s_mean": mean([x["latency_s"] for x in rows]),
               "words_by_profile": {p: mean([x["words"] for x in ans_rows if x["profile"] == p]) for p in {x["profile"] for x in ans_rows}},
               "warning_rate": mean([float(bool([w for w in x["warnings"] if not w.startswith("llm_error")])) for x in rows]),
               "note": "Chỉ số tự động là proxy. Faithfulness/Naturalness/Readability cần chấm tay trong human_rating.csv."}
    (out / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    with (out / "human_rating.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["test_id", "question", "answer", "faithfulness_1_5", "relevance_1_5", "completeness_1_5", "naturalness_1_5", "readability_1_5", "violated_must_not_guess(y/n)", "notes"])
        for x in rows: w.writerow([x["test_id"], x["question"], x["answer"], "", "", "", "", "", "", ""])
    print(json.dumps(summary, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
