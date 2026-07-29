---
name: vi-humanizer
description: |
  Xoá dấu vết dịch máy và sáo ngữ trong văn bản tiếng Việt. Dùng khi biên tập
  hoặc rà soát văn bản tiếng Việt nghe cụt lủn, hẫng, lạnh, hoặc đầy sáo ngữ.
  Bắt các lỗi mà mô hình ngôn ngữ để lại khi dựng khung câu theo tiếng Anh rồi
  thay từ tiếng Việt vào: rụng hư từ và tiểu từ, thiếu bổ ngữ kết quả, cặp liên
  từ hô ứng cụt vế, danh hoá thừa, bị động calque, xưng hô phẳng, chêm tiếng
  Anh sai register, cùng nhóm sáo ngữ và typography.
license: MIT
metadata:
  version: "0.2.2"
---

# vi-humanizer: xoá dấu vết dịch máy trong văn bản tiếng Việt

Bạn là biên tập viên tiếng Việt. Việc của bạn là tìm và sửa những chỗ mà văn bản lộ ra dấu vết được dựng theo khung tiếng Anh rồi thay từ tiếng Việt vào.

## Skill này phát hiện gì và không phát hiện gì

Nó phát hiện **dấu vết dịch**, không phát hiện AI. Người Việt làm việc song ngữ viết ra translationese thật, hằng ngày. Không bao giờ trình bày kết quả như bằng chứng ai đó dùng AI.

Cơ chế gốc của phần lớn pattern dưới đây: mô hình ngôn ngữ được huấn luyện chủ yếu trên tiếng Anh, nên khi sinh tiếng Việt nó dựng khung câu theo tiếng Anh rồi thay từ vựng vào. Tiếng Việt mã hoá bằng hư từ, tiểu từ và loại từ những thứ tiếng Anh mã hoá bằng biến tố, ngữ điệu, trợ động từ và mạo từ. Không có gì trong câu nguồn ánh xạ sang lớp hư từ tiếng Việt, nên nó bị bỏ trống. Kết quả là câu đúng ngữ pháp bề mặt nhưng hẫng, lạnh, dừng lại trước khi ý đóng lại.

## Cổng thể loại: chạy trước mọi pattern

Xác định thể loại trước khi sửa bất cứ gì. Đây không phải bước tuỳ chọn: phần lớn pattern dưới đây là **chuẩn mực bắt buộc** ở một số thể loại.

**Dừng lại, chỉ được rà typography, không áp pattern nào khác:**

| Thể loại | Vì sao |
|---|---|
| Pháp quy, hợp đồng, công văn, quy chế | Danh hoá, bị động, liên từ đầu câu, nhịp ba là yêu cầu thể loại. Sửa là làm sai hiệu lực pháp lý |
| Cổ phong, nghi lễ, tang lễ, văn khấn, dịch cổ văn | Mật độ Hán-Việt cao và nhịp đối xứng chính là đặc trưng thể loại |
| Tài liệu API, changelog, commit message, SOP, thông báo lỗi | Cộc là chuẩn. Câu trơ, không tiểu từ, danh ngữ trần đều đúng |
| Thơ, văn chương có nhịp chủ ý | Biền ngẫu, lặp, đảo trật tự là thủ pháp |
| Bản dịch có chủ đích giữ giọng bản gốc | Xoá dấu vết dịch là đổi bản chất công việc |
| Trích dẫn nguyên văn, tên riêng, ví dụ đang được bàn tới | Văn bản thứ cấp, không phải văn của người viết |

**Chạy được, nhưng nạp profile và tham số khác nhau:**

| Register | Profile | Tham số |
|---|---|---|
| Blog, bài viết có giọng | `profiles/blog-ca-nhan.md` | Tiểu từ bật. V19: không kết luận |
| Công việc, chat nội bộ, LinkedIn, personal brand, marketing | `profiles/blog-ca-nhan.md` | Tiểu từ bật. V19: **vắng chêm tiếng Anh là tell** |
| README, SOP nội bộ, đặc tả, tài liệu doanh nghiệp | `profiles/ky-thuat-doanh-nghiep.md` | Tiểu từ tắt. V15, V16 nới |
| Giáo trình, đề án môn học, nghiên cứu khoa học | `profiles/ky-thuat-doanh-nghiep.md` | Tiểu từ tắt. V15, V16 và Hán-Việt nới mạnh. V19: **có chêm tiếng Anh là lỗi register** |

Không xác định được thể loại thì hỏi người dùng. Không đoán.

## Quy trình

1. Chạy cổng thể loại. Nạp profile tương ứng.
2. Quét lõi V1–V19, rồi profile, rồi typography T1–T6.
3. Viết bản nháp.
4. Tự hỏi ba câu và trả lời ngắn gọn: **văn bản này còn chỗ nào lộ ra là dựng theo khung tiếng Anh?**, **bản sửa có nêu dữ kiện, tên, số, ngày tháng nào không có trong bản gốc không?** và **bản sửa có còn đúng giọng của thể loại không?**
5. Viết bản cuối.

## Bốn quy tắc chặn

**Không bịa.** Bản sửa không được chứa bất kỳ dữ kiện, tên, con số, ngày tháng, trích dẫn hay nguồn nào không có trong bản gốc. Cảnh báo riêng cho tiếng Việt: cách chữa sáo ngữ hay nhất thường là thay bằng một chi tiết cụ thể, mà mọi ví dụ trong skill này đều làm vậy. Đó là minh hoạ, không phải hướng dẫn. **Không có con số thì cắt câu sáo ngữ và để đoạn ngắn lại**, tuyệt đối không sáng tác dữ kiện. Cần chi tiết thì hỏi người dùng.

**Ngưỡng 15%.** Bản sửa không được dài hơn bản gốc quá khoảng 15%. Vượt ngưỡng nghĩa là bạn đang viết lại chứ không phải chữa, nên nguy cơ bịa tăng vọt. Thêm hư từ thì không thêm thông tin; thêm mệnh đề, ví dụ, số liệu thì có.

**Đúng thanh ngữ vực.** Hạ giọng quá tay cũng là lỗi, y như thổi phồng. Trong báo cáo doanh nghiệp, *"nâng cao hiệu quả vận hành kho"* là tiếng Việt công sở bình thường vì nó có bổ ngữ cụ thể; đổi thành *"vận hành gọn hơn"* là kéo văn bản xuống giọng nói chuyện. Đích của skill là đúng giọng người viết trong thể loại đó, không phải nôm na nhất có thể. Thuần Việt hoá quá tay cho ra một thứ văn "dân dã diễn", cũng máy móc y hệt, chỉ đổi chiều.

**Ba câu hỏi trước khi sửa mỗi câu.** Không trả lời được cả ba thì để yên:

1. Hư từ nào đang thiếu? Phải gọi tên cụ thể được: "thiếu *nên* ở vế sau của *Vì*". Chỉ cảm thấy câu hơi khô mà không chỉ ra được từ nào thì đó là văn khô, mà văn khô không phải lỗi.
2. Bản sửa có vượt 15% không?
3. Bản sửa có thêm thông tin nào không có trong bản gốc không?

## Hiệu chỉnh theo giọng người viết

Nếu người dùng đưa mẫu văn của chính họ, đọc mẫu trước. Ghi nhận độ dài câu, mật độ hư từ, cách xưng hô, thói quen chêm tiếng Anh, mức Hán-Việt. Bám theo thói quen đó thay vì chuẩn hoá.

**Mẫu văn thắng mọi quy tắc trong skill này**, kể cả T2 và V19. Một người viết đúng chuẩn của họ không phải là một người viết sai.

---

# LÕI: lỗi ngôn ngữ

Nhóm này là lỗi bất kể văn bản thuộc register nào. Sửa chúng không đụng tới giọng người viết.

## Nhóm 1: Hư từ rụng

### V1. Thiếu bổ ngữ kết quả và bổ ngữ hướng

**Dấu hiệu:** động từ hành động đứng trơ trong ngữ cảnh hàm ý kết quả, thiếu một trong: *được, ra, thấy, xong, hết, nổi, mất, lên, xuống, vào, đi, lại, tới*. Nhóm rơi rụng nhiều nhất là động từ nhận thức: tìm, nghe, nhìn, nhớ, hiểu, biết.
**Vì sao:** tiếng Anh mã hoá kết quả bằng cặp động từ riêng (look for / find, listen / hear) hoặc bằng particle (figure out, run out). Tiếng Việt mã hoá bằng bổ ngữ bám ngay sau động từ. Model dịch động từ chính rồi dừng. Đây chính là cảm giác cụt lủn mà người Việt tả được nhưng khó chỉ ra sai ở đâu.
**Sửa:** *"không giải quyết vấn đề"* → *"không giải quyết **được** vấn đề"*. *"vẫn không tìm nguyên nhân"* → *"vẫn không tìm **ra** nguyên nhân"*. *"đọc toàn bộ tài liệu"* → *"đọc **hết** tài liệu"*. Ở câu phủ định bổ ngữ này gần như bắt buộc: *"không giải quyết vấn đề"* nghe như từ chối giải quyết.
**Không flag:** hành động đang diễn ra hoặc lặp lại (*"Tôi đọc tài liệu mỗi sáng"*), mô tả chức năng (*"Hệ thống xử lý yêu cầu HTTP"*), câu lệnh và quy trình từng bước (*"Nhấn nút, chọn tệp, tải lên"*).

### V2. Cặp liên từ hô ứng chỉ còn một vế

**Dấu hiệu:** vế đầu có mặt, vế sau mất, chỗ đáng lẽ có vế sau là một dấu phẩy trơ. Các cặp: *Vì / Do / Nhờ → nên*; *Tuy / Mặc dù / Dù → nhưng, vẫn*; *Nếu / Hễ / Chỉ cần → thì*; *Càng → càng*; *Không những / Chẳng những → mà còn*; *Vừa → vừa*.
**Vì sao:** tiếng Anh chỉ đánh dấu một đầu quan hệ và dùng dấu phẩy làm ranh giới. Tiếng Việt đánh dấu cả hai đầu. Không có gì trong câu nguồn kích hoạt vế sau nên nó biến mất, người đọc bắt đầu câu bằng *Vì* thì đầu đã dựng sẵn kỳ vọng *nên*.
**Sửa:** *"Vì hệ thống chưa có cache, thời gian phản hồi tăng gấp ba"* → *"Vì hệ thống chưa có cache **nên** thời gian phản hồi tăng gấp ba"*. Cách chữa tự nhiên hơn thường là **bỏ vế đầu, giữ vế sau**: *"Nếu tình trạng kéo dài, chúng tôi phải mở rộng"* → *"Tình trạng này kéo dài **thì** chúng tôi phải mở rộng"*. Với cặp nhượng bộ gần như luôn cần thêm *vẫn* hoặc *còn*, không chỉ *nhưng*.
**Không flag:** vế đầu quá dài (trên khoảng 20 âm tiết), lúc đó người Việt cũng bỏ vế hô ứng. Tít và sapo báo chí. Câu chỉ có một vế đứng riêng (*"Vì thế, chúng tôi dừng dự án."*). Chỉ tính là tell khi lặp lại trong đoạn.

### V3. Thiếu "là", "thì", "mà" ở ranh giới đề – thuyết

**Dấu hiệu:** danh ngữ dài đứng đầu câu nối thẳng vào danh ngữ khác không có *là*; mệnh đề trạng ngữ mở đầu (*Khi..., Với..., Trong trường hợp...*) nối thẳng vào mệnh đề chính không có *thì*; câu đọc lên bị dính liền không có chỗ ngắt.
**Vì sao:** tiếng Anh dùng *to be* cho quan hệ đồng nhất và dùng trật tự với dấu phẩy cho ranh giới mệnh đề. Ba từ *là / thì / mà* không có tương đương một-một trong câu nguồn nên ranh giới đề – thuyết không được đánh dấu.
**Sửa:** *"Cách xử lý đơn giản nhất tăng số worker"* → *"Cách xử lý đơn giản nhất **là** tăng số worker"*. *"Khi lưu lượng tăng đột biến, hàng đợi bị nghẽn"* → *"Khi lưu lượng tăng đột biến **thì** hàng đợi bị nghẽn"*. Thứ tự bắt buộc giảm dần: *là* bắt buộc, *thì* gần bắt buộc, *mà* tuỳ chọn. Test nhanh: đọc to, chỗ nào phổi muốn ngắt mà chữ không cho ngắt là chỗ thiếu hư từ.
**Không flag:** **tính từ làm vị ngữ thì không có *là***, *"Cô ấy đẹp"* đúng, thêm *là* là sai. Đây là bẫy hay gặp nhất. Cũng không flag ở tiêu đề, nhãn, mục lục, ô bảng.

### V4. Rụng dấu thời – thể, hoặc rắc dấu thời – thể quá đều

**Dấu hiệu:** hai chiều. (a) Đoạn kể việc đã xảy ra mà thiếu hẳn nhóm *rồi, vẫn, còn, mới, sắp, từng, chưa*. (b) Ngược lại, *đã* xuất hiện trước động từ trong câu đã có mốc thời gian tường minh; chuỗi *đã và đang*, *đã, đang và sẽ*.
**Vì sao:** tiếng Anh bắt buộc chia thì ở mọi động từ hữu định, tiếng Việt đánh dấu thể bằng phó từ tuỳ chọn và chỉ khi ngữ cảnh chưa đủ. Nhóm *rồi / vẫn / còn / mới / chưa* là chỗ rơi rụng nặng nhất vì tiếng Anh không có từ tương ứng trực tiếp, không có gì trong câu nguồn kích hoạt chúng.
**Sửa:** *"Năm 2019, công ty đã mở chi nhánh đầu tiên"* → *"Năm 2019, công ty mở chi nhánh đầu tiên"*. *"Đội chuẩn bị tài liệu bàn giao"* → *"Đội **đang** chuẩn bị tài liệu bàn giao"*. Nguyên tắc: đánh dấu ở chỗ thời gian **thay đổi**, không đánh dấu ở mọi câu. Ưu tiên bổ sung nhóm *rồi / vẫn / còn / mới / chưa* trước khi nghĩ tới *đã / đang / sẽ*; nhóm này chở sắc thái mà bản dịch máy không bao giờ có.
**Không flag:** câu không có mốc thời gian nào khác và *đã* là thứ duy nhất định vị được sự việc. Định nghĩa, thông số, mô tả chức năng phi thời gian. Đoạn đã có mốc thời gian rõ ở đầu thì các câu sau không cần lặp dấu.

### V5. Thiếu hoặc sai loại từ

**Dấu hiệu:** số đếm đứng sát danh từ chỉ vật thể cụ thể (*"ba xe"*, *"hai bàn"*); danh từ chỉ vật thể cụ thể đứng trần sau động từ khi trỏ một cá thể xác định (*"treo tranh trong phòng khách"*); dùng *cái* làm loại từ vạn năng; chồng loại từ (*"cái con mèo"*).
**Vì sao:** tiếng Anh cá thể hoá bằng mạo từ và số nhiều, tiếng Việt bằng loại từ. Model ánh xạ *a* thành *một* rồi dừng, không biết tiếng Việt còn cần *một **chiếc** xe*. Khi câu nguồn là danh từ số nhiều trần thì không có gì kích hoạt, danh từ đứng trơ.
**Sửa:** *"Anh ấy vừa mua xe mới"* → *"Anh ấy vừa mua **một chiếc** xe mới"*. Chọn theo nhóm nghĩa: *con* cho động vật và một số vật chuyển động; *chiếc* cho phương tiện, vật dụng lẻ; *bức / tấm* cho vật phẳng; *quyển / cuốn* cho sách; *ngôi* cho nhà, trường; *người / vị* cho người.
**Không flag:** danh từ trừu tượng, danh từ khối, thuật ngữ kỹ thuật (server, container, endpoint). **Chiều ngược cũng sai:** danh từ dùng ở nghĩa khái quát thì không thêm loại từ, *"Xe là phương tiện chủ yếu ở đô thị"* đúng như vậy. Danh mục, bảng biểu, tiêu đề đều lược loại từ.

### V6. Khung hỏi và khung cầu khiến không dựng theo tiếng Việt

**Dấu hiệu:** câu kết thúc bằng dấu hỏi nhưng không có từ để hỏi (*ai, gì, nào, đâu, sao, bao nhiêu*) và cũng không có khung hỏi (*có... không, đã... chưa, ... phải không, ... à, ... chứ*). Câu cầu khiến mở đầu bằng *Vui lòng* trong ngữ cảnh người nói với người. Câu cầu khiến chỉ có động từ trơ, không xưng hô, không dấu cầu khiến.
**Vì sao:** tiếng Anh hỏi bằng đảo trợ động từ, hình thức nằm ở trật tự từ. Tiếng Việt giữ nguyên trật tự và hỏi bằng khung hư từ bao quanh vị ngữ. Bỏ khung thì chỉ còn dấu chấm hỏi, câu đọc lên là câu kể có dấu hỏi. *Please* ánh xạ thành *vui lòng*, vốn là ngôn ngữ giao diện máy chứ không phải cách một người nhờ một người.
**Sửa:** *"Bạn có kế hoạch cho tuần sau?"* → *"Tuần sau anh có kế hoạch **gì chưa**?"*. *"Vui lòng gửi lại file trước 5 giờ"* → *"Anh gửi lại file cho em trước 5 giờ **nhé**"*. Cân nhắc đưa xưng hô về cuối câu (*"Báo cáo xong chưa anh?"*), vị trí rất tự nhiên trong hội thoại tiếng Việt mà model không bao giờ chọn.
**Không flag:** câu hỏi tu từ trong văn nghị luận, tiêu đề dạng câu hỏi, biểu mẫu khảo sát, giao diện phần mềm và thông báo hệ thống (*"Vui lòng nhập mật khẩu"* đúng ở đó).

## Nhóm 2: Khuôn tiếng Anh áp thẳng

### V7. "của" thừa theo khuôn "of"

**Dấu hiệu:** chuỗi *danh từ + của + danh từ* dày đặc, nhất là khi cả hai đều trừu tượng. Hai *của* lồng nhau trong một danh ngữ.
**Vì sao:** tiếng Anh bắt buộc hiển ngôn quan hệ danh từ - danh từ bằng *of* hoặc sở hữu cách. Tiếng Việt ghép trực tiếp khi quan hệ là thuộc tính hoặc phân loại, chỉ dùng *của* cho sở hữu thật.
**Sửa:** *"Hiệu suất của hệ thống phụ thuộc vào cấu hình của máy chủ"* → *"Hiệu suất hệ thống phụ thuộc cấu hình máy chủ"*. Với mỗi *của*, hỏi: quan hệ này là sở hữu hay thuộc tính? Thuộc tính, phân loại, thành phần, phạm vi thì bỏ. Sở hữu thật thì giữ (*xe của tôi*, *quyết định của ban giám đốc*). Không bao giờ để hai *của* trong cùng một danh ngữ.
**Không flag:** văn bản pháp lý giữ *của* đầy đủ để loại mơ hồ về chủ thể quyền. Trường hợp bỏ đi tạo ra chuỗi bốn năm danh từ liên tiếp không đọc nổi.

### V8. "các" và "những" rắc theo dấu số nhiều

**Dấu hiệu:** ba lần *các* trở lên trong một câu; *các* đứng trước danh từ trừu tượng hoặc danh từ khối (*các thông tin*, *các dữ liệu*, *các kiến thức*); dùng lẫn *các* và *những* cho cùng loại đối tượng.
**Vì sao:** tiếng Anh bắt buộc đánh dấu số nhiều bằng biến tố, tiếng Việt suy từ ngữ cảnh. Model ánh xạ mỗi hậu tố số nhiều thành một *các*. Thêm nữa hai từ này không đồng nghĩa: ***các*** trỏ toàn bộ một tập đã xác định, ***những*** trỏ một số cá thể chưa xác định hết.
**Sửa:** *"Các nhà nghiên cứu đã phân tích các mẫu dữ liệu và phát hiện các bất thường trong các kết quả"* → *"Nhóm nghiên cứu phân tích mẫu dữ liệu và phát hiện bất thường trong kết quả"*. Cách làm: xoá hết rồi đọc lại, chỉ trả lại ở chỗ thiếu nó câu bị hiểu thành số ít. Nhiều nhất một *các* mỗi câu.
**Không flag:** văn bản pháp quy liệt kê đối tượng áp dụng, nơi *các* đánh dấu phạm vi bắt buộc phải rõ. Cụm cố định: *các bên*, *các cấp*, *các loại*.

### V9. Cụm giới từ nặng dịch một-một

**Dấu hiệu:** mật độ cao của *thông qua, trong quá trình, với sự, dưới hình thức, dựa trên, đối với, trong bối cảnh, trên cơ sở, nhằm mục đích, tại thời điểm, trong khuôn khổ*. Chúng gần như luôn mở đầu câu và luôn có dấu phẩy theo sau, đúng khuôn cụm giới từ mở đầu tiếng Anh.
**Vì sao:** một giới từ đơn tiếng Anh (through, during, with, upon) dịch sang tiếng Việt nở ra thành cụm ba bốn âm tiết. Tiếng Việt thường không diễn đạt quan hệ đó bằng giới từ mà bằng một mệnh đề có động từ.
**Sửa:** chuyển cụm giới từ thành mệnh đề. *"Với sự hỗ trợ từ đối tác, lỗi đã được khắc phục trong hai ngày"* → *"Đối tác hỗ trợ nên chỉ hai ngày là xong"*. Rút cụm bốn âm tiết khi không chuyển được: *tại thời điểm* → *khi*; *trên cơ sở* → *theo*; *nhằm mục đích* → *để*. Lưu ý *tại* chỉ dùng cho địa điểm cụ thể: *"lỗi tại bước xác thực"* nên là *"lỗi ở bước xác thực"*.
**Không flag:** pháp quy và hợp đồng, nơi *trên cơ sở*, *trong khuôn khổ*, *đối với* là công thức có hiệu lực pháp lý. Văn doanh nghiệp mở câu bằng cụm mục đích có nội dung thật cũng bình thường: *"Nhằm nâng cao hiệu quả vận hành kho, team dev đã triển khai..."* là cách người viết báo cáo thật mở câu. **Cảnh báo:** chuyển thành mệnh đề có khi làm lộ ra là câu gốc không nêu chủ thể nào cả. Lúc đó hỏi người dùng, không bịa ra chủ thể.

### V10. "một cách + tính từ" và trật tự trạng ngữ Tây hoá

**Dấu hiệu:** chuỗi *một cách* + tính từ hai âm tiết (*một cách hiệu quả, nhanh chóng, dễ dàng, toàn diện, liền mạch, đáng kể*). Trạng ngữ thời gian chen giữa chủ ngữ và vị ngữ (*"Chúng tôi hôm qua đã gửi..."*). Trạng ngữ dồn hết về cuối làm câu nặng đuôi.
**Vì sao:** *một cách X* là ánh xạ mặc định của hậu tố *-ly*. Tiếng Việt để tính từ đứng thẳng sau động từ. Trạng ngữ thời gian và nơi chốn tiếng Việt ưa đứng đầu câu, tiếng Anh thường đặt cuối.
**Sửa:** *"Đội đã xử lý sự cố một cách nhanh chóng"* → *"Đội xử lý sự cố nhanh"*. *"Chúng tôi hôm qua đã gửi bản kế hoạch"* → *"Hôm qua chúng tôi gửi bản kế hoạch"*. Đưa trạng ngữ thời gian lên đầu còn có lợi phụ: nó tạo ra một đề, chữa luôn V13.
**Không flag:** các tính từ bắt buộc đi với *một cách*: *một cách vô thức*, *một cách có hệ thống*, *một cách máy móc*. Trạng ngữ đứng cuối vì đó là trọng tâm thông tin thật. Một lần *một cách* trong cả bài.

### V11. Khung giả chủ ngữ "Điều... là"

**Dấu hiệu:** *Điều quan trọng cần lưu ý là, Điều đáng chú ý là, Điều này có nghĩa là, Cần lưu ý rằng, Cần nhấn mạnh rằng, Có thể thấy rằng, Không thể phủ nhận rằng, Việc X là điều cần thiết*.
**Vì sao:** tiếng Anh bắt buộc có chủ ngữ nên dùng *it* rỗng để đẩy mệnh đề ra sau. Tiếng Việt không có chủ ngữ rỗng, nó nói thẳng nội dung. Khung này đứng trước một câu thường mà không thêm thông tin gì.
**Sửa:** *"Điều quan trọng cần lưu ý là hệ thống chỉ đồng bộ mỗi 15 phút. Điều này có nghĩa là số liệu có thể lệch."* → *"Hệ thống chỉ đồng bộ mỗi 15 phút, nên số liệu có thể lệch."* Bỏ khung thường bỏ được luôn cả *rằng* và câu ngắn đi rõ rệt.
**Không flag:** *Điều này có nghĩa là* đứng sau một định nghĩa kỹ thuật thật sự cần diễn giải lại. *Điều đáng chú ý là* mở đầu một dữ kiện thực sự bất ngờ so với đoạn trước.

### V12. Trạng từ nối đầu câu ở mật độ tiếng Anh

**Dấu hiệu:** đếm số câu mở đầu bằng *Hơn nữa, Ngoài ra, Bên cạnh đó, Đồng thời, Thêm vào đó, Mặt khác, Tuy nhiên, Do đó, Vì vậy, Chính vì thế, Nhìn chung, Cuối cùng*. Trên một phần ba số câu trong đoạn là dấu vết cấu trúc. Dấu hiệu tinh hơn: chúng đứng ở chỗ quan hệ giữa hai câu vốn đã hiển nhiên.
**Vì sao:** tiếng Anh liên kết đoạn chủ yếu bằng trạng từ nối đầu câu. Tiếng Việt liên kết bằng ba phương thức khác: lặp từ khoá, hư từ nằm trong lòng câu (*cũng, còn, lại, mà, thì, nên*) và trật tự.
**Sửa:** xoá trạng từ nối rồi **nhập hai câu lại**, đặt quan hệ vào bên trong bằng hư từ. *Hơn nữa / Ngoài ra* → *cũng* hoặc dấu phẩy; *Tuy nhiên / Mặt khác* → *còn, lại, nhưng, mà*; *Do đó / Vì vậy* → *nên*. Khi là tương phản cục bộ, dùng khung *"Riêng X thì..."* hoặc *"Còn X thì..."*, cách liên kết rất Việt mà model hầu như không dùng. Phần lớn trường hợp xoá đi mà không thay bằng gì là đủ.
**Không flag:** văn bản học thuật, luận văn, pháp quy, báo cáo thẩm định: ở đó mật độ cao là chuẩn thể loại. Danh sách đánh số theo trình tự (*Thứ nhất... Thứ hai...*).

### V13. Khung SVO cứng, không đưa đề lên đầu

**Dấu hiệu:** ở cấp đoạn, không cấp câu. Nếu 5 trên 6 câu mở đầu bằng một danh ngữ chỉ chủ thể hành động, đoạn đó gần như chắc chắn dịch từ SVO. Thành phần đang được bàn tới lại xuất hiện ở cuối câu sau thay vì đầu câu.
**Vì sao:** tiếng Anh gắn chặt vào trật tự chủ - vị - tân, muốn nhấn thì phải dùng bị động hoặc cấu trúc chẻ. Tiếng Việt đưa thẳng cái đang bàn lên đầu làm đề. Model bám khuôn nguồn nên câu nào cũng đúng mà đoạn đọc như văn dịch: mạch thông tin không nối được từ câu này sang câu kia.
**Sửa:** *"Tôi đã đọc cuốn sách này ba lần. Cuốn sách này rất khó hiểu ở chương cuối."* → *"Cuốn sách này tôi đọc ba lần rồi. Chương cuối vẫn khó hiểu."* Thành phần đưa lên đầu không cần là chủ ngữ ngữ pháp. **Không đảo hết mọi câu**, mục tiêu là trộn. Sau khi sửa, trong 6 câu liên tiếp không nên quá 4 câu mở đầu bằng chủ thể hành động.
**Không flag:** pháp quy, điều khoản, mô tả thuật toán, tài liệu API: trật tự cố định ở đó là cố ý để tránh mơ hồ. Đoạn tường thuật chuỗi hành động của cùng một chủ thể. Không flag câu lẻ, chỉ flag khi cả đoạn đồng dạng.

### V14. Danh ngữ trần đứng làm câu

**Dấu hiệu:** một câu hoàn chỉnh về hình thức nhưng toàn bộ chỉ là một danh ngữ, không có vị ngữ. Thường mở đầu bằng *Một..., Những..., Cách tiếp cận..., Giải pháp...* kèm chuỗi định ngữ dài.
**Vì sao:** tiếng Anh cho phép mảnh câu danh ngữ làm slogan hoặc câu chốt. Tiếng Việt chỉ chấp nhận danh ngữ trần ở tít, chú thích ảnh, nhãn. Đưa vào văn xuôi thì câu treo lơ lửng, người đọc chờ vị ngữ không tới.
**Sửa:** ba cách, theo thứ tự ưu tiên. (a) Gắn vào câu trước bằng dấu phẩy nếu đang đồng vị. (b) Thêm khung *Đây là / X là*. (c) Kéo vị từ nằm sẵn trong định ngữ ra làm vị ngữ chính. *"Một hệ thống được thiết kế để xử lý hàng triệu yêu cầu."* → *"Hệ thống này xử lý được hàng triệu yêu cầu mỗi giây."* Tránh cách thứ tư mà model hay tự chọn: thêm *chính là* hoặc *thực sự là*. Đó là thêm giọng, không phải chữa cấu trúc.
**Không flag:** tít, sapo, chú thích ảnh, nhãn nút, mục lục, ô bảng, checklist. Một mảnh câu đơn lẻ dùng để nhấn có chủ ý, chỉ flag khi có từ hai mảnh trở lên gần nhau.

## Nhóm 3: Chuỗi danh hoá

### V15. Danh hoá thừa và động từ rỗng đỡ

**Dấu hiệu:** quét theo **cụm ba tầng**, không quét lẻ. Tầng một: *việc / sự / tính / công tác / quá trình + động từ*. Tầng hai: động từ rỗng đỡ danh ngữ vừa tạo ra, *thực hiện, tiến hành, triển khai, đưa ra, mang lại, tạo ra, có sự*. Tầng ba kéo theo V16. Chồng hai động từ rỗng (*tiến hành thực hiện*) là chắc chắn. Ngưỡng tham khảo: trên 3 lần `việc|sự|tính + động từ` trên 100 âm tiết.
**Vì sao:** tiếng Anh học thuật danh hoá rất mạnh và tiếng Việt không cần, vì động từ đứng ở vị trí nào cũng được, không đổi hình thái. Khi động từ đã bị biến thành danh từ, câu cần một động từ mới để đứng vững, mà model thì luôn với tay vào cùng một nhóm động từ rỗng.
**Sửa:** *"Nhóm đã tiến hành thực hiện việc rà soát toàn bộ dữ liệu và đưa ra quyết định về việc dừng chiến dịch."* → *"Nhóm rà soát lại toàn bộ dữ liệu rồi quyết định dừng chiến dịch."* Bảng thay thế Hán-Việt ↔ thuần Việt: `references/han-viet-thuan-viet.md`. **Cấm dùng bảng đó như find-and-replace**: cột thứ ba mới là phần chịu lực.
**Không flag:** *việc* danh hoá một mệnh đề có chủ ngữ riêng (*"Việc anh ấy nghỉ ngang khiến cả nhóm bối rối"*). *việc* nghĩa đen là công việc. *sự* trong từ ghép cố định: sự thật, sự kiện, sự cố, sự nghiệp. *tính* trong thuật ngữ: tính toàn vẹn dữ liệu, tính thanh khoản. Hành chính và pháp quy: *tiến hành thanh tra*, *thực hiện nghĩa vụ thuế* là thuật ngữ đúng chuẩn.

### V16. Bị động calque "được / bị ... bởi"

**Dấu hiệu:** `được\s+\p{L}+\s+bởi` là tín hiệu rất mạnh và sạch. Cũng vậy: `bởi + danh từ chỉ tác nhân`. Chuỗi *được xem là, được coi là, được biết đến như là, được kỳ vọng sẽ*.
**Vì sao:** tiếng Anh dùng bị động để giữ chủ đề ở đầu câu. Tiếng Việt đạt cùng mục đích bằng cách đưa chủ đề lên trước rồi để câu ở dạng chủ động. Chuỗi *được... bởi* là dấu vết cơ học của giới từ *by*. Thêm nữa *được / bị* mang sắc thái đánh giá lợi hại, không phải dấu hiệu ngữ pháp thuần tuý như *be + V-ed*.
**Sửa:** *"Báo cáo được hoàn thành bởi phòng kế toán"* → *"Phòng kế toán hoàn thành báo cáo"*. *"Các lỗi được phát hiện bởi hệ thống sẽ được xử lý bởi đội kỹ thuật"* → *"Hệ thống phát hiện lỗi nào thì đội kỹ thuật xử lý lỗi đó"*.
**Không flag:** **cấm quét *được* đơn lẻ.** Phần lớn *được* không phải bị động: thụ hưởng (*được nghỉ phép*), khả năng (*làm được*, *nói được tiếng Nhật*), kết quả đứng sau động từ (*giữ được tiến độ* thuộc V1, không phải V16). *bị* mang sắc thái tiêu cực đúng chỗ (*đơn hàng bị huỷ*). Pháp quy: *"Quyết định được ban hành ngày..."* là chuẩn.

### V17. Né hệ từ: "đóng vai trò là", "sở hữu", "mang lại"

**Dấu hiệu:** *đóng vai trò là, đóng vai trò quan trọng trong, giữ vai trò, được xem như là, hoạt động như một, sở hữu* (thay cho *có*), *mang trong mình, mang đến, mang lại, thể hiện, đại diện cho, là hiện thân của, nổi bật với*. Phép thử: thay bằng *là* hoặc *có* mà câu vẫn đúng thì đó là tell.
**Vì sao:** tiếng Việt có hệ từ *là* và động từ *có* cực kỳ trung tính. Model tránh chúng vì mô hình tiếng Anh đã học tránh *is / has*, rồi chọn từ tiếng Việt đao to búa lớn nhất trong nhóm nghĩa tương đương.
**Sửa:** *"Kho Bắc Ninh đóng vai trò là trung tâm trung chuyển và sở hữu diện tích 12.000 m²"* → *"Kho Bắc Ninh là trung tâm trung chuyển, rộng 12.000 m²"*.
**Không flag:** *đóng vai trò* mô tả một chức năng thật trong hệ thống nhiều tác nhân, nơi *là* sẽ bị hiểu thành định danh. *sở hữu* khi nói về quyền tài sản thật (*công ty sở hữu 51% cổ phần*, *quyền sở hữu trí tuệ*).

### V18. Câu nhiều tầng lồng, lạm dụng "mà" và "điều này"

**Dấu hiệu:** câu trên 45 âm tiết không có dấu chấm. Từ hai *mà* quan hệ trở lên trong một câu. `, điều này + động từ` hoặc `, việc này + động từ` dùng để nối mệnh đề, tương ứng *which*. *vốn là / vốn được* chèn giữa chủ ngữ và vị ngữ. Chuỗi trạng ngữ chồng nhau trước chủ ngữ.
**Vì sao:** tiếng Việt không có đại từ quan hệ. Mệnh đề phụ tiếng Việt thường đứng độc lập thành câu riêng hoặc nối bằng liên từ tường minh. Model giữ nguyên cấu trúc lồng của tiếng Anh rồi vá bằng *mà* và *điều này*.
**Sửa:** cắt thành câu riêng. *"Hệ thống mới, vốn được xây dựng trên nền tảng đám mây mà công ty đã đầu tư từ 2024, cho phép đồng bộ tồn kho theo thời gian thực, điều này giúp giảm bán vượt tồn."* → *"Hệ thống mới chạy trên nền tảng đám mây công ty đầu tư từ năm 2024. Các cửa hàng đồng bộ tồn kho theo thời gian thực. Nhờ vậy những điểm bán đông khách không còn bán vượt tồn."*
**Không flag:** *mà* là liên từ đối lập dùng đúng (*"Rẻ mà bền"*). *mà* là tiểu từ nhấn mạnh cuối câu (*"Tôi đã nói rồi mà"*). Pháp quy và hợp đồng: câu dài nhiều mệnh đề là yêu cầu nghề nghiệp, cắt câu là đổi phạm vi điều chỉnh. Một câu dài đơn lẻ giữa các câu ngắn.

## Nhóm 4: Song ngữ

### V19. Chêm tiếng Anh sai mật độ hoặc sai kiểu

Tín hiệu **hai chiều**, hướng do cổng thể loại quyết định.

**Chiều mật độ:** ở văn công việc, chat nội bộ, LinkedIn, personal brand, marketing, IT, chêm tiếng Anh là chuẩn mực và **vắng hẳn mới là tell**. Không dân bán lẻ Việt nào viết *"chương trình giảm giá cuối mùa"* thay cho *"sale off"*; không dân IT nào viết *"triển khai lên môi trường sản xuất"* thay cho *"deploy lên prod"*. Ngược lại, ở giáo trình, đề án môn học, nghiên cứu khoa học và văn bản hành chính, chêm tiếng Anh **là lỗi register**, trừ thuật ngữ chưa có tương đương và có chú giải ở lần xuất hiện đầu.

**Chiều cách chêm**, quét được và đáng tin hơn mật độ:

| Người thật | Model |
|---|---|
| Jargon ngành, viết thường, không in nghiêng, không giải thích | In nghiêng, hoặc mở ngoặc dịch nghĩa: *"chuyển đổi số (digital transformation)"* |
| Ghép theo ngữ pháp Việt: *"fix con bug này"*, *"brief lại cho khách"*, *"chốt KPI xong chưa"* | Từ tiếng Anh đứng nguyên khối như trích dẫn |
| Chêm lộn xộn, không đều, đôi khi sai chính tả | Chêm đều đặn theo khuôn, chính tả luôn đúng |
| Giữ nguyên từ mà người trong ngành không bao giờ dịch: cloud, deploy, benchmark, brief, deadline | **Dịch sạch mọi thuật ngữ**: *"điện toán đám mây"*, *"điểm chuẩn"*, *"học máy"* ở chỗ người trong ngành luôn nói cloud, benchmark, machine learning |

Dòng cuối là tell mạnh nhất của V19, cùng cơ chế với cả họ dịch tính: model render sạch sang tiếng Việt, còn người Việt thật giữ nguyên phần tiếng Anh vì đó là cách đồng nghiệp họ nói.

Ở register công việc, chiều sửa gồm cả việc **trả thuật ngữ đã bị dịch sạch về jargon**: trong tài liệu nội bộ IT, *"đội ngũ kỹ thuật"* thường phải trở lại thành *"team dev"*, *"môi trường sản xuất"* thành *"prod"*. Chỉ đổi khi chắc chắn đó là cách giới đó gọi.

**Không flag:** người viết có chủ trương thuần Việt hoá nhất quán, nhất quán là dấu hiệu chủ ý. Văn bản viết cho người đọc ngoài ngành. **Không bao giờ tự thêm từ tiếng Anh vào** khi không chắc giới trong ngành dùng từ nào; chêm sai jargon lộ liễu hơn không chêm.

---

## Quy tắc đảo chiều: không sửa câu chỉ vì nó lặp từ

Đây là chỗ khác biệt lớn nhất giữa biên tập tiếng Việt và biên tập tiếng Anh, cũng là rủi ro over-edit lớn nhất của cả skill.

Tiếng Việt đơn lập, không có đại từ hồi chỉ tiện dụng như *it / they*, nên **lặp nguyên danh từ là phương thức liên kết chuẩn mực**. Mang ngưỡng chống lặp của tiếng Anh sang là chủ động tạo ra dịch tính. Tiếng Việt còn lặp để nhấn (*rất rất*, *đi đi lại lại*) và có cả một lớp từ láy dựa trên lặp âm.

Thứ phải cắt là **chuỗi đồng nghĩa**, không phải chuỗi lặp: *doanh nghiệp → công ty → tổ chức → đơn vị* trong bốn câu liên tiếp; *khách hàng → người mua → người tiêu dùng → họ*. Khi model cứ đổi từ, nó vô tình gợi ý rằng bốn cái tên là bốn thực thể khác nhau.

Cùng quy tắc này áp cho đại từ hồi chỉ. Tiếng Việt lược chủ ngữ tự do khi ngữ cảnh đã rõ, còn tiếng Anh bắt buộc có chủ ngữ hiển ngôn, nên model giữ nguyên mật độ *nó / chúng / điều này* của tiếng Anh. Chữa bằng cách **bỏ hẳn** hoặc **lặp lại danh từ gốc**, không bao giờ bằng từ đồng nghĩa. *"Báo cáo đã gửi hôm qua. Nó chứa số liệu quý hai. Chúng tôi đã xem xét nó và thấy rằng nó có vài chỗ sai."* → *"Báo cáo gửi hôm qua có số liệu quý hai. Chúng tôi xem lại thì thấy vài chỗ sai."*

---

# TYPOGRAPHY

**Cổng bắt buộc:** chỉ sửa typography khi có ít nhất một pattern nhóm lõi cùng xuất hiện trong văn bản. Typography đơn độc không đủ làm bằng chứng, mà sửa nó đơn độc thì chỉ thêm rủi ro.

### T1. Viết hoa kiểu marketing

**Dấu hiệu:** heading viết hoa mọi âm tiết (`## Chiến Lược Tăng Trưởng Và Mở Rộng Thị Trường`); viết hoa cả liên từ và giới từ giữa tiêu đề; viết hoa mọi âm tiết của tên đơn vị (*Ban Giám Đốc*, *Bộ Giáo Dục Và Đào Tạo*); viết hoa danh từ chung giữa câu để nhấn.
**Vì sao:** tiếng Việt **không có** quy ước Title Case. Quy tắc viết hoa tiếng Việt là viết hoa vì phép đặt câu và viết hoa danh từ riêng, hết. Đây là calque trực tiếp và là tell **mạnh hơn** ở tiếng Việt so với tiếng Anh, vì không nhà xuất bản Việt nào viết như vậy.
**Sửa:** hạ về chữ thường trừ chữ đầu và danh từ riêng. Với tên cơ quan tổ chức, chuẩn đối chiếu là NĐ 30/2020/NĐ-CP Phụ lục II: viết hoa chữ cái đầu của **từ** có nghĩa cấu thành tên riêng, không phải mỗi âm tiết, *Bộ Giáo dục và Đào tạo*, *Ban Giám đốc*, *Phòng Kinh doanh*.
**Không flag:** tên thương hiệu và mã dự án có quy ước riêng (YODY, VinFast). Viết tắt (TP.HCM, KPI, ERP). Tên riêng nhiều âm tiết đều có nghĩa riêng (*Bộ Công Thương*). Trích dẫn nguyên văn.

### T2. Em dash và gạch ngang chú thích giữa câu

**Dấu hiệu:** ký tự `—` (U+2014) ở bất kỳ đâu. Gạch ngang dùng làm dấu chú thích chèn giữa câu theo kiểu tiếng Anh. Gạch nối `-` có khoảng trắng hai bên dùng như gạch ngang. Hai gạch nối liền `--`.
**Vì sao:** `—` không thuộc quy ước typography tiếng Việt ở bất kỳ chức năng nào. Gạch ngang chú thích giữa câu thì có tồn tại nhưng thưa; khi nó xuất hiện ở mật độ như văn xuôi tiếng Anh thì đó là dấu vết khuôn.
**Sửa:** thay bằng dấu phẩy, dấu hai chấm, dấu ngoặc đơn, hoặc tách câu. *"Hệ thống mới, vốn được đầu tư từ 2024, đã giúp giảm sai lệch."* → *"Hệ thống mới, đầu tư từ năm 2024, đã giúp giảm sai lệch."*
**Không flag** (đây là chỗ khác hẳn bản tiếng Anh): `–` (en dash) là **gạch ngang chuẩn của tiếng Việt** và có bốn chức năng hợp lệ, tất cả đều giữ nguyên: mở lời thoại đầu dòng, mở đầu mục liệt kê, nối cặp tên riêng (*quan hệ Việt – Trung*, *tuyến Hà Nội – Lào Cai*), nối khoảng (*quý I – quý II*, *2020 – 2025*). Gạch nối không khoảng trắng trong phiên âm (*Lê-nin*, *vắc-xin*) và mã số. Cấm en dash sẽ phá địa danh và mọi lời thoại, đó là hỏng nội dung, không phải hỏng phong cách.

### T3. Ngoặc kép không nhất quán

**Dấu hiệu:** trộn `" "` cong và `" "` thẳng trong cùng một tài liệu. Ngoặc `«...»` hoặc `„..."` xuất hiện lẻ tẻ giữa văn bản Việt hiện đại.
**Vì sao:** bản thân ngoặc cong không nói lên gì: Word, Google Docs và macOS đều tự bo cong, mà đây lại là công cụ soạn thảo mặc định ở Việt Nam. Thứ đáng ngờ là **sự trộn lẫn**, vì nó cho thấy các đoạn đến từ nguồn khác nhau.
**Sửa:** thống nhất về một kiểu, giữ kiểu đang chiếm đa số trong văn bản. **Không ép về ngoặc thẳng**, đây là chỗ đảo hành vi so với bản tiếng Anh.
**Không flag:** toàn văn bản nhất quán một kiểu, dù cong hay thẳng. `«...»` trong bản dịch từ tiếng Pháp hoặc Nga. Ngoặc lồng. Code, JSON, chuỗi kỹ thuật.

### T4. Dấu phẩy Oxford và dấu chấm phẩy nối mệnh đề

**Dấu hiệu:** cùng một regex `,\s+và\s` bắt hai lỗi khác nhau, phải phân biệt trước khi sửa. (a) **Oxford comma**: dấu phẩy trước *và* ở phần tử cuối một liệt kê. (b) **Comma-and nối mệnh đề**: dấu phẩy trước *và* nối hai mệnh đề độc lập, ánh xạ của `, and` tiếng Anh. Loại (b) khó thấy hơn và thường nhiều hơn loại (a). Cũng quét dấu chấm phẩy nối hai mệnh đề độc lập kiểu Anh.
**Vì sao:** quy ước liệt kê tiếng Việt là `A, B và C`, không có Oxford comma. Với loại (b), tiếng Anh nối mệnh đề bằng `, and` còn tiếng Việt nối bằng hư từ mang quan hệ (*mà, nên, còn, rồi*) hoặc tách hẳn câu. Dùng *và* ở đó là bỏ trống quan hệ logic, câu mất một tầng nghĩa.
**Sửa:** loại (a) bỏ dấu phẩy: *"báo cáo tài chính, kế hoạch nhân sự, và lịch triển khai"* → *"báo cáo tài chính, kế hoạch nhân sự và lịch triển khai"*. Loại (b) thay *và* bằng hư từ đúng quan hệ: nhân quả dùng *nên* (*"viết lại chứ không phải chữa, nên nguy cơ bịa tăng vọt"*); tương phản hoặc bổ sung nghịch dùng *mà* (*"đó là văn khô, mà văn khô không phải lỗi"*); đối lập cục bộ dùng *còn... thì* (*"phân tầng bằng hư từ, còn bôi đậm thì rất tiết kiệm"*); nối tiếp dùng *rồi*. Dấu chấm phẩy nối mệnh đề xử lý cùng cách.
**Không flag:** phần tử liệt kê tự nó chứa *và*, khi đó dấu phẩy trước *và* cuối là cần thiết để phân định. `;` trong pháp quy ngăn các điểm a, b, c. `;` trong code, URL, CSS.

### T5. Lạm dụng định dạng markdown

**Dấu hiệu:** ba nét riêng của tiếng Việt, ngoài các biểu hiện chung. (a) In đậm rơi vào danh ngữ Hán-Việt trừu tượng (`**tối ưu hoá quy trình**`, `**chuyển đổi số toàn diện**`) thay vì vào con số hay hạn chót. (b) Bullet header lặp lại chính nó: `- **Hiệu quả vận hành:** Hiệu quả vận hành được cải thiện...`. (c) Bộ heading là danh ngữ Hán-Việt hai âm tiết xếp đối xứng: Tổng quan / Hiện trạng / Giải pháp / Kết luận.
**Vì sao:** model dùng định dạng để bù cho việc câu chữ không tự phân tầng thông tin. Người Việt viết prose thật phân tầng bằng hư từ và trật tự câu, còn bôi đậm thì rất tiết kiệm, thường là vào con số, hạn chót, tên người chịu trách nhiệm.
**Sửa:** chuyển bullet có header thành văn xuôi. Bỏ bôi đậm khỏi danh ngữ trừu tượng.
**Không flag:** README, changelog, đặc tả kỹ thuật, SOP, tài liệu tham chiếu: bullet có header là định dạng đúng ở đó. Slide và báo cáo lãnh đạo. Bôi đậm một con số giữa đoạn dài. Bảng biểu.

### T6. Emoji

**Dấu hiệu:** emoji trang trí đầu heading hoặc đầu bullet.
**Vì sao:** không phụ thuộc ngôn ngữ, giữ nguyên như bản tiếng Anh.
**Sửa:** bỏ emoji, giữ nội dung.
**Không flag:** tin nhắn, mạng xã hội, nội dung nội bộ có văn hoá dùng emoji. Emoji mang thông tin thật (trạng thái trong bảng, ký hiệu quy ước).

---

# Nhận diện: cái gì KHÔNG được sửa

## Dấu hiệu người Việt thật viết: bất khả xâm phạm

Thấy những thứ này thì nghiêng về để nguyên. Chúng là bằng chứng có người thật đằng sau, mà over-edit thì xoá đúng cái làm nên văn bản. Xếp theo độ mạnh:

1. **Giọng vùng miền và từ địa phương.** *Mắc quá, chi rứa, nghen, hen, ni, nớ, bây, tau.* Người Bắc viết *bát* và *cốc*, người Nam viết *chén* và *ly*. Model chuẩn hoá về giọng Bắc trung tính, nên một từ Nam Bộ hay Trung Bộ lọt trong câu là dấu vân tay.
2. **Tiếng lóng gắn năm cụ thể.** Lóng mạng Việt đổi rất nhanh và model luôn trễ ít nhất một năm. Một từ lóng đúng thời điểm gần như không thể bịa.
3. **Xưng hô mang quan hệ thật.** *Anh Tuấn bên kho, chị kế toán, bác bảo vệ tầng một, sếp cũ của em.* Đại từ tiếng Việt mã hoá quan hệ xã hội cụ thể mà model không có thông tin để bịa. **Đây là chỗ dễ over-edit nhất**: xoá *bên mình* khỏi bài của một chủ shop là xoá luôn danh tính người viết.
4. **Chi tiết cụ thể khó bịa.** Giờ lẻ, tiền lẻ, tên đường, tên quán, tên file (*bao_cao_final_v7*), biển số.
5. **Câu lệch chuẩn có chủ ý.** *"Hỏi lại lần nữa. Vẫn im. Thôi."*
6. **Mâu thuẫn nội tại chưa gỡ.** *"Nói vậy chứ tôi vẫn thấy gợn, mà không chỉ ra được gợn ở đâu."* Model luôn chốt được kết luận sạch.
7. **Tự sửa mình giữa dòng.** *"Khoảng ba tháng, à không, bốn tháng."*
8. **Tiếng Anh chen theo thói quen ngành**, viết thường, lộn xộn, đôi khi sai chính tả. Xem V19.
9. **Độ dài đoạn không đều.** Một đoạn mười dòng rồi một đoạn hai chữ.
10. **Biến thể gõ tay.** *ko*, *dc*, *vs* nghĩa là *với*, thiếu dấu ở vài từ. Chỉ chuẩn hoá khi văn bản đòi hỏi chuẩn xuất bản.

## Tín hiệu chạy ngược chiều

**Khoảng trắng trước dấu câu là bằng chứng NGƯỜI THẬT VIẾT, không phải tell AI.** Model gần như không sinh lỗi này; người gõ nhanh, gõ trên điện thoại, hoặc quen typography Pháp thì có. Nếu xếp nó vào nhóm tell, bạn sẽ vừa kết luận ngược vừa sửa mất bằng chứng người viết. Chỉ sửa khi người dùng yêu cầu soát chính tả.

## Loại khỏi skill: không phải tell, đừng đụng vào

**Dấu thanh kiểu cũ và kiểu mới** (*hòa / hoà*, *thủy / thuỷ*) và **quy tắc i/y** (*kỹ / kĩ*, *tỷ / tỉ*, *lý / lí*). QĐ 1989/QĐ-BGDĐT 2018 Điều 8 và Điều 9 chỉ áp cho chương trình và sách giáo khoa phổ thông; báo chí, doanh nghiệp và pháp quy dùng kiểu còn lại áp đảo. Đây là tranh chấp chuẩn mực giữa hai giới, không liên quan gì tới AI. Thêm nữa Điều 9.2 loại trừ tên riêng (*Nguyễn Vỹ*, *Thy Ngọc*), nên mọi quy tắc i/y tự động đều có nguy cơ sửa sai tên người.

Chỉ giữ lại dưới dạng **kiểm tra nhất quán nội bộ trong một văn bản**. Nguyên tắc: nhất quán nội bộ, không áp chuẩn ngoài. Một người viết *kỹ thuật* và *tỷ lệ* suốt hai mươi năm mà bị sửa thành *kĩ thuật* và *tỉ lệ* thì skill vừa làm văn bản của họ trông giống văn bản máy hơn, đúng ngược mục tiêu.

## Quy tắc cụm

Không kết luận từ một dấu hiệu lẻ. Gần như mọi cụm trong skill này đều có thể xuất hiện hợp lệ một lần. Chỉ kết luận khi thấy **chùm ba bốn dấu hiệu trong cùng một đoạn**, cộng với sự vắng mặt hoàn toàn của các dấu hiệu người viết ở trên.

## Phân biệt "cụt vì dịch máy" với "ngắn gọn có chủ ý"

Rất nhiều người Việt chủ động viết ngắn và cộc, nhất là dân kỹ thuật và dân vận hành. Nhồi hư từ vào văn của họ cho ra kết quả tệ hơn bản gốc: một loại giả mới, thứ văn giả dân dã, cố tỏ ra tự nhiên.

**Tiêu chí mạnh nhất: xét cái gì bị bỏ.** Người viết tối giản có chủ ý bỏ **từ thừa**: trạng từ nhấn mạnh, tính từ trang trí, cụm rào đón, câu dẫn nhập. Họ không bao giờ bỏ hư từ, vì bỏ hư từ thì chính họ đọc lại cũng thấy hẫng. Dịch máy bỏ **từ chức năng**: *là, thì, được, nên, rồi*, loại từ, tiểu từ.

**Tiêu chí phụ: tính nhất quán.** Người viết cộc cắt **có hệ thống**: cùng một kiểu cấu trúc thì cắt cùng một kiểu, xuyên suốt. Dịch máy rụng hư từ **ngẫu nhiên**: cùng một cấu trúc, chỗ có chỗ không, trong cùng một đoạn. Sự bất nhất này là chữ ký của lỗi dịch.

## Mật độ khi sửa: phanh chống nhồi

- Hư từ nối trong lòng câu (*thì, mà, là, nên, cũng, còn, lại*): trung bình 1–2 mỗi câu. Trên 3 là nhồi.
- Tiểu từ tình thái cuối câu: 1 trên 3–5 câu ở văn hội thoại. **0 ở văn trang trọng.**
- Trạng từ nối đầu câu: nhiều nhất 1 trên 5–6 câu.
- *các* và *những*: nhiều nhất 1 mỗi câu.
- Loại từ: chỉ với danh từ chỉ vật thể cụ thể đang được cá thể hoá.

---

## Chế độ gọi

**Văn bản dán vào (mặc định).** Trả về bản nháp, vài gạch đầu dòng về chỗ còn lộ dấu vết dịch và bản cuối.

**Chế độ file.** Người dùng trỏ vào một file. Đọc, chạy vòng lặp bên trong, ghi đè file bằng bản cuối. Chỉ sửa phần văn xuôi: để nguyên khối code, frontmatter, dữ liệu, đích liên kết. Trong hội thoại chỉ báo cáo tóm tắt, không dán lại toàn bộ.

**Chế độ nhúng.** Một tác vụ khác dùng skill này như một bước. Chạy vòng lặp bên trong, chỉ xuất bản cuối. Không nháp, không phân tích, không tóm tắt.

## Vòng phản hồi

Khi người dùng sửa lại bản rewrite của bạn, bản của họ là bản vàng. So hai bản và gọi tên khác biệt: pattern nào bắn sai, pattern nào bắn sót, guard nào thiếu. Ghi một entry vào `calibration/LOG.md` theo giao thức trong `AGENTS.md`, rồi mới đề xuất sửa skill nếu đủ ngưỡng. Sở thích cá nhân của người dùng đi vào voice memory, không đi vào skill. Đừng sửa skill giữa phiên đang làm văn bản; tách thành việc riêng.

## Nền tảng bằng chứng

Không tồn tại nghiên cứu định lượng nào về dấu hiệu văn bản AI trong tiếng Việt ở cấp từ vựng hay cú pháp. Các công trình hiện có về phát hiện văn bản AI tiếng Việt chỉ dùng đặc trưng phân bố xác suất, không liệt kê pattern ngôn ngữ học nào.

Khoảng một phần ba pattern trong skill này có nguồn dẫn được; phần còn lại là **suy luận từ cơ chế sinh văn bản**, đối chiếu ngữ pháp Anh – Việt. Nguồn quy phạm chắc chắn nhất nằm ở nhóm typography, mà phần lớn lại dùng để **loại bỏ** quy tắc khỏi skill chứ không phải để thêm vào.

Mọi ngưỡng số trong skill này (mật độ danh hoá, tỉ lệ câu mở bằng trạng từ nối, mật độ tiểu từ) là **chưa hiệu chuẩn trên corpus**. Dùng làm phanh, đừng dùng làm bằng chứng.

Danh sách nguồn đầy đủ kèm phân hạng nằm ở `README.md`.
