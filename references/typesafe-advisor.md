# Thẩm định bằng TypeSafe đã có trên host

Vietnamizer không đóng gói runtime TypeSafe, không thiết lập credential và không cần dịch vụ
này để biên tập. Có thể tận dụng skill chính chủ đã có khi thẩm định hữu ích cho tác vụ hiện tại
và đáp ứng các điều kiện dưới đây. Đây chỉ là phần bổ trợ, không phải dependency.

## Điều kiện sử dụng

- Host đã cung cấp skill TypeSafe chính chủ qua cơ chế discovery được hỗ trợ. Dùng định danh do
  host cung cấp; không đoán tên, quét thư mục máy, tải hướng dẫn từ mạng hoặc tự cài skill.
- Skill đã cài chỉ cung cấp hướng dẫn; khả năng gọi dịch vụ phải thực sự có và được phép.
- Người dùng đã đồng ý gửi đúng đoạn văn và ngữ cảnh tối thiểu cho lần thẩm định. Yêu cầu biên tập
  đơn thuần, skill đã cài hoặc key có sẵn không thay thế cho sự đồng ý này.
- Cấu hình, credential, kết nối và chính sách dữ liệu do skill TypeSafe cùng host quản lý.
  Vietnamizer không đọc key từ môi trường, yêu cầu dán key hoặc dựng connector thay họ.

Nếu harness không cung cấp skill TypeSafe, bỏ qua im lặng và tiếp tục core; không gợi ý agent
hoặc người dùng cài đặt, thiết lập hay tìm key. Nếu thiếu điều kiện khác, cũng tiếp tục core.
Chỉ báo *chưa kiểm tra* khi người dùng chủ động hỏi hoặc yêu cầu thẩm định bằng TypeSafe;
không mạo nhận kết quả. Việc không dùng TypeSafe không phải lỗi hoặc thiếu sót của tác vụ.

## Ranh giới phán đoán

Host Agent gọi tên V20 `lexically_incomplete` hoặc `unnatural_collocation`, loại trừ vùng bảo
toàn và tạo trước một đến ba candidate. TypeSafe chỉ thẩm định nhu cầu sửa, chất lượng candidate,
giữ nghĩa, giọng và an toàn; không được yêu cầu sinh, nối hoặc sửa câu chữ.

Chỉ gửi đoạn nhỏ nhất còn đủ nghĩa và các candidate đã có. Loại secret, vùng bảo toàn, định danh
không cần thiết, nhãn kiểm thử và provenance; nếu không tách được dữ liệu nhạy cảm thì bỏ qua
dịch vụ. Không gửi toàn tài liệu chỉ để quyết định một edit cục bộ.

Tín hiệu chỉ hỗ trợ Agent; không làm hard gate, không cứu candidate đã trượt năm quy tắc chốt
chặn và không dùng threshold chưa hiệu chỉnh. Xếp hạng chỉ áp dụng cho ít nhất hai candidate
đã đủ chuẩn. Agent quyết định giữ hay sửa và viết bản cuối.

Chỉ dùng kết quả thực sự nhận được cho đúng đoạn gốc, ngữ cảnh và candidate hiện tại. Input đổi
thì kết quả cũ hết hiệu lực. Thiếu capability, timeout hoặc response không hợp lệ là *chưa kiểm
tra*, không phải `pass`; việc biên tập vẫn tiếp tục bằng core.
