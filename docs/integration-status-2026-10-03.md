# Quyết định tích hợp Vietnamizer 0.9.7

## Phạm vi maintainer đã duyệt

- Tích hợp thay đổi đã review vào `main`, push GitHub và kiểm CI; chưa tạo tag, GitHub Release
  hoặc submit directory Codex/Claude.
- Codex native: ảnh maintainer cung cấp xác nhận plugin 0.9.7 nạp skill và giữ nguyên câu
  “Tôi rời công ty lúc sáu giờ.”. Ca README chạy trong phiên có skill đã cài chỉ thêm “là”;
  kiểm so sánh byte xác nhận khối code không đổi. Đây không phải ca README chạy qua picker mới.
- Maintainer bỏ kiểm native light mode và harness không có TypeSafe khỏi điều kiện chặn
  tích hợp Codex. Hai ca này không được đánh dấu đã kiểm đạt.
- Claude Desktop: ảnh maintainer cung cấp xác nhận bản 0.9.7 bật, một skill và mô tả mới
  đã hiển thị. Maintainer bỏ kiểm model Claude khỏi điều kiện chặn; chưa có bằng chứng chạy.
- Icon Claude Desktop vẫn là icon mặc định. Gói chứa icon SVG hợp lệ; chưa xác minh client
  hiển thị icon tùy chỉnh qua đường upload ZIP. Không coi validator là bằng chứng UI đã đạt.

## Ranh giới phát hành

Kiểm local trước tích hợp: 37 kiểm thử offline đạt; validator pattern/version, validator
marketplace Claude và discovery một skill đạt. CI trên commit được push là bằng chứng riêng,
phải kiểm sau tích hợp. Publisher identity, scan và approval trên portal vẫn chưa được kiểm.

Code TypeSafe advisor, evaluation harness và dependency đã được loại khỏi repo và payload.
Skill chính chủ do host cung cấp chỉ là phần bổ trợ; không có skill thì bỏ qua im lặng.
Các spec/corpus lịch sử được giữ với nhãn ngừng triển khai, không phục hồi mã tích hợp từ đó.
