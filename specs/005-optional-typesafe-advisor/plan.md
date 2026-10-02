# Implementation Plan: Cố vấn TypeSafe tùy chọn

**Branch**: `005-optional-typesafe-advisor` | **Date**: 2026-09-29 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/005-optional-typesafe-advisor/spec.md`

## Summary

Đưa một advisor CLI tùy chọn, không dependency, vào public skill để host local có thể gửi một edit
V20 cùng 1–3 candidate đã tạo sẵn tới Jev. CLI chỉ trả typed semantic judgments đã bind với input;
host Agent giữ quyền quyết định và câu chữ cuối. `TYPESAFE_API_KEY` là opt-in duy nhất nhưng readiness
chỉ được xác nhận bằng probe thật. Thiếu key, quyền thực thi, mạng hoặc response hợp lệ thì adapter
trả `unchecked`/exit 2 và core Markdown tiếp tục nguyên vẹn. Claude Org ZIP có thể mang adapter như
supporting file nhưng không được tuyên bố TypeSafe hoạt động nếu host không thực thi và probe được.

## Technical Context

**Language/Version**: Markdown; Python 3.10+ standard library cho public advisor CLI; test suite và
evaluation harness hiện khóa Python 3.12

**Primary Dependencies**: Public advisor không có dependency ngoài Python standard library;
`typesafe-sdk==0.7.1` tiếp tục chỉ thuộc dependency group `eval` và không được advisor import

**Storage**: Không có persistent runtime state; capability observation chỉ sống trong invocation
hoặc agent session, còn sanitized evidence dùng file JSON/Markdown đã có governance của repo

**Testing**: `unittest`, fake HTTPS transport, CLI subprocess contract tests, package byte/inventory
tests, validator hiện có và một live probe trung tính chỉ khi owner opt-in quota

**Target Platform**: Local agent hosts có Python 3.10+, shell, HTTPS và environment secret
injection; Claude Org hoặc host Markdown-only chạy core-only nếu không có đủ capability

**Project Type**: Agent skill Markdown kèm optional local CLI; không có server, database hoặc daemon

**Performance Goals**: Mỗi `probe`, `assess` hoặc `rank` dùng tối đa một HTTP request, timeout 8
giây và không retry trong interactive path; lỗi phải trả control cho core ngay sau budget đó

**Constraints**: Jev không sinh/sửa prose; Agent quyết định cuối; chỉ V20; model pin
`jev-1.13.0`; endpoint HTTPS cố định; request tối thiểu; stdout/log/artifact không raw prose; key chỉ
từ environment; question IDs và state dùng stable keys; v1/v2 evaluation artifacts không đổi

**Scale/Scope**: Ba command (`probe`, `assess`, `rank`), 1–3 candidate mỗi edit, hai source issue,
ba candidate components, sáu safety dimensions, một ranking chỉ cho shortlist ≥2 candidate

## Constitution Check

*GATE: Passed before Phase 0 research; re-checked after Phase 1 design.*

| Principle / gate | Pre-design | Post-design |
|---|---|---|
| I. Bằng chứng tiếng Việt trước convention | Scope chỉ dùng lát cắt V20 đã có corpus/eval; không mở pattern mới | Runtime question contract có version riêng và giữ hard negative/Không flag; model vẫn advisory vì coverage chưa đủ |
| II. Giữ nghĩa và giọng trước câu hay hơn | Candidate được tạo trước và chấm tách meaning, voice, safety | CLI trả raw signals, không trả action hoặc prose; Agent phải áp năm chốt chặn trước bản cuối |
| III. Tách quy tắc chung khỏi profile | Feature không đổi V/T/B/K hoặc style resolver | Advisor chỉ chạy sau khi core đã gọi tên V20; style selection không được gửi thành lỗi |
| IV. Hiệu chỉnh từ evidence có nhãn | Không lấy threshold ví dụ từ docs làm policy | Model/question pin; stable-key probe lặp lại; v2 frozen evidence giữ nguyên, runtime contract có digest mới |
| V. Skill Markdown tự đứng được | Public adapter là optional và standard-library | No-key/no-exec/no-network đều exit 2 + core tiếp tục; package không có core dependency mới |
| Package/data | Key không vào file/archive; raw prose chỉ tồn tại trong request cần thiết | Fixed endpoint, exact schema, content binding, sanitized output và package inventory test |
| Development/release | Mọi behavior bắt đầu bằng RED; live quota là gate riêng | Fake transport trong CI; probe thật chỉ sau owner opt-in; release version vẫn là owner gate |

Không có constitution violation cần exception.

## Project Structure

### Documentation (this feature)

```text
specs/005-optional-typesafe-advisor/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── advisor-cli.md
├── checklists/
│   └── requirements.md
└── tasks.md                    # tạo ở bước speckit-tasks, không thuộc plan này
```

### Source Code (repository root)

```text
SKILL.md                        # capability route, khi nào MAY gọi advisor, authority của Agent
README.md                       # setup decision tree, privacy, host/Claude Org capability limits
AGENTS.md                       # ownership của advisor và ranh giới với guard_eval/v2

advisor/
├── __init__.py
├── __main__.py                 # python3 -m advisor
├── cli.py                      # probe/assess/rank, exit codes và JSON I/O
├── client.py                   # fixed HTTPS endpoint, timeout, error allowlist
├── models.py                   # strict runtime request/result schema, content binding
└── questions.py                # runtime-only templates, stable-key state, question digests

references/
└── typesafe-advisor.md         # cách Agent dùng signal và fallback, không chứa threshold action

scripts/
├── validate-package.py         # exact advisor inventory và public contract checks
└── package-skill.sh            # thêm advisor/ vào hai archive từ cùng staged payload

tests/advisor/
├── __init__.py
├── fixtures/
│   ├── valid-v20.json
│   └── protected-canary.json
├── test_cli.py
├── test_client.py
├── test_models.py
└── test_questions.py

tests/test_package_security.py  # archive inventory, no-key/no-secret và adapter bytes

guard_eval/v2/                 # frozen evaluation lane; không import advisor runtime
eval/guard/v2/                 # frozen config/policy/holdout evidence; không đổi bytes
```

**Structure Decision**: `advisor/` là runtime contract mới, độc lập với `guard_eval/v2/`. Không
refactor v2 sang dùng chung code vì request shape v2 đã sinh evidence lịch sử bằng candidate list,
trong khi runtime phải sửa anti-pattern bằng candidate map keyed ổn định. Mỗi lane có owner và
version digest riêng; v2 là frozen evidence, `advisor/questions.py` là nguồn chuẩn duy nhất cho
runtime. Public package thêm nguyên thư mục `advisor/`, còn tests, eval corpus và harness vẫn ở
ngoài archive.

## Complexity Tracking

Không có constitution violation. Adapter riêng thay vì tái dùng `guard_eval/v2` là ranh giới bắt
buộc để không biến evaluation schema có label/provenance thành public runtime payload và không sửa
bytes/digest của evidence đã khóa.
