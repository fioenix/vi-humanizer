# Package và installed bytes: vi-humanizer 0.9.0

Ngày chạy: 2026-09-28

## Archive

- Lệnh: `./scripts/package-skill.sh`
- File: `dist/vi-humanizer.skill`
- Kích thước: 78.659 byte
- SHA-256: `941c34c964f514aed4e8385fcc5a5bdae73a9cdb74f26c3350badc9e289cb825`
- Số entry: 12, gồm thư mục gốc, `SKILL.md`, hai profile, ba reference và hai file calibration.
- Entry cấm: 0. Archive không chứa `.specify/`, `.agents/`, `specs/`, `tests/`, `eval/`,
  `guard_eval/`, `guard_eval_v2/`, `artifacts/` hoặc `.git/`.

## Cài đặt chung

Lệnh `npx skills add . --skill vi-humanizer --agent '*' --global --yes` cài một bản chung tại
`~/.agents/skills/vi-humanizer`. Skills CLI báo Codex và Antigravity dùng bản chung, còn Claude Code
đọc qua symlink. Hai runtime ngoài phạm vi là Eve và PromptScript không hỗ trợ cài skill toàn cục.

Đường dẫn đã kiểm:

- Codex: `~/.codex/skills/vi-humanizer` → `~/.claude/skills/vi-humanizer`
- Claude Code: `~/.claude/skills/vi-humanizer` → `~/.agents/skills/vi-humanizer`
- Antigravity: `~/.gemini/skills/vi-humanizer` → `~/.agents/skills/vi-humanizer`

## Đối chiếu SHA-256 source và bản cài

```text
MATCH  a97d3cdbe89139ff565bde4ade6cdd3620d741f1374725f6d48b9f0316394b45  SKILL.md
MATCH  ba0ec90d7e5b90dc2d6ee22d91e4ce7ed2bb2b7c4a4f2fec8985c334e3b28af2  profiles/blog-ca-nhan.md
MATCH  fdb822f26c202926aa5078f9fa3a2c4d64bd95a98bb675d6b8257d477e7aa64d  profiles/ky-thuat-doanh-nghiep.md
MATCH  3c674df085e784560a402604b8607f13e648f67177b1832bd7ac4acf39b442fb  references/bang-tra-cuu.md
MATCH  3287b3da62780c2e8a393e2252312bd4ad7c9306596fa4d54d48e3ed6102c27b  references/bo-giai-phong-cach.md
MATCH  9b75276be84b811e752a5094eb2034f7bece429fa0022be242c4996581d45a28  references/han-viet-thuan-viet.md
MATCH  91d375b8886e689da3d58ce0d707dc31002969e7309b8913dd05fa4ec48bb7a0  calibration/LOG.md
MATCH  d674f521614033c268c95c8d19b3b0039e62f5c3f5fc2fabcc334266edccf7b0  calibration/ca-kiem-thu.md
```

`SKILL.md` đọc qua đường dẫn Antigravity và bản chung cùng có SHA-256
`a97d3cdbe89139ff565bde4ade6cdd3620d741f1374725f6d48b9f0316394b45`.
