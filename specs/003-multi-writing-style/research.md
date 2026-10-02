# Research: Bộ giải nhiều phong cách viết

## Decision 1: Dùng model tổ hợp, không dùng enum tone phẳng

**Decision**: Style context gồm mục đích, người đọc/quan hệ, thanh ngữ vực, kênh và bằng chứng giọng; resolver tạo một style brief từ các chiều này.

**Rationale**: `formal/casual` không phân biệt được chat đồng nghiệp với bài kể cá nhân, hoặc SOP với bài học thuật. Ai trả giá cho enum phẳng là người đọc: văn bản đúng câu nhưng sai quan hệ và sai chức năng.

**Alternatives considered**:

- Thêm nhiều giá trị tone độc lập: dễ gọi nhưng các giá trị chồng nhau và không giải được xung đột.
- Tạo một profile cho mỗi style: nhân đôi pattern B/K và làm drift source of truth.
- Suy giọng chỉ từ mẫu văn: không có mẫu thì mất fallback; mẫu còn có thể chứa lỗi hoặc sai phạm vi.

## Decision 2: Giữ hai base profile, thêm bảy style card

**Decision**: Hai profile hiện có tiếp tục làm cổng pattern. Registry mới có bảy card: kể trải nghiệm cá nhân, phối hợp công việc, chuyên môn công khai, marketing thuyết phục, hướng dẫn kỹ thuật, vận hành doanh nghiệp và học thuật phân tích.

**Rationale**: Bảy card bao phủ các nhóm người dùng đã có trong route hiện tại nhưng tách được mục đích, người đọc và cách kết. Chúng là “cách giữ giọng” chứ không phải bảy bộ lỗi.

**Alternatives considered**:

- Chỉ tách `formal`, `neutral`, `casual`: vẫn nhập nhằng kênh và mục đích.
- Cho style card tùy ý không registry: khó kiểm thử, khó giữ nhất quán giữa runtime và README.
- Port hệ nhóm của `blader/humanizer`: upstream 3.0.0 không có multi-style; đó là pattern organization cho tiếng Anh.

## Decision 3: Precedence là hợp đồng, không phải heuristic mềm

**Decision**: Yêu cầu hiện tại → ràng buộc thể loại/protected region → mẫu hiện tại hoặc hồ sơ đúng người và phạm vi → style card → mặc định base profile.

**Rationale**: Nếu precedence không cố định, cùng đầu vào có thể đổi kết quả theo memory được nạp hay thứ tự agent đọc file. Yêu cầu hiện tại phải thắng, nhưng không được phá bảo toàn nghĩa và các vùng bất khả xâm phạm.

**Alternatives considered**:

- Mẫu văn luôn thắng: có thể mang lỗi hoặc sai kênh.
- Profile luôn thắng: làm mất giọng cá nhân và vô hiệu hóa yêu cầu cụ thể.
- Merge mọi tín hiệu: không xác định ai chịu trách nhiệm khi hai tín hiệu xung đột.

## Decision 4: Chia tài liệu theo chức năng trước khi chọn style

**Decision**: Một file có thể có nhiều style brief ở các phần khác nhau, nhưng mỗi phần chỉ có một card. Code, schema, bảng dữ liệu và trích dẫn không nhận card.

**Rationale**: README có thể có lời giới thiệu mang giọng tác giả và phần API trung tính. Ép một style toàn file làm một phía trả giá: hoặc phần kỹ thuật bị “humanize” quá tay, hoặc phần tác giả bị làm phẳng.

**Alternatives considered**:

- Một style cho toàn file: đơn giản nhưng sai với tài liệu hỗn hợp.
- Chọn style theo từng câu: quá vụn, làm giọng dao động và tăng ceremony.

## Decision 5: Hỏi chỉ khi ambiguity thay đổi quan hệ

**Decision**: Chỉ hỏi khi thiếu thông tin sẽ làm đổi đại từ, thanh ngữ vực hoặc mục đích đáng kể; khác biệt nhỏ thì giữ nguyên đầu vào.

**Rationale**: Hỏi mọi lần làm skill khó dùng. Tự chọn đại từ khi chưa biết vai vế có thể xúc phạm người nhận. Ranh giới này đặt chi phí hỏi vào nơi hậu quả cao.

**Alternatives considered**:

- Luôn hỏi style: nhiều ceremony và người dùng thường chỉ chấp nhận mặc định.
- Không bao giờ hỏi: đổi xưng hô hoặc register mà không có bằng chứng.

## Decision 6: Không dùng TypeSafe hoặc policy 002 trong runtime 003

**Decision**: Resolver là instruction Markdown và ca kiểm thử offline. Feature 002 vẫn là evidence lane vì holdout trả `collect_more_labels`.

**Rationale**: Skill phải tự đứng được, và bằng chứng hiện tại cho thấy v2 bỏ sót cả năm ca cần sửa nhưng chưa có candidate chấp nhận được. Đưa policy đó vào route phong cách sẽ trộn hai vấn đề và mở một failure surface không cần thiết.

**Alternatives considered**:

- Dùng Jev chọn style mỗi lượt: thêm network/secret/cost và không có holdout style.
- Dùng code regex theo channel: channel không đủ suy ra quan hệ hoặc mục đích.

## Decision 7: Profile là family, style card là resource con

**Decision**: Mỗi base profile là một thư mục chứa `rules.md` và `styles/`. Resolver cùng registry
dùng chung tiếp tục ở `references/bo-giai-phong-cach.md`.

**Rationale**: Hai thư mục `profiles/` và `styles/` ngang hàng làm người cài hiểu nhầm skill chỉ có
hai phong cách hoặc không biết card thuộc profile nào. Quan hệ cha–con làm bảy card hiện rõ trong
gói Claude Org, đồng thời giữ ranh giới: rules quyết định có căn cứ sửa, card quyết định cách diễn đạt
trong số những lựa chọn còn hợp lệ.

**Alternatives considered**:

- Ba thư mục ngang hàng: đúng về khái niệm nhưng mơ hồ trong cây cài đặt.
- Một profile cho mỗi style: nhân đôi B/K pattern và làm lệch nguồn chuẩn.
- Nhập reference vào từng profile: sao chép resolver và bảng tra dùng chung.

## Prior art and evidence boundary

- `blader/humanizer` 3.0.0 cho writing sample quyền ưu tiên nhưng không có kiến trúc nhiều phong cách; chỉ dùng như prior art cho precedence, không copy pattern tiếng Anh.
- Route hiện tại của `vi-humanizer` đã liệt kê bảy nhóm chức năng nhưng gom vào hai profile. Đây là bằng chứng sản phẩm trực tiếp cho registry mới.
- Các ví dụ và calibration của 003 dùng fixture trung tính. Không đưa giọng cá nhân của một người hoặc thông tin tổ chức vào public package.
