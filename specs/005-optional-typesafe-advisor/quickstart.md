# Quickstart: Xác minh Feature 005

> Retired on 2026-10-03: the TypeSafe implementation and its tests were removed from the repo.
> This is a historical record, not a current task list or runnable guide. See
> `specs/005-optional-typesafe-advisor/spec.md` for the superseding owner decision.

Các lệnh dưới đây là validation contract sau implementation. Chúng không tự cài dependency, không
in key và không dùng quota trừ phần **Live probe**.

## 1. Offline baseline

```bash
python3 scripts/validate-package.py
python3 -m unittest discover -v
```

Kỳ vọng: toàn bộ test xanh; advisor test dùng fake transport và không gọi mạng.

## 2. Core-only khi không có key

```bash
env -u TYPESAFE_API_KEY python3 -m advisor probe
```

Kỳ vọng:

- exit `2`;
- stdout là sanitized JSON với `state=core_only` và `reason_code=missing_api_key`;
- không import `typesafe-sdk`, không gọi mạng, không tạo file;
- core `SKILL.md` vẫn hoàn tất các calibration case hiện có.

## 3. Strict request/privacy contract

```bash
env -u TYPESAFE_API_KEY python3 -m advisor assess \
  < tests/advisor/fixtures/valid-v20.json
```

Kỳ vọng: exit `2` vì thiếu key nhưng input được validate, output có binding và không lặp raw prose.

Chạy fixture có canary/protected field:

```bash
env -u TYPESAFE_API_KEY python3 -m advisor assess \
  < tests/advisor/fixtures/protected-canary.json
```

Kỳ vọng: exit `1` trước network vì schema có field ngoài allowlist; stdout/stderr không chứa canary.

## 4. Stable-key và question-version tests

```bash
python3 -m unittest -v \
  tests.advisor.test_questions \
  tests.advisor.test_models
```

Kỳ vọng:

- candidates serialize thành object keyed, không list;
- mọi question gọi `candidates.<stable_id>.text`, không gọi index;
- candidate order không đổi request digest;
- target đặt đầu/giữa/cuối batch vẫn bind đúng;
- runtime question digest không phụ thuộc hoặc sửa digest frozen v2.

## 5. Fake transport end-to-end

```bash
python3 -m unittest -v \
  tests.advisor.test_client \
  tests.advisor.test_cli
```

Kỳ vọng: checked, timeout, auth, 429, 529, malformed response, model mismatch và stale binding đều
ra đúng exit/status; không raw body hoặc exception xuất hiện.

## 6. Live probe — chỉ sau opt-in

Prerequisite: host đã inject `TYPESAFE_API_KEY` bằng secret mechanism của chính host. Không dán key
vào command, file hoặc chat.

```bash
python3 -m advisor probe
```

Kỳ vọng: exit `0`, `state=advisor_verified`, observed model `jev-1.13.0`, timestamp, latency và usage
thật. Chạy ít nhất hai lần và lưu chỉ sanitized observation nếu cần evidence.

Nếu exit `2`, core workflow vẫn dùng được. Reason code cho biết thiếu key, authentication, timeout,
rate limit, overload, connection, model mismatch hoặc response invalid mà không lộ raw error.

## 7. Live assess — fixture trung tính

Chỉ chạy sau probe và owner approval quota:

```bash
python3 -m advisor assess < tests/advisor/fixtures/valid-v20.json
```

Kỳ vọng: result checked có exact score maps, binding và versions; không có source/candidate prose,
`keep`, `replace`, `reject` hoặc selected candidate.

## 8. Package gates

```bash
./scripts/package-skill.sh
npx skills add . --list
claude plugin validate .
git diff --check
```

Kiểm cả hai archive:

- có exact `advisor/` runtime files và `references/typesafe-advisor.md`;
- không có tests, eval corpus, `guard_eval/`, pyproject, secret hoặc raw evidence;
- source/archive bytes khớp;
- upload Claude Org vẫn chạy core-only nếu host không cho thực thi Python/network/secret injection.

## 9. Release owner gate

Trước khi đổi ba nguồn version và đóng release artifact, owner phải chốt version. Plan không mặc định
`0.9.6` hay `0.10.0`.
