# Dữ liệu và quyền riêng tư

`vi-humanizer` là bộ hướng dẫn biên tập chạy trong agent mà người dùng chọn. Quy trình Markdown
cốt lõi không có máy chủ riêng, telemetry hoặc bước gửi văn bản đến dịch vụ của maintainer.
Plugin không khai báo MCP server, hook hay quyền đăng nhập vào dịch vụ bên ngoài.

Văn bản đưa vào Claude hoặc Codex vẫn được xử lý theo cấu hình, quyền truy cập và chính sách dữ
liệu của nền tảng đó. Cài skill không làm văn bản trở thành dữ liệu chỉ xử lý trên máy.

## Advisor tùy chọn

Python CLI `advisor/` chỉ gọi TypeSafe khi host chủ động chạy lệnh với credential được inject.
Core không tự gọi CLI. Nếu dùng `assess` hoặc `rank`, các đoạn văn và ngữ cảnh được chọn cho lệnh
đó được gửi qua HTTPS tới TypeSafe để nhận tín hiệu thẩm định. Jev không sinh văn bản; host agent
vẫn quyết định có sửa hay không. Thiếu credential hoặc lỗi dịch vụ không chặn core.

CLI không ghi API key, request body hoặc raw response vào báo cáo. Điều này không thay thế chính
sách dữ liệu của TypeSafe hoặc log do host tự bật. Xem contract và giới hạn input trong
[`references/typesafe-advisor.md`](references/typesafe-advisor.md) trước khi bật advisor.

## Issue, pull request và ca sửa sai

Issue và pull request của repo công khai có thể được người khác đọc. Chỉ gửi nội dung mày có
quyền công bố; thay tên, dữ kiện nội bộ và thông tin cá nhân bằng ví dụ giả lập. Không gửi API key
hoặc credential qua issue. Hướng dẫn ca hiệu chuẩn nằm trong [`CONTRIBUTING.md`](CONTRIBUTING.md).

Liên hệ về quyền riêng tư qua [GitHub Issues](https://github.com/fioenix/vi-humanizer/issues),
chỉ mô tả vấn đề đã loại dữ liệu nhạy cảm.
