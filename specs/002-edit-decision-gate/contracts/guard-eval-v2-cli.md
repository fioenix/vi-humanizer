# Contract: `guard_eval.v2` CLI

## Invocation and compatibility

V2 chạy từ repo root:

```bash
uv run --locked --group eval python -m guard_eval.v2 <subcommand> [options]
```

`python -m guard_eval` và toàn bộ command/JSON contract v1 phải giữ nguyên. Console output dành cho
người đọc; automation dựa trên exit code và JSON artifact.

## Exit codes

| Code | Meaning |
|---:|---|
| `0` | Command hoàn tất; output hợp lệ và không có unchecked case |
| `1` | Schema, integrity, provenance, digest, model hoặc leakage invalid |
| `2` | Run có kiểm soát nhưng incomplete vì unchecked case; không được kết luận |

`stop` và `collect_more_labels` là go/no-go outcomes hợp lệ trong report, nên command vẫn exit 0. Chúng
không phải lỗi thực thi.

## `validate`

```bash
python -m guard_eval.v2 validate \
  --manifest eval/guard/v2/manifest.json
```

Validates offline before policy freeze:

- schema, required fields, case/candidate uniqueness và label consistency;
- dev byte digest, declared corpus metadata, exact model/question config digests;
- promoted lineage chỉ ở dev, resolve về v1 bytes/fingerprint đã khóa;
- v1 policy/corpus/config/pricing/report khớp `v1-artifact-lock.json`;
- dev coverage và label consistency;
- path không thoát repo và artifact files chỉ dùng public/neutral provenance.

Command chỉ kiểm shape/path/digest declaration của descriptor holdout; nó không đọc hoặc parse file
holdout. Full holdout digest, historical leakage, label và coverage validation chỉ chạy bên trong
`holdout`, sau khi frozen policy preconditions đã pass. Command không import TypeSafe SDK, không
đọc key và không gọi mạng.

## `evaluate-dev`

```bash
python -m guard_eval.v2 evaluate-dev \
  --manifest eval/guard/v2/manifest.json \
  --authorization specs/002-edit-decision-gate/evidence/dev-revision-approval.json \
  --config eval/guard/v2/evaluation-config.json \
  --output artifacts/guard-eval-v2/dev-judgments.json
```

Preconditions:

- Manifest validation pass.
- Dev-label approval khóa đúng proposal, dev bytes/version, config, model và hai question-set digests.
- Chỉ đọc split `dev`; không có option để đổi sang holdout.
- Config/model/question-set versions khớp code.
- `TYPESAFE_API_KEY` chỉ đọc từ environment; CLI không nhận key argument.

Behavior:

1. Gọi absolute-judgment request một lần mỗi case.
2. Không áp policy, không biết labels/provenance và không dựng Choice ở bước này.
3. Ghi `JudgmentRun` có `policy_version=null`.
4. Thiếu key/service/invalid response ghi `unchecked`, reason code allowlist và exit 2.

Vì shortlist phụ thuộc threshold chưa fit, dev ranking evidence được thu bởi command kế tiếp trong
quá trình fit, dùng candidate policies được tạo từ absolute judgments. Mọi ranking call bổ sung vẫn
được ghi thành raw typed evidence, không ghi recommendation.

## `fit-policy`

```bash
python -m guard_eval.v2 fit-policy \
  --manifest eval/guard/v2/manifest.json \
  --authorization specs/002-edit-decision-gate/evidence/dev-revision-approval.json \
  --config eval/guard/v2/evaluation-config.json \
  --absolute-run artifacts/guard-eval-v2/dev-judgments.json \
  --output-policy artifacts/guard-eval-v2/candidate-policy.json \
  --output-run artifacts/guard-eval-v2/dev-judgments-ranked.json
```

Contract:

- Chỉ nhận complete dev run; từ chối holdout, unchecked, model/question mismatch.
- Sinh các bộ absolute threshold candidate trên dev rồi replay recommendation end-to-end theo
  selection order đã khóa. Loại mọi bộ tạo `replace` cho candidate có
  `expected_acceptable=false` hoặc safety label true trước khi so metric; bộ còn lại tạo đúng một
  shortlist cuối cho mỗi case.
- Với shortlist cuối có ít nhất hai candidate, thu Choice evidence đúng một lần; cache theo
  `case_fingerprint + shortlist + ranking_question_set_version + model`.
- Fit ranking confidence/margin thresholds trên evidence đó; output policy canonical có self-digest.
- Question `preserves_meaning_and_nuance` phải chấm đúng sắc thái của candidate đã có: hoàn chỉnh
  một tổ hợp từ vựng còn thiếu không đồng nghĩa với chấp nhận một từ gần nghĩa làm lệch sắc thái.
- Output run cuối vẫn là raw `JudgmentRun`, `policy_version=null`, chứa ranking evidence đã thực sự
  quan sát. Policy không được ghi recommendation vào raw run.
- Không overwrite `eval/guard/v2/policy.json`. Maintainer review candidate policy và chủ động freeze.
- Nếu question/config/corpus digest đổi sau một candidate bị reject, approval dev cũ không còn hợp
  lệ; command phải yêu cầu proposal/approval mới bind đúng các digest mới.

## `apply-policy`

```bash
python -m guard_eval.v2 apply-policy \
  --manifest eval/guard/v2/manifest.json \
  --run artifacts/guard-eval-v2/dev-judgments-ranked.json \
  --policy eval/guard/v2/policy.json \
  --output artifacts/guard-eval-v2/dev-recommendations.json
```

Pure offline transform:

- Không import SDK, đọc key hoặc gọi mạng.
- Cho phép `policy.fitted_corpus_version != run.corpus_version`; field fit chỉ là provenance.
- Vẫn bắt buộc pipeline/config/question/model khớp.
- Ghi `RecommendationRun` không chứa raw scores; recommendation không được thực thi như runtime command.
- Cùng raw run + policy tạo cùng recommendations và semantic digest.

## `compare`

```bash
python -m guard_eval.v2 compare \
  --manifest eval/guard/v2/manifest.json \
  --authorization specs/002-edit-decision-gate/evidence/holdout-authorization.json \
  --v1-run artifacts/guard-eval-v2/holdout/v1-judgments.json \
  --v1-recommendations artifacts/guard-eval-v2/holdout/v1-recommendations.json \
  --v2-run artifacts/guard-eval-v2/holdout/v2-judgments.json \
  --v2-recommendations artifacts/guard-eval-v2/holdout/v2-recommendations.json \
  --pricing eval/guard/v2/pricing.json \
  --output artifacts/guard-eval-v2/holdout/comparison-report.json
```

Pure offline report:

- Hai pipelines phải có cùng evaluation corpus, case IDs và fingerprints.
- Requested/observed exact model phải giống nhau; nếu khác thì comparison invalid, không gọi đó là
  delta kiến trúc.
- Mỗi metric ghi numerator, denominator, rate, unit, direction, minimum denominator và delta.
- Coverage thiếu tạo `collect_more_labels`; protected regression hoặc harmful/unacceptable
  `replace` recommendation tạo `stop`.
- Disagreement chỉ chứa ID/fingerprint/recommendation/reason code; privacy scan chạy trước khi ghi file.
- Report cost/latency/tokens riêng cho v1, v2 và tổng.

## `holdout`

```bash
python -m guard_eval.v2 holdout \
  --manifest eval/guard/v2/manifest.json \
  --authorization specs/002-edit-decision-gate/evidence/holdout-authorization.json \
  --v1-config eval/guard/evaluation-config.json \
  --v1-policy eval/guard/policy.json \
  --v2-config eval/guard/v2/evaluation-config.json \
  --v2-policy eval/guard/v2/policy.json \
  --pricing eval/guard/v2/pricing.json \
  --output-dir artifacts/guard-eval-v2/holdout
```

Đây là public path duy nhất đọc holdout v2. Preconditions:

- V1 lock, v2 corpus/config và frozen v2 policy đều hợp lệ.
- Frozen v2 policy khớp dev provenance và chưa từng được fit từ holdout.
- Người vận hành đã nhận phê duyệt riêng của maintainer hoặc agent được owner ủy quyền rõ để dùng quota và mở holdout; CLI không tự
  suy diễn quyền này từ sự tồn tại của file.
- Authorization phải khóa đúng corpus, holdout bytes, policy, config và hai question-set digests;
  đồng thời khóa `v1_artifact_lock_sha256`, `v1_artifact_lock_digest`, `v1_config_version`,
  `v1_policy_version`, `v1_question_set_version` và `v1_model_version`. Status chung chung hoặc
  approval của phase trước không hợp lệ.

Fixed order; ba bước đầu phải hoàn tất trước lần đọc đầu tiên của file holdout:

```text
validate dev + v1 byte lock without reading holdout
  → validate frozen v2 policy against dev/config/question/model provenance
  → authorize holdout phase
  → open and fully validate holdout digest/labels/coverage/historical leakage
  → v1-compatible raw evaluation on projected v2 holdout
  → v2 absolute evaluation
  → v2 shortlist ranking where needed
  → apply frozen v1 policy offline và normalize output thành shadow recommendation
  → apply frozen v2 recommendation policy offline
  → compare offline
```

Không fit policy, sửa label/corpus/config hoặc overwrite frozen file. Holdout validator cập nhật
registry chỉ bằng một thay đổi reviewable riêng sau khi run đã được mở; live command không âm thầm
commit hoặc mutate tracked files. Một pipeline incomplete làm
comparison `decision=null` và command exit 2. Mismatch/integrity error exit 1.

## TypeSafe request contract

### Absolute request

State dùng request projection trong `data-model.md`. Questions:

- `source_context_sufficient`;
- `lexically_incomplete`, `unnatural_collocation`;
- mỗi candidate: `fixes_issue`, `preserves_meaning_and_nuance`, `fits_voice_and_genre`;
- mỗi candidate: sáu Noul safety độc lập.

Không question nào yêu cầu model sinh, nối, sửa hoặc đề xuất prose. Questions không thấy labels,
split, provenance, candidate origin, baseline hoặc case ID.

### Ranking request

State chỉ chứa cùng source/context/intent/genre và shortlist candidate đã đủ chuẩn. Choice options
chỉ là `candidate:<id>` cho shortlist; không có `keep_original` hoặc `none_of_candidates`.

Choice instruction ưu tiên: tiếng Việt tự nhiên, giữ intent/voice/lexical nuance và thay đổi tối
thiểu cần thiết. Kết quả chỉ có ranking probabilities/choice/confidence; policy chỉ tạo shadow
recommendation. Host Agent sở hữu quyết định biên tập và câu chữ cuối.

## V1 compatibility contract

- `RecommendationCaseV2` được project sang request-compatible v1 case; v2 labels/lineage không được gửi.
- V1 questions, config, exact model, frozen policy và toàn bộ runtime modules được dùng nguyên bytes
  theo `v1-artifact-lock.json`; bất kỳ drift nào cũng chặn trước khi mở holdout.
- Compatibility runner bọc v1 typed judgment vào envelope `pipeline_version=v1_compat`.
- Khi áp policy v1 lên holdout v2, bỏ equality sai giữa fitted corpus và evaluation corpus nhưng
  vẫn kiểm policy/config/question/model/case fingerprint.
- Baseline observation trong corpus không được dùng thay policy v1.

## Artifact privacy contract

Generated artifacts dùng schema allowlist và từ chối recursive keys trong `data-model.md`. Ngoài
key scan, validator serialize output rồi từ chối nếu chứa exact source/candidate strings, fixture
canary secret, raw SDK message hoặc token thuộc denylist định danh cá nhân/tổ chức.

Artifacts có thể commit chỉ gồm sanitized comparison report và v1 byte-lock evidence. Raw runs và
recommendation runs ở `artifacts/guard-eval-v2/` luôn gitignored.
