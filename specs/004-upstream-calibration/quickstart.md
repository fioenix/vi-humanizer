# Quickstart: Kiểm chứng upstream calibration

## 1. Baseline

```bash
python3 scripts/validate-package.py
uv run --locked --group eval python -m unittest discover -s tests -v
```

Expected trước feature: v0.8.0, 51 pattern, 129 test pass.

## 2. RED trước pattern

Thêm 24 case vào `calibration/ca-kiem-thu.md` và evidence vào `calibration/LOG.md` trước khi sửa
V/B/K. Chạy từng case với inventory 0.8.0.

Expected RED:

- ARG/QUAL/REL chưa có pattern sở hữu trực tiếp;
- AUTH marketing chưa được B8 mô tả đủ và AUTH evidence chưa có K-pattern;
- mọi ca âm vẫn phải `keep`.

## 3. Placement và GREEN

Đối chiếu `contracts/pattern-placement.md`, rồi chạy lại 24 case sau revision.

Expected:

- 12/12 positive case được flag đúng pattern;
- 12/12 negative case được giữ;
- không case nào đổi dữ kiện, quan hệ, mức chắc chắn hoặc nguồn;
- B8 và K7 không cùng sửa một câu.

## 4. Full gates

```bash
uv run --locked --group eval python -m unittest discover -s tests -v
python3 scripts/validate-package.py
npx skills add . --list
claude plugin validate .
git diff --check
./scripts/package-skill.sh
```

Expected:

- 129 test pass;
- version mới đồng bộ và validator báo 55 pattern;
- package chỉ chứa public payload;
- archive không có `specs/`, `.specify/`, `.agents/`, eval, tests hoặc artifacts.

## 5. Installed bytes

Cài lại `vi-humanizer` cho runtime dùng bản chép, rồi so SHA-256 source/installed của `SKILL.md`,
hai profile và các reference được package. Codex, Claude Code và Antigravity phải đọc cùng bản mới.
