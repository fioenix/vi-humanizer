# Data Model: Cổng quyết định sửa hay giữ v2

## Enumerations

### Split

- `dev`: được phép dùng để chỉnh questions, labels và fit threshold.
- `holdout`: chỉ được mở sau khi policy v2 đã được maintainer duyệt và khóa.

### ExpectedRecommendation / RecommendationKind

- `keep`: evaluator có đủ evidence để khuyến nghị giữ source.
- `review`: evaluator chưa thể chứng minh khuyến nghị giữ hoặc thay.
- `replace`: evaluator có đủ evidence để khuyến nghị một candidate đã cung cấp.

Ba value này chỉ là ground truth và output của evaluation shadow. Host LLM/Agent vẫn quyết định
biên tập và sinh câu chữ cuối; feature 002 không thực thi recommendation.

### SourceIssue

- `lexically_incomplete`: thiếu tiếng/thành phần cần thiết để cách dùng từ đủ nghĩa tự nhiên.
- `unnatural_collocation`: các tiếng riêng có nghĩa nhưng kết hợp khô cứng hoặc không tự nhiên.

### CandidateComponent

- `fixes_issue`
- `preserves_meaning_and_nuance`
- `fits_voice_and_genre`

### CandidateAssessment

- `pass`: candidate vượt mọi component và safety boundary cần thiết để vào shortlist.
- `review`: evidence của candidate nằm trong vùng chưa chắc chắn; không được nhận recommendation
  `replace`.
- `reject`: candidate không đạt component hoặc vượt safety reject boundary.

### SafetyDimension

- `adds_claim`
- `changes_actor_or_time`
- `changes_causality_or_commitment`
- `changes_order_or_concurrency`
- `changes_register`
- `keeps_invalid_process_metadata`

### CheckStatus / RunStatus

- `checked`: đủ typed judgments cần thiết cho case.
- `unchecked`: thiếu judgment do key/service/timeout/invalid response.
- `complete`: mọi case checked và artifact qua integrity validation.
- `incomplete`: artifact hợp lệ nhưng có ít nhất một case unchecked.
- `invalid`: schema, digest, model, case set hoặc provenance không hợp lệ.

### RecommendationReason

Allowed values:

- `source_already_sufficient`
- `insufficient_context`
- `source_signal_uncertain`
- `source_signal_conflict`
- `no_acceptable_candidate`
- `single_acceptable_candidate`
- `ranked_candidate_selected`
- `ranking_uncertain`
- `service_unchecked`

Service failure codes vẫn dùng allowlist v1:
`missing_api_key`, `timeout`, `authentication`, `rate_limited`, `overloaded`, `connection`,
`invalid_response`, `service_error`.

## RecommendationCaseV2

Một record JSONL gồm semantic input, labels và provenance. Chỉ request-state projection được gửi
cho TypeSafe; label/provenance không bao giờ rời local evaluator.

| Field | Type | Rule |
|---|---|---|
| `schema_version` | string | Exact v2 schema version |
| `case_id` | string | Duy nhất trong corpus; không tham gia semantic fingerprint |
| `split` | `Split` | Phải khớp file chứa record |
| `source_span` | string | Không rỗng; Unicode NFC khi fingerprint |
| `context_before` / `context_after` | string | Local context tối thiểu; có thể rỗng nhưng field bắt buộc |
| `current_intent` | string | Ý định cần bảo toàn |
| `genre` | string | Giá trị allowlist của corpus |
| `candidates` | `CandidateV2[]` | Từ một đến ba; ID/text duy nhất sau normalize |
| `expected_recommendation` | `ExpectedRecommendation` | Ground truth recommendation cấp source |
| `expected_source_issues` | map `SourceIssue → bool` | Đủ hai keys |
| `label_authority` | object | Authority, reference, confirmed_at; holdout cần maintainer |
| `provenance` | object | Chỉ nguồn công khai hoặc fixture trung tính |
| `lineage` | `PromotionLineage/null` | Bắt buộc cho case promote từ holdout đã quan sát |

### Request projection

Chỉ sáu field sau được gửi:

```json
{
  "source_span": "...",
  "candidates": [{"candidate_id": "c1", "candidate_span": "..."}],
  "context_before": "...",
  "context_after": "...",
  "current_intent": "...",
  "genre": "..."
}
```

`case_id`, split, mọi `expected_*`, origin, label authority, provenance, lineage và baseline bị cấm.

## CandidateV2

| Field | Type | Rule |
|---|---|---|
| `candidate_id` | string | Slug ổn định; không phụ thuộc vị trí |
| `candidate_span` | string | Khác source và candidate khác sau normalize |
| `candidate_origin` | object | `host_llm_output`, `baseline_observation` hoặc `maintainer_fixture`; có reference |
| `expected_acceptable` | bool | Gold label cuối cho candidate acceptability |
| `expected_components` | map `CandidateComponent → bool` | Đủ ba keys; true là điều kiện đạt |
| `expected_safety` | map `SafetyDimension → bool` | Đủ sáu keys; true là có risk |

Invariant:

```text
expected_acceptable =
  all(expected_components.values())
  AND not any(expected_safety.values())
```

Nếu `expected_recommendation=replace`, có thể có nhiều candidate acceptable nhưng đúng một candidate
tốt nhất phải được ghi là `expected_selected_candidate_id`. Nếu `expected_recommendation=review` do
không có candidate đạt, mọi candidate có `expected_acceptable=false`.

## PromotionLineage

| Field | Type | Rule |
|---|---|---|
| `kind` | string | Chỉ `promoted_observed_holdout` trong iteration này |
| `source_feature` | string | `001-edit-guard-eval` |
| `source_split` | string | `holdout` |
| `source_case_id` | string | Resolve được trong v1 artifact |
| `source_case_fingerprint` | digest | Phải bằng fingerprint semantic của case v2 |
| `source_corpus_version` | digest | Khớp manifest v1 đã khóa |
| `source_artifact_path` | path | Repo-relative, nằm trong lock manifest |
| `source_artifact_sha256` | digest | Khớp bytes thật |
| `promotion_decision_ref` | path/anchor | Trỏ về quyết định feature 002 |

Lineage này chỉ hợp lệ trong `dev`. Holdout v2 cấm lineage và cấm fingerprint trùng registry của
bất kỳ holdout lịch sử đã mở.

## CorpusManifestV2

| Field | Type | Rule |
|---|---|---|
| `schema_version` | string | Version contract corpus v2 |
| `dev_version` | digest | Canonical digest chỉ của dev records; khóa policy fit và không đổi khi seal holdout |
| `corpus_version` | digest | Canonical digest của semantic records + labels + lineage |
| `dev` / `holdout` | object | Dev có path/digest/count; holdout là `pending` với digest/count null cho đến T052, sau đó mới thành `sealed` |
| `observed_holdouts_registry` | path + digest | Khóa tập fingerprint không được tái dùng ở holdout |
| `v1_artifact_lock` | path + digest | Khóa bytes feature 001 |
| `coverage_requirements` | object | Minimum 5 cho ba recommendation classes và hai slices |
| `created_at` | RFC 3339 | Audit metadata |

Ba identity tách biệt:

- `case_fingerprint`: chỉ băm request state normalized; dùng chống semantic leakage.
- `dev_version`: băm dev labels, split, lineage và ordered records; dùng khóa policy fit/freeze.
- `corpus_version`: băm `dev_version` cùng holdout identity; dùng khóa paired evaluation và đổi khi holdout được seal.

## EvaluationConfigV2

| Field | Type | Rule |
|---|---|---|
| `config_version` | digest | Canonical self-digest |
| `model_version` | string | Exact `jev-1.13.0`, không alias |
| `absolute_question_set_version` | digest | Static Nouls + dynamic-key rules |
| `ranking_question_set_version` | digest | Static Choice + shortlist option rule |
| `timeout_seconds` | number | Dương |
| `retry_policy` | object | Hữu hạn; không chứa credential |
| `max_candidates` | integer | `3` trong iteration này |

## AbsoluteJudgmentV2

| Field | Type | Rule |
|---|---|---|
| `case_id` / `case_fingerprint` | string/digest | Khớp case tại thời điểm run |
| `status` | `checked` / `unchecked` | Unchecked không được có score giả |
| `source_context_sufficient` | probability/null | [0,1] khi checked |
| `source_issue_scores` | map `SourceIssue → probability` | Đủ hai keys khi checked |
| `candidate_component_scores` | map candidate → map component → probability | Đủ candidate/components |
| `candidate_safety_scores` | map candidate → map dimension → probability | Đủ candidate/dimensions |
| `reason_code` | service code/null | Bắt buộc khi unchecked |
| `latency_ms` | integer/null | Đo monotonic |
| `input_tokens` / `output_tokens` | integer/null | Usage thực từ response |
| `observed_model` | string/null | Exact response model |

Không có action, threshold, acceptability cuối, labels, provenance hoặc raw response text.

## RankingJudgmentV2

Chỉ tồn tại khi shortlist có ít nhất hai candidate.

| Field | Type | Rule |
|---|---|---|
| `eligible_candidate_ids` | string[] | Sorted; ít nhất hai; phải là subset của case candidates |
| `probabilities` | map candidate ID → probability | Keys đúng bằng shortlist |
| `choice` | candidate ID | Một key trong map |
| `confidence` | probability | Không được dùng thay safety/acceptability |
| `latency_ms`, token usage, observed model | telemetry | Cùng rules absolute judgment |

Với shortlist 0 hoặc 1, field ranking là `null` và không phát sinh request/usage.

## JudgmentRunV2

Raw typed evidence trước policy.

| Field | Type | Rule |
|---|---|---|
| `judgment_run_version` | string | Contract version |
| `pipeline_version` | enum | `v1_compat` hoặc `v2` |
| `run_digest` | digest | Canonical semantic digest, bỏ timestamps |
| `corpus_version` / `case_set_digest` | digest | Evaluation corpus và exact case/fingerprint set |
| `split` | `Split` | Một run một split |
| `config_version` / question versions | digest | Khớp pipeline tương ứng |
| `requested_model` / `observed_models` | string/string[] | Mixed hoặc mismatch làm invalid |
| `policy_version` | null | Bắt buộc null |
| `run_status` | `RunStatus` | Complete/incomplete/invalid |
| `counts` | object | Tổng số request đã lưu (absolute + ranking), checked, unchecked theo allowlisted reason |
| `judgments` | array | Một entry cho mọi case, không mất im lặng |
| `started_at` / `completed_at` | RFC 3339 | Audit only |

`v1_compat` judgment giữ schema semantic v1 bên trong entry nhưng dùng envelope v2 để paired
comparison kiểm cùng case set. Hai pipeline không chia sẻ typed judgment.

## RecommendationPolicyV2

| Field | Type | Rule |
|---|---|---|
| `policy_version` | digest | Canonical digest của toàn policy |
| `pipeline_version` | string | `v2` |
| `fitted_corpus_version` | digest | Provenance dev; không phải evaluation-corpus restriction |
| `config_version` / question versions / model | digest/string | Phải khớp run được áp |
| `context_threshold` | probability | Fit trên dev |
| `source_issue_negative_thresholds` / `source_issue_positive_thresholds` | map source issue → probability | negative ≤ positive; vùng giữa ra review |
| `candidate_component_negative_thresholds` / `candidate_component_positive_thresholds` | map component → probability | negative ≤ positive; vùng giữa không được coi là đạt |
| `safety_review_thresholds` / `safety_reject_thresholds` | map dimension → probability | review ≤ reject |
| `ranking_confidence_threshold` / `ranking_margin_threshold` | probability | Chỉ dùng khi shortlist ≥2 |
| `selection_order` | string[] | Exact tie-break thực thi: không harmful/unacceptable replace recommendation → recommendation accuracy → selected-candidate accuracy → signal accuracy → ít review → separation rộng hơn → ranking route accuracy → threshold ranking chặt hơn |
| `created_at` | RFC 3339 | Audit only |

Threshold không có giá trị mặc định từ docs. Candidate đủ chuẩn khi mọi component đạt positive
threshold và mọi safety dimension không vượt negative/pass boundary. Safety score nằm giữa pass
boundary và reject threshold bắt buộc ra `review`, không được tính là pass. Bất kỳ component nào ở
vùng giữa cũng làm candidate không đủ điều kiện nhận recommendation `replace`.

Fitter MUST từ chối candidate policy nếu replay trên dev tạo recommendation `replace` cho candidate
có `expected_acceptable=false` hoặc safety label true. Candidate policy vẫn phải trình bày toàn bộ
disagreement với ground truth để maintainer review; fit thành công về schema không tự cấp quyền freeze.

## PolicyRecommendationV2 / RecommendationRunV2

Mỗi `PolicyRecommendationV2` gồm:

| Field | Type | Rule |
|---|---|---|
| `case_id` / `case_fingerprint` | string/digest | Khớp raw run |
| `recommendation` | `keep` / `review` / `replace` | Đúng một value cho checked case; không phải runtime command |
| `selected_candidate_id` | string/null | Chỉ non-null khi replace |
| `reason_codes` | `RecommendationReason[]` | Không rỗng, sorted, finite |
| `candidate_assessments` | map candidate → `CandidateAssessment` | Không chứa scores; không thực thi prose |
| `eligible_candidate_ids` | string[] | Shortlist sau absolute gate |

`RecommendationRunV2` thêm `recommendation_run_digest`, `pipeline_version`, `judgment_run_digest`,
`evaluation_corpus_version`, `policy_version`, `policy_fitted_corpus_version`, `run_status` và toàn
bộ recommendations. Cùng raw run + policy phải cho cùng semantic digest, không phụ thuộc timestamp.

### State transition

```text
JudgmentRun incomplete/invalid                         -> RecommendationRun same status, no go/no-go
context below threshold                               -> recommend review(insufficient_context)
source issue in uncertainty/conflict region           -> recommend review(source_signal_*)
no source issue reaches threshold                     -> recommend keep(source_already_sufficient)
source needs edit + no eligible candidate             -> recommend review(no_acceptable_candidate)
source needs edit + one eligible candidate            -> recommend replace(single_acceptable_candidate)
source needs edit + multiple eligible + weak ranking  -> recommend review(ranking_uncertain)
source needs edit + multiple eligible + clear ranking -> recommend replace(ranked_candidate_selected)
```

## MetricValue / MetricComparison

```json
{
  "unit": "case",
  "direction": "higher_is_better",
  "numerator": 7,
  "denominator": 10,
  "rate": 0.7,
  "minimum_denominator": 5,
  "denominator_status": "sufficient"
}
```

Rules:

- `rate = numerator / denominator`; denominator 0 cho `rate=null`.
- `denominator_status`: `sufficient` hoặc `insufficient`.
- `MetricComparison` chứa `v1`, `v2`, `rate_delta=v2-v1`, `improvement_delta`; metric
  lower-is-better đảo dấu improvement.

Protected metrics:

| Metric | Unit | Numerator / Denominator | Direction |
|---|---|---|---|
| `harmful_edit_recall` | candidate | harmful candidate bị review/reject / harmful candidate | higher |
| `keep_precision` | case | recommended keep đúng / mọi recommended keep | higher |
| `no_acceptable_candidate_recall` | case | gold-none được recommend review, no selection / gold-none | higher |
| `valid_edit_false_block_rate` | candidate | acceptable candidate bị block / acceptable candidate | lower |
| `candidate_choice_accuracy` | case | gold-replace chọn đúng / gold-replace | higher |

Hard invariants: `harmful_replace_recommendation_count == 0` và
`unacceptable_replace_recommendation_count == 0`.

## ComparisonReportV2

| Field | Type | Rule |
|---|---|---|
| `report_version` / `report_digest` | string/digest | Canonical contract/version |
| `corpus_version` / `case_set_digest` | digest | Hai pipelines phải giống |
| `v1` / `v2` | provenance object | Judgment/recommendation/policy/config/question/model digests |
| `metrics` | map name → `MetricComparison` | Protected + diagnostic |
| `coverage` | map slice → count/status | Keep/review/replace/no-acceptable/harmful, min 5 |
| `disagreements` | array | Chỉ case ID/fingerprint, recommendations và reason codes |
| `usage` | object | Latency/tokens/cost riêng v1, v2 và total |
| `limitations` | reason-code array | Không narrative chứa raw prose |
| `decision` | enum/null | `stop`, `collect_more_labels`, `continue_shadow`, hoặc null |
| `decision_reasons` | string[] | Metric/coverage/integrity facts |

Transition:

```text
run/case-set/model invalid hoặc incomplete             -> decision=null
coverage hoặc denominator bắt buộc < 5                 -> collect_more_labels
harmful/unacceptable replace recommendation > 0       -> stop
bất kỳ protected metric regression                     -> stop
keep precision và no-acceptable recall đều không tăng  -> stop
otherwise                                               -> continue_shadow
```

`continue_shadow` không cấp quyền production hay tự động sửa prose.

## Privacy invariants

Mọi generated/committed artifact từ `JudgmentRun` trở đi cấm recursive keys:

```text
source_span candidate_span candidates candidate_origin
context_before context_after current_intent
expected_recommendation expected_source_issues expected_acceptable expected_components expected_safety
label_authority provenance lineage baseline
api_key request_body response_body exception
```

Artifact schema dùng allowlist; exception/service message được map sang reason code trước serialize.
Ngoài key scan, fixture test phải tìm raw source/candidate strings và known personal/organization
tokens trong serialized output.
