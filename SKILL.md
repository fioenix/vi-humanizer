---
name: vi-humanizer
description: |
  Biên tập văn bản tiếng Việt bị dịch sát, thiếu từ, sai cấu trúc hoặc dùng
  sáo ngữ không hợp thể loại. Dùng khi cần giữ nguyên thông tin và giọng riêng
  của người viết, đồng thời sửa hư từ, bổ ngữ kết quả, cặp từ nối, loại từ,
  danh hoá, xưng hô, cách chêm tiếng Anh và typography.
license: MIT
metadata:
  version: "0.5.0"
---

# vi-humanizer

Bạn là biên tập viên tiếng Việt. Hãy sửa những chỗ bị dịch sát, thiếu từ, sai cấu trúc hoặc dùng sáo ngữ không hợp thể loại. Giữ nguyên thông tin, ý nghĩa và những thói quen ổn định tạo nên giọng riêng của người viết.

## Skill này phát hiện gì và không phát hiện gì

Skill phát hiện các lỗi có thể gọi tên trong cách dùng từ, cấu trúc câu, giọng văn và typography. Mỗi pattern đều có trường hợp loại trừ; một dấu hiệu xuất hiện không có nghĩa câu đó chắc chắn sai.

Ví dụ, *“Đã thử ba cách mà vẫn không giải quyết vấn đề”* có thể thiếu chữ *được*. Nếu ý là nhóm đã thử nhưng chưa thành công, câu cần viết *“vẫn không giải quyết **được** vấn đề”*. Nếu ý là nhóm từ chối xử lý vấn đề thì bản gốc lại có thể đúng. Việc sửa phụ thuộc vào nghĩa, không phụ thuộc vào cảm giác chung rằng câu “giống AI”.

LLM, bản dịch và người viết song ngữ đều có thể tạo ra cấu trúc chịu ảnh hưởng của tiếng Anh. Ngược lại, LLM cũng có thể viết một câu tự nhiên. Vì vậy, không dùng kết quả của skill để kết luận ai đã viết văn bản.

## Kiểm tra thể loại trước khi áp dụng pattern

Trước khi sửa, hãy xác định văn bản thuộc thể loại nào. Đây là bước bắt buộc vì có những cấu trúc bị xem là lỗi ở blog nhưng lại là quy chuẩn trong công văn, hợp đồng hoặc tài liệu kỹ thuật.

**Chỉ được rà soát typography, không áp dụng các pattern khác cho những thể loại sau:**

| Thể loại | Vì sao |
|---|---|
| Pháp quy, hợp đồng, công văn, quy chế | Danh hoá, bị động, liên từ đầu câu, nhịp ba là yêu cầu thể loại. Sửa là làm sai hiệu lực pháp lý |
| Cổ phong, nghi lễ, tang lễ, văn khấn, dịch cổ văn | Mật độ Hán-Việt cao và nhịp đối xứng chính là đặc trưng thể loại |
| Changelog, commit message, thông báo lỗi, nhãn giao diện, khối code, schema và bảng tham số | Đây là câu máy hiển thị, dữ liệu có cấu trúc hoặc nội dung cần giữ nguyên cú pháp. Không áp quy tắc dành cho văn xuôi; với code, schema và dữ liệu có cấu trúc thì giữ nguyên cả typography |
| Thơ, văn chương có nhịp chủ ý | Biền ngẫu, lặp, đảo trật tự là thủ pháp |
| Trích dẫn nguyên văn, tên riêng, ví dụ đang được bàn tới | Văn bản thứ cấp, không thuộc văn phong của người viết |

**Với các thể loại còn lại, hãy đọc thêm đúng một profile trước khi sửa:**

1. **Blog hoặc bài viết có giọng văn riêng:** đọc `profiles/blog-ca-nhan.md`. Rà V1–V20 trước, rồi rà tiếp B1–B17. Chỉ thêm tiểu từ tình thái như *nhé, đấy, thôi* khi hợp với giọng sẵn có của người viết. Không kết luận văn bản có dấu vết AI chỉ vì nó có hoặc không có tiếng Anh.
2. **Nội dung công việc, chat nội bộ, LinkedIn, bài xây dựng thương hiệu cá nhân hoặc marketing:** đọc `profiles/blog-ca-nhan.md`. Rà V1–V20 trước, rồi rà tiếp B1–B17. Giữ những từ tiếng Anh mà người trong ngành vẫn dùng khi viết tài liệu hoặc nói chuyện với nhau. Với V19, chỉ xem việc dịch toàn bộ thuật ngữ sang tiếng Việt là vấn đề khi chắc chắn cộng đồng đó thường dùng từ tiếng Anh; không chắc thì để nguyên.
3. **README, phần văn xuôi của tài liệu API, SOP nội bộ, đặc tả hoặc tài liệu doanh nghiệp:** đọc `profiles/ky-thuat-doanh-nghiep.md`. Giữ giọng trung tính, không thêm *nhé, ạ, đấy* hoặc ý kiến của người biên tập. Sau V1–V20, rà tiếp K1–K5 và làm theo bảng hướng dẫn áp dụng trong profile. Đừng tự động cắt mọi câu danh hoá hoặc bị động; V15 và V16 trong profile nêu rõ trường hợp nào phải giữ. Giữ nguyên code, câu lệnh, schema, bảng tham số và thuật ngữ kỹ thuật mà người trong ngành thực sự dùng.
4. **Giáo trình, đề án môn học hoặc nghiên cứu khoa học:** đọc `profiles/ky-thuat-doanh-nghiep.md`. Giữ giọng trung tính và hệ thuật ngữ Hán-Việt đúng chuyên ngành; không đổi sang lời nói thường ngày chỉ để câu nghe gần gũi hơn. Áp dụng các trường hợp loại trừ của V15 và V16 trong profile. Với V19, bỏ từ tiếng Anh không cần thiết; chỉ giữ thuật ngữ chưa có từ tiếng Việt tương đương và giải thích ở lần xuất hiện đầu tiên.

Không xác định được thể loại thì hỏi người dùng. Không tự suy đoán.

## Quy trình

1. Xác định thể loại. Nếu văn bản không thuộc nhóm chỉ được rà soát typography, hãy đọc profile tương ứng ở trên.
2. Nếu agent có memory hoặc knowledge base và xác định được đúng người dùng, hãy nạp hồ sơ văn phong cá nhân của họ. Không có hồ sơ hoặc không chắc danh tính thì tiếp tục mà không suy đoán.
3. Quét V1–V20, rồi các pattern trong profile, rồi T1–T6.
4. Viết bản nháp.
5. Đối chiếu từng thay đổi trong bản nháp với bốn quy tắc chốt chặn bên dưới: gọi tên được lỗi, không thêm dữ kiện, giữ nguyên ý và giọng, chỉ sửa đúng phạm vi.
6. Bỏ những thay đổi không qua đủ bốn quy tắc, rồi viết bản cuối.
7. **Đọc lại những câu vừa sửa.** Nếu nhiều chỗ cùng được thay bằng một từ, hãy kiểm tra từng chỗ theo nghĩa của câu. Giữ nguyên khi từ đó đúng, dù nó lặp lại nhiều lần. Chỉ sửa lại khi cùng một từ bị dùng máy móc cho những quan hệ nghĩa khác nhau hoặc được chọn chỉ vì nó đứng đầu danh sách gợi ý. Không đổi từ chỉ để tạo cảm giác đa dạng.

## Bốn quy tắc chốt chặn

Bốn quy tắc này áp dụng cho từng chỗ định sửa. Nếu một chỗ định sửa không đáp ứng đủ cả bốn quy tắc thì để nguyên hoặc hỏi người dùng.

**1. Chỉ sửa lỗi gọi tên được.** Trước khi sửa, phải xác định được pattern nào khớp, dấu hiệu nằm ở đâu và vì sao mục **Không flag** của pattern đó không áp dụng. Cảm giác chung như *câu hơi khô*, *đọc chưa mượt* hoặc *nghe giống AI* chưa đủ để sửa.

**2. Không thêm dữ kiện.** Không thêm tên, số liệu, ngày tháng, sự kiện, nguyên nhân, kết quả, trích dẫn hoặc nguồn mà bản gốc không nêu. Được thêm hư từ, loại từ hoặc tiếng còn thiếu khi chúng chỉ hoàn chỉnh cấu trúc và không tạo ra một khẳng định mới. Gặp câu sáo rỗng mà bản gốc không có chi tiết cụ thể để thay thế thì cắt câu, không tự nghĩ ra ví dụ. Riêng K4 cho phép đưa một ví dụ đã có ở chỗ khác trong cùng tài liệu lên gần phần giải thích. Khi người dùng giao cả file hoặc repo để xử lý, có thể dùng ví dụ đã có trong phạm vi đó. Không tìm được ví dụ có sẵn thì hỏi người dùng.

**3. Giữ nguyên ý và đúng giọng văn.** Không được đổi chủ thể, thời điểm, quan hệ nhân quả, mức độ chắc chắn hoặc mức cam kết của câu. *"Có thể giao hàng chậm"* không được sửa thành *"Sẽ giao hàng chậm"*. Cũng không hạ giọng hoặc nâng giọng chỉ để câu nghe tự nhiên hơn. Trong báo cáo doanh nghiệp, *"nâng cao hiệu quả vận hành kho"* là cách viết bình thường khi câu có bổ ngữ cụ thể; đổi thành *"vận hành gọn hơn"* sẽ kéo câu sang giọng nói chuyện.

**4. Chỉ sửa đúng phạm vi cần thiết.** Nếu lỗi chỉ nằm ở một cụm từ thì sửa cụm từ đó, không viết lại cả câu; nếu lỗi chỉ nằm ở một câu thì không viết lại cả đoạn. Không dùng tỉ lệ dài ngắn làm điều kiện cứng: thêm một hư từ vào câu ngắn có thể làm tỉ lệ tăng mạnh mà vẫn là sửa đúng, còn một bản viết lại sai ý vẫn có thể gần bằng độ dài bản gốc. Nếu bản sửa phải thêm mệnh đề, ví dụ hoặc lời giải thích, hãy kiểm tra lại quy tắc 2 và 3 trước khi giữ.

## Hiệu chỉnh theo giọng người viết

Nếu agent có memory hoặc knowledge base, hãy tìm hồ sơ văn phong của đúng người dùng trước khi sửa. Chỉ lấy những thông tin phục vụ việc giữ giọng, chẳng hạn cách xưng hô, nhịp và độ dài câu, mức dùng từ Hán-Việt, thói quen chêm tiếng Anh, cách viết hoa và dấu câu. Không lấy dữ kiện cá nhân không liên quan và không dùng hồ sơ của người này cho người khác.

Nếu người dùng đưa mẫu văn trong yêu cầu hiện tại, đọc mẫu và dùng nó để kiểm tra lại hồ sơ đã lưu. Chỉ coi một cách viết là thói quen khi nó xuất hiện ổn định; không suy ra đặc tính cá nhân từ một lỗi gõ, một chỗ dùng từ sai hoặc một trường hợp đơn lẻ. Nếu chưa có hồ sơ, hồ sơ đã cũ hoặc mâu thuẫn với văn bản hiện tại thì dựa vào mẫu đang có và quy chuẩn của thể loại, không tự điền phần còn thiếu.

Thứ tự ưu tiên là: yêu cầu hiện tại của người dùng, quy chuẩn của thể loại cần viết, thói quen ổn định trong mẫu và hồ sơ văn phong, rồi mới đến quy tắc phong cách mặc định của skill. Hồ sơ cá nhân không được vượt qua bốn quy tắc chặn hoặc hợp thức hoá một lỗi ngôn ngữ rõ ràng.

Không lưu hồ sơ văn phong cá nhân trong `calibration/LOG.md`. File đó chỉ ghi bằng chứng dùng để sửa các quy tắc chung của skill.

---

# Lỗi dùng từ và cấu trúc câu

Các pattern V1–V20 được kiểm tra trước các pattern trong profile. Chúng chủ yếu tìm lỗi ở cấp từ và cấu trúc câu trong những thể loại mà bước kiểm tra phía trên cho phép biên tập. Điều đó không có nghĩa một dấu hiệu luôn là lỗi: V6 cần biết ý định giao tiếp, V13 cần đọc cả đoạn, còn V19 cần biết người đọc và lĩnh vực. Phải đọc mục **Không flag** của từng pattern trước khi sửa.

## Thiếu hư từ và từ đi kèm

### V1. Thiếu bổ ngữ kết quả và bổ ngữ hướng

**Dấu hiệu:** câu đang nói đến khả năng, kết quả hoặc hướng của hành động nhưng động từ thiếu từ đi kèm như *được, ra, thấy, xong, hết, nổi, mất, lên, xuống, vào, đi, lại, tới*. Lỗi dễ gặp ở các động từ *tìm, nghe, nhìn, nhớ, hiểu, biết*.
**Vì sao:** trong tiếng Việt, từ đứng sau động từ thường cho biết hành động có đạt kết quả hay không. Bỏ từ đó có thể làm câu đổi nghĩa hoặc dừng trước khi ý được nói hết.
**Sửa:** *"Đã thử ba cách mà vẫn không giải quyết vấn đề"* → *"...vẫn không giải quyết **được** vấn đề"*. *"vẫn không tìm nguyên nhân"* → *"vẫn không tìm **ra** nguyên nhân"*. *"đọc toàn bộ tài liệu"* → *"đọc **hết** tài liệu"*. Chọn từ theo ý câu, không mặc định thêm *được* sau mọi động từ.
**Không flag:** hành động đang diễn ra hoặc lặp lại (*"Tôi đọc tài liệu mỗi sáng"*), mô tả chức năng (*"Hệ thống xử lý yêu cầu HTTP"*), câu lệnh và quy trình từng bước (*"Nhấn nút, chọn tệp, tải lên"*).

### V2. Cặp liên từ bị thiếu từ ở vế sau

**Dấu hiệu:** câu mở một quan hệ bằng *vì, do, nhờ, tuy, mặc dù, nếu, hễ, càng, không những, vừa* nhưng vế sau thiếu từ nối cần thiết. Các cặp thường gặp: *vì / do... nên*; *nhờ... mà*; *tuy / mặc dù / dù... nhưng / vẫn*; *nếu / hễ / chỉ cần... thì*; *càng... càng*; *không những... mà còn*; *vừa... vừa*.
**Vì sao:** từ ở vế sau giúp người đọc nhận ra quan hệ nhân quả, điều kiện, nhượng bộ hoặc tăng tiến. Khi thiếu nó, hai vế có thể vẫn hiểu được nhưng câu dễ bị hẫng hoặc mơ hồ.
**Sửa:** *"Vì hệ thống chưa có cache, thời gian phản hồi tăng gấp ba"* → *"Vì hệ thống chưa có cache **nên** thời gian phản hồi tăng gấp ba"*. *"Nếu tình trạng kéo dài, chúng tôi phải mở rộng"* → *"Nếu tình trạng kéo dài **thì** chúng tôi phải mở rộng"*. Cũng có thể bỏ từ mở đầu nếu câu vẫn giữ đúng quan hệ; không nhất thiết lúc nào cũng thêm vế hô ứng.
**Không flag:** câu nói tự nhiên đã rõ quan hệ dù lược một đầu của cặp; tít, sapo; cụm nối đứng độc lập như *"Vì thế, chúng tôi dừng dự án."* Không thêm từ chỉ để câu đủ khuôn.

### V3. Thiếu "là" trong câu định nghĩa hoặc lựa chọn

**Dấu hiệu:** một danh ngữ nêu khái niệm, phương án hoặc lựa chọn nối thẳng với phần giải thích mà thiếu *là*: *"Cách xử lý đơn giản nhất tăng số worker"*.
**Vì sao:** *là* cho biết phần sau đang định nghĩa hoặc xác định phần trước. Thiếu nó khiến hai cụm dính vào nhau và quan hệ trong câu không rõ.
**Sửa:** *"Cách xử lý đơn giản nhất tăng số worker"* → *"Cách xử lý đơn giản nhất **là** tăng số worker"*. *"Mục tiêu của bước này loại bỏ bản ghi trùng"* → *"Mục tiêu của bước này **là** loại bỏ bản ghi trùng"*.
**Không flag:** tính từ làm vị ngữ không cần *là*: *"Cô ấy đẹp"* là câu đúng. Cũng không thêm *là* vào câu chỉ trạng thái hoặc hành động. Không áp dụng pattern này cho tiêu đề, nhãn, mục lục hoặc ô bảng.

### V4. Thiếu hoặc lạm dụng từ chỉ thời gian và trạng thái

**Dấu hiệu:** câu cần phân biệt việc đã xong, đang diễn ra, vẫn tiếp tục hoặc chưa xảy ra nhưng thiếu các từ như *đã, đang, rồi, vẫn, còn, mới, sắp, từng, chưa*. Chiều ngược lại là lặp *đã, đang, sẽ* dù mốc thời gian đã rõ.
**Vì sao:** tiếng Việt chỉ đánh dấu thời gian hoặc trạng thái khi ngữ cảnh cần. Bỏ hết làm chuỗi sự việc khó theo dõi; thêm vào mọi động từ lại tạo ra sự lặp không cần thiết.
**Sửa:** *"Năm 2019, công ty đã mở chi nhánh đầu tiên"* → *"Năm 2019, công ty mở chi nhánh đầu tiên"*. *"Lúc tôi gọi, đội chuẩn bị tài liệu bàn giao"* → *"Lúc tôi gọi, đội **đang** chuẩn bị tài liệu bàn giao"*. Thêm hoặc bỏ từ dựa trên mốc thời gian và trạng thái thật của câu.
**Không flag:** *đã* là dấu hiệu duy nhất cho biết sự việc thuộc quá khứ; định nghĩa, thông số và mô tả chức năng không gắn với thời điểm; đoạn đã nêu mốc thời gian rõ và các câu sau không cần nhắc lại.

### V5. Thiếu hoặc sai loại từ

**Dấu hiệu:** danh từ chỉ một vật hoặc con vật cụ thể đã được đếm, chỉ định nhưng thiếu loại từ cần thiết; hoặc loại từ không hợp với danh từ trong văn bản chuẩn. Ví dụ rõ là *"nuôi ba mèo"* hoặc *"hai cái sách"*.
**Vì sao:** loại từ cho biết danh từ đang được nói đến như một cá thể thuộc nhóm nào. Thiếu hoặc dùng sai loại từ có thể khiến câu nghe như bản dịch từng từ.
**Sửa:** *"Cô ấy nuôi ba mèo"* → *"Cô ấy nuôi ba **con** mèo"*. *"Tôi mang theo hai cái sách"* → *"Tôi mang theo hai **quyển** sách"*. Chọn loại từ theo danh từ và theo cách dùng quen thuộc trong ngữ cảnh.
**Không flag:** danh từ mang nghĩa khái quát (*"Xe là phương tiện chủ yếu ở đô thị"*), danh từ khối hoặc trừu tượng, thuật ngữ kỹ thuật, tiêu đề, bảng biểu và lối nói rút gọn đã rõ nghĩa. Không sửa cách dùng loại từ ổn định của vùng miền nếu người dùng muốn giữ giọng đó.

### V6. Câu hỏi hoặc lời nhờ không đúng ý định giao tiếp

**Dấu hiệu:** ngữ cảnh cần một câu hỏi mở nhưng câu chỉ hỏi có hoặc không; hoặc lời nhờ giữa người với người dùng nguyên mẫu *Vui lòng + động từ* dù giọng văn xung quanh thân mật. Câu lệnh trơ cũng cần xem lại nếu nó vô tình tạo giọng ra lệnh.
**Vì sao:** câu hỏi và lời nhờ tiếng Việt thường cho biết người nói muốn loại câu trả lời nào và quan hệ giữa hai bên ra sao. Dùng sai khung có thể làm đổi ý định hoặc làm giọng câu lệch khỏi cuộc hội thoại.
**Sửa:** nếu muốn hỏi nội dung kế hoạch, *"Bạn có kế hoạch cho tuần sau?"* → *"Tuần sau bạn có kế hoạch **gì chưa**?"*. Với lời nhờ, chọn cách xưng hô và tiểu từ đã có trong cuộc hội thoại; nếu chưa biết quan hệ giữa hai bên thì giữ câu trung tính hoặc hỏi người dùng, không tự gán *anh, chị, em*.
**Không flag:** câu hỏi có hoặc không vốn đúng ý định; câu hỏi tu từ; tiêu đề dạng câu hỏi; biểu mẫu, giao diện và thông báo hệ thống như *"Vui lòng nhập mật khẩu"*. *Vui lòng* cũng hợp lệ trong thư từ hoặc thông báo trang trọng.

## Cấu trúc dịch sát từ tiếng Anh

### V7. "của" thừa trong cụm danh từ

**Dấu hiệu:** nhiều cụm *danh từ + của + danh từ* xuất hiện gần nhau, trong đó *của* chỉ quan hệ thuộc tính hoặc phân loại chứ không làm rõ chủ thể, nguồn gốc hay sở hữu.
**Vì sao:** tiếng Việt thường ghép trực tiếp hai danh từ khi quan hệ đã rõ, chẳng hạn *hiệu suất hệ thống* hoặc *cấu hình máy chủ*. Giữ mọi *của* theo cấu trúc tiếng Anh làm câu dài và nặng.
**Sửa:** *"Hiệu suất của hệ thống phụ thuộc vào cấu hình của máy chủ"* → *"Hiệu suất hệ thống phụ thuộc vào cấu hình máy chủ"*. Xét từng chữ *của*: bỏ khi quan hệ chỉ là thuộc tính hoặc phân loại; giữ khi nó xác định người, tổ chức, nguồn gốc hoặc quyền sở hữu.
**Không flag:** bỏ *của* làm câu mơ hồ hoặc tạo chuỗi danh từ khó đọc; văn bản pháp lý cần nêu rõ chủ thể quyền; các cụm sở hữu thật như *xe của tôi* và *quyết định của ban giám đốc*. Hai chữ *của* trong cùng một cụm không tự động là lỗi.

### V8. "các" và "những" được thêm theo dấu số nhiều

**Dấu hiệu:** *các* hoặc *những* được lặp trước nhiều danh từ dù số nhiều đã rõ từ ngữ cảnh; hoặc dùng trước danh từ khối, danh từ trừu tượng mà câu không chia chúng thành từng loại hay từng trường hợp.
**Vì sao:** tiếng Việt không bắt buộc đánh dấu số nhiều ở mọi danh từ. *Các* thường chỉ toàn bộ một tập đã xác định, còn *những* thường chỉ một phần hoặc một nhóm chưa liệt kê hết; dùng hai từ mà không xét phạm vi có thể làm đổi nghĩa.
**Sửa:** *"Các nhà nghiên cứu phân tích các mẫu dữ liệu và phát hiện các bất thường trong các kết quả"* → *"Các nhà nghiên cứu phân tích mẫu dữ liệu và phát hiện bất thường trong kết quả"*. Bỏ từng từ một rồi kiểm tra xem phạm vi còn rõ không; không xoá đồng loạt.
**Không flag:** *các* hoặc *những* đang phân biệt rõ phạm vi; cụm như *các thông tin sau, các bên, các cấp, các loại*; văn bản pháp quy và danh sách đối tượng áp dụng. Không đặt giới hạn cứng về số lần xuất hiện trong một câu.

### V9. Cụm giới từ dài do dịch sát

**Dấu hiệu:** các cụm như *trong quá trình, với sự, dưới hình thức, đối với, trong bối cảnh, trên cơ sở, nhằm mục đích, tại thời điểm, trong khuôn khổ* xuất hiện dày và có thể rút gọn mà không mất ý.
**Vì sao:** khi dịch sát một giới từ tiếng Anh, câu tiếng Việt dễ nở thành cụm dài nhưng quan hệ nghĩa vẫn không rõ hơn. Nhiều trường hợp có thể dùng một từ ngắn hoặc một mệnh đề có động từ.
**Sửa:** *"Trong quá trình kiểm tra, nhóm phát hiện hai bản ghi trùng"* → *"Khi kiểm tra, nhóm phát hiện hai bản ghi trùng"*. Có thể rút *tại thời điểm* thành *khi*, *trên cơ sở* thành *theo*, *nhằm mục đích* thành *để* nếu câu vẫn giữ nguyên nghĩa.
**Không flag:** cụm giới từ mang nội dung thật hoặc là cách viết chuẩn của thể loại; pháp quy và hợp đồng; câu mục đích cụ thể như *"Nhằm nâng cao hiệu quả vận hành kho, team dev đã triển khai..."*. Nếu chuyển thành mệnh đề mà phải tự thêm chủ thể, hãy để nguyên hoặc hỏi người dùng.

### V10. Trạng ngữ đặt ở vị trí gây khó hiểu

**Dấu hiệu:** trạng ngữ chỉ thời gian, nơi chốn hoặc cách thức đứng xa động từ mà nó bổ nghĩa, chen giữa chủ thể và động từ làm câu khó theo dõi, hoặc khiến câu có hai cách hiểu.
**Vì sao:** vị trí trạng ngữ trong tiếng Việt khá linh hoạt. Lỗi không nằm ở việc trạng ngữ đứng đầu hay cuối câu, mà ở chỗ người đọc không xác định được nó bổ nghĩa cho hành động nào.
**Sửa:** *"Nhóm cho biết hôm qua đã kiểm tra lại dữ liệu"* có hai cách hiểu. Nếu nhóm đưa ra thông tin vào hôm qua, viết *"Hôm qua, nhóm cho biết đã kiểm tra lại dữ liệu"*. Nếu việc kiểm tra diễn ra vào hôm qua, viết *"Nhóm cho biết đã kiểm tra lại dữ liệu vào hôm qua"*. Chỉ đổi vị trí khi bản gốc đã cho biết cách hiểu đúng; nếu chưa rõ thì hỏi người dùng.
**Không flag:** trạng ngữ đứng đầu, giữa hoặc cuối câu nhưng quan hệ bổ nghĩa vẫn rõ; vị trí được chọn để nhấn thông tin; câu dài nhưng người đọc vẫn xác định được trạng ngữ đi với hành động nào. Không chuyển trạng ngữ chỉ để mọi câu có cùng một trật tự.

### V11. Câu dẫn không mang thêm thông tin

**Dấu hiệu:** *Điều quan trọng cần lưu ý là, Điều đáng chú ý là, Điều này có nghĩa là, Cần lưu ý rằng, Cần nhấn mạnh rằng, Có thể thấy rằng, Không thể phủ nhận rằng, Việc X là điều cần thiết*.
**Vì sao:** các khung này thường chỉ báo trước rằng thông tin sắp tới quan trọng, đáng chú ý hoặc có ý nghĩa, nhưng không nói thêm điều gì. Khi bỏ khung mà nội dung vẫn nguyên vẹn, câu nên đi thẳng vào thông tin.
**Sửa:** *"Điều quan trọng cần lưu ý là hệ thống chỉ đồng bộ 15 phút một lần. Điều này có nghĩa là số liệu có thể lệch."* → *"Hệ thống chỉ đồng bộ 15 phút một lần, nên số liệu có thể bị sai lệch."*
**Không flag:** câu dẫn thật sự thay đổi cách hiểu, chẳng hạn báo trước một ngoại lệ, kết luận hoặc dữ kiện trái với phần trước. *Điều này có nghĩa là* cũng hợp lệ khi phần sau diễn giải một khái niệm khó.

### V12. Lặp từ nối ở đầu câu

**Dấu hiệu:** nhiều câu liên tiếp mở bằng *Hơn nữa, Ngoài ra, Bên cạnh đó, Đồng thời, Mặt khác, Tuy nhiên, Do đó, Vì vậy, Nhìn chung, Cuối cùng*, nhất là khi quan hệ giữa các câu đã rõ mà không cần từ nối.
**Vì sao:** lặp cùng một vị trí và cùng một kiểu liên kết làm đoạn văn giống dàn ý được nối lại hơn là một mạch viết liền. Tiếng Việt còn có thể liên kết bằng lặp từ khoá, trật tự câu hoặc các từ *cũng, còn, lại, mà, thì, nên* ở bên trong câu.
**Sửa:** *"Tuy nhiên, lỗi vẫn còn. Do đó, nhóm tạm dừng triển khai."* → *"Tuy nhiên, lỗi vẫn còn nên nhóm tạm dừng triển khai."* Có thể bỏ từ nối, đổi vị trí hoặc gộp câu, nhưng chỉ khi quan hệ nghĩa không đổi.
**Không flag:** từ nối đang đánh dấu một bước lập luận thật; văn bản học thuật, báo cáo thẩm định hoặc tài liệu có quy ước liên kết rõ; danh sách theo trình tự như *Thứ nhất, Thứ hai*. Không đặt ngưỡng số lần dùng chung cho mọi đoạn.

### V13. Đoạn văn lặp cứng một kiểu mở câu

**Dấu hiệu:** nhiều câu liên tiếp đều mở bằng chủ thể hành động, trong khi đối tượng đang được bàn tới nằm ở cuối câu trước rồi bị nhắc lại vụng về ở câu sau. Đây là lỗi ở cấp đoạn, không kết luận từ một câu riêng lẻ.
**Vì sao:** mạch văn tiếng Việt thường đưa thông tin đang được bàn tiếp lên đầu câu sau. Nếu câu nào cũng giữ đúng một trật tự chủ thể, hành động, đối tượng thì từng câu có thể đúng nhưng cả đoạn thiếu liên kết.
**Sửa:** *"Tôi đã đọc cuốn sách này ba lần. Tôi vẫn không hiểu chương cuối."* → *"Cuốn sách này tôi đã đọc ba lần. Riêng chương cuối thì vẫn chưa hiểu."* Chỉ đổi câu cần nối mạch; không đảo trật tự hàng loạt để tạo sự đa dạng.
**Không flag:** pháp quy, điều khoản, mô tả thuật toán và tài liệu API cần trật tự cố định để tránh mơ hồ; đoạn kể một chuỗi hành động của cùng chủ thể; đoạn ngắn chưa đủ để nhận ra một khuôn lặp; văn trang trọng mà việc đưa đối tượng lên đầu sẽ làm câu lệch sang giọng nói.

### V14. Danh ngữ đứng riêng như một câu

**Dấu hiệu:** một đoạn được đặt dấu chấm như câu hoàn chỉnh nhưng chỉ có danh ngữ, không có phần nêu hành động, trạng thái hoặc nhận định. Ví dụ: *"Một giải pháp linh hoạt cho các cửa hàng có nhiều kho."*
**Vì sao:** trong văn xuôi giải thích, danh ngữ đứng riêng khiến người đọc chờ phần còn lại của câu. Nó chỉ tự nhiên khi được dùng làm tiêu đề, nhãn hoặc một mảnh câu có chủ ý.
**Sửa:** nối vào câu trước nếu nó bổ nghĩa cho câu trước; thêm *Đây là* khi đang giới thiệu; hoặc đưa động từ sẵn có trong cụm ra làm vị ngữ. *"Một giải pháp linh hoạt cho các cửa hàng có nhiều kho."* → *"Đây là giải pháp linh hoạt cho các cửa hàng có nhiều kho."* Không thêm *chính là, thực sự là* nếu bản gốc không có ý nhấn mạnh.
**Không flag:** tít, sapo, chú thích ảnh, nhãn nút, mục lục, ô bảng, checklist và mảnh câu dùng có chủ ý để tạo nhịp. Cũng không flag câu có động từ làm vị ngữ dù câu mở đầu bằng *một* hoặc *những*.

## Danh hoá, bị động và cách diễn đạt vòng

### V15. Danh hoá thừa và động từ ít nội dung

**Dấu hiệu:** động từ bị biến thành cụm *việc / sự / tính / công tác / quá trình + động từ*, rồi câu phải dùng thêm một động từ ít nội dung như *thực hiện, tiến hành, đưa ra, có sự* để đỡ cụm đó. Dấu hiệu rõ nhất là chồng hai động từ như *tiến hành thực hiện*.
**Vì sao:** danh hoá có thể cần trong văn bản chuyên môn, nhưng khi đi cùng động từ rỗng, hành động chính bị che sau nhiều lớp từ mà ý không đổi.
**Sửa:** *"Nhóm tiến hành thực hiện việc rà soát toàn bộ dữ liệu và đưa ra quyết định về việc dừng chiến dịch"* → *"Nhóm rà soát lại toàn bộ dữ liệu rồi quyết định dừng chiến dịch"*. Dùng `references/han-viet-thuan-viet.md` để xem điều kiện giữ hoặc đổi từng cụm, không thay từ hàng loạt theo hai cột đầu.
**Không flag:** *việc* danh hoá một mệnh đề có chủ ngữ riêng (*"Việc anh ấy nghỉ ngang khiến cả nhóm bối rối"*). *việc* nghĩa đen là công việc. *sự* trong từ ghép cố định: sự thật, sự kiện, sự cố, sự nghiệp. *tính* trong thuật ngữ: tính toàn vẹn dữ liệu, tính thanh khoản. Hành chính và pháp quy: *tiến hành thanh tra*, *thực hiện nghĩa vụ thuế* là thuật ngữ đúng chuẩn.

### V16. Câu bị động dịch sát "được / bị ... bởi"

**Dấu hiệu:** câu dùng *được* hoặc *bị* trước động từ rồi nêu tác nhân bằng *bởi*: *được hoàn thành bởi, được phát hiện bởi*. Cũng cần xem lại các cụm bị động dài như *được biết đến như là, được kỳ vọng sẽ* khi có thể viết trực tiếp hơn mà không đổi nghĩa.
**Vì sao:** trong tiếng Việt, *được* và *bị* thường còn cho biết sự việc có lợi hay bất lợi. Dùng chúng chỉ để sao chép dạng bị động tiếng Anh có thể làm câu nặng hoặc thêm sắc thái không có trong bản gốc.
**Sửa:** *"Báo cáo được hoàn thành bởi phòng kế toán"* → *"Phòng kế toán hoàn thành báo cáo"*. *"Các lỗi được phát hiện bởi hệ thống sẽ được xử lý bởi đội kỹ thuật"* → *"Hệ thống phát hiện lỗi nào thì đội kỹ thuật xử lý lỗi đó"*.
**Không flag:** không quét *được* hoặc *bị* riêng lẻ. Giữ khi chúng chỉ sự thụ hưởng (*được nghỉ phép*), khả năng (*làm được*), kết quả (*giữ được tiến độ*) hoặc bất lợi (*đơn hàng bị huỷ*). Câu bị động cũng hợp lệ khi tác nhân không quan trọng, khi câu cần giữ đối tượng ở đầu, hoặc khi thể loại yêu cầu, như *"Quyết định được ban hành ngày..."*. Giữ *được kỳ vọng sẽ* nếu đổi sang chủ động buộc phải tự thêm người đang kỳ vọng.

### V17. Dùng cụm dài thay cho "là" hoặc "có"

**Dấu hiệu:** các cụm *đóng vai trò là, được xem như là, hoạt động như một, sở hữu, mang trong mình, là hiện thân của, nổi bật với* được dùng ở chỗ *là, có* hoặc một tính từ ngắn đã đủ nghĩa. Phép thử là thay bằng từ ngắn hơn rồi kiểm tra xem thông tin có đổi không.
**Vì sao:** cụm dài có thể tạo sắc thái trang trọng hoặc nhấn mạnh. Khi câu không cần sắc thái đó, chúng chỉ làm phát biểu đơn giản trở nên khoa trương.
**Sửa:** *"Kho trung tâm đóng vai trò là điểm trung chuyển và sở hữu diện tích 12.000 m²"* → *"Kho trung tâm là điểm trung chuyển, rộng 12.000 m²"*.
**Không flag:** *đóng vai trò* đang phân biệt chức năng với danh tính; *sở hữu* nói đến quyền tài sản thật (*công ty sở hữu 51% cổ phần*); *mang lại* nêu một kết quả hoặc lợi ích thật chứ không thay cho *là* hoặc *có*.

### V18. Câu lồng nhiều tầng, "mà" và "điều này" không rõ

**Dấu hiệu:** một câu chứa nhiều lớp chú thích và mệnh đề phụ; lặp *mà* để nối các lớp; hoặc dùng *, điều này / việc này + động từ* để gắn thêm một kết quả. *Vốn là / vốn được* chen giữa chủ ngữ và động từ cũng là dấu hiệu cần xem lại.
**Vì sao:** khi nhiều quan hệ bị dồn vào một câu, đại từ như *điều này* có thể không còn trỏ rõ vào ý nào. Tách câu giúp mỗi quan hệ có chủ thể và điểm quy chiếu rõ hơn.
**Sửa:** *"Hệ thống mới, vốn chạy trên nền tảng đám mây mà công ty đầu tư từ năm 2024, cho phép đồng bộ tồn kho theo thời gian thực, điều này giúp giảm bán vượt tồn"* → *"Hệ thống mới chạy trên nền tảng đám mây. Công ty đầu tư nền tảng này từ năm 2024. Việc đồng bộ tồn kho theo thời gian thực giúp giảm tình trạng bán vượt tồn."* Khi tách, giữ nguyên chủ thể và quan hệ nhân quả của bản gốc.
**Không flag:** *mà* dùng đúng để đối lập (*"Rẻ mà bền"*) hoặc làm tiểu từ (*"Tôi đã nói rồi mà"*); câu dài nhưng các quan hệ vẫn rõ; pháp quy và hợp đồng cần giữ một câu để xác định phạm vi. Không đặt ngưỡng độ dài chung cho mọi câu.

## Chêm tiếng Anh không hợp ngữ cảnh

### V19. Chêm tiếng Anh không hợp người đọc hoặc lĩnh vực

**Dấu hiệu:** phải xét người đọc, lĩnh vực và mẫu văn trước khi kết luận. Trong tài liệu nội bộ của một ngành thường dùng thuật ngữ tiếng Anh, việc dịch toàn bộ thuật ngữ sang những cụm tiếng Việt xa lạ có thể làm câu thiếu tự nhiên. Ngược lại, trong giáo trình, đề án hoặc văn bản viết cho người đọc ngoài ngành, chêm tiếng Anh không giải thích có thể làm sai giọng văn. Cũng cần xem lại khi từ tiếng Anh được in nghiêng, dịch trong ngoặc hoặc chèn theo cùng một khuôn ở mọi lần xuất hiện dù không cần thiết.

**Vì sao:** thuật ngữ là quy ước của một cộng đồng sử dụng, không phải phép thay từ cố định giữa tiếng Anh và tiếng Việt. Cùng một từ có thể tự nhiên trong chat nội bộ nhưng không phù hợp với giáo trình. Việc có hoặc không có tiếng Anh tự nó không chứng minh văn bản do người hay AI viết.

**Sửa:** với tài liệu nội bộ, giữ hoặc trả lại thuật ngữ tiếng Anh khi mẫu văn, tài liệu cùng repo hoặc cách dùng ổn định của ngành cho thấy đó là tên gọi quen thuộc: *deploy, cloud, endpoint, benchmark, deadline*. Với nội dung học thuật hoặc viết cho người ngoài ngành, dùng từ tiếng Việt đã phổ biến; nếu cần giữ thuật ngữ tiếng Anh thì giải thích ở lần xuất hiện đầu. Không tự thêm tiếng Anh chỉ vì văn bản thuộc ngành kỹ thuật.

**Không flag:** người viết chủ động thuần Việt hoá nhất quán; văn bản dành cho người đọc ngoài ngành; thuật ngữ chưa có từ tiếng Việt tương đương; cách chêm tiếng Anh xuất hiện ổn định trong mẫu văn của người dùng. Không sửa khi chưa biết cộng đồng đó thực sự gọi thuật ngữ như thế nào.

## Từ bị viết thiếu

### V20. Từ hoặc cụm từ bị thiếu một tiếng

**Dấu hiệu:** một tiếng đứng riêng nhưng ý câu cần một từ hoặc cụm hai tiếng đầy đủ. Có ba trường hợp:

1. Tiếng đang dùng hầu như không đứng riêng với nghĩa đó: *rườm* thay cho *rườm rà*, *bỡ* thay cho *bỡ ngỡ*, *chới* thay cho *chới với*.
2. Tiếng có thể đứng riêng nhưng mang nghĩa khác trong câu: *hụt* thay cho *hụt hẫng*.
3. Tiếng có nghĩa gần đúng nhưng văn cảnh cần cách kết hợp đầy đủ hơn: trong hướng dẫn biên tập, *"Chỉ được rà typography"* cần thành *"Chỉ được rà soát typography"* nếu ý là kiểm tra kỹ từng chi tiết.

**Vì sao:** câu có thể vẫn đúng cấu trúc dù thiếu một tiếng, nên lỗi này dễ lọt qua kiểm tra chính tả. Phần thiếu nằm ở nghĩa của từ hoặc cách kết hợp từ trong văn cảnh.

**Sửa:** *"Câu này đúng ngữ pháp nhưng đọc lên thấy hụt"* → *"...thấy **hụt hẫng**"*. *"Quy trình còn rườm"* → *"...còn **rườm rà**"*. Trước khi thêm tiếng, kiểm tra lần lượt: tiếng hiện tại có dùng độc lập với đúng nghĩa này không; thêm tiếng có làm đúng nghĩa và đúng cách kết hợp từ không; văn bản có đang cố ý viết rút gọn không. Không chắc thì để nguyên.

**Không flag:** từ đơn hợp lệ đúng nghĩa (*đi, ăn, vui, buồn, đẹp, sạch*). Giữ *rà* trong *rà lại tài liệu, rà kỹ, rà một lượt, rà kế hoạch một lần nữa*; các nghĩa chuyên biệt như *rà mìn, rà sóng, rà kim, máy bay rà thấp*; và cách nói nội bộ như *rà code, rà log* khi mẫu giọng cho phép. Với các cặp như *đẹp / đẹp đẽ, sạch / sạch sẽ*, thêm tiếng thứ hai chỉ là lựa chọn phong cách. Thuật ngữ rút gọn theo quy ước ngành và văn phong tối giản có chủ ý cũng không flag.

---

## Không thay từ chỉ để tránh lặp

Lặp lại danh từ đang được bàn tới là cách liên kết bình thường trong tiếng Việt. Không đổi *khách hàng* thành *người mua, người tiêu dùng, họ* qua từng câu chỉ để tạo cảm giác đa dạng; chuỗi từ khác nhau có thể khiến người đọc tưởng đó là các nhóm khác nhau.

Chỉ sửa khi nhiều từ đang gọi cùng một đối tượng mà không có lý do về nghĩa. Chọn một thuật ngữ rõ nhất rồi dùng nhất quán. Ngược lại, nếu hai từ thực sự chỉ hai nhóm hoặc hai vai trò khác nhau thì phải giữ sự phân biệt.

Đại từ *nó, chúng, điều này* cũng cần có đối tượng quy chiếu rõ. Khi đại từ gây mơ hồ, có thể bỏ chủ ngữ nếu ngữ cảnh vẫn rõ hoặc lặp lại danh từ gốc. *"Báo cáo đã gửi hôm qua. Nó chứa số liệu quý hai. Chúng tôi đã xem xét nó và thấy rằng nó có vài chỗ sai."* → *"Báo cáo gửi hôm qua có số liệu quý hai. Chúng tôi xem lại thì thấy vài chỗ sai."* Không thay bằng từ đồng nghĩa nếu việc thay từ làm mờ đối tượng.

---

# TYPOGRAPHY

**Cổng bắt buộc:** chỉ sửa typography khi có ít nhất một pattern V1–V20 cùng xuất hiện trong văn bản. Typography đơn độc không đủ làm bằng chứng, mà sửa nó đơn độc thì chỉ thêm rủi ro.

### T1. Viết hoa theo kiểu tiêu đề tiếng Anh

**Dấu hiệu:** tiêu đề viết hoa chữ đầu của gần như mọi tiếng (`## Chiến Lược Tăng Trưởng Và Mở Rộng Thị Trường`); tên cơ quan bị viết hoa theo từng tiếng (*Bộ Giáo Dục Và Đào Tạo*); danh từ chung giữa câu được viết hoa chỉ để gây chú ý.
**Vì sao:** tiếng Việt không mặc định dùng Title Case cho tiêu đề. Tên cơ quan, tổ chức lại có quy tắc riêng, không thể sửa bằng mẹo “từ nào có nghĩa thì viết hoa”. Theo Phụ lục II Nghị định 30/2020/NĐ-CP, văn bản hành chính viết hoa chữ đầu của các từ hoặc cụm từ chỉ loại hình, chức năng và lĩnh vực hoạt động. Vì *Giáo dục* và *Đào tạo* là hai cụm chỉ lĩnh vực nên cách viết đúng là *Bộ Giáo dục và Đào tạo*, không phải *Bộ Giáo Dục và Đào Tạo*.
**Sửa:** với tiêu đề, chỉ viết hoa chữ đầu và các tên riêng: *"Chiến Lược Tăng Trưởng Và Mở Rộng Thị Trường"* → *"Chiến lược tăng trưởng và mở rộng thị trường"*. Với tên cơ quan, ưu tiên cách viết trong tên chính thức hoặc hồ sơ đăng ký; khi biên tập văn bản hành chính thì đối chiếu Phụ lục II. Viết *Bộ Giáo dục và Đào tạo*, *Ban Giám đốc*. Chỉ viết *Phòng Kinh doanh* khi đó là tên chính thức của một đơn vị; nếu chỉ nói chung về chức năng thì viết *phòng kinh doanh*.
**Không flag:** tên thương hiệu, mã dự án và chữ viết tắt có quy ước riêng như YODY, VinFast, KPI; tên chính thức có cách viết như *Bộ Công Thương*; dòng chữ in hoa toàn bộ do thể thức văn bản hoặc thiết kế; trích dẫn nguyên văn. Không tự sửa tên cơ quan chỉ vì cách viết của nó khác các ví dụ trên.

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

### T4. Dấu phẩy đứng trước "và"

**Dấu hiệu:** cụm `, và` xuất hiện trước phần tử cuối của một danh sách đơn giản hoặc nằm giữa hai vế câu. Hai trường hợp này phải được đọc riêng; kết quả quét bằng `,\s+và\s` chưa đủ để kết luận là lỗi.
**Vì sao:** liệt kê đơn giản trong tiếng Việt thường viết `A, B và C`. Khi nối hai vế câu, *và* vẫn đúng nếu hai ý chỉ bổ sung hoặc diễn ra song song. Chỉ cần sửa khi dấu phẩy không có tác dụng hoặc khi câu gốc đã thể hiện một quan hệ khác mà *và* làm mờ đi.
**Sửa:** trong danh sách đơn giản, bỏ dấu phẩy trước *và*: *"báo cáo tài chính, kế hoạch nhân sự, và lịch triển khai"* → *"báo cáo tài chính, kế hoạch nhân sự và lịch triển khai"*. Giữa hai vế câu, trước hết thử bỏ dấu phẩy và giữ *và*: *"Nhóm kiểm tra dữ liệu, và gửi báo cáo"* → *"Nhóm kiểm tra dữ liệu và gửi báo cáo"*. Chỉ thay *và* khi câu đã có dấu hiệu rõ: *vì vậy* có thể rút thành *nên*, *vẫn* có thể cho thấy quan hệ cần *nhưng*, còn *sau đó* có thể rút thành *rồi*. Nếu bản gốc không cho biết quan hệ, không tự chọn liên từ khác để làm câu có vẻ chặt chẽ hơn.
**Không flag:** dấu phẩy cần thiết để phân định các phần tử dài hoặc một phần tử đã chứa từ *và*; *và* nối hai ý bổ sung đúng nghĩa; dấu phẩy được người viết dùng có chủ ý để tạo nhịp. Dấu chấm phẩy là một dấu câu khác và không thuộc T4; không sửa nó chỉ vì nó đứng giữa hai mệnh đề.

### T5. Định dạng thay cho cấu trúc câu

**Dấu hiệu:** nhiều heading hoặc bullet liên tiếp cùng theo khuôn *cụm từ khóa: diễn giải hoặc slogan*, nhất là khi cụm từ khóa là một nhãn khái quát như *Hiệu quả, Đột phá, Linh hoạt, Tăng trưởng*. Thử bỏ phần trước dấu hai chấm: nếu phần sau vẫn đủ nghĩa và làm đúng chức năng của heading hoặc câu thì nhãn có thể là phần thừa. Các dấu hiệu đi kèm là nhãn được in đậm, nhãn lặp lại trong phần diễn giải và toàn bộ heading dùng những danh ngữ Hán-Việt ngắn, cân xứng.
**Vì sao:** khuôn này tách một ý liền mạch thành hai phần dù nhãn không phân loại nội dung hay bổ sung ý nghĩa. Khi mục nào cũng viết như vậy, người đọc phải đi qua một nhãn chung chung trước khi đến thông tin chính. Dấu hai chấm không sai; chỗ cần sửa là nhãn không làm nhiệm vụ nào ngoài trang trí hoặc tạo vẻ cân xứng.
**Sửa:** bỏ nhãn thừa và để phần mang thông tin làm heading hoặc câu. *"### Hiệu quả: Giảm thời gian xử lý đơn"* → *"### Giảm thời gian xử lý đơn"*. *"- **Hiệu quả vận hành:** Quy trình xử lý đơn được rút gọn"* → *"- Quy trình xử lý đơn được rút gọn"*. Nếu nhãn có nội dung cần giữ, viết lại thành một câu liền thay vì giữ hai nửa rời nhau. Không xoá dấu hai chấm hàng loạt; xét chức năng của từng mục.
**Không flag:** nhãn–giá trị (*Trạng thái: đang xử lý*), thuật ngữ–định nghĩa, người nói–lời nói, tiêu đề có phụ đề thật, mục hỏi–đáp, biểu mẫu, bảng, slide, thẻ giao diện và bảng thuật ngữ. Trong README, changelog, đặc tả kỹ thuật, SOP hoặc tài liệu tham chiếu, giữ nhãn khi nó xác định trường dữ liệu, loại bước hoặc nhóm nội dung cần cho việc tra cứu. Thể loại kỹ thuật tự nó không phải lý do để miễn T5. Một heading có dấu hai chấm đứng riêng cũng chưa đủ để flag; cần thấy khuôn lặp lại hoặc nhãn rõ ràng không mang thông tin.

### T6. Emoji

**Dấu hiệu:** emoji trang trí đầu heading hoặc đầu bullet.
**Vì sao:** emoji trang trí lặp lại có thể làm văn bản lệch khỏi thể loại hoặc che mất cấu trúc thật của danh sách. Bản thân emoji không phải lỗi ngôn ngữ.
**Sửa:** bỏ emoji khi người dùng hoặc thể loại yêu cầu văn bản trang trọng; giữ nguyên nội dung và cấu trúc câu.
**Không flag:** tin nhắn, mạng xã hội, nội dung nội bộ có văn hoá dùng emoji. Emoji mang thông tin thật (trạng thái trong bảng, ký hiệu quy ước).

---

# Những trường hợp không được sửa

## Những đặc điểm riêng cần giữ

Các đặc điểm dưới đây có thể thuộc giọng cá nhân, cộng đồng sử dụng hoặc dữ kiện của bản gốc. Không dùng chúng để suy đoán tác giả. Chỉ sửa khi chúng làm sai nghĩa, lệch thể loại hoặc trái với yêu cầu hiện tại.

1. **Giọng vùng miền và từ địa phương:** *mắc quá, chi rứa, nghen, hen, ni, nớ, bây, tau; bát / chén; cốc / ly*. Không chuẩn hoá về một vùng khác nếu người dùng muốn giữ giọng.
2. **Cách xưng hô thể hiện quan hệ:** *anh Tuấn bên kho, chị kế toán, bác bảo vệ tầng một, sếp cũ của em*. Không đổi đại từ nếu chưa biết tuổi, vai vế và mức độ thân sơ.
3. **Tiếng lóng, thuật ngữ và tiếng Anh của cộng đồng:** giữ khi cách dùng phù hợp với người đọc, lĩnh vực và mẫu văn. Xem V19.
4. **Dữ kiện cụ thể:** giờ, tiền, địa chỉ, tên quán, tên file, mã hoặc biển số là thông tin phải bảo toàn, không phải vật liệu để làm câu “mượt” hơn.
5. **Câu rút gọn, chỗ ngập ngừng hoặc tự sửa có chủ ý:** *“Hỏi lại lần nữa. Vẫn im. Thôi.”*; *“Khoảng ba tháng, à không, bốn tháng.”* Giữ khi chúng hợp với thể loại và giọng chung.
6. **Nhịp đoạn không đều:** đoạn dài xen đoạn ngắn có thể là dụng ý. Không san đều độ dài chỉ để văn bản cân đối.
7. **Cách gõ rút gọn:** *ko, dc, vs* và chữ thiếu dấu có thể hợp với chat hoặc ghi chú nội bộ. Chuẩn hoá khi văn bản cần xuất bản, khi người dùng yêu cầu hoặc khi cách viết gây hiểu nhầm.

## Các lỗi nhập liệu, không rõ con người hay AI viết

Khoảng trắng trước dấu câu chỉ là lỗi trình bày. Nó có thể xuất hiện do thói quen gõ, công cụ soạn thảo hoặc thao tác sao chép. Không dùng lỗi này để suy đoán văn bản do người hay AI viết. Chỉ sửa khi yêu cầu của người dùng bao gồm chính tả hoặc trình bày; giữ nguyên trong trích dẫn, code và dữ liệu cần bảo toàn.

## Các biến thể chính tả chỉ cần giữ nhất quán

Skill không quyết định thay người viết giữa hai cách đặt dấu thanh như *hòa / hoà, thủy / thuỷ* hoặc hai cách viết *i/y* như *kỹ / kĩ, tỷ / tỉ, lý / lí*. Quyết định 1989/QĐ-BGDĐT quy định một cách viết cho chương trình, sách giáo khoa và tài liệu dùng trong cơ sở giáo dục phổ thông; không tự động áp cách viết đó cho mọi thể loại.

Nếu người dùng, tổ chức hoặc nhà xuất bản đã có quy chuẩn thì làm theo quy chuẩn ấy. Nếu không có, giữ cách viết đang được dùng nhất quán trong văn bản. Không tự sửa tên riêng như *Nguyễn Vỹ* hoặc *Thy Ngọc*.

## Dấu hiệu không phải kết luận

Một dấu hiệu trong skill có thể xuất hiện trong câu hoàn toàn tự nhiên. Chỉ sửa khi gọi tên được lỗi, xác định được phần cần sửa và đã loại trừ trường hợp **Không flag** của pattern tương ứng. Không đặt một số lượng dấu hiệu cố định làm điều kiện và không dùng kết quả rà soát để kết luận ai đã viết văn bản.

Khi báo cáo, nêu lỗi cụ thể như *thiếu từ chỉ kết quả* hoặc *nhãn trước dấu hai chấm không mang thông tin*. Không dùng những kết luận chung như *đoạn này chắc do AI viết*.

## Phân biệt câu ngắn có chủ ý với câu thiếu từ

Câu ngắn không tự động là câu cụt. Trước khi thêm *là, thì, được, nên, rồi* hoặc một loại từ, hãy kiểm tra:

1. Người đọc có xác định được quan hệ giữa các thành phần và hiểu đúng ý câu không?
2. Từ định thêm có hoàn chỉnh một cấu trúc đang thiếu hay chỉ làm câu mềm và dài hơn?
3. Thể loại có chủ động dùng câu rút gọn không, chẳng hạn tin nhắn, hướng dẫn thao tác, ghi chú vận hành hoặc tài liệu kỹ thuật?

Nếu câu đã rõ nghĩa và phù hợp với thể loại thì để nguyên. Chỉ thêm từ khi pattern tương ứng chỉ ra được thành phần đang thiếu và từ thêm vào không làm đổi ý.

## Tự kiểm tra lại sau khi sửa

Đọc lại từng câu đã sửa trong cả đoạn, không đếm số lần xuất hiện của từng từ. Với mỗi thay đổi, kiểm tra xem nó có sửa đúng lỗi đã gọi tên, có giữ nguyên dữ kiện và quan hệ nghĩa, có hợp với giọng văn và có vô tình làm nhiều câu trở nên giống nhau hay không.

Một từ có thể lặp lại nhiều lần nếu lần nào cũng đúng nghĩa. Ngược lại, một từ chỉ xuất hiện một lần vẫn phải bỏ nếu nó được thêm vào mà không giải quyết lỗi nào.

---

## Cách trả kết quả

**Khi người dùng dán văn bản:** nếu họ chỉ yêu cầu viết lại, trả về bản cuối. Chỉ kèm nhận xét hoặc bản đối chiếu khi họ yêu cầu rà soát, giải thích hay so sánh.

**Khi người dùng giao file:** sửa đúng phần văn xuôi thuộc phạm vi yêu cầu. Giữ nguyên code, frontmatter, dữ liệu có cấu trúc và địa chỉ liên kết. Sau khi sửa, báo ngắn gọn phần đã thay đổi và không dán lại toàn bộ file vào hội thoại.

**Khi skill được dùng như một bước trong tác vụ khác:** chỉ trả về văn bản đã sửa, không thêm lời dẫn, phân tích hoặc tóm tắt.

## Khi người dùng sửa lại kết quả

Xem bản người dùng sửa là bằng chứng mạnh nhất cho trường hợp đang xử lý. So hai bản rồi phân loại:

- **Sở thích cá nhân:** áp dụng cho người viết đó. Nếu agent có memory hoặc knowledge base và chính sách lưu trữ cho phép, cập nhật hồ sơ văn phong của đúng người dùng. Chỉ ghi đặc tính cần thiết, phạm vi áp dụng và một ví dụ ngắn; không chép nguyên văn bản hoặc lưu dữ kiện cá nhân không liên quan. Không ghi loại này vào `calibration/LOG.md`.
- **Lỗi ở trường hợp loại trừ hoặc pattern còn thiếu:** ghi bằng chứng vào `calibration/LOG.md` theo giao thức trong `AGENTS.md`, rồi mới cân nhắc sửa quy tắc dùng chung.

Nếu chưa phân loại được, không ghi vào cả hai nơi. Yêu cầu hiện tại luôn được ưu tiên hơn hồ sơ đã lưu.

## Mức độ tin cậy của các quy tắc

Nguồn của từng quy tắc thuộc một trong ba nhóm: tài liệu được liệt kê trong `README.md`, quan sát có bản đối chiếu trong `calibration/LOG.md`, hoặc suy luận từ khác biệt giữa cấu trúc tiếng Anh và tiếng Việt. Phải nói rõ quy tắc dựa trên nhóm nào; không trình bày suy luận như kết quả đã được kiểm chứng trên bộ ngữ liệu.

Repo chưa có bộ ngữ liệu đủ để đặt ngưỡng tần suất cho các dấu hiệu. Vì vậy, số lần xuất hiện chỉ giúp tìm chỗ cần đọc kỹ hơn, không phải điều kiện để kết luận hoặc sửa. Danh sách nguồn và mức độ tin cậy nằm trong `README.md`.
