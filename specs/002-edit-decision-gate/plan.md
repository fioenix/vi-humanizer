# Implementation Plan: Cổng quyết định sửa hay giữ v2

**Branch**: `codex/002-edit-decision-gate` | **Date**: 2026-09-28 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/002-edit-decision-gate/spec.md`

## Summary

Mở một lane `guard_eval.v2` song song, không đổi semantics, public CLI hay bytes artifact của
feature 001. Host LLM/Agent giữ quyền quyết định biên tập và câu chữ cuối. Jev chỉ tạo các phán
đoán tuyệt đối có cấu trúc về source, từng candidate và safety; code suy ra candidate đủ chuẩn,
chỉ dùng `Choice` để xếp hạng từ hai candidate đủ chuẩn trở lên, rồi policy tất định tạo
`keep`, `review` hoặc `replace` recommendation cho evaluation shadow. Raw judgment được tách khỏi
recommendation run để replay threshold offline. Holdout v2 được hai pipeline v1/v2 chấm bằng hai
raw run riêng trên cùng case set, sau đó report so metric có tử số, mẫu số và chiều cải thiện.

## Technical Context

**Language/Version**: Python 3.12, giữ cùng runtime đã khóa của harness v1

**Primary Dependencies**: Python standard library cho schema, policy, digest và report;
`typesafe-sdk==0.7.1` đã khóa trong `uv.lock` cho live semantic judgments

**Storage**: File local bất biến: JSON manifest/config/policy/lock, JSONL corpus và JSON artifact;
không có database

**Testing**: `unittest` cho unit/contract/integration offline với fake evaluator; live TypeSafe chỉ
chạy ở các gate được maintainer hoặc agent được owner ủy quyền rõ duyệt

**Target Platform**: macOS và Linux có Python 3.12 cùng `uv`; GitHub Actions Ubuntu chỉ chạy
verification offline

**Project Type**: Developer evaluation CLI nội bộ, tách khỏi payload Markdown của skill

**Performance Goals**: Một absolute-judgment request cho mỗi case; request Choice thứ hai chỉ khi
có ít nhất hai candidate đủ chuẩn; report latency, token usage và cost thực đo cho từng pipeline

**Constraints**: Giữ v1 byte-stable; Agent sở hữu quyết định biên tập cuối; Jev không sinh/sửa
prose; code v2 không thực thi recommendation; không gửi label/provenance; không commit raw prose
trong artifact; lỗi external service thành `unchecked`; holdout v2 chỉ mở sau khi policy được duyệt
và khóa; không thay V/T/profile/package payload

**Scale/Scope**: Một maintainer, corpus hàng chục case; holdout tối thiểu năm case cho mỗi recommendation
class và mỗi slice bắt buộc; hai pipeline, hai raw runs, một comparison report

## Constitution Check

*GATE: Passed before Phase 0 research; re-checked after Phase 1 design.*

- **Bằng chứng tiếng Việt trước convention: PASS**. V2 giữ các hiện tượng có nhãn
  `lexically_incomplete` và `unnatural_collocation`, thêm hard negatives theo thể loại và không
  biến một cách diễn đạt khác thành lỗi.
- **Giữ nghĩa và giọng: PASS**. Candidate chỉ đủ chuẩn khi sửa đúng lỗi, giữ nghĩa và sắc thái,
  hợp giọng/thể loại và không vướng safety risk. Choice không thể override cổng này.
- **Tách quy tắc chung và profile: PASS**. `genre`, intent và voice là state của evaluation; feature
  không sửa V-series, T-series hay profile.
- **Hiệu chỉnh từ bằng chứng có nhãn: PASS**. Holdout v1 đã xem chỉ được promote vào dev v2 với
  lineage bất biến; holdout v2 chống trùng xuyên iteration và chỉ mở sau policy freeze.
- **Skill Markdown tự đứng được: PASS**. Toàn bộ v2 nằm trong maintenance harness; thiếu key hoặc
  lỗi dịch vụ tạo `unchecked`, không ảnh hưởng workflow Markdown.
- **Traceability: PASS**. Raw `JudgmentRun` có `policy_version=null`; `RecommendationRun` ghi policy
  đã áp; `ComparisonReport` giữ digests, counts, denominators, model, usage và cost.
- **Behavioral/release gates: PASS**. Test bắt đầu từ ca đỏ; live evaluation ở shadow mode; release
  gates hiện hành vẫn bắt buộc và không được thay bằng kết quả TypeSafe.

**Post-design re-check**: PASS. `research.md`, `data-model.md`, CLI contract và quickstart đều giữ
Agent ở authority biên tập, TypeSafe ở vai trò thẩm định, tách raw judgment khỏi recommendation
policy, khóa v1 và không mở đường production.

## Project Structure

### Documentation (this feature)

```text
specs/002-edit-decision-gate/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── guard-eval-v2-cli.md
├── evidence/            # approval/rejection và sanitized report theo từng gate
├── checklists/
│   └── requirements.md
└── tasks.md             # chỉ tạo bởi speckit-tasks sau khi plan được duyệt
```

### Source Code (repository root)

```text
guard_eval/                 # v1 public contract; không đổi semantics
└── v2/
    ├── __init__.py
    ├── __main__.py         # python -m guard_eval.v2
    ├── cli.py              # v2 commands và paired holdout orchestration
    ├── models.py           # v2 corpus/judgment/recommendation/report types
    ├── config.py           # exact model/question pins, retry controls và pricing
    ├── corpus.py           # schema, lineage, historical leakage và v1 projection
    ├── questions.py        # absolute Nouls và shortlist Choice
    ├── typesafe_adapter.py # two-stage request, typed parse, unchecked mapping
    ├── evaluator.py        # JudgmentRun v2 và compatible v1 run trên v2 cases
    ├── policy.py           # fit/replay deterministic shadow recommendations
    ├── report.py           # denominator-aware paired comparison
    └── privacy.py          # shared v2 artifact denylist validation

eval/guard/                 # feature 001 files giữ nguyên bytes
├── ...                     # existing v1 corpus/config/policy/pricing
└── v2/
    ├── manifest.json
    ├── dev.jsonl
    ├── holdout.jsonl        # chỉ xuất hiện sau T052; trước đó manifest ghi pending
    ├── evaluation-config.json
    ├── policy.json
    ├── pricing.json
    ├── observed-holdouts.json
    └── v1-artifact-lock.json

tests/guard_eval/            # v1 regression suite giữ nguyên
tests/guard_eval_v2/
├── test_models.py
├── test_corpus.py
├── test_questions.py
├── test_typesafe_adapter.py
├── test_evaluator.py
├── test_policy.py
├── test_report.py
├── test_cli.py
└── fixtures/

artifacts/guard-eval-v2/    # generated locally; ignored by git
```

**Structure Decision**: Dùng namespace `guard_eval.v2` thay vì thêm cờ version vào module v1 vì
schema Choice, judgment, policy và report v1 đều hard-code semantics cũ. Utility thuần như Unicode
normalize hoặc canonical digest có thể được tái dùng bằng import; mọi contract có semantics đổi
được định nghĩa trong v2. Corpus v2 nằm dưới `eval/guard/v2/`, còn lock manifest liệt kê chính xác
mọi file v1 phải byte-stable. Package script không được thêm bất kỳ đường dẫn harness nào.

## Design Decisions

### Semantic question graph

- Request tuyệt đối chứa `source_context_sufficient`, hai Noul nguồn
  `lexically_incomplete`/`unnatural_collocation`, và với từng candidate: `fixes_issue`,
  `preserves_meaning_and_nuance`, `fits_voice_and_genre` cùng sáu safety Nouls hẹp.
- Không hỏi cả `source_is_good` và `source_needs_edit`. Code dùng nhánh `no` của chính các Noul lỗi
  để suy ra source đã ổn; không giả định xác suất của hai câu hỏi đối nghịch cộng thành một.
- `candidate_acceptable` là predicate tất định từ các component đã fit threshold, không phải một
  Noul tổng hợp thứ hai. Ground truth vẫn gắn nhãn acceptability cho từng candidate.
- Sau absolute request, code tạo shortlist. Shortlist rỗng ra `review`; một candidate không cần
  Choice; từ hai candidate trở lên mới gọi request Choice chỉ chứa candidate IDs đủ chuẩn.
- Choice chỉ xếp hạng tương đối. Nó không có `keep_original`, `none_of_candidates`, quyền safety
  hoặc quyền `replace`.

### Recommendation transition

```text
run thiếu hoặc invalid                                  -> unchecked
context không đủ; signal vùng giữa hoặc mâu thuẫn       -> recommend review
không có lỗi nguồn đủ mạnh                              -> recommend keep
có lỗi nguồn nhưng shortlist rỗng                       -> recommend review
shortlist có đúng một candidate                         -> recommend replace(candidate)
shortlist có nhiều candidate + Choice không đủ rõ       -> recommend review
shortlist có nhiều candidate + Choice đủ rõ             -> recommend replace(winner)
```

Mọi recommendation `replace` chỉ nhận candidate đã qua acceptability và safety. Threshold chỉ được
fit trên dev; không lấy số ví dụ trong docs TypeSafe làm mặc định. Reason code là enum hữu hạn và
mô tả nhánh policy, không chứa prose hay exception. Recommendation không được thực thi trong feature
002; host Agent không phải consumer runtime của CLI shadow này.

### Artifact and comparison boundary

- `JudgmentRun` giữ typed scores/probabilities và telemetry, không labels, threshold hay recommendation;
  `policy_version=null`.
- `RecommendationRun` chỉ giữ recommendation, candidate IDs/assessments, reason codes và digests;
  không lặp raw scores.
- V1 và v2 tạo hai `JudgmentRun` riêng trên cùng holdout v2 vì question contracts khác nhau. V2
  project case sang schema request v1 mà không gửi v2 labels/lineage.
- `corpus_version_fitted` là provenance của policy, không phải lệnh cấm áp policy lên corpus đánh
  giá khác. Compatibility layer vẫn bắt khớp pipeline, question set, config và observed model.
- `ComparisonReport` chỉ được tính khi hai recommendation run có cùng case IDs, fingerprints và holdout
  corpus. Report ghi từng metric dưới dạng numerator/denominator/rate/direction và delta có hướng.

### Corpus governance

- Case v1 đã quan sát được copy semantic content vào dev v2, có lineage trỏ về source path,
  byte digest, case ID, fingerprint và corpus version. Promote rồi sửa semantic content là invalid.
- Registry `observed-holdouts.json` khóa fingerprint của mọi holdout đã mở. Holdout v2 không được
  trùng registry; case promoted chỉ hợp lệ ở dev. Dev validation không đọc holdout; full digest,
  label, leakage và coverage validation chỉ chạy sau frozen-policy gate trong command `holdout`.
- Trước T052, descriptor holdout có `status=pending`, `sealed=false`, digest/count null và file chưa
  tồn tại. Chỉ authorization khóa đúng frozen inputs mới cho phép đổi descriptor sang `sealed`.
- `dev_version` chỉ băm dev records và khóa policy fit/freeze; `corpus_version` băm thêm holdout
  identity cho paired evaluation. Vì vậy seal holdout không làm policy đã duyệt ở T051 mất hiệu lực.
- `v1-artifact-lock.json` liệt kê path và SHA-256 của policy, corpus, config, pricing và report đã
  commit. Offline test từ chối bất kỳ byte drift nào.
- Holdout coverage đếm theo case cho `keep`, `review`, `replace`, no-acceptable và harmful slices;
  candidate-level metric vẫn dùng candidate làm đơn vị khi định nghĩa yêu cầu.

### Metrics and go/no-go

- Protected metrics: harmful-edit recall, keep precision, no-acceptable-candidate recall,
  valid-edit false-block rate và candidate-choice accuracy; hard invariants
  `harmful_replace_recommendation_count == 0` và
  `unacceptable_replace_recommendation_count == 0`.
- Diagnostic metrics: keep recall, review rate, review-on-expected-keep, unwanted replace on
  expected keep, safety false accept, latency, token usage và cost riêng cho v1/v2/tổng.
- Coverage dưới 5 ở bất kỳ recommendation class hoặc slice bắt buộc nào ra `collect_more_labels`.
  Prediction-dependent denominator của keep precision dưới 5 cũng chặn với reason riêng.
- Một protected regression hoặc harmful `replace` recommendation ra `stop`. Nếu không regression, keep
  precision và no-acceptable recall phải có ít nhất một metric tăng nghiêm ngặt mới có thể
  `continue_shadow`. Kết quả này không cấp quyền production.

### Rejected candidate revision

- Candidate policy đầu tiên và kết quả replay 6/9 được lưu thành rejection evidence sanitized;
  không sửa hoặc trình bày lại artifact đó như một candidate đã duyệt.
- Contract v2 dùng `CandidateAssessment` và `candidate_assessments`; không giữ tên `CandidateAction`
  hoặc compatibility alias làm evaluator trông như executor.
- Regression test phải tái hiện ca candidate không chấp nhận được từng nhận recommendation
  `replace` trước khi sửa fitter hoặc question contract.
- `preserves_meaning_and_nuance` phải phân biệt việc hoàn chỉnh một tổ hợp từ vựng còn thiếu với
  việc thay bằng từ gần nghĩa nhưng làm lệch sắc thái; Jev vẫn chỉ chấm candidate đã được cung cấp.
- Fitter chọn policy bằng replay end-to-end trên dev. Mọi threshold tuple tạo `replace` cho candidate
  có `expected_acceptable=false` hoặc safety label true bị loại trước khi so các metric còn lại.
- Vì question-set/config/corpus digest thay đổi, approval T049 cũ không được tái dùng. Revision phải
  tạo proposal mới, nhận approval mới, chạy live dev lại rồi mới trình candidate policy kế tiếp.
- Chỉ sau khi maintainer hoặc agent được owner ủy quyền rõ duyệt candidate kế tiếp mới được freeze `eval/guard/v2/policy.json` và mở
  authorization riêng cho holdout. Không có bước nào trao quyền sửa prose cho code hoặc Jev.

## Requirements Coverage

| Requirements | Design owner |
|---|---|
| FR-001, FR-013, FR-014, FR-023, FR-025 | Corpus lineage, observed-holdout registry, v1 artifact lock và CLI holdout gate |
| FR-002, FR-006–FR-010, FR-027 | `RecommendationPolicyV2` truth table, finite reason codes, `RecommendationRun` contract và shadow-only authority |
| FR-003–FR-005 | Component Nouls, derived candidate acceptability và shortlist-only Choice |
| FR-011, FR-018 | `JudgmentRun → RecommendationRun → ComparisonReport` separation |
| FR-012, FR-015 | `RecommendationCaseV2`, per-candidate labels, provenance và coverage rules |
| FR-016–FR-017 | `MetricValue`, paired v1/v2 evaluation và go/no-go transition |
| FR-019, FR-021–FR-022, FR-024 | Privacy denylist, unchecked mapping, neutral fixtures và model pin/mismatch validation |
| FR-020, FR-026 | Separate shadow CLI/package namespace; no Markdown workflow or package payload changes |

## Complexity Tracking

Không có vi phạm constitution cần biện minh. Lane v2 tạo thêm module vì bốn contract v1 thay đổi
semantics đồng thời; thêm cờ version vào code v1 sẽ làm tăng nguy cơ digest drift và phá khả năng
replay bằng chứng feature 001.
