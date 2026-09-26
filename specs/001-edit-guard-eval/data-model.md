# Data Model: Đánh giá guard theo từng edit

## Enumerations

### Split

- `dev`: được phép dùng để chỉnh questions và fit policy.
- `holdout`: chỉ được đọc sau khi policy đã khóa.

### NaturalnessReason

- `lexically_incomplete`: source thiếu một tiếng để thành từ/cụm đúng nghĩa đang dùng.
- `unnatural_collocation`: từng tiếng có nghĩa nhưng kết hợp không tự nhiên trong ngữ cảnh.

### GuardDimension

- `adds_claim`
- `changes_actor_or_time`
- `changes_causality_or_commitment`
- `changes_order_or_concurrency`
- `changes_register`
- `keeps_invalid_process_metadata`

### CandidateOriginKind

- `host_llm_output`: output của host LLM chạy vi-humanizer, có model/workflow reference.
- `baseline_observation`: output đã đóng băng của workflow baseline.
- `maintainer_fixture`: phương án kiểm thử do maintainer cung cấp hoặc xác nhận.

### GuardAction

- `pass`: candidate vượt safety policy.
- `review`: candidate cần người xem.
- `reject`: candidate vi phạm rõ trong eval; vẫn không tác động output thật.

### EditDecision

- `keep`: source không cần sửa.
- `replace`: dùng nguyên văn một candidate đã cung cấp.
- `review`: source/candidate judgments chưa đủ để tự chọn trong shadow artifact.

### CheckStatus

- `checked`: có đủ naturalness, preference và safety judgments hợp lệ.
- `unchecked`: evaluator không đưa ra đủ judgment vì key/service/timeout/response error.

### RunStatus

- `complete`: artifact hợp lệ và mọi case đã được chấm.
- `incomplete`: artifact hợp lệ nhưng có ít nhất một case `unchecked`.
- `invalid`: input, schema, digest, leakage hoặc artifact không qua integrity validation.

## CandidateEdit

| Field | Type | Required | Rule |
|---|---|---:|---|
| `candidate_id` | string | yes | Duy nhất trong case; slug ổn định, không phụ thuộc vị trí |
| `candidate_span` | string | yes | Không rỗng; khác source và candidate khác sau normalize |
| `candidate_origin` | object | yes | `kind` thuộc `CandidateOriginKind`, `reference`, `authority`; thêm model/workflow version khi áp dụng |
| `expected_dimensions` | map `GuardDimension` → bool | yes | Đủ sáu keys; ground truth safety |
| `expected_guard_action` | `GuardAction` | yes | `pass` chỉ khi cả sáu dimensions false |

## EvaluationCase

Một record JSONL, đại diện cho một source cùng nhóm candidate cạnh tranh.

| Field | Type | Required | Rule |
|---|---|---:|---|
| `case_id` | string | yes | Duy nhất trong corpus; slug ổn định, không mang nhãn |
| `split` | `Split` | yes | Phải khớp file split được manifest chỉ định |
| `source_span` | string | yes | Không rỗng; raw prose chỉ nằm trong corpus |
| `candidates` | `CandidateEdit[]` | yes | Từ 1 đến 3 phần tử; ID và normalized text duy nhất |
| `context_before` | string | yes | Có thể rỗng nhưng field phải tồn tại |
| `context_after` | string | yes | Có thể rỗng nhưng field phải tồn tại |
| `current_intent` | string | yes | Đủ để xét thay đổi có được yêu cầu hay không |
| `genre` | string | yes | Tên thể loại theo cổng của `SKILL.md`/profile |
| `inseparable_edit_ids` | string[] | yes | Rỗng nếu case là một edit; nếu không phải nêu các edit con |
| `expected_needs_edit` | bool | yes | Source có cần sửa theo phạm vi V20 hay không |
| `expected_naturalness_reasons` | `NaturalnessReason[]` | yes | Rỗng iff `expected_needs_edit=false` |
| `expected_preferred_option` | string | yes | `keep_original`, `candidate:<id>` hoặc `none_of_candidates` |
| `expected_edit_decision` | `EditDecision` | yes | Ground truth cho hành động quan sát cuối |
| `label_source` | object | yes | `kind`, `authority`, `reference`; holdout cần maintainer |
| `pattern_refs` | string[] | yes | Phải chứa `V20` cho positive; có thể chứa V20 cho no-flag |
| `baseline` | object | yes | `edit_decision`, `selected_candidate_id`, `guard_action`, version/reference/authority; replace phải trỏ candidate trong case |
| `provenance` | object | yes | Repo-relative path cùng line/section hoặc immutable source id |

### Label consistency

- `expected_needs_edit=false` đòi `expected_naturalness_reasons=[]`,
  `expected_preferred_option=keep_original` và `expected_edit_decision=keep`.
- `expected_needs_edit=true` đòi ít nhất một naturalness reason và preferred option không được là
  `keep_original`; `none_of_candidates` ánh xạ tới `expected_edit_decision=review`.
- `expected_edit_decision=replace` đòi preferred option là một candidate ID có thật và candidate đó
  có `expected_guard_action=pass`.
- Candidate harmful khi ít nhất một expected safety dimension true; harmful candidate không được
  có `expected_guard_action=pass`.
- Baseline không quyết định nhãn và có thể khác expected values.
- Baseline `keep` bắt buộc `selected_candidate_id=null`; `replace` bắt buộc trỏ candidate trong case;
  `review` có thể mang candidate ID khi candidate bị guard hoặc null khi không phương án nào được
  baseline chọn. Giá trị null ở baseline review ánh xạ `none_of_candidates` khi tính preference.

### Identity and fingerprint

`case_id` là identity cho người đọc; `case_fingerprint` là identity kỹ thuật. Fingerprint bằng
SHA-256 của canonical JSON gồm source, candidate objects **đã sắp theo `candidate_id`**, context,
intent và genre sau Unicode NFC cùng whitespace normalization. `case_id`, split và thứ tự serialize
candidate không tham gia fingerprint. Validator từ chối fingerprint trùng giữa dev và holdout.

## CorpusManifest

| Field | Type | Rule |
|---|---|---|
| `schema_version` | string | Version của record contract |
| `corpus_version` | string | `sha256:<digest>` của canonical dev + holdout |
| `dev.path` / `holdout.path` | string | Repo-relative JSONL path, không thoát bằng `..` |
| `dev.sha256` / `holdout.sha256` | string | Digest bytes của từng split file |
| `baseline_workflow_version` | string | Ban đầu là `vi-humanizer-0.7.1` |
| `coverage_requirements` | object | Positive/hard-negative V20 và safety dimensions, plus `none_of_candidates > 0` với ít nhất một safety-pass candidate ở từng split |
| `created_at` | RFC 3339 string | Audit metadata, không tham gia semantic labels |

## EvaluationConfig

| Field | Type | Rule |
|---|---|---|
| `config_version` | string | `sha256:<digest>` của canonical config |
| `model_version` | string | Version model pin, ban đầu `jev-1.13.0` |
| `question_set_version` | string | Digest của toàn bộ Noul/Choice definitions |
| `timeout_seconds` | number | Dương; chỉ kiểm soát request |
| `retry_policy` | object | Số lần và backoff hữu hạn; không chứa credential |

Dev evaluation chỉ cần manifest và config. Policy được tạo sau từ dev run, nên config không tham
chiếu ngược tới policy.

## JudgmentSet

Kết quả TypeSafe cho một case.

| Field | Type | Rule |
|---|---|---|
| `case_id` | string | Phải tồn tại trong manifest |
| `case_fingerprint` | string | Phải khớp case tại thời điểm run |
| `status` | `CheckStatus` | `checked` hoặc `unchecked` |
| `naturalness_scores` | map `NaturalnessReason` → float | Hai values trong [0,1], chỉ khi checked |
| `preference_probabilities` | map option ID → float | Đủ original/candidates/none, tổng hợp lệ |
| `preference_choice` | option ID | Phải là key trong probability map |
| `preference_confidence` | float | Trong [0,1], chỉ khi checked |
| `candidate_safety_scores` | map candidate ID → map dimension → float | Đủ candidate và sáu keys |
| `reason_code` | string/null | Bắt buộc khi unchecked; cấm raw exception text |
| `latency_ms` | integer/null | Số đo monotonic của request |
| `input_tokens` / `output_tokens` | integer/null | Từ response usage |
| `model_version` | string/null | Versioned response model, không chỉ alias |

Allowed `reason_code`: `missing_api_key`, `timeout`, `authentication`, `rate_limited`,
`overloaded`, `connection`, `invalid_response`, `service_error`.

## DecisionPolicy

| Field | Type | Rule |
|---|---|---|
| `policy_version` | string | `sha256:<digest>` của canonical policy |
| `corpus_version_fitted` | string | Trỏ đúng dev corpus version |
| `config_version` | string | Config dùng để tạo dev run |
| `question_set_version` | string | Digest của question definitions |
| `model_version` | string | Version model dùng để fit |
| `needs_edit_thresholds` | map reason → float | Mỗi value trong [0,1] |
| `preference_confidence_threshold` | float | Trong [0,1] |
| `preference_margin_threshold` | float | Trong [0,1] |
| `safety_review_threshold` | float | Trong [0,1] |
| `safety_reject_threshold` | float | review ≤ reject ≤ 1 |
| `selection_order` | string[] | Các tiêu chí tất định trong `research.md` |
| `created_at` | RFC 3339 string | Audit metadata |

Candidate guard action lấy max sáu safety probabilities. Edit transition cho checked judgment:

```text
mọi naturalness score dưới threshold
  + Choice tự tin chọn keep_original                        -> keep
ít nhất một naturalness score đạt threshold
  + Choice tự tin chọn candidate
  + candidate safety action=pass                            -> replace(candidate_id)
mọi tổ hợp còn lại                                          -> review
```

Policy không có transition runtime; feature chỉ tạo action quan sát trong artifact. `replace`
luôn tham chiếu candidate ID, không chứa prose mới.

## PricingSnapshot

| Field | Type | Rule |
|---|---|---|
| `pricing_version` | string | `sha256:<digest>` của canonical snapshot |
| `model_version` | string | Phải khớp model trong policy/run |
| `currency` | string | ISO 4217, ban đầu `USD` |
| `input_cost_per_million_tokens` | number | Không âm |
| `output_cost_per_million_tokens` | number | Không âm |
| `observed_at` | RFC 3339 string | Ngày đọc pricing |
| `source` | URL string | Trang pricing chính thức |

Pricing snapshot chỉ ảnh hưởng trường cost; không tham gia route hoặc go/no-go.

## EvaluationRun

| Field | Type | Rule |
|---|---|---|
| `run_id` | string | UUID hoặc content-addressed id |
| `started_at` / `completed_at` | RFC 3339 string | Bắt buộc |
| `split` | `Split` | Một run chỉ đọc một split |
| `corpus_version` / `config_version` | string | Phải khớp manifest/config |
| `question_set_version` | string | Phải khớp code hiện tại |
| `requested_model` | string | Version pin trong config |
| `observed_models` | string[] | Version thực từ responses |
| `policy_version` / `pricing_version` | null | Raw run chưa áp policy/pricing |
| `run_status` | `RunStatus` | `complete`, `incomplete` hoặc `invalid` |
| `counts` | object | total, checked, unchecked theo reason |
| `judgments` | `JudgmentSet[]` | Một entry cho mọi case, không mất im lặng |

Run `invalid` nếu mixed model version, thiếu/thừa case hoặc digest mismatch. Run hợp lệ có
`unchecked > 0` mang trạng thái `incomplete`, vẫn được lưu nhưng không dùng cho go/no-go.

## EvaluationReport

| Field | Type | Rule |
|---|---|---|
| `report_version` | string | Version contract |
| `run_id` | string | Run nguồn |
| `run_status` | `RunStatus` | Kế thừa validity/completeness của run |
| `corpus_version` / `config_version` / `model_version` | string | Phải khớp inputs |
| `policy_version` / `pricing_version` | string | Versions thực sự áp dụng |
| `metrics.baseline` | object | Need-to-edit recall, unnecessary-edit, candidate choice, no-acceptable-candidate recall, harmful recall, valid-edit false-block, safety false accept và review |
| `metrics.candidate` | object | Cùng metrics; thêm latency, usage và estimated cost |
| `metrics.by_reason` | object | Confusion counts cho hai naturalness reasons |
| `metrics.by_dimension` | object | Confusion counts cho sáu safety dimensions |
| `coverage` | object | Case count, source kind, authority, genre, positive/hard negatives |
| `limitations` | string[] | Cỡ mẫu, gaps, dev tuning và unchecked cases |
| `decision` | enum/null | `stop`, `collect_more_labels`, `continue_shadow`; null nếu không đủ điều kiện |
| `decision_reasons` | string[] | Chỉ dùng metric/validity facts, không dùng raw prose |

Metric denominators:

- `need_to_edit_recall`: case có `expected_needs_edit=true`.
- `unnecessary_edit_rate`: case có `expected_needs_edit=false`; mọi decision khác `keep` là lỗi.
- `candidate_choice_accuracy`: case có `expected_edit_decision=replace`; đúng khi final decision là
  `replace` với preferred candidate ID.
- `no_acceptable_candidate_recall`: case có `expected_preferred_option=none_of_candidates`; đúng khi
  Choice chọn `none_of_candidates` và final decision là `review`.
- `unacceptable_candidate_replace_rate` *(dev fit only)*: case có
  `expected_preferred_option=none_of_candidates`; lỗi khi policy vẫn trả `replace`. Metric này chọn
  threshold bảo vệ action nhưng không thay thế `no_acceptable_candidate_recall` khi báo cáo model.
- `valid_edit_false_block_rate`: candidate có `expected_guard_action=pass`; lỗi khi safety policy
  cho `review` hoặc `reject`.
- `safety_false_accept_rate`: observed `replace`; lỗi khi candidate được chọn có expected guard
  action khác `pass`.
- `harmful_edit_recall`: candidate có ít nhất một expected safety dimension true; đúng khi safety
  policy cho `review` hoặc `reject`.

### Go/no-go transition

```text
artifact invalid                                      -> invalid/null
có unchecked holdout                                  -> incomplete/null
metric bắt buộc có mẫu số bằng 0                      -> complete/collect_more_labels
ba metric need-to-edit/candidate-choice/no-acceptable
  đều không tăng, hoặc một metric giảm              -> complete/stop
unnecessary-edit, valid-edit false block
  hoặc safety false accept tăng                       -> complete/stop
harmful-edit recall giảm                              -> complete/stop
otherwise                                             -> complete/continue_shadow
```

`continue_shadow` không đồng nghĩa production-ready và không cấp quyền tự động sửa, loại hoặc
hoàn edit.
