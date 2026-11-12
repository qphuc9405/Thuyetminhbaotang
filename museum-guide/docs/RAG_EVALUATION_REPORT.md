# Báo cáo đánh giá RAG
_Số liệu do `scripts/run_retrieval_eval.py` đo trên `tests/evaluation/rag_test_dataset.json` (30 câu trả lời được + 8 ngoài kho; vi/en/zh). Kết quả chi tiết từng câu: `docs/retrieval_eval_results.json`._

## 1. Đã đo (retrieval, không cần LLM)
| Metric | Mục tiêu | **Đo được** | Đạt? |
|---|---|---|---|
| Recall@3 / @5 / @10 | Recall@5 ≥ 0.85 | 0.756 / **0.850** / 0.917 | @5 đạt (sát ngưỡng) |
| Precision@5 (@3, @10) | ≥ 0.70 | **0.320** (0.411, 0.217) | **Không** – xem ghi chú |
| Hit Rate@3 / @5 / @10 | Hit@5 ≥ 0.90 | 0.800 / **0.867** / 0.933 | **Không** (@5); @10 đạt |
| MRR | – | 0.769 | – |
| NDCG@3 / @5 / @10 | – | 0.630 / 0.679 / 0.761 | – |
| Abstention (cổng bằng chứng, trước LLM) | ≥ 0.90 | **0.75** (6/8) | **Không** |
| Câu trả lời được bị cổng chặn nhầm | – | 0/30 | – |
| Latency truy xuất TB | – | ≈ 6 ms | – |

**Ghi chú Precision@5:** nhãn liên quan dựa trên trang in và mỗi câu hỏi sự kiện chỉ có 1–3 chunk đúng, nên Precision@5 tối đa chỉ ≈ 0.2–0.6 dù xếp hạng hoàn hảo; ngưỡng 0.70 không phù hợp với dạng câu hỏi tra cứu đơn lẻ này. Cần nhãn theo mức độ liên quan để so sánh công bằng.
**Abstention:** 2 câu sai (RAG-U01 "giá vé bảo tàng Điện Biên Phủ", RAG-U06 "số điện thoại Tổng thống Mỹ") vì chứa khái niệm/cụm có trong kho nên vượt cổng từ vựng; theo thiết kế đó là việc của LLM (`insufficient_evidence`) – **chưa đo được**.

## 2. Cải tiến trước/sau (theo quy trình prompt mục XVIII)
| Bước | Recall@5 | Hit@5 | Abstention | Câu đáp được bị chặn |
|---|---|---|---|---|
| Baseline (BM25+n-gram, coverage token) | 0.783 | 0.833 | 0.625 | 9/30 |
| + thành phần cụm từ (bigram/trigram) + cổng khái niệm/thực thể lạ | 0.883* | 0.900* | 0.875* | 1/30 |
| Cuối (loại trang mục lục/bìa khỏi chunk; sửa phát hiện thực thể đứng đầu câu) | 0.850 | 0.867 | 0.750 | 0/30 |
\*trước khi loại trang cấu trúc và sửa lỗ hổng "Obama…" do test phát hiện; số cuối trung thực hơn.
**Cảnh báo phương pháp:** các cải tiến được chọn bằng chính bộ câu hỏi này (38 câu, chưa có tập kiểm riêng), nên số có thể lạc quan; đáp án chuẩn **không** bị sửa để nâng điểm. Cần bộ lớn hơn do chuyên gia lịch sử duyệt.

## 3. CHƯA đo được (không có khoá Ollama/ElevenLabs, máy chủ bị chặn)
Faithfulness, Answer Relevancy, Context Precision/Recall (dạng LLM-judge), **Citation Accuracy trên đầu ra LLM thật**, **Abstention của LLM**, Multilingual Accuracy của câu trả lời, latency sinh câu trả lời. Đã có sẵn: bộ câu hỏi + đáp án tham chiếu, bước kiểm tra citation bằng code (`validate_llm_output`), test với LLM giả lập (72 test pytest). Việc cần làm khi có khoá: chạy lại `/api/chat` trên bộ câu hỏi, lưu trace (question, retrieved, context, raw response, validation) và tính các metric trên.
Không có số liệu nào ở mục 3 được ước tính hay tự nhận.


## 4. Cập nhật v2 (bộ 60 câu: +22 câu tổng hợp, kể chuyện, hình ảnh, nguồn mâu thuẫn, đa ngôn ngữ, không có đáp án)
| Metric | Bộ 38 câu (v1) | **Bộ 60 câu (v2)** |
|---|---|---|
| Recall@5 | 0.850 | **0.736** |
| Hit@5 / Hit@10 | 0.867 / 0.933 | **0.776 / 0.878** |
| Precision@5 | 0.320 | 0.286 |
| MRR | 0.769 | 0.638 |
| Cổng từ chối (trước LLM) | 0.75 | 0.545 (5 câu trong miền nhưng không có đáp án vượt cổng, theo thiết kế dựa vào LLM) |
| Context Recall (context thật gửi LLM) | – | cũ 0.777 → **mới 0.850** (`docs/context_recall_results.json`) |
Số giảm ở v2 phản ánh câu hỏi khó hơn (tổng hợp nhiều chương, tiếng Anh/Trung kể chuyện), không phải hệ thống kém đi. Mỗi câu v2 có `must_include` và `must_not_guess` để chấm đầu ra LLM khi có khoá (`scripts/run_llm_eval.py`).

## Phụ lục 31/10/2026 – sau khi bổ sung nguồn
So sánh trên cùng code cuối (gồm điểm thưởng cụm tên riêng), chỉ khác dữ liệu. Chi tiết và cách đọc: `SUPPLEMENT_INTEGRATION_REPORT.md` §6.

| 60 câu cũ | Recall@5 | P@5 | Hit@5 | Recall@10 | Hit@10 | MRR |
|---|---|---|---|---|---|---|
| DB chỉ có sách | 0,777 | 0,298 | 0,816 | 0,866 | 0,898 | 0,678 |
| DB sau bổ sung | 0,787 | 0,278 | 0,837 | 0,838 | 0,878 | 0,636 |

Gold mới (16 câu, `rag_test_dataset_supplement.json`): Recall@5 0,787, Hit@5 0,938, MRR 0,674.

