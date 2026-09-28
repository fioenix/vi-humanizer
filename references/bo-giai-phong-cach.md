# Bộ giải phong cách viết

File này được đọc sau cổng thể loại trong `SKILL.md`. Nó giúp agent chọn cách giữ giọng cho phần văn xuôi đang biên tập; nó không thêm lỗi mới và không thay thế các pattern V, T, B hoặc K.

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
| Yêu cầu hiện tại khác hồ sơ cũ | Làm theo yêu cầu hiện tại trong lượt này; không sửa hồ sơ nếu người dùng chưa yêu cầu lưu |
| Mẫu đúng người/đúng kênh khác mặc định card | Dùng đặc tính ổn định của mẫu nếu không vi phạm profile hoặc chốt chặn |
| Nhãn giọng khác mô tả cụ thể | Dùng mô tả cụ thể; nhãn chỉ là từ khóa tìm hướng |
| Một đặc tính chỉ xuất hiện một lần | Không coi là thói quen; giữ cách hiện tại hoặc tìm thêm bằng chứng trong mẫu |
| Bộ nhớ không chắc đúng người hoặc sai kênh | Không dùng bộ nhớ |
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

### `ke-trai-nghiem`: Kể trải nghiệm cá nhân

- **Dùng khi:** người viết kể điều mình đã làm, thấy hoặc thay đổi suy nghĩ để người đọc hiểu trải nghiệm đó; base profile `blog-ca-nhan`.
- **Thanh ngữ vực:** tự nhiên theo mẫu, có thể thân mật nhưng không tự hạ giọng hoặc làm câu bông đùa.
- **Xưng hô:** giữ ngôi kể và cách gọi người đọc đang có. Không đổi *tôi* thành *mình*, hoặc ngược lại, chỉ để tạo cảm giác gần gũi.
- **Nhịp:** giữ diễn biến, chỗ ngập ngừng, câu ngắn và câu chen ngang có chức năng. Không san mọi đoạn thành một nhịp đều.
- **Thuật ngữ:** giữ từ ngành mà người viết thực sự dùng; giải thích khi chính người đọc cần, không dịch đồng loạt sang từ đời thường.
- **Cách kết:** dừng ở quan sát, thay đổi hoặc câu hỏi thật đã có trong bản gốc; không thêm bài học phổ quát cho đủ kết.
- **Không tự thêm:** trải nghiệm, cảm xúc, chi tiết đời sống, lời thú nhận hoặc kết luận mà người viết không nêu.
- **Ca kiểm thử:** dương MS01 và MS10; chống rò MS02 và MS09.

### `phoi-hop-cong-viec`: Phối hợp công việc

- **Dùng khi:** tin nhắn, bình luận hoặc đoạn trao đổi giữa những người đang phối hợp một việc; base profile `blog-ca-nhan`.
- **Thanh ngữ vực:** trực tiếp, nghề nghiệp và vừa đủ thân theo quan hệ đã có; không tự biến thành công văn hoặc chat suồng sã.
- **Xưng hô:** giữ đại từ, vai trò và tên gọi đang có. Thiếu vai vế mà đổi đại từ sẽ đổi quan hệ thì hỏi một câu.
- **Nhịp:** ưu tiên câu ngắn nêu tình trạng, việc cần làm, người nhận hoặc mốc có sẵn. Không biến bullet công việc thành đoạn diễn giải dài.
- **Thuật ngữ:** giữ cách gọi nội bộ và tiếng Anh quen thuộc với nhóm người đọc; không dùng jargon để tỏ ra chuyên nghiệp.
- **Cách kết:** bước tiếp theo, mốc hoặc lời xác nhận có thật. Tiểu từ chỉ được giữ/thêm khi mẫu và quan hệ cho phép.
- **Không tự thêm:** deadline, người chịu trách nhiệm, mức ưu tiên, lời hứa hoặc quyền ra lệnh không có trong đầu vào.
- **Ca kiểm thử:** dương MS03 và MS12; chống rò MS04 và MS11.

### `chuyen-mon-cong-khai`: Chuyên môn công khai

- **Dùng khi:** bài chia sẻ chuyên môn, LinkedIn hoặc bài quan điểm cho người đọc ngoài nhóm làm việc trực tiếp; base profile `blog-ca-nhan`.
- **Thanh ngữ vực:** nghề nghiệp nhưng có tác giả hiện diện; lập luận rõ hơn chat, ít thể chế hơn báo cáo.
- **Xưng hô:** giữ ngôi thứ nhất nếu nó gắn với quan sát hoặc trách nhiệm thật; không thêm *chúng ta* để kéo người đọc vào một đồng thuận giả.
- **Nhịp:** đi từ kết luận hoặc dữ kiện cụ thể tới giải thích; giữ nhịp riêng của tác giả, không dựng hook và kết luận theo khuôn mạng xã hội.
- **Thuật ngữ:** dùng từ ngành đúng cộng đồng và giải thích vừa đủ cho người đọc rộng hơn; không thay thuật ngữ chỉ để tránh lặp.
- **Cách kết:** hệ quả, giới hạn hoặc bước tiếp theo đã có trong nội dung; không thêm lời mời bình luận máy móc.
- **Không tự thêm:** số liệu, nguồn, vị thế chuyên gia, trải nghiệm cá nhân hoặc mức chắc chắn cao hơn bản gốc.
- **Ca kiểm thử:** dương MS04 và MS05; chống rò MS03 và MS06.

### `marketing-thuyet-phuc`: Marketing thuyết phục

- **Dùng khi:** nội dung giới thiệu sản phẩm/dịch vụ có mục tiêu giúp người đọc cân nhắc hoặc thực hiện một CTA đã được giao; base profile `blog-ca-nhan`.
- **Thanh ngữ vực:** rõ lợi ích nhưng không thổi phồng; mức thân mật theo kênh và mẫu thương hiệu trong yêu cầu hiện tại.
- **Xưng hô:** giữ cách gọi người đọc đang có. Không tự thêm *bạn, nhà mình, khách hàng thân yêu* nếu quan hệ chưa được xác định.
- **Nhịp:** đưa giới hạn, lợi ích và điều kiện cụ thể trước; không dàn thành chuỗi slogan, câu hỏi tu từ hoặc nhịp ba trang trí.
- **Thuật ngữ:** ưu tiên cách gọi người mua hiểu mà không làm sai tên tính năng; không chêm tiếng Anh chỉ để tạo vẻ hiện đại.
- **Cách kết:** giữ CTA có thật và đúng mức cam kết. Không có CTA thì không tự thêm một CTA mới.
- **Không tự thêm:** khẩn cấp giả, khan hiếm, lời hứa kết quả, so sánh nhất, testimonial, chứng nhận hoặc dữ kiện bán hàng.
- **Ca kiểm thử:** dương MS07 và MS14; chống rò MS08 và MS13.

### `huong-dan-ky-thuat`: Hướng dẫn kỹ thuật

- **Dùng khi:** README, phần văn xuôi của tài liệu API, hướng dẫn cài đặt hoặc xử lý lỗi; base profile `ky-thuat-doanh-nghiep`.
- **Thanh ngữ vực:** trung tính, chính xác, hướng hành động; không thêm thân mật để làm tài liệu có vẻ “người”.
- **Xưng hô:** ưu tiên câu lệnh hoặc chủ thể kỹ thuật đã có; không thêm ngôi thứ nhất và không đổi tác nhân của thao tác.
- **Nhịp:** điều kiện trước hành động khi cần, một bước cho một hành động, cấu trúc song song khi giúp quét nhanh; giữ code và thứ tự.
- **Thuật ngữ:** nhất quán theo cộng đồng kỹ thuật và tài liệu lân cận; không dịch tên API, command, schema hoặc identifier.
- **Cách kết:** kết quả mong đợi, điều kiện dừng hoặc liên kết đã có; không thêm lời chúc hay mời dùng tiếp.
- **Không tự thêm:** command, tham số, output, nguyên nhân lỗi, compatibility hoặc bảo đảm vận hành chưa có nguồn trong phạm vi tài liệu.
- **Ca kiểm thử:** dương MS06, MS08 và MS09; chống rò MS05, MS07 và MS10.

### `van-hanh-doanh-nghiep`: Vận hành doanh nghiệp

- **Dùng khi:** SOP, báo cáo, biên bản hoặc hướng dẫn bàn giao cần giữ vai trò, điều kiện và trách nhiệm; base profile `ky-thuat-doanh-nghiep`.
- **Thanh ngữ vực:** trung tính và nghiệp vụ; không hành chính hoá câu chỉ để tạo vẻ chính thức.
- **Xưng hô:** dùng vai trò hoặc chủ thể đã nêu. Không suy ai có thẩm quyền và không đổi lời nhờ thành mệnh lệnh.
- **Nhịp:** ưu tiên cấu trúc dễ quét, song song khi các bước cùng cấp; không phá bảng, checklist hoặc nhãn–giá trị có chức năng.
- **Thuật ngữ:** giữ từ nghiệp vụ, Hán-Việt đúng nghĩa và cách gọi nhất quán; không thuần Việt hoá điều khoản hoặc trạng thái được định nghĩa.
- **Cách kết:** trạng thái hoàn tất, điều kiện chuyển bước hoặc đầu mối đã có; không thêm khẩu hiệu hoặc lời kêu gọi chung chung.
- **Không tự thêm:** vai trò, phê duyệt, deadline, cam kết, thứ tự, quan hệ đồng thời hoặc trạng thái hoàn tất.
- **Ca kiểm thử:** dương MS02 và MS11; chống rò MS01, MS03 và MS12.

### `hoc-thuat-phan-tich`: Học thuật phân tích

- **Dùng khi:** giáo trình, đề án, bài nghiên cứu hoặc đoạn lập luận cần phân biệt dữ liệu, suy luận và giới hạn; base profile `ky-thuat-doanh-nghiep`.
- **Thanh ngữ vực:** trung tính, có mức dè dặt đúng bằng chứng; không làm thân mật hoặc nâng mức chắc chắn để câu dứt khoát hơn.
- **Xưng hô:** giữ *chúng tôi* khi đó là nhóm tác giả; không thêm ngôi thứ nhất nếu văn bản đang dùng lối trình bày phi cá nhân.
- **Nhịp:** ưu tiên quan hệ lập luận rõ, thuật ngữ ổn định và câu chuyển có chức năng; không cắt câu dài nếu việc cắt làm mất phạm vi hoặc điều kiện.
- **Thuật ngữ:** giữ thuật ngữ chuyên ngành và cách dẫn nguồn; tiếng Anh chỉ giữ khi chưa có tương đương ổn định hoặc quy ước ngành yêu cầu.
- **Cách kết:** chỉ nêu kết luận và giới hạn được dữ liệu hỗ trợ; không thêm ý nghĩa xã hội rộng hơn nếu nguồn không nêu.
- **Không tự thêm:** trích dẫn, tác giả, số liệu, quan hệ nhân quả, khả năng suy rộng hoặc lối mượn uy tín thay cho bằng chứng.
- **Ca kiểm thử:** dương MS13; chống rò MS07 và MS14.
