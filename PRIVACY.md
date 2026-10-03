# Dữ liệu và quyền riêng tư

`vietnamizer` là bộ hướng dẫn biên tập chạy trong agent mà người dùng chọn. Quy trình Markdown
cốt lõi không có máy chủ riêng, telemetry hoặc bước gửi văn bản đến dịch vụ của maintainer.
Plugin không khai báo MCP server, hook hay quyền đăng nhập vào dịch vụ bên ngoài.

Văn bản đưa vào Claude hoặc Codex vẫn được xử lý theo cấu hình, quyền truy cập và chính sách dữ
liệu của nền tảng đó. Cài skill không làm văn bản trở thành dữ liệu chỉ xử lý trên máy.

## TypeSafe tùy chọn đã có trên host

Repo và các gói phân phối không chứa mã tích hợp TypeSafe. Khi Agent tận dụng skill
TypeSafe chính chủ đã có trên host và người dùng đồng ý gửi dữ liệu, đoạn gốc, candidate và ngữ cảnh tối
thiểu có thể được gửi tới TypeSafe. Vietnamizer không quản lý credential hoặc kết nối đó và
không tự bật dịch vụ. Thiếu capability hoặc lỗi không chặn core.

Maintainer không nhận hoặc lưu văn bản biên tập qua một máy chủ Vietnamizer, nên không có thời
hạn lưu phía maintainer cho dữ liệu này. Thời hạn lưu, cách xóa và log phía Claude/Codex hoặc
TypeSafe phụ thuộc tài khoản, cấu hình và chính sách của từng bên; repo không bảo đảm họ không
lưu dữ liệu. Người dùng cần kiểm chính sách dịch vụ trước khi cho phép gửi, có thể từ chối
thẩm định và tiếp tục dùng core. Hướng dẫn nằm trong
[ranh giới TypeSafe](references/typesafe-advisor.md).

Skill chỉ dùng mẫu giọng hoặc hồ sơ người dùng chủ động cung cấp trong tác vụ, không tự truy
xuất hay cập nhật memory. Việc lưu hội thoại hoặc file bởi host vẫn theo chính sách host.

## Issue, pull request và ca sửa sai

Issue và pull request của repo công khai có thể được người khác đọc. Chỉ gửi nội dung mày có
quyền công bố; thay tên, dữ kiện nội bộ và thông tin cá nhân bằng ví dụ giả lập. Không gửi API key
hoặc credential qua issue. Hướng dẫn ca hiệu chuẩn nằm trong [`CONTRIBUTING.md`](CONTRIBUTING.md).

Liên hệ về quyền riêng tư qua [GitHub Issues](https://github.com/fioenix/vietnamizer/issues),
chỉ mô tả vấn đề đã loại dữ liệu nhạy cảm.
