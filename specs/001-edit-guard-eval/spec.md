# Feature Specification: Đánh giá guard theo từng edit

**Feature Branch**: `codex/001-edit-guard-eval`

**Created**: 2026-09-26

**Status**: Retired implementation (owner decision 2026-10-03); historical evidence retained

The TypeSafe-dependent harness and its tests were removed in unreleased v0.9.7.
This specification records the former experiment, not current implementation requirements.
See `specs/005-optional-typesafe-advisor/spec.md` for the superseding owner decision.

**Input**: Xây corpus có nhãn ở cấp edit, một runner chạy bằng một lệnh và một phép thử
shadow cho quyết định biên tập của vi-humanizer. Harness phải đo cả việc source có cần sửa theo
V20 hay không, candidate nào nên được chọn và candidate đó có giữ nghĩa, giọng cùng ý định hay
không. Jev chỉ thẩm định và phân loại; candidate do host LLM chạy vi-humanizer tạo trước. Feature
chưa sửa output production và chưa làm hook riêng cho vi-humanizer.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Dựng corpus guard có thể kiểm chứng (Priority: P1)

Người bảo trì chuyển bằng chứng dùng được trong calibration log, ca kiểm thử và bản vàng
thành từng record ở cấp edit. Mỗi record có source, từ một đến ba candidate do vi-humanizer/host
LLM tạo, ngữ cảnh cần đọc, nhãn source có cần sửa hay không, phương án được ưu tiên, nhãn an toàn,
nguồn nhãn và split.

**Why this priority**: Không có corpus đúng đơn vị thì mọi con số về recall, false block và
ngưỡng đều không có nghĩa. Đây là đầu vào độc lập cho mọi phần còn lại.

**Independent Test**: Kiểm tra toàn bộ corpus mà không gọi external evaluator; mỗi record hợp
lệ, truy được về bằng chứng gốc, có đủ nhãn bắt buộc và không xuất hiện ở cả hai tập.

**Acceptance Scenarios**:

1. **Given** một entry có bản gốc, candidate edit và bản vàng, **When** nhập entry vào corpus,
   **Then** mỗi khác biệt được tách thành record riêng và giữ link tới nguồn bằng chứng.
2. **Given** một bản vàng chứa cả sửa lỗi và sở thích cá nhân, **When** tạo nhãn,
   **Then** phần sở thích không bị coi là edit có hại nếu chưa có ruling dùng chung.
3. **Given** một record đã nằm trong tập phát triển, **When** người bảo trì thêm cùng record vào
   holdout, **Then** bước kiểm tra corpus từ chối bộ dữ liệu.
4. **Given** hai câu dùng cùng một tiếng đơn nhưng chỉ một câu thiếu từ theo V20, **When** tạo nhãn,
   **Then** corpus ghi một positive và một hard negative thay vì coi tiếng đơn luôn là lỗi.

---

### User Story 2 - Quyết định có nên sửa và chọn candidate trong shadow (Priority: P2)

Người bảo trì chạy evaluator trên một manifest có observation baseline của workflow hiện tại đã
được đóng băng và maintainer xác nhận. Jev đánh giá source có cần sửa theo V20 hay không, chọn giữa
bản gốc, các candidate đã cung cấp và `none_of_candidates`, rồi chấm an toàn cho từng candidate.
Code tất định tổng hợp thành `keep`, `replace` hoặc `review`; không thành phần nào thay đổi văn bản
đầu ra thật. Lệnh đánh giá không chạy lại workflow Markdown hiện tại.

**Why this priority**: Giá trị của external evaluator chỉ được biết khi so trực tiếp với baseline
trên cùng case và cùng ground truth. Shadow mode ngăn một probe chưa hiệu chỉnh tác động tới người
đọc.

**Independent Test**: Chạy evaluator trên một corpus cố định và xác nhận lệnh giữ nguyên baseline
observation đã xác nhận, tạo đủ kết quả candidate, lỗi dịch vụ và metadata phù hợp với giai đoạn
của lần chạy mà không sửa source text.

**Acceptance Scenarios**:

1. **Given** source dùng một tiếng thiếu trong tổ hợp đang xét và có candidate tự nhiên, **When**
   chạy đánh giá, **Then** artifact ghi phán đoán source cần sửa, candidate được ưu tiên và các
   phán đoán an toàn cùng phiên bản corpus, config, question set và model.
2. **Given** thiếu credential, timeout hoặc lỗi dịch vụ, **When** chạy đánh giá, **Then** record
   được ghi là *chưa kiểm tra*, quy trình kết thúc có kiểm soát và không được tính là pass.
3. **Given** một edit gộp hoặc tách câu, **When** evaluator đọc edit, **Then** nó chấm change hunk
   cùng ngữ cảnh đoạn văn thay vì ghép máy móc từng cặp câu.
4. **Given** source đã tự nhiên như *Cốc nước đã đầy*, **When** candidate đổi thành một cụm dài hơn,
   **Then** evaluator có thể chọn `keep_original` và policy quan sát trả `keep`.
5. **Given** source cần sửa nhưng không candidate nào vừa tự nhiên vừa an toàn, **When** tổng hợp
   judgment, **Then** policy quan sát trả `review`, không cho Jev tự viết thêm phương án.

---

### User Story 3 - Ra quyết định giữ hay bỏ hướng TypeSafe (Priority: P3)

Người bảo trì đọc báo cáo trên holdout để biết evaluator có nhận ra đúng chỗ cần sửa, tránh sửa
chỗ vốn tự nhiên, chọn đúng candidate và không làm tăng edit có hại hay không. Báo cáo đưa ra kết
luận tiếp tục hoặc dừng, kèm giới hạn của bằng chứng, thay vì chỉ đếm số lần guard bắn.

**Why this priority**: Outcome của feature là một quyết định có bằng chứng. Tích hợp production
không có giá trị nếu probe không thắng baseline.

**Independent Test**: Dùng hai bộ kết quả giả lập, một bộ thắng baseline và một bộ không thắng;
báo cáo phải lần lượt đưa ra kết luận *tiếp tục shadow* và *dừng hướng candidate guard* theo cùng
một policy công khai.

**Acceptance Scenarios**:

1. **Given** ít nhất một trong need-to-edit recall, candidate-choice accuracy và
   no-acceptable-candidate recall tăng so với baseline; hai metric còn lại cùng harmful-edit recall
   không giảm; unnecessary-edit, valid-edit false-block và safety false accept không tăng,
   **When** tạo báo cáo, **Then** kết luận là đủ điều kiện tiếp tục shadow, chưa đủ điều kiện tự động sửa.
2. **Given** không metric tích cực nào tăng, một metric tích cực giảm hoặc một error rate tăng,
   **When** tạo báo cáo, **Then** kết luận là dừng hướng đó thay vì điều chỉnh ngưỡng trên holdout.
3. **Given** holdout thiếu nhãn đủ thẩm quyền hoặc có giao với tập phát triển, **When** tạo báo cáo,
   **Then** hệ thống từ chối đưa ra kết luận go/no-go.

### Edge Cases

- Candidate edit giống hệt source span hoặc chỉ đổi khoảng trắng.
- Một tiếng đơn đúng ở ngữ cảnh này nhưng thiếu hoặc kết hợp gượng ở ngữ cảnh khác.
- Candidate ghép thêm tiếng nhưng làm câu quan liêu, dài hoặc đổi sắc thái thay vì tự nhiên hơn.
- Nhiều candidate đều tự nhiên; thứ tự candidate thay đổi giữa hai lần serialize.
- Source cần sửa nhưng mọi candidate đều kém hoặc làm sai nghĩa.
- Hai candidate trùng nhau sau Unicode/whitespace normalization.
- Một change hunk gồm nhiều edit độc lập, trong đó chỉ một edit có hại.
- Người dùng chủ động yêu cầu đổi thanh ngữ vực, mức cam kết hoặc cấu trúc tài liệu.
- Candidate edit thêm hư từ hoặc loại từ nhưng không tạo khẳng định mới.
- Siêu dữ liệu quá trình là nội dung hợp lệ của changelog, decision record hoặc báo cáo tiến độ.
- Bản vàng thêm một lựa chọn phong cách cá nhân nhưng không chỉ ra lỗi dùng chung.
- Một record thiếu source text, ngữ cảnh, nguồn nhãn hoặc expected action.
- Một record bị đổi sau khi corpus version đã được dùng để tạo báo cáo.
- Model version thay đổi giữa các record trong cùng một lần chạy.
- Lỗi dịch vụ xảy ra sau khi một phần corpus đã được chấm.
- Báo cáo hoặc telemetry vô tình chứa raw prose từ corpus.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Mỗi evaluation case MUST đại diện cho một edit độc lập hoặc ghi rõ các edit không thể
  tách vì cần được hiểu cùng nhau.
- **FR-002**: Mỗi case MUST có source span, từ một đến ba candidate spans với ID ổn định, ngữ cảnh
  đủ dùng, ý định hiện tại của người dùng, thể loại, nhãn source có cần sửa, candidate được ưu tiên,
  nhãn an toàn, nguồn nhãn và đường dẫn tới bằng chứng gốc.
- **FR-003**: Nhãn guard MUST tách ít nhất các chiều: thêm khẳng định mới; đổi chủ thể hoặc thời
  điểm; đổi nhân quả hoặc mức cam kết; đổi thứ tự hoặc quan hệ đồng thời; đổi thanh ngữ vực; và
  giữ siêu dữ liệu quá trình không hợp lệ.
- **FR-004**: Corpus MUST có ca dương và hard negative cho từng chiều phán đoán, gồm V20 và các
  trường hợp **Không flag** nơi từ đơn đúng nghĩa, cách rút gọn có chủ ý hoặc thêm tiếng chỉ là lựa
  chọn phong cách. Mỗi split MUST có ca `none_of_candidates` mà ít nhất một candidate vẫn pass
  safety nhưng không đủ tự nhiên để chọn, nhằm tách năng lực preference khỏi guard.
- **FR-005**: Corpus MUST tách tập phát triển khỏi holdout và MUST từ chối trùng case hoặc biến thể
  chỉ khác định dạng giữa hai tập.
- **FR-006**: Case trong holdout MUST có nhãn do maintainer xác nhận. Nhãn do agent hoặc evaluator
  tự sinh MAY dùng để tìm candidate case nhưng MUST NOT tự trở thành ground truth.
- **FR-007**: Người bảo trì MUST chạy được toàn bộ đánh giá bằng một lệnh và nhận một artifact kết
  quả cùng exit status phản ánh việc lần chạy có hoàn tất hợp lệ hay không.
- **FR-008**: Mỗi case MUST có observation baseline của workflow `SKILL.md` hiện tại được đóng băng
  và maintainer xác nhận, gồm quyết định giữ/sửa và candidate đã chọn nếu có. Baseline và evaluator
  MUST được chấm độc lập trên cùng ground truth; evaluator MUST NOT nhận baseline observation làm
  state, và lệnh đánh giá MUST NOT chạy lại workflow Markdown hiện tại.
- **FR-009**: Candidate guard MUST chạy ở shadow mode trong feature này và MUST NOT sửa, loại hoặc
  hoàn bất kỳ edit nào trong output thật.
- **FR-010**: Candidate guard MUST đọc change hunk cùng ngữ cảnh cần thiết; hệ thống MUST NOT coi
  sentence pairing là ánh xạ đúng trong mọi trường hợp.
- **FR-011**: Khi external evaluator không khả dụng, kết quả MUST ghi *chưa kiểm tra*, giữ nguyên
  output và tách các case đó khỏi mẫu số accuracy.
- **FR-012**: Mỗi lần chạy MUST ghi corpus version, model version, thời điểm chạy, số case đã chấm,
  số case chưa chấm và lý do chưa chấm. Raw judgment run MUST ghi evaluation-config version và
  `policy_version=null`; mọi holdout run hoặc report có áp dụng policy MUST ghi policy version.
- **FR-013**: Báo cáo MUST có need-to-edit recall, unnecessary-edit rate, candidate-choice accuracy,
  no-acceptable-candidate recall, harmful-edit recall, valid-edit false-block rate, safety
  false-accept rate, review rate, số lỗi dịch vụ, latency và cost, tách theo từng chiều phán đoán
  và theo tập dữ liệu.
- **FR-014**: Báo cáo MUST nêu giới hạn về cỡ mẫu, nguồn nhãn, coverage và mọi thay đổi đã dùng dữ
  liệu phát triển để điều chỉnh câu hỏi hoặc policy.
- **FR-015**: Trên một holdout run hợp lệ và đầy đủ, policy go/no-go MUST khuyến nghị tiếp tục shadow
  chỉ khi evaluator cải thiện ít nhất một trong need-to-edit recall, candidate-choice accuracy và
  no-acceptable-candidate recall so với baseline mà không làm giảm hai metric còn lại hoặc
  harmful-edit recall, đồng thời không làm tăng unnecessary-edit rate, valid-edit false-block rate
  hoặc safety false accept.
  Nếu không đạt, policy MUST khuyến nghị dừng; nếu run hợp lệ nhưng bằng chứng chưa đủ, policy MAY
  khuyến nghị thu thập thêm nhãn mà không chỉnh trên holdout. Run invalid MUST có `run_status=invalid`;
  run có case chưa kiểm tra MUST có `run_status=incomplete`; cả hai MUST có `decision=null`.
- **FR-016**: Telemetry và báo cáo tổng hợp MUST NOT chứa raw prose, credential, dữ liệu cá nhân
  hoặc nội dung khách hàng.
- **FR-017**: External evaluator MUST chỉ nhận các trường cần cho từng phán đoán và MUST NOT nhận
  toàn bộ tài liệu khi change hunk cùng ngữ cảnh cục bộ đã đủ.
- **FR-018**: Quy trình Markdown hiện tại MUST tiếp tục dùng được khi feature không được cài, không
  có credential hoặc bị tắt.
- **FR-019**: Phần positive editing của feature MUST giới hạn ở V20: từ/cụm từ thiếu một tiếng và
  kết hợp từ không tự nhiên theo ngữ cảnh. Phần safety MUST giới hạn ở rule 2, các thành phần đo
  được của rule 3 và rule 5. Việc xác nhận các pattern khác thật sự áp dụng vẫn ở ngoài phạm vi.
- **FR-020**: Feature MUST NOT thêm cổng thể loại, phân loại kết quả của `scan-tells.sh`, tự dựng
  calibration log, production blocking hoặc hook nhắc dùng vi-humanizer.
- **FR-021**: Candidate generation MUST nằm ngoài Jev. Mỗi case MUST nhận từ một đến ba candidate
  trước khi gọi evaluator và ghi nguồn của từng candidate là output host LLM chạy vi-humanizer,
  baseline observation hoặc fixture do maintainer xác nhận. Jev MUST NOT tạo, nối, sửa hoặc diễn
  đạt lại candidate text.
- **FR-022**: External evaluator MUST đánh giá độc lập liệu source có cần sửa vì `lexically_incomplete` hoặc
  `unnatural_collocation`, có xét ngữ cảnh và các trường hợp **Không flag** của V20.
- **FR-023**: External evaluator MUST chọn đúng một option trong `keep_original`, các candidate ID đã cung cấp và
  `none_of_candidates`; kết quả MUST không phụ thuộc thứ tự candidate.
- **FR-024**: External evaluator MUST chấm sáu chiều safety trong FR-003 cho từng candidate; hệ
  thống MUST giữ các phán đoán độc lập thay vì yêu cầu evaluator đưa ra action cuối.
- **FR-025**: Hệ thống MUST tổng hợp tất định thành `keep`, `replace` hoặc `review`: các phán đoán
  không thấy nhu cầu sửa và preference tự tin chọn bản gốc thì `keep`; ít nhất một phán đoán thấy
  cần sửa, preference tự tin chọn candidate vượt safety policy thì `replace`; mọi trường hợp còn
  lại thì `review`.
- **FR-026**: Mọi `replace` trong artifact MUST tham chiếu nguyên văn một candidate ID đã có trong
  case; artifact MUST NOT chứa text mới do evaluator sinh.
- **FR-027**: Corpus, tài liệu, ví dụ và artifact được commit MUST chỉ dùng nội dung đã công khai
  trong chính repo hoặc fixture trung lập do maintainer tạo. Chúng MUST NOT chứa narrative nội bộ,
  dữ liệu khách hàng, định danh riêng hoặc thông tin có thể gắn dự án với một công ty hay tổ chức.

### Key Entities

- **Evaluation Case**: Một source span, một đến ba candidate edits, ngữ cảnh, ý định, thể loại,
  nhãn need-to-edit, preferred option, nhãn safety, expected edit decision và bằng chứng truy ngược.
- **Candidate Edit**: Một candidate ID ổn định, candidate span và nguồn tạo/xác nhận trước khi gọi
  evaluator.
- **Source Naturalness Judgment**: Các xác suất source thiếu từ hoặc kết hợp từ không tự nhiên.
- **Candidate Preference**: Lựa chọn giữa bản gốc, candidate IDs và `none_of_candidates`.
- **Edit Decision**: Kết quả tất định `keep`, `replace` hoặc `review`; chỉ được quan sát trong eval.
- **Corpus Version**: Tập case bất biến dùng cho một lần đánh giá, gồm phần phát triển, holdout và
  coverage matrix.
- **Judgment Set**: Phán đoán need-to-edit, candidate preference và safety cho một case, kèm trạng
  thái đã chấm hoặc chưa kiểm tra.
- **Decision Policy**: Quy tắc tất định biến judgment thành candidate guard action rồi thành
  `keep`, `replace` hoặc `review`; feature này chỉ quan sát policy, không tác động output thật.
- **Evaluation Run**: Manifest của một lần chạy, liên kết corpus, config, model, policy nếu đã áp
  dụng, kết quả, trạng thái hoàn tất và giới hạn.
- **Evaluation Report**: Bản tổng hợp metrics, coverage, run status và quyết định go/no-go nếu run
  đủ điều kiện; không chứa raw prose.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% case được nhập từ calibration evidence truy ngược được tới đoạn nguồn và ghi rõ
  nguồn nhãn; không có case holdout chỉ mang nhãn tự sinh từ agent.
- **SC-002**: Corpus validator phát hiện 100% fixture cố ý thiếu trường bắt buộc, trùng giữa tập phát
  triển và holdout, hoặc có corpus version không khớp nội dung.
- **SC-003**: Một lệnh tạo được evaluation artifact có kết quả cho mọi case hoặc lý do *chưa kiểm
  tra* cho từng case không được chấm; không có case bị mất im lặng.
- **SC-004**: Báo cáo chứa đủ mọi metric và giới hạn trong FR-013 và FR-014, đồng thời không chứa
  raw prose từ corpus.
- **SC-005**: Khi external evaluator thiếu credential, timeout hoặc trả lỗi, 100% case bị ảnh hưởng
  được ghi là *chưa kiểm tra* và quy trình Markdown hiện tại vẫn vượt package validation.
- **SC-006**: Go/no-go policy cho cùng một kết luận trên mọi lần đọc cùng evaluation artifact và
  từ chối kết luận khi holdout bị nhiễm dữ liệu phát triển hoặc thiếu nhãn maintainer.
- **SC-007**: Evaluator chỉ được khuyến nghị tiếp tục shadow khi ít nhất một trong need-to-edit
  recall, candidate-choice accuracy và no-acceptable-candidate recall tăng; hai metric còn lại cùng
  harmful-edit recall không giảm; unnecessary-edit, valid-edit false-block và safety false accept
  không tăng so với baseline trên holdout.
- **SC-008**: Mọi holdout run hợp lệ, đầy đủ kết thúc bằng một trong ba quyết định có bằng chứng:
  dừng evaluator, thu thập thêm nhãn, hoặc tiếp tục shadow. Run invalid kết thúc với trạng thái
  `invalid`; run chưa kiểm tra đủ kết thúc với trạng thái `incomplete`; cả hai không có quyết định
  và không trường hợp nào kết luận production-ready.
- **SC-009**: 100% `replace` trong fixture và holdout report tham chiếu đúng một candidate ID đã
  cung cấp; đổi thứ tự candidate không đổi preferred option hoặc edit decision.
- **SC-010**: Báo cáo tách được lỗi bỏ sót chỗ cần sửa, lỗi sửa thừa, lỗi chọn sai candidate, lỗi
  không từ chối được toàn bộ candidate kém và lỗi chấp nhận candidate không an toàn; không gộp năm
  loại lỗi thành một score duy nhất.
- **SC-011**: 100% candidate trong corpus có origin truy ngược được; request gửi evaluator không
  chứa origin/ground truth và response không thể thêm candidate text mới.

## Assumptions

- Corpus đầu tiên chỉ dùng văn bản công khai trong repo và fixture trung lập do maintainer cung cấp;
  không dùng narrative nội bộ, dữ liệu khách hàng hoặc định danh riêng của bất kỳ tổ chức nào.
- Maintainer của vi-humanizer là authority cuối cho nhãn holdout. Nhãn khác được giữ cùng provenance
  nhưng không tự thay thế xác nhận đó.
- Observation của quy trình tự kiểm tra trong `SKILL.md` 0.7.1, được maintainer xác nhận và đóng
  băng theo từng case, là baseline cần so; observation gồm quyết định giữ/sửa và candidate được
  chọn nếu có. Lệnh đánh giá không chạy lại workflow đó và baseline không mặc định là ground truth.
- Cỡ corpus ban đầu đủ cho feasibility probe và quyết định nội bộ, không đủ để công bố độ chính xác
  chung của Jev trên tiếng Việt.
- External evaluator vẫn là thành phần tùy chọn; chi tiết triển khai thuộc technical plan và không
  thay đổi ranh giới hành vi đã duyệt trong spec này.
