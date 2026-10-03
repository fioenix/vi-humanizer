# Quickstart Validation: Đánh giá guard theo từng edit

> Retired on 2026-10-03: the TypeSafe implementation and its tests were removed from the repo.
> This is a historical record, not a current task list or runnable guide. See
> `specs/005-optional-typesafe-advisor/spec.md` for the superseding owner decision.

Các lệnh dưới đây là contract kiểm chứng sau khi implementation hoàn tất; ở giai đoạn plan hiện
tại chúng chưa chạy được.

## Prerequisites

- Python 3.12.
- `uv` có trong `PATH`.
- `TYPESAFE_API_KEY` được inject qua environment cho bước live; không ghi vào `.env` hoặc command.
- `eval/guard/policy.json` đã được fit và review trên dev trước khi chạy holdout.

## 1. Đồng bộ môi trường khóa version

```bash
uv sync --locked --group eval
```

Expected: cài đúng resolution trong `uv.lock`, gồm `typesafe-sdk==0.7.1`; working tree không đổi.

## 2. Chạy verification offline

```bash
uv run --locked python -m unittest discover -s tests -p 'test_*.py' -v
python3 scripts/validate-package.py
```

Expected: mọi unit/contract/integration test dùng fake evaluator pass, gồm cặp V20 positive/hard
negative, candidate-order invariance và trường hợp `none_of_candidates`; package validator vẫn báo
đúng version và số pattern hiện hành. Không command nào gọi TypeSafe.

## 3. Xác thực corpus mà không có credential

```bash
env -u TYPESAFE_API_KEY \
  uv run --locked --group eval python -m guard_eval validate \
  --manifest eval/guard/manifest.json
```

Expected: exit 0, không gọi mạng, xác nhận dev/holdout không trùng và mọi digest khớp.

## 4. Chứng minh fail-open không biến thành pass

```bash
env -u TYPESAFE_API_KEY \
  uv run --locked --group eval python -m guard_eval all \
  --manifest eval/guard/manifest.json \
  --config eval/guard/evaluation-config.json \
  --policy eval/guard/policy.json \
  --pricing eval/guard/pricing.json \
  --split holdout \
  --output-dir artifacts/guard-eval/no-key
```

Expected: exit 2; mỗi holdout case có status `unchecked` và reason `missing_api_key`; run/report có
`run_status=incomplete`, `decision=null`; skill/package validation vẫn chạy độc lập.

## 5. Chạy dev và fit policy

```bash
uv run --locked --group eval python -m guard_eval evaluate \
  --manifest eval/guard/manifest.json \
  --config eval/guard/evaluation-config.json \
  --split dev \
  --output artifacts/guard-eval/dev-run.json

uv run --locked --group eval python -m guard_eval fit-policy \
  --manifest eval/guard/manifest.json \
  --config eval/guard/evaluation-config.json \
  --run artifacts/guard-eval/dev-run.json \
  --output artifacts/guard-eval/candidate-policy.json
```

Expected: dev run exit 0, ghi config/model/question-set versions cùng `policy_version=null`;
candidate policy khóa threshold need-to-edit, Choice confidence/margin và safety, đồng thời ghi
corpus, config, model và question-set version. Maintainer phải review rồi chủ động thay
`eval/guard/policy.json`; command không tự overwrite frozen policy.

## 6. Chạy holdout bằng một lệnh

```bash
  uv run --locked --group eval python -m guard_eval all \
  --manifest eval/guard/manifest.json \
  --config eval/guard/evaluation-config.json \
  --policy eval/guard/policy.json \
  --pricing eval/guard/pricing.json \
  --split holdout \
  --output-dir artifacts/guard-eval/holdout
```

Expected: exit 0 khi mọi case được chấm; raw run có `policy_version=null`, còn report ghi frozen
policy/pricing versions, baseline/evaluator metrics cho need-to-edit, unnecessary edits, candidate
choice, no-acceptable-candidate recall, harmful-edit recall, valid-edit false-block và safety false
accept, cùng latency, usage, coverage và limitations. Mọi observed `replace` phải tham chiếu
candidate ID đã cung cấp. Run complete có đúng một decision: `stop`,
`collect_more_labels` khi metric bắt buộc có mẫu số bằng 0, hoặc `continue_shadow`. Không decision
nào là production-ready.

## 7. Kiểm tra artifact không rò raw prose

```bash
python3 - <<'PY'
import json
from pathlib import Path

for path in Path("artifacts/guard-eval").rglob("*.json"):
    text = path.read_text(encoding="utf-8")
    data = json.loads(text)
    banned = {
        "source_span", "candidate_span", "candidates", "candidate_origin",
        "context_before", "context_after",
        "current_intent", "baseline", "label_source", "provenance",
        "api_key", "request_body", "exception",
    }

    def keys(value):
        if isinstance(value, dict):
            for key, child in value.items():
                yield key
                yield from keys(child)
        elif isinstance(value, list):
            for child in value:
                yield from keys(child)

    leaked = banned.intersection(keys(data))
    assert not leaked, f"{path}: forbidden keys {sorted(leaked)}"
print("OK: generated artifacts contain no forbidden raw-prose fields")
PY
```

Expected: script in `contracts/guard-eval-cli.md` passes trên toàn bộ generated JSON artifacts.

## 8. Release regression gates

Chỉ khi feature chuẩn bị phát hành:

```bash
python3 scripts/validate-package.py
npx skills add . --list
claude plugin validate .
```

Expected: cả ba gate hiện hành pass. Live TypeSafe run không thay thế bất kỳ gate nào.
