# Báo cáo tích hợp nguồn bổ sung (2026-10-31, cập nhật lần 2)

Đây là đợt **bổ sung dữ liệu** cho hệ thống đang hoạt động, không xây lại ứng dụng. Cách làm:
- Chỉ thêm nguồn, chunk, ảnh, sự kiện và quan hệ mới.
- Bảng `pages`, `events` và `sources` cũ được giữ nguyên không đổi.
- Thay đổi duy nhất trên chunk cũ là trường `keywords`, do glossary có thêm nhóm mới gắn nhãn tự động.
- Thay đổi duy nhất trên ảnh cũ là `IMG024.duplicate_group = DUP-S024`, ghi nhận IMG036 là cùng bức ảnh.
- Các điều trên đã được kiểm tra bằng diff JSON trước/sau.

## 1. Kết quả tóm tắt

| Hạng mục | Trước | Sau | Ghi chú |
|---|---|---|---|
| Nguồn (`sources`) | 10 | **15** | +SRC003, SRC004, SRC005 (bài viết), SRC006 (Archive_4.zip), NOTE01 (ghi chú đối chiếu) |
| Chunk / bản ghi tri thức | 614 | **676** | +53 chunk bài viết (24 + 14 + 15), +9 ghi chú đối chiếu |
| Ảnh | 49 | **65** | +16 ảnh duy nhất từ Archive_4.zip |
| Sự kiện dòng thời gian | 29 | **31** | +EV29 (sách tr.116, anchor đã khớp OCR), +EV-S01 (bài viết) |
| Quan hệ | 783 | **1.571** | phần lớn là liên kết chủ đề ảnh ↔ trang sách (độ tin cậy thấp) |
| Test backend (pytest) | 81 | **104 pass** | +23 test trong `tests/test_supplement.py` |
| Test frontend (vitest) | 22 | **24 pass** | +2 test giao diện |

## 2. Ảnh – Archive_4.zip

**Kiểm kê:**
- ZIP có 33 mục. Trong đó có 16 tệp `__MACOSX/._*` (bị bỏ qua) và một ZIP lồng `Archive 3.zip`.
- `Archive 3.zip` chứa 10 ảnh trùng byte-for-byte (SHA-256) với ảnh ở cấp ngoài. Chúng được ghi nhận trong báo cáo, không tạo bản ghi trùng.
- Còn lại **16 ảnh duy nhất**: 11 JPEG, 5 WEBP, kích thước từ 333×480 đến 1200×894.

**Lưu trữ:**
- Ảnh nằm ở `data/raw/archive4/`, **giữ nguyên tên file gốc**, kể cả Unicode NFD của macOS và khoảng trắng thừa. ZIP gốc giữ ở `data/raw/Archive_4.zip`.
- Khi tạo tiêu đề và từ khóa, tên file được chuẩn hóa sang NFC.

**Phân biệt căn cứ cho từng trường** (cột `images.metadata_basis`):

| Loại thông tin | Căn cứ | Ví dụ |
|---|---|---|
| `filename_title`, `title` | `filename` – **chưa xác minh** | "Cầu Hiền Lương bị bom Mỹ đánh sập năm 1967" |
| `visual_description`, `visible_text` | `visual_inspection` – đã xem từng ảnh | IMG038: biển ghi "XÂY DỰNG NĂM 1952 / CHIỀU DÀI: 183,8m" |
| `caption` | `document_caption` | 9 tên file trùng **nguyên văn** chú thích ảnh trong bài SRC003, dòng 14, 22, 28, 34, 48, 54, 62–63, 73, 81 |

Chú thích trong SRC003 là của một bài báo thứ cấp, nên **không** được coi là xác minh lịch sử của ảnh.

**Không suy đoán:**
- Trường `estimated_date` của cả 16 ảnh đều là "Chưa xác định".
- `time_period` chỉ ghi khi có căn cứ, và luôn kèm căn cứ đó. Ví dụ: "Theo tên file/chú thích SRC003: 1967 (chưa xác minh; sách tr.183 ghi 9-1966)".
- Không nhận dạng người. "O Nhạn" và "mẹ Diệm" chỉ được ghi là "theo tên file".
- Ảnh IMG038 có chữ "1952" trên biển trong ảnh. Đó là năm xây cầu, không phải năm chụp.

**Phân loại:**
- 10 ảnh `archive_photo`.
- 6 ảnh `contemporary_photo`: ảnh màu chụp di tích hoặc hiện vật thời nay. Loại này có bộ lọc mới trong thư viện ảnh.

**Trùng lặp với ảnh cũ** (dùng SHA-256, pHash, SIFT + RANSAC, rồi kiểm tra lại bằng mắt; không xóa ảnh nào):

| Ảnh mới | Ảnh cũ | Quan hệ | Căn cứ |
|---|---|---|---|
| IMG036 | IMG024 | `variant_of_same_photograph` (nhóm DUP-S024) | SIFT inliers = 1233, pHash cách 0 |
| IMG039 | IMG004 / IMG034 | `same_scene_different_frame` | SIFT inliers 423 / 117; người và xe khác nhau |
| IMG042 | IMG030 | `likely_same_photograph` | SIFT inliers 146; IMG030 là bản màu (có thể đã tô màu) |
| IMG047 | IMG049 | `similar_installation` (độ tin cậy thấp) | chỉ so bằng mắt |

Hai cặp khớp SIFT bị loại vì xem bằng mắt thấy là khớp nhầm: IMG046↔BKFIG07 (khớp chữ trên pano) và IMG045↔IMG019.

**Liên kết ảnh vào hệ thống tìm kiếm và thuyết minh:**

| Quan hệ | Số lượng | Ý nghĩa |
|---|---|---|
| `captioned_in_document` | 9 | Ảnh nằm trong `chunks.image_ids` của đoạn chứa chú thích, nên được chọn trực tiếp khi đoạn đó được truy xuất |
| `adjacent_text_in_document` | 11 | Đoạn ngay trước/sau chú thích (ảnh trong bài nằm giữa hai đoạn nên không chắc minh họa đoạn nào) |
| `topic_corroborated_by_document` | 12 | Ví dụ: IMG045 (cầu hai màu thời nay) ↔ đoạn nói năm 2014 phục hồi hai màu sơn |
| `topic_corroborated_by` | 673 | Liên kết chủ đề tới trang sách |
| `illustrates_topic` | 4 | Tới sự kiện EV02, EV05, EV19, EV26, luôn ghi rõ "không phải ảnh chụp tại sự kiện" |

Ngoài ra, `search_text` của ảnh gồm tiêu đề theo tên file, slug, mô tả, chú thích và bối cảnh, để ImageIndex tìm được theo nội dung tên file.

Bảng đầy đủ từng ảnh: `docs/DATASET_DOCUMENTATION.md` mục 5b, và `scripts/curation_supplement.py`.

## 3. Tài liệu – 3 tệp văn bản

| Nguồn | Tệp gốc | Tác giả | Nhà xuất bản / URL | Số dòng | Chunk |
|---|---|---|---|---|---|
| SRC003 "Về lịch sử cầu Hiền Lương" | `bcb09328-attachment.txt` | Minh Vượng (dòng 85) | Chưa xác định – tệp không ghi | 102 | 24 |
| SRC004 "Những màn chọi cờ, đấu loa…" (có lời kể nhân chứng) | `3fc2987b-attachment.txt` | Chưa xác định (ảnh ghi "Nhật Anh") | Chưa xác định | 92 | 14 |
| SRC005 "Hệ thống loa phóng thanh bờ Bắc…" (kỷ niệm 47 năm) | `01abc224-attachment.txt` | Chưa xác định (ảnh ghi "BTLSQG") | Chưa xác định | 22 | 15 |

**Chunk theo đoạn:**
- Gộp các đoạn trong cùng một mục, mỗi chunk tối đa 900 ký tự. Đoạn dài được cắt theo câu.
- Tài liệu không có số trang, nên **vị trí gốc lưu theo số dòng** (`chunks.provision = "dòng 62–65"`). Giao diện và trích dẫn hiển thị "SRC003 · dòng 62–65".
- Chú thích ảnh trong bài được giữ dạng `[Chú thích ảnh trong bài: …]`.
- Chỉ đề mục thật mới được dùng làm `section`. Tiêu đề bài không được lặp vào mọi chunk, vì trong phép thử đầu, việc lặp này làm lệch xếp hạng.
- Đã kiểm tra tự động: **mọi dòng không rỗng** của 3 tệp đều có trong chunk (test `test_doc_chunks_cover_every_line_with_position`).

**Lưu ý loại nguồn:**
- Cả 3 tệp là bài viết thứ cấp (`SECONDARY_ARTICLE`, `verification_status = secondary_unverified`).
- SRC004 thuật lại hồi ức của bà Nguyễn Thị Hương, ông Nguyễn Văn Quảng và ông Hoàng Nghi.
- System prompt được bổ sung yêu cầu ghi nguồn khi dùng: "theo bài viết của…", "theo lời kể của…".

## 4. Xung đột giữa các nguồn – không gộp, không chọn

Có 9 bản ghi `CURATOR_NOTE` (NOTE-01…NOTE-09). Mỗi bản ghi:
- Chỉ trích lại nội dung đã có trong nguồn, kèm trang in sách hoặc số dòng bài viết. Các vị trí này đã được đối chiếu với OCR và văn bản gốc.
- Có quan hệ `compares_source` tới các chunk ở cả hai phía.

| Ghi chú | Nội dung khác nhau |
|---|---|
| NOTE-01 | Cầu bị đánh sập: sách tr.183 ghi **9-1966**; SRC003 (dòng 30, 83) ghi **2/8/1967**; SRC004 và SRC005 ghi năm 1967 |
| NOTE-02 | Năm nâng cấp cầu: sách ghi **1945**, SRC003 ghi **1943**. Tải trọng cầu 1952: sách ghi **10 tấn**, SRC003 ghi **18 tấn**. Biển trong ảnh IMG038 ghi 183,8 m |
| NOTE-03 | Cột cờ đầu tiên: sách ghi 8-10-1954, cờ 24 m²; SRC003 ghi cờ 3,2×4,8 m; lời kể ông Hoàng Nghi nói dựng dịp 2/9/1954 |
| NOTE-04 | Cột cờ phía Nam 1956: sách ghi **thép 25 m**; SRC004 ghi **xi măng cốt thép 30 m** |
| NOTE-05 | Trụ cờ phía Bắc 1957: sách ghi **32 m**; SRC004 ghi **34,5 m**. Phía Nam lên 35 m: sách ghi năm 1961, SRC004 ghi năm 1957 |
| NOTE-06 | Đội sơn cầu: sách ghi Đội 337, 10 người, từ 9-11-1958, xong 16-1-1959; lời kể bà Hương ghi từ 1956, đội 20 người, đến 1960 thì giữ hai màu xanh – vàng |
| NOTE-07 | Cầu sau 1967: sách ghi xây năm 1974 và không nêu năm phục chế; SRC003 ghi phục chế **2001**; SRC005 ghi **2008**; SRC004 ghi dựng lại năm 1974 |
| NOTE-08 | Hệ thống loa: đường kính loa 500 W là 1,72 m (sách) và 1,7 m (bài viết). Các số liệu 5 cụm × 24 loa 25 W, đường dây 6 KvA, trạm tăng âm cách cầu 2,5 km chỉ có trong bài viết. Chương sách về phát thanh có phạm vi 1956–1962 |
| NOTE-09 | Nơi lưu giữ loa 500 W: trước Bảo tàng Vĩnh Linh (SRC003); Nhà trưng bày "Vĩ tuyến 17…" (SRC005); gian VOV tại Trung tâm Triển lãm Quốc gia (tên file IMG046) |

**Cách truy xuất xử lý ghi chú đối chiếu:**
- Các ghi chú dày từ khóa nên dễ chiếm hạng đầu. Vì vậy truy xuất **không cho ghi chú chiếm suất top-k**.
- Nếu có ghi chú trong nhóm 2k kết quả đầu, đúng 1 ghi chú được gắn vào cuối ngữ cảnh. Nhờ vậy LLM thấy chỗ các nguồn khác nhau mà nguồn gốc không bị đẩy ra ngoài.
- Prompt yêu cầu nêu phiên bản của từng nguồn kèm trích dẫn riêng và không chọn bên nào.

## 5. Thay đổi trong pipeline RAG (không phá API cũ)

**Mô hình dữ liệu:**
- `Image` có thêm 3 cột tùy chọn: `source_id`, `filename_title`, `metadata_basis`.
- Các API cũ trả thêm trường. Không trường cũ nào bị đổi hoặc bỏ.

**Truy xuất:**
- Glossary thêm "Giơnevơ"/"geneve" (cách viết của SRC003), nhóm `relic` (di tích, phục dựng, phục chế, phục hồi…) và nhóm `announcer` (phát thanh viên, O Nhạn).
- Thử thêm "màu sơn" vào nhóm `paint` làm MRR của bộ câu hỏi cũ giảm còn 0,543, nên **đã hoàn tác**.
- Thêm điểm thưởng **cụm tên riêng viết hoa khớp nguyên văn có dấu**. Khi bỏ dấu, "O Nhạn" trùng với "ở nhân" và "Ngô Thị Diệm" bị lẫn. Đã thử trọng số 0,006 / 0,015 / 0,03 / 0,05. Từ 0,03 trở lên chỉ số không tăng thêm, nên chốt **0,03**.
- Mở rộng chunk lân cận áp dụng cho cả bài viết (cùng nguồn).

**Truy xuất ảnh (theo metadata, không có image embedding):**
- Thêm điểm thưởng cho cụm hai từ liền kề, để phân biệt "bờ Nam" với "bờ Bắc" trong tên file.

**Context và prompt:**
- Context ghi rõ "chú thích trong bài SRC003" và "tiêu đề/thời gian/địa điểm dựa trên TÊN FILE (chưa xác minh)".
- Prompt thêm quy tắc ghi nguồn cho `SECONDARY_ARTICLE`, lời kể nhân chứng và `CURATOR_NOTE`.

**Lỗi đã sửa:**
- `/api/timeline` từng gom mọi quan hệ trỏ tới sự kiện, nên ghi chú NOTE-03 bị hiển thị như một ảnh. Nay chỉ lấy quan hệ có `from_type = image`.
- `/api/documents` nay đếm ảnh theo `source_id`.

**API và giao diện:**
- `/api/images/{id}` trả thêm `related_passages[].source_id/provision/relation`. Đoạn có chú thích ảnh được xếp đầu.
- Giao diện:
  - Nhãn nguồn mới: "Bài viết (thứ cấp)", "Ghi chú đối chiếu nguồn".
  - Trang chi tiết ảnh có mục "Tiêu đề theo tên file" kèm cảnh báo chưa xác minh.
  - Đoạn tư liệu liên quan hiển thị "SRC003 · dòng …".
  - Thư viện ảnh có bộ lọc "Ảnh di tích/hiện vật ngày nay"; phần giới thiệu cập nhật số ảnh.

## 6. Kiểm thử

Tất cả số liệu dưới đây là kết quả chạy thật trong phiên này (2026-10-31). **LLM và TTS thật chưa được gọi** vì môi trường không có API key. Các test chat dùng LLM giả lập (httpx.MockTransport). Chế độ dự phòng khi không có LLM đã được kiểm tra trên server thật.

**6.1 Test tự động**
- `pytest`: **104 passed**.
- `vitest`: **24 passed**. `tsc --noEmit` sạch. `npm run build` thành công.

`tests/test_supplement.py` kiểm tra các yêu cầu sau:
- **Metadata nguồn:** không bịa URL hay nhà xuất bản.
- **Tài liệu:** mọi dòng đều có trong chunk và có vị trí dòng.
- **Ảnh:**
  - 16 ảnh giữ tên file gốc, có căn cứ cho từng trường, không gán niên đại hay danh tính.
  - 9 chú thích trùng tên file và được gắn vào đoạn chứa chú thích.
  - Trùng lặp được ghi nhận, không xóa.
- **Ghi chú đối chiếu:** 9 ghi chú, mỗi ghi chú nối tới ≥ 2 nguồn.
- **Truy xuất:**
  - Tìm đúng đoạn bài viết mới cho các câu: "O Nhạn", "trạm tăng âm", "bà Nguyễn Thị Hương", "Minh Lương".
  - Ghi chú đối chiếu được gắn cuối, không chiếm suất.
  - Tìm ảnh theo nội dung tên file.
- **API:** ảnh `.webp` và tên file có dấu và khoảng trắng phục vụ được; trang chi tiết ảnh có chú thích bài viết.
- **Chat (LLM giả lập):**
  - Trả nguồn SRC003 kèm "dòng …" và ảnh IMG043.
  - Ngữ cảnh gộp được sách, bài viết và ảnh.
  - Câu hỏi về điểm xung đột đưa NOTE-01 vào ngữ cảnh.

**6.2 Truy xuất trên 60 câu gold cũ**

So sánh trên cùng code cuối; chỉ khác dữ liệu (DB cũ so với DB mới):

| | Recall@5 | P@5 | Hit@5 | Recall@10 | Hit@10 | MRR |
|---|---|---|---|---|---|---|
| Trước bổ sung (chỉ sách) | 0,777 | 0,298 | 0,816 | 0,866 | 0,898 | 0,678 |
| Sau bổ sung – nhãn cũ (chỉ trang sách) | **0,787** | 0,278 | **0,837** | 0,838 | 0,878 | 0,636 |
| Sau bổ sung – có tính nguồn mới\* | 0,787 | 0,302 | 0,857 | 0,838 | 0,878 | 0,661 |

\* Chunk bài viết được tính là liên quan nếu chứa **đủ mọi** từ khóa `must_include` của câu (`--source-aware`).

Cách đọc kết quả:
- Thêm 53 đoạn bài viết làm Recall@5 và Hit@5 tăng nhẹ.
- Nhưng **Recall@10 giảm 0,028, Hit@10 giảm 0,020 và MRR giảm 0,017–0,042**: các đoạn bài viết cạnh tranh với trang sách.
- Một phần mức giảm là do gold chỉ đánh nhãn trang sách. Ví dụ, ở RAG-020 và RAG-021, SRC003 dòng 77 và 83 chứa đúng giờ kéo cờ và con số 267 lá cờ.
- Phần còn lại là chi phí thật.

Các chỉ số khác:
- Độ chính xác từ chối không đổi (0,545).
- Tỉ lệ câu trả lời được đi qua cổng bằng chứng không đổi (0,98).
- Context recall (`eval_context_recall.py`): 0,850 trong báo cáo trước, nay **0,830**.
- Riêng điểm thưởng tên riêng, nếu đo trên DB chỉ có sách, đã nâng Recall@5 từ 0,736 lên 0,777.

**6.3 Truy xuất trên 16 câu gold mới** (`tests/evaluation/rag_test_dataset_supplement.json`)
- Chunk kỳ vọng được tra từ số dòng thật bằng `scripts/make_supplement_gold.py`, không gõ tay ID.
- Kết quả: Recall@5 **0,787**, Hit@5 **0,938**, Recall@10 0,850, Hit@10 0,938, MRR 0,674. 16/16 câu đi qua cổng bằng chứng.
- Câu trượt: **SUP-13** ("đường dây điện cấp cho hệ thống loa dài bao nhiêu"). Đoạn chứa thông tin "6KvA" (SRC005 dòng 18, mảnh 2) không lọt top 10.

**6.4 Truy xuất ảnh** (`scripts/run_image_eval.py`)
- ImageIndex với 16 truy vấn lấy từ nội dung tên file: Hit@1 **0,875**, Hit@3 **1,0**, MRR@5 0,927.
- Hai câu không đứng hạng 1:
  - "Cụm loa phát thanh bên bờ Nam": IMG042 đứng hạng 2. Sau khi bỏ dấu, "Nam" trùng với "năm".
  - "loudspeakers on the southern bank": IMG042 đứng hạng 3.
- Ảnh mà pipeline chat thực sự chọn cho 5 câu có ảnh kỳ vọng: **5/5 đúng**.

**6.5 Kiểm tra thủ công trên server thật** (ảnh chụp ở `docs/screenshots/supplement/`)
- `image_detail_IMG043.png`, `image_detail_IMG037.png`, `image_detail_IMG046.png`: tiêu đề theo tên file, cảnh báo chưa xác minh, chú thích bài viết, đoạn tư liệu theo dòng.
- `gallery_contemporary.png`: bộ lọc ảnh di tích/hiện vật ngày nay (6 ảnh).
- `chat_fallback_loudspeakers.png`: chat ở chế độ dự phòng (không có LLM). Nguồn gồm sách tr.114 và SRC003 dòng 54–56; ảnh gồm IMG042, IMG041, IMG047.

## 7. Hạn chế còn lại (trung thực)
- **Nguồn chưa xác minh:**
  - Cả 3 bài viết không có URL, tên báo hay ngày đăng trong tệp. Ngày đăng chỉ ước lượng từ câu "kỷ niệm 40/47 năm" và được ghi rõ như vậy.
  - Nguồn gốc và bản quyền của 16 ảnh chưa xác định.
- **Chưa đo với LLM/TTS thật:** chưa có số đo chất lượng câu trả lời và chưa kiểm tra việc LLM có thực sự nêu cả hai phía khi có xung đột. Cần chạy `scripts/run_llm_eval.py` khi có key.
- **Chuyển ngữ:** mô tả ảnh (`visual_description`) chỉ có tiếng Việt; tiêu đề ảnh có đủ vi/en/zh.
- **Lỗi có sẵn từ trước:** chunk sách SRC001-0261 và SRC001-0262 mở đầu giống hệt nhau (do bộ chia chunk sách), nên có thể hiện như hai nguồn trùng trong chat. Lỗi không do đợt bổ sung gây ra. Chưa sửa, vì sửa sẽ thay đổi chunk sách và toàn bộ đường cơ sở đánh giá.
- **Tên riêng ngắn:** tên riêng ngắn hoặc từ địa danh trùng từ thường sau khi bỏ dấu ("bờ Nam" và "năm") vẫn có thể bị xếp hạng thấp.

## 8. Chạy lại
```
python scripts/build_knowledge_base.py                       # dựng lại toàn bộ, gồm đợt bổ sung
python scripts/verify_extraction.py --write-doc
python scripts/make_supplement_gold.py
python scripts/run_retrieval_eval.py                         # 60 câu cũ
python scripts/run_retrieval_eval.py --source-aware --out docs/retrieval_eval_results_source_aware.json
python scripts/run_retrieval_eval.py --dataset tests/evaluation/rag_test_dataset_supplement.json --out docs/retrieval_eval_results_supplement.json
python scripts/run_image_eval.py
cd backend && python -m pytest -q ; cd ../frontend && npx vitest run
```

## 9. Cập nhật lần 2 – mục "Những mẩu chuyện thú vị", nguồn web, bỏ cụm "theo tên file"

### 9.1 Mục "Những mẩu chuyện thú vị"
- **10 mẩu chuyện**, mỗi chuyện có đủ 3 thứ tiếng vi/en/zh (bản en/zh do nhóm dịch). Dữ liệu ở `scripts/curation_anecdotes.py` → `knowledge_base/anecdotes.json`; API `GET /api/anecdotes`.
  1. Cây cầu hai màu sơn
  2. Cuộc chọi cờ: từ 12 m lên 38,6 m
  3. Cuộc chiến âm thanh
  4. Chiếc loa 500W giờ ở đâu?
  5. Mẹ Diệm và những lá cờ rách
  6. 122 m² vải đỏ cho một lá cờ
  7. Đêm cột cờ gãy
  8. Đổi bờ ngày chẵn, ngày lẻ
  9. Năm dòng chữ gửi người thân
  10. 450 và 444 tấm ván
- **Giao diện:**
  - Trang chủ có section 6 thẻ chuyện, đặt sau dòng thời gian.
  - Trang mới `/stories` (mục "Chuyện kể" trên thanh điều hướng) hiển thị đủ 10 chuyện, kèm ảnh, nguồn, khung "Các nguồn ghi khác nhau" và nút "Hỏi hướng dẫn viên".
  - Chatbot có thêm nhóm câu hỏi gợi ý "Mẩu chuyện thú vị".
- **Kiểm chứng:**
  - Mỗi trích dẫn sách hoặc bài viết có điểm neo, được build kiểm tra trong OCR trang in hoặc đúng dòng tệp gốc. Kết quả: **toàn bộ khớp, 0 cảnh báo**.
  - Trích dẫn báo web không kiểm tra tự động được, nên được đánh dấu `verified_anchor = null` và có link URL.
  - Chuyện nào các nguồn ghi khác nhau thì nói rõ trong văn kể và trỏ tới ghi chú đối chiếu. Ví dụ: chọi cờ → NOTE-03/04/05/11; loa 500W → NOTE-09.

### 9.2 Nguồn web mới (đọc ngày 31/10/2026)

| Nguồn | Bài | Dùng cho |
|---|---|---|
| WEB001 | Báo Nhân Dân, Sơn Bách – Thành Đạt, 27/4/2022 | Lời Đại tá Nguyễn Thanh Hà về chọi cờ; đêm 2–3/8/1967 |
| WEB002 | Báo Thanh tra, Minh Tân, 20/6/2025 | Đài Truyền thanh Vĩnh Linh; loa 500W ở Bảo tàng Báo chí Việt Nam |
| WEB003 | Báo Văn Hóa, Sơn Thùy – Hồng Nguyên, 4/5/2025 | Ông Nguyễn Đức Lãng, người may cờ |
| WEB004 | VnExpress (chỉ đọc được đoạn trích) | Phục chế năm 2001, sơn lại hai màu năm 2014 |

- Mỗi bài có 1 bản ghi tri thức WX001–WX005. Đây là **diễn giải ngắn của nhóm**, không chép nguyên văn.
- Thêm 2 ghi chú đối chiếu (tổng cộng 11):
  - **NOTE-10:** cột cờ bờ Nam bị đánh sập đêm 2/8 (sách, SRC003) hay đêm 3/8/1967 (WEB001).
  - **NOTE-11:** lá cờ năm 1962 rộng 134 m² (sách, SRC003) hay khoảng 96 m² (lời ông Lãng).
- NOTE-03/04/05/07/09 được bổ sung đối chiếu với nguồn web. Ví dụ, WEB001 khớp với sách về trụ cờ 32 m năm 1957.

### 9.3 Bỏ cụm "theo tên file"
- Tiêu đề 16 ảnh được viết lại gọn theo mô tả đi kèm, ví dụ "O Nhạn – phát thanh viên chính của Đài Truyền thanh Vĩnh Linh thời đấu loa", "Cụm loa phát thanh bên bờ Nam".
- Thời gian, địa điểm và nhân vật ghi "theo chú thích trong bài SRC003" (với 9 ảnh có chú thích) hoặc "(chưa xác minh)".
- Trên trang chi tiết ảnh, mục "Tiêu đề theo tên file" đổi thành "Mô tả ban đầu đi kèm ảnh – Chưa xác minh".
- Căn cứ vẫn được lưu nội bộ (`metadata_basis.title = filename`).
- Context gửi LLM ghi "theo mô tả đi kèm ảnh (CHƯA xác minh…, không nhận dạng người)", để chatbot không khẳng định danh tính hay niên đại.
- Có test bảo đảm cụm này không còn xuất hiện trong mọi trường hiển thị của 16 ảnh.
- **Đánh đổi cần biết:** tiêu đề như "Mẹ Diệm vá cờ Tổ quốc" hay "O Nhạn – …" nay trình bày như chú thích ảnh. Người xem chỉ thấy "chưa xác minh" khi mở trang chi tiết.

### 9.4 Số đo sau cập nhật lần 2
- **Kho:** 19 nguồn, 683 chunk (thêm 5 WX và 2 NOTE), 65 ảnh, 31 sự kiện, 1.586 quan hệ, 10 mẩu chuyện.
- **Test:** pytest **107 passed** (+3: nguồn web, `/api/anecdotes` và mọi trích dẫn khớp neo, không còn "theo tên file"). vitest **25 passed** (+1: trang Chuyện kể). `tsc` sạch, build thành công.
- **Kiểm tra trên trình duyệt (Playwright):** không có lỗi console; bản mobile 390 px không tràn ngang. Ảnh chụp: `docs/screenshots/supplement/home_anecdotes.png`, `stories_page.png`, `stories_loa500w.png`, `stories_mobile.png`, `image_detail_IMG043.png`.
- **Truy xuất 60 câu cũ:** Recall@5 0,787, Hit@5 0,837, Hit@10 0,878 (không đổi so với lần 1).
  - MRR theo nhãn chỉ trang sách giảm từ 0,636 xuống **0,609**, vì 5 bản ghi web thường đứng hạng đầu.
  - Ở chế độ có tính nguồn mới (bài viết và báo web chứa đủ từ khóa bắt buộc): P@5 0,306, Hit@5 0,857, MRR 0,634.
  - So với DB chỉ có sách (MRR 0,678), mức giảm vẫn còn.
- **Truy xuất 16 câu nguồn mới:** Recall@5 0,819, Hit@5 0,938, MRR 0,674.
- **Truy xuất ảnh theo mô tả:** Hit@1 tăng từ 0,875 lên **1,0** (tiêu đề gọn hơn nên khớp tốt hơn). Pipeline chọn đúng ảnh 5/5.
- **Chưa kiểm chứng:** việc LLM thật kể lại các mẩu chuyện đúng nguồn chưa được kiểm chứng, vì chưa có API key.

