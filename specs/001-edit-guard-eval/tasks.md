---
description: "Dependency-ordered implementation tasks for the edit-level guard evaluation harness"
---

# Tasks: Đánh giá guard theo từng edit

> Retired on 2026-10-03: the TypeSafe implementation and its tests were removed from the repo.
> This is a historical record, not a current task list or runnable guide. See
> `specs/005-optional-typesafe-advisor/spec.md` for the superseding owner decision.

**Input**: Design documents from `specs/001-edit-guard-eval/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/guard-eval-cli.md`, `quickstart.md`

**Tests**: Mọi hành vi mới bắt đầu bằng test đỏ theo constitution. Live TypeSafe calls không chạy
trong CI và cần owner cho phép dùng credential/quota trước khi thực hiện.

**Organization**: Task được nhóm theo ba user stories. Mỗi task tạo một deliverable có thể review
và nêu file cùng lệnh kiểm chứng cụ thể.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Có thể làm song song vì dùng file riêng và không phụ thuộc task chưa hoàn tất.
- **[Story]**: Liên kết task với user story trong `spec.md`.
- Task không có story label thuộc setup, foundation hoặc cross-cutting work.

## Global Constraints

- Skill Markdown và gói `vi-humanizer.skill` phải tiếp tục dùng được khi không cài harness.
- Host LLM chạy vi-humanizer tạo 1–3 candidate; Jev chỉ thẩm định/phân loại và không sinh prose.
- TypeSafe chỉ chạy shadow; không task nào được sửa, loại hoặc hoàn edit trong output thật.
- Dev và holdout phải tách biệt; holdout không được dùng để chỉnh questions hoặc threshold.
- Raw prose chỉ nằm trong corpus local và TypeSafe request tối thiểu; generated artifacts không
  được chứa raw prose, credential hoặc raw exception.
- Model, corpus, config, question set, policy và pricing versions phải truy ngược được.

---

## Phase 1: Setup

**Purpose**: Tạo môi trường tái lập mà không thay đổi payload của agent skill.

- [x] T001 Tạo `pyproject.toml` với Python `>=3.12,<3.13`, dependency group `eval = ["typesafe-sdk==0.7.1"]`, sinh `uv.lock`, rồi chạy `uv sync --locked --group eval` và xác nhận working tree chỉ đổi hai file này
- [x] T002 [P] Tạo package rỗng `guard_eval/__init__.py` và entrypoint `guard_eval/__main__.py` chỉ chuyển quyền cho `guard_eval.cli.main()`; không thêm business logic hoặc import TypeSafe ở package import time
- [x] T003 [P] Cập nhật `.gitignore` để bỏ qua `.venv/` và `artifacts/guard-eval/`, nhưng không bỏ qua `eval/guard/`, `pyproject.toml` hoặc `uv.lock`

**Checkpoint**: `uv sync --locked --group eval` hoàn tất; `python -c 'import guard_eval'` không gọi mạng và không cần API key.

---

## Phase 2: Foundational Contracts

**Purpose**: Khóa types, config và CLI semantics mà cả ba user stories dùng chung.

**Critical**: Không bắt đầu user story trước khi phase này pass.

- [x] T004 [P] Viết test đỏ trong `tests/guard_eval/test_models.py` cho hai `NaturalnessReason`, ba `CandidateOriginKind`, sáu `GuardDimension`, ba `GuardAction`, ba `EditDecision`, hai `CheckStatus`, ba `RunStatus`, required fields của `CandidateEdit`, `EvaluationCase`, `JudgmentSet`, `DecisionPolicy`, `EvaluationRun`, nullable decision/version fields và mọi threshold range/order trong `data-model.md`; chạy `python -m unittest tests.guard_eval.test_models -v` và xác nhận FAIL vì `guard_eval.models` chưa có contract
- [x] T005 Implement dataclass, enum, canonical JSON codec và validation errors trong `guard_eval/models.py` để T004 pass; giữ `reason_code` trong allowlist của `data-model.md` và không cho `unchecked` mang dimension scores
- [x] T006 [P] Viết test đỏ trong `tests/guard_eval/test_config.py` cho `EvaluationConfig` và `PricingSnapshot`: digest phải là `sha256:<digest>`, model/config phải khớp, timeout dương, retry hữu hạn, pricing không âm và source là HTTPS; chạy test và xác nhận FAIL
- [x] T007 Implement loader cùng canonical digest trong `guard_eval/config.py`, rồi tạo `eval/guard/evaluation-config.json` pin `jev-1.13.0` và `eval/guard/pricing.json` ghi snapshot USD cùng source/date; chạy `python -m unittest tests.guard_eval.test_config -v` và xác nhận PASS
- [x] T008 [P] Viết test đỏ trong `tests/guard_eval/test_cli.py` cho `python -m guard_eval --help`, các subcommand `validate`, `evaluate`, `fit-policy`, `report`, `all` và exit codes `0/1/2`; test phải chứng minh `validate` không import `typesafe_sdk`
- [x] T009 Implement parser và dispatch skeleton trong `guard_eval/cli.py` cùng `guard_eval/__main__.py`; subcommand chưa có handler phải trả lỗi contract rõ, không dùng placeholder success
- [x] T010 Chạy `uv run --locked python -m unittest tests.guard_eval.test_models tests.guard_eval.test_config tests.guard_eval.test_cli -v` và `python3 scripts/validate-package.py`; lưu output chứng minh foundation pass mà package skill vẫn hợp lệ

**Checkpoint**: Types, versioned config, pricing snapshot và CLI contract đã cố định; chưa có corpus hoặc network call.

---

## Phase 3: User Story 1 - Dựng corpus guard có thể kiểm chứng (Priority: P1) MVP

**Goal**: Có corpus edit-level, provenance đầy đủ, dev/holdout tách biệt và validator chạy offline.

**Independent Test**: Chạy `env -u TYPESAFE_API_KEY uv run --locked python -m guard_eval validate --manifest eval/guard/manifest.json`; lệnh exit 0, không gọi mạng và từ chối mọi fixture thiếu field, trùng split, sai digest hoặc thiếu coverage.

### Tests for User Story 1

- [x] T011 [P] [US1] Viết test đỏ và fixtures trong `tests/guard_eval/test_corpus.py` cùng `tests/guard_eval/fixtures/invalid/` cho required fields, 1–3 candidate, stable/unique candidate IDs, duplicate/no-op normalized text, `candidate_origin.kind/reference/authority` và model/workflow version khi áp dụng, consistency giữa need-to-edit/reasons/preferred option/edit decision, đủ sáu safety dimensions theo candidate, baseline mapping `keep=null`/`replace=candidate_id`/`review=candidate_id|null`, baseline/holdout maintainer authority, path `..`, file digest mismatch và corpus version mismatch
- [x] T012 [P] [US1] Mở rộng test đỏ trong `tests/guard_eval/test_corpus.py` cho fingerprint Unicode NFC/whitespace và candidate-order invariance, duplicate/formatting-only variant giữa dev/holdout, coverage `positive > 0` và `hard_negative > 0` cho hai V20 reasons lẫn từng safety dimension, cùng `none_of_candidates > 0` có ít nhất một safety-pass candidate ở mỗi split

### Implementation for User Story 1

- [x] T013 [US1] Implement JSONL loader, candidate validation, order-invariant canonical fingerprint, split leakage detection, path confinement, label consistency, coverage matrix và manifest digest trong `guard_eval/corpus.py`; chạy T011–T012 và xác nhận PASS
- [x] T014 [P] [US1] Trích case công khai có provenance từ `calibration/LOG.md`, `calibration/ca-kiem-thu.md`, `SKILL.md` và profiles, rồi ghi 1–3 candidate vào `eval/guard/dev.jsonl` với origin chính xác (`host_llm_output`, `baseline_observation` hoặc `maintainer_fixture`) cùng reference; trình labels/baseline cho maintainer xác nhận; tối thiểu có contrast V20 `đầy/đầy đủ`, `rời/rời rạc`, `rà/rà soát`, các **Không flag**, candidate overformalize và một ca expected `none_of_candidates` dù candidate vẫn pass safety
- [x] T015 [US1] Đề xuất `eval/guard/holdout.jsonl` với case V20 khác dev nhưng cùng coverage classes, origin/reference cho mọi candidate, rồi trình maintainer duyệt need-to-edit, preferred option, safety labels và baseline; chỉ ghi record có `label_source.authority="maintainer"` cùng `baseline.authority="maintainer"`, không dùng evaluator để tự tạo ground truth
- [x] T016 [US1] Tạo `eval/guard/manifest.json` với SHA-256 của hai split, computed corpus version, baseline workflow `vi-humanizer-0.7.1` và coverage requirements; chạy validator và sửa dữ liệu cho tới khi hai naturalness reasons cùng mọi safety dimension có positive/hard negative ở cả hai split
- [x] T017 [US1] Viết contract tests cho `validate` trong `tests/guard_eval/test_cli.py`, rồi implement handler trong `guard_eval/cli.py` để exit 0 khi corpus hợp lệ và exit 1 cho schema/digest/leakage error mà không đọc credential
- [x] T018 [US1] Chạy independent test của US1, toàn bộ `tests.guard_eval.test_corpus`, rồi `python3 scripts/validate-package.py`; lưu output mới và review diff corpus để xác nhận không có narrative nội bộ, dữ liệu khách hàng, định danh riêng hoặc thông tin gắn dự án với một công ty hay tổ chức

**Checkpoint**: MVP hoàn tất khi corpus hợp lệ, truy được provenance và chạy validation offline bằng một lệnh.

---

## Phase 4: User Story 2 - Quyết định có nên sửa và chọn candidate trong shadow (Priority: P2)

**Goal**: Chấm source need-to-edit, candidate preference và safety trong một TypeSafe request mà
không tác động output thật, không sinh prose và luôn giữ một result cho mỗi case.

**Independent Test**: Dùng fake adapter chạy `evaluate` trên fixture corpus; artifact có đúng một judgment cho mỗi case, cùng config/model/question versions, và case lỗi trở thành `unchecked` thay vì pass.

### Tests for User Story 2

- [x] T019 [P] [US2] Viết test đỏ trong `tests/guard_eval/test_questions.py` cho hai need-to-edit Nouls, dynamic Choice gồm `keep_original`/candidate IDs/`none_of_candidates`, sáu safety Nouls mỗi candidate, shared structured state, stable `question_set_version`, candidate-order invariance; candidate IDs/text không đổi version nhưng thay static instruction hoặc quy tắc dựng options phải đổi digest
- [x] T020 [P] [US2] Viết test đỏ trong `tests/guard_eval/test_typesafe_adapter.py` bằng fake SDK cho response đủ naturalness probabilities, Choice probabilities/confidence, safety scores/model/usage, missing key, timeout, authentication, exhausted rate limit, overload, connection error và malformed response; assert artifact chỉ có option IDs/allowlisted reason code, không có generated prose, raw exception hoặc request body
- [x] T021 [P] [US2] Viết test đỏ trong `tests/guard_eval/test_evaluator.py` cho one-request-per-candidate-group, exact case completeness, local context của gộp/tách câu, partial service failure, mixed response models, case/candidate reorder không đổi judgment semantics và Choice không được trả option ngoài allowlist

### Implementation for User Story 2

- [x] T022 [US2] Implement hai need-to-edit `Noul`, dynamic candidate `Choice`, sáu safety `Noul` mỗi candidate, structured-state allowlist và canonical order-independent question-set digest trong `guard_eval/questions.py`; không đưa case id, provenance, labels hoặc baseline vào state, không có instruction sinh hoặc sửa prose
- [x] T023 [US2] Implement lazy SDK boundary trong `guard_eval/typesafe_adapter.py` với `typesafe-sdk==0.7.1`, model/timeout/retry từ config, monotonic latency và exception-to-reason mapping; không log API key, state hoặc raw exception
- [x] T024 [US2] Implement split execution và privacy-safe raw `EvaluationRun` trong `guard_eval/evaluator.py`; mọi input case phải sinh đúng một `checked` hoặc `unchecked` judgment chứa naturalness/preference/per-candidate safety khi checked, raw run luôn ghi config/model/question versions cùng `policy_version=null` và `pricing_version=null`, unchecked làm `run_status=incomplete`, còn mixed model/digest/missing case làm `run_status=invalid`
- [x] T025 [US2] Viết test đỏ cho `evaluate` trong `tests/guard_eval/test_cli.py`, gồm exit 0 với fake dev success, exit 2 khi thiếu key/partial unchecked, exit 1 khi config/corpus/question digest lệch và từ chối `--split holdout` vì holdout chỉ chạy qua `all` với frozen policy
- [x] T026 [US2] Implement `evaluate` handler trong `guard_eval/cli.py` theo `contracts/guard-eval-cli.md`; dev evaluation chỉ nhận `--manifest` và `--config`, không đòi policy chưa được fit
- [x] T027 [US2] Chạy toàn bộ test US2 với fake adapter và independent no-key scenario từ `quickstart.md`; xác nhận output có `unchecked/missing_api_key`, không có raw prose và `python3 scripts/validate-package.py` vẫn pass

**Checkpoint**: Shadow evaluator hoàn tất về hành vi với fake/no-key paths; chưa tiêu API quota và chưa có production action.

---

## Phase 5: User Story 3 - Ra quyết định giữ hay bỏ hướng TypeSafe (Priority: P3)

**Goal**: Fit policy trên dev, tổng hợp `keep`/`replace`/`review`, đo baseline/evaluator trên holdout
và tạo quyết định tái lập `stop`, `collect_more_labels` hoặc `continue_shadow`.

**Independent Test**: Dùng hai fixture runs, một candidate thắng baseline và một candidate không thắng; cùng input phải tạo cùng policy/report, đúng decision, metrics và privacy constraints.

### Tests for User Story 3

- [x] T028 [P] [US3] Viết test đỏ trong `tests/guard_eval/test_policy.py` cho exhaustive observed-value search của need-to-edit, Choice confidence/margin và safety thresholds; deterministic `keep`/`replace(candidate_id)`/`review`; `none_of_candidates` luôn route `review`; fitter không được giảm review rate bằng cách replace case có ground truth `none_of_candidates`; không bao giờ replace bằng text ngoài candidates; tie order theo `research.md`; từ chối holdout/unchecked/mixed-config dev run
- [x] T029 [P] [US3] Viết test đỏ trong `tests/guard_eval/test_report.py` cho baseline/evaluator need-to-edit recall, unnecessary-edit rate, candidate-choice accuracy chỉ trên expected replace, no-acceptable-candidate recall, harmful-edit recall, valid-edit false-block rate, safety false-accept rate, review rate, service errors, latency p50/p95, tokens, estimated cost, per-reason/per-dimension coverage và limitations
- [x] T030 [P] [US3] Mở rộng `tests/guard_eval/test_report.py` với transition tách run status khỏi decision: invalid → `invalid/null`, unchecked → `incomplete/null`, metric bắt buộc có mẫu số 0 → `complete/collect_more_labels`; nếu cả ba metric need-to-edit/candidate-choice/no-acceptable đều không tăng, một trong ba giảm, unnecessary-edit/valid-edit false-block/safety false accept tăng hoặc harmful recall giảm → `complete/stop`; còn đạt FR-015 → `complete/continue_shadow`; assert candidate reorder giữ nguyên decision và report không chứa forbidden raw-prose keys

### Implementation for User Story 3

- [x] T031 [US3] Implement deterministic threshold fitting, per-candidate `GuardAction`, final `EditDecision` routing và canonical `policy_version` trong `guard_eval/policy.py`; policy tham chiếu dev corpus/config/question/model versions, không đọc holdout và mọi replace chỉ mang candidate ID có thật
- [x] T032 [US3] Implement need-to-edit, unnecessary-edit, candidate-choice, no-acceptable-candidate metrics cùng harmful-edit recall, valid-edit false-block, safety false accept, pricing, coverage, limitations, version binding, integrity gates và go/no-go transition trong `guard_eval/report.py`; giữ `decision=null` cho invalid/incomplete, chỉ dùng `collect_more_labels` cho complete run có metric bắt buộc với mẫu số 0, chỉ đọc IDs/digests/judgments/labels local và không serialize raw prose/provenance
- [x] T033 [US3] Viết CLI contract tests đỏ cho `fit-policy`, `report` và `all` trong `tests/guard_eval/test_cli.py`, gồm `all = validate → evaluate → report`, không fit policy ngầm và không overwrite `eval/guard/policy.json`
- [x] T034 [US3] Implement `fit-policy`, `report` và `all` handlers trong `guard_eval/cli.py` với arguments đúng `contracts/guard-eval-cli.md` và exit codes 0/1/2
- [x] T035 [US3] Sau khi owner cho phép dùng TypeSafe credential/quota, chạy dev evaluation thật, tạo `artifacts/guard-eval/candidate-policy.json`, trình metrics/threshold cho maintainer review rồi mới ghi policy đã duyệt vào `eval/guard/policy.json`
- [x] T036 [US3] Sau khi policy và holdout labels đã được duyệt cùng owner cho phép live call, chạy holdout bằng command `all`, giữ raw run dưới `artifacts/guard-eval/holdout/`, ghi sanitized report vào `specs/001-edit-guard-eval/evidence/holdout-report.json` và không chỉnh question, threshold hoặc corpus sau khi đọc kết quả
- [x] T037 [US3] Chạy `python -m unittest tests.guard_eval.test_policy tests.guard_eval.test_report tests.guard_eval.test_cli -v` trên fixtures trong `tests/guard_eval/fixtures/` để tái lập positive V20, correct-simple-word hard negative, `none_of_candidates`, candidate reorder, nhánh thắng/không thắng, thiếu mẫu và incomplete/invalid; đối chiếu live report nếu có, xác nhận chỉ run complete mới có đúng một decision và không gọi `continue_shadow` là production-ready

**Checkpoint**: Có decision artifact hợp lệ hoặc có bằng chứng rõ vì sao phải dừng/thu thập thêm nhãn. Không có production blocking.

---

## Phase 6: Polish and Cross-Cutting Verification

**Purpose**: Tích hợp maintenance workflow, CI offline và release gates mà không mở rộng feature.

- [x] T038 [P] Cập nhật `README.md` với cách cài dependency group, candidate origin, cấu trúc `guard_eval/`, command offline/live và ranh giới không đóng gói; cập nhật `AGENTS.md` với vai trò của corpus, policy, pricing và artifacts
- [x] T039 [P] Cập nhật `.github/workflows/validate.yml` để cài `uv`, chạy `uv sync --locked --group eval` và toàn bộ test với fake adapter; workflow không có secret, không gọi TypeSafe và vẫn giữ ba package/plugin gates hiện tại
- [x] T040 Chạy tuần tự mọi scenario offline trong `specs/001-edit-guard-eval/quickstart.md`, gồm no-key exit 2 và artifact privacy scan; sửa chỉ các lỗi thuộc contract đã duyệt
- [x] T041 Chạy full verification `uv run --locked python -m unittest discover -s tests -p 'test_*.py' -v`, `python3 scripts/validate-package.py`, `npx skills add . --list` và `claude plugin validate .`; lưu output mới thay vì suy từ CI/config
- [x] T042 Review toàn bộ diff theo `specs/001-edit-guard-eval/spec.md`, `plan.md`, constitution và requirements coverage; xác nhận mọi changed line thuộc feature, không có raw prose trong generated artifacts được track và implementation được commit hoặc ghi rõ trạng thái parked

---

## Dependencies and Execution Order

### Phase dependencies

- **Setup**: bắt đầu ngay.
- **Foundational**: phụ thuộc Setup; chặn mọi user story.
- **US1**: phụ thuộc Foundational; là MVP và cung cấp corpus cho US2/US3.
- **US2**: phụ thuộc US1 vì evaluator cần corpus hợp lệ.
- **US3**: phụ thuộc US2 vì policy/report cần judgment artifacts.
- **Polish**: phụ thuộc các user stories được chọn; live tasks T035–T036 vẫn cần owner authorization.

### User story dependency graph

```text
Setup → Foundation → US1 corpus → US2 shadow evaluator → US3 decision report → Polish
```

US1 có thể ship nội bộ như MVP validator/corpus mà chưa cài TypeSafe. US2 hoàn tất behavioral
paths bằng fake evaluator ngay cả khi chưa được phép dùng quota. US3 chỉ hoàn tất live evidence sau
các owner gates ghi trong T035–T036.

### Within each story

- Viết test và xác nhận RED trước implementation tương ứng.
- Models/config trước loader; loader trước evaluator; evaluator trước policy/report.
- Không sửa test expectation để hợp thức hóa output sai; thay đổi contract phải quay lại plan/spec.
- Mỗi checkpoint cần output mới của lệnh kiểm tra.

### Parallel opportunities

- T002 và T003 chạy song song sau T001.
- T004, T006 và T008 chạy song song; mỗi cặp implementation chờ test đỏ tương ứng.
- T011 và T012 chạy song song; T014 có thể bắt đầu trong khi T013 đang được implement.
- T019, T020 và T021 chạy song song; T022–T024 thực hiện sau test tương ứng.
- T028, T029 và T030 chạy song song; T031–T032 thực hiện sau test tương ứng.
- T038 và T039 chạy song song sau core implementation.

## Parallel Examples

### User Story 1

```text
Task T011: Viết schema/action/integrity corpus tests và invalid fixtures.
Task T012: Viết fingerprint/leakage/coverage tests.
Task T014: Curate dev cases từ public repo evidence trong file dữ liệu riêng.
```

### User Story 2

```text
Task T019: Khóa question battery và question-set digest.
Task T020: Khóa SDK error mapping và privacy behavior.
Task T021: Khóa evaluator completeness và mixed-model behavior.
```

### User Story 3

```text
Task T028: Khóa deterministic policy fitting.
Task T029: Khóa metric, latency, usage và cost calculations.
Task T030: Khóa decision transitions và report privacy.
```

## Implementation Strategy

### MVP first

1. Hoàn tất T001–T010.
2. Hoàn tất T011–T018 cho US1.
3. Dừng và chạy independent US1 validation.
4. Review corpus/provenance trước khi cài hoặc gọi TypeSafe.

### Incremental delivery

1. **US1**: corpus và validator offline.
2. **US2**: shadow evaluator với fake/no-key verification; live call vẫn khóa.
3. **US3**: policy/report deterministic, rồi mới xin phép live dev và holdout calls.
4. **Polish**: docs, CI, full gates và integration status.

## Notes

- `[P]` chỉ dùng khi task sửa file khác và không phụ thuộc task chưa xong.
- Generated files trong `artifacts/guard-eval/` không commit.
- `eval/guard/policy.json` chỉ commit sau dev fit và maintainer review.
- Không task nào cấp quyền merge, publish, live quota use hoặc production integration.
- Nếu cùng một invariant vẫn đỏ sau hai correction độc lập, dừng trước correction thứ ba và chạy
  architecture checkpoint theo `AGENTS.md`.
