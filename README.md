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

Từ thư mục chứa tệp README này, trong terminal thứ nhất:

```bash
python3 backend/manage.py seed
python3 backend/server.py
```

Trong terminal thứ hai:

```bash
cd frontend
npm install
npm run dev
```

Mở **http://localhost:5173**. Vite chuyển tiếp đường dẫn `/api` đến backend tại `127.0.0.1:8000`. Lệnh `seed` có thể chạy lại; tài liệu trùng `id` sẽ được cập nhật.

## Thêm tư liệu

Mỗi tài liệu JSON cần `id`, `title`, `content`. Có thể thêm `source` và `category` để ghi nguồn và phân loại. Ví dụ lưu nội dung sau vào `tai-lieu.json`:

```json
{
  "id": "cau-hien-luong-nguon-1",
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
  -d '{"id":"vi-du","title":"Tư liệu mới","content":"Nội dung cần tra cứu","source":"Nguồn tư liệu"}'
```

API còn có `GET /api/health`, `GET /api/documents`, `GET /api/search?q=...` và `POST /api/chat` với body `{"question":"..."}`.

Khi đang khám phá một điểm đến, giao diện gửi thêm `zone_id` (`bridge`, `museum`, `flag` hoặc `monument`) để câu trả lời chỉ lấy tư liệu của địa điểm đó. API tìm kiếm cũng nhận `zone_id` tùy chọn.

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

- Màn hình chính dùng lại ảnh thiết kế gốc với hướng dẫn viên ảo; bốn điểm đến và các nút vẽ sẵn trên ảnh đều có vùng nhấn tương tác.
- Mỗi điểm đến mở một giao diện riêng với ảnh 3D dựng từ ảnh tham khảo do bạn cung cấp.
- Thuyết minh tự phát khi chọn điểm đến hoặc chủ đề; có nút tạm dừng, phát lại và dừng.
- Ô chat tra cứu backend theo địa điểm và hiển thị nguồn tư liệu.
- Thư viện ảnh gồm cảnh 3D, ảnh tham khảo gốc và một ảnh liên quan từ Wikimedia Commons.
- Mục video liên quan mở trên trang của VOV, VTV hoặc Tuổi Trẻ; cần kết nối Internet để xem.
- Điều khiển âm thanh, toàn màn hình, đổi thiết lập giọng đọc, chia sẻ và sao chép liên kết.

Liên kết chia sẻ tới từng điểm đến sử dụng `#bridge`, `#museum`, `#flag` hoặc `#monument`.

Ảnh màn hình chính chứa sẵn nhãn và các thanh điều khiển. Các vùng nhấn trong suốt được đặt theo vị trí trong ảnh nên cần điều chỉnh nếu thay đổi bố cục ảnh.

Các cảnh 3D là hình minh họa, không phải ảnh tư liệu lịch sử hay mô hình 3D có thể xoay. Ảnh Wikimedia Commons trong thư viện ghi tên tác giả, nguồn và giấy phép CC BY-SA 3.0 ngay dưới ảnh.
