---

description: "Task list for the multi writing style resolver"
---

# Tasks: Bộ giải nhiều phong cách viết

**Input**: Design documents from `/specs/003-multi-writing-style/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/style-resolution.md

**Tests**: TDD bắt buộc. Validator contract và ca calibration phải được thêm/chạy RED trước khi instruction tương ứng được triển khai.

**Organization**: Tasks được nhóm theo user story để mỗi phần có thể kiểm chứng độc lập.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Có thể làm song song vì khác file và không phụ thuộc task chưa xong
- **[Story]**: User story tương ứng
- Mỗi task ghi exact file path và verification

## Phase 1: Setup

**Purpose**: Khóa baseline và biến style registry thành contract có thể fail độc lập.

- [x] T001 Ghi baseline pattern/version/line-budget và xác nhận 129 test hiện có xanh trước 003 trong `specs/003-multi-writing-style/evidence/baseline.md`
- [x] T002 Viết validator contract RED yêu cầu `references/bo-giai-phong-cach.md`, đúng bảy canonical card ID và consumer markers trong `scripts/validate-package.py`; chạy để chứng minh fail trước implementation

---

## Phase 2: Foundational

**Purpose**: Tạo source of truth và governance dùng chung cho cả ba user story.

**⚠️ CRITICAL**: Không sửa route trong `SKILL.md` trước khi registry schema và ranh giới profile được chốt.

- [x] T003 Tạo schema Style Context, Base Profile, Style Brief, precedence và card contract trong `references/bo-giai-phong-cach.md` mà chưa thêm pattern V/T/B/K
- [x] T004 [P] Cập nhật vai trò file, source-of-truth và hợp đồng style-card-not-pattern trong `AGENTS.md`
- [x] T005 Chạy `python3 scripts/validate-package.py` và ghi output vào `specs/003-multi-writing-style/evidence/foundation-red.md` để chứng minh chỉ còn fail vì thiếu/không đủ bảy card

**Checkpoint**: Registry contract tồn tại, public, offline và không chạm pattern inventory.

---

## Phase 3: User Story 1 - Chọn đúng phong cách (Priority: P1) 🎯 MVP

**Goal**: Bảy mục đích viết được định tuyến bằng hai base profile và một style card, không còn ép vào hai tone.

**Independent Test**: Bảy cặp cùng dữ kiện chọn đúng card và không import lựa chọn của card đối chứng.

### Tests for User Story 1

- [x] T006 [US1] Thêm tối thiểu 14 ca RED, mỗi card có một ca dương và một ca chống rò giọng giữ cùng content invariant, trong `calibration/ca-kiem-thu.md`

### Implementation for User Story 1

- [x] T007 [US1] Viết đủ bảy card `ke-trai-nghiem`, `phoi-hop-cong-viec`, `chuyen-mon-cong-khai`, `marketing-thuyet-phuc`, `huong-dan-ky-thuat`, `van-hanh-doanh-nghiep`, `hoc-thuat-phan-tich` với mọi field bắt buộc trong `references/bo-giai-phong-cach.md`
- [x] T008 [US1] Thay route hai-tone bằng bước thu thập năm chiều, chọn base profile và đọc đúng một style card trong `SKILL.md`
- [x] T009 [P] [US1] Ghi ranh giới card tương thích và những lựa chọn profile vẫn sở hữu trong `profiles/blog-ca-nhan/rules.md`
- [x] T010 [P] [US1] Ghi ranh giới card tương thích và những lựa chọn profile vẫn sở hữu trong `profiles/ky-thuat-doanh-nghiep/rules.md`
- [x] T011 [US1] Bổ sung usage, kiến trúc và bảng bảy style card không lặp toàn bộ registry trong `README.md`
- [x] T012 [US1] Chạy và ghi kết quả 14 ca US1 vào `specs/003-multi-writing-style/evidence/us1-style-matrix.md`; mọi case phải giữ facts/intent và không rò giọng

**Checkpoint**: User Story 1 dùng được độc lập; validator nhận đúng bảy card và pattern count vẫn 51.

---

## Phase 4: User Story 2 - Giải xung đột tín hiệu (Priority: P2)

**Goal**: Yêu cầu hiện tại, thể loại, mẫu/hồ sơ và defaults luôn được giải theo một precedence duy nhất.

**Independent Test**: Các ca xung đột cho cùng kết quả bất kể thứ tự tài liệu được đọc; chỉ ambiguity đổi quan hệ mới hỏi.

### Tests for User Story 2

- [x] T013 [US2] Thêm ca RED cho current-request-over-memory, sample-over-default, label-vs-description, single-observation và unknown-address trong `calibration/ca-kiem-thu.md`

### Implementation for User Story 2

- [x] T014 [US2] Implement precedence, `preserve-current` và `ask-one-question` trong `references/bo-giai-phong-cach.md`
- [x] T015 [US2] Đồng bộ workflow, memory scope và rule “mô tả cụ thể thắng nhãn tone” trong `SKILL.md`
- [x] T016 [US2] Chạy ca xung đột và ghi bằng chứng vào `specs/003-multi-writing-style/evidence/us2-precedence.md`

**Checkpoint**: User Story 1 và 2 cùng pass; resolver không tự đổi đại từ khi thiếu vai vế.

---

## Phase 5: User Story 3 - Tài liệu pha nhiều chức năng (Priority: P3)

**Goal**: Tài liệu hỗn hợp được chia theo chức năng; protected region giữ nguyên và style không rò giữa các phần.

**Independent Test**: Fixture ghép có narrator prose, hướng dẫn, code, bảng, trích dẫn và CTA giữ nguyên byte ở protected region, còn mỗi phần văn xuôi chọn đúng brief.

### Tests for User Story 3

- [x] T017 [US3] Thêm mixed-document RED case và exact protected-region assertions trong `calibration/ca-kiem-thu.md`

### Implementation for User Story 3

- [x] T018 [US3] Implement functional segmentation, one-card-per-segment và protected-region exit trong `references/bo-giai-phong-cach.md`
- [x] T019 [US3] Đưa segmentation trước pattern scan và giữ output contract không lộ style label trong `SKILL.md`
- [x] T020 [US3] Chạy mixed-document case và ghi byte-preservation/style-leakage evidence vào `specs/003-multi-writing-style/evidence/us3-mixed-document.md`

**Checkpoint**: Cả ba user story pass độc lập và khi ghép lại.

---

## Phase 6: Polish & Release Gates

**Purpose**: Đồng bộ public package, tự rà tiếng Việt và tạo bằng chứng release.

- [x] T021 Tự rà toàn bộ prose mới bằng `SKILL.md`, sửa câu nén/thuật ngữ Anh không cần thiết nhưng không đổi contract trong `SKILL.md`, `profiles/`, `references/bo-giai-phong-cach.md` và `README.md`
- [x] T022 Đồng bộ version feature release trong `SKILL.md`, `.claude-plugin/plugin.json` và mục lịch sử mới nhất của `README.md`; giữ pattern count 51
- [x] T023 Cập nhật validator cho line budget, exact seven-card inventory, consumer markers và package payload trong `scripts/validate-package.py`
- [x] T024 Chạy quickstart/full tests/package gates và ghi command/output/digest vào `specs/003-multi-writing-style/evidence/release-gates.md`
- [x] T025 Kiểm tra package archive chỉ chứa public skill payload và so SHA-256 source/installed bytes theo `specs/003-multi-writing-style/quickstart.md`
- [x] T026 Rà `git diff --check`, kiểm không có dữ liệu cá nhân/tổ chức/secret và commit feature 003 bằng commit nguyên tử

---

## Dependencies & Execution Order

### Phase Dependencies

- Phase 1 không có dependency.
- Phase 2 phụ thuộc T002 RED và chặn mọi user story.
- US1 phụ thuộc Phase 2.
- US2 phụ thuộc registry/card của US1 nhưng test được riêng bằng ca precedence.
- US3 phụ thuộc route cơ bản của US1, không phụ thuộc implementation detail của US2.
- Polish phụ thuộc cả ba story pass.

### Within Each User Story

- Calibration/test case MUST tồn tại và thể hiện RED trước instruction tương ứng.
- Registry source of truth trước consumer updates.
- Evidence chỉ được ghi sau khi thật sự chạy case/gate.
- Checkbox không thay command output.

### Parallel Opportunities

- T004 có thể chạy song song với T003.
- T009 và T010 có thể chạy song song sau T008 contract đã rõ.
- Documentation/evidence ở file khác có thể chuẩn bị song song, nhưng verification chờ implementation tương ứng.

---

## Parallel Example: User Story 1

```text
Task T009: Cập nhật ranh giới card trong profiles/blog-ca-nhan/rules.md
Task T010: Cập nhật ranh giới card trong profiles/ky-thuat-doanh-nghiep/rules.md
```

---

## Implementation Strategy

### MVP First

1. Làm Phase 1 và 2, giữ validator RED có chủ đích.
2. Thêm calibration US1 trước instruction.
3. Implement bảy card + route US1.
4. Dừng và chạy ma trận 14 ca trước khi thêm precedence/mixed-document.

### Incremental Delivery

1. US1: phân biệt bảy mục đích viết.
2. US2: cố định cách giải xung đột.
3. US3: mở rộng sang tài liệu hỗn hợp.
4. Bump version và release gates chỉ sau khi cả ba xanh.

## Notes

- Không gọi TypeSafe/Jev để chạy resolver; noulmes chỉ được dùng như decision check của agent bảo trì.
- Không sửa pattern inventory trong 003.
- Không đưa ví dụ riêng của người dùng hay tổ chức vào public calibration.
- Nếu cùng một acceptance invariant vẫn đỏ sau hai correction, dừng và chạy architecture checkpoint trước correction thứ ba.

---

## Phase 7: Revision 0.9.5 - Profile/style hierarchy

**Goal**: Public package cho thấy rõ hai profile family và bảy style card mà không nhập pattern, style và reference thành một nguồn sự thật.

- [x] T027 Viết package regression test RED yêu cầu mỗi profile có `rules.md`, đúng các style card tương thích trong `styles/` và không còn hai profile file phẳng.
- [x] T028 Chuyển B/K rules vào hai profile directory, tách bảy card khỏi registry thành bảy file và giữ resolver/precedence dùng chung trong `references/bo-giai-phong-cach.md`.
- [x] T029 Cập nhật mọi consumer trong `SKILL.md`, `README.md`, `AGENTS.md`, calibration, validator và Spec Kit artifact đang mô tả cấu trúc hiện hành.
- [x] T030 Viết validator regression test RED cho style card thiếu field, rồi kiểm exact path, owner, field contract và archive inventory từ file thật.
- [x] T031 Đồng bộ version `0.9.5`, chạy full tests cùng ba package gate, đóng gói lại hai artifact và so byte source/archive cho toàn bộ public payload.
- [x] T032 Rà diff, secret/private-data scan, ghi evidence revision và tạo commit nguyên tử; không push nếu chưa có lệnh riêng của owner.
