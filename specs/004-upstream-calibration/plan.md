# Implementation Plan: Hiệu chuẩn khoảng trống upstream

**Branch**: `codex/004-upstream-calibration` | **Date**: 2026-09-28 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/004-upstream-calibration/spec.md`

## Summary

Hiệu chuẩn bốn giả thuyết từ `blader/humanizer` 3.0.0 bằng 24 ca tiếng Việt có nhãn, ghi bằng
chứng vào calibration trước khi sửa rule, rồi phát hành đúng phần qua ba pattern V mới, một pattern
K mới và phần mở rộng B8. TypeSafe chỉ là ý kiến ngữ nghĩa thứ hai cho placement; maintainer giữ
quyền quyết định và skill runtime vẫn là Markdown offline.

## Technical Context

**Language/Version**: Markdown; Python 3.12 cho validator/eval hiện có; shell cho package gates

**Primary Dependencies**: Không có dependency runtime; TypeSafe SDK chỉ dùng một lần ở research lane

**Storage**: File trong repo; không có database

**Testing**: 24 ca chạy tay trong `calibration/ca-kiem-thu.md`; `uv ... unittest` 129 test;
`scripts/validate-package.py`; plugin/package/install gates

**Target Platform**: Agent Skills và Claude Code plugin đọc Markdown

**Project Type**: Open-source agent skill

**Performance Goals**: Không áp dụng; thay đổi không thêm runtime call

**Constraints**: Offline ở runtime; không secret/raw prose trong artifact eval; pattern đủ bốn mục;
line budget; V/T/B/K liên tục; ví dụ public trung tính

**Scale/Scope**: 4 giả thuyết, 24 ca bắt buộc, 3 V-pattern mới, 1 K-pattern mới, 1 revision B8

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle/gate | Trước research | Sau design |
|---|---|---|
| Bằng chứng tiếng Việt trước convention | Pass: upstream chỉ là giả thuyết | Pass: 24 ca được yêu cầu trước pattern |
| Giữ nghĩa và giọng | Pass: spec khóa dữ kiện, quan hệ, mức chắc chắn | Pass: contract có edit boundary và ca âm |
| Tách V khỏi profile | Pass: placement là deliverable riêng | Pass: B8/K7 được phân vai; V23–V25 không phụ thuộc kênh |
| Hiệu chỉnh từ bằng chứng có nhãn | Pass: log trước rule | Pass: case schema và decision record có provenance |
| Markdown tự đứng được | Pass: TypeSafe chỉ research | Pass: không có dependency runtime |
| Version/inventory/package gates | Pass: thuộc US3 | Pass: quickstart khóa mọi gate |

Không có vi phạm constitution cần biện minh.

## Project Structure

### Documentation (this feature)

```text
specs/004-upstream-calibration/
├── plan.md
├── spec.md
├── research.md
├── data-model.md
├── contracts/
│   └── pattern-placement.md
├── quickstart.md
├── checklists/
│   └── requirements.md
├── evidence/
│   ├── calibration-red.md
│   ├── calibration-results.md
│   ├── release-gates.md
│   └── package-install.md
└── tasks.md
```

### Source Code (repository root)

```text
SKILL.md                              V23–V25 và version
profiles/blog-ca-nhan.md              mở rộng B8, phân vai K7
profiles/ky-thuat-doanh-nghiep.md     K7, phân vai B8
calibration/LOG.md                    bằng chứng trước khi sửa rule
calibration/ca-kiem-thu.md            24 ca dương/âm
README.md                             inventory, nguồn, changelog
.claude-plugin/plugin.json            version
scripts/validate-package.py           inventory/contract/package gates
tests/                                129 test nền không đổi hành vi
```

**Structure Decision**: Giữ kiến trúc Markdown hiện có. Không thêm service, corpus runtime hoặc
adapter mới; mọi evidence phát triển nằm trong spec/calibration và package chỉ lấy payload public.

## Complexity Tracking

Không có violation.
