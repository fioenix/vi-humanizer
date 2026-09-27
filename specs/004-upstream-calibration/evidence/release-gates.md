# Release gates: vi-humanizer 0.9.0

Ngày chạy: 2026-09-28

Các lệnh dưới đây được chạy trên cùng working tree sau khi chốt version và tự rà câu chữ.

| Gate | Kết quả đọc từ output mới |
|---|---|
| `uv run --locked --group eval python -m unittest discover -s tests -v` | PASS; 129 test chạy trong 0,844 giây; kết thúc bằng `OK` |
| `python3 scripts/validate-package.py` | PASS; `Gói vi-humanizer v0.9.0 hợp lệ, gồm 55 pattern` |
| `npx skills add . --list` | PASS; tìm thấy đúng một skill `vi-humanizer` từ đường dẫn repo hiện tại |
| `claude plugin validate .` | PASS; marketplace manifest hợp lệ |
| `git diff --check` | PASS; exit 0, không có output |

Test nền vẫn ghi `complete all run: decision=collect_more_labels` cho evaluation gate 002. Đây là
trạng thái shadow đã duyệt, không phải lỗi của feature 004 và không cho phép bật tự động thay văn bản.

## SHA-256 của các file phát hành chính

```text
a97d3cdbe89139ff565bde4ade6cdd3620d741f1374725f6d48b9f0316394b45  SKILL.md
ba0ec90d7e5b90dc2d6ee22d91e4ce7ed2bb2b7c4a4f2fec8985c334e3b28af2  profiles/blog-ca-nhan.md
fdb822f26c202926aa5078f9fa3a2c4d64bd95a98bb675d6b8257d477e7aa64d  profiles/ky-thuat-doanh-nghiep.md
3cebe59acd9383c0a63b9e32f6a1173ba4689f0f9c882dee5123b3ea15e4d1a1  README.md
d94963e8666af63d6dcffe364075232d59f15c329a5823e477930fb2c1d1e182  .claude-plugin/plugin.json
a5e686cd05db71caf81a48ae6fd08f1394986bd743a49b10bd07b72b43273611  scripts/validate-package.py
91d375b8886e689da3d58ce0d707dc31002969e7309b8913dd05fa4ec48bb7a0  calibration/LOG.md
d674f521614033c268c95c8d19b3b0039e62f5c3f5fc2fabcc334266edccf7b0  calibration/ca-kiem-thu.md
```
