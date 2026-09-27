# Tasks: Cổng quyết định sửa hay giữ v2

**Input**: Design documents from `specs/002-edit-decision-gate/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`,
`contracts/guard-eval-v2-cli.md`, `quickstart.md`

**Tests**: Mọi contract và acceptance behavior phải có test đỏ trước implementation. Live TypeSafe
không chạy trong CI; fake adapter chứng minh orchestration offline.

**Organization**: Tasks được nhóm theo user story và theo thứ tự dependency. Mỗi task tạo một diff
hoặc output kiểm chứng được; task live/manual giữ nguyên unchecked cho tới đúng approval gate.

**Revision status**: T001–T050 ghi lại implementation/candidate đầu tiên. Candidate đó đã bị
maintainer reject; các tên `Decision*`/`action` trong task đã hoàn tất là lịch sử của contract cũ,
không phải contract cần giữ. Execution hiện tại bắt đầu ở T051 và mọi approval gắn với T049 chỉ có
giá trị lịch sử, không được tái dùng sau khi question/config/corpus digest đổi.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Có thể làm song song vì khác file và không phụ thuộc task chưa xong.
- **[Story]**: User story trong `spec.md`.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Mở namespace v2 mà không thay public contract v1.

- [X] T001 Tạo package skeleton `guard_eval/v2/__init__.py` và `guard_eval/v2/__main__.py` để `python -m guard_eval.v2` có entry point riêng
- [X] T002 [P] Tạo test package và fixture directories tại `tests/guard_eval_v2/__init__.py` và `tests/guard_eval_v2/fixtures/`
- [X] T003 Bổ sung đúng pattern `artifacts/guard-eval-v2/` vào `.gitignore` và chứng minh `scripts/package-skill.sh` không đóng gói harness

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Typed schema, digest, config và privacy contracts dùng chung cho cả ba stories.

**⚠️ CRITICAL**: Không bắt đầu user story trước khi phase này pass.

- [X] T004 [P] Viết test đỏ cho enums, required fields, canonical digest và serialization không chứa prose trong `tests/guard_eval_v2/test_models.py`
- [X] T005 Implement enums, canonical digest, `DecisionCaseV2`, `CandidateV2`, `JudgmentRunV2` và `DecisionRunV2` trong `guard_eval/v2/models.py`; giữ constraints: 1–3 candidate, exact component/safety keys, `policy_version=null` ở raw run
- [X] T006 [P] Viết test đỏ cho recursive key denylist, raw-string canary và allowlisted service reason trong `tests/guard_eval_v2/test_privacy.py`
- [X] T007 Implement schema allowlist và privacy validation trong `guard_eval/v2/privacy.py`; cấm raw prose, labels, provenance, request/response body, secret và raw exception
- [X] T008 [P] Viết test đỏ cho exact model pin, dual question-set digests, retry/timeout và pricing snapshot trong `tests/guard_eval_v2/test_config.py`
- [X] T009 Implement `EvaluationConfigV2` và pricing loader/self-digest trong `guard_eval/v2/config.py`; từ chối alias model, digest mismatch và negative price
- [X] T010 Chạy test foundational targeted bằng `uv run --locked python -m unittest tests.guard_eval_v2.test_models tests.guard_eval_v2.test_privacy tests.guard_eval_v2.test_config -v`
- [X] T011 Cập nhật `specs/002-edit-decision-gate/plan.md` project tree nếu implementation cần file contract mới, không thay design semantics đã duyệt

**Checkpoint**: Schema/config/privacy v2 pass độc lập, chưa gọi TypeSafe.

---

## Phase 3: User Story 1 - Quyết định đúng giữ, xem lại hay thay (Priority: P1) 🎯 MVP

**Goal**: Jev chỉ trả absolute/ranking judgments; policy tất định tạo shortlist và shadow
recommendation `keep/review/replace`; host Agent sở hữu quyết định biên tập và câu chữ cuối.

**Independent Test**: Fake judgments cho source tốt, source cần sửa có candidate đạt, không candidate
đạt, component không chắc và ranking không rõ phải tạo đúng recommendation/reason; Choice không thể
làm candidate không đủ chuẩn nhận recommendation `replace`.

### Tests for User Story 1

- [X] T012 [P] [US1] Viết test đỏ cho request allowlist, hai source-issue Nouls, ba component Nouls/candidate và sáu safety Nouls/candidate trong `tests/guard_eval_v2/test_questions.py`
- [X] T013 [P] [US1] Viết test đỏ chứng minh Choice chỉ nhận shortlist ≥2, không có `keep_original`/`none_of_candidates`, và 0/1 candidate không tạo request trong `tests/guard_eval_v2/test_questions.py`
- [X] T014 [P] [US1] Viết test đỏ cho adapter checked/unchecked, exact observed model, two-stage usage và không lưu raw SDK response trong `tests/guard_eval_v2/test_typesafe_adapter.py`
- [X] T015 [P] [US1] Viết test đỏ cho truth table `keep/review/replace`, uncertainty bands, derived acceptability, safety gate và deterministic replay trong `tests/guard_eval_v2/test_policy.py`
- [X] T016 [P] [US1] Viết test đỏ cho raw run completeness, mixed-model invalidation và ranking chỉ chạy sau shortlist trong `tests/guard_eval_v2/test_evaluator.py`
- [X] T017 [P] [US1] Viết CLI contract test đỏ cho `validate`, `evaluate-dev`, `fit-policy`, `apply-policy`, exit 0/1/2 và missing-key behavior trong `tests/guard_eval_v2/test_cli.py`

### Implementation for User Story 1

- [X] T018 [US1] Implement absolute/ranking question builders và stable question-set digests trong `guard_eval/v2/questions.py`
- [X] T019 [US1] Implement lazy TypeSafe boundary, typed response parser, retry mapping và usage aggregation trong `guard_eval/v2/typesafe_adapter.py`
- [X] T020 [US1] Implement absolute evaluation, shortlist-dependent ranking và exact case completeness trong `guard_eval/v2/evaluator.py`
- [X] T021 [US1] Implement two-band source/component thresholds, safety actions, policy fit order và deterministic action transition trong `guard_eval/v2/policy.py`
- [X] T022 [US1] Implement `validate`, `evaluate-dev`, `fit-policy` và `apply-policy` orchestration trong `guard_eval/v2/cli.py`
- [X] T023 [US1] Chạy toàn bộ targeted US1 tests và lưu output mới bằng `uv run --locked python -m unittest tests.guard_eval_v2.test_questions tests.guard_eval_v2.test_typesafe_adapter tests.guard_eval_v2.test_evaluator tests.guard_eval_v2.test_policy tests.guard_eval_v2.test_cli -v`

**Checkpoint**: US1 hoạt động hoàn toàn với fake evaluator và không phụ thuộc corpus holdout.

---

## Phase 4: User Story 2 - Học từ v1 mà không làm bẩn holdout (Priority: P2)

**Goal**: Promote failure v1 vào dev có lineage, khóa bytes v1 và chống holdout leakage xuyên iteration.

**Independent Test**: Validator pass với promoted dev case nguyên fingerprint; fail khi đổi semantic
content, đưa promoted case vào holdout, trùng historical fingerprint hoặc làm drift một byte v1.

### Tests for User Story 2

- [X] T024 [P] [US2] Viết test đỏ cho v2 corpus schema, case fingerprint khác corpus version và dev/holdout split invariants trong `tests/guard_eval_v2/test_corpus.py`
- [X] T025 [P] [US2] Viết test đỏ cho `PromotionLineage` resolve path/digest/case/fingerprint và chỉ hợp lệ ở dev trong `tests/guard_eval_v2/test_corpus.py`
- [X] T026 [P] [US2] Viết test đỏ cho historical holdout registry, sealed holdout không bị đọc ở dev validate và full validation chỉ sau policy gate trong `tests/guard_eval_v2/test_corpus.py`
- [X] T027 [P] [US2] Viết test đỏ cho exact v1 byte-lock manifest và phát hiện một-byte drift trong `tests/guard_eval_v2/test_v1_compat.py`
- [X] T028 [P] [US2] Viết test đỏ cho projection v2→v1 không mang labels/provenance và frozen v1 policy áp được lên evaluation corpus khác trong `tests/guard_eval_v2/test_v1_compat.py`

### Implementation for User Story 2

- [X] T029 [US2] Implement corpus loaders, semantic fingerprint, corpus digest, lineage resolution, dev validation và sealed-holdout gate trong `guard_eval/v2/corpus.py`
- [X] T030 [US2] Implement historical registry validation, v1 artifact byte lock và v1 request projection/compat policy replay trong `guard_eval/v2/corpus.py` và `guard_eval/v2/evaluator.py`
- [X] T031 [US2] Tạo `eval/guard/v2/v1-artifact-lock.json` và `eval/guard/v2/observed-holdouts.json` từ bytes/provenance hiện tại, không sửa file feature 001
- [X] T032 [US2] Chạy targeted US2 tests và byte-diff gate cho `eval/guard/`, `specs/001-edit-guard-eval/evidence/` bằng command ghi trong `quickstart.md`

**Checkpoint**: V1 byte-stable; holdout v2 vẫn sealed và chưa được đọc.

---

## Phase 5: User Story 3 - Ra quyết định bằng metric có mẫu số (Priority: P3)

**Goal**: So v1/v2 trên cùng holdout bằng metric có numerator/denominator/direction và conservative
go/no-go.

**Independent Test**: Synthetic paired runs chứng minh insufficient denominator ra
`collect_more_labels`, protected regression/harmful auto-replace ra `stop`, safe strict improvement
ra `continue_shadow`, còn incomplete/mismatched runs không có decision.

### Tests for User Story 3

- [X] T033 [P] [US3] Viết test đỏ cho `MetricValue`, case-vs-candidate units, denominator status và improvement delta đúng chiều trong `tests/guard_eval_v2/test_report.py`
- [X] T034 [P] [US3] Viết test đỏ cho coverage ≥5 ở keep/review/replace/no-acceptable/harmful và prediction-support của keep precision trong `tests/guard_eval_v2/test_report.py`
- [X] T035 [P] [US3] Viết test đỏ cho hard invariant, protected regression, strict-improvement rule và incomplete/invalid null decision trong `tests/guard_eval_v2/test_report.py`
- [X] T036 [P] [US3] Viết CLI integration test đỏ cho offline `compare` và paired `holdout` orchestration không fit/overwrite policy trong `tests/guard_eval_v2/test_cli.py`

### Implementation for User Story 3

- [X] T037 [US3] Implement metric calculators, coverage gates, disagreement rows, usage/cost aggregation và report digest trong `guard_eval/v2/report.py`
- [X] T038 [US3] Implement offline `compare` command và exact paired-run/case-set/model validation trong `guard_eval/v2/cli.py`
- [X] T039 [US3] Implement `holdout` orchestration với pre-open frozen-policy gate, full holdout validation, separate v1/v2 runs và no tracked-file mutation trong `guard_eval/v2/cli.py`
- [X] T040 [US3] Chạy targeted US3 tests bằng `uv run --locked python -m unittest tests.guard_eval_v2.test_report tests.guard_eval_v2.test_cli -v`

**Checkpoint**: Paired comparison hoạt động hoàn toàn với fixtures/fake evaluator; chưa mở real holdout.

---

## Phase 6: Corpus, Documentation & Cross-Cutting Validation

**Purpose**: Chuẩn bị development evidence và chứng minh feature không làm đổi skill/package.

- [X] T041 Viết test đỏ cho manifest/config/dev corpus/pricing fixtures trung tính và minimum coverage diagnostics trong `tests/guard_eval_v2/test_corpus_artifacts.py`
- [X] T042 Tạo `eval/guard/v2/manifest.json`, `evaluation-config.json`, `pricing.json` và `dev.jsonl` bằng nội dung công khai hoặc fixture trung tính; không tạo/open real holdout trước gate
- [X] T043 Promote exact observed v1 holdout failures vào dev v2 với lineage trong `eval/guard/v2/dev.jsonl` và chứng minh semantic fingerprint không đổi
- [X] T044 Cập nhật `README.md` và `AGENTS.md` chỉ cho architecture/evaluation maintenance facts thực sự thay đổi; không thêm organization-specific data hoặc đổi package feature claims
- [X] T045 Rà `specs/002-edit-decision-gate/quickstart.md` theo CLI thực tế và thêm lệnh exact byte-lock/privacy/full-test verification
- [X] T046 Chạy full offline suite, `git diff --check`, `python3 scripts/validate-package.py`, privacy scan và xác nhận không có tracked raw artifacts
- [X] T047 Chạy `npx skills add . --list` và `claude plugin validate .`; đọc output thay vì suy luận từ config

---

## Phase 7: Candidate đầu tiên và quyết định reject

**Purpose**: Giữ bằng chứng của candidate đầu tiên đúng như nó đã xảy ra; không biến rejection
thành approval hoặc sửa artifact lịch sử.

- [X] T048 Tạo dev label proposal sanitized tại `specs/002-edit-decision-gate/evidence/dev-label-proposal.json` để maintainer review, không chứa raw prose
- [X] T049 Maintainer duyệt dev labels và ghi approval reference trong `specs/002-edit-decision-gate/evidence/dev-label-approval.json`
- [X] T050 Sau approval T049, chạy live dev evaluation/fit qua secret injection và ghi sanitized candidate-policy artifact trong `specs/002-edit-decision-gate/evidence/policy-candidate.json`
- [X] T051 Ghi quyết định maintainer reject candidate 6/9 và ca unacceptable nhận `replace` thành artifact sanitized bất biến tại `specs/002-edit-decision-gate/evidence/policy-candidate-review.json`; không chứa raw prose và không freeze `eval/guard/v2/policy.json`

---

## Phase 8: User Story 1 Revision - Agent authority và recommendation contract (Priority: P1)

**Goal**: Đổi toàn bộ contract v2 chưa phát hành sang `Recommendation*`, làm rõ câu hỏi giữ sắc
thái và khiến fitter fail closed trước mọi unacceptable/harmful replace recommendation.

**Independent Test**: Regression fixture của candidate bị reject phải đỏ trên code cũ; sau revision,
fitter từ chối mọi threshold tuple tạo `replace` cho candidate `expected_acceptable=false`, output
chỉ dùng recommendation terminology và không thành phần nào sinh hoặc sửa prose.

### Tests for User Story 1 revision

- [X] T052 [US1] Viết test đỏ khóa rename `RecommendationKind`, `CandidateAssessment`, `RecommendationCaseV2`, `RecommendationPolicyV2`, `PolicyRecommendationV2`, `RecommendationRunV2`, `expected_recommendation`, `recommendation`, `candidate_assessments` và `recommendation_run_digest` trong `tests/guard_eval_v2/test_models.py`
- [X] T053 [US1] Viết regression test đỏ tái hiện candidate `expected_acceptable=false` từng nhận recommendation `replace`, đồng thời yêu cầu fitter không trả policy candidate khi mọi threshold tuple vi phạm hard invariant trong `tests/guard_eval_v2/test_policy.py`
- [X] T054 [US1] Viết test đỏ cho `preserves_meaning_and_nuance`: hoàn chỉnh tổ hợp từ vựng còn thiếu phải khác với thay bằng từ gần nghĩa làm lệch sắc thái; request vẫn chỉ chấm candidate đã cung cấp trong `tests/guard_eval_v2/test_questions.py`
- [X] T055 [US1] Viết CLI contract test đỏ cho option/output `--v1-recommendations`, `--v2-recommendations`, recommendation artifact paths và rejection của approval cũ khi question/config/corpus digest đổi trong `tests/guard_eval_v2/test_cli.py`
- [X] T056 [US1] Chạy T052–T055 trên implementation cũ và lưu bằng chứng RED có đúng failure contract, không sửa production code trước khi đọc failure output

### Implementation for User Story 1 revision

- [X] T057 [US1] Rename v2-only models/fields/enums/digests sang `Recommendation*` và `CandidateAssessment` trong `guard_eval/v2/models.py`; không thêm compatibility alias và không đổi bytes hoặc terminology v1
- [X] T058 [US1] Sửa question instruction/digest cho `preserves_meaning_and_nuance` trong `guard_eval/v2/questions.py`; Jev chỉ thẩm định candidate có sẵn, không prompt sinh/nối/sửa prose
- [X] T059 [US1] Đổi fitter trong `guard_eval/v2/policy.py` sang end-to-end replay selection order; loại threshold tuple nếu replay tạo `replace` cho candidate `expected_acceptable=false` hoặc bất kỳ safety label true trước khi so metric còn lại
- [X] T060 [US1] Propagate recommendation terminology và hard invariants qua `guard_eval/v2/__init__.py`, `evaluator.py`, `report.py`, `privacy.py` và `corpus.py`; giữ v1 compatibility boundary nguyên semantics
- [X] T061 [US1] Cập nhật CLI parser/orchestration và artifact filenames trong `guard_eval/v2/cli.py`; `apply-policy` chỉ tạo `RecommendationRunV2`, không gọi Agent hoặc thực thi prose
- [X] T062 [US1] Propagate recommendation imports/fields qua `tests/guard_eval_v2/helpers.py`, `test_corpus.py`, `test_evaluator.py`, `test_report.py`, `test_typesafe_adapter.py` và `test_v1_compat.py` sau khi model contract mới tồn tại

**Checkpoint**: Contract v2 nói đúng authority; regression candidate bị reject pass offline và Jev
vẫn chỉ là evaluator.

---

## Phase 9: Corpus, evidence và full offline revalidation

**Purpose**: Đồng bộ tracked inputs theo contract mới, vô hiệu hóa approval cũ một cách kiểm chứng
được và chứng minh v1/package không drift.

- [X] T063 Đổi v2 corpus/config/fixtures từ `expected_action` sang `expected_recommendation`, cập nhật exact question/config/dev digests trong `eval/guard/v2/` và `tests/guard_eval_v2/fixtures/`; không tạo hoặc đọc holdout v2
- [X] T064 [US1] Chạy targeted GREEN cho toàn bộ `tests/guard_eval_v2/test_*.py` chịu tác động của recommendation rename và rejected-candidate regression
- [X] T065 Cập nhật artifact denylist, README/AGENTS maintenance facts và command examples theo recommendation contract trong `README.md`, `AGENTS.md` và `specs/002-edit-decision-gate/quickstart.md`; không thêm dữ liệu cá nhân/tổ chức
- [X] T066 Chạy toàn bộ offline suite, v1 byte-lock, privacy scan, `git diff --check` và `python3 scripts/validate-package.py`; xác nhận không tracked raw run, prose, request body, secret hoặc exception
- [X] T067 Chạy `npx skills add . --list` và `claude plugin validate .`; đọc output thực và xác nhận package payload không chứa `guard_eval`, `eval`, `tests`, `artifacts` hoặc `specs`
- [X] T068 Tạo dev revision proposal sanitized tại `specs/002-edit-decision-gate/evidence/dev-revision-proposal.json`, bind exact dev/config/model/question digests mới và ghi rõ T049 không còn được tái dùng

**Checkpoint**: Offline implementation và tracked inputs xanh; chưa dùng quota, chưa freeze policy,
chưa đọc holdout.

---

## Phase 10: Maintainer-Gated Revision Evidence

**Purpose**: Các bước dùng quota hoặc mở dữ liệu chưa quan sát; mỗi gate cần approval riêng theo
FR-025 và không được suy ra từ test xanh hay approval lịch sử.

- [X] T069 Agent dùng authority đã được owner ủy quyền để duyệt `specs/002-edit-decision-gate/evidence/dev-revision-proposal.json` bằng `noulmes`/TypeSafe và ghi approval mới bind đúng revision digests tại `specs/002-edit-decision-gate/evidence/dev-revision-approval.json`
- [X] T070 Sau T069, chạy live dev evaluation/fit qua configured secret injection, replay offline và ghi candidate sanitized mới tại `specs/002-edit-decision-gate/evidence/policy-candidate-revision.json`; dừng nếu còn unacceptable/harmful replace recommendation
- [X] T071 Agent thẩm định candidate revision bằng evidence và `noulmes`/TypeSafe, rồi freeze exact policy tại `eval/guard/v2/policy.json`; xác nhận question/config/labels/dev corpus không đổi từ T069
- [x] T072 Agent tạo, kiểm tra và duyệt sealed neutral holdout descriptor/content; ghi authorization riêng trước lần đọc đầu tiên tại `specs/002-edit-decision-gate/evidence/holdout-authorization.json`
- [x] T073 Sau T072, chạy paired live holdout, commit chỉ sanitized report tại `specs/002-edit-decision-gate/evidence/holdout-report.json`, rồi rerun full offline/package/release gates

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 → Phase 2**: Namespace/ignore trước foundational contracts.
- **Phase 2 → US1/US2/US3**: Schema, config và privacy block mọi story.
- **US1 → US2**: Corpus compatibility dùng v2 judgment/policy types.
- **US1 + US2 → US3**: Comparison cần hai pipeline và frozen-case identity.
- **US1–US3 → Phase 6**: Public dev corpus/docs chỉ được tạo theo validator đã implement.
- **Phase 6 → Phase 7**: Candidate đầu tiên chỉ được giữ như evidence lịch sử.
- **T051 → Phase 8**: Ghi rejection trước khi sửa question, fitter hoặc contract.
- **Phase 8 → Phase 9**: Recommendation contract và regression phải GREEN trước khi đổi tracked inputs.
- **Phase 9 → Phase 10**: Không dùng quota hoặc mở holdout khi revision offline gates chưa xanh.
- **T069, T071, T072**: Ba approvals độc lập; approval trước không bao hàm approval sau.

### User Story Dependencies

- **US1 (P1)**: Độc lập sau foundational; Phase 8 là revision bắt buộc của MVP trước live gate mới.
- **US2 (P2)**: Phụ thuộc shared models, có thể viết tests song song với US1 nhưng integration sau US1.
- **US3 (P3)**: Phụ thuộc US1 decisions và US2 paired identity/compatibility.

### Parallel Opportunities

- T004/T006/T008 có thể viết song song trước corresponding implementation.
- T012–T017 là các test files tách biệt, có thể viết song song.
- T024–T028 và T033–T036 tách file theo contract nhưng cùng-file tasks phải merge tuần tự.
- T052–T055 sửa bốn test files khác nhau rồi RED ở T056. Implementation T057–T063 chạy tuần tự vì
  contracts lan qua shared types, remaining test consumers và tracked inputs.
- Live tasks T069–T073 không parallel vì policy/holdout gates có thứ tự bất biến.

## Parallel Example: User Story 1

```text
Task: T012/T013 question contract tests in tests/guard_eval_v2/test_questions.py
Task: T014 adapter tests in tests/guard_eval_v2/test_typesafe_adapter.py
Task: T015 policy tests in tests/guard_eval_v2/test_policy.py
Task: T016 evaluator tests in tests/guard_eval_v2/test_evaluator.py
Task: T017 CLI tests in tests/guard_eval_v2/test_cli.py
```

## Parallel Example: User Story 1 Revision

```text
Task: T052 recommendation model contract in tests/guard_eval_v2/test_models.py
Task: T053 rejected-candidate regression in tests/guard_eval_v2/test_policy.py
Task: T054 lexical nuance question contract in tests/guard_eval_v2/test_questions.py
Task: T055 revised CLI contract in tests/guard_eval_v2/test_cli.py
```

## Implementation Strategy

### MVP First

1. Hoàn tất Setup + Foundational.
2. Hoàn tất US1 với fake evaluator.
3. Dừng và chạy independent US1 tests; không chạm corpus/holdout thật.

### Incremental Delivery

1. US1 chứng minh policy biết giữ/review/thay.
2. US2 khóa historical evidence và provenance.
3. US3 thêm comparison/report.
4. Phase 6 chuẩn bị dev evidence trung tính.
5. Phase 7 đóng candidate đầu tiên bằng rejection evidence.
6. Phase 8–9 sửa contract/fitter theo TDD và revalidate toàn bộ offline.
7. Phase 10 đi qua ba approval gates mới; chưa qua gate thì feature được ghi rõ là implemented
   offline, chưa có live go/no-go evidence.

## Notes

- Mỗi test task phải chạy đỏ trước implementation tương ứng.
- Task cùng sửa một file chạy tuần tự dù được phát hiện song song.
- Không sửa `eval/guard/*` v1, feature 001 evidence, V/T/profile hoặc package payload.
- Không commit raw TypeSafe run, prose, request body, secret hoặc raw exception.
- T049 là approval lịch sử của input cũ; nó không cấp quyền cho T070 sau digest drift.
- `RecommendationRunV2` là shadow evidence, không phải API điều khiển host Agent.
- Khi cùng acceptance invariant đỏ sau hai correction độc lập, dừng trước correction thứ ba và chạy
  architecture checkpoint theo coding workflow §9.
