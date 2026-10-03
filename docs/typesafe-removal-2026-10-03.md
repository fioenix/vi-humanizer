# Bỏ mã TypeSafe khỏi Vietnamizer

Owner đã thay quyết định giữ source nghiên cứu ngày 03/10/2026 bằng yêu cầu bỏ mã TypeSafe
khỏi repo. Bản 0.9.7 vẫn chưa phát hành; thay đổi đang local, chưa commit, push hoặc submit.

## Phạm vi đã áp dụng

- Gỡ CLI `advisor/`, harness `guard_eval/` v1/v2 và kiểm thử/fixture dành riêng cho chúng.
- Gỡ `pyproject.toml`, `uv.lock` và dependency `typesafe-sdk`; CI dùng Python standard library
  để kiểm đóng gói, không cài SDK hoặc cấu hình API key.
- Bỏ hướng dẫn chạy CLI nghiên cứu; đồng bộ README, privacy, contributor docs và AGENTS.
- Vietnamizer chỉ tận dụng skill TypeSafe chính chủ được host cung cấp khi thẩm định hữu ích
  và có quyền gửi dữ liệu; không quét máy, tự cài, đọc key hoặc dựng connector.
- Owner làm rõ thêm: harness không cung cấp TypeSafe thì bỏ qua im lặng, không nhắc agent hoặc
  người dùng cài/thiết lập. Đây là phần bổ trợ tùy chọn, không phải dependency hoặc lỗi cần xử lý.
- Giữ pattern, style card, version và branding đã duyệt.

Corpus/config ở `eval/guard/` và đặc tả/báo cáo cũ vẫn là hồ sơ lịch sử đã ngừng dùng. Chúng
không phải mã chạy, cấu hình hiện hành hoặc bằng chứng TypeSafe cải thiện chất lượng hiện tại.
Quickstart và task ledger của các feature đã ngừng dùng có cảnh báo; số test trong báo cáo cũ
không được hiểu là số test của suite hiện hành.

## Kiểm chứng mới

Các kết quả suite, review và cài profile dưới đây thuộc snapshot gỡ mã trước lần làm rõ về
bỏ qua im lặng. Sau lần làm rõ, validator repo và dựng ba archive đã chạy lại thành công
(`output/typesafe-optional-package.log`); chưa chạy model để kiểm hành vi im lặng thực tế.

- `python3 -m unittest discover -s tests -p 'test_*.py' -v`: 36 test, OK (11.273 giây).
  Log local: `output/typesafe-removal-tests.log`. Số test giảm do bỏ suite của hệ thống đã gỡ,
  không phải chạy bỏ qua các test còn tồn tại.
- Validator repo: 0.9.7, 55 pattern hợp lệ; plugin metadata và cả ba archive được dựng lại.
- Claude marketplace validator và strict plugin validator: qua.
- Skills CLI 1.5.20 discovery: đúng một skill Vietnamizer.
- Cài archive vào profile Claude tạm: một skill, không agent/hook/MCP/LSP; profile được dọn
  sau khi kiểm. Log: `output/typesafe-removal-install.log`.
- `git diff --check`: qua. Không đổi asset hoặc manifest branding.
- Review độc lập đối chiếu diff và archive cuối: không thấy Critical, Important hoặc Minor;
  không phán quyết hành vi model, dịch vụ live, UI hoặc directory eligibility chưa được kiểm.
- Validator phụ `quick_validate.py` của skill-creator chưa chạy được vì Python thiếu PyYAML;
  không cài thêm dependency. Validator repo và hai validator Claude nêu trên đã chạy thành công.

Các phép kiểm trên không gọi model hoặc TypeSafe; chúng không chứng minh hành vi biên tập
thực tế, chất lượng thẩm định hay giao diện sáng/tối trên marketplace. Chưa kiểm portal,
publisher eligibility hoặc niêm yết chính thức. Các archive tên cũ trong `dist/` và môi trường
local bị ignore không được xóa trong thay đổi source này; không dùng chúng để phát hành.
Một số thư mục vừa gỡ source còn cache `.pyc` bị ignore trên máy; chúng không thuộc Git hay
archive mới. “Gỡ mã khỏi repo” ở đây nói về source public, không phải xóa mọi byte lịch sử local.

| Archive mới | SHA256 |
|---|---|
| vietnamizer.skill | e4e3edfc7d4a86ac31e9011b8d5765d631a5f6d2dbcffd88b49ca33af1b090f6 |
| vietnamizer-claude-org.zip | 6035cad87b3e3bbf9a6f62ff963591c129924be516a290b122c35a3e657b9819 |
| vietnamizer-plugin.zip | 517f19797525f338a768dc89e905c6ba9caf565e428453d2799ad25901ec95e5 |
