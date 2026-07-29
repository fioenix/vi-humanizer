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

---

## 2026-07-30 · README của chính repo (tài liệu kỹ thuật)

**Nguồn:** chạy skill lên `README.md` theo yêu cầu của người dùng. Đây là self-application, không phải bản vàng của người thật, nên bằng chứng yếu hơn entry trên.

**Cổng thể loại:** README repo → profile `ky-thuat-doanh-nghiep`, tiểu từ tắt, V13 tắt, V15 và V16 nới, T5 nới mạnh, V19 giữ jargon.

**Bắt được, đều là lỗi thật:**

| Pattern | Chỗ sai | Sửa |
|---|---|---|
| T2 | Em dash chú thích giữa câu: *"phá địa danh và mọi lời thoại — hỏng nội dung"* | Thay bằng *"tức là hỏng nội dung chứ không phải..."* |
| V7 | *"Đừng dùng kết quả của nó như bằng chứng"*, *của* thừa theo khuôn *of* | Bỏ *của nó* |
| V16 | *"Bộ pattern tiếng Việt được xây mới hoàn toàn"* | *"thì xây mới hoàn toàn"* |
| V3 | *"Chép cả cây thư mục vào chỗ harness của bạn tìm skill"*, mệnh đề quan hệ thiếu ranh giới | Viết lại thành *"vào thư mục skill của harness"* |
| T4 | Ba chỗ `, và`: một Oxford comma thật (*"tìm trong lock, không thấy, và báo lỗi"*), hai chỗ comma-and nối mệnh đề kiểu Anh | Thay bằng *nên* và *mà… lại* |

**Cổng thể loại hoạt động đúng, ba lần từ chối sửa:**

- `, và` trong mục Lịch sử phiên bản: changelog nằm trong nhóm thể loại bị chặn. Để nguyên.
- *"một cách nhanh chóng"* và *"Điều quan trọng cần lưu ý là"* trong bảng pattern: đây là ví dụ đang được bàn tới, thuộc ngoại lệ văn bản thứ cấp. Để nguyên.
- Bullet có header và bảng dày đặc: T5 nới mạnh cho README. Để nguyên.

**Phân loại:** cả năm mục đều là **lỗi thật của văn bản**, không phải lỗi guard của skill. Skill bắn đúng, không bắn thừa. Không sửa pattern nào.

**Quan sát đáng ghi:** phần lớn công việc trong lượt này không phải sửa câu mà là vá nội dung đã lệch so với repo (cây thư mục thiếu `calibration/` và `scripts/`, số dòng bảng ghi sai, mục "việc bắt buộc cho v0.2" đã lỗi thời khi repo đang ở 0.2.0). Skill không bắt được loại lỗi này vì nó chỉ soi ngôn ngữ, không đối chiếu văn bản với thực tế. Nếu muốn agent tự bảo trì README, cần một bước kiểm tra riêng: đối chiếu mọi phát biểu về cấu trúc repo với cây thư mục thật. Chưa đủ cơ sở để thành pattern, ghi lại để theo dõi.
