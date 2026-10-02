# Contract: Optional TypeSafe Advisor CLI

## Invocation

Chạy từ skill root:

```bash
python3 -m advisor probe
python3 -m advisor assess
python3 -m advisor rank
```

`assess` và `rank` đọc đúng một JSON object từ stdin. Không command nào nhận API key, source text,
candidate text hoặc endpoint qua command-line argument.

## Exit codes

| Code | Meaning | Host behavior |
|---:|---|---|
| `0` | Checked result hợp lệ | Agent MAY đọc signal; vẫn tự quyết định |
| `1` | Caller contract/input invalid | Agent sửa invocation; không gọi core result là checked |
| `2` | Optional advisor unavailable/unchecked | Tiếp tục core workflow, ghi *chưa kiểm tra* nếu cần status |

Keyboard interrupt và process termination không được nuốt thành exit 2.

## Output channel

- Stdout: đúng một JSON object canonical, UTF-8, newline cuối file.
- Stderr: chỉ message hữu hạn cho invalid invocation; không raw exception, request, response hoặc prose.
- Không command nào ghi file hoặc log mặc định.

## `probe`

Không nhận stdin prose. CLI dùng một fixture trung tính cố định và một Noul question cố định để kiểm
key, network, endpoint, response schema và observed model.

### Checked output / exit 0

```json
{
  "checked_at": "2026-09-29T00:00:00Z",
  "latency_ms": 120,
  "observed_model": "jev-1.13.0",
  "question_set_version": "sha256:<64-hex>",
  "reason_code": null,
  "schema_version": "1.0.0",
  "state": "advisor_verified",
  "usage": {"input_tokens": 1, "output_tokens": 1}
}
```

### Missing key / exit 2

`state=core_only`, `reason_code=missing_api_key`, không có model/usage.

### Attempt failed / exit 2

`state=advisor_unchecked`, reason code thuộc allowlist, không raw service detail.

## `assess`

Input theo `AdvisorRequest` trong [data-model.md](../data-model.md). Candidates là object keyed:

```json
{
  "case_id": "v20_case_01",
  "candidates": {
    "candidate_1": {"text": "Câu này đọc lên thấy hụt hẫng."}
  },
  "context": {"after": "", "before": ""},
  "current_intent": "Giữ giọng nhận xét trực tiếp.",
  "genre": "blog-ca-nhan",
  "schema_version": "1.0.0",
  "source": {"pattern": "V20", "text": "Câu này đọc lên thấy hụt."}
}
```

Checked output theo `AbsoluteAdvisorResult`. Exact keys:

- Hai source issues: `lexically_incomplete`, `unnatural_collocation`.
- Ba candidate components: `fixes_issue`, `preserves_meaning_and_nuance`,
  `fits_voice_and_genre`.
- Sáu safety dimensions: `adds_claim`, `changes_actor_or_time`,
  `changes_causality_or_commitment`, `changes_order_or_concurrency`, `changes_register`,
  `keeps_invalid_process_metadata`.

CLI không trả recommendation hoặc prose.

## `rank`

Input là exact `AdvisorRequest` cộng `eligible_candidate_ids`. Shortlist phải có 2–3 ID đã tồn tại.
Question criteria trỏ từng option vào `candidates.<id>.text`; option order canonical theo ID.

Checked output có exact shortlist, choice, full probabilities, confidence, binding, versions, model,
latency và usage. Nó không có `keep_original` hay `none_of_candidates`; việc có sửa hay không đã nằm
ngoài lệnh ranking và thuộc Agent.

## Provider boundary

- Endpoint: fixed HTTPS TypeSafe System One endpoint.
- Model request/observed: exact `jev-1.13.0`.
- Authorization: bearer value chỉ đọc từ `TYPESAFE_API_KEY`.
- Timeout: 8 giây; 1 attempt; không background retry.
- Response body tối đa 1 MiB; lớn hơn được map thành `invalid_response` trước khi JSON decode.
- HTTP/provider errors map sang allowlisted reason code; body không được phản chiếu ra output.

## Binding and freshness

Host MUST so `case_binding`, question version và observed model trước khi dùng result. Nếu source,
context, intent, genre, candidate text hoặc candidate set đổi, host bỏ result và MAY gọi lại trên
input mới. Một probe cũ không làm lần `assess` mới thành checked.

## Privacy contract

- Không chấp nhận field ngoài schema; label/provenance/baseline bị từ chối trước network.
- Reject trước network nếu source/candidate vượt 1.000 ký tự, context trước/sau vượt 2.000 ký tự
  mỗi phần hoặc current intent vượt 1.000 ký tự.
- Protected region không được đưa vào source/context.
- Request chỉ sống trong memory của process và HTTPS call; không log hoặc ghi file.
- Output/artifact không chứa raw source, raw candidate, raw provider response hoặc secret.
- Không follow HTTP redirect để tránh chuyển bearer token sang endpoint ngoài contract.
