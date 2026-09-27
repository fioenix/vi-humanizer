# Research: Hiệu chuẩn khoảng trống upstream

## Decision 1: Upstream chỉ cung cấp giả thuyết

**Decision**: Dùng `blader/humanizer` 3.0.0 để tìm khoảng trống, không port nguyên pattern hoặc
watch list tiếng Anh.

**Rationale**: Repo tiếng Việt có ranh giới V/B/K, cổng thể loại và **Không flag** chặt hơn upstream.
Bốn khoảng trống có thể áp dụng là phản biện không có đối tượng, chồng từ giảm độ chắc chắn, quan
hệ mơ hồ dù nguồn cụ thể và borrowed authority. Hai tín hiệu one-line closer/dramatic fragment và
biến thể rộng của *không phải X mà Y* vẫn ở backlog.

**Alternatives considered**: Port 25 pattern; đồng bộ năm nhóm upstream. Cả hai bị loại vì lẫn quy
tắc tiếng Anh với tiếng Việt và phá source of truth hiện tại.

## Decision 2: Placement dự kiến sau khi đọc pattern hiện có

| Giả thuyết | Placement dự kiến | Lý do |
|---|---|---|
| Phản biện ý không ai nêu | V23 mới; B5 trỏ sang V23 | Lỗi nằm ở đối tượng tranh luận, không ở khuôn song hành của B5 và có thể xảy ra trong mọi văn xuôi được phép |
| Chồng từ giảm độ chắc chắn | V24 mới | Trùng modal cùng chức năng khác V17/V20; **Không flag** giữ các từ có phạm vi nghĩa riêng |
| Làm mơ hồ quan hệ đã rõ | V25 mới | Làm mất quan hệ đã có là lỗi giữ nghĩa, không phụ thuộc thể loại và không thuộc cụm giới từ dài V9 |
| Mượn uy tín thay nội dung | Mở rộng B8 cho claim thuyết phục; thêm K7 cho attribution làm bằng chứng | Cùng bề mặt nhưng lý do lỗi khác theo profile; hai pattern phải phân vai và trỏ lẫn nhau |

Đây là ruling để viết task. Mỗi placement vẫn phải qua đủ 24 ca; ca nào phá ranh giới thì revision
tương ứng được thu hẹp hoặc `defer`, không ép evidence theo ruling.

## Decision 3: TypeSafe chỉ là ý kiến ngữ nghĩa thứ hai

**Decision**: Gọi Jev 1.13.0 bằng tám Choice độc lập trên cùng state công khai, gồm scope và existing
coverage cho mỗi giả thuyết. Không gửi secret, dữ liệu cá nhân/tổ chức hoặc labels của corpus 002.

**Rationale**: Placement là phán đoán ngữ nghĩa đóng; Choice phù hợp hơn sinh prose. Code/tài liệu
giữ quyết định và không dùng confidence làm threshold phát hành.

**Observed result**:

| Câu hỏi | Choice | Confidence | Xác suất đáng chú ý |
|---|---|---:|---|
| Arguing scope | `general_V` | 0.90 | V 0.91 |
| Arguing coverage | `new_pattern` | 0.30 | new 0.53; extend B5 0.46 |
| Qualifier scope | `general_V` | 0.86 | V 0.90 |
| Qualifier coverage | `new_pattern` | 0.96 | new 0.97 |
| Relationship scope | `general_V` | 0.95 | V 0.96 |
| Relationship coverage | `new_pattern` | 1.00 | new 1.00 |
| Authority scope | `profile_pair` | 0.57 | pair 0.65; V 0.31 |
| Authority coverage | `new_pattern` | 0.30 | new 0.43; extend both 0.29 |

Usage: 2,050 input tokens, 432 output tokens. Hai câu coverage confidence thấp được coi là tín hiệu
cần maintainer đọc kỹ, không phải quyền tự động tạo pattern. Sau khi đối chiếu constitution, lựa
chọn là V23 mới thay vì kéo lỗi chung vào B5; với authority, mở rộng B8 ở nhánh thuyết phục và tạo
K7 ở nhánh bằng chứng, tránh một V-rule quá rộng.

**Alternatives considered**: Cho Jev quyết định action; dùng Score để xếp hạng; bật TypeSafe ở
runtime. Đều bị loại vì typed judgment không phải ground truth và feature không cần service ngoài.

## Decision 4: 24 ca là coverage contract, không phải ngưỡng tần suất

**Decision**: Mỗi giả thuyết có ba ca dương và ba ca âm ở các ngữ cảnh khác nhau.

**Rationale**: Sáu ca cho phép kiểm ít nhất ba false-positive boundary của từng rule. Con số này
không được dùng để nói hiện tượng phổ biến hay đặt threshold quét tự động.

**Alternatives considered**: Một cặp ví dụ; corpus lớn có thống kê. Một cặp không đủ lộ ranh giới,
còn corpus thống kê nằm ngoài scope và chưa có nguồn nhãn phù hợp.

## Sources

- `blader/humanizer` release 3.0.0: <https://github.com/blader/humanizer/releases/tag/v3.0.0>
- `blader/humanizer` source 3.0.0: <https://github.com/blader/humanizer/tree/v3.0.0>
- TypeSafe documentation index: <https://docs.typesafe.ai/llms.txt>
- TypeSafe Choice: <https://docs.typesafe.ai/primitives/choice>
- TypeSafe state: <https://docs.typesafe.ai/concepts/state>
