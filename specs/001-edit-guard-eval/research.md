# Research: Đánh giá guard theo từng edit

## 1. Runtime và dependency

**Decision**: Dùng Python 3.12, `uv` và dependency group `eval` có
`typesafe-sdk==0.7.1`; commit `uv.lock`. Phần còn lại dùng standard library và `unittest`.

**Rationale**: CI hiện dùng Python 3.12. SDK 0.7.1 yêu cầu Python từ 3.10, có typed questions,
response validation, timeout và retry policy. Viết lại HTTP client sẽ tạo thêm code ở đúng ranh
giới dễ sai nhất nhưng không tăng giá trị cho feasibility probe. Dependency chỉ phục vụ maintenance
harness và không được đóng gói cùng skill.

**Alternatives considered**:

- HTTP API trực tiếp bằng `urllib`: ít dependency nhưng phải tự xử lý retry, rate limit, timeout
  và response validation.
- Cài SDK toàn cục: khó tái lập và trái yêu cầu khóa version.
- Chuyển sang Node.js: repo và validator hiện đã dùng Python; thêm runtime thứ hai không có lợi.

**Sources**: [Python SDK](https://docs.typesafe.ai/sdk/python.md),
[SDK changelog](https://docs.typesafe.ai/sdk/python/changelog.md),
[API errors and retries](https://docs.typesafe.ai/api.md#errors)

## 2. Primitive và request shape

**Decision**: Dùng một request trên structured state với ba nhóm primitive:

1. Hai Noul source-level: `lexically_incomplete`, `unnatural_collocation`.
2. Một Choice với options `keep_original`, từng `candidate:<id>` và `none_of_candidates`.
3. Sáu Noul safety cho từng candidate: `adds_claim`, `changes_actor_or_time`,
   `changes_causality_or_commitment`, `changes_order_or_concurrency`, `changes_register`,
   `keeps_invalid_process_metadata`.

**Rationale**: Noul phù hợp với từng mệnh đề yes/no; Choice phù hợp với một lựa chọn loại trừ lẫn
nhau và trả phân bố xác suất/confidence trên toàn bộ options. `none_of_candidates` cho phép nói
source cần sửa nhưng các phương án hiện có đều không đạt. Batching giữ source, preference và safety
trên cùng state nhưng từng question vẫn độc lập. Code giữ raw probabilities/confidence và tự quyết
threshold/action; Jev không được yêu cầu viết prose.

**Alternatives considered**:

- Yêu cầu Jev viết candidate: sai vai trò; biến evaluator thành generator và không chứng minh được
  phương án cuối thuộc tập đã review.
- Một Choice duy nhất chọn loại vi phạm: sai vì một edit có thể vi phạm nhiều chiều đồng thời.
- Một Score “mức độ có hại”: gộp nhiều nghĩa vào một trục và làm mất lý do review.
- Một Noul tổng hợp “edit này có hại không”: khó chẩn đoán và khó biết câu hỏi nào cần hiệu chỉnh.

**Sources**: [Noul](https://docs.typesafe.ai/primitives/noul),
[Choice](https://docs.typesafe.ai/primitives/choice),
[Composite scoring](https://docs.typesafe.ai/patterns/composite-scoring),
[Confidence routing](https://docs.typesafe.ai/patterns/confidence-routing)

## 3. Model version

**Decision**: Pin `jev-1.13.0` trong versioned evaluation config và ghi model thật từ response vào
từng evaluation artifact. Frozen policy tham chiếu đúng config version đã dùng để fit. Không dùng
`jev-latest` cho benchmark chính.

**Rationale**: Alias có thể đổi mà không đổi code; threshold đã fit theo một version không được
coi là hợp lệ cho version mới. Jev hiện ưu tiên tiếng Anh và yêu cầu kiểm thử riêng cho workload
ngoài tiếng Anh, nên corpus tiếng Việt là điều kiện bắt buộc chứ không phải bước tùy chọn.

**Alternatives considered**:

- `jev-latest`: tiện cho khám phá nhưng làm benchmark khó tái lập.
- `jev-preview`: không phù hợp cho bằng chứng quyết định và hiện không có preview riêng.

**Source**: [TypeSafe models](https://docs.typesafe.ai/models.md)

## 4. Corpus và versioning

**Decision**: Lưu case trong JSONL, một source cùng nhóm một đến ba candidate mỗi dòng; manifest
JSON chỉ định split và SHA-256. Corpus version là digest của canonical content, không phải số
version do người viết tự tăng.

**Rationale**: JSONL tạo diff hẹp, stream được và cho phép mỗi case có raw prose nhiều dòng dưới
dạng chuỗi JSON. Digest phát hiện case bị sửa sau khi đã tạo báo cáo. Fingerprint chống leakage
được tính từ source, candidates đã sắp theo candidate ID, context và intent sau khi chuẩn hóa
Unicode NFC cùng whitespace; case id và thứ tự serialize candidate không tham gia fingerprint.

**Alternatives considered**:

- CSV: không phù hợp với multiline prose và nested labels.
- YAML: dễ đọc nhưng cần parser ngoài và có nhiều cách serialize tương đương.
- Một JSON array lớn: mỗi edit có thể tạo diff nhiều dòng không cần thiết.

## 5. Baseline

**Decision**: Baseline là observation đã đóng băng của workflow `SKILL.md` 0.7.1 trên từng case,
do maintainer xác nhận và có provenance. Nó ghi source được giữ hay sửa, candidate được chọn nếu có
và guard action. Baseline observation tách khỏi expected label.

**Rationale**: Repo chưa có executable baseline; dựng thêm một LLM baseline sẽ đo một hệ thống
mới chứ không đo hành vi hiện tại. Một observation được xác nhận cho phép tính baseline metrics
trên đúng case mà không đưa candidate answer vào baseline. Khi workflow thay đổi, tạo baseline
version mới thay vì sửa observation cũ.

Lệnh `evaluate` và `all` không chạy lại workflow Markdown. Chúng xác thực version/provenance của
baseline observation đã đóng băng rồi chấm candidate độc lập trên cùng ground truth.

**Alternatives considered**:

- Dùng ground truth làm baseline: tạo baseline hoàn hảo giả và khiến phép so sánh vô nghĩa.
- Chạy một general-purpose LLM với toàn bộ `SKILL.md`: thêm model, prompt và runtime ngoài phạm vi.
- Không có baseline: chỉ đo accuracy tuyệt đối, không trả lời candidate có cải thiện hiện trạng hay
  không.

## 6. Fit policy mà không làm nhiễm holdout

**Decision**: Từ dev, duyệt các giá trị quan sát để chọn threshold cho need-to-edit Nouls,
preference confidence/margin và safety review/reject. Policy được canonicalize, băm rồi khóa trước
khi đọc holdout.

Thứ tự chọn tất định:

1. need-to-edit recall cao hơn;
2. candidate-choice accuracy cao hơn;
3. unacceptable-candidate replace rate thấp hơn;
4. unnecessary-edit rate, valid-edit false-block rate và safety false-accept rate thấp hơn;
5. review rate thấp hơn;
6. threshold bảo thủ hơn nếu mọi chỉ số trên bằng nhau.

Code tổng hợp theo transition `keep`/`replace`/`review`; Jev chỉ cung cấp judgment. Review/reject
đều là non-pass khi tính safety. Holdout chỉ dùng để đo policy đã khóa và không được dùng để viết
lại questions, thêm candidate hoặc chọn threshold.

`no_acceptable_candidate_recall` được báo cáo và dùng làm holdout regression gate nhưng không tham
gia thứ tự fit: Choice đã chọn `none_of_candidates` hay không là raw judgment, không thay đổi khi
dịch threshold. Thay vào đó, fitter giảm `unacceptable_candidate_replace_rate`: trên các case dev
có ground truth `none_of_candidates`, policy không được giảm review rate bằng cách cho `replace`.
Metric này thay đổi được theo confidence/margin threshold và chỉ bảo vệ action; nó không biến một
raw Choice sai thành đúng.

**Rationale**: TypeSafe khuyến nghị threshold theo dữ liệu và hậu quả của domain, không dùng số
demo như quy tắc phổ quát. Việc tính review là false block đối với valid edit ngăn policy “review
mọi thứ” thắng giả bằng recall.

**Alternatives considered**:

- Ngưỡng cố định 0.5: không phản ánh chi phí false positive và đặc thù tiếng Việt.
- Một score tổng hợp do Jev trả: che mất xung đột giữa “nên sửa” và “candidate không an toàn”.
- Threshold riêng cho mọi safety dimension: dễ overfit corpus feasibility nhỏ.
- Fit lại trên holdout: phá mục đích của holdout.

**Sources**: [Noul](https://docs.typesafe.ai/primitives/noul),
[Confidence routing](https://docs.typesafe.ai/patterns/confidence-routing)

## 7. Failure semantics

**Decision**: Judgment chỉ có `checked` hoặc `unchecked`. Lỗi dịch vụ, thiếu key, timeout hoặc hết
retry tạo `unchecked`; schema/digest/leakage error làm toàn run `invalid`, không giả làm một
per-case judgment. Không chuyển bất kỳ trạng thái nào thành pass.

Run tổng hợp dùng `complete`, `incomplete` hoặc `invalid`, tách khỏi decision. `incomplete` hoặc
`invalid` luôn có `decision=null`. `collect_more_labels` chỉ áp dụng cho run `complete`, sạch nhưng
không tính được một metric bắt buộc vì mẫu số bằng 0; nó không được dùng để che lỗi dịch vụ hay
integrity failure.

**Rationale**: Đây là fail-open đối với skill output nhưng fail-closed đối với bằng chứng. Partial
artifact vẫn hữu ích cho chẩn đoán nếu mọi case thiếu kết quả đều có reason code và bị loại khỏi
mẫu số accuracy.

**Alternatives considered**:

- Dùng xác suất 0 khi request lỗi: làm lỗi hạ tầng trông như phán đoán “không vi phạm”.
- Bỏ qua case lỗi: vi phạm yêu cầu không để case mất im lặng.
- Retry vô hạn: che lỗi vận hành và làm lệnh không có điểm kết thúc.

## 8. Privacy và artifact

**Decision**: Lần đầu chỉ dùng text công khai trong repo. TypeSafe state chỉ chứa source span,
một đến ba candidate spans, context cục bộ, genre và current intent. Evaluation artifact/report
không chứa raw prose, exception text hoặc credential; chỉ giữ case/candidate IDs, digests, version,
probability/confidence, action, latency, usage và reason code.

**Rationale**: Lọc secret không thay thế data minimization. Provenance và ground truth không cần
cho semantic judgment nên không được gửi. Raw corpus ở local source tree; generated artifacts
nằm trong thư mục gitignored.

**Alternatives considered**:

- Gửi toàn document: tăng exposure, token cost và nhiễu ngữ cảnh.
- Ghi request/response thô để debug: tiện trước mắt nhưng vi phạm ranh giới telemetry.
- Dùng narrative nội bộ hoặc dữ liệu của một tổ chức ở feasibility phase: không phù hợp với phạm vi
  của một dự án nguồn mở độc lập và tạo rủi ro công khai dữ liệu không cần thiết.

## 9. Interface

**Decision**: Một CLI `python -m guard_eval` có các subcommand `validate`, `evaluate`, `fit-policy`,
`report` và `all`. `all` là đường chạy một lệnh; các subcommand còn lại giúp test và chẩn đoán.

**Rationale**: Phân tách stage làm lỗi có vị trí rõ, nhưng maintainer vẫn có một entrypoint cho
toàn bộ workflow. Contract dùng exit code 0/1/2 và JSON artifact để automation không phải parse
văn bản console.

**Alternatives considered**:

- Một script nguyên khối: khó test riêng corpus, policy và report.
- Makefile: thêm lớp wrapper nhưng không cung cấp type hoặc validation.
- Dedicated vi-humanizer hook: ngoài phạm vi đã duyệt.

## 10. Cost accounting

**Decision**: Commit một `pricing.json` có model id, đơn giá input theo một triệu token, currency,
ngày quan sát và source URL. Report nhân `input_tokens` thực đo với snapshot này; output tokens
được tính theo đúng đơn giá ghi trong snapshot, không ngầm giả định luôn miễn phí.

**Rationale**: API trả token usage nhưng không trả invoice cost. Pricing là dữ liệu thay đổi theo
thời gian, nên phải version riêng khỏi policy và ghi đúng snapshot đã dùng. Tại ngày lập plan,
Jev 1.13 được công bố ở mức 0,042 USD cho một triệu input token và output token miễn phí.

**Alternatives considered**:

- Không báo cost: vi phạm FR-013.
- Hardcode giá trong code: báo cáo cũ đổi nghĩa khi code cập nhật giá.
- Gọi tài liệu pricing mỗi lần chạy: làm report offline phụ thuộc mạng và khó tái lập.

**Source**: [TypeSafe models and pricing](https://docs.typesafe.ai/models.md)

## 11. Candidate count và ranh giới generator/evaluator

**Decision**: Jev chỉ chọn hoặc từ chối candidate đã tồn tại trước request. Candidate trong corpus
có một trong ba origin: `host_llm_output`, `baseline_observation` hoặc `maintainer_fixture`, cùng
reference truy ngược. Đường production tương lai dùng host LLM chạy vi-humanizer; origin còn lại
chỉ phục vụ evaluation. Original và `none_of_candidates` luôn là options riêng, không tính vào
giới hạn ba candidate.

**Rationale**: Một candidate duy nhất không cho biết Jev có phân biệt được phương án tự nhiên với
phương án chỉ đúng ngữ pháp hay không. Danh sách không giới hạn làm request, nhãn và phép so sánh
phình theo số phương án. Origin tách khỏi semantic request để chứng minh candidate đến trước Jev
mà không làm model thấy provenance/ground truth. Giới hạn ba đủ cho feasibility probe, giữ artifact
review được và cho phép test order invariance; nếu dữ liệu thật cho thấy thiếu coverage thì mở rộng
bằng một quyết định mới, không âm thầm đổi contract.

**Alternatives considered**:

- Jev sinh trực tiếp câu mới: trộn generation với evaluation, khó truy nguồn và trái vai trò đã chốt.
- Chỉ một candidate: đo accept/reject được nhưng không đo preference giữa các cách viết.
- Không giới hạn candidate: tăng cost và độ phức tạp mà chưa có bằng chứng cần thiết.
