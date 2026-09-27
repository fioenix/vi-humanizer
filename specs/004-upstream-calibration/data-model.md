# Data model: Hiệu chuẩn khoảng trống upstream

## CalibrationHypothesis

| Field | Constraint |
|---|---|
| `id` | Một trong `ARG`, `QUAL`, `REL`, `AUTH` |
| `name` | Tên hiện tượng tiếng Việt, không dùng label tiếng Anh làm rule |
| `upstream_origin` | Pattern upstream làm prior art |
| `risk` | False positive chính cần chặn |
| `related_patterns` | Pattern hiện có có thể mở rộng hoặc cần phân vai |
| `decision` | `extend-existing`, `new-pattern`, `defer` |
| `owner` | `V`, `B`, `K` hoặc cặp profile đã phân vai |
| `rationale` | Lý do truy được về case và constitution |

## CalibrationCase

| Field | Constraint |
|---|---|
| `case_id` | `<hypothesis>-P01..P03` hoặc `<hypothesis>-N01..N03` |
| `context` | Thể loại, người đọc, nguồn trong phạm vi và ý định cần biết |
| `input` | Tiếng Việt tự nhiên, public, không dữ liệu cá nhân/tổ chức |
| `expected` | `flag` hoặc `keep` |
| `edit_boundary` | Cụm/câu được phép sửa hoặc `none` |
| `rationale` | Vì sao rule áp dụng hoặc **Không flag** chặn |
| `provenance` | `maintainer-fixture` hoặc nguồn public đã ghi |

Validation:

- Mỗi hypothesis có đúng ba case `flag` và ba case `keep` trong slice này.
- Case không dùng tần suất để kết luận.
- Case `flag` phải có sửa tối thiểu giữ nghĩa; case `keep` không được nhận edit.

## PlacementDecision

| Field | Constraint |
|---|---|
| `hypothesis_id` | Tham chiếu CalibrationHypothesis |
| `scope_test` | Có phụ thuộc thể loại/người đọc/mục đích không |
| `coverage_test` | Pattern hiện có đã ngụ ý lỗi chưa |
| `owner` | V/B/K hợp constitution |
| `pattern_id` | ID hiện có/mới hoặc `none` khi defer |
| `cross_reference` | Bắt buộc nếu hai pattern chạm nhau |
| `evidence_cases` | Toàn bộ case của giả thuyết |

## PatternRevision

| Field | Constraint |
|---|---|
| `pattern_id` | Liên tục trong prefix owner |
| `signal` | Có thể gọi tên, không phải cảm giác “giống AI” |
| `why` | Giải thích lỗi tiếng Việt |
| `fix` | Không thêm dữ kiện hoặc nâng mức chắc chắn |
| `do_not_flag` | Bao phủ mọi negative boundary trong calibration |
| `readme_entry` | Đồng bộ inventory cùng commit |
| `version` | Đồng bộ ba nguồn version |

## State transitions

```text
hypothesis
  -> cases_labeled
  -> placement_reviewed
  -> accepted | deferred
  -> pattern_red
  -> pattern_green
  -> packaged
  -> installed_verified
```

Không được đi từ `hypothesis` thẳng tới `pattern_green`.
