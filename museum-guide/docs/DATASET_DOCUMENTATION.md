# DATASET_DOCUMENTATION – Báo cáo đối chiếu dữ liệu

_Sinh tự động bởi `python scripts/verify_extraction.py --write-doc` từ dữ liệu thực tế (trạng thái kiểm tra: **OK**)._

## 1. Sách: *Đôi bờ giới tuyến (1954–1967)* – TS. Hoàng Chí Hiếu
| Chỉ tiêu | Giá trị |
|---|---|
| Tổng số file PDF | 1 (`DoiBoGioiTuyen19541967_HoangChiHieu.pdf`, 26.6 MB) |
| Tổng số trang PDF (thực tế) | **130** |
| Số trang PDF đã xử lý (OCR + lưu ảnh scan) | **130** (thiếu: không; lỗi: không) |
| Số trang có lớp text trực tiếp | **0** (chỉ là watermark `tieulun.hopto.org`, không phải nội dung) |
| Số trang cần OCR | **130** / 130 (toàn bộ là ảnh scan) |
| Trang sách in tương ứng | 260 (mỗi trang PDF là một *spread* 2 trang sách; số trang in: trái = 2p−1, phải = 2p) |
| Số ảnh nhúng PDF phát hiện bằng `get_images()` | 130 (mỗi trang đúng 1 ảnh = bản scan nguyên spread) |
| Ảnh scan trang đã lưu (lossless PNG) | 130 (không đọc được: không) |
| OCR: độ tin cậy trung bình / thấp nhất | 93.49 / 44.93 (Tesseract 5, ngôn ngữ `vie`, upscale ×3) |
| Nửa trang có confidence < 80 | 3 |
| Nửa trang trống hoặc chỉ có hình (<15 từ) | 10: [(1, 'left'), (1, 'right'), (2, 'right'), (4, 'right'), (6, 'right'), (7, 'right'), (27, 'left'), (28, 'right'), (29, 'right'), (128, 'right')] |
| Nửa trang cần xác minh thủ công | 12: (trang PDF, bên, conf, số từ) [(1, 'left', 57.86, 7), (1, 'right', None, 0), (2, 'right', None, 0), (4, 'right', None, 0), (6, 'right', 96.0, 1), (7, 'right', 96.0, 1), (27, 'left', None, 0), (28, 'right', None, 0), (29, 'right', None, 0), (56, 'right', 75.49, 236), (77, 'left', 44.93, 227), (128, 'right', None, 0)] |

**Văn bản trực tiếp và OCR được lưu riêng:** `data/processed/ocr/page_NNN.json` có trường `direct_text` (text layer) tách biệt với `halves.*.text` (OCR) và `words[].conf` (confidence từng từ).

**Số trang in:** quy tắc suy ra từ vị trí spread được đối chiếu với số OCR đọc được ở chân trang: khớp **226** trang, lệch **10** trang (đều là lỗi chữ số của OCR, ví dụ 49↔19; xem `docs/extraction_report.json`), không đọc được số ở **24** trang (trang trống/trang hình). Quy tắc được dùng cho citation; không nhầm số trang PDF với trang in (API trả cả hai).

**Giới hạn OCR cần biết:** bản scan có độ phân giải thấp (1101×771 px/spread) nên OCR có thể sai dấu/ký tự (ví dụ "Hiển Lương" thay cho "Hiền Lương", "đổi" thay cho "đôi"). Văn bản sách được **giữ nguyên** (không tự sửa theo kiến thức ngoài); tìm kiếm dùng chuỗi đã bỏ dấu để chịu lỗi dấu. Chú thích-trích dẫn thuần (số chú thích + ký hiệu lưu trữ) bị loại khỏi chunk (đếm trong `data/processed/build_report.json`), chú thích mang nội dung được giữ lại.

## 2. Hình ảnh trong sách
- Hình ảnh ứng viên phát hiện bằng phân tích layout: **15**; đã lưu: **15** (`data/images/book/FIG_*.png`, ảnh crop từ bản scan gốc; **không thay thế** bản gốc `data/processed/pages/`).
- Sau kiểm tra bằng mắt: **12 hình lịch sử/bản đồ/bưu thiếp** (`BKFIG01–BKFIG12`, hiển thị ở Gallery) và **3 mục là thiết kế bìa/logo** (đánh dấu `cover_design`, KHÔNG hiển thị ở Gallery).
- PDF là scan: get_images() chỉ thấy 130 ảnh nguyên trang; hình trong trang được tách bằng phân tích layout (scripts/detect_figures.py) và đã kiểm tra bằng mắt trên contact sheet.
- Mỗi hình có: trang PDF, trang in, bbox trên trang, kích thước, định dạng, ID, chú thích (đọc trực tiếp từ crop; chú thích bị cắt được đánh dấu `verified_visual_partial`) và liên kết tới các đoạn văn của trang đó.
- Bảng biểu: sách không có bảng dữ liệu thuần; các biểu mẫu (bưu thiếp) nằm trong hình. **Chưa có** trích xuất bảng riêng (không có bảng để trích).

## 3. Bộ ảnh `Archive_2.zip`
| Chỉ tiêu | Giá trị |
|---|---|
| Số mục trong ZIP | 68 (bỏ qua 34 file metadata `__MACOSX`) |
| Ảnh thực tế trong ZIP / đã giải nén | **34** / **34** |
| Ảnh có mô tả (đã quan sát từng ảnh) | **44** / 34 |
| Ảnh giống hệt theo SHA-256 | 0 nhóm (tất cả 34 file có hash khác nhau) |
| Ảnh là bản khác của cùng một bức (pHash/SIFT), KHÔNG xoá | **7 nhóm × 2 ảnh = 14 ảnh** → 27 bức ảnh duy nhất về nội dung |
| Ảnh trùng với hình in trong sách (SIFT ≥ 90 inliers) | 4 ảnh (IMG004, IMG007, IMG032, IMG034) |
| Ảnh đã liên kết tới nội dung sách (cạnh `image→chunk`) | **42** / 34 (trực tiếp: 4; còn lại là liên kết theo chủ đề, có ghi `link_type`) |
| Ảnh chưa xác định nguồn | **44** / 34 (watermark LIFE/TikTok/corbis chỉ được ghi nhận, không suy ra tác giả/quyền) |
| Ảnh độ tin cậy `low` cần xác minh thủ công | 17: ['IMG005', 'IMG009', 'IMG010', 'IMG011', 'IMG012', 'IMG013', 'IMG021', 'IMG022', 'IMG023', 'IMG025', 'IMG027', 'IMG028', 'IMG030', 'IMG033', 'IMG035', 'IMG043', 'IMG050'] |
| Ảnh không đọc được | không |
| Metadata bị thiếu | không |

Nhóm bản trùng (cùng một bức ảnh, khác mã hoá/khung): `{'DUP-A': 'IMG005,IMG028', 'DUP-B': 'IMG007,IMG032', 'DUP-C': 'IMG008,IMG031', 'DUP-D': 'IMG009,IMG027', 'DUP-E': 'IMG010,IMG033', 'DUP-F': 'IMG014,IMG026', 'DUP-G': 'IMG004,IMG034', 'DUP-S024': 'IMG024,IMG036'}`. Nhóm cảnh gần nhau (cùng địa điểm, khác khung hình): `SCENE-FLAGS`.
**Năm chụp của cả 34 ảnh: "Chưa xác định".** Không có ảnh nào được gán danh tính nhân vật.

## 4. Cơ sở dữ liệu
Trang sách: 260 · Chunk theo nguồn: {'DOC001': 4, 'DOC002': 3, 'DOC006': 1, 'NOTE01': 11, 'REF001': 1, 'REF002': 1, 'SRC001': 604, 'SRC003': 24, 'SRC004': 14, 'SRC005': 15, 'WEB001': 2, 'WEB002': 1, 'WEB003': 1, 'WEB004': 1} · Tổng ảnh: 65 · Sự kiện: 31 (anchor không khớp OCR: 0).

## 5. Nguồn bổ sung (Genève)
Xem `knowledge_base/sources.json` và mục "Nguồn tư liệu ngoài" trong `PROJECT_STATUS.md`. **Trung thực về phạm vi:** môi trường phát triển không truy cập được toàn văn 5 URL bắt buộc (máy chủ không nằm trong allowlist); thông tin về điều khoản được xác minh qua trích đoạn từ kết quả tìm kiếm (Wikisource, FRUS, Fordham, CIA Reading Room, Britannica…) và được ghi `partially_verified_via_search_snippets`; DOC005 (UN Peacemaker) chỉ đăng ký metadata (`not_accessed`). Dữ liệu ngoài lưu riêng (`chunks.source_type != BOOK`), không ghi đè nội dung sách. Chưa thu thập nghiên cứu học thuật về di cư 1954–1955.

## 5b. Đợt bổ sung nguồn 2026-10-31
Chi tiết và kết quả kiểm thử: `docs/SUPPLEMENT_INTEGRATION_REPORT.md`. Tài liệu không có số trang → trích dẫn theo **số dòng** của tệp gốc (`chunks.provision`).

| Nguồn | Loại | Tiêu đề | Tác giả | Số chunk |
|---|---|---|---|---|
| NOTE01 | CURATOR_NOTE | Ghi chú đối chiếu nguồn (nhóm phát triển biên soạn) | Nhóm phát triển dự án | 11 |
| SRC003 | SECONDARY_ARTICLE | Về lịch sử cầu Hiền Lương (bài viết nhân dịp kỷ niệm 40 năm giải phóng miền Nam) | Minh Vượng | 24 |
| SRC004 | SECONDARY_ARTICLE | Những màn chọi cờ, đấu loa mang khát vọng hòa bình ở vĩ tuyến 17 (phóng sự có lời kể nhân chứng) | Chưa xác định (ảnh ghi 'Nhật Anh') | 14 |
| SRC005 | SECONDARY_ARTICLE | Hệ thống loa phóng thanh bên bờ Bắc cầu Hiền Lương (bài viết nhân kỷ niệm 47 năm giải phóng miền Nam, 30/4/2022) | Chưa xác định | 15 |
| SRC006 | ARCHIVAL_PHOTO | Archive_4.zip – ảnh bổ sung (16 ảnh duy nhất; kèm 'Archive 3.zip' lồng bên trong chứa 10 bản trùng byte) | Chưa xác định | — |

Ảnh Archive_4.zip: **16** ảnh duy nhất (tên file gốc giữ nguyên; tiêu đề lấy từ tên file được đánh dấu `metadata_basis.title = filename`).

| Ảnh | Loại | Tên file gốc | Chú thích trong bài | Quan hệ với ảnh khác | Thời gian (có căn cứ) |
|---|---|---|---|---|---|
| IMG035 | archive_photo | `1954_Geneva_Conference.jpg` | — | — | 1954 (chưa xác minh) |
| IMG036 | archive_photo | `Cầu Hiền Lương (1956-1964) phía bờ Bắc với những khẩu hiệu thể hiện khát vọng thống nhất Tổ quốc.  .jpg` | chú thích SRC003:dòng 28 (trùng tên file) | variant_of_same_photograph IMG024 | Theo chú thích trong bài SRC003: 1956-1964 (chưa xác minh) |
| IMG037 | archive_photo | `Cầu Hiền Lương bị bom Mỹ đánh sập năm 1967.  .jpg` | chú thích SRC003:dòng 34 (trùng tên file) | — | Theo chú thích trong bài SRC003: 1967 (chưa xác minh; sách SRC001 tr.183 ghi cầu bị đánh sập 9-1966) |
| IMG038 | archive_photo | `Cầu Hiền Lương do người Pháp xây dựng năm 1952.  .jpg` | chú thích SRC003:dòng 14 (trùng tên file) | — | Chưa xác định (năm 1952 trên biển là năm xây cầu, KHÔNG phải năm chụp ảnh) |
| IMG039 | archive_photo | `Cầu Hiền Lương nhìn từ phía Nam, năm 1964..jpg` | chú thích SRC003:dòng 73 (trùng tên file) | same_scene_different_frame IMG004; same_scene_different_frame IMG034 | Theo chú thích trong bài SRC003: 1964 (chưa xác minh) |
| IMG040 | contemporary_photo | `Cột cờ tại cầu Hiền Lương ngày nay.  .jpg` | chú thích SRC003:dòng 81 (trùng tên file) | — | Thời nay (ảnh màu) – năm chụp chưa xác định |
| IMG041 | archive_photo | `Cụm loa phát thanh bên bờ Bắc.  .jpg` | chú thích SRC003:dòng 48 (trùng tên file) | — | Chưa xác định |
| IMG042 | archive_photo | `Cụm loa phát thanh bên bờ Nam.  .jpg` | chú thích SRC003:dòng 54 (trùng tên file) | likely_same_photograph IMG030 | Chưa xác định |
| IMG043 | archive_photo | `O Nhạn- phát thanh viên chính của Đài Truyền thanh Vĩnh Linh trong thời kỳ đấu loa ở cầu Hiền Lương..jpg` | chú thích SRC003:dòng 62-63 (trùng tên file) | — | Thời kỳ đấu loa (chưa xác minh) |
| IMG044 | archive_photo | `Toàn cảnh Cầu Hiền Lương (ảnh chụp ngày 2-9-1959)  .jpg` | chú thích SRC003:dòng 22 (trùng tên file) | — | Theo chú thích trong bài SRC003: 2-9-1959 (chưa xác minh) |
| IMG045 | contemporary_photo | `cau-hien-luong-hai-mau-1754296891.jpg` | — | — | Thời nay (ảnh màu chụp trên cao); năm chụp chưa xác định |
| IMG046 | contemporary_photo | `chiec_loa_o_gioi_tuyen_hien_luong-_ben_hai_duoc_trung_bay_o_gian_trung_bay_dai_tieng_noi_viet_nam_tai_trung_tam_trien_lam_quoc_gia.webp` | — | — | Thời nay (ảnh màu chụp hiện vật trưng bày); năm chụp chưa xác định |
| IMG047 | contemporary_photo | `cum_loa_phong_thanh_cua_dai_truyen_thanh_vinh_linh_o_bo_bac_song_ben_hai.webp` | — | similar_installation IMG049 | Thời nay (ảnh màu); năm chụp chưa xác định – ảnh không cho biết giàn loa là nguyên bản hay phục dựng |
| IMG048 | contemporary_photo | `cum_loa_phong_thanh_duoc_phuc_dung_phia_bo_nam_trong_khuon_vien_di_tich_lich_su_quoc_gia_dac_biet_doi_bo_hien_luong-_ben_hai.webp` | — | — | Thời nay (hiện vật phục dựng – chưa xác minh); năm chụp chưa xác định |
| IMG049 | contemporary_photo | `cum_loa_phong_thanh_o_bo_bac_song_ben_hai.webp` | — | — | Thời nay (ảnh màu); năm chụp chưa xác định |
| IMG050 | archive_photo | `mẹ diệm vá cờ tổ quốc.webp` | — | — | Chưa xác định |

## 6. Cách chạy lại
```
python scripts/ingest_pdf.py          # OCR + ảnh scan trang
python scripts/detect_figures.py      # tách hình trong sách
python scripts/match_images.py        # so khớp ảnh
python scripts/build_knowledge_base.py   # gồm cả đợt bổ sung (scripts/supplement_ingest.py)
python scripts/verify_extraction.py --write-doc
```
