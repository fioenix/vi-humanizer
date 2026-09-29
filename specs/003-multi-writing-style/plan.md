# Implementation Plan: Bộ giải nhiều phong cách viết

**Branch**: `codex/003-multi-writing-style` | **Date**: 2026-09-28 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/003-multi-writing-style/spec.md`

## Summary

Thêm một bộ giải phong cách dạng tổ hợp cho workflow Markdown: xác định context theo năm chiều, giữ hai base profile hiện có, rồi chọn tối đa một trong bảy style card cho từng phần văn bản. Mỗi profile là một thư mục: `rules.md` sở hữu pattern phụ thuộc thể loại, còn `styles/` chứa đúng các card tương thích. `references/bo-giai-phong-cach.md` chỉ sở hữu resolver, precedence và registry dùng chung; style card không sở hữu pattern và không được sinh thêm dữ kiện. `SKILL.md` sở hữu thứ tự gọi cùng ranh giới protected region. Bộ kiểm thử chạy tay dùng các cặp giữ cùng dữ kiện để phát hiện rò giọng, còn validator kiểm tra registry, exact profile inventory và package nhất quán.

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
SKILL.md                                        workflow, precedence và segmentation
profiles/blog-ca-nhan/rules.md                  giới hạn profile có giọng tác giả
profiles/blog-ca-nhan/styles/                   bốn style card tương thích
profiles/ky-thuat-doanh-nghiep/rules.md         giới hạn profile trung tính
profiles/ky-thuat-doanh-nghiep/styles/          ba style card tương thích
references/bo-giai-phong-cach.md                context schema, resolver và registry
calibration/ca-kiem-thu.md                      cặp ca dương/âm và mixed-document cases
README.md                                       usage, architecture, inventory, version
AGENTS.md                                       vai trò file và hợp đồng bảo trì
scripts/validate-package.py                     registry/package consistency gates
.claude-plugin/plugin.json                      package version
```

**Structure Decision**: Giữ hai profile family thay vì tạo bảy profile độc lập. Mỗi family tách
`rules.md` khỏi các card trong `styles/`; reference registry chỉ định tuyến tới đúng file. Cách này
làm package dễ đọc mà không nhân đôi B/K hoặc trộn lựa chọn phong cách vào pattern.

## Design Decisions

1. `SKILL.md` giải protected region và base profile trước style card.
2. `references/bo-giai-phong-cach.md` là resolver và registry duy nhất; nội dung mỗi card có một nguồn chuẩn trong thư mục `styles/` của profile tương thích.
3. Một phần văn bản chỉ có một style brief. Tài liệu pha chức năng được chia thành các phần độc lập; không trộn nhiều card trong cùng phần.
4. Yêu cầu hiện tại và mô tả cụ thể có quyền cao hơn label/tone; mẫu/hồ sơ chỉ override default khi đúng người, đúng phạm vi và có bằng chứng ổn định.
5. Validator kiểm exact card/profile/path, tám field bắt buộc, consumer pointers và archive inventory từ file thật.
6. Revision cấu trúc phát hành ở `0.9.5` theo quyết định của owner; pattern inventory vẫn là 55 sau feature 004.

## Complexity Tracking

Không có vi phạm cần biện minh. Bảy card là bảy nhánh chỉ được tải sau khi resolver chọn; tách file
giảm context load mà vẫn giữ một registry duy nhất và không thêm runtime code path.
