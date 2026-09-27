# Bằng chứng US2: precedence và ambiguity

**Ngày chạy**: 2026-09-28
**Phạm vi**: MSP01–MSP05 trong `calibration/ca-kiem-thu.md`
**Cách chạy**: đối chiếu thủ công từng input với thứ tự ưu tiên và ba trạng thái giải trong
`references/bo-giai-phong-cach.md`, rồi kiểm tra lại consumer trong `SKILL.md`.

| Ca | Kết quả quan sát | Trạng thái | Pass |
|---|---|---|---|
| MSP01 | Yêu cầu hiện tại giữ giọng trung tính và không xưng *tôi* thắng hồ sơ cũ | Đã giải | Có |
| MSP02 | Mẫu README hiện tại giữ nhịp câu ngắn trong giới hạn card kỹ thuật | Đã giải | Có |
| MSP03 | Mô tả không đại từ, không tiểu từ và viết cho hội đồng chuyên môn thắng nhãn *thân mật* | Đã giải | Có |
| MSP04 | Một lần xuất hiện *nha* không được nâng thành thói quen | Giữ cách hiện tại | Có |
| MSP05 | Thiếu vai vế làm thay đổi đại từ nên resolver hỏi đúng một câu và không tự đổi | Cần hỏi một câu | Có |

## Kết luận

- 5/5 ca áp đúng precedence.
- MSP01–MSP04 không tạo câu hỏi thừa.
- MSP05 tạo đúng một câu hỏi về xưng hô; không đưa bảng tone và không tự suy vai vế.
- Không ca nào cho phép style card hoặc memory vượt qua protected region và năm quy tắc chốt chặn.
