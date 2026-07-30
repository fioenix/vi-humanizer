# Profile: tài liệu kỹ thuật, doanh nghiệp, học thuật

Nạp cùng `SKILL.md` khi cổng thể loại xác định văn bản là README, SOP nội bộ, đặc tả, tài liệu doanh nghiệp, giáo trình, đề án môn học, hoặc nghiên cứu khoa học.

Nguyên tắc chi phối cả profile này: **văn trung tính và phẳng chính là giọng người đúng ở đây.** Phần lớn nội dung dưới đây là lệnh cấm và điều chỉnh ngưỡng, không phải pattern mới. Chỉ có bốn pattern riêng.

---

## Cấm tuyệt đối

Bốn điều dưới đây không có ngoại lệ. Vi phạm chúng gây hại nhiều hơn toàn bộ lợi ích mà skill mang lại.

1. **Không chèn tiểu từ tình thái.** Không bao giờ thêm *nhé, ạ, đấy, cơ, chứ, thôi* vào quyết định, hợp đồng, báo cáo tài chính, tài liệu kỹ thuật, giáo trình hay bài nghiên cứu. Ở những thể loại này việc **không có** tiểu từ là chuẩn thể loại, không phải lỗi. Pattern B14 của profile kia bị vô hiệu hoàn toàn ở đây.

2. **Không thêm giọng, ý kiến, ngôi thứ nhất.** Mục "Giọng và cá tính" của profile kia không áp dụng. Không thêm thái độ, không thêm chỗ chưa chắc chắn, không thêm câu chen ngang.

3. **Không tạo chuỗi đồng nghĩa cho thuật ngữ.** Thuật ngữ phải lặp lại y nguyên xuyên suốt văn bản. Đây là yêu cầu nghề nghiệp, không phải lựa chọn văn phong. Quy tắc đảo chiều trong `SKILL.md` áp dụng ở đây mạnh hơn: lặp thuật ngữ là **bắt buộc**, kể cả lặp nguyên cụm dài (*team dev*, *tồn kho*) qua nhiều câu liên tiếp.

4. **Không thuần Việt hoá thuật ngữ Hán-Việt.** Xem `references/han-viet-thuan-viet.md`, cột thứ ba. Hầu như toàn bộ hệ thuật ngữ khoa học tiếng Việt là Hán-Việt, mà chuẩn hoá chúng là việc của giới chuyên môn chứ không phải của người biên tập văn phong. Ví dụ chí mạng: Bộ luật Dân sự phân biệt *chiếm hữu*, *sử dụng*, *định đoạt* thành ba quyền năng riêng biệt; gộp về thuần Việt là làm sai nghĩa pháp lý.

## Điều chỉnh ngưỡng lõi

| Pattern lõi | Điều chỉnh |
|---|---|
| V4 dấu thời – thể | Nới. Văn mô tả trạng thái phi thời gian (định nghĩa, thông số, mô tả chức năng) vốn không có dấu thời thể. Không bổ sung |
| V8 *các* và *những* | Nới với văn bản liệt kê đối tượng áp dụng, nơi *các* đánh dấu phạm vi bắt buộc phải rõ |
| V13 khung SVO | **Tắt.** Trật tự cố định trong mô tả thuật toán, điều khoản và tài liệu API là cố ý để tránh mơ hồ |
| V14 danh ngữ trần | Nới **theo vị trí, không theo tài liệu**. Nhãn, mục lục, ô bảng, checklist, gạch đầu dòng đều dùng danh ngữ trần hợp lệ, còn văn xuôi thì vẫn áp V14 như thường. Loại trừ tường minh: câu mở đầu tài liệu và câu mở đầu mục không được là danh ngữ trần, vì đó chính là chỗ người đọc cần một câu trọn vẹn nhất |
| V15 danh hoá | Nới. *tiến hành thanh tra*, *thực hiện nghĩa vụ thuế*, *công tác văn thư* là thuật ngữ đúng chuẩn. Chỉ cắt khi có chồng hai động từ rỗng (*tiến hành thực hiện*) |
| V16 bị động | Nới. *"Quyết định được ban hành ngày..."*, *"Hồ sơ được nộp theo quy định tại Điều 5"* là chuẩn văn phong hành chính. Vẫn cắt `được ... bởi` vì tác nhân nêu bằng *bởi* không thuộc quy ước nào |
| V18 câu nhiều tầng | Nới với hợp đồng và điều khoản, nơi câu dài nhiều mệnh đề xác định phạm vi điều chỉnh. Vẫn áp với README và tài liệu hướng dẫn |
| V19 chêm tiếng Anh | **Đảo chiều theo register.** Xem bảng dưới |
| T5 markdown | Nới mạnh. Bullet có header là định dạng đúng ở README, changelog, đặc tả, SOP |

**V19 trong profile này chia hai nhánh:**

| Register | Chêm tiếng Anh |
|---|---|
| README, SOP nội bộ, tài liệu doanh nghiệp, tài liệu kỹ thuật | Chuẩn mực. Giữ nguyên jargon: deploy, cloud, endpoint, benchmark, deadline. **Vắng hẳn mới là tell** |
| Giáo trình, đề án môn học, nghiên cứu khoa học | **Chêm là lỗi register.** Chỉ giữ thuật ngữ chưa có tương đương tiếng Việt, rồi chú giải ở lần xuất hiện đầu. Người Việt viết luận văn không viết *"deploy lên prod"* |

## Pattern riêng của profile này

### K1. Viết theo diff thay vì mô tả hiện trạng

**Dấu hiệu:** tài liệu hoặc chú thích viết như đang tường thuật một thay đổi thay vì mô tả sự vật như nó đang là. *"Hàm này được thêm vào để thay thế cách làm cũ"*, *"Trước đây hệ thống dùng X, giờ đã chuyển sang Y"*, *"Đã cập nhật để hỗ trợ..."*
**Vì sao:** trừ khi tài liệu vốn gắn với phiên bản, nó phải đọc được mà không cần biết commit gần nhất đã đổi gì. Model viết kiểu này vì nó đang phản ứng với yêu cầu thay đổi chứ không mô tả kết quả.
**Sửa:** *"Hàm này được thêm vào để thay thế cách lặp qua toàn bộ danh sách, vốn gây chậm O(n²)."* → *"Hàm này dùng bảng băm để tra cứu O(1), tránh chi phí O(n²) của cách lặp tuần tự."*
**Không flag:** changelog, release note, tài liệu hướng dẫn nâng cấp, biên bản họp, báo cáo tiến độ. Ở đó tường thuật thay đổi chính là nội dung.

### K2. Sáo ngữ thể chế rỗng ngoài văn bản pháp quy

**Dấu hiệu:** *đóng vai trò quan trọng, có ý nghĩa hết sức quan trọng, là yếu tố then chốt, góp phần nâng cao, đẩy mạnh, tăng cường, nhằm đáp ứng yêu cầu ngày càng cao* xuất hiện trong báo cáo doanh nghiệp, tài liệu kỹ thuật hoặc bài nghiên cứu.
**Vì sao:** đây là ngôn ngữ thể chế hợp lệ **trong** nghị quyết và văn bản chỉ đạo, nhưng khi model mang nó sang báo cáo nội bộ hay bài nghiên cứu thì nó chỉ còn là lớp đệm rỗng. Phân biệt bằng thể loại, không bằng bản thân cụm từ.
**Sửa:** thay bằng phát biểu kiểm chứng được có trong bản gốc, hoặc cắt.
**Không flag:** cụm có bổ ngữ cụ thể mang thông tin thật thì giữ: *"nâng cao hiệu quả vận hành kho"* nói rõ nâng cao cái gì, đó là tiếng Việt công sở bình thường; chỉ cắt khi cụm đứng trơ (*"nâng cao hiệu quả"* mà không nói hiệu quả của cái gì). Văn bản pháp quy, nghị quyết, kế hoạch ngành thì cổng thể loại đã chặn từ trước. Trích dẫn nguyên văn.

### K3. Bộ đề mục Hán-Việt đối xứng rỗng

**Dấu hiệu:** heading là danh ngữ Hán-Việt hai âm tiết xếp thành bộ cân đối: *Tổng quan / Hiện trạng / Giải pháp / Kết luận*, hoặc *Thách thức và cơ hội*, *Khó khăn và giải pháp*. Bộ heading cân đối đến mức đối xứng là dấu vết khuôn.
**Vì sao:** model dựng bố cục theo mẫu trước rồi mới nhét nội dung vào, nên đề mục phản ánh khuôn chứ không phản ánh nội dung thật của từng phần.
**Sửa:** đặt lại đề mục theo nội dung thật của phần đó. Nếu một mục không có nội dung riêng thì gộp vào mục khác.
**Không flag:** tài liệu theo mẫu bắt buộc (đề cương nghiên cứu theo quy định của trường, báo cáo theo biểu mẫu ngành, hồ sơ thầu). Luận văn có cấu trúc chương quy định sẵn.

### K4. Mô tả hiện tượng mà không đưa hiện tượng ra

**Dấu hiệu:** đoạn giải thích một lỗi, một cơ chế hoặc một khái niệm bằng toàn danh từ trừu tượng, không có lấy một instance. Dấu hiệu phụ đi kèm: thuật ngữ chuyên ngành xuất hiện lần đầu mà không có ví dụ đứng cạnh; câu định nghĩa dài với bổ ngữ bị đẩy ra sau chuỗi liệt kê; người đọc phải đọc hai lần mới nắm. Test nhanh: đếm số danh từ cụ thể có thể trỏ tay vào được trong đoạn. Bằng không thì đoạn đó đang mô tả thay vì cho thấy.
**Vì sao:** đây là cách "trung tính" trượt thành "vô hồn". Profile này yêu cầu văn phẳng, và người viết dễ đọc thành giấy phép cho văn trừu tượng. Hai thứ khác nhau: trung tính nói về **giọng**, trừu tượng nói về **độ cụ thể**. Một đoạn hoàn toàn có thể vừa trung tính vừa đầy ví dụ, và đó mới là tài liệu kỹ thuật tốt.
**Sửa:** kéo một instance có sẵn lên tuyến đầu. Ưu tiên ví dụ **đã tồn tại ở nơi khác trong cùng tài liệu hoặc cùng repo** (bảng tra, test case, changelog, phần phụ lục) chứ không sáng tác. Đặt instance **trước** phần giải thích, rồi mới đặt tên cho hiện tượng. Phép định nghĩa trỏ vật hiệu quả hơn phép định nghĩa bằng thuộc tính, nhất là khi người đọc chưa biết thuật ngữ.
**Không flag:** tài liệu tham chiếu thuần tra cứu (bảng, danh mục tham số, mã lỗi), nơi ví dụ nằm ở tài liệu khác và người đọc đã biết khái niệm. Phần tóm tắt điều hành. Văn bản mà instance nằm ngay ở đoạn liền sau.

### K5. Câu dẫn nhập rỗng sau đề mục

**Dấu hiệu:** một đề mục, rồi một câu ngắn chỉ nhắc lại chính đề mục đó, rồi mới tới nội dung thật. *"## Hiệu năng"* rồi *"Hiệu năng là một vấn đề quan trọng."*
**Vì sao:** model thêm một câu khởi động sau mỗi heading vì nó học rằng đoạn văn cần câu chủ đề. Câu đó không mang thông tin và làm văn bản có cảm giác độn.
**Sửa:** xoá câu dẫn, để đề mục làm việc của nó.
**Không flag:** câu sau đề mục nêu phạm vi, điều kiện áp dụng, hoặc cảnh báo thật. Tài liệu tham chiếu có quy ước một câu tóm tắt dưới mỗi mục.

---

## Về nhịp câu

Không áp B13 của profile kia. Trong quy trình SOP, mô tả API, danh mục điều khoản và tài liệu kỹ thuật, **nhịp câu đều là yêu cầu**, không phải lỗi. Câu đều giúp người đọc quét nhanh và so sánh các mục với nhau.
