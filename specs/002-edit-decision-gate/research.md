# Research: Cổng quyết định sửa hay giữ v2

Tài liệu này chốt các quyết định Phase 0. Các nhận định về TypeSafe dựa trên tài liệu chính thức;
thiết kế cho tiếng Việt và cách ghép policy là suy luận của dự án, phải được kiểm chứng trên corpus.

## R1. Tách lane v2 khỏi contract v1

**Decision**: Thêm namespace `guard_eval.v2` và corpus `eval/guard/v2/`; giữ nguyên semantics của
`python -m guard_eval`, module v1 và mọi artifact feature 001.

**Rationale**: Model validation, question digest, Choice options, policy và report v1 đều hard-code
`keep_original`/`none_of_candidates`. Nới schema v1 bằng optional fields có thể load được JSON cũ
nhưng thay semantics âm thầm; sửa template v1 làm question-set digest drift.

**Alternatives considered**:

- Thêm `--version v2` vào CLI/module v1: ít file hơn nhưng branch logic xuyên toàn pipeline, khó
  chứng minh v1 còn nguyên.
- Fork toàn bộ package: cô lập tốt nhưng nhân đôi utility thuần. V2 chỉ import utility không mang
  semantics như normalize/canonical digest; contract đổi phải có type/module riêng.

## R2. Một Noul cho một điều kiện, không hỏi hai vế đối nghịch

**Decision**: Absolute request hỏi `source_context_sufficient`, hai lỗi nguồn cụ thể, và các thuộc
tính hẹp của candidate. Không hỏi đồng thời `source_is_good` và `source_needs_edit`.

**Rationale**: `Noul` trả xác suất cho chính câu hỏi đó; hai Noul đối nghịch không tạo một phân phối
bù nhau. Jev cũng hoạt động tốt hơn khi instruction và criteria trực tiếp, ít tầng suy diễn. Code
suy ra source đủ tốt từ cùng các tín hiệu lỗi đã fit threshold, không gọi model lần hai để hỏi lại.

**Alternatives considered**:

- Một Noul tổng quát “có nên sửa không”: đơn giản nhưng che mất failure mode từ đơn/từ ghép và
  kết hợp từ khô cứng.
- Hai Noul `is_good`/`needs_edit`: dễ tạo mâu thuẫn giả và không được phép cộng xác suất thành một.

Nguồn: [Noul](https://docs.typesafe.ai/primitives/noul.md),
[Jev 1.13 jaggedness](https://docs.typesafe.ai/model-jaggedness/jev-1.13.md),
[confidence](https://docs.typesafe.ai/confidence.md).

## R3. Candidate acceptability là predicate dẫn xuất

**Decision**: Với mỗi candidate, Jev chấm `fixes_issue`, `preserves_meaning_and_nuance`,
`fits_voice_and_genre` và sáu safety risks. Policy suy ra `candidate_acceptable` bằng conjunction
của các component đã qua threshold; không dùng thêm một Noul tổng hợp để route.

**Rationale**: Câu “candidate có đủ tốt không?” gộp quá nhiều điều kiện và không chỉ ra model sai
ở đâu. Hỏi lại một kết luận tổng hợp song song cũng không bảo đảm nhất quán với các câu hỏi thành
phần. Nhãn corpus vẫn giữ `expected_candidate_acceptability` để chấm predicate cuối.

**Alternatives considered**:

- Một Noul `candidate_acceptable`: ít câu hỏi nhưng mơ hồ giữa sửa đúng lỗi, giữ sắc thái và safety.
- Dùng Choice winner như candidate đạt chuẩn: sai tầng; tốt nhất tương đối vẫn có thể không đủ tốt.

## R4. Choice chỉ chạy trên shortlist đủ chuẩn

**Decision**: Absolute request chạy trước. Shortlist rỗng ra `review`; một candidate đủ chuẩn được
chọn tất định; chỉ khi có ít nhất hai candidate đủ chuẩn mới tạo request Choice thứ hai với đúng
các candidate IDs đó.

**Rationale**: Options của request thứ hai phụ thuộc kết quả request thứ nhất, đúng trường hợp cần
request kế tiếp. `Choice.confidence` chỉ nói phân phối giữa options có rõ không, không chứng minh
winner an toàn hay có quyền thay source.

**Alternatives considered**:

- Một request chứa Choice của tất cả candidate: Choice không biết output các Noul song song.
- Giữ `keep_original`/`none_of_candidates` trong Choice: trộn quyết định tuyệt đối với xếp hạng.
- Luôn gọi Choice kể cả một candidate: tốn quota và tạo confidence vô nghĩa cho lựa chọn duy nhất.

Nguồn: [Choice](https://docs.typesafe.ai/primitives/choice.md),
[primitives and dependent requests](https://docs.typesafe.ai/primitives.md),
[confidence-gated routing](https://docs.typesafe.ai/patterns/confidence-routing.md).

## R5. Khóa model và không dùng threshold từ docs

**Decision**: Pin exact model `jev-1.13.0`; fit riêng threshold cho mỗi Noul family và Choice trên
dev. Model mismatch làm run `invalid`; service failure làm case `unchecked`.

**Rationale**: Alias có thể dịch chuyển, trong khi threshold gắn với distribution của model/question
cụ thể. Giá trị minh họa trong docs không phải calibration cho tiếng Việt. English là ngôn ngữ
huấn luyện chính nên workload tiếng Việt cần evidence riêng.

**Alternatives considered**:

- `jev-latest`: giảm maintenance nhưng làm replay không xác định.
- Một threshold dùng chung: bỏ qua risk/shape khác nhau của Noul và Choice.

Nguồn: [models and language support](https://docs.typesafe.ai/models.md),
[Jev 1.13](https://docs.typesafe.ai/model-jaggedness/jev-1.13.md).

## R6. Tách raw judgment, policy recommendation và report

**Decision**: Dùng ba lớp `JudgmentRun`, `RecommendationRun`, `ComparisonReport`. Raw run có
`policy_version=null`; recommendation run tham chiếu raw-run digest và policy; report đọc hai
recommendation runs cùng labels để tính metric.

**Rationale**: Threshold phải replay offline mà không gọi model lại. Lặp score trong recommendation
run làm hai nguồn sự thật; nhét recommendation vào raw run làm mất ranh giới pre-policy mà
constitution yêu cầu.

**Alternatives considered**:

- Một artifact chứa cả score và recommendation: gọn hơn nhưng khó chứng minh recommendation tái
  lập khi policy đổi.
- Tạo report thẳng từ response: không có reusable raw evidence và dễ kéo raw exception/prose vào.

## R7. So v1/v2 bằng hai raw runs trên cùng holdout v2

**Decision**: Project mỗi `RecommendationCaseV2` sang request state v1, chạy question contract v1 bằng
config/model v1 và question contract v2 bằng config/model v2. Áp frozen v1/v2 policies offline rồi
so hai recommendation runs trên cùng IDs/fingerprints/labels.

**Rationale**: `case.baseline` v1 là quan sát workflow, không phải policy v1. Hai question contracts
khác nhau nên không thể dùng chung một raw run. `corpus_version_fitted` phải là provenance fit; nó
không được cấm policy chấm một corpus evaluation khác nếu pipeline/config/question/model vẫn khớp.

**Alternatives considered**:

- Dùng report holdout v1 làm baseline: khác corpus, không chứng minh delta trên cùng case.
- Dùng baseline observation của case v2: so workflow với v2 chứ không so policy v1/v2.
- Dùng raw v2 cho policy v1: schema semantic không tương thích.

## R8. Promote holdout v1 vào dev v2 có lineage, không chép vào holdout

**Decision**: Copy nguyên semantic case đã quan sát vào dev v2, đổi split và thêm lineage gồm source
path/digest/case ID/fingerprint/corpus version. Registry lịch sử khóa mọi holdout fingerprint đã mở.

**Rationale**: Failure mode v1 là development evidence hữu ích nhưng không còn là holdout. Fingerprint
semantic không gồm split/provenance nên validator có thể chứng minh case promoted không bị sửa.

**Alternatives considered**:

- Sửa trực tiếp holdout v1: phá bằng chứng lịch sử.
- Chép vào holdout v2: leakage rõ ràng.
- Viết lại thành case “tương tự”: có thể dùng cho coverage mới nhưng không chứng minh regression
  chính xác của failure đã quan sát.

## R9. Metric có mẫu số, đơn vị và hướng

**Decision**: Mỗi `MetricValue` ghi `unit`, `direction`, `numerator`, `denominator`, `rate`,
`minimum_denominator`, `denominator_status`. Comparison ghi `rate_delta=v2-v1` và
`improvement_delta`, đảo dấu cho metric lower-is-better.

**Rationale**: Scalar `0.0`/`1.0` che cỡ mẫu. “Absolute delta” không nói thay đổi tốt hay xấu.
Coverage recommendation class/slice đếm theo case; candidate-level metric dùng candidate làm unit.

**Alternatives considered**:

- Chỉ rate + case count tổng: không xác định mẫu số riêng của metric.
- Chỉ absolute delta: mất hướng và có thể trình bày regression như một thay đổi trung tính.

## R10. Go/no-go bảo vệ an toàn trước review rate

**Decision**: Một harmful `replace` recommendation hoặc bất kỳ protected regression nào trả `stop`.
Thiếu mẫu số bắt buộc trả `collect_more_labels`. Chỉ khi không regression và keep precision hoặc
no-acceptable recall tăng nghiêm ngặt mới được `continue_shadow`.

**Rationale**: Mục tiêu không phải giảm review bằng mọi giá mà là biết khi nào không nên sửa và chỉ
thay bằng candidate thật sự đạt. Review rate đẹp không bù được sửa hỏng nghĩa/sắc thái.

**Alternatives considered**:

- Weighted aggregate score: một metric tốt có thể che safety regression.
- Chỉ so review rate: khuyến khích hệ thống tự tin sai.

## R11. Byte lock v1 và privacy denylist

**Decision**: Tạo lock manifest path + SHA-256 cho corpus/config/policy/pricing/report v1; test đọc
bytes thật. Mọi committed/generated v2 artifact chạy recursive key denylist và kiểm tra nội dung
không có raw prose, request body, secret, raw exception hay định danh cá nhân/tổ chức.

**Rationale**: “Không sửa” cần bằng chứng byte-level, không phải git status hoặc lời khẳng định.
Privacy không thể dựa vào việc đã bỏ key; value tự do và exception vẫn có thể rò nội dung.

**Alternatives considered**:

- Chỉ dựa vào Git history: không phát hiện drift trong working tree trước commit.
- Chỉ cấm một số keys: cần thêm schema allowlist/reason-code allowlist và fixture scan.

## R12. Agent sở hữu quyết định biên tập; v2 chỉ tạo khuyến nghị shadow

**Decision**: Host LLM/Agent là thành phần duy nhất quyết định giữ hay sửa và sinh câu chữ cuối.
Jev chỉ trả typed semantic judgments hoặc ranking cho candidate đã có. Code v2 ghép các tín hiệu
thành `keep/review/replace` recommendation để hiệu chỉnh và so sánh shadow; nó không thực thi
recommendation, không gọi agent và không sửa prose. Hard safety veto trong runtime nằm ngoài
feature 002 và cần holdout evidence cùng approval riêng.

Vì v2 chưa ship và chưa có frozen policy, contract v2 đổi tên theo đúng authority: `DecisionPolicyV2`,
`PolicyDecisionV2`, `DecisionRunV2`, `DecisionAction`, `CandidateAction`, field `action` và field
`candidate_actions` lần lượt thành `RecommendationPolicyV2`, `PolicyRecommendationV2`,
`RecommendationRunV2`, `RecommendationKind`, `CandidateAssessment`, `recommendation` và
`candidate_assessments`. Corpus dùng `expected_recommendation`. Không giữ compatibility alias trong
v2; v1 giữ nguyên bytes và terminology lịch sử.

**Rationale**: Giữ tên `decision/action` trong một evaluator không có quyền biên tập làm người đọc
hiểu nhầm authority và khuyến khích tích hợp shadow output như lệnh runtime. Alias cũ/mới tạo hai
tên cho cùng một sự thật. Đây là thời điểm rẻ nhất để sửa vì contract v2 chưa frozen hoặc phát hành.

**Alternatives considered**:

- Chỉ thêm chú thích “shadow”: ít diff hơn nhưng vẫn để API nói sai authority.
- Giữ cả `action` và `recommendation`: tương thích không cần thiết và tạo hai nguồn dữ liệu.
- Cho Jev quyết định trực tiếp: trái vai trò thẩm định, làm model vừa chấm tín hiệu vừa kết luận.

## R13. Candidate bị reject phải tạo revision mới, không hạ chuẩn duyệt

**Decision**: Candidate policy đầu tiên bị maintainer reject tại T051 sau live replay chỉ khớp 6/9
nhãn và tạo một `replace` recommendation cho candidate được gắn nhãn không chấp nhận được. Revision
phải ghi rejection artifact sanitized, thêm regression contract trước implementation, làm rõ câu
`preserves_meaning_and_nuance` cho trường hợp hoàn chỉnh từ ghép so với thay bằng từ gần nghĩa, và
từ chối freeze nếu dev replay còn recommendation thay candidate không đạt. Question/config/corpus
drift làm approval T049 cũ hết hiệu lực; live revision cần proposal và approval mới.

**Rationale**: Policy fit thành công về mặt schema không chứng minh nó đáng freeze. Ngưỡng không thể
sửa một phán đoán ngữ nghĩa đã chấm candidate sai tầng; đồng thời fitter phải fail closed trước một
recommendation vi phạm nhãn acceptability trên chính dev dùng để fit.

**Alternatives considered**:

- Freeze 6/9 rồi trông chờ holdout: dùng dữ liệu chưa quan sát để phát hiện lỗi dev đã biết.
- Chỉ chỉnh threshold: không tách được candidate đúng có score thấp hơn candidate sai đã được Jev
  chấm quá cao.
- Để code tự viết hoặc chọn prose mới: vượt authority của evaluator và trái FR-027.
