# Vĩ tuyến 17 — Giao diện và kho tư liệu

Ứng dụng React hiển thị bản đồ di tích, hiện vật và tra cứu tư liệu. Backend Python lưu tài liệu cùng vector tìm kiếm trong SQLite. Bản hiện tại chạy cục bộ, không cần tài khoản dịch vụ hay khóa API.

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

## Hiệu ứng camera khi chọn địa điểm

Bấm thẻ hoặc ghim trên bản đồ để zoom tới địa điểm trong 900 ms, sau đó mở trang chi tiết với hiệu ứng hiện dần. Nút **Bản đồ** và Back của trình duyệt đưa về bản đồ đang zoom ở địa điểm vừa xem rồi thu nhỏ về toàn cảnh. Forward khôi phục địa điểm trong URL; liên kết trực tiếp `#bridge`, `#museum`, `#flag`, `#monument`, `#union` vẫn mở được.

Cấu hình `href` và `camera: { x, y, zoom }` của từng địa điểm nằm trong `frontend/src/data.ts`; `x`, `y` là phần trăm trên ảnh gốc. Thời lượng, easing và thời gian hiện trang chi tiết nằm trong `CAMERA_MOTION` tại `frontend/src/useZoneNavigation.ts`. Component `MapCamera.tsx` tính tọa độ theo kích thước ảnh thực, `object-fit` và `object-position`, kể cả phần ảnh bị cắt trên điện thoại. Hiệu ứng dùng CSS transform/opacity, không thêm thư viện.

Khi chuyển cảnh, giao diện khóa thao tác lặp; đổi URL hoặc unmount hủy timer và animation frame còn chờ. Thao tác bàn phím dùng các nút HTML hiện có; sau khi quay về, focus trở lại thẻ địa điểm. Nếu bật `prefers-reduced-motion`, giao diện chuyển nội dung ngay và không chạy zoom.

## Tư liệu theo địa điểm

`GET /api/narration?zone_id=bridge` là API dữ liệu văn bản có sẵn, trả toàn bộ tư liệu thuộc địa điểm. Giao diện hiển thị `content` và nguồn để đọc, không chuyển văn bản thành giọng nói. Tài liệu có `id` trùng địa điểm được ưu tiên làm phần giới thiệu; những tài liệu khác có thể mở trong Mô tả tổng quan. Chat tìm trên các đoạn từ cùng kho tư liệu.

Khi chưa có tư liệu hoặc mất kết nối, giao diện thông báo và cho phép **Tải lại tư liệu**. Chuyển địa điểm hoặc về bản đồ sẽ hủy yêu cầu cũ và xóa trạng thái chat của địa điểm trước. Dữ liệu cũ chưa gán `zone_id` vẫn được giữ; có thể nhập lại với địa điểm rõ ràng bằng API hoặc CLI.

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

- Màn hình chính đặt Nhà trưng bày ở tiền cảnh bên trái đường chính, đối diện khu Kỳ đài theo bố cục ảnh tham khảo. Hướng dẫn viên nằm ngay dưới logo; thanh công cụ và năm điểm tham quan vẫn dùng được.
- Các khu vực dùng nền ảnh toàn màn hình, cùng các widget chat, Hình ảnh và Mô tả tổng quan. Nội dung chi tiết chỉ mở khi chọn widget.
- Nhân vật hướng dẫn vẫn hiển thị; ứng dụng không phát lời thuyết trình, MP3 hoặc giọng tổng hợp.
- Ô chat tra cứu backend theo địa điểm và hiển thị nguồn tư liệu.
- Thư viện ảnh gồm cảnh 3D, ảnh tham khảo gốc và một ảnh liên quan từ Wikimedia Commons.
- Điều khiển toàn màn hình, tiếng Việt, chia sẻ, sao chép liên kết và quay về bản đồ.

Thanh công cụ có bốn nút: Màn hình thường/Toàn màn hình, Tiếng Việt, Chia sẻ và Sao chép liên kết. Biểu tượng cập nhật theo trạng thái; Esc đồng bộ lại nút toàn màn hình. Micro trong chat chỉ dùng để nhập câu hỏi bằng tiếng Việt, không phát lời thuyết trình.

Liên kết chia sẻ tới từng điểm đến sử dụng `#bridge`, `#museum`, `#flag`, `#monument` hoặc `#union`.

Ảnh trang chủ hiện tại là `frontend/public/home-map-open-forecourt-sharp.png` (1672×941). Các khung địa điểm và ghim vẽ sẵn đã được xóa khỏi ảnh để thay bằng năm nút HTML thống nhất: ảnh thu nhỏ, tên, mô tả ngắn và mũi tên. Ghim vàng nhấn được nằm tại công trình tương ứng. Vị trí ghim dùng `hotspot` trong `frontend/src/data.ts`; vị trí thẻ nằm trong `frontend/src/style.css`. Nút Cầu Hiền Lương nằm bên trái, thấp hơn icon ghim một chút, dùng cùng kích thước, chữ và bố cục với các thẻ địa điểm khác. Nút Nhà trưng bày nằm góc dưới bên trái bản đồ; công trình được thu nhỏ khoảng 15–18% để thoáng hơn. Ghim và camera Nhà trưng bày cùng tọa độ `x: 13.2, y: 60.5`; nhân vật đứng dưới logo ở `top: 12.6%`.

Nhà liên hiệp có đường dẫn `#union`, bộ lọc tư liệu `zone_id=union` và dùng chung nhân vật chú bộ đội của màn hình chính. Ảnh do bạn cung cấp tại `frontend/public/union-reference.png` được dùng cho ảnh thu nhỏ của nút, nền trang chi tiết và thư viện ảnh; thư viện vẫn giữ bản đồ tổng quan. Chưa có tư liệu riêng cho điểm này; có thể nhập bằng API hoặc CLI như các điểm khác.

Ảnh được chỉnh bằng image_gen tích hợp; prompt chỉnh khung địa điểm lưu tại `assets/reference/home-map-landmarks-prompt.txt`. Sân khấu mái xanh ở tiền cảnh đã được xóa, thay bằng sân lát gạch và cảnh quan liền mạch; prompt lưu tại `assets/reference/home-map-no-stage-prompt.txt`. Bãi đỗ xe cạnh Nhà trưng bày đã được xóa và nối lại bằng thảm cỏ, lối đi; prompt lưu tại `assets/reference/home-map-no-parking-prompt.txt`. Bản `home-map-sharp.png` đã được làm rõ chi tiết bằng image_gen; prompt tại `assets/reference/home-map-sharp-prompt.txt`. Bản hiện tại được chỉnh bằng image_gen tích hợp để chuyển Nhà trưng bày sang vị trí tiền cảnh bên trái, đồng thời nối lại cảnh quan ở vị trí cũ. Prompt tại `assets/reference/home-map-museum-relocated-prompt.txt`; ảnh vị trí thực tế bạn cung cấp lưu tại `assets/reference/museum-location-aerial-reference.png`. Nhà trưng bày trong bản mới được xoay song song đường chính, mặt tiền hướng ra đường. Sân lát hình chữ nhật, lối đi thẳng chính giữa và hai mảng cỏ hai bên được vẽ theo `assets/reference/museum-forecourt-reference.png`; prompt hai bước tại `assets/reference/home-map-museum-parallel-prompts.txt`. Bản `home-map-museum-compact.png` thu nhỏ riêng công trình Nhà trưng bày, giữ hướng song song đường và bố cục sân; prompt tại `assets/reference/home-map-museum-compact-prompt.txt`. Ảnh hiện tại được chỉnh bằng imagegen để xóa hàng rào trước Nhà trưng bày, nối sân ra vỉa hè và làm rõ chi tiết; prompt tại `assets/reference/home-map-open-forecourt-sharp-prompt.txt`. Kích thước ảnh thực vẫn là 1672×941. Trang chủ bỏ bộ lọc tăng tương phản và bão hòa màu. Các ảnh bản đồ trước đó giữ để tham khảo, không dùng cho trang chủ.

## Không gian Nhà trưng bày

`#museum` sử dụng nguyên ảnh giao diện bạn cung cấp tại `frontend/public/museum/exhibition-room-topics.png`. Có thể bấm vào icon vị trí của bốn chủ đề hoặc bốn thẻ hành trình phía dưới:

1. Hiệp định Giơ-ne-vơ và giới tuyến tạm thời (1954): `#museum/topic-1`.
2. Vĩnh Linh, lũy thép nơi tuyến đầu: `#museum/topic-2`.
3. Khát vọng thống nhất của đồng bào bờ Nam: `#museum/topic-3`.
4. Ngày chiến thắng và hồi sinh: `#museum/topic-4`.

Ba hiện vật mở riêng gồm **Mẹ Vĩnh Linh và cờ** (`#museum/mother-and-flag`), **Loa phát thanh** (`#museum/loudspeaker`) và **Ngôi sao** (`#museum/bronze-star`). Các vùng bấm dùng tọa độ theo ảnh, co giãn cùng ảnh để không lệch khi đổi kích thước cửa sổ. Hover và focus bàn phím chỉ làm sáng vòng tròn nhỏ quanh icon vị trí. Trên điện thoại, các thẻ chủ đề hiện thành danh sách có chữ và có thể cuộn; nút **Mở lộ trình tham quan** liệt kê đủ bảy mục.

Trang chi tiết phóng tới đúng khu vực trong ảnh; các chủ đề mở sẵn mô tả. **Về Nhà trưng bày**, Back/Forward và tải lại URL giữ đúng trang. Nút **Hình ảnh tư liệu**, chat, thanh công cụ và **Về bản đồ** vẫn hoạt động. Nhân vật trong ảnh vẫn được giữ; các trang chi tiết dùng chung ảnh nhân vật hướng dẫn, không có thao tác phát lời nói. Mô tả theo bố cục ảnh minh họa, còn tư liệu backend giữ nguyên nội dung và nguồn.

`frontend/src/museumExhibits.ts` chứa bảy mục, nội dung và các vùng ảnh. `MuseumExhibition.tsx` kết hợp với `DestinationScene.tsx` để dùng chung dialog ảnh và mô tả. Các ảnh nền và ảnh tham khảo cũ vẫn được lưu trong `frontend/public/museum/` và `assets/reference/`.

## Nhân vật hướng dẫn

`NarratorWidget.tsx` giữ nguyên ảnh chú bộ đội tại `/soldier-guide-present.png`: trang chủ đặt ngay dưới logo, các trang địa điểm và hiện vật đặt ở tiền cảnh. Nhà trưng bày giữ nhân vật có sẵn trong ảnh nền bạn cung cấp. Nhân vật chỉ hiển thị hình ảnh, không có nút nghe, chuyển động miệng theo âm thanh, phát MP3 hay giọng đọc tự động. Các tệp âm thanh và ảnh nhân vật cũ vẫn được lưu làm tài nguyên gốc, không được ứng dụng tải hoặc phát.

## Responsive và adaptive UI

Các quy tắc trong `frontend/src/responsive.css` và `destination-scene.css` điều chỉnh bố cục bằng CSS media queries, không tải lại trang hoặc đặt lại trạng thái khi đổi kích thước:

- Màn hình rộng giữ bố cục ảnh nền cũ với các vùng chạm tương ứng trên nhãn và thanh công cụ.
- Khi chiều rộng ≤ 1100px, tỷ lệ màn hình ≤ 4:3 hoặc chiều cao ≤ 600px, trang chủ chuyển sang bố cục cuộn với bản đồ tổng quan, thẻ chọn địa điểm, công cụ có nhãn và khung chat hiển thị đầy đủ. Bản đồ tổng quan dùng để xem; chọn địa điểm bằng các thẻ bên dưới.
- Thẻ địa điểm ở trang chủ dùng hai cột trên tablet và một cột khi chiều rộng ≤ 600px. Các khu vực và hiện vật dùng khung `100dvh`; nền giữ tỷ lệ gốc, nhân vật đứng ở tiền cảnh và ba widget gọn ở bên dưới. Ở chiều rộng ≤ 760px, ô chat lên một hàng riêng, Hình ảnh và Mô tả tổng quan chia hàng bên dưới. Màn hình ngang thấp thu gọn nhân vật. Nội dung widget cuộn bên trong dialog, không gây tràn trang.
- Nút thao tác trên bố cục nhỏ có vùng chạm tối thiểu 44px; ô nhập dùng cỡ chữ 16px. Giao diện có khoảng đệm safe area và tắt hiệu ứng khi thiết bị bật giảm chuyển động.

Khi thay đổi giao diện, kiểm tra cả trang chủ và trang địa điểm ở 320×740, 390×844, 768×1024, 1024×768, 1440×900, 1920×1080 và 844×390. Kiểm tra chọn địa điểm, thanh công cụ, tư liệu và chat; không được có cuộn ngang toàn trang.

Các cảnh 3D là hình minh họa, không phải ảnh tư liệu lịch sử hay mô hình 3D có thể xoay. Ảnh Wikimedia Commons trong thư viện ghi tên tác giả, nguồn và giấy phép CC BY-SA 3.0 ngay dưới ảnh.
