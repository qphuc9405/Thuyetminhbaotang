# Kiểm tra Ollama cục bộ — 11/11/2026

## Cấu hình đã cài và chạy

- Ollama `0.40.16`, gói Linux amd64 từ trang tải chính thức của Ollama.
- Runtime: `~/.local/share/ollama-runtime`; lệnh: `~/.local/bin/ollama`.
- Dịch vụ người dùng: `~/.config/systemd/user/ollama.service`, được enable; chỉ lắng nghe `127.0.0.1:11434`.
- Model: `qwen2.5:3b`, ID `357c53fb659c`, dung lượng khoảng 1,9 GB.
- Đã kiểm tra SHA-256 của blob model khớp manifest registry:
  `5ee4f07cdb9beadbbb293e85803c569b01bd37ed059d2715faa7bb405f31caa6`.
- Inference thực tế: CPU, context 8.192 token, một yêu cầu song song.
- Backend `.env`: host `http://127.0.0.1:11434`, model `qwen2.5:3b`, timeout 300 giây, không tự retry LLM. Không cần API key cho Ollama cục bộ.
- Ứng dụng đã được khởi động lại bằng `./run.sh` sau khi cập nhật cấu hình.

## Kiểm tra đầu cuối thật

Gửi `POST http://127.0.0.1:5173/mg/api/chat`, ngôn ngữ `vi`, với câu hỏi:

> Khu di tích Vĩ tuyến 17 có gì nổi bật?

Kết quả:

| Thuộc tính | Giá trị |
|---|---|
| HTTP | 200 |
| mode | `llm` |
| Thời gian đầu cuối | 94,7 giây |
| Số phần tử sources | 8 |
| Số ảnh | 3 |
| Cảnh báo | `ungrounded_years:1954` |

Câu trả lời là văn bản tiếng Việt giới thiệu các công trình và hoạt động lịch sử; không còn thông báo dịch vụ AI không khả dụng của chế độ `extractive_fallback` trong lần thử này.

**Giới hạn:** Đây là một lần kiểm tra tích hợp để xác nhận kết nối và sinh câu trả lời thật, không phải đánh giá toàn bộ chất lượng RAG. Cảnh báo năm 1954 cho biết năm đó không được bộ kiểm tra tìm thấy trong context được chọn cho lần hỏi này. Chưa kiểm duyệt mọi khẳng định trong câu trả lời, chưa đo Anh/Trung, chưa chứng minh các ngưỡng nghiệm thu. Model nhỏ chạy CPU có thể chậm và cần tiếp tục kiểm chứng chất lượng nội dung. ElevenLabs chưa được cấu hình/kiểm tra trong công việc này.

## Vận hành

```bash
systemctl --user status ollama
systemctl --user restart ollama
~/.local/bin/ollama list
~/.local/bin/ollama ps
journalctl --user -u ollama -n 50 --no-pager
```

Dịch vụ tự khởi động trong phiên đăng nhập người dùng. Chạy web bằng `./run.sh`; địa chỉ `http://localhost:5173`. Thay đổi `.env` cần khởi động lại backend. Nội dung hội thoại cũ vẫn có thể hiển thị thông báo fallback đã nhận trước khi cài; hãy gửi câu hỏi mới sau khi tải lại trang.

## Cập nhật tối ưu độ trễ sau lần kiểm tra ban đầu

- Giữ model `qwen2.5:3b` và CPU. Vẫn truy xuất đủ ứng viên theo cấu hình (mặc định 6); ưu tiên cụm từ trong nội dung và giữ ghi chú nguồn mâu thuẫn, rồi chọn tối đa 3 đoạn cho câu thông thường. Không mở rộng đoạn lân cận, context văn bản khoảng 2.400 ký tự cộng nhãn ảnh gọn, mục tiêu 45–80 từ và tối đa 400 token đầu ra.
- Câu hỏi yêu cầu chi tiết/kể chuyện/phân tích được cấp context tới 5.000 ký tự và 850 token đầu ra. Câu hỏi về ảnh vẫn dùng metadata ảnh đầy đủ.
- Prompt local được rút gọn nhưng giữ quy tắc bám nguồn, từ chối thiếu bằng chứng, phân biệt nguồn và kiểm tra citation bằng backend. Chế độ Cloud giữ ngân sách/prompt cũ.
- Ollama giữ model trong RAM 30 phút sau lời gọi; backend local timeout 90 giây, không retry.
- Cache tối đa 128 câu trả lời trong bộ nhớ, TTL 600 giây; chỉ câu hỏi độc lập có nguồn và không có cảnh báo. Cache tách theo ngôn ngữ; câu hỏi tiếp nối vẫn dùng lịch sử và không dùng cache chung. Không cache lỗi/fallback/câu bị cảnh báo.
- Giao diện hiển thị “Đang soạn câu trả lời từ tư liệu…” kèm thời gian chờ; chưa triển khai truyền từng token ra giao diện.

Đo lại cùng câu hỏi tổng quan qua frontend proxy với hai phiên riêng:

| Lần hỏi | Thời gian | Chế độ | Cache | Cảnh báo |
|---|---:|---|---|---|
| Câu hỏi mới sau tối ưu, bản cuối | 15,55 giây | llm | Không | Không |
| Lặp lại câu hỏi đó | 0,01 giây | llm | Có | Không |
| Câu hỏi mới: Cột cờ đầu tiên ở Hiền Lương cao bao nhiêu? | 13,13 giây | llm | Không | Không |

Phép đo trung gian với prompt local khoảng 1.051 token đạt 21,54 giây, giảm từ khoảng 4.484 token/94,7 giây của lần ban đầu. Bản cuối bổ sung lựa chọn đoạn dựa trên nội dung và giữ ghi chú mâu thuẫn; phép thử câu cột cờ trả chiều cao đầu tiên 12 mét, sau đó 18 mét, phù hợp tư liệu được chọn. Không cắt danh sách ứng viên xuống top-3 ngay từ bước truy xuất vì có thể làm mất đoạn trả lời ở hạng 4–6. Các số trên là phép đo mẫu trên máy này, không phải cam kết mọi câu đều có độ trễ tương tự. Không có cảnh báo tự động chưa đồng nghĩa mọi khẳng định đã được chuyên gia kiểm chứng.

Kiểm thử sau thay đổi: **118 backend test pass, 9 frontend test pass, frontend build thành công**; sau điều chỉnh vị trí ghi nhận cờ injection, chạy lại 22 test pipeline/local đều đạt. Backend chạy trong điều kiện không có tệp `.env` local vì test kiểm tra gói mã nguồn yêu cầu tệp này vắng mặt; cấu hình local được tạm cất và khôi phục bằng `finally`, ứng dụng đang chạy giữ nguyên cấu hình đã nạp. Fixture dịch vụ mock chỉ định host/model Cloud rõ ràng để không phụ thuộc `.env` người phát triển. Các test bổ sung kiểm tra ngân sách local, cache tách ngôn ngữ/ngữ cảnh, TTL, không cache đầu ra bị cảnh báo, chỉ kiểm chứng nội dung thực sự gửi vào context, và không bỏ sót đáp án/ghi chú mâu thuẫn khi nén context.
