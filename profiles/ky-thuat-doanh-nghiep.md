# Profile cho tài liệu kỹ thuật, doanh nghiệp và học thuật

Đọc file này sau `SKILL.md` khi văn bản là README, SOP nội bộ, đặc tả, tài liệu doanh nghiệp, giáo trình, đề án môn học hoặc nghiên cứu khoa học.

Với những thể loại này, giọng trung tính thường là lựa chọn đúng. Mục tiêu là làm câu rõ nghĩa và đúng thuật ngữ, không thêm cá tính hoặc sự thân mật. File này gồm các giới hạn bắt buộc, cách áp V1–V20 và năm pattern riêng K1–K5.

---

## Những giới hạn bắt buộc

Bốn điều dưới đây giữ cho bản sửa không làm sai thể loại hoặc thuật ngữ.

1. **Không chèn tiểu từ tình thái.** Không thêm *nhé, ạ, đấy, cơ, chứ, thôi* vào quyết định, hợp đồng, báo cáo tài chính, tài liệu kỹ thuật, giáo trình hoặc bài nghiên cứu. Ở đây, việc không dùng tiểu từ là phù hợp với thể loại. Không áp B14.

2. **Không thêm giọng, ý kiến, ngôi thứ nhất.** Mục "Giọng và cá tính" của profile kia không áp dụng. Không thêm thái độ, không thêm chỗ chưa chắc chắn, không thêm câu chen ngang.

3. **Không thay thuật ngữ chỉ để tránh lặp.** Một thuật ngữ phải được gọi nhất quán trong cùng tài liệu. Có thể lặp nguyên cụm như *team dev* hoặc *tồn kho* qua nhiều câu nếu chúng vẫn chỉ cùng một đối tượng.

4. **Không thuần Việt hoá thuật ngữ Hán-Việt.** Xem cột thứ ba trong `references/han-viet-thuan-viet.md`. Nhiều thuật ngữ khoa học, hành chính và pháp lý là từ Hán-Việt đã được định nghĩa. Chẳng hạn Bộ luật Dân sự phân biệt *chiếm hữu*, *sử dụng* và *định đoạt*; thay bằng từ đời thường có thể làm mất nghĩa pháp lý.

## Cách áp V1–V20 và T1–T6

| Pattern | Cách áp dụng trong profile này |
|---|---|
| V4, từ chỉ thời gian và trạng thái | Định nghĩa, thông số và mô tả chức năng có thể không cần dấu thời gian. Chỉ thêm khi văn bản đang kể một diễn biến mà thứ tự hoặc trạng thái bị thiếu. |
| V8, *các* và *những* | Giữ *các* khi nó xác định rõ toàn bộ nhóm đối tượng áp dụng trong quy định hoặc danh mục. |
| V13, kiểu mở câu lặp lại | Giữ cấu trúc song song trong thuật toán, điều khoản, bảng tham số và tài liệu API nếu nó giúp so sánh. Trong văn xuôi, vẫn sửa khi nhiều câu liên tiếp lặp khuôn mà không có lý do. |
| V14, danh ngữ đứng riêng | Nhãn, mục lục, ô bảng, checklist và gạch đầu dòng có thể là danh ngữ. Câu mở đầu tài liệu hoặc đoạn văn xuôi vẫn cần một cấu trúc hoàn chỉnh. |
| V15, danh hoá | Giữ các thuật ngữ như *tiến hành thanh tra, thực hiện nghĩa vụ thuế, công tác văn thư*. Sửa cụm chồng động từ ít nội dung như *tiến hành thực hiện*. |
| V16, bị động | Giữ cách viết như *“Quyết định được ban hành ngày...”* hoặc *“Hồ sơ được nộp theo quy định tại Điều 5”* khi trọng tâm là quyết định hoặc hồ sơ. Chỉ đổi chủ thể khi tác nhân đã rõ và câu chủ động dễ hiểu hơn. |
| V18, câu nhiều tầng | Hợp đồng và điều khoản có thể cần một câu dài để xác định phạm vi. Với README và hướng dẫn, ưu tiên tách câu nếu quan hệ vẫn giữ nguyên. |
| V19, tiếng Anh trong câu | Chọn theo người đọc và lĩnh vực, như bảng dưới. |
| T5, định dạng | Heading, nhãn ở đầu bullet và dấu hai chấm đều hợp lệ khi chúng thể hiện cấu trúc thật của README, changelog, đặc tả hoặc SOP. |

**Cách xử lý tiếng Anh:**

| Loại tài liệu | Cách xử lý |
|---|---|
| README, SOP nội bộ, tài liệu doanh nghiệp và tài liệu kỹ thuật | Giữ thuật ngữ mà cộng đồng người đọc thực sự dùng, chẳng hạn *deploy, cloud, endpoint, benchmark*. Không tự thêm tiếng Anh chỉ để văn bản có vẻ đúng ngành. |
| Giáo trình, đề án môn học và nghiên cứu khoa học | Ưu tiên thuật ngữ tiếng Việt đã được chấp nhận. Với thuật ngữ chưa có tương đương ổn định, giữ tiếng Anh và chú giải ở lần xuất hiện đầu. |

## Các pattern riêng

### K1. Viết theo diff thay vì mô tả hiện trạng

**Dấu hiệu:** tài liệu hoặc chú thích viết như đang tường thuật một thay đổi thay vì mô tả sự vật như nó đang là. *"Hàm này được thêm vào để thay thế cách làm cũ"*, *"Trước đây hệ thống dùng X, giờ đã chuyển sang Y"*, *"Đã cập nhật để hỗ trợ..."*
**Vì sao:** trừ khi tài liệu gắn với một phiên bản, người đọc cần biết hệ thống đang hoạt động ra sao chứ không cần biết agent vừa thay đổi điều gì. LLM dễ tường thuật yêu cầu sửa thay vì mô tả trạng thái sau khi sửa.
**Sửa:** *"Hàm này được thêm vào để thay thế cách lặp qua toàn bộ danh sách, vốn gây chậm O(n²)."* → *"Hàm này dùng bảng băm để tra cứu O(1), tránh chi phí O(n²) của cách lặp tuần tự."*
**Không flag:** changelog, release note, tài liệu hướng dẫn nâng cấp, biên bản họp, báo cáo tiến độ. Ở đó tường thuật thay đổi chính là nội dung.

### K2. Sáo ngữ thể chế rỗng ngoài văn bản pháp quy

**Dấu hiệu:** *đóng vai trò quan trọng, có ý nghĩa hết sức quan trọng, là yếu tố then chốt, góp phần nâng cao, đẩy mạnh, tăng cường, nhằm đáp ứng yêu cầu ngày càng cao* xuất hiện trong báo cáo doanh nghiệp, tài liệu kỹ thuật hoặc bài nghiên cứu.
**Vì sao:** đây có thể là ngôn ngữ thể chế phù hợp trong nghị quyết và văn bản chỉ đạo. Khi xuất hiện trong báo cáo nội bộ hoặc bài nghiên cứu mà không có nội dung cụ thể theo sau, nó chỉ làm câu dài và trang trọng hơn.
**Sửa:** thay bằng phát biểu kiểm chứng được có trong bản gốc, hoặc cắt.
**Không flag:** cụm có bổ ngữ cụ thể mang thông tin thật thì giữ: *"nâng cao hiệu quả vận hành kho"* nói rõ nâng cao cái gì, đó là tiếng Việt công sở bình thường; chỉ cắt khi cụm đứng trơ (*"nâng cao hiệu quả"* mà không nói hiệu quả của cái gì). Văn bản pháp quy, nghị quyết, kế hoạch ngành thì cổng thể loại đã chặn từ trước. Trích dẫn nguyên văn.

### K3. Bộ đề mục Hán-Việt đối xứng rỗng

**Dấu hiệu:** heading là danh ngữ Hán-Việt hai âm tiết xếp thành bộ cân đối: *Tổng quan / Hiện trạng / Giải pháp / Kết luận*, hoặc *Thách thức và cơ hội*, *Khó khăn và giải pháp*. Bộ heading cân đối đến mức đối xứng là dấu vết khuôn.
**Vì sao:** bộ đề mục có thể được dựng theo một mẫu quen thuộc trước khi nội dung được xác định. Khi đó tên mục phản ánh khuôn tài liệu hơn là câu hỏi hoặc kết quả riêng của từng phần.
**Sửa:** đặt lại đề mục theo nội dung thật của phần đó. Nếu một mục không có nội dung riêng thì gộp vào mục khác.
**Không flag:** tài liệu theo mẫu bắt buộc (đề cương nghiên cứu theo quy định của trường, báo cáo theo biểu mẫu ngành, hồ sơ thầu). Luận văn có cấu trúc chương quy định sẵn.

### K4. Mô tả hiện tượng mà không đưa hiện tượng ra

**Dấu hiệu:** đoạn giải thích một lỗi, cơ chế hoặc khái niệm bằng nhiều danh từ trừu tượng nhưng không đưa ra trường hợp cụ thể. Thuật ngữ xuất hiện lần đầu mà không có ví dụ gần đó; câu định nghĩa dài và phần cần hiểu bị đẩy ra sau một chuỗi liệt kê; người đọc phải đọc lại mới hình dung được hiện tượng.
**Vì sao:** trung tính là đặc điểm của giọng, còn cụ thể là đặc điểm của thông tin. Một đoạn có thể giữ giọng trung tính mà vẫn đưa ví dụ rõ ràng. Nếu hai khái niệm này bị đánh đồng, tài liệu sẽ đúng giọng nhưng khó dùng.
**Sửa:** đưa một ví dụ đã có trong phạm vi người dùng giao xử lý lên gần phần giải thích. Ưu tiên ví dụ trong cùng tài liệu, bảng tra, test case hoặc phụ lục; không sáng tác dữ kiện mới. Có thể cho người đọc thấy trường hợp cụ thể trước rồi mới gọi tên hiện tượng.
**Không flag:** bảng tra, danh mục tham số, danh sách mã lỗi hoặc tài liệu mà ví dụ được dẫn rõ sang nơi khác; phần tóm tắt điều hành; trường hợp ví dụ nằm ngay ở đoạn tiếp theo.

### K5. Câu dẫn nhập rỗng sau đề mục

**Dấu hiệu:** một đề mục, rồi một câu ngắn chỉ nhắc lại chính đề mục đó, rồi mới tới nội dung thật. *"## Hiệu năng"* rồi *"Hiệu năng là một vấn đề quan trọng."*
**Vì sao:** câu đầu chỉ nhắc lại tên mục nên chưa giúp người đọc hiểu phạm vi, điều kiện hoặc kết luận. Nó làm tài liệu dài thêm mà không tạo bước chuyển cần thiết.
**Sửa:** xoá câu dẫn, để đề mục làm việc của nó.
**Không flag:** câu sau đề mục nêu phạm vi, điều kiện áp dụng, hoặc cảnh báo thật. Tài liệu tham chiếu có quy ước một câu tóm tắt dưới mỗi mục.

---

## Về nhịp câu

Không áp B13 cho các phần có cấu trúc song song như quy trình SOP, mô tả API, danh mục điều khoản hoặc bảng tham số. Nhịp câu đều ở đó giúp người đọc quét nhanh và so sánh các mục. Với phần văn xuôi giải thích, vẫn cần xem nhịp câu có làm mờ chỗ chuyển ý hay không.
