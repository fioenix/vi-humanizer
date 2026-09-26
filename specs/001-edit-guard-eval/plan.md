# Implementation Plan: Đánh giá guard theo từng edit

**Branch**: `codex/001-edit-guard-eval` | **Date**: 2026-09-26 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/001-edit-guard-eval/spec.md`

## Summary

Xây một evaluation harness tách khỏi gói skill, dùng corpus JSONL có nhãn ở cấp edit để so sánh
baseline đã đóng băng với một evaluator TypeSafe chạy shadow. Host LLM chạy vi-humanizer tạo từ
một đến ba candidate; Jev không viết lại mà chỉ đánh giá source có cần sửa theo V20, chọn giữa bản
gốc/các candidate/không candidate nào và chấm safety cho từng candidate. Code xác thực corpus,
fit threshold trên dev, tổng hợp tất định thành `keep`, `replace` hoặc `review`, rồi chỉ đọc holdout
để tạo báo cáo go/no-go không chứa raw prose. Lệnh đánh giá không chạy lại workflow Markdown.

## Technical Context

**Language/Version**: Python 3.12, khớp runtime CI hiện tại

**Primary Dependencies**: Standard library cho corpus, policy và report; `typesafe-sdk==0.7.1`
chỉ cho evaluator; `uv.lock` khóa toàn bộ dependency của harness

**Storage**: File local bất biến: JSON manifest, JSONL corpus, JSON policy và JSON artifacts;
không có database

**Testing**: `unittest` cho unit/contract/integration với fake evaluator; live TypeSafe chỉ là
smoke test thủ công có credential

**Target Platform**: macOS và Linux có Python 3.12 cùng `uv`; GitHub Actions Ubuntu dùng
Python 3.12 cho verification offline

**Project Type**: Developer CLI nội bộ nằm ngoài nội dung đóng gói của agent skill

**Performance Goals**: Một TypeSafe request cho mỗi case, chứa hai Noul need-to-edit, một Choice
candidate preference và sáu Noul safety cho mỗi candidate; báo cáo latency p50/p95 cùng token
usage thực đo, không đặt SLO trước khi có corpus

**Constraints**: Skill Markdown vẫn chạy offline; Jev không được tạo hoặc sửa candidate text;
không gửi toàn tài liệu khi change hunk và ngữ cảnh cục bộ đã đủ; không log raw prose hoặc secret;
thiếu key, timeout và lỗi dịch vụ phải thành `unchecked`; holdout không được dùng để chỉnh câu hỏi
hoặc threshold

**Scale/Scope**: Corpus feasibility ban đầu ở quy mô hàng chục đến vài trăm edit công khai;
một maintainer, chạy theo batch local, chưa có production traffic

## Constitution Check

*GATE: Passed before Phase 0 research; re-checked after Phase 1 design.*

- **Bằng chứng tiếng Việt trước convention: PASS**. Corpus chỉ lấy bằng chứng công khai trong
  repo, giữ provenance và hard negative; không nhập threshold từ cookbook.
- **Giữ nghĩa và giọng: PASS**. V20 cung cấp positive signal về chỗ cần sửa; sáu safety dimensions
  ánh xạ trực tiếp tới guard 2, 3 và 5. TypeSafe chỉ thẩm định candidate có sẵn, không sinh prose.
- **Tách quy tắc chung và profile: PASS**. Genre, user intent và trường hợp **Không flag** nằm
  trong state; harness không chuyển hoặc tạo pattern.
- **Hiệu chỉnh từ bằng chứng có nhãn: PASS**. Dev/holdout tách biệt, fingerprint chống trùng,
  nhãn holdout cần maintainer xác nhận và policy chỉ được fit trên dev.
- **Behavioral metrics bắt buộc: PASS**. Report giữ harmful-edit recall, valid-edit false-block,
  review rate, lỗi dịch vụ, latency và cost; các metric need-to-edit/preference chỉ bổ sung chứ
  không thay thế cổng safety của constitution.
- **Skill Markdown tự đứng được: PASS**. Dependency nằm trong maintenance harness và không đi
  vào `vi-humanizer.skill`; mọi lỗi external evaluator đều fail-open thành `unchecked`.
- **Gói, dữ liệu và release: PASS**. Output chỉ chứa case id, candidate id, digest, score, status và metrics;
  raw judgment run ghi model/corpus/config cùng `policy_version=null`, còn report áp dụng policy
  ghi policy version; các lệnh validation hiện tại vẫn là release gate.

**Post-design re-check**: PASS. `research.md`, `data-model.md`, contract CLI và quickstart đều
giữ evaluator ở shadow mode, không thêm production hook và không đưa raw prose vào artifact.

## Project Structure

### Documentation (this feature)

```text
specs/001-edit-guard-eval/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── guard-eval-cli.md
├── evidence/
│   └── holdout-report.json  # sanitized decision evidence, created only after authorized live run
├── checklists/
│   └── requirements.md
└── tasks.md                 # chỉ được tạo bởi speckit-tasks sau khi plan được duyệt
```

### Source Code (repository root)

```text
guard_eval/
├── __init__.py
├── __main__.py              # python -m guard_eval
├── cli.py                   # subcommands, exit codes và orchestration
├── models.py                # dataclass, enum và JSON codecs
├── config.py                # evaluation config, pricing snapshot và canonical digests
├── corpus.py                # load, validate, fingerprint và version checks
├── questions.py             # need-to-edit Nouls, preference Choice, safety Nouls và version
├── typesafe_adapter.py      # SDK boundary, timeout và unchecked mapping
├── evaluator.py             # split execution, per-case completeness và run artifact
├── policy.py                # fit trên dev và route keep/replace/review
└── report.py                # metrics, privacy-safe artifact và go/no-go

eval/guard/
├── manifest.json            # split paths, digest và schema/baseline/coverage references
├── dev.jsonl                # raw prose công khai cho calibration
├── holdout.jsonl            # raw prose công khai, maintainer-confirmed labels
├── evaluation-config.json   # model pin, question-set version và request controls
├── policy.json              # frozen thresholds và policy digest
└── pricing.json             # pricing snapshot dùng để ước tính cost của run

tests/guard_eval/
├── test_corpus.py
├── test_config.py
├── test_questions.py
├── test_typesafe_adapter.py
├── test_evaluator.py
├── test_policy.py
├── test_report.py
├── test_cli.py
└── fixtures/
    ├── invalid/
    ├── dev.jsonl
    └── holdout.jsonl

artifacts/guard-eval/         # generated locally; ignored by git
pyproject.toml                # Python 3.12 và dependency group `eval`
uv.lock                       # exact dependency resolution
.github/workflows/validate.yml
.gitignore
```

**Structure Decision**: Đặt harness trong package `guard_eval/` để mỗi module có một trách nhiệm
và test được mà không gọi mạng. Corpus nằm ngoài package để reviewer đọc diff trực tiếp. Không
đưa bất kỳ file nào trong hai thư mục này vào `scripts/package-skill.sh`; gói skill tiếp tục chỉ
chứa `SKILL.md`, `profiles/`, `references/` và `calibration/`.

Raw run artifacts nằm trong thư mục ignored. Sau live holdout run được owner cho phép, sanitized
report không chứa raw prose được ghi vào `specs/001-edit-guard-eval/evidence/holdout-report.json`
để quyết định có bằng chứng review được và không phụ thuộc máy đã chạy.

## Design Decisions

### Evaluation boundary

- Mỗi case gửi một structured state gồm source span, từ một đến ba candidate có ID ổn định, ngữ
  cảnh cục bộ, genre và current user intent. Provenance, expected labels và baseline không được gửi.
- Một request chứa hai Noul độc lập cho `lexically_incomplete` và `unnatural_collocation`, một
  Choice chọn `keep_original`, một candidate ID hoặc `none_of_candidates`, cùng sáu safety Nouls
  cho từng candidate. `question_set_version` băm static question templates và quy tắc dựng option;
  candidate IDs/text của từng case không tham gia version này.
- Jev chỉ trả judgment có cấu trúc. Nó không được tạo, nối, sửa hoặc diễn đạt lại candidate text;
  code mới là nơi áp threshold và quyết định action.
- Model pin `jev-1.13.0` trong `evaluation-config.json`. Nâng model tạo config version mới và
  không tái sử dụng threshold cũ nếu chưa chạy lại dev.

### Candidate generation boundary

- Candidate phải tồn tại trước khi gọi evaluator. Corpus ghi `candidate_origin` là
  `host_llm_output`, `baseline_observation` hoặc `maintainer_fixture`, kèm reference đủ để truy
  ngược. Đường production tương lai chỉ dùng host LLM chạy `vi-humanizer`; fixture/baseline origin
  chỉ phục vụ evaluation. Không có API hay prompt nào yêu cầu Jev sinh candidate.
- Mỗi candidate có ID ổn định, phải khác source và khác các candidate còn lại sau Unicode NFC cùng
  whitespace normalization. Bản gốc luôn là option ngầm; `none_of_candidates` luôn có mặt.
- Giới hạn ba candidate là ràng buộc của feasibility probe để chặn chi phí và độ phức tạp tổ hợp,
  không phải một tuyên bố rằng ba phương án luôn đủ cho mọi bài viết.
- Fingerprint canonical sắp candidate theo ID, nên đổi thứ tự serialize không tạo case mới hoặc đổi
  decision. Choice trả candidate ID chứ không trả vị trí.

### Baseline and ground truth

- Baseline là observation đã đóng băng từ workflow `SKILL.md` hiện tại, do maintainer xác nhận cho
  từng case: source được giữ hay sửa, candidate nào được chọn và guard action của candidate đó.
  Nếu baseline đã sửa source thì text đó phải có mặt trong candidate group và baseline tham chiếu
  candidate ID tương ứng. Baseline không phải ground truth và không được lấy từ evaluator.
- Khi tính preference metrics, baseline `keep` ánh xạ `keep_original`; baseline `replace` ánh xạ
  candidate ID; baseline `review` không có selected candidate ánh xạ `none_of_candidates`. Baseline
  `review` có candidate ID giữ ID đó để phân biệt “không phương án nào đạt” với “candidate cần guard”.
- Ground truth gồm `expected_needs_edit`, `expected_naturalness_reasons`,
  `expected_preferred_option`, safety dimensions theo từng candidate và `expected_edit_decision`,
  có provenance riêng. Báo cáo chấm baseline và evaluator độc lập trên cùng ground truth.
- `evaluate` và `all` không chạy lại workflow Markdown baseline; chúng chỉ xác thực rồi đọc
  observation đã đóng băng trong corpus.
- Không dựng một LLM baseline mới: làm vậy sẽ đo model khác thay vì đo trạng thái hiện tại của
  vi-humanizer.

### Policy fitting and holdout

- Policy có threshold cho hai need-to-edit Nouls, Choice confidence/margin và safety review/reject.
  Mọi threshold được fit từ các giá trị quan sát trên dev; không hardcode số minh họa từ docs.
- Candidate guard action vẫn dùng max của sáu safety Nouls và hai vùng threshold để tạo
  `pass`, `review` hoặc `reject`. Review/reject đều là non-pass khi đo safety false accept.
- Edit transition là tất định: mọi naturalness score dưới threshold và Choice tự tin chọn
  `keep_original` → `keep`; ít nhất một score đạt threshold, Choice tự tin chọn candidate và
  candidate đó `pass` safety → `replace`; mọi tổ hợp còn lại → `review`. `replace` chỉ lưu
  candidate ID đã cung cấp.
- `fit-policy` chọn policy theo thứ tự tất định trên dev: tối đa need-to-edit recall; khi hòa thì
  tối đa candidate-choice accuracy; tiếp theo tối thiểu unacceptable-candidate replace rate,
  unnecessary-edit rate, valid-edit false-block rate, safety false accept và review rate; cuối cùng
  ưu tiên threshold bảo thủ hơn.
  `no_acceptable_candidate_recall` không dùng để chọn threshold vì option Jev đã chọn không đổi theo
  threshold; metric này vẫn là cổng regression trên holdout. Thứ tự được khóa trong policy artifact.
- Raw dev/holdout evaluation chỉ cần evaluation config và luôn ghi `policy_version=null`; nó không
  route action bằng policy. Holdout chỉ được đọc sau khi policy đã có digest. Lệnh report áp dụng
  policy, ghi policy version và từ chối go/no-go nếu corpus digest, config version, policy digest
  hoặc question-set version không khớp evaluation artifact.
- Cost được tính từ token usage và pricing snapshot có source, currency cùng ngày quan sát; thay
  pricing chỉ đổi cost report, không đổi semantic judgment hoặc decision policy.

### Metric definitions

- `need_to_edit_recall`: tỷ lệ case `expected_needs_edit=true` được policy nhận là cần sửa, tức
  decision là `replace` hoặc `review` vì naturalness gate dương.
- `unnecessary_edit_rate`: tỷ lệ case `expected_needs_edit=false` không kết thúc bằng `keep`.
- `candidate_choice_accuracy`: trên các case có `expected_edit_decision=replace`, tỷ lệ policy trả
  `replace` với đúng preferred candidate ID. Case cần safety review không nằm trong mẫu số.
- No-acceptable-candidate recall (`no_acceptable_candidate_recall`): trên các case có preferred option `none_of_candidates`, tỷ lệ
  Choice chọn đúng option đó và final decision là `review`; chọn một candidate dù candidate vẫn an
  toàn về nghĩa cũng được tính là bỏ sót quyền từ chối.
- `valid_edit_false_block_rate`: trên các candidate có expected guard action `pass`, tỷ lệ safety
  policy cho `review` hoặc `reject`; metric này giữ nguyên cổng bắt buộc của constitution và không
  đồng nghĩa với `unnecessary_edit_rate` ở source level.
- `safety_false_accept_rate`: tỷ lệ observed `replace` dùng candidate có expected guard action khác
  `pass`. `harmful_edit_recall` tiếp tục đo tỷ lệ candidate harmful bị safety policy review/reject.

### Failure and privacy behavior

- Thiếu `TYPESAFE_API_KEY`, timeout, authentication error, rate limit hết retry, invalid response
  hoặc partial service failure tạo judgment `unchecked` với reason code; không tạo score giả.
- Exit `0` chỉ khi toàn bộ run hoàn tất và artifact hợp lệ; exit `2` khi run `incomplete` vì có
  case unchecked nên không thể kết luận; exit `1` cho input/schema/integrity error và run `invalid`.
- `collect_more_labels` chỉ là decision của run `complete` khi một metric bắt buộc không tính được
  vì mẫu sạch có mẫu số bằng 0. Run `incomplete` hoặc `invalid` luôn có `decision=null`.
- Per-case artifact chỉ giữ case id, split, digests, option IDs, score/probability/confidence,
  latency, token usage và status; guard/edit action chỉ xuất hiện sau khi report áp dụng policy.
  Exception text được phân loại thành reason code trước khi ghi; request body và API key không log.

## Requirements Coverage

| Requirements | Design owner |
|---|---|
| FR-001–FR-006 | `data-model.md`: edit unit, labels, positive/hard-negative coverage, split và authority |
| FR-007 | `contracts/guard-eval-cli.md`: `all` command, artifacts và exit codes |
| FR-008 | Frozen baseline observation trong corpus; metrics chấm độc lập với candidate |
| FR-009 | Shadow-only boundary trong plan, policy và report decision |
| FR-010 | Structured state có source, candidate group và context; không dùng sentence pairing |
| FR-011 | `unchecked` state, reason-code allowlist và exit 2 |
| FR-012 | Raw `EvaluationRun` ghi corpus/config/model/question, `policy_version=null` và counts; report ghi policy/pricing versions |
| FR-013 | `EvaluationReport` có need/edit, candidate choice, no-acceptable-candidate, harmful recall, valid-edit false-block, safety false accept, review, service, latency, usage và cost metrics |
| FR-014 | Report có coverage và limitations; research ghi rõ mọi dev-time tuning |
| FR-015 | Go/no-go xét naturalness improvement cùng safety regression; holdout digest gates trong report |
| FR-016–FR-017 | Request allowlist và artifact denylist trong CLI contract |
| FR-018 | Dependency chỉ ở maintenance harness; package script không đổi payload |
| FR-019–FR-020 | Positive lane khóa ở V20; safety khóa ở sáu dimensions; không thêm gate, classifier, log builder hoặc hook |
| FR-021–FR-026 | Candidate origin/boundary, Choice contract và deterministic edit transition trong plan/model/CLI contract |
| FR-027 | T018 review corpus và public artifacts; privacy scan chặn narrative nội bộ, dữ liệu khách hàng, định danh riêng và raw prose bị track |

## Complexity Tracking

Không có vi phạm constitution cần biện minh. Dependency external chỉ tồn tại trong harness đánh
giá và giải quyết retry, response validation cùng typed questions; nó không đi vào runtime của
skill Markdown.
