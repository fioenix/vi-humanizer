# Kiểm Vietnamizer trước khi gửi directory Claude

Đường cài marketplace riêng không đồng nghĩa được Anthropic niêm yết. Chạy CLI validator,
kiểm archive và cài sạch trước; portal Validate vẫn là cổng riêng cho đúng commit được gửi.

## Trạng thái nguồn

Repo và ba archive 0.9.7 không còn mã advisor, SDK hoặc harness TypeSafe. Root source vẫn có
tooling maintainer và hồ sơ lịch sử; cần review đúng commit GitHub trong portal trước khi gửi.
Không suy ra approval chỉ từ validator CLI hoặc archive đã qua kiểm tra.

README dùng ảnh Markdown với biến thể GitHub sáng/tối. Client khác có thể hiển thị cả hai ảnh;
phải xem trực tiếp, không coi fragment GitHub là hỗ trợ dark mode của mọi client. Manifest Claude
hiện trỏ icon violet; khả năng chọn icon tối tùy client, không thêm field chưa được xác nhận.

## Review Desktop ngày 03/10/2026

Ảnh review của maintainer xác nhận Desktop nhận bản 0.9.7, bật plugin và thấy một skill,
nhưng dùng icon mặc định. Mô tả trước đó chỉ có tagline; manifest và catalog đã được sửa
thành mô tả công dụng, phạm vi bảo toàn và yêu cầu tài khoản. Tagline trong README giữ nguyên.

Theo [plugin manifest reference](https://code.claude.com/docs/en/plugins-reference#directory-listing-fields),
`icon` là trường directory listing và Claude Code không đọc nó khi nạp plugin. Tài liệu này
không xác nhận Desktop hiển thị icon từ ZIP tùy chỉnh. Giữ đường dẫn SVG hợp lệ, không thêm
field dark-mode hoặc đổi định dạng ảnh chỉ dựa trên suy đoán. Icon Desktop vẫn chưa được
xác minh; validator đạt không chứng minh icon sẽ hiển thị.

Cập nhật bằng ZIP mới cùng tên plugin, không tạo bản Vietnamizer thứ hai. Sau khi cập nhật,
kiểm mô tả trong Overview và chạy các prompt bên dưới. Chưa có bằng chứng model Claude chạy.

## Ba prompt kiểm core

Các ca dưới đây là yêu cầu chạy tay và tiêu chí chấp nhận, không phải bằng chứng model đã chạy.
Trong Claude Code dùng prefix `/vietnamizer:vietnamizer`; surface khác dùng tên skill tương ứng.

### 1. Hoàn chỉnh ý nhưng giữ thông tin

```text
/vietnamizer:vietnamizer
Sửa câu sau trong một bài kể trải nghiệm, chỉ trả câu cuối:
Đã thử ba cách mà vẫn không giải quyết vấn đề.
```

Chấp nhận: bổ sung ý kết quả “giải quyết được vấn đề”, giữ “ba cách” và không thêm nguyên nhân.

### 2. Không sửa quá tay

```text
/vietnamizer:vietnamizer
Rà câu sau trong chat công việc; nếu đã tự nhiên thì giữ nguyên:
Tôi rời công ty lúc sáu giờ.
```

Chấp nhận: giữ nguyên câu; không đổi “rời” thành “rời rạc”, không đổi giờ hoặc đại từ.

### 3. Giữ thuật ngữ và byte code

````text
/vietnamizer:vietnamizer
Sửa phần văn xuôi của README dưới đây, giữ nguyên khối code từng byte:
Cách xử lý đơn giản nhất tăng số worker.

```bash
WORKERS=3 ./run-worker.sh --dry-run
```
````

Chấp nhận: thêm “là” sau “đơn giản nhất”; giữ “worker” và khối code đúng từng byte.

## Cổng dữ liệu và fallback

- Host có skill TypeSafe nhưng chưa có quyền gửi dữ liệu: không gọi dịch vụ, không tìm key.
- Harness không cung cấp skill TypeSafe: core tiếp tục im lặng, không nhắc agent hoặc người dùng
  cài đặt, thiết lập hay tìm key. Không coi việc thiếu TypeSafe là lỗi hoặc thiếu sót.
- Host có skill nhưng thiếu capability TypeSafe: core tiếp tục; không tự cài hoặc dựng connector.
- Thẩm định hữu ích và được cho phép gửi dữ liệu: chỉ thẩm định candidate có trước qua skill chính chủ đã có;
  không tự dựng connector, không gửi toàn văn bản hoặc vùng bảo toàn.
- Cho mẫu phong cách trong yêu cầu: dùng đúng mẫu; không truy xuất/lưu Claude memory.

Các bước còn chờ: chạy và lưu kết quả model trên surface mục tiêu, review UI sáng/tối,
review nguồn GitHub phân phối, kiểm URL public và portal Validate. Push, dùng quota và submit
cần quyền riêng; checklist này không thực hiện các hành động đó.

Nguồn: [checklist Anthropic](https://claude.com/docs/plugins/pre-submission-checklist),
[chính sách directory](https://support.claude.com/en/articles/13145358-anthropic-software-directory-policy),
[quy trình gửi](https://claude.com/docs/plugins/submit).
