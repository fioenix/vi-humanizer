# Đổi tên sang Vietnamizer — 03/10/2026

Owner đã chốt: “OK chốt hướng `Vietnamizer` mày cập nhật mọi thứ có liên quan, bao gồm cả tên repo nhé.”

| Thành phần hiện hành | Trước | Sau |
|---|---|---|
| GitHub repo | `fioenix/vi-humanizer` | `fioenix/vietnamizer` |
| Tên hiển thị | vi-humanizer | Vietnamizer |
| Skill và plugin ID | `vi-humanizer` | `vietnamizer` |
| Marketplace/plugin | `vi-humanizer@vi-humanizer` | `vietnamizer@vietnamizer` |
| Claude Code invocation | `/vi-humanizer:vi-humanizer` | `/vietnamizer:vietnamizer` |
| Codex skill invocation | `$vi-humanizer` | `$vietnamizer` |
| Gói skill | `vi-humanizer.skill` | `vietnamizer.skill` |
| Gói Claude Org | `vi-humanizer-claude-org.zip` | `vietnamizer-claude-org.zip` |
| Gói plugin | `vi-humanizer-plugin.zip` | `vietnamizer-plugin.zip` |
| Python project metadata | `vi-humanizer-guard-eval` | `vietnamizer-guard-eval` |

Version skill vẫn là **0.9.7, chưa phát hành**. Không đổi module Python `advisor`/`guard_eval`,
quy tắc biên tập, dependency version hoặc thẩm quyền quyết định sửa văn bản.

## Những gì cố ý không đổi

- Release/tag/asset cũ, commit history, checksum và các báo cáo bằng chứng có ngày trước migration.
- Calibration quote, corpus đã khóa, policy, artifact lock và `vi-humanizer-0.7.1` trong baseline
  provenance. Đổi các byte này chỉ vì thương hiệu sẽ làm sai lineage và khóa kiểm chứng.
- Spec/plan/task đã duyệt và constitution bản 1.0.1 là hợp đồng lịch sử, vẫn áp dụng cho sản phẩm
  đổi tên; migration này không sửa nội dung hoặc hiệu lực của các hợp đồng đó.
- Đường dẫn checkout local và các worktree đang có. Git remote của checkout hiện hành trỏ tới
  repo mới; không tự di chuyển thư mục hoặc sửa checkout khác.
- Bản skill/plugin đã cài trên profile thật: cài tên mới là một migration riêng, không xóa bản
  cũ của người dùng một cách âm thầm.

Tên cũ còn xuất hiện trong những nhóm trên là có chủ ý, không phải alias runtime được hỗ trợ.

## Chuyển bản cài sau khi source mới được merge

1. Cài skill `vietnamizer` hoặc đăng ký marketplace mới rồi cài `vietnamizer@vietnamizer` theo README.
2. Mở session mới, kiểm đúng tên mới và thử biên tập một đoạn không nhạy cảm.
3. Khi bản mới hoạt động, tắt/gỡ bản cũ qua công cụ quản lý của nền tảng để tránh hai skill cùng
   tự chọn. Không xóa cả thư mục skill dùng chung bằng lệnh recursive.

Đổi tên repo không tự đổi định danh plugin đã lưu trong profile. Các asset release trước 0.9.7
vẫn là bản tên cũ; gói tên mới phải được phát hành riêng và kiểm lại checksum trước khi upload.

## Ranh giới phát hành

Đổi tên repo GitHub là thao tác đã được owner yêu cầu. Merge vào `main`, tạo release và submit
directory không được thực hiện tự động chỉ từ việc đổi tên. Nguồn/gói mới phải qua gate hiện tại;
bằng chứng kiểm của tên cũ không được trình bày như bằng chứng cài tên mới.

## Bằng chứng kiểm tên mới

- API GitHub tại cả URL cũ và mới trả `fioenix/vietnamizer`, repository ID `1316331246`, node ID
  `R_kgDOTnWe7g`; Git remote checkout hiện hành đã đổi sang repo mới.
- Test-first: 34 test đóng gói với định danh mới phát hiện layout/archive cũ; sau migration,
  34 test đạt. Bộ test offline đầy đủ cuối lượt: **195 test, OK**.
- Reviewer độc lập kiểm snapshot mới: **195 test, OK**, không có finding cụ thể cần sửa.
- Validator source v0.9.7/55 pattern, metadata distribution và cả ba archive hợp lệ.
- Skills CLI tìm đúng một skill `vietnamizer`; Claude manifest strict validation đạt.
- Cài bản nguồn và ZIP bằng profile tạm trên Codex 0.158.0 và Claude Code 2.1.287 đạt. Codex
  `plugin/read`/`skills/list` tìm đúng một `vietnamizer:vietnamizer` đang bật, canonical bytes
  trùng source và listing asset có thật. Claude marketplace/install/manifest validation đạt.
- Không gửi model request hoặc gọi TypeSafe trong test; không đổi profile cài thật.
- Wordmark Vietnamizer đã được render và xem; corpus/spec/evidence lịch sử không có diff.

SHA-256 của artifact local cuối lượt (phải tính lại cho đúng file sẽ upload nếu dựng lại):

| Artifact | SHA-256 |
|---|---|
| `vietnamizer.skill` | `d69c61b5aad3cdfde5822924a5239689583371ff712b18d65afe31b04b1716aa` |
| `vietnamizer-claude-org.zip` | `ccc0698e3083dea49480adba000593a01b562cb5c943a93c58792ede2ec888c5` |
| `vietnamizer-plugin.zip` | `44bee55e84be03da848d10d5505de578aa86dee0f2b309ac528dbb1c53977829` |

Chưa kiểm model invocation/UI desktop thật, directory approval hoặc review pháp lý độc lập.
