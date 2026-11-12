# API (FastAPI) – tài liệu tương tác tại `/docs`
Lỗi trả dạng `{"error":{"code","message"[,"details"]}}`. Giới hạn body 20.000 byte (413). `session_id` khớp `^[A-Za-z0-9_-]{1,64}$`.

| Method | Endpoint | Mô tả |
|---|---|---|
| POST | `/api/chat` | `{message(1–2000), language: vi|en|zh|auto, session_id}` → câu trả lời + nguồn + ảnh |
| GET | `/api/search?q=&k=&source_type=&chapter=` | Chỉ truy xuất (không LLM), trả điểm thành phần |
| GET | `/api/images?q=&topic=&kind=&hide_variants=&limit=&offset=` | Danh sách ảnh (Gallery) |
| GET | `/api/images/{id}` | **Chi tiết ảnh** (JSON, 20 trường metadata + quan hệ). *Khác ví dụ gốc*: file ảnh ở endpoint dưới |
| GET | `/api/images/{id}/file?size=thumb|medium` | File ảnh (chống path traversal, có thumbnail cache) |
| GET | `/api/topics`, `/api/topics/{id}` | Chủ đề / chi tiết (chương, sự kiện, ảnh, đoạn sách) |
| GET | `/api/timeline?period=pre-1954|1954-1956|1956-1967` | Sự kiện (mỗi sự kiện có trang sách hoặc điều khoản) |
| POST | `/api/narration/generate` | `{text, language, voice_id?}` → `{audio_id,audio_url,cached,segments}`; 503 + mã lỗi nếu TTS lỗi |
| GET | `/api/narration/{audio_id}` | MP3 (audio_id là hex 40 ký tự) |
| GET | `/api/health` | Trạng thái (không lộ khoá; chỉ boolean `configured`) |
| GET | `/api/documents`, `/api/documents/SRC001/pages/{trang_in}` | Tài liệu + văn bản OCR theo trang in |
| GET | `/api/sources`, `/api/sources/{id}` | Registry nguồn |

## Phản hồi `/api/chat`
`answer` (có nhãn `[S1]`), `language`, `sources[{label,source_id,source_title,source_type,chunk_id,pdf_page,printed_page,printed_page_end,provision,chapter,content,verification_status,cited}]`, `images[{image_id,title,image_url,thumb_url,caption,time_period}]`, `confidence`, `insufficient_evidence`, `mode` (`llm|abstain|extractive_fallback`), `warnings[]`, `retrieval{backend,glossary_hits,top_scores}`.
Mọi trang/nguồn/ảnh lấy từ DB theo nhãn đã truy xuất; nhãn LLM tự bịa bị loại (`removed_unknown_citation_labels`); năm không có trong context bị cảnh báo (`ungrounded_years`).
