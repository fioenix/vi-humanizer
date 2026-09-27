# Bằng chứng package và bản cài 003

**Ngày chạy**: 2026-09-28
**Archive**: `dist/vi-humanizer.skill`
**SHA-256 archive**: `fbe9bb24378eab1a049039ed7a7f9b35a635bb50b3d43154b4b045b4c51e1b85`

## Payload

Archive có đúng tám file public:

```text
vi-humanizer/SKILL.md
vi-humanizer/profiles/blog-ca-nhan.md
vi-humanizer/profiles/ky-thuat-doanh-nghiep.md
vi-humanizer/references/han-viet-thuan-viet.md
vi-humanizer/references/bo-giai-phong-cach.md
vi-humanizer/references/bang-tra-cuu.md
vi-humanizer/calibration/LOG.md
vi-humanizer/calibration/ca-kiem-thu.md
```

Không có `specs/`, `.specify/`, `.agents/`, `eval/`, `guard_eval/`, `tests/` hoặc `artifacts/`.

## Bản cài runtime

Đã chạy:

```text
npx skills add . --skill vi-humanizer --agent '*' --global --yes
```

Công cụ cài bản chung vào `~/.agents/skills/vi-humanizer`. Codex và Claude Code cùng trỏ tới bản
chung đó; Antigravity dùng bản universal cùng vị trí. Eve và PromptScript không hỗ trợ cài skill
global nên công cụ bỏ qua hai runtime này.

| File | SHA-256 source và installed |
|---|---|
| `SKILL.md` | `284b5872dbb3ae4eecf065605cda718bb454b765e3876fb994e2b1001c82e4a3` |
| `profiles/blog-ca-nhan.md` | `82dd3cee3e7dd5cf10c64a53cf36c51dce23746d3addf6b0c753f6f6cd6ccc9c` |
| `profiles/ky-thuat-doanh-nghiep.md` | `7381a472fbe6bbe6e2951fc6a2621556159a565d69aa6566f3702a2fe99e8e24` |
| `references/bo-giai-phong-cach.md` | `3287b3da62780c2e8a393e2252312bd4ad7c9306596fa4d54d48e3ed6102c27b` |

Bốn cặp hash bằng nhau; bản cài không còn lệch source 0.8.0.
