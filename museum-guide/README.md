# Multimodal AI Museum Guide – Cầu Hiền Lương, vĩ tuyến 17 (1954–1967)

Trợ lý ảo & thuyết minh đa ngôn ngữ (vi/en/zh): hỏi đáp dựa trên sách *Đôi bờ giới tuyến (1954–1967)* (TS. Hoàng Chí Hiếu) + 34 ảnh tư liệu + văn kiện Genève; có nguồn/số trang, ảnh liên quan, dòng thời gian, chủ đề và thuyết minh bằng giọng nói.

**Kiến trúc:** OCR/ingestion → Knowledge Base (SQLite) → hybrid retrieval (BM25 + char-TF-IDF, RRF) → context builder → Ollama Cloud (`gpt-oss:120b`) → **xác thực citation bằng code** → UI React + ElevenLabs TTS (`eleven_flash_v2_5`).

> **Trung thực về năng lực:** retrieval ảnh là *metadata-based* (KHÔNG có image embedding); retrieval văn bản mặc định là từ khoá/n-gram + glossary đa ngôn ngữ (dense embedding đã cài adapter nhưng *chưa chạy/kiểm thử* ở môi trường phát triển). Xem `PROJECT_STATUS.md`.

> **Cập nhật 31/10/2026:** đã bổ sung 3 bài viết lịch sử và 16 ảnh từ Archive_4.zip vào kho tư liệu và pipeline RAG. Xem `docs/SUPPLEMENT_INTEGRATION_REPORT.md`.

## Cấu trúc
```
backend/   FastAPI (app/api, services, database, core), tests/, requirements.txt, .env.example
frontend/  React + Vite + TypeScript + Tailwind, Vitest
scripts/   ingest_pdf, detect_figures, match_images, build_knowledge_base, verify_extraction, run_retrieval_eval, eval_chunking
data/      raw/ (PDF, ZIP, ảnh giải nén), processed/ (OCR JSON, ảnh trang), images/book, museum.db
knowledge_base/  bản xuất JSON của toàn bộ KB (sources, chunks, images, events, relations…)
docs/      DATASET_DOCUMENTATION, RAG_EVALUATION_REPORT, CHUNKING_EVALUATION, TEST_REPORT, API_DOCUMENTATION, screenshots
tests/evaluation/rag_test_dataset.json   bộ câu hỏi đánh giá độc lập
```

## Cài đặt cho người mới (Ubuntu/macOS/Windows WSL)
1. **Python 3.11+** (`python3 --version`) và **Node.js 20+** (`node -v`) – tải từ python.org / nodejs.org. Không cần cài Ollama local, không cần GPU.
2. **Ollama Cloud:** tạo tài khoản tại ollama.com → Settings → Keys → tạo API key.
3. **ElevenLabs:** tạo tài khoản → Profile → API Keys. Gói Free có 10.000 credit/tháng; Flash v2.5 tốn 0,5 credit/ký tự; Free không dùng Voice Library qua API (dùng giọng premade; không có quyền thương mại).
4. Cấu hình:
   ```bash
   cd backend && cp .env.example .env     # điền OLLAMA_API_KEY và ELEVENLABS_API_KEY (không commit .env)
   pip install -r requirements.txt
   ```
   Gọi trực tiếp `https://ollama.com` thì dùng model **`gpt-oss:120b`** (hệ thống tự bỏ hậu tố `-cloud` của `OLLAMA_MODEL=gpt-oss:120b-cloud`).
5. **Dữ liệu:** repo đã kèm `data/museum.db` (đã nạp). Để tái tạo từ nguồn (cần `data/raw/DoiBoGioi…pdf`, `Archive_2.zip` giải nén vào `data/raw/archive2`; cài `tesseract-ocr` + dữ liệu ngôn ngữ `vie`):
   ```bash
   python scripts/ingest_pdf.py            # OCR 130 trang (~2 phút)
   python scripts/detect_figures.py && python scripts/match_images.py
   python scripts/build_knowledge_base.py  # nạp sách, ảnh, sự kiện, văn kiện Genève, quan hệ
   python scripts/verify_extraction.py --write-doc
   ```
   Chỉ mục truy xuất được dựng trong bộ nhớ khi khởi động (~1 giây); không cần bước vector DB riêng.
6. **Chạy:**
   ```bash
   cd frontend && npm install && npm run build      # backend sẽ phục vụ frontend/dist
   cd ../backend && uvicorn app.main:app --port 8000  # mở http://localhost:8000
   # dev: terminal 2: cd frontend && npm run dev  (http://localhost:5173, proxy /api → :8000)
   ```
   Docker: `docker compose up --build` (cần `backend/.env`). *Chưa được build thử trong môi trường phát triển.*
7. **Test:** `cd backend && python -m pytest` (72 test, mock LLM/TTS, không tốn quota) · `cd frontend && npm test` (18 test) · đánh giá retrieval: `python scripts/run_retrieval_eval.py`, chunking: `python scripts/eval_chunking.py`.
   Test tích hợp với dịch vụ thật: đặt khoá rồi gọi thủ công `curl -X POST localhost:8000/api/chat -H 'Content-Type: application/json' -d '{"message":"Cầu Hiền Lương bị chia đôi mỗi bên dài bao nhiêu?","language":"vi"}'` (đánh dấu `@pytest.mark.integration`, chưa có test tự động vì chưa có khoá).

## Khắc phục lỗi thường gặp
| Triệu chứng | Cách xử lý |
|---|---|
| `mode: extractive_fallback`, `llm_error:ollama_key_missing` | Chưa đặt `OLLAMA_API_KEY` trong `backend/.env`; khởi động lại backend |
| `llm_auth_error` | Khoá sai/hết hạn; kiểm tra bằng `curl -H "Authorization: Bearer $KEY" https://ollama.com/api/tags` |
| `llm_model_not_found` | Dùng `gpt-oss:120b` (không `-cloud`) khi host là ollama.com |
| `tts_quota_exceeded` / `tts_rate_limited` | Hết credit/giới hạn tốc độ; chatbot vẫn chạy, audio được cache nên không tốn lại |
| TTS lỗi voice | Gói Free chỉ dùng voice premade; đặt `ELEVENLABS_VOICE_*` |
| Ảnh/trang trống | Chạy `python scripts/build_knowledge_base.py`; kiểm tra `data/raw/archive2` có 34 ảnh |
| OCR sai dấu | Hiện tượng bình thường của bản scan độ phân giải thấp; văn bản gốc được giữ nguyên, tìm kiếm chịu lỗi dấu |
