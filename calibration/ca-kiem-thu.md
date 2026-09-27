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

## Nhãn và dòng liệt kê rút gọn

| # | Đầu vào | Mong đợi | Vì sao |
|---|---|---|---|
| 1 | Dòng liệt kê *“quyết định bị hoãn mà không ghi”* | *“...bị trì hoãn mà không ghi lại”* | Thiếu bổ ngữ hướng và thiếu tiếng thứ hai, V1 cùng V20 |
| 2 | Dòng liệt kê *“soạn xong rồi dừng”* | Hỏi soạn cái gì, hoặc lấy bổ ngữ có sẵn trong tài liệu | Động từ thiếu bổ ngữ, không tự nghĩ ra đối tượng |
| 3 | Nhãn nút *“Lưu”*, mục lục *“Tổng quan”* | Không flag | Lược đúng phần được phép lược |
| 4 | Ghi chú vận hành *“ca 2 xong, bàn giao ca 3”* | Không flag | Lược chủ ngữ và hư từ, bổ ngữ vẫn đủ |

## Multi-style: ma trận dương và chống rò giọng

Các ca dưới đây kiểm bộ giải phong cách, không kiểm một pattern lỗi. Mỗi cặp giữ cùng một dữ kiện cốt lõi nhưng đổi mục đích hoặc người đọc. Agent phải chọn đúng base profile và một style card; cột cuối ghi thứ không được nhập từ card đối chứng.

| Ca | Context và đầu vào | Route mong đợi | Không được rò sang |
|---|---|---|---|
| MS01 | Bài kể trải nghiệm cho người đọc cá nhân: *“Tôi thử quy trình mới ba lần. Lần thứ ba, thời gian xử lý còn sáu phút.”* | `blog-ca-nhan` + `ke-trai-nghiem`; giữ ngôi *tôi*, diễn biến và nhịp kể đang có | Không biến thành hướng dẫn từng bước hoặc báo cáo KPI |
| MS02 | Báo cáo vận hành dùng đúng dữ kiện: *“Quy trình mới được thử ba lần; lần thứ ba mất sáu phút.”* | `ky-thuat-doanh-nghiep` + `van-hanh-doanh-nghiep` | Không thêm *tôi*, cảm xúc hoặc câu kết trải nghiệm |
| MS03 | Chat giữa hai đồng nghiệp: *“Bản nháp còn hai số chưa đối chiếu. Rà lại giúp mình trước 15 giờ nhé.”* | `blog-ca-nhan` + `phoi-hop-cong-viec`; giữ lời nhờ trực tiếp và xưng hô đã có | Không đổi thành công văn hoặc CTA công khai |
| MS04 | Thông báo công khai cùng dữ kiện: *“Bản nháp còn hai số chưa đối chiếu và sẽ được rà lại trước 15 giờ.”* | `blog-ca-nhan` + `chuyen-mon-cong-khai` | Không tự thêm *mình/nhé* hoặc quan hệ đồng nghiệp |
| MS05 | Bài chuyên môn công khai: *“Cache giảm thời gian phản hồi từ 800 xuống 320 mili giây trong phép thử này. Tôi vẫn chưa coi đó là kết luận cho tải thật.”* | `blog-ca-nhan` + `chuyen-mon-cong-khai`; giữ quan điểm cùng giới hạn bằng chứng | Không làm phẳng thành README hoặc thêm lời bán hàng |
| MS06 | README dùng cùng số liệu: *“Trong phép thử này, cache giảm thời gian phản hồi từ 800 xuống 320 mili giây. Kết quả chưa đại diện cho tải thật.”* | `ky-thuat-doanh-nghiep` + `huong-dan-ky-thuat` | Không thêm ngôi *tôi*, quan điểm cá nhân hoặc hook mạng xã hội |
| MS07 | Trang giới thiệu có CTA sẵn: *“Gói thử nghiệm xử lý tối đa 200 bản ghi. Xem bảng giá để chọn mức phù hợp.”* | `blog-ca-nhan` + `marketing-thuyet-phuc`; giữ CTA có thật và giới hạn cụ thể | Không thêm khẩn cấp, lời hứa hiệu quả hoặc *tốt nhất* |
| MS08 | Tài liệu API cùng giới hạn: *“Gói thử nghiệm xử lý tối đa 200 bản ghi.”* | `ky-thuat-doanh-nghiep` + `huong-dan-ky-thuat` | Không thêm CTA, lợi ích bán hàng hoặc độ khẩn cấp |
| MS09 | Hướng dẫn kỹ thuật: *“Chạy `tool check` trước. Nếu mã thoát khác 0, dừng phát hành.”* | `ky-thuat-doanh-nghiep` + `huong-dan-ky-thuat`; giữ lệnh, điều kiện và thứ tự | Không thêm tiểu từ, trải nghiệm người viết hoặc ngôn ngữ thể chế |
| MS10 | Nhật ký trải nghiệm dùng cùng hành động: *“Tôi chạy `tool check` trước. Mã thoát khác 0 nên tôi dừng phát hành.”* | `blog-ca-nhan` + `ke-trai-nghiem` | Không đổi thành câu mệnh lệnh hoặc bỏ ngôi người kể |
| MS11 | SOP: *“Người trực ca đối chiếu hai bảng trước 15 giờ. Nếu số liệu lệch, ca sau chưa được tiếp nhận.”* | `ky-thuat-doanh-nghiep` + `van-hanh-doanh-nghiep`; giữ vai trò, thời điểm và điều kiện | Không thêm lời nhờ, *mình/nhé* hoặc quan điểm cá nhân |
| MS12 | Chat dùng cùng việc: *“Mình đối chiếu hai bảng trước 15 giờ nhé. Nếu còn lệch thì chưa bàn giao ca sau.”* | `blog-ca-nhan` + `phoi-hop-cong-viec` | Không đổi thành điều khoản SOP hoặc thêm vai trò không có |
| MS13 | Bài nghiên cứu: *“Trong mẫu 120 phiên, thời gian trung vị giảm 18%. Kết quả chưa cho phép suy rộng ngoài nhóm được quan sát.”* | `ky-thuat-doanh-nghiep` + `hoc-thuat-phan-tich`; giữ số liệu và giới hạn suy rộng | Không thêm CTA, lời hứa hay quan điểm cá nhân |
| MS14 | Nội dung giới thiệu dùng cùng số liệu: *“Trong mẫu 120 phiên, thời gian trung vị giảm 18%.”* | `blog-ca-nhan` + `marketing-thuyet-phuc` chỉ khi người dùng xác định đây là nội dung quảng bá | Không tự thêm giới hạn nghiên cứu, trích dẫn giả hoặc lời hứa |

Tất cả 14 ca phải qua năm quy tắc chốt chặn. Route đúng không cho phép sửa một câu vốn không có lỗi; nó chỉ xác định cách giữ giọng nếu một thay đổi khác đã được phép.

## Multi-style: precedence và ambiguity

| Ca | Tín hiệu xung đột | Mong đợi | Vì sao |
|---|---|---|---|
| MSP01 | Yêu cầu hiện tại: *“giữ giọng trung tính, không xưng tôi”*; hồ sơ cũ cho biết người viết thường xưng *tôi* trên blog | Làm theo yêu cầu hiện tại, không dùng *tôi* | Yêu cầu hiện tại thắng bộ nhớ; không xoá hoặc sửa hồ sơ |
| MSP02 | README kỹ thuật có mẫu hiện tại dùng câu ngắn, chủ động; card mặc định chỉ yêu cầu trung tính | Giữ nhịp câu ngắn của mẫu trong giới hạn `huong-dan-ky-thuat` | Mẫu đúng phạm vi thắng mặc định nhưng không đổi base profile |
| MSP03 | Người dùng ghi nhãn *“giọng thân mật”* nhưng mô tả *“không dùng đại từ, không tiểu từ, viết cho hội đồng chuyên môn”* | Làm theo mô tả cụ thể; định tuyến tới `hoc-thuat-phan-tich` nếu nội dung là nghiên cứu | Mô tả cụ thể đáng tin hơn nhãn mơ hồ |
| MSP04 | Trong một mẫu dài, chỉ một câu dùng *nha*, các câu khác không có tiểu từ | Không nâng *nha* thành đặc tính giọng; giữ cách hiện tại ở đoạn cần sửa | Một quan sát có thể là lỗi gõ hoặc ngoại lệ |
| MSP05 | Tin nhắn cần gửi một người nhưng đầu vào không cho biết tuổi, vai vế hay cách xưng hô; đổi *bạn* thành *anh/chị/em* sẽ đổi quan hệ | Hỏi đúng một câu ngắn về cách xưng hô | Đây là ambiguity có hậu quả; không được tự suy vai vế |

Ca MSP01–MSP04 không được tạo câu hỏi cho người dùng. Ca MSP05 phải hỏi; nếu người dùng chưa trả lời thì không tự đổi đại từ.

## Multi-style: tài liệu pha nhiều chức năng

### MX01 — văn xuôi, hướng dẫn, code, bảng, trích dẫn và CTA

**Đầu vào:**

> Tôi từng bỏ qua bước kiểm tra này và chỉ phát hiện lỗi sau khi phát hành.
>
> ## Cách kiểm tra
>
> Chạy `tool check` trước khi hợp nhất. Nếu mã thoát khác 0, dừng phát hành.
>
> ```sh
> tool check --strict
> ```
>
> | Tham số | Bắt buộc | Mặc định |
> |---|---|---|
> | `--strict` | Có | `false` |
>
> > “Không thay đổi câu lệnh trong lúc biên tập.”
>
> Xem bảng giá để chọn mức phù hợp.

**Mong đợi:**

| Phần | Route hoặc cách xử lý |
|---|---|
| Câu mở đầu có người kể | `blog-ca-nhan` + `ke-trai-nghiem` |
| Hai câu hướng dẫn | `ky-thuat-doanh-nghiep` + `huong-dan-ky-thuat` |
| Khối code | `typography-only`; giữ nguyên byte |
| Bảng tham số | `typography-only`; giữ nguyên byte |
| Trích dẫn nguyên văn | `typography-only`; giữ nguyên byte |
| CTA đã có | `blog-ca-nhan` + `marketing-thuyet-phuc`; không thêm độ khẩn cấp hay lời hứa |

**Các phép khẳng định bắt buộc:**

1. Chia theo chức năng và người đọc, không chia theo độ dài hoặc chỉ theo heading.
2. Mỗi phần văn xuôi dùng tối đa một style card; card của câu mở đầu, hướng dẫn và CTA không rò sang nhau.
3. Ba vùng protected giữ đúng từng byte, kể cả backtick, dấu `|`, khoảng trắng và dấu ngoặc kép.
4. Nếu người dùng chỉ yêu cầu viết lại, bản cuối không lộ tên base profile, style card hoặc phân tích định tuyến.
