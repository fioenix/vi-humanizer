# Ca kiểm thử

File này giữ những ca kiểm thử chạy bằng tay để kiểm tra một pattern sau khi thêm hoặc sửa. Mỗi ca gồm đầu vào, kết quả mong đợi và lý do. Repo không có bộ chạy tự động: người bảo trì đưa đầu vào cho skill rồi so kết quả với cột mong đợi.

Ca chống sửa quá tay quan trọng ngang ca phát hiện. Một pattern cắt mất nội dung hợp lệ gây thiệt hại lớn hơn một pattern bỏ sót.

## K6, siêu dữ liệu về quá trình tạo ra văn bản

| # | Đầu vào | Mong đợi | Vì sao |
|---|---|---|---|
| 1 | Báo cáo mở đầu bằng *“Tài liệu này được sinh từ X ngày Y”* | Cắt, chuyển sang commit message | Ghi chú xuất xứ, người đọc báo cáo không cần |
| 2 | Changelog mở đầu bằng *“Bản 2.1 thay thế cách làm cũ”* | Không flag | Tường thuật thay đổi là nội dung của thể loại này |
| 3 | Decision record có mục *“Vì sao chọn phương án B”* | Không flag | Lý do chọn phương án là nội dung chính |
| 4 | Workflow trong vault có mục *“Bốn bước bị cắt và lý do”* | Không flag | Ký ức tổ chức, nói về quyết định chứ không nói về người viết |
| 5 | Workflow trong vault có câu *“Bản đầu tôi viết 15 bước rồi rút còn 8”* | Đổi nhãn hoặc cắt | Cùng chủ đề với ca 4 nhưng nói về người viết |
| 6 | Tài liệu có mục *“Chỗ cần anh quyết”* kèm câu hỏi | Cắt, chuyển sang lượt trả lời trong hội thoại | Tàn dư lượt hội thoại |
| 7 | Artifact HTML có phụ đề tham chiếu tới một artifact khác chưa được đưa cho người đọc | Cắt hoặc viết lại thành câu tự đứng được | Trượt phép thử thứ hai |
| 8 | File vault mở đầu bằng dòng ghi phiên bản, các file cùng thư mục cũng vậy | Không flag | Quy ước thể loại của repo hoặc vault |

Ca 2, 3, 4 và 8 là ca chống sửa quá tay.

## V21, tàn dư lượt hội thoại của trợ lý

| # | Đầu vào | Mong đợi | Vì sao |
|---|---|---|---|
| 1 | Tài liệu mở đầu bằng *“Chắc chắn rồi! Dưới đây là ba bước triển khai”* | Bỏ vỏ, giữ ba bước | Lời chào nói với người đặt yêu cầu |
| 2 | Bài blog kết bằng *“Hy vọng bài viết hữu ích”* | Cắt | Trùng B4, xử lý ở đó cũng được |
| 3 | Email kết bằng *“Chúc anh một ngày tốt lành”* | Không flag | Quy ước thư từ có trước chatbot |
| 4 | Tài liệu hướng dẫn viết prompt, trích *“Bạn có muốn tôi viết tiếp không?”* làm ví dụ | Không flag | Trích dẫn đang được bàn tới |

## V22, rào trước về nguồn rồi đưa phỏng đoán

| # | Đầu vào | Mong đợi | Vì sao |
|---|---|---|---|
| 1 | *“Thông tin về năm thành lập không được công bố. Công ty nhiều khả năng bắt đầu từ đầu những năm 2000.”* | Giữ vế đầu, bỏ vế đoán | Dữ kiện không có nguồn |
| 2 | Báo cáo ghi *“số liệu cập nhật đến 30/06/2026”* | Không flag | Mốc dữ liệu thật |
| 3 | Kịch bản dự báo nhu cầu quý sau, ghi rõ là dự báo | Không flag | Phỏng đoán là nội dung được yêu cầu |
| 4 | Bài nghiên cứu có mục giới hạn nghiên cứu | Không flag | Thể loại yêu cầu nêu giới hạn |
