# Kiểm tra public OSS ngày 02/10/2026

## Kết luận về Git history

Giữ history và các tag đã public. Quét mirror lấy mới từ GitHub không phát hiện credential hoặc
private key. Finding duy nhất của phép quét nội dung bổ sung là đường dẫn cài Codex skill của
maintainer trong các phiên bản cũ của `specs/005-optional-typesafe-advisor/tasks.md`, dòng 103.
Đường dẫn đã được loại khỏi source hiện tại; nó không chứa credential hoặc dữ liệu khách hàng.

Rewrite chỉ để loại dấu vết môi trường này sẽ đổi commit/tag đã chia sẻ và vẫn cần xử lý các ref
PR, cache hoặc fork riêng. Bằng chứng hiện tại chưa cho thấy lợi ích đủ để thực hiện việc đó.

## Phạm vi kiểm tra history

Snapshot public được kiểm trước cleanup có main tại
`3920e4ba22acc09499d6f46fe78cf59facc7962e`, tag `v0.7.1`, `v0.9.0`, `v0.9.6` và head của PR #1–#5.
Mirror gồm 9 ref, 115 commit và 457 blob, tổng nội dung blob 5.875.379 byte.

Đã thực hiện:

- Clone mirror từ URL HTTPS công khai của repo; không dùng danh sách branch local làm bằng chứng
  cho nội dung đã public.
- Chạy Gitleaks 8.30.1 với rules mặc định, `--log-opts='--all --full-history'`, decoding mặc định
  và `--redact=100`: exit 0, 0 finding. Binary Darwin arm64 được đối chiếu SHA-256 với checksum
  upstream trước khi chạy.
- Đọc mọi blob reachable trong mirror và quét mẫu đường dẫn máy, private key header, email trong
  file và tên tổ chức ngoài phạm vi. Bốn phiên bản blob của cùng `tasks.md` còn đường dẫn cài đặt
  nói trên; không có file khớp các mẫu còn lại.
- Kiểm metadata commit: không có commit message khớp mẫu credential đã kiểm, không có metadata
  chứa tên employer ngoài phạm vi. Có hai email identity trong metadata commit.
- Quét riêng tất cả local refs bằng Gitleaks: exit 0, 0 finding. Một backup tip local không có
  trong mirror public; truy vấn commit đó qua GitHub API không xác thực trả 404.

Không in credential hoặc private path vào báo cáo. Raw scan reports và log được giữ local dưới
`output/`, không commit.

Đây là bằng chứng về các ref GitHub công khai đã lấy được tại thời điểm kiểm tra. Nó không chứng
minh sự vắng mặt của secret trong fork, bản clone của người khác, cache hoặc object không còn được
advertise. Nếu phát hiện credential thật về sau, cần xử lý credential trước rồi lập phạm vi xoá
history cụ thể theo [hướng dẫn của GitHub](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository).

## Cleanup source và package

- Bỏ Git tracking của generated Codex skills và Spec Kit init/integration state; giữ file local
  hiện có cho maintainer. Constitution, tooling chung, specs, corpus, evidence và tests tiếp tục
  được track.
- Đưa ignore của scratch output, raw evaluation runs, environment, agent local state và cache vào
  root `.gitignore`, để clone khác không phụ thuộc global ignore hoặc `.git/info/exclude` của máy.
- Thêm `CONTRIBUTING.md` với bootstrap Spec Kit v1.0.5 và lệnh kiểm offline. Init options cũng là
  state local vì integration installer ghi lại file này.
- Đưa `LICENSE` vào cả hai archive và yêu cầu validator từ chối source thiếu notice. Tooling
  Spec Kit được giữ attribution MIT tại `.specify/LICENSE`.
- CI chặn tracked files khớp ignore rules, dựng và validate cả hai archive; Claude Code validation
  được pin ở 2.1.287, phiên bản đã kiểm ở checkout này.
- Chuẩn bị patch v0.9.7 cho thay đổi package; giữ nguyên byte của release v0.9.6 đã public.

## Bằng chứng local trước review

- Hai test mới được chạy đỏ trước khi sửa package: archive thiếu licence và packager nhận source
  không có licence. Sau sửa, cả hai pass.
- Full offline suite: 183 test, kết thúc `OK`.
- `python3 scripts/validate-package.py`: v0.9.7 hợp lệ, 55 pattern.
- `./scripts/package-skill.sh`: cả hai archive pass inventory, privacy và byte-parity validation.
- `npx --yes skills@1.5.20 add . --list`: tìm đúng một skill `vi-humanizer`.
- `claude plugin validate .`: validation passed; `git diff --check`: sạch.

Các kết quả trên là kiểm local trước review. Merge, CI trên main và GitHub Release là bằng chứng
riêng; báo cáo này không tự khẳng định các bước đó đã xảy ra.
