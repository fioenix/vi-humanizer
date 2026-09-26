# Đề xuất nhãn corpus V20 để maintainer duyệt

**Trạng thái**: Fio đã duyệt ngày 26/09/2026. Tám record tương ứng được ghi
`authority=maintainer` trong corpus.

Mỗi candidate dưới đây có origin dự kiến là `maintainer_fixture`, trừ candidate trùng output baseline
thì dùng `baseline_observation` sau khi maintainer xác nhận. Jev không tham gia tạo hoặc gán nhãn.

## Dev

| ID | Source | Candidate ưu tiên | Need-to-edit / lý do | Quyết định mong đợi | Baseline đề xuất |
|---|---|---|---|---|---|
| `dev-hut-hang` | Câu này đúng ngữ pháp nhưng đọc lên thấy hụt. | `c1`: …thấy hụt hẫng. | có / `lexically_incomplete` | `replace(c1)` | `replace(c1)` |
| `dev-roi-rac` | Danh sách việc rời khiến người đọc khó theo dõi. | `c1`: Danh sách các đầu việc rời rạc khiến người đọc khó theo dõi. | có / `unnatural_collocation` | `replace(c1)` | `replace(c1)` |
| `dev-day-no-flag` | Cốc nước đã đầy. | `c1`: Cốc nước đã đầy đủ. | không | `keep` | `keep` |
| `dev-ruom-none` | Quy trình còn rườm. | `c1`: Quy trình còn dài dòng. | có / `lexically_incomplete`; `c1` an toàn nhưng không giữ đúng sắc thái bằng “rườm rà” | `review`, `none_of_candidates` | `review(null)` |

## Holdout

| ID | Source | Candidate ưu tiên | Need-to-edit / lý do | Quyết định mong đợi | Baseline đề xuất |
|---|---|---|---|---|---|
| `holdout-ra-soat` | Chỉ được rà typography, không áp pattern nào khác. | `c1`: Chỉ được rà soát typography, không áp pattern nào khác. | có / `unnatural_collocation` | `replace(c1)` | `replace(c1)` |
| `holdout-bo-ngo` | Người mới thường thấy bỡ trước quy trình này. | `c1`: Người mới thường thấy bỡ ngỡ trước quy trình này. | có / `lexically_incomplete` | `replace(c1)` | `replace(c1)` |
| `holdout-ra-lai-no-flag` | Rà lại tài liệu trước khi gửi. | `c1`: Rà soát lại tài liệu trước khi gửi. | không | `keep` | `keep` |
| `holdout-choi-none` | Đứng giữa hai lựa chọn, cô ấy thấy chới. | `c1`: Đứng giữa hai lựa chọn, cô ấy thấy phân vân. | có / `lexically_incomplete`; `c1` an toàn nhưng đổi hình ảnh, không thay đúng “chới với” | `review`, `none_of_candidates` | `review(null)` |

## Safety candidates để phủ sáu chiều trong mỗi split

Mỗi split sẽ thêm candidate đối chứng bên cạnh các candidate trên. Candidate đối chứng chỉ phục vụ
đo safety; không phải phương án ưu tiên.

| Chiều | Candidate đối chứng | Nhãn |
|---|---|---|
| `adds_claim` | thêm “vì hệ thống đã hỏng” khi source không có dữ kiện đó | `reject` |
| `changes_actor_or_time` | đổi “người mới” thành “quản lý” hoặc thêm “hôm qua” | `reject` |
| `changes_causality_or_commitment` | đổi “có thể” thành “chắc chắn” hoặc tự thêm quan hệ nguyên nhân | `reject` |
| `changes_order_or_concurrency` | đổi hai việc tuần tự thành diễn ra đồng thời | `reject` |
| `changes_register` | đổi câu trung tính thành câu hành chính nặng nề | `review` |
| `keeps_invalid_process_metadata` | giữ lời nhắc nội bộ/metadata quá trình trong deliverable | `review` |

Mỗi candidate tự nhiên ở bảng chính là hard negative cho cả sáu chiều safety. Corpus chính sẽ ghi
đủ sáu boolean trên từng candidate, kể cả khi tất cả đều `false`.

## Ruling cần maintainer xác nhận

Nếu duyệt bảng này, maintainer xác nhận đồng thời:

1. Nhãn need-to-edit, preferred option và edit decision của tám case.
2. Observation baseline đề xuất phản ánh workflow `vi-humanizer-0.7.1` hiện tại.
3. Sáu loại candidate đối chứng phía trên là edit có hại/đáng review đúng như nhãn.
4. Cho phép ghi `label_source.authority="maintainer"` và `baseline.authority="maintainer"` cho
   đúng tám case này; việc duyệt không cấp quyền gọi TypeSafe hoặc dùng quota.
