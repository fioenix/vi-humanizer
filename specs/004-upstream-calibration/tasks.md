---

description: "Task list for upstream Vietnamese calibration"
---

# Tasks: Hiệu chuẩn khoảng trống upstream

**Input**: Design documents from `/specs/004-upstream-calibration/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/pattern-placement.md

**Tests**: TDD bắt buộc. Ca calibration và RED evidence phải tồn tại trước mọi revision V/B/K.

**Organization**: Tasks được nhóm theo user story; checkbox chỉ được đánh sau verification mới.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Có thể làm song song vì không chạm cùng file hoặc phụ thuộc task chưa xong
- **[Story]**: User story tương ứng
- Mỗi task có exact file path và deliverable kiểm được

## Phase 1: Setup

**Purpose**: Khóa baseline 0.8.0 và nguồn research trước calibration.

- [x] T001 Chạy validator cùng 129 unit test trên 0.8.0 và ghi output vào `specs/004-upstream-calibration/evidence/baseline.md`
- [x] T002 Ghi review upstream, bốn khoảng trống và hai tín hiệu backlog vào `specs/004-upstream-calibration/research.md`
- [x] T003 Gọi Jev 1.13.0 bằng Choice cho scope/coverage và ghi typed result không raw secret vào `specs/004-upstream-calibration/research.md`

---

## Phase 2: User Story 1 - Phân biệt lỗi thật với tín hiệu giống lỗi (Priority: P1) 🎯 MVP

**Goal**: Bốn giả thuyết có đủ 24 ca tiếng Việt và RED evidence trước khi sửa pattern.

**Independent Test**: Mỗi giả thuyết có đúng ba ca `flag`, ba ca `keep`, đủ context/edit boundary/rationale và không dùng threshold tần suất.

### Tests for User Story 1

- [x] T004 [US1] Thêm ARG-P01..P03 và ARG-N01..N03 cho phản biện không có đối tượng vào `calibration/ca-kiem-thu.md`
- [x] T005 [US1] Thêm QUAL-P01..P03 và QUAL-N01..N03 cho modal cùng chức năng vào `calibration/ca-kiem-thu.md`
- [x] T006 [US1] Thêm REL-P01..P03 và REL-N01..N03 cho quan hệ nguồn vào `calibration/ca-kiem-thu.md`
- [x] T007 [US1] Thêm AUTH-P01..P03 và AUTH-N01..N03 cho mượn uy tín vào `calibration/ca-kiem-thu.md`
- [x] T008 [US1] Ghi bốn mục evidence trước rule với provenance và classification vào `calibration/LOG.md`
- [x] T009 [US1] Chạy 24 ca trên inventory 0.8.0 và ghi missing-owner RED cùng 12 negative keep vào `specs/004-upstream-calibration/evidence/calibration-red.md`

**Checkpoint**: 24 case cố định; từ đây không đổi expected label để làm pattern pass.

---

## Phase 3: User Story 2 - Đặt đúng ranh giới V, B hoặc K (Priority: P2)

**Goal**: Implement chỉ những revision tách được ca dương/âm và giữ source of truth duy nhất.

**Independent Test**: 12 positive được flag đúng owner, 12 negative giữ nguyên; B8 và K7 không cùng sở hữu một use case.

### Implementation for User Story 2

- [x] T010 [US2] Chốt bốn placement decision và cross-reference theo 24 ca trong `specs/004-upstream-calibration/evidence/calibration-results.md`
- [x] T011 [US2] Thêm V23 phản biện ý không có đối tượng với đủ bốn mục vào `SKILL.md`, rồi phân vai từ B5 trong `profiles/blog-ca-nhan/rules.md`
- [x] T012 [US2] Thêm V24 chồng từ chỉ khả năng cùng chức năng với guard khác phạm vi nghĩa vào `SKILL.md`
- [x] T013 [US2] Thêm V25 làm mơ hồ quan hệ đã có với ranh giới nguồn trong phạm vi tài liệu vào `SKILL.md`
- [x] T014 [US2] Mở rộng B8 cho claim thuyết phục và thêm K7 cho attribution làm bằng chứng, kèm cross-reference trong hai file profile
- [x] T015 [US2] Đồng bộ V23–V25, K7, B8 revision và nguồn upstream trong bảng pattern của `README.md`
- [x] T016 [US2] Chạy lại 24 ca, ghi 12/12 flag và 12/12 keep cùng kiểm giữ nghĩa vào `specs/004-upstream-calibration/evidence/calibration-results.md`

**Checkpoint**: Pattern inventory là 55; mọi accepted revision có đủ Dấu hiệu/Vì sao/Sửa/Không flag.

---

## Phase 4: User Story 3 - Phát hành thay đổi đã hiệu chuẩn (Priority: P3)

**Goal**: Version, package, runtime bytes và integration phản ánh đúng inventory cuối.

**Independent Test**: Full gates chạy trên final bytes; package public sạch; source/installed hash bằng nhau; commit đã tích hợp.

### Tests and release for User Story 3

- [x] T017 [US3] Mở rộng contract validator cho bốn mục bắt buộc của mọi pattern và package payload trong `scripts/validate-package.py`
- [x] T018 [US3] Dùng noulmes chốt SemVer rồi đồng bộ `SKILL.md`, `.claude-plugin/plugin.json` và changelog `README.md`
- [x] T019 [US3] Tự rà prose mới bằng `SKILL.md`, sửa câu nén/tiếng Anh thừa mà không đổi contract trong `SKILL.md`, `profiles/`, `calibration/` và `README.md`
- [x] T020 [US3] Chạy 129 unit test, validator, skill discovery, Claude validation và diff check; ghi output/digest vào `specs/004-upstream-calibration/evidence/release-gates.md`
- [x] T021 [US3] Đóng gói, kiểm archive không có private/dev payload và ghi digest vào `specs/004-upstream-calibration/evidence/package-install.md`
- [x] T022 [US3] Cài lại skill chung cho Codex/Claude Code/Antigravity và đối chiếu SHA-256 source/installed trong `specs/004-upstream-calibration/evidence/package-install.md`
- [x] T023 [US3] Quét final diff cho dữ liệu cá nhân/tổ chức/secret/local path và chạy `git show --check` trên commit dự kiến
- [x] T024 [US3] Commit feature 004 bằng commit nguyên tử sau khi mọi gate xanh
- [x] T025 [US3] Push branch, tạo/đính kèm PR cumulative 001–004, theo dõi CI, merge và tạo tag/release version mới theo convention của repo

---

## Dependencies & Execution Order

- Setup hoàn tất trước US1.
- US1 khóa expected labels trước US2.
- US2 hoàn tất trước mọi version/package gate của US3.
- T018 phụ thuộc inventory cuối ở T016.
- T020 chạy sau T017–T019; T021–T022 dùng đúng bytes đã gate.
- T024 chỉ sau privacy/diff gate; T025 chỉ sau commit sạch.

## Parallel Opportunities

- T004–T007 tách theo giả thuyết nhưng cùng file nên thực hiện tuần tự trong session này.
- Sau case lock, V24 và V25 độc lập về semantics nhưng cùng `SKILL.md`, không sửa song song.
- Package inspection và installed-byte verification phụ thuộc cùng archive nên chạy tuần tự.

## Implementation Strategy

1. Khóa baseline và 24 ca.
2. Ghi RED trước pattern.
3. Implement theo placement, không sửa nhãn test.
4. Chỉ bump version sau 24/24 GREEN.
5. Gate, package, install, commit, PR/merge/tag.

## Notes

- TypeSafe là reviewer ngữ nghĩa, không phải prose generator hoặc policy engine.
- Không đưa example riêng của người dùng/tổ chức vào public calibration.
- Nếu cùng acceptance invariant vẫn đỏ sau hai correction độc lập, dừng trước correction thứ ba và chạy architecture checkpoint.
