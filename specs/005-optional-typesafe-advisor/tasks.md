---

description: "Nhiệm vụ triển khai cố vấn TypeSafe tùy chọn"
---

# Tasks: Cố vấn TypeSafe tùy chọn

**Input**: Design documents from `/specs/005-optional-typesafe-advisor/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/advisor-cli.md`, `quickstart.md`

**Tests**: Mọi hành vi runtime và packaging mới phải bắt đầu bằng test đỏ, theo constitution và TDD.

**Organization**: Các task được nhóm theo ba user story; từng story có tiêu chí kiểm tra độc lập.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Có thể làm song song vì khác file và không phụ thuộc task chưa xong
- **[Story]**: User story mà task phục vụ

## Phase 1: Setup

**Purpose**: Khóa quyết định release và chuẩn bị cấu trúc test trước khi viết runtime.

- [ ] T001 Ghi quyết định owner dùng version `0.9.6` và trạng thái Approved trong `specs/005-optional-typesafe-advisor/spec.md`
- [ ] T002 Tạo package test namespace và fixture V20 trong `tests/advisor/__init__.py`, `tests/advisor/fixtures/valid-v20.json` và `tests/advisor/fixtures/protected-canary.json`

---

## Phase 2: Foundational

**Purpose**: Khóa schema, content binding và question contract dùng chung cho mọi user story.

- [ ] T003 [P] Viết test đỏ cho exact schema, NFC, stable ID, candidate map 1–3 phần tử, duplicate rejection và `case_binding` trong `tests/advisor/test_models.py`
- [ ] T004 [P] Viết test đỏ cho stable-key state path, candidate-order-independent digest, exact question inventory và runtime/v2 digest independence trong `tests/advisor/test_questions.py`
- [ ] T005 Chạy riêng T003–T004 và lưu bằng chứng chúng fail vì chưa có package `advisor`
- [ ] T006 Viết schema, normalization, canonical binding và sanitized result builders trong `advisor/models.py` và `advisor/__init__.py`
- [ ] T007 Viết question set V20, probe fixture, stable-key paths và version digests trong `advisor/questions.py`
- [ ] T008 Chạy `tests.advisor.test_models` và `tests.advisor.test_questions` tới khi xanh mà không đổi frozen bytes trong `guard_eval/v2/` hoặc `eval/guard/v2/`

**Checkpoint**: Input/output boundary và question identity đã test độc lập, chưa có network client.

---

## Phase 3: User Story 1 — Core vẫn chạy khi không có TypeSafe (Priority: P1) 🎯 MVP

**Goal**: Không key hoặc external service lỗi thì advisor trả trạng thái rõ ràng và core Markdown không phụ thuộc adapter.

**Independent Test**: `env -u TYPESAFE_API_KEY python3 -m advisor probe` trả exit 2, JSON `core_only/missing_api_key`, không mở network và package core vẫn validate.

- [ ] T009 [P] [US1] Viết test đỏ cho missing/blank key, no-network guarantee và sanitized failure mapping trong `tests/advisor/test_client.py`
- [ ] T010 [P] [US1] Viết test đỏ cho CLI exit 1/2, canonical stdout và không phản chiếu prose/canary/exception trong `tests/advisor/test_cli.py`
- [ ] T011 [US1] Chạy riêng T009–T010 trong `tests/advisor/` và xác nhận fail vì client/CLI chưa tồn tại
- [ ] T012 [US1] Viết fixed-endpoint client với timeout 8 giây, một attempt, environment-only key và allowlisted reason codes trong `advisor/client.py`
- [ ] T013 [US1] Viết entrypoint `probe`, `assess`, `rank`, exit codes và JSON stdin/stdout trong `advisor/cli.py`, `advisor/__main__.py`
- [ ] T014 [US1] Chạy test US1 cùng `python3 scripts/validate-package.py`; xác nhận no-key path không gọi transport và core vẫn hợp lệ

**Checkpoint**: User không dùng TypeSafe không phải cài dependency và không bị chặn.

---

## Phase 4: User Story 2 — Opt-in và xác minh readiness (Priority: P2)

**Goal**: Probe thật mới tạo `advisor_verified`; config/key presence không được tính là bằng chứng.

**Independent Test**: Fake transport chứng minh response typed đúng model tạo verified, còn auth/429/529/timeout/malformed/model mismatch đều exit 2 với reason code an toàn.

- [ ] T015 [P] [US2] Mở rộng test đỏ cho HTTP bearer request, fixed endpoint, typed probe response, usage/timestamp/model validation và error mapping trong `tests/advisor/test_client.py`
- [ ] T016 [P] [US2] Viết contract test đỏ cho output `AdvisorCapabilityObservation` và probe không chứa raw provider body trong `tests/advisor/test_cli.py`
- [ ] T017 [US2] Hoàn thiện HTTP request/response parser và probe readiness trong `advisor/client.py`, `advisor/models.py`, `advisor/cli.py`
- [ ] T018 [US2] Viết decision path setup, privacy, capability limits và live probe opt-in trong `README.md` và `references/typesafe-advisor.md`
- [ ] T019 [US2] Chạy test US2 trong `tests/advisor/test_client.py` và `tests/advisor/test_cli.py` bằng fake transport; không chạy live quota khi chưa có một opt-in riêng cho lượt live

**Checkpoint**: Người dùng phân biệt được core-only, unchecked và verified trong tối đa ba phút.

---

## Phase 5: User Story 3 — Thẩm định edit V20 (Priority: P3)

**Goal**: Jev trả các signal tuyệt đối hoặc ranking cho candidate đã có; Agent giữ quyền quyết định và viết câu cuối.

**Independent Test**: Assess/rank fake end-to-end trả exact maps, binding và versions; stale/mismatched result bị bỏ; output không có prose hay action.

- [ ] T020 [P] [US3] Viết test đỏ cho assess exact issue/component/safety maps, content binding, stale/model mismatch và không có action/prose trong `tests/advisor/test_cli.py`
- [ ] T021 [P] [US3] Viết test đỏ cho rank shortlist 2–3 stable IDs, exact probability keys, canonical order và từ chối `keep_original`/unknown/duplicate trong `tests/advisor/test_cli.py`
- [ ] T022 [US3] Triển khai assess/rank request builders và typed response validation trong `advisor/questions.py`, `advisor/client.py`, `advisor/models.py`, `advisor/cli.py`
- [ ] T023 [US3] Tích hợp capability route, thứ tự candidate-before-Jev, giới hạn V20 và Agent authority vào `SKILL.md` và `references/typesafe-advisor.md`
- [ ] T024 [US3] Chạy `tests/advisor/test_questions.py` và `tests/advisor/test_cli.py` nhiều lần với target ở đầu/giữa/cuối batch; xác nhận result bind đúng stable ID ở mọi lần

**Checkpoint**: Jev hỗ trợ phán đoán nhưng không sinh prose hoặc quyết định thay Agent.

---

## Phase 6: Packaging, release và local installation

**Purpose**: Ship cùng bytes đã test trong cả hai artifact, cập nhật local runtime và chuẩn bị ZIP Claude Org.

- [ ] T025 Viết test đỏ cho exact public advisor inventory, archive byte parity, không secret/test/eval và root layout trong `tests/test_package_security.py`
- [ ] T026 Thêm `advisor/` và `references/typesafe-advisor.md` vào payload allowlist/copy logic trong `scripts/validate-package.py` và `scripts/package-skill.sh`
- [ ] T027 Đồng bộ version `0.9.6` và changelog trong `SKILL.md`, `README.md`, `.claude-plugin/plugin.json`; cập nhật `AGENTS.md` theo cây file thật
- [ ] T028 Chạy toàn bộ unit/integration suite, validator, `git diff --check`, `npx skills add . --list` và `claude plugin validate .`
- [ ] T029 Đóng gói `dist/vi-humanizer.skill` và `dist/vi-humanizer-claude-org.zip`, kiểm inventory, byte parity và secret scan
- [ ] T030 Cài lại skill local vào `/Users/fioenix/.codex/skills/vi-humanizer/` và các runtime không phải Claude đang trỏ tới đó; đối chiếu version/bytes đã cài
- [ ] T031 Review diff của `advisor/`, `SKILL.md`, `README.md`, `references/typesafe-advisor.md`, packaging và tests theo spec/plan/security boundary; sửa finding rồi chạy lại toàn bộ gate

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup → Foundational → US1 → US2 → US3 → Packaging/release.
- US2 và US3 dùng client/schema của US1 nên không chạy trước US1.
- Package chỉ được sinh sau khi source, docs và version đã khóa.

### User Story Dependencies

- **US1 (P1)**: Chỉ phụ thuộc foundational; đây là MVP bắt buộc.
- **US2 (P2)**: Phụ thuộc no-key/failure semantics của US1.
- **US3 (P3)**: Phụ thuộc exact schema và verified client; ranking vẫn là lượt riêng sau absolute assess.

### Parallel Opportunities

- T003 và T004 có thể viết song song.
- T009 và T010 có thể viết song song.
- T015 và T016 có thể viết song song.
- T020 và T021 có thể viết song song.

## Implementation Strategy

1. Khóa schema/question identity trước để network code không định nghĩa ngược contract.
2. Ship no-key/fail-open MVP trước, rồi mới thêm verified probe.
3. Chỉ sau đó thêm assess/rank và tích hợp vào instruction layer.
4. Không chạy live TypeSafe trong CI hoặc mặc định; fake transport là evidence bắt buộc.
5. Release chỉ từ exact source bytes đã qua full gate và được cài lại local để readback.
