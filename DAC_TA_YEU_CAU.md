# ĐẶC TẢ YÊU CẦU — THUYẾT MINH BẢO TÀNG VĨ TUYẾN 17

**Phiên bản:** 1.0 · **Ngày rà soát:** 11/11/2026  
**Tên mô tả đề tài:** Hệ thống tham quan bảo tàng số và trợ lý thuyết minh đa ngôn ngữ về di tích đôi bờ Hiền Lương – Bến Hải, Vĩ tuyến 17.

## 1. Mục đích và căn cứ lập đặc tả

Tài liệu thống nhất phạm vi đề tài theo mã nguồn, dữ liệu và công việc đã có trong thư mục dự án. Đây là bản đặc tả được tái dựng từ sản phẩm hiện tại, **không phải bản sao đề bài gốc hoặc văn bản nghiệm thu đã được giảng viên/bảo tàng phê duyệt**; chưa tìm thấy các văn bản đó trong thư mục được rà soát.

Căn cứ được ưu tiên theo thứ tự:

1. Mã nguồn thực sự được ứng dụng chính sử dụng và dữ liệu hiện có.
2. Cấu hình chạy, hợp đồng API và các tệp kiểm thử.
3. Kết quả đánh giá JSON đã lưu; báo cáo có ghi rõ bộ dữ liệu và cách đo.
4. README, PROJECT_STATUS và các báo cáo mô tả theo từng đợt phát triển.

Khi tài liệu cũ khác mã nguồn, bản này mô tả mã nguồn hiện tại và ghi riêng phần khác biệt. Không suy ra một chức năng đã hoạt động thực tế chỉ vì có mã nguồn hoặc có test mô phỏng.

### 1.1. Cách đọc trạng thái

| Ký hiệu | Ý nghĩa |
|---|---|
| HT | Có trong mã nguồn hoặc dữ liệu hiện tại; chưa đồng nghĩa đã chạy kiểm thử lại trong lần rà soát này |
| ĐK | Có triển khai nhưng phụ thuộc dịch vụ, cấu hình hoặc năng lực trình duyệt |
| CX | Chưa đủ bằng chứng xác nhận chất lượng/hoạt động đầu cuối |
| BS | Yêu cầu cần bổ sung hoặc hoàn thiện; không được tính là đã hoàn thành |

Các câu “phải/cần” trong bảng yêu cầu là hành vi cần nghiệm thu. Cột trạng thái thể hiện mức đáp ứng đang có. Các đề xuất chưa có trong sản phẩm được ghi rõ BS hoặc “cần chốt”.

### 1.2. Giới hạn của lần rà soát

Đã đọc mã nguồn liên quan, kiểm kê JSON, mở SQLite ở chế độ chỉ đọc và đối chiếu tài liệu. Chưa khởi chạy ứng dụng, chưa chạy lại pytest/Vitest/build, chưa gọi Ollama/ElevenLabs. Máy hiện tại chưa có thư viện Python pytest/FastAPI/SQLAlchemy và chưa có `frontend/node_modules`; không cài thêm thư viện trong công việc lập đặc tả này. Kết quả kiểm thử lịch sử được trình bày riêng tại mục 10.

## 2. Bài toán, mục tiêu và người sử dụng

### 2.1. Bài toán

Tư liệu về giới tuyến Hiền Lương – Bến Hải gồm sách scan, ảnh, bài viết và văn kiện, khó tra cứu và khó chuyển thành một hành trình tham quan có lời kể. Hệ thống tổ chức những tư liệu này thành bản đồ, khu tham quan, chủ đề và mục trưng bày; cung cấp nội dung đọc/nghe cùng chức năng hỏi đáp có nguồn.

### 2.2. Mục tiêu

- Cho khách tham quan khám phá năm địa điểm từ bản đồ minh họa.
- Tổ chức Nhà trưng bày thành Gian khánh tiết và bốn chủ đề có nội dung, ảnh và nguồn.
- Cung cấp trợ lý hỏi đáp dựa trên kho tư liệu; hỗ trợ câu hỏi tiếp nối và câu trả lời kèm ảnh.
- Cung cấp giao diện và nội dung biên soạn bằng tiếng Việt, Anh, Trung; phát thuyết minh theo ngôn ngữ được chọn.
- Giữ khả năng truy nguyên nội dung về nguồn, trang sách, dòng bài viết hoặc điều khoản phù hợp.
- Có bằng chứng đánh giá chất lượng truy xuất và quy trình đánh giá câu trả lời; công khai giới hạn của dữ liệu và AI.

### 2.3. Người sử dụng

| Đối tượng | Nhu cầu và cách sử dụng hiện tại |
|---|---|
| Khách tham quan, học sinh, người tìm hiểu lịch sử | Xem bản đồ, mở khu/chủ đề, đọc/nghe, xem ảnh, hỏi đáp; không cần đăng nhập |
| Người biên soạn nội dung | Cập nhật dữ liệu và script biên soạn, dựng lại kho tư liệu; chưa có trang quản trị riêng |
| Người vận hành/nghiệm thu | Cấu hình dịch vụ, chạy hệ thống, kiểm tra API, chạy bộ đánh giá |

## 3. Phạm vi nội dung và sản phẩm

### 3.1. Phạm vi lịch sử

Nguồn sách cốt lõi là *Đôi bờ giới tuyến (1954–1967)* của TS. Hoàng Chí Hiếu. Nội dung ứng dụng bao gồm bối cảnh trước 1954, giai đoạn giới tuyến 1954–1967, phần mở rộng về năm 1972 và quá trình hồi sinh/đoàn tụ, cùng giới thiệu di tích hiện nay.

Vì vậy **không giới hạn toàn bộ sản phẩm ở giai đoạn 1954–1967**. Các nội dung ngoài phạm vi sách phải dẫn nguồn bổ sung phù hợp; không lấy tên sách làm bằng chứng cho sự kiện sau 1967. Đây là phạm vi quan sát được từ dữ liệu, cần đối chiếu với đề bài chính thức khi có.

### 3.2. Năm địa điểm

| Mã | Tên hiển thị tiếng Việt | Đường dẫn | Dạng nội dung |
|---|---|---|---|
| bridge | Cầu Hiền Lương | `#bridge` | Câu chuyện, dòng thời gian, ảnh, lời đọc |
| museum | Nhà trưng bày Vĩ tuyến 17 | `#museum` | Gian khánh tiết, bốn chủ đề và các mục trưng bày |
| flag | Kỳ đài Hiền Lương | `#flag` | Câu chuyện, dòng thời gian, ảnh, lời đọc |
| monument | Tượng đài Khát vọng thống nhất | `#monument` | Giới thiệu địa điểm, ảnh và nguồn |
| union | Nhà liên hợp | `#union` | Giới thiệu địa điểm, ảnh và nguồn |

### 3.3. Nhà trưng bày hiện hành

Ứng dụng chính sử dụng `frontend/src/Museum.tsx` và dữ liệu `museum.topics` trong `knowledge_base/zones.json`.

| Thành phần | Nội dung hiện có |
|---|---|
| Gian khánh tiết | Giới thiệu chung, nguồn, ảnh, thanh thuyết minh và liên kết bốn chủ đề |
| Chủ đề 1 | Hiệp định Giơ-ne-vơ và giới tuyến quân sự tạm thời — 4 mục |
| Chủ đề 2 | Tinh thần không khuất phục của người dân Vĩnh Linh và cuộc chiến đấu bảo vệ địa đầu giới tuyến — 4 mục |
| Chủ đề 3 | Nhân dân vùng Nam vĩ tuyến 17 với cuộc đấu tranh vì khát vọng thống nhất đất nước — 6 mục |
| Chủ đề 4 | Vĩ tuyến 17 sau giải phóng Quảng Trị năm 1972 — 5 mục |

Ba điểm bấm hiện vật lớn trong phòng là **Mẹ Vĩnh Linh vá cờ**, **Ngôi sao**, **Loa phát thanh**. Chúng dẫn tới mục đã có trong chủ đề 2/3, không phải ba bản ghi cộng thêm vào tổng 19 mục.

Các mục trưng bày là đơn vị nội dung số, chưa phải danh mục hiện vật vật lý đã được bảo tàng xác nhận. Các bộ 15 mục `museum.hall`, 56 bản ghi `exhibits.json` và 19 mục theo chủ đề phục vụ những cấu trúc khác nhau, không cộng hoặc dùng thay thế nhau.

### 3.4. Những chức năng ngoài phạm vi đã triển khai

Chưa có tài khoản/đăng nhập, phân quyền biên tập, CMS trên web, bán vé, đặt lịch, thanh toán, định vị GPS trong di tích, AR/VR, mô hình 3D xoay được, tải ảnh lên để AI nhận diện, tìm ảnh bằng image embedding hoặc chế độ offline đầy đủ. Các cảnh có phối cảnh 3D hiện là ảnh nền minh họa 2D.

## 4. Kiến trúc và thành phần hiện hành

```text
Trình duyệt → frontend/ (React + TypeScript + Vite)
                └─ /mg/* → museum-guide/backend/ (FastAPI)
                              ├─ SQLite: data/museum.db
                              ├─ JSON biên soạn: knowledge_base/
                              ├─ truy xuất văn bản/metadata ảnh
                              ├─ Ollama Cloud: sinh câu trả lời
                              └─ ElevenLabs: tạo âm thanh, lưu cache

Tư liệu gốc → OCR/kiểm kê → script biên soạn → dựng SQLite + JSON
```

- `./run.sh` tại thư mục dự án khởi chạy frontend cổng 5173 và backend museum-guide cổng 8077 theo mặc định; script còn chạy backend mẫu cổng 8000 nếu cổng trống.
- `frontend/vite.config.ts` chuyển `/mg/*` tới museum-guide và bỏ tiền tố `/mg` trước khi chuyển tiếp. Các API ở mục 8 ghi theo đường dẫn phía backend.
- `backend/` ngoài cùng là backend mẫu. Luồng tham quan/chat/thuyết minh hiện hành sử dụng museum-guide; không dùng lệnh import của backend mẫu để cập nhật kho museum-guide.
- `museum-guide/frontend/` là frontend riêng của phiên bản trước, không được `run.sh` khởi chạy. Báo cáo/test của frontend này không tự động chứng minh giao diện chính hoạt động đúng.
- Cơ chế backend phục vụ `museum-guide/frontend/dist` không phải cấu hình xuất bản đã được chứng minh cho frontend chính. Khi triển khai frontend chính cần cấu hình static hosting và proxy `/mg` riêng, hoặc tích hợp tương đương rồi kiểm thử.

## 5. Yêu cầu chức năng và tiêu chí kiểm tra

### 5.1. Bản đồ, điều hướng và công cụ

| Mã | Yêu cầu và tiêu chí kiểm tra | Hiện trạng | Bằng chứng |
|---|---|---|---|
| FR-01 | Trang chủ có đủ năm địa điểm; nút/thẻ/ghim mở đúng địa điểm | HT | `data.ts`, `App.tsx` |
| FR-02 | Chọn địa điểm chạy chuyển cảnh camera khoảng 900 ms; khóa thao tác lặp trong chuyển cảnh; giảm chuyển động khi thiết bị yêu cầu | HT; cần duyệt trình duyệt thật | `MapCamera.tsx`, `useZoneNavigation.ts`, CSS |
| FR-03 | Về bản đồ, Back/Forward và mở URL trực tiếp phục hồi đúng khu; kiểm tra riêng các URL con Nhà trưng bày | HT; cần kiểm thử đủ đường đi | `useZoneNavigation.ts`, `Museum.tsx` |
| FR-04 | Có công cụ toàn màn hình, chọn ngôn ngữ, bật/tắt tiếng, chia sẻ và sao chép liên kết; phản ánh kết quả/thất bại phù hợp | HT/ĐK với Fullscreen, Share, Clipboard API | `App.tsx` |
| FR-05 | Đổi kích thước cửa sổ không làm mất lựa chọn khu/ngôn ngữ; bố cục điện thoại không có cuộn ngang toàn trang | HT về CSS; CX về kiểm thử bản hiện tại | `responsive.css`, `museum-topics.css` và CSS khu vực |

Ảnh bản đồ chính hiện là `/home-map-open-forecourt-sharp.png`. Tọa độ ghim và camera là phần trăm trên ảnh, không phải tọa độ địa lý đo đạc.

### 5.2. Nội dung tham quan và trưng bày

| Mã | Yêu cầu và tiêu chí kiểm tra | Hiện trạng | Bằng chứng |
|---|---|---|---|
| FR-06 | Cầu và Kỳ đài có câu chuyện, sự kiện theo thời gian, ảnh và nguồn; lựa chọn nội dung cập nhật panel và thuyết minh | HT | `Zones.tsx`, `zones.json` |
| FR-07 | Tượng đài/Nhà liên hợp có đoạn giới thiệu, ảnh và nguồn; dùng nội dung backend thay vì chỉ văn bản mẫu trên bản đồ | HT | `PlaceView` trong `Zones.tsx`, `zones.json` |
| FR-08 | Phòng trưng bày có bốn ghim chủ đề, Gian khánh tiết, ba ghim hiện vật lớn và thanh hành trình gồm năm mục | HT | `Museum.tsx`, `museum.topics` |
| FR-09 | Vào chủ đề thấy danh sách mục trưng bày, tiêu đề, lời kể, ảnh nếu có, nguồn và thanh đọc; hỗ trợ Đọc tiếp/Thu gọn | HT | `TopicView` trong `Museum.tsx` |
| FR-10 | Hiện vật thiếu tư liệu riêng phải hiện “Cần bổ sung nguồn” cùng ghi chú; không trình bày ảnh minh họa như ảnh gốc của hiện vật | HT về nhãn; việc đủ nguồn còn BS | `needs_source`, `needs_note`, `documented` |
| FR-11 | Có thư viện ảnh và câu chuyện; ảnh mở được trong lightbox, có điều khiển phóng/thu, kéo, trước/sau và đóng | HT; thao tác cảm ứng cần kiểm tra thực tế | `common.tsx`, `Lightbox.tsx` |

URL hiện hành: `#museum`, `#museum/gioi-thieu`, `#museum/topic-1` đến `#museum/topic-4`, `#museum/topic-N/<id-mục>`. Ví dụ `#museum/topic-2/choi-loa`.

Chọn mục trong một chủ đề dùng `history.replaceState`, nên Back không bắt buộc đi qua từng mục đã xem. Không lấy đường dẫn hiện vật độc lập của giao diện cũ như `#museum/mother-and-flag` làm URL chuẩn của phiên bản hiện tại.

### 5.3. Hỏi đáp AI

| Mã | Yêu cầu và tiêu chí kiểm tra | Hiện trạng | Bằng chứng |
|---|---|---|---|
| FR-12 | Nhận câu hỏi văn bản, hiện trạng thái chờ, câu trả lời, nguồn và ảnh liên quan; có gợi ý câu hỏi theo khu/mục | HT; chất lượng với LLM thật CX | `App.tsx`, `ChatDock.tsx`, `rag_service.py` |
| FR-13 | Truy xuất nội dung từ kho tư liệu trước khi sinh câu trả lời; đưa metadata nguồn vào context và phản hồi | HT | `retrieval_service.py`, `context_builder.py` |
| FR-14 | Câu trả lời lịch sử phải bám nguồn; thiếu bằng chứng phải từ chối; nguồn mâu thuẫn cần được trình bày có phân biệt | Có cổng bằng chứng, prompt và ghi chú; chất lượng đầu ra CX | `rag_service.py`, `curation_supplement.py` |
| FR-15 | Khi LLM lỗi/thiếu khóa, hệ thống trả chế độ trích xuất từ tư liệu thay vì làm hỏng toàn bộ chat | HT/ĐK với backend | `extractive_fallback` trong `rag_service.py` |
| FR-16 | Kiểm tra nhãn trích dẫn, loại nhãn không có trong context; cảnh báo một số năm không có căn cứ | HT, không phải kiểm chứng ngữ nghĩa toàn bộ câu trả lời | `validate_llm_output` |
| FR-17 | Lưu hội thoại theo `session_id`, sử dụng ngữ cảnh gần đây cho câu hỏi tiếp nối | HT | `api/chat.py`, `repository.py`, `is_followup` |
| FR-18 | Nhập câu hỏi bằng micro khi trình duyệt hỗ trợ; ngôn ngữ nhận dạng theo lựa chọn vi/en/zh | ĐK; là nhận dạng tiếng nói của trình duyệt | `speechInput` trong `App.tsx` |

**Giới hạn cần ghi rõ:**

- Yêu cầu chat hiện chỉ nhận `message`, `language`, `session_id`; chưa có `zone_id`, `topic_id` hoặc `item_id`. Gợi ý theo khu và placeholder không đồng nghĩa truy xuất đã được lọc theo khu.
- “Hiện vật này”, “ở đây” chưa có cơ chế ràng buộc chắc chắn với hiện vật đang mở. Nếu nghiệm thu yêu cầu hiểu ngữ cảnh màn hình thì đây là việc BS.
- Chuyển khu xóa hội thoại hiển thị và hủy yêu cầu đang chờ ở frontend, nhưng `session_id` vẫn giữ trong vòng đời App; backend vẫn lưu lịch sử. Xóa khung chat chưa phải xóa lịch sử server. Cần hoàn thiện nếu yêu cầu tách phiên theo khu hoặc xóa dữ liệu hội thoại.
- Frontend lấy nội dung trả lời/nguồn/ảnh nhưng chưa hiển thị rõ `mode`, `warnings`, `confidence` hay `insufficient_evidence` như các trạng thái riêng. Phân biệt trích xuất dự phòng với câu trả lời sinh bởi LLM trên giao diện là việc BS.
- Bộ kiểm tra citation xác nhận nhãn tồn tại, không chứng minh mọi khẳng định được nguồn hỗ trợ; câu không có citation hợp lệ hoặc có năm đáng ngờ hiện chủ yếu bị hạ độ tin cậy/cảnh báo, không luôn bị chặn.
- Nhập micro không phải hội thoại giọng nói liên tục, và chưa có xử lý ảnh người dùng gửi lên.

### 5.4. Thuyết minh và nhân vật hướng dẫn

| Mã | Yêu cầu và tiêu chí kiểm tra | Hiện trạng | Bằng chứng |
|---|---|---|---|
| FR-19 | Phát/tạm dừng/tiếp tục, bật/tắt tiếng; tại một thời điểm chỉ có một nguồn đọc trong ứng dụng | HT; cần nghe thử thực tế | `audio.ts`, `Narration.tsx` |
| FR-20 | Ưu tiên ElevenLabs cho văn bản thuyết minh; chia đoạn và cache phía server; lỗi dịch vụ thì chuyển sang speechSynthesis nếu có | HT/ĐK; chất lượng dịch vụ thật CX | `narration_service.py`, `tts_service.py`, `audio.ts` |
| FR-21 | Dừng âm thanh khi rời khu/chủ đề hoặc đổi ngôn ngữ; chuyển mục đang đọc phải dừng lời cũ; không tiếp tục phát yêu cầu đã hủy | Có cơ chế; cần kiểm tra đủ Back/Forward/breadcrumb/Esc/đổi mục | `stopAll`, `speak`, các luồng điều hướng |
| FR-22 | Người hướng dẫn xuất hiện theo khu, có bong bóng lời và chuyển động miệng khi đọc | HT; chuyển động là mô phỏng theo trạng thái | `Guide.tsx`, `guides.ts`, `audio.ts` |
| FR-23 | Nếu trình duyệt chặn tự phát phải có thao tác phát thủ công; nếu giọng dự phòng đang dùng phải có thông báo tương ứng | HT/ĐK | `blocked`, `fallback`, `Narration.tsx` |

Lời giới thiệu trang chủ tiếng Việt dùng tệp `/audio/home-introduction.mp3`; Anh/Trung gọi luồng đọc văn bản. Các thanh `NarrationBar` mặc định thử tự đọc khi đổi nội dung nếu chưa tắt tiếng, nhưng trình duyệt có thể chặn autoplay. Thời lượng giọng trình duyệt là ước tính; sóng âm và khẩu hình là hiệu ứng mô phỏng, chưa phải phân tích âm thanh/lip-sync theo âm vị. Chưa có thanh tua âm thanh tương tác trong `NarrationBar`.

### 5.5. Đa ngôn ngữ

| Mã | Yêu cầu và tiêu chí kiểm tra | Hiện trạng | Bằng chứng |
|---|---|---|---|
| FR-24 | Có vi/en/zh; lưu lựa chọn trong localStorage; cập nhật chữ giao diện và thuộc tính ngôn ngữ trang | HT | `i18n.tsx`, `App.tsx` |
| FR-25 | Nội dung biên soạn của khu/chủ đề/mục có bản dịch; thiếu bản dịch thì có quy tắc dùng tiếng Việt dự phòng | HT về cấu trúc và nội dung; chất lượng dịch CX | `L3`, `pick`, `imgTitle`, `zones.json` |
| FR-26 | Câu hỏi gửi đúng lựa chọn ngôn ngữ; chatbot và giọng đọc hướng tới ngôn ngữ đó | HT/ĐK; độ chính xác đa ngôn ngữ CX | `mgChat`, `rag_service.py`, `audio.ts` |

Không đồng nhất giao diện ba ngôn ngữ với toàn bộ kho gốc đã dịch. Nội dung sách OCR và nhiều caption vẫn bằng tiếng Việt; retrieval Anh/Trung hiện dựa nhiều vào glossary ánh xạ thuật ngữ. Chất lượng giọng dự phòng phụ thuộc giọng cài sẵn của trình duyệt/hệ điều hành.

## 6. Yêu cầu dữ liệu và tính truy nguyên

### 6.1. Kiểm kê trực tiếp tại ngày rà soát

| Đối tượng | Số lượng | Cách xác nhận |
|---|---:|---|
| Nguồn | 35 | `sources.json`, bảng `sources` |
| Trang sách | 260 | Bảng `pages`; báo cáo nguồn ghi PDF scan 130 trang chứa các trang sách |
| Đoạn tư liệu | 683 | `chunks.json`, bảng `chunks` |
| Ảnh trong kho | 65 | `images.json`, bảng `images`; không tính mọi ảnh nền/static frontend |
| Sự kiện | 31 | `events.json`, bảng `events` |
| Quan hệ | 1.586 | `relations.json`, bảng `relations` |
| Chủ đề trong CSDL | 13 | Bảng `topics`; khác bốn chủ đề tham quan Nhà trưng bày |
| Bản ghi danh mục trưng bày riêng | 56 | `exhibits.json`; không phải tổng mục của giao diện bốn chủ đề |
| Mục trong bốn chủ đề đang dùng | 19 | `zones.json`: 4 + 4 + 6 + 5 |
| Mục gắn `needs_source=true` | 9 | Theo chủ đề: 2 + 2 + 2 + 3 |

Kho 35 nguồn gồm 1 BOOK, 20 WEB_ARTICLE, 6 HISTORICAL_DOCUMENT, 3 SECONDARY_ARTICLE, 2 ARCHIVAL_PHOTO, 2 REFERENCE_WORK và 1 CURATOR_NOTE. Đây là số bản ghi đăng ký nguồn, không phải 35 tài liệu đều đã được kiểm chứng đầy đủ.

Cầu hiện có 4 chuyện, 10 mốc và 13 ảnh; Kỳ đài có 4 chuyện, 7 mốc và 9 ảnh trong dữ liệu khu. Các số liệu là ảnh chụp trạng thái dữ liệu, không phải hạn mức cố định khi phát triển tiếp.

### 6.2. Quy tắc dữ liệu

| Mã | Yêu cầu | Hiện trạng |
|---|---|---|
| DR-01 | Giữ tư liệu gốc, OCR và metadata để đối chiếu; phân biệt trang PDF với trang sách in | Có pipeline/dữ liệu; OCR còn cần người duyệt |
| DR-02 | Đoạn tư liệu có ID, nguồn, nội dung và vị trí tham chiếu phù hợp; không biến diễn giải của nhóm thành nguyên văn sách | Có schema/pipeline; cần kiểm duyệt nội dung |
| DR-03 | Lời kể biên soạn có citation; trích dẫn sách có anchor để kiểm tra khi dựng dữ liệu | Có trong script biên soạn; anchor khớp OCR chưa đảm bảo OCR đúng |
| DR-04 | Ảnh có metadata và quan hệ với sự kiện/chủ đề/đoạn; giữ thông tin chưa xác định thay vì suy đoán | Có cấu trúc dữ liệu; xuất xứ, năm chụp và quyền dùng một số ảnh còn CX |
| DR-05 | Nội dung từ nguồn khác nhau phải được giữ riêng; ghi chú rõ số liệu/niên đại bất đồng | Có CURATOR_NOTE và ghi chú đối chiếu; đầu ra LLM thật cần kiểm tra |
| DR-06 | Phân biệt ảnh cảnh minh họa, ảnh hiện trạng và ảnh tư liệu; ghi nhãn mục chưa có ảnh hiện vật riêng | Có một phần nhãn/ghi chú; cần duyệt toàn bộ nội dung khi nghiệm thu |
| DR-07 | Cập nhật qua script nguồn rồi dựng lại SQLite/JSON; thay đổi dữ liệu phải kiểm tra liên kết và citation | Có `build_knowledge_base.py`; JSON khu được cache ở backend, cần khởi động lại backend để bảo đảm đọc bản mới |

Không yêu cầu xóa mục thiếu nguồn khỏi bản nghiên cứu hiện tại, nhưng các mục đó phải có nhãn. Trước khi coi là danh mục bảo tàng chính thức cần xác nhận hiện vật, tư liệu gốc và quyền sử dụng nội dung.

## 7. Cơ chế AI thực tế và giới hạn năng lực

### 7.1. Luồng hỏi đáp

1. Kiểm tra câu hỏi, ngôn ngữ, mã phiên; lấy lịch sử gần đây.
2. Xử lý câu hỏi tiếp nối, mở rộng thuật ngữ bằng glossary và phân loại nhu cầu trả lời.
3. Truy xuất BM25 + TF-IDF n-gram ký tự, hợp nhất thứ hạng RRF và điều chỉnh theo cụm từ/metadata; có adapter dense tùy chọn.
4. Qua cổng bằng chứng sơ bộ; có thể từ chối trước LLM.
5. Mở rộng context bằng các đoạn lân cận theo hồ sơ câu hỏi; chọn ảnh qua metadata/quan hệ.
6. Gửi context và yêu cầu ngôn ngữ tới Ollama; khi lỗi trả nội dung trích xuất dự phòng.
7. Kiểm tra nhãn nguồn/ảnh và năm, tạo payload có nguồn, ảnh, cảnh báo, chế độ trả lời.

Mặc định `EMBEDDING_BACKEND=tfidf`; không mô tả cấu hình này là embedding ngữ nghĩa đa ngôn ngữ. Adapter `sbert` dùng model cấu hình `intfloat/multilingual-e5-small` cần thư viện/model bổ sung và chưa có bằng chứng chạy thực tế trong tài liệu hiện có. Không dùng FAISS/Chroma trong luồng mặc định; chỉ mục được dựng trong bộ nhớ từ SQLite.

### 7.2. Dịch vụ ngoài

- Ollama mặc định host `https://ollama.com`, cấu hình model `gpt-oss:120b-cloud`; code đổi thành `gpt-oss:120b` khi gọi host này. Đây là cấu hình repo, không phải xác nhận tính sẵn có của dịch vụ tại ngày nghiệm thu.
- ElevenLabs mặc định model `eleven_flash_v2_5`; giọng có thể được chọn theo nhân vật hoặc cấu hình backend.
- Không đưa khóa dịch vụ vào frontend/tài liệu. Có khóa cấu hình chưa đủ chứng minh model/voice/quota hoạt động.
- Tính “đa phương thức” hiện tại là phối hợp văn bản, ảnh và âm thanh ở đầu ra/trải nghiệm; chưa có nhận dạng ảnh đầu vào hay image embedding.

## 8. Hợp đồng API phục vụ đặc tả

### 8.1. Các API chính

| Phương thức | Đường dẫn backend | Vai trò |
|---|---|---|
| GET | `/api/health` | Số lượng dữ liệu, backend retrieval, trạng thái cấu hình LLM/TTS |
| GET | `/api/zones/{zone_id}` | Dữ liệu năm khu; museum trả cả cấu trúc topics và hall |
| GET | `/api/images` | Danh sách ảnh và bộ lọc/phân trang |
| GET | `/api/images/{id}` | Metadata ảnh |
| GET | `/api/images/{id}/file?size=thumb\|medium` | Nội dung ảnh/thumbnail; không có size thì lấy ảnh gốc theo API |
| GET | `/api/anecdotes` | Bộ câu chuyện biên soạn |
| POST | `/api/chat` | Hỏi đáp |
| POST | `/api/narration/generate` | Tạo hoặc lấy âm thanh đã cache |
| GET | `/api/narration/{audio_id}` | Tệp MP3 |
| GET | `/api/search` | Truy xuất văn bản để kiểm tra/đánh giá |
| GET | `/api/topics`, `/api/topics/{id}`, `/api/timeline` | API chủ đề/sự kiện của kho; không đồng nghĩa là trang riêng trong frontend chính |
| GET | `/api/documents`, `/api/documents/SRC001/pages/{trang_in}` | Tài liệu và OCR theo trang sách |
| GET | `/api/sources`, `/api/sources/{id}` | Tra cứu registry nguồn |
| GET | `/api/story`, `/api/exhibits` | API nội dung còn được giữ từ các đợt trước; không phải màn hình mặc định thay cho bản đồ/bốn chủ đề |

### 8.2. Chat

```json
{"message":"Cầu Hiền Lương có hai màu sơn như thế nào?","language":"vi","session_id":"thamquan-01"}
```

- `message`: sau khi bỏ khoảng trắng hai đầu phải không rỗng, tối đa 2.000 ký tự theo schema hiện tại.
- `language`: `vi`, `en`, `zh`, `auto`; frontend chính gửi ngôn ngữ đang chọn.
- `session_id`: 1–64 ký tự, gồm chữ/số/`_`/`-`; mặc định backend là `default`, frontend tạo mã phiên riêng trong bộ nhớ.
- Phản hồi có `answer`, `language`, `sources`, `images`, `confidence`, `insufficient_evidence`, `mode`, `warnings`, `retrieval`.
- `mode`: `llm`, `abstain`, `extractive_fallback`. Không chấm phản hồi fallback như chất lượng mô hình sinh.
- Cấu hình còn biến `max_message_chars=800`, nhưng schema endpoint hiện dùng giới hạn 2.000; không lấy giá trị 800 làm giới hạn API đã thực thi.

### 8.3. Tạo giọng đọc

Body gồm `text` (1–8.000 ký tự), `language` (`vi|en|zh`), `voice_id` tùy chọn. Frontend hiện chuẩn hóa văn bản và cắt ở 7.900 ký tự trước khi gửi. Backend loại nhãn citation khỏi lời đọc, chia đoạn mặc định khoảng 900 ký tự và cache theo model/giọng/ngôn ngữ/văn bản. Thay đổi các thành phần này làm thay khóa cache.

Lỗi ứng dụng có dạng `{"error":{"code":"...","message":"..."}}`; một số lỗi route sử dụng `HTTPException` mặc định của FastAPI và có thể trả `detail`. Chưa được coi toàn bộ API có một định dạng lỗi thống nhất tuyệt đối.

## 9. Yêu cầu phi chức năng

| Mã | Yêu cầu/tiêu chí | Hiện trạng |
|---|---|---|
| NFR-01 | Bố cục dùng được trên desktop, tablet, điện thoại; kiểm tra 320×740, 390×844, 768×1024, 1024×768, 1440×900, 1920×1080 và 844×390 | Các cỡ này là checklist đã ghi trong README; chưa duyệt lại bản hiện hành |
| NFR-02 | Thao tác bằng bàn phím, có tên truy cập cho nút, focus phù hợp, Esc đóng/quay lại theo ngữ cảnh; tôn trọng reduced motion | Có code/ARIA/CSS; chưa có đánh giá đầy đủ theo chuẩn accessibility |
| NFR-03 | Mất kết nối/tải dữ liệu lỗi có thông báo và tải lại; LLM/TTS lỗi không làm mất toàn bộ phần đọc/xem | Có xử lý dự phòng; cần E2E |
| NFR-04 | Không lộ khóa API; kiểm tra đầu vào và đường dẫn file; dữ liệu nguồn được coi là context không tin cậy | Có SecretStr, schema, safe path và prompt; chưa phải kiểm toán bảo mật |
| NFR-05 | Middleware kiểm tra Content-Length vượt 20.000 byte trả 413 | Có code; chưa khẳng định giới hạn body tuyệt đối cho yêu cầu không khai báo Content-Length |
| NFR-06 | Lưu hội thoại phía server cần được mô tả rõ cho vận hành; nếu triển khai công khai cần chốt thời gian lưu, xóa và cách tách phiên | Có SQLite chat_messages; chính sách lưu/xóa là BS |
| NFR-07 | Có quy trình dựng lại kho từ nguồn và chạy hệ thống; ghi rõ môi trường phụ thuộc | Có script; cài mới hoàn toàn và Docker còn CX |
| NFR-08 | Đo thời gian tải, phản hồi chat và tạo giọng trên môi trường nghiệm thu; chốt ngưỡng P95 và số người dùng đồng thời | BS; chưa có SLO hay tải mục tiêu được thống nhất |

`run.sh` kiểm tra Python ≥3.10 và Node ≥18; README riêng của museum-guide hướng dẫn Python ≥3.11, Node ≥20. Chưa có bằng chứng kiểm thử toàn bộ ma trận phiên bản tối thiểu. Nên dùng một môi trường nghiệm thu cố định, ghi đúng phiên bản thực chạy cùng lockfile/thư viện, rồi mới công bố mức tương thích.

## 10. Bằng chứng kiểm thử và chất lượng

### 10.1. Những gì có thể xác nhận từ tệp hiện có

- Frontend chính có **9 ca `it(...)`** trong `frontend/src/__tests__/app.test.tsx`: chuỗi đa ngôn ngữ, fallback âm thanh, điều khiển một nguồn đọc, phòng bốn chủ đề, hiện vật lớn/thanh hành trình, Back trong phòng, đổi tiếng Trung, chat có ảnh/lightbox, khu Cầu. API/Audio được mô phỏng trong các ca này; không phải 9 ca gọi dịch vụ thật.
- PROJECT_STATUS cập nhật 08/11 ghi **111 backend test pass**. TEST_REPORT cũ ghi **107 backend + 25 frontend test pass**; số frontend đó thuộc `museum-guide/frontend` trong ngữ cảnh báo cáo, không dùng thay cho frontend chính.
- Báo cáo ảnh chụp/Playwright và các kết quả pass là bằng chứng lịch sử theo bản được kiểm tra khi đó, chưa chứng minh bản gộp hiện tại đã chạy lại toàn bộ.
- Có bộ đánh giá chính 60 câu (49 có đáp án, 11 không có đáp án) và bộ bổ sung 16 câu có đáp án. Chưa thấy báo cáo kết quả LLM/TTS thật đủ để kết luận chất lượng đã đạt.

### 10.2. Số liệu truy xuất đã lưu

Đọc trực tiếp trường `aggregate` của các tệp JSON dưới đây; **không phải số đo chạy mới ngày 11/11**. Cấu hình kết quả ghi 683 chunk và backend `hybrid(bm25+char-tfidf)`.

| Bộ/cách chấm | Recall@5 | Precision@5 | Hit@5 | MRR | Tỷ lệ từ chối trước LLM trên câu không đáp được |
|---|---:|---:|---:|---:|---:|
| 60 câu, nhãn chuẩn hiện có | 0,787 | 0,278 | 0,837 | 0,609 | 0,545 |
| 60 câu, có xét nguồn bổ sung (`source_aware_relevance=true`) | 0,787 | 0,306 | 0,857 | 0,634 | 0,545 |
| 16 câu bổ sung | 0,819 | 0,300 | 0,938 | 0,674 | Không áp dụng: không có câu ngoài đáp án |

Nguồn số liệu: `retrieval_eval_results.json`, `retrieval_eval_results_source_aware.json`, `retrieval_eval_results_supplement.json`. Không trộn kết quả 38 câu cũ với 60 câu hoặc chọn điểm cao nhất của các lần đo khác nhau để báo cáo một kết quả chung.

Các mục tiêu lịch sử trong báo cáo là Recall@5 ≥0,85; Precision@5 ≥0,70; Hit@5 ≥0,90; Abstention ≥0,90. Bộ 60 câu trong bảng chưa đạt các mức đó. Tỷ lệ từ chối trước LLM không đại diện tỷ lệ từ chối đúng của toàn hệ thống sau LLM.

Ngưỡng Precision@5 cần chốt lại cùng quy tắc gán nhãn: nếu một câu chỉ có tối đa 1–3 đoạn được gán đúng, Precision@5 không thể đạt 0,70 cho riêng câu đó. Không tự giảm ngưỡng để coi là đạt; cần làm rõ thước đo, nhãn liên quan và tập kiểm độc lập.

### 10.3. Quy trình xác nhận trước nghiệm thu

| Mã | Nhóm kiểm tra | Điều kiện đạt cần có | Trạng thái bằng chứng |
|---|---|---|---|
| AC-01 | Khởi chạy và build | Cài/chạy trên môi trường ghi nhận; API health có dữ liệu; build frontend chính thành công | Chưa chạy lại |
| AC-02 | Bản đồ và URL | Mở đủ năm khu; mở URL con; Back/Forward và về bản đồ đúng; không kẹt chuyển cảnh | Có test một phần, cần E2E |
| AC-03 | Nhà trưng bày | Đủ Gian khánh tiết, bốn chủ đề, 19 mục theo snapshot; ba ghim mở đúng mục; nhãn thiếu nguồn hiện đúng | Đối chiếu dữ liệu/mã; chưa duyệt UI thật |
| AC-04 | Âm thanh | Nghe được vi/en/zh; chỉ một nguồn đọc; dừng ở mọi đường thoát; xác nhận fallback và autoplay bị chặn | Có test mô phỏng; dịch vụ thật CX |
| AC-05 | Chat có nguồn | Lưu trace câu hỏi–retrieval–context–đầu ra–citation; phân biệt llm/fallback; chấm câu ngoài kho và nguồn mâu thuẫn | Có script/quy trình; đầu ra thật CX |
| AC-06 | Đa ngôn ngữ | Kiểm tra giao diện, nội dung, câu trả lời và giọng; người biết ngôn ngữ duyệt các bản dịch mẫu | Có chuỗi/bản dịch; chất lượng CX |
| AC-07 | Dữ liệu | Kiểm tra ID/link, số trang, anchor, ảnh; có danh sách OCR/nguồn/hiện vật chưa xác minh | Có dữ liệu/báo cáo; còn nội dung cần duyệt |
| AC-08 | Responsive và lỗi | Kiểm tra các kích thước mục 9; tải lại khi lỗi; không tràn ngang; thao tác cảm ứng/bàn phím | Cần kiểm tra bản gộp |
| AC-09 | Đánh giá truy xuất | Chạy lại cùng tập kiểm/cách chấm, lưu JSON và phiên bản dữ liệu; đối chiếu mục tiêu đã thống nhất | Có kết quả cũ; ngưỡng chưa đạt |

Lệnh tham khảo, chạy từ thư mục phù hợp sau khi đã cài phụ thuộc:

```bash
# Tại thư mục Thuyetminhbaotang/
./run.sh
./run.sh --build  # dựng lại kho rồi chạy; không cần làm cho mỗi lần chỉ xem

# Frontend chính: tại frontend/
npm test
npm run build

# Backend: tại museum-guide/backend/
python -m pytest

# Đánh giá: tại museum-guide/
python scripts/run_retrieval_eval.py
python scripts/run_image_eval.py
python scripts/eval_chunking.py
python scripts/run_llm_eval.py --base http://localhost:8077
```

Lệnh LLM evaluation cần backend đã cấu hình, có thể tiêu tốn quota và tạo tệp kết quả. Các chỉ số tự động trong `run_llm_eval.py` là proxy; faithfulness, tự nhiên, dễ đọc và vi phạm `must_not_guess` còn cần chấm tay. Không coi tên ngôn ngữ trả về hay nhãn citation tồn tại là đủ chứng minh câu trả lời đúng.

## 11. Những điểm cần hoàn thiện/chốt với đề bài chính thức

| Ưu tiên | Việc cần xử lý | Lý do |
|---|---|---|
| P0 | Đối chiếu tên/phạm vi đề tài với văn bản gốc; xác nhận phần sau 1972 nằm trong phạm vi | Tránh dùng giới hạn 1954–1967 để nghiệm thu nội dung rộng hơn |
| P0 | Chạy LLM/TTS thật, lưu bằng chứng và chấm chất lượng trên vi/en/zh | Có tích hợp chưa chứng minh chất lượng sử dụng |
| P0 | Duyệt nguồn lịch sử, OCR quan trọng, 9 mục thiếu nguồn và ảnh | Bảo đảm nội dung không bị hiểu là hồ sơ hiện vật đã xác nhận |
| P1 | Chốt chat toàn kho hay có ngữ cảnh khu/hiện vật; nếu theo khu thì bổ sung tham số, retrieval và quản lý phiên | Hiện frontend chưa truyền ngữ cảnh khu; lịch sử server vẫn dùng chung phiên |
| P1 | Hiển thị chế độ fallback/cảnh báo phù hợp; kiểm tra hành vi khi câu trả lời không có nguồn hợp lệ | Hiện frontend chưa thể hiện hết trạng thái backend |
| P1 | Chốt bộ kiểm độc lập, nhãn và ngưỡng nghiệm thu retrieval/abstention/chất lượng sinh | Số liệu hiện tại chưa đạt ngưỡng lịch sử; cách chấm còn cần thống nhất |
| P1 | Chạy build, test và duyệt giao diện chính sau gộp trên desktop/mobile | Báo cáo cũ và frontend cũ không thay thế kiểm thử bản hiện hành |
| P2 | Chốt triển khai frontend chính, cấu hình proxy, phiên bản runtime, lưu/xóa hội thoại và mức tải | Chưa có cấu hình production được xác nhận đầy đủ |
| P2 | Thử adapter dense đa ngôn ngữ hoặc image embedding nếu đề bài thật sự yêu cầu | Không tự tính adapter chưa chạy hoặc metadata ảnh là năng lực embedding đã đạt |

## 12. Hồ sơ bàn giao và truy vết

Các tệp sau là căn cứ để cập nhật đặc tả khi sản phẩm thay đổi. Liên kết tính từ vị trí tài liệu này.

| Nhóm yêu cầu | Tệp căn cứ |
|---|---|
| Phạm vi giao diện hiện hành | [App.tsx](frontend/src/App.tsx), [Museum.tsx](frontend/src/Museum.tsx), [Zones.tsx](frontend/src/Zones.tsx), [data.ts](frontend/src/data.ts) |
| Bản đồ/điều hướng | [MapCamera.tsx](frontend/src/MapCamera.tsx), [useZoneNavigation.ts](frontend/src/useZoneNavigation.ts) |
| Nội dung bốn chủ đề | [curation_topics.py](museum-guide/scripts/curation_topics.py), [zones.json](museum-guide/knowledge_base/zones.json) |
| API và kiểu dữ liệu frontend | [mg.ts](frontend/src/mg.ts), [schemas](museum-guide/backend/app/schemas/__init__.py), [story API](museum-guide/backend/app/api/story.py), [chat API](museum-guide/backend/app/api/chat.py) |
| AI và nguồn | [rag_service.py](museum-guide/backend/app/services/rag_service.py), [retrieval_service.py](museum-guide/backend/app/services/retrieval_service.py), [context_builder.py](museum-guide/backend/app/services/context_builder.py) |
| Giọng đọc/nhân vật/ngôn ngữ | [audio.ts](frontend/src/audio.ts), [Narration.tsx](frontend/src/Narration.tsx), [Guide.tsx](frontend/src/Guide.tsx), [i18n.tsx](frontend/src/i18n.tsx), [narration_service.py](museum-guide/backend/app/services/narration_service.py) |
| Dữ liệu nguồn và dựng kho | [knowledge_base](museum-guide/knowledge_base/), [build_knowledge_base.py](museum-guide/scripts/build_knowledge_base.py), [DATASET_DOCUMENTATION](museum-guide/docs/DATASET_DOCUMENTATION.md) |
| Chạy và cấu hình | [run.sh](run.sh), [vite.config.ts](frontend/vite.config.ts), [config.py](museum-guide/backend/app/config.py), [requirements.txt](museum-guide/backend/requirements.txt), [package.json](frontend/package.json) |
| Kiểm thử frontend hiện hành | [app.test.tsx](frontend/src/__tests__/app.test.tsx) |
| Đánh giá đã lưu | [kết quả 60 câu](museum-guide/docs/retrieval_eval_results.json), [kết quả xét nguồn bổ sung](museum-guide/docs/retrieval_eval_results_source_aware.json), [kết quả 16 câu](museum-guide/docs/retrieval_eval_results_supplement.json) |
| Quy trình đánh giá LLM | [run_llm_eval.py](museum-guide/scripts/run_llm_eval.py), [bộ 60 câu](museum-guide/tests/evaluation/rag_test_dataset.json) |
| Lịch sử phát triển/giới hạn | [README](README.md), [museum-guide README](museum-guide/README.md), [PROJECT_STATUS](museum-guide/PROJECT_STATUS.md), [TEST_REPORT](museum-guide/docs/TEST_REPORT.md), [RAG_EVALUATION_REPORT](museum-guide/docs/RAG_EVALUATION_REPORT.md) |

### 12.1. Quy tắc cập nhật và xử lý tài liệu cũ

- Dùng tài liệu này làm bản tổng hợp hiện trạng và tiêu chí đề xuất; không ghi đè đề bài chính thức nếu sau này được cung cấp.
- Các mô tả README cũ như “không phát giọng”, “chỉ tiếng Việt”, “7 mục”, “15 hiện vật”, “không cần khóa API” không còn đại diện đầy đủ cho phiên bản hiện hành. Không cần khóa để sử dụng chế độ dự phòng khác với có đủ dịch vụ AI/TTS.
- Số lượng test và dữ liệu phải gắn với phiên bản/bộ kiểm và ngày đo; không cập nhật bằng cách cộng dồn các bản ghi theo lịch sử.
- Thay đổi chức năng cần cập nhật mã FR/DR/NFR liên quan, tiêu chí AC và bằng chứng. Thay đổi dữ liệu cần cập nhật snapshot ở mục 6 và chạy lại đánh giá bị ảnh hưởng.
- Đặc tả này chỉ thêm tài liệu; không sửa mã nguồn, dữ liệu gốc, README hoặc các báo cáo lịch sử trong lần lập bản 1.0.

## 13. Bổ sung vận hành sau khi lập bản 1.0 — 11/11/2026

Sau lần rà soát ở mục 1, đã cài phụ thuộc, chạy ứng dụng và cài Ollama cục bộ `0.40.16` với `qwen2.5:3b`. Backend đã đổi sang host `http://127.0.0.1:11434`; một câu hỏi tiếng Việt qua frontend proxy đã trả HTTP 200, `mode=llm`, 8 phần tử nguồn và 3 ảnh trong 94,7 giây. Có cảnh báo `ungrounded_years:1954`. Xem [bằng chứng kiểm tra local](museum-guide/docs/OLLAMA_LOCAL_VERIFICATION.md).

Điều này bổ sung bằng chứng tích hợp LLM thật cho cấu hình local, không xác nhận toàn bộ chất lượng LLM, các ngưỡng nghiệm thu hoặc cấu hình Ollama Cloud trước đây. ElevenLabs vẫn chưa được kiểm tra thật; các kết quả test/build và đánh giá đa ngôn ngữ trong các mục trước không tự động đổi thành đã đạt. Các phát biểu “chưa khởi chạy/chưa có phụ thuộc/chưa gọi LLM thật” ở phần rà soát ban đầu được hiểu theo thời điểm lập bản 1.0.

### 13.1. Tối ưu độ trễ local cùng ngày

Đã thêm ngân sách prompt/context/đầu ra ngắn cho câu hỏi thường trên Ollama local; giữ ngân sách lớn hơn cho yêu cầu chi tiết. Câu độc lập có nguồn và không có cảnh báo được cache trong RAM tối đa 10 phút, 128 mục; tách ngôn ngữ và không dùng cache chung cho câu hỏi tiếp nối. Cache mất khi backend khởi động lại. Khi đổi kho tư liệu cần khởi động lại để xóa cache. Model được giữ trong RAM 30 phút; timeout backend local đổi từ 300 xuống 90 giây.

Đo lại câu hỏi tổng quan trên bản cuối: 15,55 giây cho lần mới, 0,01 giây cho lần lặp qua cache; câu hỏi mới về chiều cao cột cờ đầu tiên mất 13,13 giây. Vẫn truy xuất đủ ứng viên trước khi chọn đoạn gọn theo nội dung và giữ ghi chú nguồn mâu thuẫn. Đã chạy 118 backend test, 9 frontend test và build frontend thành công. Đây là bằng chứng hiệu năng theo các mẫu đã thử, không thay cho đánh giá chất lượng lịch sử hay ngưỡng latency P95. Chi tiết và điều kiện kiểm thử ở báo cáo local được liên kết trên.
