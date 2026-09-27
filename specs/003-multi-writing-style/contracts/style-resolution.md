# Contract: Giải phong cách trước khi biên tập

## Input contract

Resolver chỉ được dùng những gì có trong yêu cầu hiện tại, văn bản/mẫu người dùng giao, profile đúng thể loại và hồ sơ đúng người nếu runtime cung cấp hợp lệ. Nó không tìm kiếm thông tin ngoài, không gọi external model và không dùng labels/evidence của feature 002.

## Fixed order

```text
split protected regions
  -> group remaining prose by function
  -> determine base profile
  -> collect five context dimensions
  -> select 0..1 compatible style card
  -> apply precedence
  -> edit with existing patterns
  -> run five guards
```

## Precedence contract

1. Yêu cầu hiện tại và mô tả cụ thể của người dùng.
2. Ràng buộc thể loại, protected region và năm quy tắc chốt chặn.
3. Mẫu trong lượt hiện tại hoặc hồ sơ đúng người/đúng phạm vi có bằng chứng ổn định.
4. Style card được chọn.
5. Mặc định của base profile.

Nếu label tone mâu thuẫn với mô tả cụ thể, mô tả thắng. Nếu yêu cầu hiện tại đòi thêm dữ kiện, đổi nghĩa hoặc phá protected region, guard thắng và agent phải nêu ranh giới thay vì âm thầm làm.

## Selection contract

- Mỗi segment có đúng một base profile.
- Mỗi segment có không quá một style card.
- Card phải tương thích base profile.
- `typography-only` không có style card.
- Không có fallback “làm tự nhiên hơn” chung chung. Thiếu bằng chứng nhỏ thì giữ cách đang có; thiếu bằng chứng làm đổi quan hệ thì hỏi một câu.

## Card contract

Mỗi card phải có: người đọc/mục đích, register, xưng hô, nhịp, thuật ngữ, cách kết, `never_add`, ca dương và ca chống rò giọng. Card không được chứa danh sách từ bị cấm toàn cục và không được đánh số như pattern V/T/B/K.

## Mixed-document contract

- Segment theo chức năng, không theo độ dài tùy ý.
- Cùng chức năng và cùng người đọc nên dùng chung brief.
- Chỗ chuyển người nói trong trích dẫn/hội thoại không làm thay đổi giọng của narrator.
- Code, schema, bảng dữ liệu và trích dẫn giữ nguyên theo cổng hiện tại.

## Output contract

- Yêu cầu viết lại: chỉ trả bản cuối.
- Yêu cầu rà/giải thích/so sánh: có thể nêu base profile, card và bằng chứng chọn ở mức ngắn gọn.
- Khi sửa file: báo phần đã sửa, không dán lại toàn file.
- Style label không được xuất hiện trong deliverable trừ khi người dùng yêu cầu.

## Failure contract

| Condition | Required behavior |
|---|---|
| Không đủ tín hiệu nhưng khác biệt nhỏ | Giữ phong cách hiện tại |
| Thiếu quan hệ làm đổi đại từ/register | Hỏi đúng một câu ngắn |
| Mẫu và profile xung đột | Giữ ràng buộc thể loại, dùng phần mẫu không xung đột |
| Memory sai người hoặc sai kênh | Không dùng |
| Card muốn thêm claim/CTA/khẩn cấp | Bỏ thay đổi ở five-guard pass |
| Tài liệu pha chức năng | Tách segment và resolve riêng |
| External evaluator không có | Không ảnh hưởng; feature không phụ thuộc evaluator |
