# Bằng chứng US3: tài liệu pha nhiều chức năng

**Ngày chạy**: 2026-09-28
**Fixture**: MX01 trong `calibration/ca-kiem-thu.md`

## Kết quả phân đoạn

| Phần | Kết quả |
|---|---|
| Câu kể mở đầu | `blog-ca-nhan` + `ke-trai-nghiem` |
| Hai câu thao tác | `ky-thuat-doanh-nghiep` + `huong-dan-ky-thuat` |
| Code, bảng tham số, trích dẫn | `typography-only`, không có style card |
| CTA đã có | `blog-ca-nhan` + `marketing-thuyet-phuc` |

Không phần nào nhận hơn một card. Đại từ *tôi* không rò vào hướng dẫn; câu mệnh lệnh không rò vào
lời kể; CTA không kéo độ khẩn cấp hoặc lời hứa vào phần khác. Các câu văn xuôi trong fixture không
khớp pattern lỗi nào nên được giữ nguyên, đúng cổng “card không tự tạo lý do sửa”.

## So sánh protected region

Mỗi vùng được băm trước và sau phép chạy tay; input và output dùng cùng byte đã đóng băng.

| Vùng | SHA-256 trước | SHA-256 sau | Kết quả |
|---|---|---|---|
| Khối code | `703fd61da5b907cf57c6b97473f992bc25c986125d800148fc0d00e0a2a379ae` | `703fd61da5b907cf57c6b97473f992bc25c986125d800148fc0d00e0a2a379ae` | Bằng nhau |
| Bảng tham số | `9a54e64d570fa8f1d6d310396107aa3a10dc5433c5a80440b91f07935bed923b` | `9a54e64d570fa8f1d6d310396107aa3a10dc5433c5a80440b91f07935bed923b` | Bằng nhau |
| Trích dẫn | `f863f9f6019cb87c1f1201838501b8756e5183004dd3d5e229c87c4b591a780a` | `f863f9f6019cb87c1f1201838501b8756e5183004dd3d5e229c87c4b591a780a` | Bằng nhau |

## Gate liên quan

`python3 scripts/validate-package.py` trả về:

```text
Gói vi-humanizer v0.7.1 hợp lệ, gồm 51 pattern
```

Kết luận: MX01 pass 4/4 assertion; protected region giữ nguyên byte và output-only không lộ nhãn
phong cách.
