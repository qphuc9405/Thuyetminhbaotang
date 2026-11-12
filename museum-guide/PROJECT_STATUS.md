# PROJECT_STATUS (cập nhật 2026-10-31)

## Đã hoàn thành (có bằng chứng chạy thật)
- Kiểm kê & trích xuất: 130/130 trang PDF scan được OCR (Tesseract `vie`, conf TB 93,5), lưu ảnh scan trang, 260 trang sách in với số trang suy ra + đối chiếu; 12 hình lịch sử trong sách được tách bằng phân tích layout và kiểm tra bằng mắt; 34/34 ảnh ZIP được quan sát từng ảnh, có metadata đủ 20 trường, hash SHA-256/pHash, 7 nhóm bản trùng (không xoá), 4 ảnh khớp hình in trong sách. `docs/DATASET_DOCUMENTATION.md`.
- Knowledge Base SQLite + JSON export; 604 chunk sách + 10 bản ghi văn kiện ngoài; 29 sự kiện (28 từ sách, mỗi sự kiện có trang in và *anchor* khớp OCR; 1 từ văn kiện); 13 chủ đề; 763 quan hệ có kiểu/căn cứ.
- Backend FastAPI đủ endpoint bắt buộc; Ollama Cloud client (timeout/retry/backoff/auth); ElevenLabs TTS (chia đoạn, cache, quota); xác thực citation bằng code; từ chối khi thiếu bằng chứng; fallback khi LLM/TTS lỗi; chống prompt injection ở mức context + system prompt.
- Frontend 8 trang, 3 ngôn ngữ, audio player, lightbox, trạng thái loading/empty/error, responsive.
- 72 + 18 test pass; báo cáo chunking/retrieval có số đo.

## CHƯA làm được / chưa đạt (không giả vờ hoàn thành)
1. **Chưa gọi LLM/TTS thật** (không có khoá; mạng môi trường chặn ollama.com, elevenlabs.io). Mọi chỉ số chất lượng câu trả lời (faithfulness, answer relevancy, citation accuracy trên đầu ra thật, abstention của LLM, đa ngôn ngữ) **chưa đo**. Tên endpoint/model/giới hạn được xác minh qua tài liệu công khai tìm được (docs.ollama.com/cloud, help.elevenlabs.io), chưa thử gọi.
2. **Không có embedding ngữ nghĩa**: không tải được model từ HuggingFace. Retrieval hiện là BM25 + char-TF-IDF + glossary đa ngôn ngữ biên soạn tay (`glossary.py`); truy vấn tiếng Anh/Trung chỉ tốt với các thuật ngữ có trong glossary. Adapter `sbert` (multilingual-e5) đã viết nhưng *chưa chạy*. **Không có image embedding** → truy xuất ảnh là metadata-based. Không dùng ChromaDB/FAISS (chỉ mục trong bộ nhớ, đủ cho 614 chunk).
3. **Nguồn Genève:** không tải được toàn văn 5 URL bắt buộc (allowlist). Nội dung điều khoản diễn giải từ trích đoạn kết quả tìm kiếm, trạng thái `partially_verified_via_search_snippets`; DOC005 (UN Peacemaker) `not_accessed`. **Chưa có** nghiên cứu học thuật về di cư 1954–1955 (chỉ có nội dung sách, chương 5).
4. **OCR chưa được người kiểm tra:** 12 nửa trang cần xác minh thủ công (danh sách trong DATASET_DOCUMENTATION); lỗi dấu còn nhiều. Caption 4 hình sách bị cắt; 9 ảnh ZIP độ tin cậy `low`.
5. **Mô tả ảnh/đáp án chuẩn do nhóm phát triển (AI) biên soạn**, chưa có chuyên gia lịch sử duyệt. Năm chụp 34 ảnh = "Chưa xác định"; quyền sử dụng ảnh chưa xác định (watermark LIFE/TikTok/corbis chỉ được ghi nhận) – cần làm rõ trước khi trưng bày công khai.
6. Mục tiêu Precision@5 ≥ 0.70, Hit@5 ≥ 0.90, Abstention ≥ 0.90 **chưa đạt** (xem RAG_EVALUATION_REPORT).
7. Mô tả ảnh chỉ có tiếng Việt (tiêu đề ảnh có en/zh); nội dung sách chỉ tiếng Việt; chưa có bản dịch KB.
8. Docker chưa build; không có test tích hợp tự động với dịch vụ thật.

## Nâng cấp 31/10/2026: bảo tàng số kể chuyện
Đã làm: trang chủ kể chuyện 4 chương có trích dẫn đã kiểm tra, timeline tương tác có nhãn ảnh trung thực, gallery editorial, chat kiểu hướng dẫn viên, prompt + hồ sơ câu hỏi + mở rộng context (Context Recall 0.777→0.850), bộ test 60 câu, 81+22 test pass. Chưa làm được: đo chất lượng thuyết minh của mô hình thật (thiếu khoá). Chi tiết: `docs/REDESIGN_REPORT.md`.

## Việc tiếp theo đề xuất
Đặt khoá → chạy đánh giá E2E thật và lưu trace → tải model embedding đa ngôn ngữ (`EMBEDDING_BACKEND=sbert`) và so sánh → nhờ chuyên gia hiệu đính OCR/ảnh/đáp án chuẩn → bổ sung toàn văn Genève và nghiên cứu di cư 1954–1955 → xác minh bản quyền ảnh.

## Bổ sung nguồn 31/10/2026 (chi tiết: `docs/SUPPLEMENT_INTEGRATION_REPORT.md`)
- **Đã thêm** (dữ liệu cũ giữ nguyên, kiểm tra bằng diff JSON):
  - 3 bài viết thứ cấp: SRC003 (Minh Vượng), SRC004 (có lời kể nhân chứng), SRC005. Tổng 53 chunk, trích dẫn theo **số dòng** tệp gốc.
  - Archive_4.zip (SRC006): 16 ảnh duy nhất, giữ tên file gốc. Tiêu đề theo tên file được gắn nhãn chưa xác minh. 9 tên file trùng chú thích ảnh trong SRC003.
  - 9 ghi chú đối chiếu (NOTE-01…09) nêu chỗ sách và bài viết khác nhau về niên đại và số liệu.
  - 2 sự kiện mới. Tổng hiện có 676 chunk, 65 ảnh, 31 sự kiện, 1.571 quan hệ.
- **Kiểm thử:** pytest 104 passed (+23), vitest 24 passed (+2).
- **Đánh giá truy xuất:**
  - Gold mới 16 câu: Hit@5 0,938.
  - Ảnh theo nội dung tên file: Hit@3 1,0.
  - Gold cũ 60 câu: Recall@5 0,777 → 0,787, nhưng Recall@10 0,866 → 0,838 và MRR 0,678 → 0,636 (đánh giá theo nhãn chỉ trang sách).
- **Chưa làm:** chưa có URL hay ngày đăng của 3 bài viết; nguồn gốc và bản quyền ảnh Archive_4 chưa xác định; chưa kiểm chứng với LLM thật rằng câu trả lời nêu cả hai phía khi nguồn mâu thuẫn.
- **Cập nhật lần 2 (31/10/2026):**
  - Thêm mục "Những mẩu chuyện thú vị": 10 chuyện vi/en/zh, trang `/stories`, section trên trang chủ, `GET /api/anecdotes`. Mọi trích dẫn sách/bài viết khớp neo.
  - Thêm 4 nguồn báo web (WEB001–004) dạng bản ghi diễn giải và 2 ghi chú đối chiếu mới (NOTE-10, NOTE-11).
  - Bỏ cụm "theo tên file" khỏi mọi nội dung hiển thị của ảnh.
  - pytest 107 passed, vitest 25 passed.
  - MRR trên 60 câu cũ theo nhãn chỉ trang sách: 0,609.


## Cập nhật 08/11/2026 – Nhà trưng bày số + bản dịch khu vực
- `scripts/curation_hall.py`: 15 hiện vật cho giao diện phòng trưng bày (vị trí trên ảnh phòng, nhãn và lời kể vi/en/zh, trích dẫn). Trích dẫn sách có anchor được kiểm tra trên OCR trang in khi build (đã sửa 5 trích dẫn về đúng trang in: 51, 207, 222, 226, 239). Không còn cảnh báo anchor.
- Nguồn mới dùng cho hiện vật: ngôi sao đồng trên cột cờ (tr.188 + SRC003 dòng 75 – hai nguồn khác nhau về số bóng điện, nêu cả hai), cột mốc khu phi quân sự (tr.27, 51), truyền đơn 2-1967 (tr.222), máy vô tuyến điện/ống nhòm trận Dốc Miếu 3-1967 (tr.226), sơ tán học sinh K.8 (tr.237–239), bến đò Tùng Luật B (tr.207), công an giới tuyến (tr.62).
- `zones.json`: thêm `museum.hall`; sự kiện khu Cầu/Kỳ đài có `title_i18n`/`summary_i18n` (tóm tắt zh mới); Tượng đài/Nhà liên hợp có `title_i18n`, `subtitle_i18n`, `paragraphs_i18n`. `exhibits.json`: ảnh có `title_en`/`title_zh` (thêm bản dịch tên 12 hình in trong sách).
- Kiểm thử: pytest **111 passed** (thêm `test_museum_hall_items_trilingual_and_cited`, `test_zone_translations`).
- Chưa đo: chất lượng giọng ElevenLabs và câu trả lời LLM (môi trường phát triển không có khoá API; chat chạy chế độ trích xuất, thuyết minh dùng giọng trình duyệt).
