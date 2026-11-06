# Vĩ tuyến 17 — Giao diện và kho tư liệu

Ứng dụng React hiển thị bản đồ di tích, thuyết minh và tra cứu tư liệu. Backend Python lưu tài liệu cùng vector tìm kiếm trong SQLite. Bản hiện tại chạy cục bộ, không cần tài khoản dịch vụ hay khóa API.

```text
trolyaobaotang/
├── frontend/          # React, Vite và ảnh đang dùng
├── backend/           # API Python, dữ liệu mẫu, SQLite và kiểm tra
└── assets/reference/  # Ảnh thiết kế gốc để tham khảo
```

## Chạy ứng dụng

Cần Python 3.10+ và Node.js 18+.

Từ thư mục chứa tệp README này, chạy một lệnh trong một terminal:

```bash
./run.sh
```

Script tự tạo `backend/.venv`, cài thư viện frontend nếu cần, tạo dữ liệu mẫu khi chưa có SQLite, rồi chạy cả backend và frontend. Nhấn `Ctrl+C` để dừng cả hai. Nếu muốn chạy riêng từng phần:

```bash
backend/.venv/bin/python backend/server.py
cd frontend
npm run dev
```

Mở **http://localhost:5173**. Vite chuyển tiếp đường dẫn `/api` đến backend tại `127.0.0.1:8000`. Lệnh `seed` có thể chạy lại; tài liệu trùng `id` sẽ được cập nhật.

## Thêm tư liệu

Mỗi tài liệu JSON cần `id`, `title`, `content`. Gán `zone_id` bằng `bridge`, `museum`, `flag`, `monument` hoặc `union`; dùng `null` cho tư liệu tổng quan (chỉ tìm được khi không lọc địa điểm). Có thể thêm `source` và `category` để ghi nguồn và phân loại. Ví dụ lưu nội dung sau vào `tai-lieu.json`:

```json
{
  "id": "cau-hien-luong-nguon-1",
  "zone_id": "bridge",
  "title": "Cầu Hiền Lương",
  "content": "Nội dung tư liệu đã được kiểm chứng...",
  "source": "Tên tài liệu hoặc đường dẫn nguồn",
  "category": "Di tích"
}
```

Nhập một tài liệu hoặc một mảng tài liệu bằng lệnh:

```bash
python3 backend/manage.py import tai-lieu.json
python3 backend/manage.py list
```

Có thể thêm trực tiếp qua API:

```bash
curl -X POST http://127.0.0.1:8000/api/documents \
  -H 'Content-Type: application/json' \
  -d '{"id":"vi-du","zone_id":"bridge","title":"Tư liệu mới","content":"Nội dung cần tra cứu","source":"Nguồn tư liệu"}'
```

API còn có `GET /api/health`, `GET /api/documents`, `GET /api/search?q=...` và `POST /api/chat` với body `{"question":"..."}`.

Khi đang khám phá một điểm đến, giao diện gửi thêm `zone_id` (`bridge`, `museum`, `flag`, `monument` hoặc `union`) để câu trả lời chỉ lấy tư liệu của địa điểm đó. API tìm kiếm cũng nhận `zone_id` tùy chọn.

## Dữ liệu thuyết minh theo địa điểm

`GET /api/narration?zone_id=bridge` trả toàn bộ tư liệu thuộc địa điểm. Giao diện dùng `content` để đọc và hiển thị nguồn; chat tìm trên các đoạn được tách từ chính nội dung này. Tài liệu có `id` trùng địa điểm (ví dụ `bridge`) là bài giới thiệu ưu tiên; nếu chưa có, dùng tài liệu đầu tiên theo tiêu đề và ID. Các tài liệu còn lại đều có thể chọn để nghe. Khi backend không có dữ liệu hoặc mất kết nối, giao diện thông báo thay vì đọc nội dung tĩnh khác nguồn.

Sau khi khôi phục backend hoặc bổ sung tư liệu, nhấn **Tải lại tư liệu** trong mục Câu chuyện để tải lại ngay tại địa điểm đang xem.

Khi mở SQLite cũ lần đầu, hệ thống thêm cột `zone_id` và gán các ID `bridge`, `bridge-*` (tương tự ba địa điểm còn lại) về địa điểm tương ứng, giữ nguyên nội dung. Tài liệu cũ có ID khác giữ `zone_id = null`; nhập lại với `zone_id` rõ ràng để đưa vào địa điểm. Tài liệu mới có ID tùy ý phải khai báo trường này. API và CLI dùng cùng quy trình kiểm tra, tách đoạn, tạo vector và lưu trong một giao dịch.

Không có các nút phát lại, tạm dừng hoặc dừng. Chọn lại địa điểm hiện tại, đổi thiết lập giọng đọc hoặc mở chủ đề khác không ngắt bài đang phát. Chuyển địa điểm, về bản đồ hoặc Back/Forward sẽ hủy yêu cầu chat/thuyết minh cũ và xóa trạng thái của địa điểm trước.

## Cách tìm kiếm hoạt động

`backend/vector_store.py` chia tài liệu dài thành đoạn, tạo vector từ từ tiếng Việt và cụm ký tự, rồi lưu vector cùng đoạn văn trong `backend/data/knowledge.sqlite3`. Khi tìm kiếm, backend tính độ tương đồng cosine và trả về đoạn phù hợp cùng nguồn. Phương pháp này chạy hoàn toàn ngoại tuyến và phù hợp bản demo; nó ưu tiên sự trùng khớp từ ngữ, chưa hiểu ngữ nghĩa sâu như mô hình embedding chuyên dụng. Câu trả lời là trích nội dung tìm được, chưa có mô hình ngôn ngữ sinh câu trả lời.

Dữ liệu mẫu ở `backend/data/seed.json` được tạo từ nội dung giao diện trước đó và **chưa được kiểm duyệt lịch sử**. Hãy thay bằng tư liệu có nguồn đáng tin cậy trước khi sử dụng công khai. Tệp SQLite được bỏ qua trong Git; chạy `seed` để tạo lại ở máy khác.

## Kiểm tra

```bash
python3 -m unittest discover -s backend/tests -v
cd frontend
npm run build
```

## Giao diện hiện có

- Màn hình chính giữ giao diện ảnh nền cũ, bổ sung Nhà trưng bày bên trái Tượng đài; giữ hướng dẫn viên, thanh công cụ và năm điểm tham quan, gồm cả Nhà liên hiệp.
- Mỗi điểm đến mở một giao diện riêng với ảnh 3D dựng từ ảnh tham khảo do bạn cung cấp.
- Thuyết minh tự phát khi vào điểm đến; bài đang phát tiếp tục đến hết hoặc dừng khi chuyển địa điểm. Chọn chủ đề khác để đọc nội dung; chỉ bắt đầu đọc chủ đề được chọn khi không có bài đang phát.
- Ô chat tra cứu backend theo địa điểm và hiển thị nguồn tư liệu.
- Thư viện ảnh gồm cảnh 3D, ảnh tham khảo gốc và một ảnh liên quan từ Wikimedia Commons.
- Mục video liên quan mở trên trang của VOV, VTV hoặc Tuổi Trẻ; cần kết nối Internet để xem.
- Điều khiển âm thanh, toàn màn hình, đổi thiết lập giọng đọc, chia sẻ và sao chép liên kết.

Thanh công cụ ở trang chủ và trang địa điểm dùng các nút HTML có nhãn theo trạng thái: Âm thanh bật/tắt, Màn hình thường/Toàn màn hình, Tiếng Việt/English và Đã sao chép. Biểu tượng và nhãn cập nhật cùng nhau; khi thoát toàn màn hình bằng Esc, nút cũng trở về trạng thái thường. Nút ngôn ngữ thay đổi thiết lập giọng đọc tổng hợp, không dịch nội dung hoặc bản thu MP3.

Liên kết chia sẻ tới từng điểm đến sử dụng `#bridge`, `#museum`, `#flag`, `#monument` hoặc `#union`.

Ảnh trang chủ hiện tại là `frontend/public/home-map-sharp.png` (1672×941). Các khung địa điểm và ghim vẽ sẵn đã được xóa khỏi ảnh để thay bằng năm nút HTML thống nhất: ảnh thu nhỏ, tên, mô tả ngắn và mũi tên. Ghim vàng nhấn được nằm tại công trình tương ứng. Vị trí ghim dùng `hotspot` trong `frontend/src/data.ts`; vị trí thẻ nằm trong `frontend/src/style.css`. Nút Cầu Hiền Lương nằm trên vùng sông bên trái cầu. Nút Nhà trưng bày được thu nhỏ và đặt bên trái tòa nhà; các nút không chồng nhau.

Nhà liên hiệp có đường dẫn `#union`, bộ lọc tư liệu `zone_id=union` và dùng lại nhân vật hướng dẫn Nhà trưng bày. Ảnh do bạn cung cấp tại `frontend/public/union-reference.png` được dùng cho ảnh thu nhỏ của nút, nền trang chi tiết và thư viện ảnh; thư viện vẫn giữ bản đồ tổng quan. Chưa có tư liệu thuyết minh riêng cho điểm này; có thể nhập bằng API hoặc CLI như các điểm khác.

Ảnh được chỉnh bằng image_gen tích hợp; prompt chỉnh khung địa điểm lưu tại `assets/reference/home-map-landmarks-prompt.txt`. Sân khấu mái xanh ở tiền cảnh đã được xóa, thay bằng sân lát gạch và cảnh quan liền mạch; prompt lưu tại `assets/reference/home-map-no-stage-prompt.txt`. Bãi đỗ xe cạnh Nhà trưng bày đã được xóa và nối lại bằng thảm cỏ, lối đi; prompt lưu tại `assets/reference/home-map-no-parking-prompt.txt`. Ảnh hiện tại đã được làm rõ chi tiết bằng image_gen, vẫn có kích thước thực 1672×941; prompt tại `assets/reference/home-map-sharp-prompt.txt`. Trang chủ bỏ bộ lọc tăng tương phản và bão hòa màu. Các ảnh bản đồ trước đó giữ để tham khảo, không dùng cho trang chủ.

## Nhân vật thuyết minh

Trang chủ phát bản thu MP3 do bạn cung cấp tại `frontend/public/audio/home-introduction.mp3`. Bản thu phát liên tục; chuyển địa điểm sẽ dừng bản thu trước khi phát thuyết minh của địa điểm. Nút âm thanh tắt tiếng bản thu mà không đặt lại vị trí. Nếu trình duyệt chặn tự phát, chạm lời chào để nghe; chạm lại trong lúc phát không khởi động lại bản thu. Bản thu giữ nguyên ngôn ngữ của file; nút đổi ngôn ngữ giọng đọc chỉ áp dụng cho thuyết minh tổng hợp tại các địa điểm.

Mỗi địa điểm dùng một nhân vật thuyết minh riêng: chú bộ đội ở Cầu Hiền Lương, nữ hướng dẫn viên áo dài ở Nhà trưng bày, nữ chiến sĩ ở Kỳ đài và người thuyết minh lớn tuổi ở Tượng đài. Trang chủ giữ chú bộ đội ban đầu. Cấu hình trong `frontend/src/guides.ts`; các ảnh mới ở `frontend/public/guides/`, gồm ảnh tư thế giới thiệu và ảnh miệng nói cho từng nhân vật. Tất cả dùng chung cử chỉ, nhịp chuyển động và điều khiển thuyết minh; việc đổi nhân vật không đổi giọng đọc hoặc nội dung. Nhân vật là hình minh họa hư cấu, không đại diện cho nhân vật lịch sử cụ thể. Bộ prompt tạo ảnh bằng công cụ image_gen được lưu tại `assets/reference/narrator-prompts.json`.

## Responsive và adaptive UI

Các quy tắc trong `frontend/src/responsive.css` điều chỉnh bố cục bằng CSS media queries, không tải lại trang hoặc đặt lại trạng thái khi đổi kích thước:

- Màn hình rộng giữ bố cục ảnh nền cũ với các vùng chạm tương ứng trên nhãn và thanh công cụ.
- Khi chiều rộng ≤ 1100px, tỷ lệ màn hình ≤ 4:3 hoặc chiều cao ≤ 600px, trang chủ chuyển sang bố cục cuộn với bản đồ tổng quan, thẻ chọn địa điểm, công cụ có nhãn và khung chat hiển thị đầy đủ. Bản đồ tổng quan dùng để xem; chọn địa điểm bằng các thẻ bên dưới.
- Thẻ địa điểm dùng hai cột trên tablet và một cột khi chiều rộng ≤ 600px. Trang khám phá chuyển sang một cột ở ≤ 900px; thanh chọn địa điểm cuộn ngang khi cần.
- Nút thao tác trên bố cục nhỏ có vùng chạm tối thiểu 44px; ô nhập dùng cỡ chữ 16px. Giao diện có khoảng đệm safe area và tắt hiệu ứng khi thiết bị bật giảm chuyển động.

Khi thay đổi giao diện, kiểm tra cả trang chủ và trang địa điểm ở 320×740, 390×844, 768×1024, 1024×768, 1440×900, 1920×1080 và 844×390. Kiểm tra chọn địa điểm, thanh công cụ, tư liệu và chat; không được có cuộn ngang toàn trang.

Các cảnh 3D là hình minh họa, không phải ảnh tư liệu lịch sử hay mô hình 3D có thể xoay. Ảnh Wikimedia Commons trong thư viện ghi tên tác giả, nguồn và giấy phép CC BY-SA 3.0 ngay dưới ảnh.
