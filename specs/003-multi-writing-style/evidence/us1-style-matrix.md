# US1 evidence: ma trận bảy phong cách

**Ngày chạy:** 2026-09-28
**Nguồn:** 14 fixture trung tính MS01–MS14 trong `calibration/ca-kiem-thu.md`
**Phương pháp:** đối chiếu route table trong `SKILL.md`, card contract và từng mục **Không tự thêm**; không gọi external evaluator.

## Structural check

One-off checker đọc file thật và xác nhận:

- 7 canonical card, đúng thứ tự;
- 14 case ID duy nhất;
- mỗi card trỏ tới ít nhất một ca dương và một ca đối chứng;
- mọi case reference đều tồn tại.

Output: `structural style matrix: PASS`.

## Semantic review

| Case | Expected brief | Facts/intent | Leakage guard | Result |
|---|---|---|---|---|
| MS01 | `blog-ca-nhan` + `ke-trai-nghiem` | Giữ ba lần thử và sáu phút | Không biến thành procedure/KPI | PASS |
| MS02 | `ky-thuat-doanh-nghiep` + `van-hanh-doanh-nghiep` | Giữ cùng số lần và thời gian | Không thêm ngôi kể/cảm xúc | PASS |
| MS03 | `blog-ca-nhan` + `phoi-hop-cong-viec` | Giữ hai số, 15 giờ và lời nhờ | Không công văn hóa | PASS |
| MS04 | `blog-ca-nhan` + `chuyen-mon-cong-khai` | Giữ hai số và 15 giờ | Không thêm quan hệ đồng nghiệp | PASS |
| MS05 | `blog-ca-nhan` + `chuyen-mon-cong-khai` | Giữ 800/320 ms và giới hạn tải thật | Không README hóa/bán hàng | PASS |
| MS06 | `ky-thuat-doanh-nghiep` + `huong-dan-ky-thuat` | Giữ cùng số liệu và giới hạn | Không thêm ngôi tác giả/hook | PASS |
| MS07 | `blog-ca-nhan` + `marketing-thuyet-phuc` | Giữ 200 bản ghi và CTA có sẵn | Không thêm khẩn cấp/lời hứa | PASS |
| MS08 | `ky-thuat-doanh-nghiep` + `huong-dan-ky-thuat` | Giữ giới hạn 200 bản ghi | Không thêm CTA/lợi ích | PASS |
| MS09 | `ky-thuat-doanh-nghiep` + `huong-dan-ky-thuat` | Giữ command, exit code và thứ tự | Không thêm tiểu từ/trải nghiệm | PASS |
| MS10 | `blog-ca-nhan` + `ke-trai-nghiem` | Giữ command, exit code và hành động đã làm | Không đổi thành mệnh lệnh | PASS |
| MS11 | `ky-thuat-doanh-nghiep` + `van-hanh-doanh-nghiep` | Giữ vai trò, 15 giờ và điều kiện bàn giao | Không thêm lời nhờ/xưng hô | PASS |
| MS12 | `blog-ca-nhan` + `phoi-hop-cong-viec` | Giữ cùng việc và điều kiện | Không biến thành điều khoản | PASS |
| MS13 | `ky-thuat-doanh-nghiep` + `hoc-thuat-phan-tich` | Giữ 120 phiên, 18% và giới hạn suy rộng | Không CTA/lời hứa | PASS |
| MS14 | `blog-ca-nhan` + `marketing-thuyet-phuc` khi context xác nhận | Giữ 120 phiên và 18% | Không trích dẫn/hedge/lời hứa giả | PASS |

## Outcome

- Route accuracy theo nhãn: 14/14.
- Facts/intent preserved: 14/14.
- Cross-style leakage: 0/14.
- Style-only edit without named pattern/request: 0/14; route không tự tạo lý do sửa.
