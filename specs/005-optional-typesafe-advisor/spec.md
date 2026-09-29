# Feature Specification: Cố vấn TypeSafe tùy chọn

**Feature Branch**: `codex/005-optional-typesafe-advisor`

**Created**: 2026-09-29

**Status**: Approved

**Input**: Mở feature 005 để người dùng có thể bật TypeSafe/Jev như một lớp cố vấn tùy chọn cho
`vi-humanizer`. Core skill vẫn phải chạy đầy đủ khi không có TypeSafe. Host LLM tạo candidate và
quyết định có sửa hay không; Jev chỉ thẩm định các tín hiệu ngữ nghĩa có cấu trúc, không viết văn.

## Clarifications

### Session 2026-09-29

- Q: Thành phần nào có quyền quyết định biên tập cuối? → A: Host LLM/Agent quyết định giữ hay sửa,
  chọn candidate và viết bản cuối; Jev chỉ trả tín hiệu thẩm định hoặc xếp hạng candidate đã có.
- Q: TypeSafe được bật bằng cách nào? → A: `TYPESAFE_API_KEY` là công tắc opt-in duy nhất; không có
  cờ enable thứ hai. Tuy nhiên, chỉ được báo lớp cố vấn đang hoạt động sau một probe thật trả về
  typed response hợp lệ; có config nhưng không có tín hiệu không phải là bằng chứng.
- Q: Feature 005 có được biến kết quả `collect_more_labels` của feature 002 thành cổng tự động
  không? → A: Không. Tín hiệu Jev chỉ mang tính cố vấn trong feature này; không được tự chặn, tự
  thay hoặc tự cứu một candidate. (agent decided; basis: holdout v2 chưa đủ coverage và noulmes
  xác nhận host Agent vẫn sở hữu quyết định cuối)
- Q: Upload riêng skill lên Claude Org có đồng nghĩa Jev đã dùng được không? → A: Không. ZIP MAY
  chứa optional advisor adapter nhưng không chứa secret; host vẫn phải có quyền thực thi adapter,
  kết nối mạng và secret injection. Thiếu một trong các năng lực đó thì skill chạy core-only và
  phải nói đúng trạng thái.
- Q: Feature 005 phát hành ở version nào? → A: `0.9.6`; owner đã duyệt ngày 2026-09-29.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Dùng đầy đủ core skill mà không cần TypeSafe (Priority: P1)

Người dùng cài `vi-humanizer` và biên tập tiếng Việt như bình thường mà không cần tài khoản
TypeSafe, SDK, API key hoặc kết nối mạng. Họ không bị chặn bởi lời nhắc thiết lập, lỗi dependency
hay trạng thái evaluator giả thành công.

**Why this priority**: TypeSafe là progressive enhancement. Nếu người dùng không dùng TypeSafe
phải trả giá bằng một skill khó cài hoặc kém ổn định hơn, feature đã đi ngược yêu cầu sản phẩm.

**Independent Test**: Cài từng artifact công khai trong môi trường không có key và connector, rồi
chạy các ca biên tập core hiện có. Kết quả hoàn tất bằng workflow Markdown; không có external call,
không có lỗi dependency và mọi trạng thái thẩm định được ghi là *không bật* hoặc *chưa kiểm tra*.

**Acceptance Scenarios**:

1. **Given** một bản cài mới không có TypeSafe, **When** người dùng gọi `vi-humanizer`, **Then** toàn
   bộ cổng thể loại, pattern, style card và năm quy tắc chốt chặn vẫn chạy được.
2. **Given** có key nhưng host không có connector tương thích, **When** skill bắt đầu xử lý,
   **Then** host không báo TypeSafe đang hoạt động, không gọi giả và tiếp tục bằng core workflow.
3. **Given** connector timeout, bị giới hạn lượt gọi hoặc trả response sai contract, **When** đang
   thẩm định một edit, **Then** edit đó trở về Agent với trạng thái *chưa kiểm tra*; lỗi không được
   đổi thành `pass`, `keep` hoặc `replace`.

---

### User Story 2 - Bật và xác minh lớp cố vấn mà không lộ secret (Priority: P2)

Người dùng muốn hưởng lợi từ TypeSafe có một hướng dẫn ngắn để biết host hiện tại có hỗ trợ lớp cố
vấn hay không, thiết lập API key ở môi trường của host, chạy một probe vô hại và phân biệt rõ giữa
*đã cài skill TypeSafe*, *đã opt-in* và *đã quan sát được typed response thật*.

**Why this priority**: Người dùng hiện dễ nhầm việc upload `vi-humanizer`, cài TypeSafe agent skill
hoặc đặt một biến môi trường với một integration đang chạy thật. Setup chỉ đáng tin khi kiểm được
tín hiệu thực tế mà không in hoặc lưu secret.

**Independent Test**: Làm theo hướng dẫn trên một host có connector và một host không có connector.
Host thứ nhất trả typed response cùng model thực tế mà không lộ key; host thứ hai dừng ở hướng dẫn
capability phù hợp và vẫn dùng được core skill.

**Acceptance Scenarios**:

1. **Given** host có connector và key hợp lệ, **When** người dùng chạy bước xác minh, **Then** họ
   nhận được trạng thái *đã xác minh*, model thực tế và thời điểm kiểm tra mà không thấy key.
2. **Given** chỉ cài TypeSafe agent skill để cung cấp tài liệu cho coding agent, **When** chưa có
   runtime connector, **Then** tài liệu không mô tả đó là lớp cố vấn đang hoạt động.
3. **Given** người dùng upload ZIP lên Claude Org, **When** môi trường Org không cung cấp connector
   TypeSafe, **Then** hướng dẫn nói rõ bản upload vẫn là core-only thay vì yêu cầu nhét key vào ZIP.
4. **Given** key không hợp lệ hoặc dịch vụ không phản hồi, **When** probe chạy, **Then** kết quả chỉ
   nêu mã lý do an toàn và bước khắc phục; không ghi request, raw exception hoặc credential.

---

### User Story 3 - Dùng Jev để thẩm định một edit khó quyết (Priority: P3)

Khi core skill đã gọi tên được một lỗi thuộc lát cắt từ/cụm từ của V20 nhưng Agent còn phân vân có
nên sửa hoặc candidate nào vừa tự nhiên vừa an toàn, Agent có thể gửi source span, ngữ cảnh tối
thiểu và các candidate đã tạo sẵn cho Jev. Agent đọc tín hiệu có cấu trúc, tự quyết định giữ hay sửa
và chịu trách nhiệm cho câu cuối.

**Why this priority**: Giá trị của feature không nằm ở việc “đã kết nối API”, mà ở chỗ giúp Agent
phân biệt một từ đơn đúng với một kết hợp bị hụt, đồng thời giảm sửa quá tay mà không giao quyền
viết cho evaluator.

**Independent Test**: Dùng bộ ca có từ đơn đúng, cụm thiếu tiếng, candidate tự nhiên, candidate đổi
nghĩa và `none_of_candidates`. Xác nhận Jev chỉ nhận candidate có trước, trả từng tín hiệu độc lập,
còn Agent mới đưa ra và giải thích quyết định cuối.

**Acceptance Scenarios**:

1. **Given** từ đơn đang đúng nghĩa và đúng vai trò, **When** Jev thẩm định source cùng ngữ cảnh,
   **Then** Agent có đủ tín hiệu để giữ nguyên thay vì ghép thêm tiếng theo quán tính.
2. **Given** source bị hụt một tiếng và có một candidate tự nhiên, giữ nghĩa, **When** Jev thẩm định
   candidate, **Then** Agent có thể chọn candidate đó nhưng quyết định vẫn được ghi là của Agent.
3. **Given** source cần sửa nhưng mọi candidate đều đổi nghĩa, lệch giọng hoặc chỉ là cách diễn đạt
   ít tệ hơn, **When** Jev thẩm định, **Then** không candidate nào được tự động thay vào bản cuối.
4. **Given** có từ hai candidate đủ chuẩn trở lên, **When** cần xếp hạng tương đối, **Then** Jev chỉ
   xếp hạng shortlist đó; kết quả xếp hạng không được cứu candidate đã trượt cổng tuyệt đối.
5. **Given** source hoặc candidate thay đổi sau khi có response, **When** Agent chuẩn bị dùng kết
   quả cũ, **Then** kết quả bị coi là hết hiệu lực và không được áp vào bytes mới.

### Edge Cases

- `TYPESAFE_API_KEY` tồn tại nhưng rỗng, hết hạn hoặc trỏ tới tài khoản không có quota.
- Host đọc được key nhưng không có network, connector hoặc quyền gọi external service.
- Probe từng pass nhưng connector vừa đổi version hoặc model thực tế không còn khớp contract.
- Cùng một request có nhiều edit; tín hiệu của edit này không được gán nhầm cho edit khác.
- Một edit nằm giữa batch dài; câu hỏi phải gọi edit/candidate bằng stable key, không bằng vị trí.
- Candidate giống source hoặc trùng nhau sau Unicode/whitespace normalization.
- Source cần sửa nhưng chỉ có một candidate và candidate đó không đủ chuẩn.
- Protected region, trích dẫn nguyên văn, tên riêng hoặc dữ liệu có cấu trúc nằm sát source span.
- Văn bản chứa secret, dữ liệu khách hàng hoặc thông tin mà người dùng không muốn gửi ra ngoài.
- Người dùng yêu cầu đổi giọng; lựa chọn style không được biến thành phán đoán lỗi V20.
- Response đến sau khi Agent đã sửa source hoặc thay candidate.
- TypeSafe trả xác suất gần ngưỡng hoặc hai lần probe cho kết quả khác nhau.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Core `vi-humanizer` MUST tiếp tục cài và chạy đầy đủ mà không cần tài khoản TypeSafe,
  API key, SDK, connector hoặc mạng.
- **FR-002**: `TYPESAFE_API_KEY` MUST là công tắc opt-in duy nhất; feature MUST NOT tạo thêm cờ
  enable có thể lệch trạng thái với credential.
- **FR-003**: Key, token hoặc credential MUST chỉ được nạp qua cơ chế secret của host; MUST NOT
  nằm trong prompt, command history, file cấu hình được commit, archive, log hoặc output.
- **FR-004**: Host MUST tách ít nhất ba trạng thái: `core_only`, `advisor_unchecked` và
  `advisor_verified`. Sự tồn tại của key hoặc config MUST NOT tự tạo trạng thái verified.
- **FR-005**: `advisor_verified` MUST chỉ được ghi sau một probe thật nhận typed response hợp lệ,
  ghi nhận model thực tế và hoàn tất mà không lộ secret hoặc prose riêng tư.
- **FR-006**: Khi thiếu key, connector, SDK hoặc network; khi timeout, rate limit, auth failure hay
  response sai contract; feature MUST fail open về core workflow và ghi *chưa kiểm tra*, không ghi
  `pass` và không tự suy ra quyết định biên tập.
- **FR-007**: Tài liệu setup MUST phân biệt rõ TypeSafe agent skill cung cấp kiến thức cho coding
  agent với runtime connector thực sự gọi Jev.
- **FR-008**: Tài liệu setup MUST có decision path riêng cho host hỗ trợ connector, host chỉ chạy
  skill Markdown và Claude Org upload; không môi trường nào được yêu cầu đóng gói secret vào skill.
- **FR-009**: Host LLM MUST tạo từ một đến ba candidate trước external call. Jev MUST NOT sinh, nối,
  sửa, hoàn thiện hoặc diễn đạt lại prose.
- **FR-010**: Host LLM/Agent MUST là thành phần duy nhất quyết định có sửa hay không, chọn candidate
  nào và tạo bản cuối. Tín hiệu Jev MUST chỉ mang tính cố vấn trong feature 005.
- **FR-011**: Runtime advisory ban đầu MUST giới hạn ở lát cắt V20 đã được features 001–002 đánh
  giá: `lexically_incomplete` và `unnatural_collocation`, cùng các trường hợp **Không flag** liên
  quan. Style selection và các pattern khác nằm ngoài scope.
- **FR-012**: Chỉ một edit mà core skill đã gọi tên được pattern, có source span ổn định, ngữ cảnh
  tối thiểu và candidate hợp lệ mới MAY gọi Jev. Feature MUST NOT gửi toàn bộ tài liệu chỉ để thẩm
  định một edit cục bộ.
- **FR-013**: Mỗi câu hỏi MUST thẩm định một chiều độc lập: source có cần sửa, candidate có sửa đúng
  lỗi, giữ nghĩa và sắc thái, giữ giọng/thể loại, cùng từng rủi ro an toàn. Một score tổng hợp duy
  nhất MUST NOT che các tín hiệu xung đột.
- **FR-014**: Edit, candidate và câu hỏi trong một batch MUST được gọi bằng stable key; MUST NOT gọi
  bằng chỉ số vị trí. Kết quả MUST liên kết lại đúng source/candidate bytes đã gửi.
- **FR-015**: Xếp hạng tương đối MUST chỉ chạy khi có ít nhất hai candidate đã qua cổng tuyệt đối;
  nó MUST NOT tạo quyền thay source hoặc cứu một candidate không đủ chuẩn.
- **FR-016**: Feature MUST NOT đưa threshold mẫu từ tài liệu TypeSafe vào production như ngưỡng đã
  hiệu chỉnh. Mọi threshold ảnh hưởng routing MUST truy được về policy và evidence đã duyệt.
- **FR-017**: Do feature 002 kết luận `collect_more_labels`, feature 005 MUST NOT dùng Jev làm hard
  gate, auto-replace hoặc auto-reject. Mọi response chỉ là evidence cho Agent xem xét.
- **FR-018**: Protected region, credential, ground-truth label, baseline observation, candidate
  provenance và dữ liệu không cần cho phán đoán MUST NOT được gửi cho TypeSafe.
- **FR-019**: Telemetry, health output và artifact có thể commit MUST NOT chứa raw source, raw
  candidate, request body, raw response, raw exception, credential hoặc định danh cá nhân/tổ chức.
- **FR-020**: Kết quả Jev MUST bị bỏ nếu source, context tối thiểu, candidate set, question version
  hoặc model thực tế không còn khớp lần gọi.
- **FR-021**: Runtime MUST giới hạn thời gian và số lần retry để lỗi external service không kéo dài
  đáng kể workflow core hoặc tạo vòng lặp gọi vô hạn.
- **FR-022**: Offline tests MUST dùng fake adapter và MUST chứng minh không có external call. Live
  probe MUST là thao tác opt-in riêng, dùng fixture trung tính và báo usage/cost thực tế.
- **FR-023**: Public package MUST cung cấp đủ hướng dẫn để người dùng biết TypeSafe có phải là tùy
  chọn, cách xác minh readiness và cách tắt bằng việc bỏ credential; core dependency MUST không đổi.
- **FR-024**: Feature MUST NOT sửa pattern inventory, style resolver hoặc quyền quyết định đã chốt
  trong features 001–004.

### Key Entities

- **Advisor Capability State**: Trạng thái `core_only`, `advisor_unchecked` hoặc
  `advisor_verified`, kèm reason code an toàn, model thực tế và thời điểm probe nếu có.
- **Advisory Edit Case**: Một edit V20 gồm stable ID, source span, context tối thiểu, candidate set,
  content binding và version của question contract; không chứa ground truth hay provenance trong
  phần gửi tới evaluator.
- **Typed Advisory Judgment**: Các tín hiệu độc lập về nhu cầu sửa, chất lượng candidate, giữ
  nghĩa/giọng và safety; không chứa câu văn mới hoặc action cuối.
- **Host Decision Record**: Quyết định giữ, sửa hoặc xem lại do Agent đưa ra, có thể tham chiếu
  judgment nhưng không mạo nhận judgment là người ra quyết định.
- **Runtime Health Summary**: Thống kê không chứa raw prose về checked/unchecked, reason code,
  latency, usage, cost và model thực tế.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% ca core regression hoàn tất khi không có key, connector hoặc network; không ca
  nào phát sinh external call hoặc lỗi dependency.
- **SC-002**: 100% trạng thái `advisor_verified` trong test và live evidence có typed response thật,
  model thực tế và timestamp; config/key presence đơn thuần tạo 0 verified record.
- **SC-003**: 100% service/auth/timeout/malformed-response case trở về core workflow với trạng thái
  *chưa kiểm tra*; 0 case bị đổi thành `pass`, auto-keep, auto-replace hoặc auto-reject.
- **SC-004**: Trong corpus feature 005, 0 request gọi Jev trước khi candidate tồn tại và 0 response
  chứa prose mới do Jev sinh.
- **SC-005**: 100% advisory case liên kết judgment về đúng stable edit/candidate bytes; mọi case
  stale hoặc mismatch đều bị bỏ.
- **SC-006**: 100% protected-region và privacy fixtures chứng minh chỉ source span cùng context tối
  thiểu được gửi; 0 secret, label, provenance hoặc raw document xuất hiện trong request capture.
- **SC-007**: 100% runtime log, health output và artifact commit vượt privacy scan, không chứa raw
  prose, credential, request/response body, raw exception hoặc định danh riêng.
- **SC-008**: Người bảo trì có thể dùng hướng dẫn công khai để xác định trong tối đa ba phút rằng
  host đang core-only, thiếu connector hay advisor đã verified, mà không cần mở source code.
- **SC-009**: Trên các ca lặp lại dành cho stable-key và batch-position, target edit được liên kết
  đúng ở mọi lần chạy; kết quả không được tính là đạt nếu chỉ pass một lần.
- **SC-010**: Public package vẫn cài được bằng cả artifact agent-skill và Claude Org ZIP; TypeSafe
  không trở thành core dependency và không secret nào xuất hiện trong hai archive.

## Assumptions

- Feature 001–002 là nguồn bằng chứng hiện có cho lát cắt V20. Kết luận
  `collect_more_labels` cho phép tiếp tục thử nghiệm/cố vấn, không cho phép tự động hóa quyết định.
- TypeSafe agent skill giúp agent hiểu API và cách thiết kế câu hỏi; nó không tự biến host thành một
  runtime connector. Feature 005 phải diễn đạt đúng giới hạn này.
- Một số host, đặc biệt môi trường chỉ upload skill Markdown, có thể không cung cấp external tool.
  Core-only là một kết quả được hỗ trợ, không phải lỗi cài đặt.
- Người dùng chịu trách nhiệm xem chính sách dữ liệu của TypeSafe trước khi opt-in gửi văn bản;
  feature vẫn phải tối thiểu hóa dữ liệu và loại protected region bất kể chính sách đó.
- Model alias, SDK và API contract có thể thay đổi. Plan phải khóa version/digest phù hợp và xác
  minh model thực tế thay vì suy ra từ config.
- Live probe dùng quota thật nên chỉ chạy khi owner hoặc người dùng đã opt-in rõ; offline CI không
  dùng credential.
