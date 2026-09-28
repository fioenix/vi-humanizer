# Feature Specification: Cổng quyết định sửa hay giữ v2

**Feature Branch**: `codex/002-edit-decision-gate`

**Created**: 2026-09-26

**Status**: Evaluated — `collect_more_labels`

**Input**: Tiếp tục sau khi evaluation v1 ra quyết định `stop`: giữ nguyên bằng chứng v1, mở một iteration mới để vi-humanizer phân biệt khi nào nên giữ nguyên, khi nào cần người xem và khi nào có thể chọn một bản sửa.

## Clarifications

### Session 2026-09-27

- Q: Trong runtime vi-humanizer, thành phần nào có quyền quyết định biên tập cuối cùng? → A: Host LLM/Agent quyết định giữ hay sửa và thực hiện việc viết; Jev chỉ thẩm định tín hiệu ngữ nghĩa, còn code feature 002 chỉ tạo khuyến nghị shadow và evidence để đánh giá, không điều khiển workflow Markdown.

### Session 2026-09-28

- Q: Enum v2 mô tả kết quả thẩm định từng candidate có giữ tên `CandidateAction` không? → A: Đổi thành `CandidateAssessment`, khớp field `candidate_assessments`, không giữ compatibility alias; v1 giữ nguyên terminology và bytes. (agent decided; basis: v2 chưa phát hành và tên `action` làm sai authority đã duyệt)
- Q: Ai được ghi nhận là người duyệt các live gate khi owner đã giao agent tự quyết đến hết goal? → A: Giữ `maintainer` cho phê duyệt trực tiếp; cho phép `owner_authorized_agent` khi owner đã ủy quyền rõ trong cuộc hội thoại, và luôn ghi đúng actor thật thay vì giả thành maintainer.
- Q: TypeSafe/Jev được bật bằng cách nào trong một cài đặt công khai? → A: Chỉ sự hiện diện của `TYPESAFE_API_KEY` mới bật lớp thẩm định tùy chọn; không thêm cờ `enabled` thứ hai, không đưa `typesafe-sdk` vào dependency lõi, và thiếu key/SDK/dịch vụ không được làm gián đoạn workflow Markdown. (agent decided; basis: constitution yêu cầu skill tự đứng được và noulmes trả `SUPPORTS` 0.98)
- Q: Làm rõ cơ chế opt-in này có tạo một runtime feature mới và buộc tăng version không? → A: Không; giữ `0.9.0` vì thay đổi chỉ công khai hóa ranh giới của evaluation architecture đã phát hành, chưa thêm runtime connector vào gói `.skill`. (agent decided; basis: package hiện không chứa harness/SDK và noulmes trả `SUPPORTS` 0.94)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Quyết định đúng giữ, xem lại hay thay (Priority: P1)

Người bảo trì muốn lớp thẩm định shadow tách bốn câu hỏi: bản gốc đã ổn chưa, có thật sự cần sửa không, từng candidate có phải một cải thiện chấp nhận được không và candidate nào tốt hơn trong số những candidate đã đủ chuẩn. Lớp này tạo khuyến nghị và bằng chứng cho host LLM/Agent; một lựa chọn tương đối không được coi là bằng chứng rằng Agent nên thay bản gốc.

**Why this priority**: Holdout v1 dừng chính vì cổng chưa phân biệt được một candidate tốt nhất tương đối với một candidate đủ tốt để thay bản gốc.

**Independent Test**: Chạy một corpus có đủ nhãn `keep`, `review` và `replace`; đối chiếu khuyến nghị shadow, reason code và phân loại candidate với nhãn maintainer, đồng thời chứng minh evaluator không sửa prose hoặc điều khiển workflow Markdown.

**Acceptance Scenarios**:

1. **Given** bản gốc đã tự nhiên và đủ nghĩa, **When** các candidate chỉ diễn đạt lại hoặc làm mất sắc thái từ vựng, **Then** evaluator khuyến nghị `keep` hoặc `review`, không khuyến nghị `replace`.
2. **Given** bản gốc cần sửa và có ít nhất một candidate an toàn, cải thiện đúng lỗi, **When** phán đoán tuyệt đối và kết quả xếp hạng nhất quán với nhau, **Then** evaluator có thể khuyến nghị `replace` với candidate đã đủ chuẩn; host Agent vẫn sở hữu quyết định và câu chữ cuối.
3. **Given** bản gốc cần sửa nhưng không candidate nào đủ chuẩn, **When** evaluator tổng hợp phán đoán, **Then** evaluator khuyến nghị `review`, không chọn phương án ít tệ nhất.
4. **Given** các phán đoán mâu thuẫn hoặc không chắc chắn, **When** không thể chứng minh một khuyến nghị rõ ràng, **Then** evaluator trả `review` kèm reason code hữu hạn để Agent tự xem xét lại.

---

### User Story 2 - Học từ v1 mà không làm bẩn holdout (Priority: P2)

Người bảo trì muốn dùng các failure mode đã lộ diện ở v1 làm bằng chứng phát triển, nhưng không sửa lại policy, corpus hoặc report lịch sử của v1 và không dùng lại các ca đã xem để chứng minh iteration mới.

**Why this priority**: Nếu vừa chỉnh theo ca holdout vừa dùng chính ca đó làm bằng chứng, quyết định go/no-go không còn giá trị.

**Independent Test**: Kiểm tra provenance và digest để xác nhận artifacts v1 không đổi, ca đã quan sát chỉ xuất hiện trong lane phát triển/hồi quy và holdout v2 chưa từng được dùng để chỉnh câu hỏi hay policy.

**Acceptance Scenarios**:

1. **Given** policy, corpus và report v1 đã được commit, **When** iteration v2 được chuẩn bị, **Then** bytes và digest của artifacts v1 không thay đổi.
2. **Given** các ca holdout v1 đã được xem, **When** chúng được dùng để chống hồi quy, **Then** chúng được ghi rõ là dữ liệu phát triển và không tính vào bằng chứng holdout v2.
3. **Given** policy v2 đã được duyệt và khóa, **When** holdout v2 được mở, **Then** không đổi question, threshold, label hoặc corpus sau khi đọc kết quả.

---

### User Story 3 - Ra quyết định bằng metric có mẫu số (Priority: P3)

Người bảo trì muốn report cho biết cổng mới có cải thiện quyết định sửa hay giữ hay không, với số ca và mẫu số của từng metric, thay vì chỉ nhìn tỷ lệ từ một corpus quá nhỏ.

**Why this priority**: Tỷ lệ 0% hoặc 100% trên một ca không đủ để phân biệt một cải thiện thật với may rủi lấy mẫu.

**Independent Test**: Tạo report từ kết quả có đủ và thiếu coverage; xác nhận report hiển thị count, denominator, slice và trả `collect_more_labels` khi thiếu mẫu số bắt buộc.

**Acceptance Scenarios**:

1. **Given** một metric bắt buộc có quá ít ca được gắn nhãn, **When** report được tạo, **Then** report trả `collect_more_labels` thay vì `continue_shadow`.
2. **Given** v1 và v2 cùng được chấm trên holdout v2, **When** report so sánh hai policy, **Then** mỗi metric có count, denominator và chênh lệch tuyệt đối.
3. **Given** một metric an toàn hoặc độ chính xác bắt buộc giảm, **When** go/no-go được tính, **Then** quyết định là `stop` bất kể review rate có đẹp hơn hay không.

### Edge Cases

- Nhiều candidate cùng đủ chuẩn nhưng lựa chọn tương đối có confidence thấp.
- Candidate được xếp hạng cao nhất nhưng phán đoán tuyệt đối cho biết nó không đủ chuẩn.
- Bản gốc được đánh giá là đã ổn trong khi một tín hiệu khác lại cho rằng cần sửa.
- Candidate cải thiện độ tự nhiên nhưng đổi nghĩa, đổi giọng hoặc làm mất sắc thái từ vựng.
- Candidate trùng bản gốc hoặc trùng một candidate khác sau khi chuẩn hóa.
- Model version thực tế không khớp version đã khóa cho evaluation.
- Một phần request lỗi, timeout hoặc thiếu credential.
- Một cách dùng từ tự nhiên ở thể loại này nhưng bị xem là khô cứng ở thể loại khác.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Iteration v2 MUST giữ nguyên bytes của policy, corpus, config và report đã commit trong feature 001.
- **FR-002**: Với mỗi ca được kiểm tra đầy đủ, evaluator MUST chỉ sinh một trong ba khuyến nghị shadow: `keep`, `review` hoặc `replace`; các giá trị này MUST NOT được thực thi như hành động biên tập trong feature 002.
- **FR-003**: Cổng MUST phân biệt phán đoán tuyệt đối về bản gốc, phán đoán tuyệt đối về từng candidate, xếp hạng tương đối giữa các candidate và kiểm tra an toàn.
- **FR-004**: Mỗi phán đoán ngữ nghĩa MUST hỏi một điều kiện trực tiếp; MUST NOT dùng phủ định kép hoặc giả định xác suất của hai câu hỏi đối nghịch cộng thành 1.
- **FR-005**: Phán đoán candidate đủ chuẩn MUST xét đồng thời việc cải thiện đúng lỗi, giữ nghĩa, giữ giọng, phù hợp với thể loại và không làm mất sắc thái từ vựng.
- **FR-006**: Lựa chọn tương đối MUST NOT tự nó tạo khuyến nghị `replace`; policy tất định chỉ sở hữu việc tổng hợp phán đoán thành khuyến nghị shadow, không sở hữu quyết định hoặc câu chữ cuối của host Agent.
- **FR-007**: Khuyến nghị `replace` MUST chỉ xuất hiện khi bản gốc không đủ tốt, nhu cầu sửa đủ mạnh, candidate được chọn đủ chuẩn, an toàn và lựa chọn đủ rõ ràng.
- **FR-008**: Khuyến nghị `keep` MUST chỉ xuất hiện khi bằng chứng cho bản gốc đã ổn không mâu thuẫn với một tín hiệu cần sửa đủ mạnh.
- **FR-009**: Khi không candidate nào đủ chuẩn, evaluator MUST khuyến nghị `review` và MUST NOT khuyến nghị candidate tốt nhất tương đối.
- **FR-010**: Phán đoán mâu thuẫn hoặc không đủ chắc chắn MUST tạo khuyến nghị `review`; thiếu phán đoán do run không hoàn chỉnh MUST ra `unchecked`. Không trường hợp nào được âm thầm đổi thành khuyến nghị `keep` hay `replace`.
- **FR-011**: Raw semantic judgments MUST được lưu tách khỏi recommendation policy để có thể đánh giá lại threshold mà không gọi model lại.
- **FR-012**: Mỗi ca MUST có split, provenance, label authority, genre, expected recommendation và expected candidate acceptability.
- **FR-013**: Ca đã quan sát từ holdout v1 MAY được dùng làm regression development data, nhưng MUST được ghi provenance và MUST NOT tính vào holdout v2.
- **FR-014**: Holdout v2 MUST là tập chưa dùng để thiết kế question, fit policy hoặc chọn threshold; policy v2 MUST được duyệt và khóa trước khi mở holdout.
- **FR-015**: Corpus MUST bao phủ ít nhất các slice: bản gốc đã tự nhiên, thiếu kết hợp từ tự nhiên, kết hợp từ khô cứng, không candidate nào đủ chuẩn, candidate đổi nghĩa và candidate đổi thanh ngữ vực.
- **FR-016**: Mỗi metric MUST báo cả tỷ lệ, tử số và mẫu số; metric bắt buộc chưa đủ mẫu số MUST làm quyết định thành `collect_more_labels`.
- **FR-017**: Go/no-go MUST so sánh policy v1 và v2 trên cùng holdout v2; bất kỳ suy giảm nào ở metric an toàn hoặc độ chính xác bắt buộc MUST trả `stop`.
- **FR-018**: Report MUST tách raw model answer, policy recommendation và các ca phán đoán ngữ nghĩa không đồng ý với khuyến nghị shadow.
- **FR-019**: Report và artifact có thể commit MUST NOT chứa raw prose, request body, credential, exception nguyên văn hoặc định danh cá nhân/tổ chức.
- **FR-020**: Evaluation v2 MUST ở shadow mode và MUST NOT thay đổi workflow biên tập Markdown hay tự động sửa prose.
- **FR-021**: Thiếu credential, timeout, lỗi service hoặc response không hợp lệ MUST ra `unchecked` và không được tính là pass.
- **FR-022**: Corpus, tài liệu, ví dụ và artifact được commit MUST chỉ dùng nội dung công khai hoặc fixture trung tính.
- **FR-023**: Sau khi đọc holdout v2, question, threshold, label và corpus MUST NOT thay đổi trong cùng iteration.
- **FR-024**: Evaluation MUST khóa model version và ghi model version thực tế; mismatch MUST làm run không hợp lệ.
- **FR-025**: Label proposal, policy candidate và việc mở holdout MUST được maintainer hoặc agent được owner ủy quyền rõ duyệt riêng trước mỗi live gate; artifact MUST ghi đúng actor thật là `maintainer` hoặc `owner_authorized_agent`.
- **FR-026**: Feature MUST NOT thay đổi V-series, T-series, profile hoặc package payload của vi-humanizer.
- **FR-027**: Host LLM/Agent MUST là thành phần duy nhất quyết định giữ hay sửa và sinh câu chữ cuối trong runtime vi-humanizer. Jev MUST chỉ thẩm định tín hiệu hoặc xếp hạng candidate đã có; code feature 002 MUST chỉ chuẩn hóa evidence, áp policy cho evaluation và không được gọi, sửa hoặc thay thế prose.
- **FR-028**: TypeSafe/Jev MUST là progressive enhancement được opt-in bằng `TYPESAFE_API_KEY`; core skill MUST không phụ thuộc API key, SDK hoặc mạng, và MUST không có cờ enable thứ hai có thể lệch trạng thái với credential.

### Key Entities

- **Recommendation Case v2**: Một đơn vị đánh giá gồm bản gốc, context tối thiểu, candidate, nhãn khuyến nghị, nhãn candidate, split và provenance.
- **Absolute Judgment**: Phán đoán độc lập về việc bản gốc đã ổn, có cần sửa, hoặc một candidate có đủ chuẩn hay không.
- **Relative Ranking**: Thứ tự ưu tiên giữa các candidate; không mang quyền quyết định thay bản gốc.
- **Recommendation Policy v2**: Quy tắc tất định kết hợp phán đoán, ngưỡng và cấp rủi ro thành khuyến nghị shadow `keep`, `review` hoặc `replace`; đây là artifact evaluation, không phải quyền biên tập. Run không hoàn chỉnh được ghi là `unchecked`.
- **Evaluation Report v2**: Bằng chứng so sánh v1/v2 gồm metric có mẫu số, coverage, disagreement, usage, cost, limitation và quyết định.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% ca evaluation hoàn chỉnh có đúng một khuyến nghị shadow `keep`, `review` hoặc `replace` và một reason code được cho phép; 0 ca làm thay đổi prose hoặc workflow Markdown.
- **SC-002**: Trên holdout v2, harmful-edit recall của v2 không thấp hơn v1 và không candidate có nhãn harmful nào nhận khuyến nghị `replace`.
- **SC-003**: Trên holdout v2, keep precision và no-acceptable-candidate recall của v2 đều không thấp hơn v1, đồng thời ít nhất một trong hai metric tăng nghiêm ngặt.
- **SC-004**: Trên holdout v2, valid-edit false-block rate và candidate-choice accuracy của v2 không xấu hơn v1.
- **SC-005**: Mỗi recommendation class `keep`, `review` và `replace`, cùng slice `no acceptable candidate` và `harmful candidate`, có ít nhất 5 ca gắn nhãn trong holdout v2; thiếu bất kỳ mẫu số nào thì report không được ra `continue_shadow`.
- **SC-006**: Cùng raw judgments, policy và config luôn tạo cùng khuyến nghị shadow, metric và quyết định go/no-go mà không cần gọi lại external evaluator.
- **SC-007**: 100% run thiếu credential hoặc có lỗi service trả `unchecked`/incomplete và không làm hỏng workflow Markdown hiện tại.
- **SC-008**: 100% report và artifact được track vượt privacy scan: không raw prose, secret, request body, raw exception hoặc định danh cá nhân/tổ chức.
- **SC-009**: Report hiển thị latency, token usage và cost thực tế để maintainer duyệt; không suy ra ngân sách từ config hoặc pricing snapshot.
- **SC-010**: Cài đặt và chạy gói `vi-humanizer.skill` không có `TYPESAFE_API_KEY` hoặc `typesafe-sdk` vẫn hoàn tất workflow Markdown; chỉ live evaluation command trả `unchecked`/exit 2 khi lớp thẩm định không khả dụng.

## Assumptions

- Holdout v1 đã được mở và đọc sau quyết định `stop`; nó chỉ còn giá trị là regression development data cho v2.
- Holdout v2 là corpus mới, trung tính, được maintainer hoặc agent được owner ủy quyền gắn nhãn và không được mở trước khi policy v2 đã khóa.
- Policy v1 sẽ được chấm trên holdout v2 làm baseline so sánh; kết quả cũ trên holdout v1 không được dùng thay cho phép so sánh này.
- Mức 5 ca cho mỗi mẫu số bắt buộc là mức lấy mẫu tối thiểu khả thi của iteration, không phải tuyên bố ý nghĩa thống kê hoặc ngưỡng chung cho tiếng Việt.
- Candidate vẫn do host LLM chạy vi-humanizer, baseline observation hoặc maintainer fixture tạo; external evaluator không sinh, nối hay sửa prose.
- Host LLM/Agent giữ quyền quyết định biên tập cuối; khuyến nghị của feature 002 chỉ phục vụ hiệu chỉnh và đánh giá shadow. Mọi hard safety veto trong runtime là một integration riêng, chỉ được xem xét sau holdout và approval mới.
- Mọi live call, quota use, label approval, policy freeze và holdout opening vẫn cần phê duyệt ở đúng gate bởi maintainer hoặc agent được owner ủy quyền rõ.
