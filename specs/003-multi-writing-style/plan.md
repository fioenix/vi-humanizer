# Implementation Plan: Bộ giải nhiều phong cách viết

**Branch**: `codex/003-multi-writing-style` | **Date**: 2026-09-28 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/003-multi-writing-style/spec.md`

## Summary

Thêm một bộ giải phong cách dạng tổ hợp cho workflow Markdown: xác định context theo năm chiều, giữ hai base profile hiện có, rồi chọn tối đa một trong bảy style card cho từng phần văn bản. Style card nằm trong một reference public, không sở hữu pattern và không được sinh thêm dữ kiện. `SKILL.md` sở hữu thứ tự ưu tiên và ranh giới protected region; profile tiếp tục sở hữu lỗi phụ thuộc thể loại. Bộ kiểm thử chạy tay dùng các cặp giữ cùng dữ kiện để phát hiện rò giọng, còn validator kiểm tra registry/inventory/package nhất quán.

## Technical Context

**Language/Version**: Markdown; Python 3 cho validator hiện có

**Primary Dependencies**: Không thêm dependency; dùng package/validation tooling sẵn có

**Storage**: File Markdown trong `SKILL.md`, `profiles/`, `references/`, `calibration/`; không có database

**Testing**: `scripts/validate-package.py`, ca chạy tay trong `calibration/ca-kiem-thu.md`, `npx skills add . --list`, `claude plugin validate .`, `git diff --check`

**Target Platform**: Agent runtime tương thích skill Markdown và Claude Code plugin

**Project Type**: Agent skill public, không build và không cần network khi dùng

**Performance Goals**: Mỗi phần văn bản chọn một base profile và tối đa một style card; không mở thêm external call hay context file không liên quan

**Constraints**: `SKILL.md` ≤ 550 dòng; profile blog ≤ 320 dòng; profile kỹ thuật ≤ 220 dòng; pattern V/T/B/K không đổi; payload public không chứa thông tin cá nhân/tổ chức; feature 002 không đi vào runtime

**Scale/Scope**: 7 style card, 5 chiều context, 2 base profile, 1 nhóm protected region và tối thiểu 14 ca calibration dương/âm

## Constitution Check

*GATE: Passed before research; re-checked after design.*

| Principle | Pre-design check | Post-design check |
|---|---|---|
| I. Bằng chứng tiếng Việt đứng trước convention | Style không được gọi là lỗi; research dùng phạm vi tiếng Việt và mapping upstream chỉ làm prior art | Contract giữ pattern inventory nguyên vẹn; ca calibration kiểm lựa chọn style chứ không thêm lỗi |
| II. Giữ nghĩa và giọng trước khi làm câu hay hơn | Resolver bắt buộc giữ năm chốt chặn và không sinh dữ kiện | Mỗi card có mục không được tự thêm; cặp test giữ cùng nội dung |
| III. Tách quy tắc chung khỏi profile thể loại | Hai base profile tiếp tục sở hữu pattern; style card chỉ giải lựa chọn hợp lệ | Reference mới không có số hiệu V/T/B/K và không thay đổi pattern |
| IV. Hiệu chỉnh từ bằng chứng có nhãn | Mỗi style cần ca dương và chống rò giọng | Quickstart và data model khóa label authority/provenance trung tính |
| V. Giữ skill Markdown tự đứng được | Không dùng TypeSafe/002 runtime | Thiết kế chỉ dùng Markdown và validator offline |
| Package/data constraints | Version, inventory và line budget đổi đồng bộ trong release task | Validator sẽ kiểm style registry và payload; không có dữ liệu riêng |

Không có constitution violation hoặc complexity exception.

## Project Structure

### Documentation (this feature)

```text
specs/003-multi-writing-style/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── style-resolution.md
├── checklists/
│   └── requirements.md
└── tasks.md
```

### Source and validation (repository root)

```text
SKILL.md                                workflow, precedence và segmentation
profiles/blog-ca-nhan.md                giới hạn profile có giọng tác giả
profiles/ky-thuat-doanh-nghiep.md       giới hạn profile trung tính
references/bo-giai-phong-cach.md        context schema, resolver và 7 style card
calibration/ca-kiem-thu.md              cặp ca dương/âm và mixed-document cases
README.md                               usage, architecture, registry inventory, version
AGENTS.md                               vai trò file và hợp đồng bảo trì
scripts/validate-package.py             deterministic registry/package consistency gates
.claude-plugin/plugin.json              package version
```

**Structure Decision**: Dùng một reference registry thay vì tạo bảy profile. Profile tiếp tục chứa pattern phụ thuộc thể loại; style card chỉ mô tả lựa chọn hợp lệ về xưng hô, nhịp, register, thuật ngữ và cách kết. Cách này tránh nhân đôi B/K và giữ `SKILL.md` dưới line budget.

## Design Decisions

1. `SKILL.md` giải protected region và base profile trước style card.
2. `references/bo-giai-phong-cach.md` là registry duy nhất của bảy card; README chỉ liệt kê và trỏ tới, không sao chép toàn bộ nội dung.
3. Một phần văn bản chỉ có một style brief. Tài liệu pha chức năng được chia thành các phần độc lập; không trộn nhiều card trong cùng phần.
4. Yêu cầu hiện tại và mô tả cụ thể có quyền cao hơn label/tone; mẫu/hồ sơ chỉ override default khi đúng người, đúng phạm vi và có bằng chứng ổn định.
5. Validator kiểm các heading/card ID chuẩn xuất hiện đúng một lần, `SKILL.md`/README trỏ đúng registry và package chứa reference mới.
6. Release bump ở cuối feature sau khi test style matrix xanh; không thay pattern count 51.

## Complexity Tracking

Không có vi phạm cần biện minh. Reference mới là một nguồn chuẩn duy nhất thay vì bảy file/profile và không thêm runtime code path.
