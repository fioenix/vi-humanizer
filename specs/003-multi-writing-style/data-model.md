# Data Model: Bộ giải nhiều phong cách viết

Đây là model khái niệm cho instruction Markdown, không phải schema runtime hay API.

## 1. Style Context

| Field | Bắt buộc | Validation |
|---|---:|---|
| `purpose` | Có | Một mục đích giao tiếp cụ thể của phần văn bản |
| `audience` | Có | Nhóm người đọc có thể mô tả được; không tự điền danh tính |
| `relationship` | Có điều kiện | Chỉ dùng khi có bằng chứng về vai vế/thân sơ; thiếu mà ảnh hưởng đại từ thì hỏi |
| `register` | Có | Mức trang trọng đang có hoặc được yêu cầu; không suy từ một từ đơn lẻ |
| `channel` | Có | Kênh sử dụng như chat, bài công khai, tài liệu tra cứu, SOP, bài học thuật |
| `genre` | Có | Dùng để chọn cổng typography-only hoặc base profile |
| `voice_evidence` | Không | Mẫu hiện tại/hồ sơ đúng người, đúng phạm vi; cần nhiều dấu hiệu ổn định |
| `protected_regions` | Có | Code, schema, bảng dữ liệu, trích dẫn hoặc vùng chỉ typography |

## 2. Base Profile

| Giá trị | Phạm vi | Sở hữu |
|---|---|---|
| `blog-ca-nhan` | Văn bản có tác giả hiện diện, chat công việc, bài công khai, marketing | B1–B17 và giới hạn giữ giọng |
| `ky-thuat-doanh-nghiep` | README, API prose, SOP, báo cáo, giáo trình, học thuật | K1–K6 và giới hạn trung tính/thuật ngữ |
| `typography-only` | Pháp quy, hợp đồng, nghi lễ, thơ có nhịp, code/schema/data, trích dẫn | Chỉ phạm vi typography hiện được phép; không chọn style card |

## 3. Style Card

Mỗi card có đúng các field khái niệm sau:

| Field | Validation |
|---|---|
| `card_id` | Một slug ổn định, xuất hiện đúng một lần trong registry |
| `name` | Tên tiếng Việt mô tả mục đích, không phải phán xét “hay/dở” |
| `compatible_profile` | Một base profile |
| `audience_and_purpose` | Nêu người đọc và việc văn bản cần giúp họ làm |
| `register` | Mức trang trọng và biên độ được phép |
| `address` | Quy tắc giữ/chọn xưng hô; không tự suy vai vế |
| `rhythm` | Nhịp câu cần giữ, không đặt ngưỡng cứng |
| `terminology` | Cách xử lý Hán-Việt, tiếng Anh và thuật ngữ ngành |
| `ending` | Cách kết hợp lệ với mục đích |
| `never_add` | Dữ kiện, lời hứa, khẩn cấp, quan hệ hoặc thái độ không có trong đầu vào |
| `positive_case_ref` | Trỏ tới ca dương trong calibration |
| `leakage_case_ref` | Trỏ tới ca chống rò giọng |

Canonical cards:

1. `ke-trai-nghiem`
2. `phoi-hop-cong-viec`
3. `chuyen-mon-cong-khai`
4. `marketing-thuyet-phuc`
5. `huong-dan-ky-thuat`
6. `van-hanh-doanh-nghiep`
7. `hoc-thuat-phan-tich`

## 4. Style Brief

| Field | Validation |
|---|---|
| `segment_scope` | Một phần có chức năng thống nhất; không nhỏ tới từng câu nếu không cần |
| `base_profile` | Đúng một giá trị |
| `style_card` | Không hoặc đúng một card tương thích |
| `current_request_overrides` | Chỉ những yêu cầu cụ thể, không ghi label mơ hồ thay mô tả |
| `voice_overrides` | Chỉ đặc tính ổn định, đúng người và đúng phạm vi |
| `preserve_constraints` | Năm chốt chặn, thuật ngữ, protected region, facts/meaning |
| `confidence_state` | `resolved`, `preserve-current`, hoặc `ask-one-question` |

## 5. Style Calibration Pair

| Field | Validation |
|---|---|
| `case_id` | Slug ổn định |
| `content_invariant` | Dữ kiện và intent phải giống ca đối chứng |
| `expected_profile` | Nhãn base profile |
| `expected_card` | Nhãn card hoặc null cho protected region |
| `positive_signals` | Những tín hiệu đủ để chọn card |
| `must_not_import` | Đại từ, nhịp, thuật ngữ, CTA hoặc register của card đối chứng |
| `label_authority` | Fixture trung tính được maintainer/owner-authorized agent review |
| `provenance` | Public/neutral only |

## Relationships and transitions

```text
raw document
  -> protected-region split
  -> functional segments
  -> Style Context per segment
  -> Base Profile
  -> compatible Style Card (0..1)
  -> precedence resolution
  -> Style Brief
  -> existing V/B/K/T edit workflow
  -> five-guard validation
  -> final text
```

- `typography-only` kết thúc route trước style card.
- `ask-one-question` chỉ xuất hiện khi ambiguity có thể đổi quan hệ; sau câu trả lời quay lại `resolved`.
- Không có transition từ style card sang việc thêm pattern hoặc tự sinh dữ kiện.
