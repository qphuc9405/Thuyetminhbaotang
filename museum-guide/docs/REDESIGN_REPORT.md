# Báo cáo nâng cấp: Bảo tàng số kể chuyện & Hướng dẫn viên AI

## 1. Chẩn đoán trước khi sửa (đọc code hiện có)
| Vấn đề | Nguyên nhân tìm thấy |
|---|---|
| Câu trả lời ngắn, khô | System prompt ép *"at most ~180 words"*; `max_tokens=1200`; mọi câu hỏi dùng chung `top_k=6` và context 7.000 ký tự; không gom đoạn liền kề của cùng sự kiện |
| Trang chủ như trang điều hướng | Home chỉ có tiêu đề, nút, câu hỏi mẫu, trạng thái hệ thống; không có ảnh, không có mạch kể |
| Timeline là danh sách | Chỉ 3/29 sự kiện có ảnh; không có cửa sổ thuyết minh, không có mốc trước/sau |
| **Lỗi dữ liệu** | Sự kiện "cầu có hai màu" (EV19) bị gắn nhầm với BKFIG10 (bưu thiếp) thay vì BKFIG11 (hình cầu hai màu) – đã sửa |

## 2. Thay đổi backend / RAG (không phá API cũ; chỉ thêm trường)
- **`answer_profiles.py` (mới):** phân loại câu hỏi → hồ sơ: `simple` (top-6, 100–180 từ, 1.100 token), `event`/`entity` (top-8 + đoạn liền kề của 2 kết quả đầu, 200–350 từ, 12.000 ký tự context), `period` (top-10 +3, 350–550 từ), `story` (top-12 +4, 450–700 từ, 16.000 ký tự, 3.400 token, context sắp theo trang). Nhận biết đối tượng nghe: học sinh / đoàn khách.
- **`expand_with_neighbors`:** bổ sung đoạn trước/sau *cùng chương* (một sự kiện thường trải nhiều trang). Đoạn bổ sung đặt **sau** toàn bộ kết quả để bị cắt trước khi chạm giới hạn – phát hiện qua đo đạc (xem mục 5).
- **System prompt mới** (`rag_service.py`): vai hướng dẫn viên đứng trong phòng trưng bày; mở đầu dẫn dắt → bối cảnh → diễn biến → ý nghĩa → kết nối; đoạn văn liền mạch, hạn chế gạch đầu dòng/tiêu đề; cụm chuyển tiếp; độ dài mục tiêu theo hồ sơ (*"là mục tiêu, không phải hạn ngạch – ngắn hơn là đúng khi tư liệu ít"*); giữ nguyên toàn bộ quy tắc chống bịa (không thêm sự kiện, lời thoại, cảm xúc nhân vật; trích dẫn cuối câu/đoạn; phân biệt Hiệp định 20/7 – Tuyên bố 21/7 – tuyên bố đơn phương; giới tuyến ≠ biên giới; tách 1954–1956 / 1956–1967; không định danh người trong ảnh). Nhiệt độ 0,35 (văn tự nhiên hơn, vẫn thấp).
- Câu hỏi tiếp nối ("nói kỹ hơn về sự kiện vừa đề cập") kế thừa độ sâu và ngữ cảnh câu trước.
- Cảnh báo `short_answer` khi có ≥4 đoạn tư liệu mà câu trả lời < 40% độ dài mục tiêu.
- Phản hồi `/api/chat` thêm `retrieval.profile`, `target_words`, `n_context_chunks`.
- **`/api/story` (mới):** 4 chương trang chủ, mỗi câu khẳng định có trích dẫn; 20 trích dẫn trang sách đều được kiểm tra *anchor* trong OCR khi build (0 cảnh báo). Văn dẫn chuyện do nhóm biên soạn từ các trang được trích; en/zh là bản dịch của nhóm.
- **Timeline:** ảnh cho 25/29 mốc với **nhãn trung thực**: `illustrates` (hình trong sách thuộc chương sự kiện, 2 mốc) hoặc `illustrates_topic` (*"ảnh minh hoạ cùng chủ đề – không phải ảnh chụp tại sự kiện"*). 4 mốc ném bom 1965 không có ảnh phù hợp → để trống, không gán bừa.
- Glossary thêm nhóm "đời sống / người dân / gia đình" (vi/en/zh).

## 3. Thay đổi frontend
- **Hệ thống thiết kế:** giấy ngà `#F2ECE0`, đen than `#1C1915`, nâu đất `#6B5440`, đỏ cờ `#A6261C` (nhấn), xanh lam trầm `#22414F` (dòng sông). Chữ: Noto Serif (tiêu đề) + Be Vietnam Pro (nội dung), **tự host** qua `@fontsource` (đủ dấu tiếng Việt, không phụ thuộc mạng). Góc vuông, ít card, nhiều khoảng trắng, ảnh xử lý nhẹ tông tư liệu. Chuyển động: ken-burns chậm ở hero, chữ hiện dần, khối nội dung hiện khi cuộn; tắt hoàn toàn khi người dùng bật *reduced motion*.
- **Trang chủ (`Home.tsx`)**: Hero toàn màn hình dùng ảnh IMG034 (độ tin cậy cao, trùng hình tr.187) + tiêu đề, khẩu hiệu, 1954–1967, hai nút hành trình/hướng dẫn viên, ghi chú nguồn ảnh → 4 chương câu chuyện (ảnh lớn xen kẽ trái/phải, số chương, giai đoạn, đoạn dẫn, nguồn, 3 nút: chủ đề / dòng thời gian / hỏi hướng dẫn viên) → dải timeline cuộn ngang theo giai đoạn (mở cửa sổ thuyết minh) → phòng trưng bày ảnh chọn lọc (editorial grid) → khu "Hãy để câu chuyện lịch sử được tiếp tục" với câu hỏi theo chủ đề.
- **Chat**: cột trái giới thiệu hướng dẫn viên + 10 câu hỏi theo 5 chủ đề có thật trong kho; câu trả lời trình bày như văn thuyết minh (`RichAnswer`: tách đoạn, **đậm** mốc/thuật ngữ, `###` hiếm khi dùng, chỉ số trích dẫn dẫn tới thẻ nguồn; nhãn không có trong nguồn bị ẩn), ảnh liên quan, "Xem nguồn tư liệu (n)" thu gọn, nghe thuyết minh, liên kết dòng thời gian/phòng trưng bày.
- **Timeline**: dải giới thiệu, ba giai đoạn có tiêu đề và mô tả, trục dọc, mỗi mốc có ảnh/nguồn/nút; `EventModal` dùng chung với trang chủ: ảnh + nhãn minh hoạ, tóm tắt, nguồn, bằng chứng OCR, hỏi chatbot, xem chủ đề, mốc trước/sau (phím ←/→, Esc); nhận `?period=` từ trang chủ.
- **Gallery**: tiêu đề + giới thiệu, chip chủ đề, bố cục masonry ảnh lớn đúng tỉ lệ (có width/height chống nhảy layout), nhãn kiểu bảo tàng. **Chi tiết ảnh**: ảnh lớn dính khi cuộn + nhãn bảo tàng.
- Điều hướng: header tối, trong suốt trên hero, menu thu gọn trên mobile; toàn bộ chuỗi giao diện mới có vi/en/zh.

## 4. Danh sách file
**Mới:** `backend/app/services/answer_profiles.py`, `backend/app/api/story.py`, `backend/tests/test_storytelling.py`, `frontend/src/components/{RichAnswer,EventModal}.tsx`, `frontend/src/lib/{useReveal,questions}.ts`, `knowledge_base/story.json` (sinh tự động), `scripts/run_llm_eval.py`, `scripts/eval_context_recall.py`, `docs/REDESIGN_REPORT.md`, `docs/screenshots/after/*`.
**Sửa:** `backend/app/services/{rag_service,retrieval_service,glossary}.py`, `backend/app/api/{timeline,images}.py`, `backend/app/main.py`, `scripts/{curation_kb,build_knowledge_base}.py`, `tests/evaluation/rag_test_dataset.json` (38 → 60 câu), `frontend/src/{index.css,api/client.ts,i18n/index.tsx}`, `frontend/tailwind.config.js`, `frontend/package.json` (+2 font), `frontend/src/components/Layout.tsx`, `frontend/src/pages/{Home,Chat,Timeline,Gallery,ImageDetail}.tsx`, `frontend/src/__tests__/*`.
Không xoá dữ liệu lịch sử; API cũ giữ nguyên (chỉ thêm trường/endpoint).

## 5. Kiểm thử đã chạy (trung thực)
| Nhóm | Kết quả |
|---|---|
| Backend pytest (gồm 9 test mới cho hồ sơ câu hỏi, prompt, mở rộng context, câu chuyện, minh hoạ timeline) | **81 passed** |
| Frontend vitest (UI-01…UI-12 theo bảng mới: hero/4 chương/timeline rail/modal mốc trước-sau/câu trả lời dài/chip gallery/đổi ngôn ngữ…) | **22 passed**, build OK |
| Duyệt thật bằng Chromium (desktop 1366, mobile 390): trang chủ, timeline + cửa sổ sự kiện, gallery, chi tiết ảnh, chat | 0 lỗi console, không tràn ngang (`scrollWidth` = viewport) |
| **Context Recall** (đơn vị kỳ vọng có trong context gửi LLM, 49 câu) | cũ **0,777** → mới **0,850**; event 0,875→1,00; entity 0,784→0,922; period 0,50→0,50; story 0,125→0,25 |
| Retrieval trên bộ 60 câu (khó hơn bộ 38 câu cũ) | Recall@5 0,736 · Hit@5 0,776 · Hit@10 0,878 · MRR 0,638 · Precision@5 0,286 · cổng từ chối 0,545 (6/11) |

Phát hiện & sửa nhờ đo: lần đầu, mở rộng đoạn liền kề làm Context Recall nhóm entity **giảm** (0,784→0,745) vì đoạn chèn xen đẩy kết quả hạng 5–6 ra khỏi giới hạn ký tự; sau khi đặt đoạn bổ sung ở cuối: 0,922. Thử tăng trọng số "cụm từ" ×2: MRR +0,024 nhưng Recall@5 −0,010 → **đã hoàn tác** (không đủ bằng chứng).

**CHƯA kiểm thử được (không có khoá Ollama/ElevenLabs):** LLM-01…LLM-18 với mô hình thật — chất lượng văn thuyết minh, độ dài thực tế, độ tự nhiên trong 3 ngôn ngữ, Faithfulness, Citation Accuracy trên đầu ra thật. Ảnh `*_chat_layout_MOCK.png` dùng **câu trả lời mẫu do nhóm soạn từ tr.183–186** chỉ để minh hoạ bố cục, *không phải đầu ra của mô hình*; ảnh `*_chat_real_fallback.png` là phản hồi thật khi chưa có khoá. Khi có khoá: `python scripts/run_llm_eval.py` → `docs/llm_eval/summary.json` + phiếu chấm tay `human_rating.csv` (Faithfulness, Naturalness, Readability, vi phạm must_not_guess).

## 6. Ảnh trước/sau
`docs/screenshots/before/` (giao diện cũ) và `docs/screenshots/after/` (desktop & mobile: home_hero, home_full, timeline, timeline_event, gallery, image_detail, chat_real_fallback, chat_layout_MOCK). Ảnh full-page của trang chat có thanh header dính hiện ở giữa ảnh – đó là hiện tượng của chế độ chụp toàn trang, không xuất hiện khi dùng thật.

## 7. Vấn đề còn tồn tại
1. Chưa đo chất lượng thuyết minh thật (mục 5). Văn dẫn trong prompt chỉ *khuyến khích* mô hình viết dài & truyền cảm; độ dài thực tế phụ thuộc mô hình.
2. Câu hỏi kể chuyện toàn giai đoạn: Context Recall mới 0,25 – truy xuất từ khoá chưa gom đủ tư liệu trải nhiều chương. Hướng xử lý: embedding ngữ nghĩa (cần Internet) hoặc truy xuất theo chương/sự kiện cho hồ sơ `story`.
3. Ảnh hero là ảnh lưu trữ 960 px (chất lượng tốt nhất trong kho) – hơi mềm trên màn hình lớn; có watermark LIFE mờ.
4. Nhiều mốc dùng chung một ảnh minh hoạ chủ đề (đã ghi nhãn rõ).
5. Mô tả chi tiết ảnh vẫn chỉ có tiếng Việt; chương câu chuyện, tiêu đề, giao diện đã có vi/en/zh.
6. Cổng từ chối trước LLM chỉ chặn câu rõ ràng ngoài miền; câu "trong miền nhưng không có đáp án" (RAG-048/049, U01, U06) dựa vào LLM — chưa đo.

## 8. Chạy lại
```
python scripts/build_knowledge_base.py          # sinh story.json + quan hệ ảnh–sự kiện mới
cd frontend && npm install && npm run build     # thêm @fontsource
cd ../backend && uvicorn app.main:app --port 8000
python scripts/run_retrieval_eval.py && python scripts/eval_context_recall.py   # không tốn quota
python scripts/run_llm_eval.py                  # cần OLLAMA_API_KEY, TỐN QUOTA
```
