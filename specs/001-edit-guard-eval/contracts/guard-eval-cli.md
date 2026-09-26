# Contract: `guard_eval` CLI

## Invocation

Mọi command chạy từ repo root:

```bash
uv run --locked --group eval python -m guard_eval <subcommand> [options]
```

Console output chỉ dành cho người đọc. Automation phải dựa vào exit code và JSON artifact.

## Exit codes

| Code | Meaning |
|---:|---|
| `0` | Command hoàn tất; artifact hợp lệ và không có case unchecked |
| `1` | Input, schema, digest, leakage hoặc artifact invalid |
| `2` | Command hoàn tất có kiểm soát nhưng còn case unchecked nên không được kết luận |

## `validate`

```bash
python -m guard_eval validate --manifest eval/guard/manifest.json
```

Validates:

- JSON/JSONL shapes và required fields;
- case id uniqueness;
- từ một đến ba candidate có ID/text duy nhất sau normalize và `candidate_origin` hợp lệ;
- need-to-edit, preferred option, safety và edit-decision consistency;
- maintainer authority cho holdout;
- dev/holdout fingerprint leakage;
- split file digest và computed corpus version;
- không có path thoát khỏi repo.

Không import TypeSafe SDK, không đọc `TYPESAFE_API_KEY` và không gọi mạng.

## `evaluate`

```bash
python -m guard_eval evaluate \
  --manifest eval/guard/manifest.json \
  --config eval/guard/evaluation-config.json \
  --split dev \
  --output artifacts/guard-eval/dev-run.json
```

Preconditions:

- Corpus validation pass.
- Public `evaluate` command chỉ nhận `split=dev`; holdout chỉ được đọc qua `all` sau khi frozen
  policy đã được cung cấp.
- Config digest, corpus version, question-set version và model version nhất quán.
- `TYPESAFE_API_KEY` chỉ đọc từ environment; CLI không nhận key argument.

Postconditions:

- Output có đúng một judgment cho mọi case trong split.
- Output không chứa source, candidate, context, intent, credential hoặc raw exception.
- Output ghi corpus/config/question/model versions, `policy_version=null`, `pricing_version=null`
  và `run_status` độc lập với mọi decision sau này.
- Thiếu key/service failure tạo `unchecked` và exit 2; không tạo pass giả.
- Input/schema error không tạo partial artifact được coi là hợp lệ và exit 1.

## `fit-policy`

```bash
python -m guard_eval fit-policy \
  --manifest eval/guard/manifest.json \
  --config eval/guard/evaluation-config.json \
  --run artifacts/guard-eval/dev-run.json \
  --output artifacts/guard-eval/candidate-policy.json
```

Command chỉ nhận run có `split=dev`. Nó từ chối holdout run, unchecked case, mixed model version
hoặc question-set mismatch. Selection order là contract trong `research.md`; output canonical JSON
có `policy_version` tự băm. Command không overwrite `eval/guard/policy.json`; maintainer phải review
candidate policy rồi chủ động freeze bản được duyệt.

## `report`

```bash
python -m guard_eval report \
  --manifest eval/guard/manifest.json \
  --config eval/guard/evaluation-config.json \
  --policy eval/guard/policy.json \
  --pricing eval/guard/pricing.json \
  --run artifacts/guard-eval/holdout-run.json \
  --output artifacts/guard-eval/holdout-report.json
```

Command tính baseline và evaluator metrics trên cùng ground truth, áp dụng frozen policy rồi ghi
policy/pricing versions. Run invalid hoặc có unchecked holdout tạo `decision=null`; run `complete`
chỉ tạo `collect_more_labels` khi một metric bắt buộc có mẫu số bằng 0. Report phải tách
need-to-edit recall, unnecessary-edit rate, candidate-choice accuracy, no-acceptable-candidate
recall, harmful-edit recall, valid-edit false-block rate, safety false-accept rate và review rate;
không chứa raw prose.

## `all`

```bash
python -m guard_eval all \
  --manifest eval/guard/manifest.json \
  --config eval/guard/evaluation-config.json \
  --policy eval/guard/policy.json \
  --pricing eval/guard/pricing.json \
  --split holdout \
  --output-dir artifacts/guard-eval
```

Thứ tự cố định: `validate → evaluate → report`. `all` chỉ đọc baseline observation đã đóng băng,
không chạy lại workflow Markdown, không fit policy ngầm và không được sửa `eval/guard/policy.json`;
maintainer phải fit, review rồi freeze policy trên dev trước.

## TypeSafe request contract

State gửi đi:

```json
{
  "source_span": "...",
  "candidates": [
    {"candidate_id": "c1", "candidate_span": "..."},
    {"candidate_id": "c2", "candidate_span": "..."}
  ],
  "context_before": "...",
  "context_after": "...",
  "current_intent": "...",
  "genre": "..."
}
```

Questions gồm hai Noul có keys đúng bằng `NaturalnessReason`, một Choice có options
`keep_original`, từng `candidate:<id>` và `none_of_candidates`, cùng sáu safety Noul cho mỗi
candidate. Mỗi Noul có instruction và criteria `true`/`false`; Choice chỉ trả option ID đã cung cấp,
probabilities và confidence. API model phải là version pin trong evaluation config; report kiểm tra
version đó khớp policy đã fit. `question_set_version` băm static templates cùng quy tắc dựng dynamic
options, không băm candidate IDs/text của từng case. Không question nào yêu cầu hoặc cho phép Jev
sinh candidate text.

Các field sau bị cấm trong request: mọi field bắt đầu bằng `expected_`, `candidate_origin`,
`baseline`, `label_source`, `provenance`, `split`, `case_id`. Chúng sẽ làm model thấy đáp án hoặc
gửi dữ liệu không cần thiết.

## Artifact privacy contract

Máy kiểm tra privacy phải serialize output rồi từ chối nếu có bất kỳ key nào sau đây ở mọi độ sâu:

```text
source_span
candidate_span
candidates
candidate_origin
context_before
context_after
current_intent
baseline
label_source
provenance
api_key
request_body
exception
```

Reason code phải thuộc allowlist trong `data-model.md`; message từ SDK không được ghi nguyên văn.
