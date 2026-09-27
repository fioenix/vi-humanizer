# Feature Specification: Bộ giải nhiều phong cách viết

**Feature Branch**: `codex/003-multi-writing-style`

**Created**: 2026-09-28

**Status**: Approved by owner delegation

**Input**: Nâng `vi-humanizer` từ hai nhánh giọng quá rộng thành cơ chế chọn phong cách tiếng Việt theo mục đích, người đọc, thanh ngữ vực, kênh và mẫu giọng; vẫn giữ quy tắc ngôn ngữ tách khỏi lựa chọn phong cách.

## Clarifications

### Session 2026-09-28

- Q: Multi writing style có phải là danh sách tone phẳng như `formal/casual` không? → A: Không. Mỗi lượt biên tập giải năm chiều: mục đích, người đọc và quan hệ, thanh ngữ vực, kênh, cùng bằng chứng giọng của đúng người viết; kết quả chọn một base profile và một style card tương thích.
- Q: Feature 003 có dùng Jev hoặc policy v2 để tự quyết phong cách không? → A: Không. Feature phải chạy độc lập bằng Markdown; kết quả 002 là `collect_more_labels`, nên không đưa evaluation policy vào runtime.
- Q: Style card có được biến thành lỗi ngôn ngữ hoặc pattern mới không? → A: Không. Style card chỉ điều khiển cách giữ giọng và cách giải quyết lựa chọn hợp lệ; V/B/K/T chỉ flag lỗi theo hợp đồng hiện tại.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Chọn đúng phong cách thay vì ép vào hai tone (Priority: P1)

Người dùng đưa một văn bản cần biên tập. Skill xác định mục đích, người đọc, quan hệ xưng hô, mức trang trọng, kênh và mẫu giọng trước khi sửa, rồi chọn đúng một phong cách làm chuẩn cho từng phần văn bản. Một bài kể trải nghiệm, chat công việc, bài chuyên môn công khai, nội dung marketing, hướng dẫn kỹ thuật, SOP vận hành và bài học thuật không còn bị gom thành hai tone chung chung.

**Why this priority**: Nếu chỉ có “cá nhân” và “trung tính”, cùng một profile phải xử lý nhiều mục đích trái nhau. Bản sửa vì thế có thể đúng ngữ pháp nhưng vẫn sai nhịp, sai xưng hô hoặc sai mức trang trọng.

**Independent Test**: Đưa bảy ca trung tính có cùng một ý nhưng khác mục đích và người đọc; xác nhận mỗi ca được định tuyến tới đúng phong cách, giữ nguyên dữ kiện, đồng thời không áp lựa chọn của phong cách này sang phong cách khác.

**Acceptance Scenarios**:

1. **Given** một bài kể trải nghiệm cá nhân có mẫu giọng, **When** skill biên tập, **Then** bản sửa giữ ngôi kể, nhịp câu, chỗ dè dặt và cách chêm từ ổn định của mẫu thay vì kéo sang giọng báo cáo.
2. **Given** một tin nhắn phối hợp giữa đồng nghiệp, **When** skill biên tập, **Then** bản sửa giữ cách xưng hô và nhịp trao đổi trực tiếp, không biến thành bài blog hoặc công văn.
3. **Given** một bài chuyên môn công khai, **When** skill biên tập, **Then** bản sửa vẫn có quan điểm cá nhân nhưng giữ lập luận, dẫn chứng và mức trang trọng phù hợp với người đọc rộng hơn.
4. **Given** một nội dung marketing, **When** skill biên tập, **Then** bản sửa giữ mục tiêu thuyết phục và lời kêu gọi có thật nhưng không thêm lời hứa, độ khẩn cấp hoặc dữ kiện mới.
5. **Given** README hoặc hướng dẫn kỹ thuật, **When** skill biên tập, **Then** bản sửa ưu tiên khả năng tra cứu, thuật ngữ nhất quán và câu lệnh rõ, không thêm cá tính giả.
6. **Given** SOP hoặc báo cáo vận hành, **When** skill biên tập, **Then** bản sửa giữ vai trò, điều kiện, cam kết và cấu trúc quét nhanh, không kéo thành lời trò chuyện.
7. **Given** văn bản học thuật, **When** skill biên tập, **Then** bản sửa giữ thuật ngữ, mức độ dè dặt và quy ước trích dẫn, không thuần Việt hóa hoặc làm thân mật để “dễ đọc”.

---

### User Story 2 - Giải xung đột giữa yêu cầu, thể loại và mẫu giọng (Priority: P2)

Người dùng có thể yêu cầu một phong cách cụ thể, cung cấp mẫu văn, hoặc có hồ sơ văn phong đã lưu. Skill cần dùng thứ tự ưu tiên rõ để không lấy mặc định của profile đè lên yêu cầu hiện tại, không lấy một mẫu đơn lẻ đè lên ràng buộc thể loại, và không dùng hồ sơ của người này cho người khác.

**Why this priority**: Nhiều phong cách chỉ hữu ích nếu xung đột được giải nhất quán. Nếu không, càng thêm style card càng làm hành vi khó đoán.

**Independent Test**: Chạy các cặp ca có yêu cầu hiện tại, mẫu giọng, hồ sơ và thể loại xung đột; xác nhận resolver luôn áp cùng thứ tự ưu tiên và dừng hỏi khi thiếu thông tin thật sự làm thay đổi kết quả.

**Acceptance Scenarios**:

1. **Given** yêu cầu hiện tại nêu rõ người đọc và mức trang trọng, **When** hồ sơ cũ khác với yêu cầu đó, **Then** yêu cầu hiện tại thắng.
2. **Given** mẫu văn ổn định của đúng người viết, **When** style card mặc định khác về nhịp, xưng hô hoặc mức chêm tiếng Anh, **Then** mẫu văn thắng trong phạm vi không vi phạm thể loại và năm quy tắc chốt chặn.
3. **Given** chỉ có một cách viết xuất hiện một lần trong mẫu, **When** không đủ bằng chứng đó là thói quen, **Then** skill không nâng nó thành đặc tính giọng.
4. **Given** không xác định được người đọc hoặc quan hệ xưng hô và hai lựa chọn sẽ tạo ra bản sửa khác đáng kể, **When** không có bằng chứng nào khác, **Then** skill hỏi một câu ngắn thay vì tự đổi đại từ.
5. **Given** văn bản thuộc nhóm chỉ được rà typography, **When** người dùng không chủ động yêu cầu viết lại thể loại đó, **Then** style card không vượt qua cổng loại trừ.

---

### User Story 3 - Xử lý tài liệu pha nhiều chức năng mà không rò giọng (Priority: P3)

Một tài liệu có thể chứa phần giới thiệu có tác giả hiện diện, phần hướng dẫn trung tính, trích dẫn, code và lời kêu gọi. Skill cần định tuyến theo phần có chức năng khác nhau thay vì ép cả file vào một phong cách, đồng thời vẫn giữ một giọng chung ở những phần cùng chức năng.

**Why this priority**: Tài liệu thật thường pha nhiều loại nội dung. Chọn một tone cho toàn file làm phần kỹ thuật bị thân mật hóa hoặc phần cá nhân bị làm phẳng.

**Independent Test**: Dùng một tài liệu ghép gồm đoạn kể, hướng dẫn, bảng, code, trích dẫn và lời kêu gọi; xác nhận chỉ phần văn xuôi được phép mới bị sửa, mỗi phần dùng đúng phong cách và các vùng phải giữ nguyên không đổi byte.

**Acceptance Scenarios**:

1. **Given** một file có phần mở đầu cá nhân và phần hướng dẫn kỹ thuật, **When** skill biên tập, **Then** phần mở đầu giữ giọng tác giả còn phần hướng dẫn giữ thuật ngữ và nhịp thao tác.
2. **Given** code, schema, bảng tham số hoặc trích dẫn nguyên văn nằm giữa văn xuôi, **When** skill biên tập, **Then** các vùng đó không nhận style card và không đổi nội dung.
3. **Given** hai phần có cùng mục đích nhưng nhịp hoặc xưng hô dao động không chủ đích, **When** skill biên tập, **Then** chúng được đưa về cùng style brief mà không san bằng các khác biệt có dụng ý.
4. **Given** người dùng chỉ yêu cầu bản cuối, **When** resolver đã chọn phong cách, **Then** kết quả không kèm nhãn phong cách hoặc phân tích; bằng chứng định tuyến chỉ được nêu khi người dùng yêu cầu giải thích hay rà soát.

### Edge Cases

- Văn bản quá ngắn nên không đủ bằng chứng để suy ra nhịp hoặc xưng hô.
- Người dùng gọi tên một tone nhưng mô tả cụ thể của họ khác nghĩa thông thường của nhãn đó.
- Mẫu văn chứa lỗi gõ, lỗi ngôn ngữ hoặc một câu cố ý phá giọng chung.
- Một người viết có nhiều giọng theo kênh; hồ sơ đúng người nhưng sai phạm vi.
- Nội dung marketing nằm trong tài liệu kỹ thuật hoặc lời giải thích kỹ thuật nằm trong bài cá nhân.
- Văn bản đổi người nói trong trích dẫn, hội thoại hoặc biên bản.
- Yêu cầu “viết như người khác” có nguy cơ nhại giọng thay vì chỉ giữ đặc tính được nêu rõ.
- Người dùng không yêu cầu đổi phong cách; skill chỉ được sửa lỗi và giữ phong cách đang có.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Trước khi sửa, skill MUST phân biệt tối thiểu năm chiều: mục đích giao tiếp, người đọc và quan hệ, thanh ngữ vực, kênh, cùng bằng chứng giọng của đúng người viết.
- **FR-002**: Resolver MUST chọn đúng một base profile và tối đa một style card cho mỗi phần văn bản; MUST NOT chồng nhiều preset mâu thuẫn lên cùng một phần.
- **FR-003**: Registry MUST có ít nhất bảy style card: kể trải nghiệm cá nhân, phối hợp công việc, chuyên môn công khai, marketing thuyết phục, hướng dẫn kỹ thuật, vận hành doanh nghiệp và học thuật phân tích.
- **FR-004**: Mỗi style card MUST nêu người đọc, mục đích, mức trang trọng, cách xưng hô, nhịp câu, chính sách thuật ngữ/tiếng Anh, cách kết và những điều tuyệt đối không tự thêm.
- **FR-005**: Style card MUST là hướng dẫn giữ hoặc giải quyết lựa chọn hợp lệ; MUST NOT biến khác biệt phong cách thành lỗi ngôn ngữ, pattern mới hoặc căn cứ suy đoán tác giả.
- **FR-006**: Thứ tự ưu tiên MUST là: yêu cầu hiện tại; ràng buộc thể loại và vùng phải giữ nguyên; mẫu văn hiện tại hoặc hồ sơ đúng người, đúng phạm vi; style card; rồi mặc định của base profile.
- **FR-007**: Yêu cầu dùng một phong cách cụ thể MUST NOT vượt qua năm quy tắc chốt chặn, tự thêm dữ kiện, đổi nghĩa, đổi mức chắc chắn hoặc phá thuật ngữ bắt buộc.
- **FR-008**: Khi nhãn phong cách và mô tả cụ thể xung đột, resolver MUST làm theo mô tả cụ thể và coi nhãn chỉ là gợi ý.
- **FR-009**: Một đặc tính cá nhân MUST chỉ được dùng khi có bằng chứng ổn định và đúng danh tính/phạm vi; một lỗi đơn lẻ MUST NOT trở thành đặc tính giọng.
- **FR-010**: Văn bản hỗn hợp MUST được chia theo chức năng nội dung; code, schema, dữ liệu có cấu trúc, trích dẫn nguyên văn và vùng typography-only MUST giữ ranh giới hiện tại.
- **FR-011**: Skill MUST giữ nguyên hành vi trả kết quả hiện tại: chỉ bản cuối khi người dùng yêu cầu viết lại; chỉ giải thích lựa chọn style khi người dùng yêu cầu rà soát, so sánh hoặc giải thích.
- **FR-012**: Nếu hai lựa chọn phong cách hợp lý sẽ làm thay đổi đại từ, thanh ngữ vực hoặc mục đích mà không có đủ bằng chứng, skill MUST hỏi đúng một câu ngắn; với khác biệt nhỏ, MUST giữ cách đang có.
- **FR-013**: Feature MUST chạy hoàn toàn bằng Markdown, không cần network, secret, TypeSafe hoặc evaluation policy; feature 002 MUST vẫn chỉ là evidence lane sau quyết định `collect_more_labels`.
- **FR-014**: Feature MUST NOT thêm, bỏ hoặc đổi nghĩa V1–V22, T1–T6, B1–B17 hoặc K1–K6; mọi thay đổi pattern từ upstream thuộc một calibration slice khác.
- **FR-015**: Tài liệu và ví dụ public MUST dùng nội dung trung tính, không chứa tên công ty, tổ chức, dữ liệu nội bộ hoặc hồ sơ cá nhân.
- **FR-016**: Mỗi style card MUST có ít nhất một ca dương và một ca chống rò giọng trong bộ kiểm thử chạy tay; cặp ca MUST giữ cùng dữ kiện để cô lập khác biệt phong cách.
- **FR-017**: README, `SKILL.md`, registry phong cách, test tay, package inventory và lịch sử phiên bản MUST mô tả cùng một tập style card và cùng thứ tự ưu tiên.

### Key Entities

- **Style Context**: Tập bằng chứng trước khi sửa gồm mục đích, người đọc/quan hệ, thanh ngữ vực, kênh, thể loại, vùng phải giữ nguyên và mẫu giọng.
- **Base Profile**: Bộ giới hạn/pattern hiện có cho văn bản có giọng cá nhân hoặc văn bản kỹ thuật, doanh nghiệp, học thuật.
- **Style Card**: Hợp đồng ngắn cho một mục đích viết, không phải nhãn lỗi; mô tả các lựa chọn hợp lệ và ranh giới không được vượt qua.
- **Style Brief**: Kết quả giải cho một phần văn bản, kết hợp base profile, một style card và các override có bằng chứng từ yêu cầu/mẫu giọng.
- **Protected Region**: Phần không nhận style card hoặc chỉ nhận typography theo cổng hiện tại.
- **Style Calibration Pair**: Hai hoặc nhiều ca giữ cùng nội dung nhưng khác mục đích/người đọc để kiểm tra resolver và chống rò giọng.

## Success Criteria *(mandatory)*

- **SC-001**: 100% ca trong ma trận bảy phong cách chọn đúng base profile và style card đã gắn nhãn, không cần network hoặc secret.
- **SC-002**: 100% cặp chống rò giọng giữ đúng dữ kiện nhưng không mang đại từ, nhịp, thuật ngữ hoặc lời kêu gọi của phong cách đối chứng.
- **SC-003**: 100% ca xung đột áp đúng thứ tự ưu tiên; không có hồ sơ cũ hoặc style card nào đè lên yêu cầu hiện tại hợp lệ.
- **SC-004**: 100% protected region trong ca tài liệu hỗn hợp giữ nguyên byte; chỉ văn xuôi trong phạm vi được phép nhận style brief.
- **SC-005**: 0 style card tạo dữ kiện, lời hứa, độ khẩn cấp, quan hệ xưng hô hoặc mức chắc chắn không có trong đầu vào.
- **SC-006**: Mỗi style card có ít nhất một ca dương và một ca âm/chống rò giọng được ghi trong test tay; toàn bộ package gate hiện có đều pass.
- **SC-007**: `SKILL.md` và mỗi file profile vẫn nằm trong giới hạn dòng của repo, còn gói cài đặt chỉ chứa payload public của skill.

## Assumptions

- “Nhiều phong cách” là nhiều mục đích viết có ràng buộc rõ, không phải bắt chước vô hạn giọng của từng cá nhân.
- Hai base profile hiện có tiếp tục sở hữu pattern phụ thuộc thể loại; feature 003 thêm lớp resolver và style card, không nhân đôi pattern.
- Mẫu trong yêu cầu hiện tại đáng tin hơn memory cũ; không có mẫu thì giữ phong cách đang có thay vì tự “làm cho có cá tính”.
- Multi-style áp cho biên tập văn bản, không mở rộng skill thành công cụ sinh nội dung từ trang trắng.
- Việc hiệu chỉnh bốn khoảng trống từ `blader/humanizer` 3.0.0 diễn ra sau 003 và không được dùng để lách FR-014.
