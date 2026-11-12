# Báo cáo kiểm thử (đã chạy thật)
| Nhóm | Công cụ | Kết quả |
|---|---|---|
| A. Backend (API-*, LLM-*, GRD/HAL/CIT/CTX/MLLM mô phỏng, TTS-*, RET-*, PDF-*, IMG-*, bảo mật) | `cd backend && python -m pytest` | **107 passed** (81 cũ + 26 test đợt bổ sung nguồn, nguồn web và mẩu chuyện trong `tests/test_supplement.py`, 31/10/2026) |
| A. Frontend (UI-01…UI-12) | `cd frontend && npm test` | **25 passed** (+3: nhãn nguồn bài viết, mô tả ảnh, trang Chuyện kể); `npm run build` thành công |
| A. Kiểm tra đối chiếu dữ liệu | `python scripts/verify_extraction.py` | **OK** (130/130 trang, 15/15 hình, 34/34 ảnh) |
| B. Đánh giá retrieval | `python scripts/run_retrieval_eval.py` | xem `RAG_EVALUATION_REPORT.md` và `SUPPLEMENT_INTEGRATION_REPORT.md` §6 |
| B. Đánh giá truy xuất ảnh | `python scripts/run_image_eval.py` | Hit@1 1,0 · Hit@3 1,0 (16 truy vấn theo mô tả ảnh); pipeline chọn đúng ảnh 5/5 |
| Duyệt UI thật | Playwright + Chromium, desktop 1280 & mobile 390 | không lỗi console, không tràn ngang; ảnh chụp ở `docs/screenshots/` |

## Điều quan trọng cần đọc
- Unit test dùng `httpx.MockTransport`: **không có lời gọi thật** tới Ollama/ElevenLabs. Vì vậy **TTS-01…03/08 (nghe đúng nội dung), LLM-01…15 với model thật, E2E-01…15 với LLM thật chưa được chạy**. Test mô phỏng chỉ chứng minh logic phía backend (retry, timeout, quota, xác thực citation, từ chối, fallback), không chứng minh chất lượng câu trả lời của model.
- Test đã bắt và sửa các lỗi thật: danh từ riêng đứng đầu câu không được phát hiện; mục lục lọt vào chunk; test từng ghi vào CSDL thật (nay dùng bản sao); regex thực thể bắt nhầm chữ thường.
- Phản hồi khi `OLLAMA_API_KEY` thiếu đã được chạy thật qua trình duyệt: chatbot trả `extractive_fallback` kèm nguồn, trang, ảnh.
- Docker image chưa build; chưa cài thử từ môi trường sạch hoàn toàn (đã chạy trên môi trường dev này).


## Cập nhật sau nâng cấp giao diện & thuyết minh
Xem `docs/REDESIGN_REPORT.md` mục 5 (Context Recall cũ/mới, bộ 60 câu, các test chưa chạy được vì thiếu khoá).
