# Quickstart Validation: Cổng quyết định sửa hay giữ v2

Các lệnh dưới đây là contract kiểm chứng cho implementation và revision hiện hành. Tên
`recommendation` là chủ ý: output của feature 002 chỉ phục vụ shadow evaluation, không phải lệnh
biên tập cho host Agent.

## Prerequisites

- Python 3.12 và `uv` trong `PATH`.
- V1 artifacts ở commit feature 001 còn nguyên bytes.
- Live command nhận `TYPESAFE_API_KEY` qua secret-injection wrapper đã cấu hình trên máy maintainer;
  repo không ghi tên/path của wrapper và không ghi key vào file/command/log.
- Mỗi gate live, policy freeze và holdout opening có phê duyệt riêng của maintainer hoặc agent được owner ủy quyền rõ.

## 1. Đồng bộ environment đã khóa

```bash
uv sync --locked --group eval
```

Expected: exact resolution hiện có, gồm `typesafe-sdk==0.7.1`; không sửa lockfile.

## 2. Chạy toàn bộ verification offline

```bash
uv run --locked python -m unittest discover -s tests -p 'test_*.py' -v
python3 scripts/validate-package.py
```

Expected: v1 và v2 unit/contract/integration tests pass bằng fake evaluator; không gọi mạng. Package
validator vẫn thấy đúng V/T/profile/version hiện hành.

Các ca bắt buộc gồm:

- source đã tự nhiên nhưng candidate diễn đạt lại hoặc làm mất sắc thái;
- từ/cụm thiếu thành phần và kết hợp từ khô cứng;
- không candidate nào đủ chuẩn;
- candidate sửa đúng lỗi nhưng đổi nghĩa, giọng hoặc lexical nuance;
- shortlist 0, 1 và nhiều candidate;
- Choice winner ngoài shortlist không thể override absolute gate;
- uncertainty/conflict tạo recommendation `review`; service failure ra `unchecked`;
- apply cùng run + policy cho cùng recommendation semantic digest.

## 3. Chứng minh v1 byte-stable và corpus governance

```bash
env -u TYPESAFE_API_KEY \
  uv run --locked --group eval python -m guard_eval.v2 validate \
  --manifest eval/guard/v2/manifest.json
```

Expected: exit 0, không import SDK/call mạng; lock manifest khớp mọi v1 byte; promoted cases chỉ ở
dev và giữ fingerprint. Command chỉ kiểm descriptor, không đọc/parse holdout v2 trước policy freeze.

## 4. Chứng minh fail-open không thành pass

```bash
env -u TYPESAFE_API_KEY \
  uv run --locked --group eval python -m guard_eval.v2 evaluate-dev \
  --manifest eval/guard/v2/manifest.json \
  --authorization specs/002-edit-decision-gate/evidence/dev-revision-approval.json \
  --config eval/guard/v2/evaluation-config.json \
  --output artifacts/guard-eval-v2/no-key.json
```

Expected: exit 2; mọi case `unchecked/missing_api_key`; raw run `policy_version=null`; không có
recommendation, score giả, raw exception hay prose. `python -m guard_eval` và workflow Markdown vẫn chạy.

## 5. Chạy dev absolute judgments

Lệnh live chỉ chạy sau khi maintainer hoặc agent được owner ủy quyền rõ duyệt quota:

```bash
uv run --locked --group eval python -m guard_eval.v2 evaluate-dev \
  --manifest eval/guard/v2/manifest.json \
  --authorization specs/002-edit-decision-gate/evidence/dev-revision-approval.json \
  --config eval/guard/v2/evaluation-config.json \
  --output artifacts/guard-eval-v2/dev-absolute.json
```

Expected: một absolute request mỗi case; exact observed model khớp pin; output chỉ có typed scores,
usage/latency và digests, không labels/recommendation/prose.

## 6. Fit recommendation policy trên dev và thu ranking evidence

Sau khi maintainer hoặc agent được owner ủy quyền rõ duyệt labels/absolute-fit gate:

```bash
uv run --locked --group eval python -m guard_eval.v2 fit-policy \
  --manifest eval/guard/v2/manifest.json \
  --authorization specs/002-edit-decision-gate/evidence/dev-revision-approval.json \
  --config eval/guard/v2/evaluation-config.json \
  --absolute-run artifacts/guard-eval-v2/dev-absolute.json \
  --output-policy artifacts/guard-eval-v2/candidate-policy.json \
  --output-run artifacts/guard-eval-v2/dev-ranked.json
```

Expected: fit absolute thresholds trước, dựng shortlist từ absolute policy đã chọn, chỉ gọi Choice
cho shortlist có ít nhất hai candidate, rồi fit ranking thresholds. Candidate policy ghi full fit
provenance; raw ranked run vẫn `policy_version=null`. Command từ chối candidate policy nếu dev replay
tạo recommendation `replace` cho candidate được gắn nhãn không chấp nhận được hoặc harmful, và
không overwrite frozen policy.

Maintainer review artifact rồi mới chủ động freeze thành `eval/guard/v2/policy.json`.
Nếu `--output-run` đã tồn tại, command chỉ dùng cache khi absolute judgments, current shortlist,
question/model contract đều khớp; cache thiếu/thừa ranking bị từ chối trước khi gọi quota.

Candidate bị reject phải được ghi vào
`specs/002-edit-decision-gate/evidence/policy-candidate-review.json`. Nếu revision đổi question,
config hoặc corpus, tạo proposal/approval mới bind đúng digest trước lần live-run kế tiếp; approval
của candidate cũ không được tái dùng.

## 7. Replay policy offline

```bash
env -u TYPESAFE_API_KEY \
  uv run --locked --group eval python -m guard_eval.v2 apply-policy \
  --manifest eval/guard/v2/manifest.json \
  --run artifacts/guard-eval-v2/dev-ranked.json \
  --policy eval/guard/v2/policy.json \
  --output artifacts/guard-eval-v2/dev-recommendations.json
```

Expected: không gọi mạng; mỗi checked case có đúng một recommendation `keep/review/replace` và
finite reason code; mọi replace trỏ tới candidate trong eligible shortlist. Chạy lại cho cùng
semantic digest; feature 002 không thực thi recommendation lên prose.

## 8. Mở holdout và so v1/v2

Chỉ chạy sau khi maintainer hoặc agent được owner ủy quyền rõ duyệt frozen policy và cho phép mở holdout/quota:

```bash
uv run --locked --group eval python -m guard_eval.v2 holdout \
  --manifest eval/guard/v2/manifest.json \
  --authorization specs/002-edit-decision-gate/evidence/holdout-authorization.json \
  --v1-config eval/guard/evaluation-config.json \
  --v1-policy eval/guard/policy.json \
  --v2-config eval/guard/v2/evaluation-config.json \
  --v2-policy eval/guard/v2/policy.json \
  --pricing eval/guard/v2/pricing.json \
  --output-dir artifacts/guard-eval-v2/holdout
```

Expected:

- hai raw runs riêng trên cùng case IDs/fingerprints;
- lần đọc holdout đầu tiên chỉ xảy ra sau khi frozen-policy preconditions pass; full validator kiểm
  digest, historical leakage, labels và coverage trước live calls;
- authorization bind cả v2 frozen inputs lẫn v1 artifact-lock/config/policy/question/model exact;
- frozen v1/v2 policies áp offline, không fit hoặc sửa holdout;
- metric có numerator/denominator/rate/direction/delta;
- latency/tokens/cost riêng v1, v2 và total;
- go/no-go decision `stop`, `collect_more_labels` hoặc `continue_shadow`; incomplete cho `decision=null`;
- không raw prose, request/response body, secret, raw exception hoặc định danh riêng.

## 9. Chứng minh report replay không cần external evaluator

```bash
env -u TYPESAFE_API_KEY \
  uv run --locked --group eval python -m guard_eval.v2 compare \
  --manifest eval/guard/v2/manifest.json \
  --authorization specs/002-edit-decision-gate/evidence/holdout-authorization.json \
  --v1-run artifacts/guard-eval-v2/holdout/v1-judgments.json \
  --v1-recommendations artifacts/guard-eval-v2/holdout/v1-recommendations.json \
  --v2-run artifacts/guard-eval-v2/holdout/v2-judgments.json \
  --v2-recommendations artifacts/guard-eval-v2/holdout/v2-recommendations.json \
  --pricing eval/guard/v2/pricing.json \
  --output artifacts/guard-eval-v2/holdout/replayed-report.json
```

Expected: exit 0, không gọi mạng; semantic report digest và go/no-go decision khớp report trước dù timestamp
khác. Fit-corpus version có thể khác evaluation-corpus version nhưng mọi contract/model digest phải
khớp.

Nếu candidate policy bị reject, phải thêm regression contract rồi đổi question/config/corpus khi cần.
Mọi drift ở ba input này làm approval dev cũ hết hiệu lực; revision chỉ được live-run sau proposal và
approval mới, không sửa trực tiếp frozen policy.

## 10. Privacy scan và package boundary

```bash
uv run --locked python -m unittest \
  tests.guard_eval_v2.test_report \
  tests.guard_eval_v2.test_cli -v

git diff -- scripts/package-skill.sh
git diff --exit-code -- \
  eval/guard/dev.jsonl eval/guard/evaluation-config.json eval/guard/holdout.jsonl \
  eval/guard/manifest.json eval/guard/policy.json eval/guard/pricing.json \
  specs/001-edit-guard-eval/evidence/corpus-label-proposal.md \
  specs/001-edit-guard-eval/evidence/holdout-report.json
git check-ignore artifacts/guard-eval-v2/probe.json
```

Expected: artifact denylist, raw-string canary và organization-token fixtures đều bị chặn; package
script không đổi và không đưa `guard_eval`, `eval`, `tests`, `artifacts` hay `specs` vào skill.

## 11. Release regression gates

Chỉ khi feature chuẩn bị phát hành:

```bash
python3 scripts/validate-package.py
npx skills add . --list
claude plugin validate .
```

Expected: ba gate hiện hành pass. Live TypeSafe report không thay thế bất kỳ gate nào. Nếu package
payload không đổi như FR-026, không cần cài lại runtime chỉ để phân phối harness nội bộ.
