# Bằng chứng RED US3

**Ngày chạy**: 2026-09-28
**Fixture**: MX01 trong `calibration/ca-kiem-thu.md`

Sau khi thêm fixture, chạy:

```text
rg -n "đóng băng.*byte|khôi phục.*byte|so sánh.*byte" references/bo-giai-phong-cach.md SKILL.md
```

Kết quả: exit 1, không có match.

Hợp đồng trước implementation mới chỉ nêu các vùng phải giữ nguyên. Nó chưa bắt buộc đóng băng
byte trước khi chia phần, khôi phục nguyên trạng sau khi sửa và so sánh byte trước khi trả kết quả.
Vì vậy MX01 đang RED ở acceptance quan trọng nhất của SC-004.
