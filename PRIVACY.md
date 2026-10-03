# Dữ liệu và quyền riêng tư

`vietnamizer` là bộ hướng dẫn biên tập chạy trong agent mà người dùng chọn. Quy trình Markdown
cốt lõi không có máy chủ riêng, telemetry hoặc bước gửi văn bản đến dịch vụ của maintainer.
Plugin không khai báo MCP server, hook hay quyền đăng nhập vào dịch vụ bên ngoài.

Văn bản đưa vào Claude hoặc Codex vẫn được xử lý theo cấu hình, quyền truy cập và chính sách dữ
liệu của nền tảng đó. Cài skill không làm văn bản trở thành dữ liệu chỉ xử lý trên máy.

## Dữ liệu đầu vào và quyền kiểm soát

Quy trình dùng văn bản người dùng chủ động cung cấp, yêu cầu biên tập, ngữ cảnh tối thiểu và
mẫu giọng tùy chọn cho đúng tác vụ. Những phần này có thể chứa dữ liệu cá nhân; người dùng nên
ẩn danh trước khi gửi. Vietnamizer không yêu cầu hồ sơ cá nhân, vị trí, lịch sử hội thoại hoặc
dữ liệu khác chỉ để dự phòng. Mục đích sử dụng là biên tập và đối chiếu ý, giọng của văn bản.

Không cung cấp dữ liệu thẻ thanh toán thuộc PCI DSS, thông tin sức khỏe cá nhân được bảo vệ
(PHI), định danh do chính phủ cấp, mật khẩu, API key, mã MFA/OTP hoặc secret xác thực khác.
Nếu nhận thấy các dữ liệu này, skill dừng biên tập đầu vào đó và yêu cầu bản đã che hoặc ví dụ
giả lập; không trích lại, lưu thành ca hiệu chuẩn hay gửi sang TypeSafe. Consent không gỡ bỏ
giới hạn này. Ví dụ giả lập hoặc nội dung nói chung về sức khỏe và giấy tờ không bị cấm chỉ vì
chủ đề. Việc biên tập không cần thu thập thêm dữ liệu cá nhân nhạy cảm; ưu tiên bản đã ẩn danh.

Người dùng có thể không cung cấp mẫu giọng, từ chối thẩm định bên ngoài hoặc dùng bản giả lập
mà vẫn dùng được quy trình cốt lõi. Skill không tự lưu phản hồi hoặc sửa quy tắc: ghi nhật ký
hiệu chuẩn cần một tác vụ bảo trì và quyền ghi file cụ thể. Xóa hội thoại hoặc file được host
lưu phải thực hiện qua cơ chế của host; Vietnamizer không điều khiển hay bảo đảm thời hạn xóa
của nền tảng đó.

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

Maintainer và người đọc GitHub có thể tiếp cận nội dung mày chủ động đăng để hỗ trợ hoặc xem
ca sửa sai. Nội dung công khai không có thời hạn tự xóa do Vietnamizer đặt; lịch sử Git, bản
fork và bản sao có thể vẫn còn sau khi chỉnh sửa. Có thể sửa bài đăng hoặc liên hệ maintainer
để yêu cầu gỡ nội dung trong phạm vi kiểm soát của repo; không bảo đảm xóa mọi bản sao trên
GitHub hoặc do người khác giữ. Ca hiệu chuẩn được duyệt chỉ dùng ví dụ được phép công bố,
đã loại dữ liệu cá nhân và nhạy cảm, để bảo trì quy tắc biên tập.

Liên hệ về quyền riêng tư qua [GitHub Issues](https://github.com/fioenix/vietnamizer/issues),
chỉ mô tả vấn đề đã loại dữ liệu nhạy cảm.
