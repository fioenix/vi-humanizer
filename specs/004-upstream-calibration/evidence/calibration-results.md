# Kết quả calibration và placement

**Ngày chốt placement**: 2026-09-28

## Placement decisions

| Hypothesis | Decision | Owner | Pattern | Ranh giới |
|---|---|---|---|---|
| ARG | `new-pattern` | V | V23 | V23 bắt thiếu đối tượng tranh luận; B5 chỉ bắt khuôn song hành nâng giọng/lặp ý |
| QUAL | `new-pattern` | V | V24 | Chỉ flag modal cùng chức năng; khác phạm vi nghĩa thì giữ |
| REL | `new-pattern` | V | V25 | Chỉ dùng quan hệ cụ thể có sẵn trong phạm vi tài liệu |
| AUTH | `extend-existing` + `new-pattern` | B + K | B8 + K7 | B8 sở hữu claim thuyết phục; K7 sở hữu attribution làm bằng chứng |

Lý do không `defer`: 12 ca dương đều có edit boundary nhỏ và 12 ca âm có điều kiện loại trừ gọi
tên được. Lý do không mở rộng V9/V17/V20: các pattern đó không ngụ ý lỗi quan hệ hoặc modal scope.
Lý do không tạo một V-pattern cho AUTH: một câu mượn uy tín chỉ trở thành lỗi theo hai chức năng
khác nhau ở profile B và K; cross-reference ngăn hai pattern cùng sửa một câu.

## GREEN results

Đã chạy tay trên revision V23–V25, B8 và K7, không đổi expected labels đã khóa.

| Hypothesis | Positive | Negative | Giữ nghĩa |
|---|---:|---:|---|
| ARG | 3/3 flag bằng V23 | 3/3 keep | Chỉ cắt vỏ phản biện; khẳng định thật giữ nguyên |
| QUAL | 3/3 flag bằng V24 | 3/3 keep | Mỗi edit giữ một mức dè dặt; modal khác phạm vi không bị cắt |
| REL | 3/3 flag bằng V25 | 3/3 keep | Chỉ khôi phục quan hệ có trong nguồn; không nâng quan hệ chưa chắc chắn |
| AUTH | 3/3 flag bằng B8/K7 đúng profile | 3/3 keep | Không tự đặt nguồn; attribution có citation/định danh được giữ |

Kết quả tổng: 12/12 positive flag, 12/12 negative keep, 0 ca bị hai pattern cùng sửa.

Structural gate:

```text
ARG 3 flag + 3 keep
QUAL 3 flag + 3 keep
REL 3 flag + 3 keep
AUTH 3 flag + 3 keep
V23 contract=PASS
V24 contract=PASS
V25 contract=PASS
K7 contract=PASS
cross-reference=PASS
Gói vi-humanizer v0.8.0 hợp lệ, gồm 55 pattern
```
