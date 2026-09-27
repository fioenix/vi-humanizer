# Contract: Calibration và pattern placement

## Input

- Một hypothesis upstream.
- Sáu case tiếng Việt: ba dương, ba âm.
- Pattern inventory hiện tại và constitution.
- Ý kiến TypeSafe nếu đã chạy; output này không bắt buộc và không có quyền override case.

## Decision order

1. Xác định lỗi có gọi tên được mà không nhắc “AI” hay không.
2. Kiểm mọi ca âm và nêu **Không flag** cần thiết.
3. Nếu ca dương/âm chưa tách được, chọn `defer`.
4. Nếu tách được, kiểm pattern hiện có đã ngụ ý lỗi chưa; có thì `extend-existing`.
5. Nếu cần pattern mới, chọn owner:
   - V: lỗi giữ nguyên bản chất ở mọi thể loại được phép biên tập;
   - B: phụ thuộc tác giả, người đọc, marketing hoặc mục đích thuyết phục;
   - K: phụ thuộc chuẩn bằng chứng của kỹ thuật/doanh nghiệp/học thuật.
6. Khi hai pattern chạm nhau, pattern hẹp hơn phải trỏ sang pattern kia và nói phần mình sở hữu.

## Accepted decisions for implementation

| Hypothesis | Decision | Owner/pattern |
|---|---|---|
| ARG | `new-pattern` | V23; B5 chỉ sở hữu khuôn song hành và trỏ V23 khi ý bị phản biện không có đối tượng |
| QUAL | `new-pattern` | V24; loại trừ modal khác phạm vi nghĩa |
| REL | `new-pattern` | V25; chỉ dùng quan hệ đã có trong phạm vi tài liệu |
| AUTH | `extend-existing` + `new-pattern` | B8 sở hữu claim thuyết phục; K7 sở hữu attribution làm bằng chứng; hai bên trỏ nhau |

Những quyết định này bị hạ thành `defer` nếu calibration case không pass; không được sửa expected
label sau khi pattern đã viết để ép GREEN.

## Pattern contract

Mỗi pattern revision có đủ:

- **Dấu hiệu**: điều kiện dương và phạm vi ngữ cảnh;
- **Vì sao**: lỗi cụ thể với người đọc;
- **Sửa**: edit nhỏ nhất, lấy dữ kiện từ input;
- **Không flag**: toàn bộ boundary hợp lệ từ ca âm.

## Release contract

- Pattern number liên tục.
- README inventory, source note, changelog và version đồng bộ.
- Validator báo đúng tổng pattern cuối.
- Public diff không có tên người/công ty/tổ chức, dữ liệu nội bộ, secret hoặc local path.
- Runtime package không gọi TypeSafe và không chứa specs/eval/artifacts.
