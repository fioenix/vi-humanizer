# Data Model: Cố vấn TypeSafe tùy chọn

## 1. AdvisorCapabilityObservation

Một quan sát tạm thời về năng lực TypeSafe của host; không phải config được persist.

| Field | Type | Required | Rules |
|---|---|---:|---|
| `schema_version` | string | yes | Exact runtime observation version |
| `state` | enum | yes | `core_only`, `advisor_unchecked`, `advisor_verified` |
| `reason_code` | enum/null | yes | Chỉ có ở non-verified state; allowlist, không raw error |
| `observed_model` | string/null | yes | Verified phải đúng pinned model |
| `question_set_version` | sha256/null | yes | Verified phải có |
| `checked_at` | RFC3339 UTC/null | yes | Verified/unchecked live attempt phải có; missing-key MAY null |
| `latency_ms` | integer/null | yes | Không âm; không có khi chưa call |
| `usage` | Usage/null | yes | Chỉ verified; không suy từ pricing/config |

### State transitions

```text
no key / no executable capability ───────────────> core_only
key present + call started ──────────────────────> advisor_unchecked
advisor_unchecked + valid typed pinned response ─> advisor_verified
advisor_verified + later failed/stale call ──────> advisor_unchecked
any state + key removed ─────────────────────────> core_only
```

Không state nào tự được persist làm truth cho session sau.

## 2. AdvisorRequest

Input exact-schema cho `assess`; chỉ chứa dữ liệu Jev cần.

| Field | Type | Required | Rules |
|---|---|---:|---|
| `schema_version` | string | yes | Exact supported version |
| `case_id` | stable key | yes | `[a-z][a-z0-9_]{0,63}`; không dùng list index |
| `source` | SourceSpan | yes | Text V20 cần xét, non-empty NFC |
| `context` | LocalContext | yes | Trước/sau tối thiểu; mỗi field string |
| `current_intent` | string | yes | Non-empty, tối đa 1.000 ký tự, không thêm dữ kiện ngoài lượt hiện tại |
| `genre` | enum | yes | `blog-ca-nhan` hoặc `ky-thuat-doanh-nghiep` |
| `candidates` | map<stable key, Candidate> | yes | 1–3 entry, sorted khi serialize, không trùng text/source |

Field lạ bị từ chối. Schema không có split, label, expected action, provenance, baseline, document
path, user identity hay protected-region bytes.

## 3. SourceSpan / LocalContext / Candidate

### SourceSpan

- `text`: raw source span cần model đọc; non-empty, giữ nguyên Unicode nội dung, tối đa 1.000 ký tự.
- `pattern`: luôn `V20` ở feature này.

### LocalContext

- `before`: chuỗi tối thiểu để hiểu nghĩa/quan hệ; có thể rỗng, tối đa 2.000 ký tự.
- `after`: chuỗi tối thiểu để hiểu nghĩa/quan hệ; có thể rỗng, tối đa 2.000 ký tự.

### Candidate

- `text`: candidate do host LLM tạo trước; non-empty NFC, tối đa 1.000 ký tự.
- Candidate key nằm ở map owner, được question nhắc bằng `candidates.<key>.text`.
- Candidate text không được giống source hoặc candidate khác sau normalization.

## 4. CaseBinding

Digest `sha256:` của canonical request semantic bytes, gồm source, context, intent, genre và candidate
map nhưng không gồm field runtime như timestamp. Mọi result MUST trả binding này.

Binding đổi khi bất kỳ nội dung hoặc candidate set nào đổi. Host chỉ dùng result nếu binding, model
và question version còn khớp.

## 5. AbsoluteAdvisorResult

| Field | Type | Checked | Unchecked |
|---|---|---:|---:|
| `schema_version` | string | yes | yes |
| `status` | `checked`/`unchecked` | `checked` | `unchecked` |
| `case_id` | stable key | yes | yes |
| `case_binding` | sha256 | yes | yes |
| `question_set_version` | sha256 | yes | yes |
| `observed_model` | string/null | pinned | null |
| `source_context_sufficient` | probability/null | value | null |
| `source_issue_scores` | exact map/null | 2 values | null |
| `candidate_component_scores` | exact nested map/null | 3/candidate | null |
| `candidate_safety_scores` | exact nested map/null | 6/candidate | null |
| `reason_code` | enum/null | null | allowlisted value |
| `latency_ms` | integer/null | value | value if call started |
| `usage` | Usage/null | value | null |

Result không có action, selected candidate, raw source/candidate, request/response body hoặc exception.

## 6. RankingRequest / RankingResult

`RankingRequest` chứa cùng `AdvisorRequest` và `eligible_candidate_ids` là exact set 2–3 key đã có.
CLI từ chối shortlist một phần tử, unknown key hoặc duplicate.

Checked `RankingResult` chứa:

- `case_binding`, `ranking_question_set_version`, `observed_model`.
- `eligible_candidate_ids` đã sort.
- `choice`, `probabilities` exact same key set và `confidence`.
- `latency_ms`, `usage`.

Unchecked result chỉ chứa binding/version/shortlist cùng allowlisted `reason_code`; không chứa choice
hoặc probabilities giả.

## 7. Usage

- `input_tokens`: integer không âm từ response thật.
- `output_tokens`: integer không âm từ response thật.
- Không lưu cost trong từng response; sanitized health MAY tính cost từ pricing snapshot riêng nhưng
  không được dùng cost để route.

## 8. Reason codes

Allowlist ban đầu:

- `missing_api_key`
- `execution_unavailable`
- `timeout`
- `authentication`
- `rate_limited`
- `overloaded`
- `connection`
- `invalid_response`
- `model_mismatch`
- `stale_binding`
- `service_error`

Raw HTTP body, provider message và traceback không đi qua data model.
