# Đánh giá chunking (kích thước & overlap)

_Sinh tự động bởi `scripts/eval_chunking.py` trên 38 câu hỏi của `tests/evaluation/rag_test_dataset.json` (30 trả lời được + 8 ngoài kho)._

Retrieval: hybrid BM25 + char-TF-IDF (không dense embedding, xem README). Quan hệ liên quan dựa trên TRANG IN kỳ vọng nên độc lập với kích thước chunk.

| Cấu hình | max_chars | overlap | #chunk | độ dài TB | Recall@5 | Precision@5 | Hit@5 | MRR | NDCG@5 | Đủ từ khoá context (top-5) | Cặp chunk kề trùng/câu | ms/truy vấn |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S-low | 400 | 0 | 1146 | 310 | 0.794 | 0.280 | 0.867 | 0.734 | 0.623 | 0.767 | 1.03 | 6.7 |
| S-mid | 400 | 80 | 1318 | 468 | 0.806 | 0.333 | 0.867 | 0.751 | 0.662 | 0.783 | 1.53 | 8.6 |
| M-low | 900 | 0 | 528 | 681 | 0.867 | 0.293 | 0.900 | 0.760 | 0.650 | 0.800 | 0.67 | 5.2 |
| M-mid | 900 | 150 | 614 | 772 | 0.867 | 0.313 | 0.900 | 0.774 | 0.666 | 0.817 | 1.47 | 6.2 |
| L-low | 1600 | 0 | 295 | 1238 | 0.850 | 0.273 | 0.867 | 0.765 | 0.722 | 0.867 | 0.67 | 4.4 |
| L-mid | 1600 | 250 | 336 | 1290 | 0.817 | 0.280 | 0.833 | 0.774 | 0.650 | 0.867 | 0.70 | 4.8 |

**Cấu hình có tổng (Hit@5 + Recall@5 + MRR) cao nhất:** `M-mid` (max_chars=900, overlap=150).

## Cách đọc & giới hạn
- 'Đủ từ khoá context' = tỉ lệ từ khoá kỳ vọng xuất hiện trong văn bản của top-5 gộp lại (đại diện cho độ đầy đủ của context, không phải chất lượng câu trả lời).
- 'Cặp chunk kề trùng' đếm các cặp chunk trong top-5 nằm ở trang kề nhau và chia sẻ từ ở biên (hệ quả của overlap).
- Bộ câu hỏi nhỏ (38 câu) và thuộc cùng bộ dùng để tinh chỉnh retrieval, nên chênh lệch nhỏ giữa các cấu hình KHÔNG có ý nghĩa thống kê; cần bộ câu hỏi lớn hơn, được chuyên gia lịch sử duyệt, trước khi kết luận cứng.
- Chunk lớn làm tăng khả năng chứa đủ thông tin nhưng giảm độ chính xác định vị trang và tăng token gửi LLM; chunk nhỏ ngược lại.