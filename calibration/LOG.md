# Log hiệu chuẩn

Bộ nhớ bằng chứng của skill. Mỗi quan sát một entry, ghi trước khi sửa skill. Giao thức đầy đủ ở `AGENTS.md`, mục "Nâng cấp từ sử dụng thật".

---

## 2026-07-30 · báo cáo doanh nghiệp (kho vận)

**Nguồn:** bản vàng do Fioenix (người bản ngữ, chủ repo) viết lại output của skill.

**Đoạn skill xuất ra:**
> Đội kỹ thuật đã triển khai hệ thống quản lý kho mới để vận hành gọn hơn. Dữ liệu tồn kho đồng bộ nhanh, các cửa hàng xem được thông tin theo thời gian thực. Riêng độ trễ thì đội vẫn chưa giải quyết được.

**Bản vàng:**
> Nhằm mục đích nâng cao hiệu quả vận hành kho, team dev đã triển khai hệ thống quản lý kho mới. Dữ liệu tồn kho đồng bộ nhanh hơn, các cửa hàng xem được thông tin tồn kho theo thời gian thực. Riêng độ trễ của hệ thống thì team dev vẫn chưa giải quyết được.

**Khác biệt gọi tên được:**

| # | Khác biệt | Phân loại | Quyết định |
|---|---|---|---|
| 1 | "đội kỹ thuật" ↔ "team dev": register công việc IT dùng jargon, skill lại xuất tiếng Việt dịch sạch | Lỗi guard (V19 thiếu chiều sửa chủ động) | Sửa ở v0.1.1: V19 thêm chiều trả thuật ngữ bị dịch sạch về jargon |
| 2 | "vận hành gọn hơn" ↔ "nâng cao hiệu quả vận hành kho": skill hạ giọng quá tay, kéo báo cáo xuống văn nói | Lỗi guard (thiếu quy tắc thanh ngữ vực ở tầng chặn) | Sửa ở v0.1.1: thêm quy tắc chặn thứ tư + nới K2 cho cụm có bổ ngữ cụ thể |
| 3 | Giữ "Nhằm mục đích..." mở câu: skill coi là filler V9, người viết báo cáo thật dùng bình thường khi cụm có nội dung | Lỗi guard (V9 quá gắt với văn doanh nghiệp) | Sửa ở v0.1.1: nới guard V9 |
| 4 | Lặp "tồn kho", lặp "team dev" nguyên cụm qua các câu | Khớp quy tắc đảo chiều có sẵn, output của skill né lặp là sai hướng | Bổ sung ví dụ vào lệnh cấm số 3 của profile kỹ thuật ở v0.1.1 |
| 5 | "độ trễ" ↔ "độ trễ của hệ thống": bản vàng thêm định ngữ cho rõ | Sở thích cá nhân (cả hai đều tự nhiên) | Không sửa skill |

**Ghi chú:** n=1 nhưng người sửa là chủ repo và cả bốn lỗi guard đều gọi tên được, nên đủ ngưỡng theo giao thức. Đây cũng là entry mẫu cho định dạng log.
