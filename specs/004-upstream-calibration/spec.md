# Feature Specification: Hiệu chuẩn khoảng trống upstream

**Feature Branch**: `codex/004-upstream-calibration`

**Created**: 2026-09-28

**Status**: Approved by owner delegation

**Input**: Đối chiếu `blader/humanizer` 3.0.0 với tiếng Việt, hiệu chuẩn bốn giả thuyết còn thiếu
bằng ca dương và ca chống sửa quá tay, rồi chỉ cập nhật pattern/version khi bằng chứng cho phép.

## Clarifications

### Session 2026-09-28

- Q: Phát hành inventory tăng từ 51 lên 55 pattern bằng version nào? → A: `0.9.0`, vì đây là thay
  đổi hành vi tương thích ngược nên tăng MINOR (agent decided; basis: SemVer và noulmes không tìm
  thấy quyết định cũ nào chi phối lựa chọn này).
- Q: Tích hợp chuỗi feature 001–004 theo cách nào? → A: Dùng một PR cumulative rồi rebase-merge để
  giữ bốn commit nguyên tử trong lịch sử tuyến tính; sau đó tạo tag và GitHub release `v0.9.0` kèm
  archive đã kiểm (agent decided; basis: 002 phụ thuộc 001, các feature cùng một chuỗi và noulmes
  không tìm thấy quyết định cũ nào chi phối lựa chọn này).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Phân biệt lỗi thật với tín hiệu giống lỗi (Priority: P1)

Người bảo trì cần biết bốn hiện tượng upstream có thực sự là lỗi trong tiếng Việt hay chỉ là lựa
chọn hợp lệ theo ngữ cảnh. Bốn giả thuyết gồm: phản biện một ý không ai nêu, chồng từ giảm độ chắc
chắn cùng chức năng, nói quan hệ mơ hồ dù nguồn đã nêu quan hệ cụ thể và mượn uy tín thay cho nội
dung nguồn.

**Why this priority**: Upstream tiếng Anh chỉ cung cấp giả thuyết. Nếu sửa pattern trước khi có ca
âm, skill sẽ sửa quá tay những câu phản biện có đối tượng, mức dè dặt có chủ ý hoặc dẫn nguồn thật.

**Independent Test**: Với mỗi giả thuyết, chạy tối thiểu ba ca dương và ba ca âm ở các ngữ cảnh
khác nhau; người rà phải gọi tên được dấu hiệu, phần cần sửa và lý do mục **Không flag** có hoặc
không áp dụng. Số ca là độ phủ ngữ cảnh, không phải ngưỡng tần suất để kết luận lỗi.

**Acceptance Scenarios**:

1. **Given** một câu phủ định ý chưa từng xuất hiện trong lập luận, **When** bỏ vỏ phản biện mà dữ
   kiện không đổi, **Then** ca được gắn nhãn dương cho giả thuyết phản biện không có đối tượng.
2. **Given** một ADR, FAQ hoặc đoạn tranh luận nêu rõ phương án/ý kiến đang phản biện, **When** cùng
   cấu trúc phủ định xuất hiện, **Then** ca được gắn nhãn âm và không bị sửa.
3. **Given** hai từ chỉ khả năng cùng làm một chức năng, **When** bỏ một từ mà mức chắc chắn không
   đổi, **Then** ca được gắn nhãn dương; nếu hai từ có phạm vi nghĩa khác nhau thì giữ nguyên.
4. **Given** nguồn trong phạm vi tài liệu đã nêu vai trò hay quan hệ cụ thể, **When** bản viết làm
   quan hệ đó mơ hồ hơn, **Then** ca được gắn nhãn dương; thiếu nguồn thì không được tự đoán.
5. **Given** câu viện dẫn một nhóm có thẩm quyền nhưng không cho biết ai hoặc nguồn nào, **When** uy
   tín được dùng thay cho lập luận, **Then** ca được gắn nhãn dương; trích dẫn có tên và phạm vi rõ
   là ca âm.

---

### User Story 2 - Đặt đúng ranh giới V, B hoặc K (Priority: P2)

Người bảo trì cần đưa mỗi hiện tượng đã được xác nhận vào đúng chủ sở hữu: mở rộng pattern gần nhất,
thêm pattern mới ở V/B/K, hoặc hoãn nếu chưa đủ bằng chứng. Một lỗi không được nhân đôi ở hai
profile chỉ vì nó xuất hiện trong nhiều thể loại.

**Why this priority**: Sai vị trí làm một lựa chọn phong cách biến thành lỗi chung, hoặc khiến cùng
một dấu hiệu có hai nguồn chuẩn mâu thuẫn.

**Independent Test**: Áp cây quyết định placement cho cả bốn giả thuyết và kiểm mỗi quyết định với
ma trận ca dương/âm. TypeSafe có thể làm ý kiến ngữ nghĩa thứ hai, nhưng maintainer phải ghi lý do
và code/tài liệu mới quyết định pattern nào được áp dụng.

**Acceptance Scenarios**:

1. **Given** một lỗi giữ nguyên bản chất ở mọi thể loại được phép biên tập, **When** placement được
   xét, **Then** nó thuộc V và có trường hợp loại trừ cho ngữ cảnh hợp lệ.
2. **Given** một tín hiệu chỉ thành lỗi theo người đọc, mục đích thuyết phục hoặc chuẩn dẫn nguồn,
   **When** placement được xét, **Then** nó thuộc đúng profile B hoặc K thay vì V.
3. **Given** pattern hiện có đã ngụ ý đầy đủ hiện tượng, **When** ca mới chỉ mở rộng dấu hiệu,
   **Then** pattern hiện có được mở rộng, không tạo số hiệu mới.
4. **Given** bằng chứng chưa tách được ca dương khỏi ca âm, **When** review kết thúc, **Then** giả
   thuyết được ghi `defer` và inventory không đổi vì giả thuyết đó.

---

### User Story 3 - Phát hành thay đổi đã hiệu chuẩn (Priority: P3)

Người dùng skill nhận được các quy tắc tiếng Việt có ví dụ tự nhiên, trường hợp loại trừ rõ và
không mang dữ liệu cá nhân/tổ chức. README, version, package và bản cài runtime phải đồng bộ với
inventory cuối cùng.

**Why this priority**: Calibration không tạo giá trị nếu kết quả chỉ nằm trong spec hoặc bản cài
vẫn chạy bytes cũ.

**Independent Test**: Chạy toàn bộ ca calibration, validator, 129 test hiện có, plugin validation,
package inspection và đối chiếu SHA-256 source/installed; mọi gate phải đọc từ output mới.

**Acceptance Scenarios**:

1. **Given** một hiện tượng được chấp nhận thành pattern, **When** phát hành, **Then** pattern có đủ
   **Dấu hiệu / Vì sao / Sửa / Không flag**, ví dụ tiếng Việt và ca chống sửa quá tay.
2. **Given** inventory thay đổi, **When** package được tạo, **Then** README, validator và ba nguồn
   version đồng bộ; số hiệu V/T/B/K vẫn liên tục.
3. **Given** repo là mã nguồn mở cá nhân, **When** quét release diff, **Then** không có tên công ty,
   tổ chức, dữ liệu nội bộ, hồ sơ cá nhân, secret hoặc đường dẫn máy cục bộ.

### Edge Cases

- Cấu trúc *không phải X mà Y* có đối lập thật và cả hai vế đều mang thông tin.
- *Có thể sẽ* biểu thị khả năng của một sự kiện tương lai, không phải lúc nào cũng là chồng modal.
- *Dường như có thể* có hai phạm vi nghĩa khác nhau trong văn bản học thuật.
- Nguồn chỉ nói “có liên quan” nên skill không được tự nâng thành vai trò cụ thể.
- Cụm *nhiều người cho rằng* là đối tượng khảo sát thật hoặc một phát biểu đang được phân tích.
- Trích dẫn nêu tên tác giả nhưng không có nguồn trong phạm vi người dùng giao.
- Một giả thuyết có ca dương rõ ở blog nhưng ca âm chiếm ưu thế ở tài liệu học thuật.
- Hai giả thuyết chạm cùng một câu; pattern hẹp hơn phải phân vai, không cùng sửa một chỗ hai lần.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Feature MUST hiệu chuẩn riêng bốn giả thuyết đã nêu; không nhập nguyên danh sách
  pattern tiếng Anh hoặc hai tín hiệu backlog còn lại.
- **FR-002**: Mỗi giả thuyết MUST có tối thiểu ba ca dương và ba ca âm/chống sửa quá tay dùng tiếng
  Việt tự nhiên và nội dung trung tính. Đây là yêu cầu độ phủ, không phải ngưỡng kết luận theo tần suất.
- **FR-003**: Mỗi ca MUST ghi ngữ cảnh, đầu vào, nhãn mong đợi, phần được phép sửa và lý do giữ/sửa.
- **FR-004**: Mỗi giả thuyết MUST kết thúc bằng một quyết định `extend-existing`, `new-pattern` hoặc
  `defer`, kèm chủ sở hữu V/B/K và lý do.
- **FR-005**: Placement MUST tuân theo constitution: V chỉ cho lỗi không phụ thuộc thể loại; lựa
  chọn phụ thuộc người đọc, mục đích hoặc thanh ngữ vực nằm trong B/K.
- **FR-006**: Feature MUST mở rộng pattern gần nhất nếu pattern đó đã ngụ ý hiện tượng; chỉ thêm số
  mới khi không pattern nào hiện có sở hữu lỗi.
- **FR-007**: Pattern được thêm hoặc sửa MUST có đủ bốn mục **Dấu hiệu / Vì sao / Sửa / Không flag**.
- **FR-008**: Sửa từ giảm độ chắc chắn MUST giữ đúng mức dè dặt còn lại; không được biến khả năng
  thành khẳng định.
- **FR-009**: Sửa quan hệ mơ hồ MUST chỉ dùng quan hệ cụ thể đã có trong phạm vi tài liệu; không tìm
  hoặc bịa vai trò từ bên ngoài.
- **FR-010**: Sửa borrowed authority MUST không biến skill thành fact checker; trích dẫn có chủ thể
  và nguồn hợp lệ phải được giữ.
- **FR-011**: TypeSafe/Jev MAY hỗ trợ phân loại hoặc kiểm tra quyết định, nhưng MUST NOT sinh prose,
  thay maintainer đặt threshold hay trở thành dependency runtime của skill.
- **FR-012**: Mọi ví dụ, evidence và tài liệu public MUST không chứa dữ liệu cá nhân, tên công ty,
  tổ chức, dữ liệu nội bộ, secret hoặc đường dẫn máy cục bộ.
- **FR-013**: Nếu pattern inventory đổi, README, validator, calibration, changelog và version MUST
  đổi trong cùng feature; version mới MUST lớn hơn 0.8.0 theo SemVer.
- **FR-014**: Package cuối MUST vẫn chạy độc lập không cần network, TypeSafe hay secret và chỉ chứa
  public skill payload.
- **FR-015**: Full release gates MUST gồm unit tests, package validator, skill discovery, Claude
  plugin validation, diff check, package inventory và installed-byte verification.

### Key Entities

- **Calibration Hypothesis**: Một hiện tượng upstream cần xác nhận trong tiếng Việt, gồm phạm vi,
  dấu hiệu dự kiến, rủi ro false positive và quyết định cuối.
- **Calibration Case**: Mẫu tiếng Việt có ngữ cảnh, input, expected label, edit boundary, rationale
  và provenance không nhạy cảm.
- **Placement Decision**: Kết luận mở rộng pattern, thêm pattern hay hoãn; nêu owner V/B/K và pattern
  liên quan.
- **Pattern Revision**: Thay đổi public đã qua calibration, có đủ bốn mục và số hiệu liên tục.
- **Release Evidence**: Output mới của các gate, digest package và so sánh bytes bản cài.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Cả bốn giả thuyết có ít nhất 3 ca dương và 3 ca âm; 24/24 ca ghi đủ trường bắt buộc.
- **SC-002**: 4/4 giả thuyết có placement decision và không có hai nguồn chuẩn cho cùng một lỗi.
- **SC-003**: 100% pattern được chấp nhận qua toàn bộ ca dương của chính nó và không sửa các ca âm.
- **SC-004**: 100% thay đổi giữ dữ kiện, quan hệ, mức chắc chắn và nguồn có trong đầu vào.
- **SC-005**: Pattern inventory, README và ba nguồn version khớp tuyệt đối; validator báo số pattern
  cuối cùng và mọi dãy V/T/B/K liên tục.
- **SC-006**: Toàn bộ 129 test nền và các gate package/release pass trên final bytes.
- **SC-007**: Privacy scan trên release diff có 0 dữ liệu cá nhân/tổ chức/secret/path cục bộ.

## Assumptions

- Upstream 3.0.0 chỉ là nguồn giả thuyết và prior art, không phải bằng chứng quy phạm tiếng Việt.
- Ba ca dương và ba ca âm mỗi giả thuyết đủ để kiểm ranh giới ngữ cảnh ở slice này, nhưng không
  chứng minh tần suất ngoài thực tế.
- Ca do maintainer tạo được dùng để kiểm hợp đồng; một pattern mới chỉ được nhận nếu các ca tách
  được lỗi khỏi cách viết hợp lệ bằng tiêu chí gọi tên được.
- Hai tín hiệu *one-line closer/dramatic fragment* và mở rộng tổng quát *không phải X mà Y* ngoài
  bốn giả thuyết vẫn ở backlog, trừ phần thật sự thuộc phản biện không có đối tượng.
- Feature 002 tiếp tục ở trạng thái `collect_more_labels`; feature 004 không bật runtime gate.
