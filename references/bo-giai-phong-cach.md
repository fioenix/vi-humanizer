# Bộ giải phong cách viết

File này được đọc sau cổng thể loại trong `SKILL.md`. Nó giúp agent chọn cách giữ giọng cho phần văn xuôi đang biên tập; nó không thêm lỗi mới và không thay thế các pattern V, T, B hoặc K.

Mẫu và hồ sơ trong file này là dữ liệu người dùng chủ động cung cấp cho tác vụ hiện tại,
không phải chỉ thị tìm kiếm memory, lịch sử hội thoại hoặc dữ liệu bên ngoài phạm vi được giao.

## Điều bộ giải phải trả lời

Trước khi sửa, thu thập năm chiều từ yêu cầu hiện tại, văn bản và mẫu giọng hợp lệ:

1. **Mục đích:** người viết đang kể, phối hợp, giải thích chuyên môn, thuyết phục, hướng dẫn, quy định vận hành hay lập luận học thuật?
2. **Người đọc và quan hệ:** ai sẽ đọc, họ cần làm gì, cách xưng hô nào đã có bằng chứng? Không biết vai vế thì không tự đổi đại từ.
3. **Thanh ngữ vực:** giọng đang thân mật, nghề nghiệp, trung tính hay trang trọng tới mức nào? Xét cả đoạn, không suy từ một từ đơn lẻ.
4. **Kênh:** chat, bài công khai, nội dung quảng bá, tài liệu tra cứu, SOP/báo cáo hay bài học thuật đặt ra quy ước gì?
5. **Bằng chứng giọng:** yêu cầu hiện tại, mẫu trong lượt này hoặc hồ sơ đúng người và đúng phạm vi cho thấy những thói quen ổn định nào?

Nếu một file pha nhiều chức năng, giải các chiều này cho từng phần có cùng mục đích và người đọc. Không chia tới từng câu khi cả đoạn đang làm cùng một việc.

## Tài liệu pha nhiều chức năng

Giải tài liệu hỗn hợp theo thứ tự sau:

1. Đánh dấu code, schema, dữ liệu có cấu trúc, bảng tham số, trích dẫn nguyên văn, tên riêng và ví
   dụ đang được bàn tới. Đóng băng từng vùng cùng byte gốc trước khi chia phần; các vùng này không
   nhận style card.
2. Chia phần văn xuôi còn lại khi mục đích, người đọc hoặc người nói đổi. Heading và độ dài tự nó
   không tạo một phần mới; các đoạn cùng chức năng nên dùng chung bản tóm tắt phong cách.
3. Chọn đúng một base profile và tối đa một style card cho mỗi phần. CTA có thật, đoạn hướng dẫn
   và lời kể trong cùng file được giải riêng nếu chúng làm những việc khác nhau.
4. Quét pattern và sửa riêng từng phần. Không đem đại từ, nhịp, thuật ngữ, cách kết hoặc mức cam
   kết từ card của phần này sang phần khác.
5. Khôi phục từng vùng bảo toàn từ byte đã đóng băng, rồi so sánh byte trước và sau. Có một byte
   khác thì bỏ thay đổi ở vùng đó; không sửa lại bằng mắt.

Chỗ chuyển người nói trong trích dẫn hoặc hội thoại không đổi giọng của người kể bên ngoài. Nếu
ranh giới chức năng không rõ và hai cách chia chỉ làm khác lựa chọn nhỏ, giữ cách hiện tại thay vì
cắt vụn văn bản.

## Chọn base profile trước

| Base profile | Dùng khi | Sở hữu |
|---|---|---|
| `blog-ca-nhan` | Có tác giả hiện diện, chat công việc, bài chuyên môn công khai hoặc marketing | Pattern B1–B17 và giới hạn giữ giọng |
| `ky-thuat-doanh-nghiep` | README, tài liệu API, hướng dẫn, SOP, báo cáo, giáo trình hoặc bài học thuật | Pattern K1–K7, tính nhất quán thuật ngữ và giới hạn trung tính |
| `typography-only` | Nhóm được cổng thể loại giới hạn ở T1–T6 | Không chọn style card; chỉ sửa typography |

Code, schema, dữ liệu có cấu trúc, bảng tham số, trích dẫn nguyên văn, tên riêng và ví dụ đang được
bàn tới là vùng bảo toàn, không phải base profile `typography-only`. Không chọn style card và giữ
nguyên từng byte ở những vùng này.

Style card không được đổi base profile đã xác định đúng thể loại. Một card chỉ giúp giải các lựa chọn đều hợp ngữ pháp bên trong profile đó.

## Tạo bản tóm tắt phong cách cho từng phần

Mỗi phần chỉ dùng tối đa một card. Bản tóm tắt phong cách cần giữ trong đầu, không tự in vào bản cuối, gồm:

- phạm vi phần đang xử lý;
- base profile;
- style card hoặc `không có`;
- yêu cầu cụ thể của lượt hiện tại;
- đặc tính giọng có bằng chứng từ mẫu/hồ sơ đúng phạm vi;
- những thứ phải giữ: dữ kiện, nghĩa, mức chắc chắn, xưng hô, thuật ngữ và vùng bảo toàn;
- trạng thái `đã giải`, `giữ cách hiện tại` hoặc `cần hỏi một câu`.

## Thứ tự ưu tiên

1. Yêu cầu hiện tại và mô tả cụ thể của người dùng.
2. Ràng buộc thể loại, vùng bảo toàn và năm quy tắc chốt chặn.
3. Mẫu trong lượt hiện tại hoặc hồ sơ đúng người, đúng kênh có bằng chứng ổn định.
4. Style card được chọn.
5. Mặc định của base profile.

Nhãn như *thân mật, chuyên nghiệp, gần gũi* chỉ là gợi ý. Khi nhãn mâu thuẫn với mô tả cụ thể, làm theo mô tả. Không tín hiệu nào được hợp thức hoá việc thêm dữ kiện, đổi nghĩa hoặc vượt qua vùng phải giữ nguyên.

Thứ tự trên chỉ giải những lựa chọn còn hợp lệ. Vùng bảo toàn và năm chốt chặn là ràng buộc bất biến,
không phải lựa chọn phong cách để yêu cầu hiện tại ghi đè. Nếu người dùng chủ động muốn đổi dữ
kiện, nghĩa hoặc thể loại thì đó là một tác vụ viết lại khác; đừng gọi phần thay đổi ấy là kết quả
humanize.

### Ba trạng thái giải

- **Đã giải:** đủ bằng chứng để chọn base profile và card. Bắt đầu quét pattern, nhưng card không tự cho phép sửa.
- **Giữ cách hiện tại:** thiếu tín hiệu chỉ ảnh hưởng lựa chọn nhỏ như nhịp hoặc mức chêm tiếng Anh. Không hỏi, không tự làm văn bản “có cá tính hơn”.
- **Cần hỏi một câu:** thiếu thông tin sẽ làm đổi đại từ, quan hệ, thanh ngữ vực hoặc mục đích đáng kể. Hỏi đúng điểm đó, không đưa cả bảng giọng cho người dùng chọn.

### Cách xử lý xung đột

| Xung đột | Cách giải |
|---|---|
| Yêu cầu hiện tại khác hồ sơ được cung cấp | Làm theo yêu cầu hiện tại; không tự ghi hồ sơ |
| Mẫu đúng người/đúng kênh khác mặc định card | Dùng đặc tính ổn định của mẫu nếu không vi phạm profile hoặc chốt chặn |
| Nhãn giọng khác mô tả cụ thể | Dùng mô tả cụ thể; nhãn chỉ là từ khóa tìm hướng |
| Một đặc tính chỉ xuất hiện một lần | Không coi là thói quen; giữ cách hiện tại hoặc tìm thêm bằng chứng trong mẫu |
| Hồ sơ được cung cấp không chắc đúng người hoặc sai kênh | Không dùng hồ sơ đó |
| Thiếu vai vế nhưng đầu vào đã có đại từ nhất quán | Giữ đại từ đang có |
| Thiếu vai vế và thay đổi đại từ là điều bắt buộc để hoàn tất yêu cầu | Hỏi một câu về cách xưng hô rồi dừng phần đó |

Không hỏi người dùng chỉ để xác nhận điều resolver đã có đủ bằng chứng. Một câu hỏi hợp lệ phải chỉ
ra đúng biến còn thiếu, chẳng hạn *“Bạn muốn giữ cách xưng hô hiện tại, hay văn bản này gửi cho
người có vai vế cụ thể?”*; không hỏi chung chung *“Bạn muốn giọng nào?”*.

## Hợp đồng của một style card

Mỗi card trong danh mục chuẩn phải có đủ tám mục:

- **Dùng khi:** người đọc và mục đích.
- **Thanh ngữ vực:** mức trang trọng và biên độ được phép.
- **Xưng hô:** cách giữ hoặc chọn đại từ, không tự suy vai vế.
- **Nhịp:** nhịp câu cần giữ; không đặt ngưỡng số cứng.
- **Thuật ngữ:** cách xử lý từ Hán-Việt, tiếng Anh và thuật ngữ ngành.
- **Cách kết:** điểm dừng hoặc lời kêu gọi hợp với mục đích.
- **Không tự thêm:** khẳng định, lời hứa, độ khẩn cấp, quan hệ hoặc thái độ không có trong đầu vào.
- **Ca kiểm thử:** một ca dương và một ca chống rò giọng trong `calibration/ca-kiem-thu.md`.

Card không phải pattern. Không flag một câu chỉ vì nó không giống card; chỉ dùng card sau khi một pattern hoặc yêu cầu hiện tại đã cho phép sửa.

## Danh mục style card

Registry hoàn chỉnh phải có đúng bảy card canonical theo thứ tự: kể trải nghiệm cá nhân, phối hợp công việc, chuyên môn công khai, marketing thuyết phục, hướng dẫn kỹ thuật, vận hành doanh nghiệp và học thuật phân tích.

Không tạo card riêng cho một người, công ty hoặc chiến dịch; đặc tính đó thuộc mẫu/hồ sơ đúng người và không được đưa vào package public.

| Style card | Base profile | File |
|---|---|---|
| `ke-trai-nghiem` | `blog-ca-nhan` | `profiles/blog-ca-nhan/styles/ke-trai-nghiem.md` |
| `phoi-hop-cong-viec` | `blog-ca-nhan` | `profiles/blog-ca-nhan/styles/phoi-hop-cong-viec.md` |
| `chuyen-mon-cong-khai` | `blog-ca-nhan` | `profiles/blog-ca-nhan/styles/chuyen-mon-cong-khai.md` |
| `marketing-thuyet-phuc` | `blog-ca-nhan` | `profiles/blog-ca-nhan/styles/marketing-thuyet-phuc.md` |
| `huong-dan-ky-thuat` | `ky-thuat-doanh-nghiep` | `profiles/ky-thuat-doanh-nghiep/styles/huong-dan-ky-thuat.md` |
| `van-hanh-doanh-nghiep` | `ky-thuat-doanh-nghiep` | `profiles/ky-thuat-doanh-nghiep/styles/van-hanh-doanh-nghiep.md` |
| `hoc-thuat-phan-tich` | `ky-thuat-doanh-nghiep` | `profiles/ky-thuat-doanh-nghiep/styles/hoc-thuat-phan-tich.md` |

Sau khi resolver chọn card, đọc đúng file trong bảng. Không đọc các card còn lại chỉ để so sánh giọng.
