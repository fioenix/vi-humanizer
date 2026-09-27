# Baseline trước feature 003

**Ghi nhận:** 2026-09-28
**Commit nền:** `87b1b73` (`Add v2 edit decision evaluation`)

## Hành vi và package

- `uv run --locked --group eval python -m unittest discover -s tests -v`
  - Kết quả: `Ran 129 tests ... OK`.
- `python3 scripts/validate-package.py`
  - Baseline gần nhất: `Gói vi-humanizer v0.7.1 hợp lệ, gồm 51 pattern`.
- `npx skills add . --list`
  - Baseline gần nhất: tìm thấy đúng một skill `vi-humanizer`.
- `claude plugin validate .`
  - Baseline gần nhất: `Validation passed`.

## Inventory khóa trước 003

| Artifact | Lines | Contract |
|---|---:|---|
| `SKILL.md` | 396 | tối đa 550 |
| `profiles/blog-ca-nhan.md` | 146 | tối đa 320 |
| `profiles/ky-thuat-doanh-nghiep.md` | 111 | tối đa 220 |

- Version: `0.7.1`.
- V1–V22: 22 pattern.
- T1–T6: 6 pattern.
- B1–B17: 17 pattern.
- K1–K6: 6 pattern.
- Tổng: 51 pattern.

Feature 003 phải giữ nguyên toàn bộ inventory trên; style card không được đánh số hoặc đếm như pattern.
