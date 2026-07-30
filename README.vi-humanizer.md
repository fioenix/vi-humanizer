# vi-humanizer

*"Câu này đúng ngữ pháp mà đọc lên thấy hụt."*

Câu trên chỉ cần đọc lên là biết AI viết. Trong tiếng Việt, người ta không kết câu bằng những từ đơn cụt lủn như vậy. Nếu là người Việt viết thì câu này sẽ đại loại là: "Câu này đúng ngữ pháp nhưng đọc lên thấy hụt hẫng". Từ "mà" và "nhưng" tuy gần nghĩ nhưng cách dùng phổ biến không giống nhau; từ "hụt" là một từ rất hiếm khi xuất hiện như một `từ đơn`, thông thường nó phải là một thành phần trong `từ ghép` như "hụt hẫng", "hụt hơi", "thiếu hụt"...

vi-humanizer là agent skill để hướng dẫn AI viết thuần Việt hơn: những từ ghép bị cắt đi kiểu đó, hoặc sáo ngữ (kiểu viết lặp đi lặp lại) và lỗi typography. 

## Skill này phát hiện gì

Chữ *được* thuộc lớp hư từ, lớp mà tiếng Việt bắt buộc có còn tiếng Anh thì không. Hàng loạt chỗ trống khác cùng cơ chế: *"Vì hệ thống chưa có cache, thời gian phản hồi tăng gấp ba"* mở bằng *Vì* mà không có vế *nên*; *"Cách xử lý đơn giản nhất tăng số worker"* thiếu chữ *là* nên hai danh ngữ dính liền.

Cả trang như vậy thì đúng ngữ pháp bề mặt mà cụt, hẫng, lạnh, dừng trước khi ý đóng lại. Người Việt cảm được ngay nhưng thường không chỉ ra được sai ở đâu. Skill gọi tên từng chỗ rồi trả lại chữ đã rụng.

**Lưu ý quan trọng về định vị:** skill này phát hiện **dấu vết dịch**, không phát hiện AI. Người Việt làm việc song ngữ viết ra translationese thật, hằng ngày. Đừng dùng kết quả như bằng chứng ai đó dùng AI.

## Cài đặt

### Skills CLI

```bash
npx skills add fioenix/vi-humanizer --global
```

Cập nhật:

```bash
npx skills update vi-humanizer --global --yes
```

Cài cho mọi agent harness trên máy trong một lệnh:

```bash
npx skills add fioenix/vi-humanizer --skill vi-humanizer --global --agent '*' --yes
```

Lệnh này đặt một bản duy nhất ở `~/.agents/skills/vi-humanizer` rồi symlink cho khoảng 70 harness, nên về sau chỉ cần update một lần là mọi agent cùng lên bản mới. Vài harness không hỗ trợ cài global (Eve, PromptScript) sẽ báo lỗi và bị bỏ qua, phần còn lại vẫn cài bình thường.

Bỏ `--global` để cài trong phạm vi dự án và commit cùng repo. Lưu ý: cờ `--global` phải khớp giữa lúc cài và lúc update. Cài global mà update thiếu `--global` thì CLI tìm trong lock của project hiện tại, không thấy nên báo lỗi `repository 'vi-humanizer' does not exist`.

### Claude Code plugin

```
/plugin marketplace add fioenix/vi-humanizer
/plugin install vi-humanizer@vi-humanizer
```

Gọi bằng `/vi-humanizer:vi-humanizer`.

### Claude Desktop và claude.ai

Hai chỗ này không đọc thư mục skill trên máy, chúng cần một file `.skill` để upload. Đóng gói bằng:

```bash
./scripts/package-skill.sh
```

Ra `dist/vi-humanizer.skill`, kéo thả vào Claude Desktop hoặc upload trong phần Skills của claude.ai. Gói chỉ chứa phần runtime (`SKILL.md`, `profiles/`, `references/`, `calibration/`); README, AGENTS.md và manifest plugin không nằm trong đó.

### Thủ công

Runtime artifact là `SKILL.md` cùng ba thư mục `profiles/`, `references/` và `calibration/`. Chép cả cây thư mục vào thư mục skill của harness.

```bash
git clone https://github.com/fioenix/vi-humanizer.git /duong/dan/toi/skills/vi-humanizer
```

## Dùng thế nào

```
/vi-humanizer

[dán văn bản vào đây]
```

Trỏ vào file thì skill sửa tại chỗ:

```
Humanize phần văn xuôi trong docs/bai-viet.md
```

### Hiệu chỉnh theo giọng của bạn

```
/vi-humanizer

Đây là mẫu văn của tôi để bạn bắt giọng:
[2-3 đoạn bạn tự viết]

Giờ sửa đoạn này:
[văn bản cần sửa]
```

Mẫu văn **thắng mọi quy tắc trong skill**. Một người viết đúng chuẩn của họ không phải là một người viết sai.

## Kiến trúc

Skill chia theo trục **lỗi ngôn ngữ** và **lỗi giọng**, không chia theo chuyên đề.

- **Lỗi ngôn ngữ** sai ở cấp hư từ và cấu trúc câu. Là lỗi bất kể văn bản thuộc thể loại nào. Sửa chúng không đụng tới giọng người viết. Nhóm này nằm trong `SKILL.md`.
- **Lỗi giọng** phụ thuộc hoàn toàn vào register. Cùng một cụm là tell chí mạng ở blog và là chuẩn mực bắt buộc ở công văn. Nhóm này nằm trong `profiles/`.

```
SKILL.md                            cổng thể loại, lõi V1-V19, typography T1-T6, nhận diện
profiles/blog-ca-nhan.md            B1-B17 + giọng và cá tính
profiles/ky-thuat-doanh-nghiep.md   K1-K5 + lệnh cấm và điều chỉnh ngưỡng
references/han-viet-thuan-viet.md   bảng tra 111 dòng + năm phép thử
references/bang-tra-cuu.md          bổ ngữ kết quả, cặp hô ứng, loại từ, checklist
calibration/LOG.md                  bộ nhớ bằng chứng cho vòng tự hiệu chuẩn
scripts/validate-package.py         kiểm đồng bộ, chạy trong CI
scripts/package-skill.sh            đóng gói dist/vi-humanizer.skill
scripts/scan-tells.sh               tự soi repo bằng nhóm pattern quét máy được
```

Trước khi áp bất kỳ pattern nào, skill chạy một **cổng thể loại**. Sáu nhóm văn bản bị chặn hoàn toàn: pháp quy và hợp đồng, cổ phong và nghi lễ, tài liệu API và changelog, thơ, bản dịch có chủ đích, trích dẫn nguyên văn. Ở những thể loại đó, danh hoá, bị động và nhịp đối xứng là **yêu cầu thể loại**, không phải lỗi.

## Bộ pattern

### Lõi: lỗi ngôn ngữ (V1–V19)

Hư từ rụng. Đây là nhóm không có tương đương trong bản tiếng Anh.

| # | Pattern | Ví dụ |
|---|---|---|
| V1 | Thiếu bổ ngữ kết quả và hướng | "không giải quyết vấn đề" → "không giải quyết **được** vấn đề" |
| V2 | Cặp liên từ hô ứng chỉ còn một vế | "Vì A, B" → "A **nên** B" |
| V3 | Thiếu "là / thì / mà" ở ranh giới đề – thuyết | "Cách đơn giản nhất tăng số worker" → "... **là** tăng số worker" |
| V4 | Rụng dấu thời – thể, hoặc rắc quá đều | thiếu hẳn "rồi / vẫn / còn / mới / chưa" trong đoạn kể việc |
| V5 | Thiếu hoặc sai loại từ | "mua xe mới" → "mua **một chiếc** xe mới" |
| V6 | Khung hỏi và cầu khiến sai | "Bạn có kế hoạch tuần sau?" → "Tuần sau anh có kế hoạch **gì chưa**?" |

Khuôn tiếng Anh áp thẳng.

| # | Pattern | Ví dụ |
|---|---|---|
| V7 | "của" thừa theo khuôn "of" | "hiệu suất của hệ thống" → "hiệu suất hệ thống" |
| V8 | "các / những" rắc theo dấu số nhiều | "các thông tin", "các dữ liệu" |
| V9 | Cụm giới từ nặng dịch một-một | "Với sự hỗ trợ từ đối tác" → "Đối tác hỗ trợ nên..." |
| V10 | "một cách + tính từ", trạng ngữ Tây hoá | "xử lý một cách nhanh chóng" → "xử lý nhanh" |
| V11 | Khung giả chủ ngữ "Điều... là" | "Điều quan trọng cần lưu ý là..." |
| V12 | Trạng từ nối đầu câu ở mật độ tiếng Anh | "Hơn nữa, ... Ngoài ra, ... Bên cạnh đó, ..." |
| V13 | Khung SVO cứng, không đưa đề lên đầu | "Tôi đã đọc cuốn sách này" → "Cuốn sách này tôi đọc rồi" |
| V14 | Danh ngữ trần đứng làm câu | "Một hệ thống được thiết kế để..." |

Chuỗi danh hoá. Quét theo cụm ba tầng, không quét lẻ.

| # | Pattern | Ví dụ |
|---|---|---|
| V15 | Danh hoá thừa và động từ rỗng đỡ | "tiến hành thực hiện việc rà soát" → "rà soát" |
| V16 | Bị động calque "được / bị ... bởi" | "được hoàn thành bởi phòng kế toán" → "phòng kế toán hoàn thành" |
| V17 | Né hệ từ: "đóng vai trò là", "sở hữu" | "đóng vai trò là trung tâm" → "là trung tâm" |
| V18 | Câu nhiều tầng lồng, lạm dụng "mà", "điều này" | cắt thành câu riêng |

Song ngữ.

| # | Pattern | Ví dụ |
|---|---|---|
| V19 | Chêm tiếng Anh sai mật độ hoặc sai kiểu | "điện toán đám mây" ở chỗ dân trong ngành nói "cloud" |

### Typography (T1–T6)

Chỉ sửa khi có ít nhất một pattern lõi cùng xuất hiện. Typography đơn độc không đủ làm bằng chứng.

| # | Pattern | Khác gì bản tiếng Anh |
|---|---|---|
| T1 | Viết hoa kiểu marketing | Tiếng Việt không có Title Case, nên đây là tell **mạnh hơn** |
| T2 | Em dash và gạch ngang chú thích giữa câu | **Hẹp hơn hẳn.** Chỉ cấm `—`. `–` là gạch ngang chuẩn tiếng Việt |
| T3 | Ngoặc kép không nhất quán | **Đảo hành vi.** Không ép về ngoặc thẳng, chỉ kiểm nhất quán |
| T4 | Dấu phẩy Oxford và comma-and nối mệnh đề | Mới. Tiếng Việt không có Oxford comma. Nối mệnh đề thì dùng hư từ chứ không dùng *và* |
| T5 | Lạm dụng markdown | Thêm ba nét riêng của tiếng Việt |
| T6 | Emoji | Giữ nguyên |

### Profile blog, cá nhân, công việc, marketing (B1–B17)

| # | Pattern |
|---|---|
| B1 | Sáo ngữ tôn vinh tầm quan trọng |
| B2 | Ẩn dụ kho sẵn và calque thành ngữ tiếng Anh |
| B3 | Mở bài dẫn dắt vòng vo |
| B4 | Kết bài lạc quan sáo rỗng |
| B5 | Song hành phủ định "không chỉ... mà còn" |
| B6 | Nghi vấn tu từ mở đoạn kiểu SEO |
| B7 | Tụng ca địa phương và doanh nghiệp |
| B8 | Danh xưng phóng đại |
| B9 | Hán-Việt hoá tên gọi đời thường |
| B10 | Thành ngữ dùng lệch và mật độ thành ngữ bất thường |
| B11 | Nhịp ba cân âm tiết và biền ngẫu giả |
| B12 | Cụm bốn âm tiết Hán-Việt tự chế |
| B13 | Nhịp câu đều đặn bất thường |
| B14 | Rụng tiểu từ tình thái cuối câu |
| B15 | Xưng hô lơ lửng và phẳng |
| B16 | Giả thân mật |
| B17 | Trộn register không chủ đích |

### Profile kỹ thuật, doanh nghiệp, học thuật (K1–K5)

| # | Pattern |
|---|---|
| K1 | Viết theo diff thay vì mô tả hiện trạng |
| K2 | Sáo ngữ thể chế rỗng ngoài văn bản pháp quy |
| K3 | Bộ đề mục Hán-Việt đối xứng rỗng |
| K4 | Mô tả hiện tượng mà không đưa hiện tượng ra |
| K5 | Câu dẫn nhập rỗng sau đề mục |

Phần lớn profile này là **lệnh cấm**, không phải pattern: cấm chèn tiểu từ, cấm thêm giọng, cấm tạo chuỗi đồng nghĩa cho thuật ngữ, cấm thuần Việt hoá thuật ngữ Hán-Việt.

## Ba chỗ skill này đi ngược bản tiếng Anh

**1. Không bao giờ sửa câu chỉ vì nó lặp từ.** Bản tiếng Anh coi lặp danh từ là lỗi văn phong và chữa bằng từ đồng nghĩa. Tiếng Việt đơn lập, không có đại từ hồi chỉ tiện dụng như *it / they*, nên lặp nguyên danh từ là **phương thức liên kết chuẩn mực**. Mang ngưỡng chống lặp của tiếng Anh sang là chủ động tạo ra dịch tính. Thứ phải cắt là chuỗi đồng nghĩa (*doanh nghiệp → công ty → tổ chức → đơn vị*), không phải chuỗi lặp.

**2. Không cấm en dash.** Bản tiếng Anh cấm cả `—` và `–`. Trong tiếng Việt, `–` là gạch ngang chuẩn với bốn chức năng hợp lệ: lời thoại, liệt kê đầu dòng, cặp tên riêng (*quan hệ Việt – Trung*), khoảng (*2020 – 2025*). Bê nguyên quy tắc đó sang sẽ phá địa danh và mọi lời thoại, tức là hỏng nội dung chứ không phải hỏng phong cách.

**3. Không ép ngoặc kép về dạng thẳng.** Word, Google Docs và macOS đều tự bo cong, mà đây lại là công cụ soạn thảo mặc định ở Việt Nam. Ép về ngoặc thẳng sẽ sửa hàng loạt văn bản người thật gõ. Chỉ kiểm tra nhất quán nội bộ.

## Hai thứ bị loại khỏi skill có chủ đích

**Dấu thanh kiểu cũ và kiểu mới** (*hòa / hoà*) và **quy tắc i/y** (*kỹ / kĩ*, *tỷ / tỉ*). QĐ 1989/QĐ-BGDĐT 2018 Điều 8 và 9 chỉ áp cho sách giáo khoa phổ thông; báo chí, doanh nghiệp và pháp quy dùng kiểu còn lại áp đảo. Đây là tranh chấp chuẩn mực giữa hai giới, không liên quan gì tới AI. Thêm nữa Điều 9.2 loại trừ tên riêng (*Nguyễn Vỹ*, *Thy Ngọc*), nên mọi quy tắc i/y tự động đều có nguy cơ sửa sai tên người.

Chỉ giữ lại dưới dạng kiểm tra nhất quán nội bộ. Nguyên tắc: **nhất quán nội bộ, không áp chuẩn ngoài.**

## Một tín hiệu chạy ngược chiều

**Khoảng trắng trước dấu câu là bằng chứng người thật viết, không phải tell AI.** Mô hình gần như không sinh lỗi này; người gõ nhanh trên điện thoại thì có. Skill khai báo chiều tín hiệu này tường minh, vì để agent tự suy thì nó sẽ vừa kết luận ngược vừa sửa mất bằng chứng.

## Skill tự hiệu chuẩn từ sử dụng thật

Skill được thiết kế để một agent chạy lâu dài tự nâng cấp nó dựa trên cách người thật viết và sửa. Khi người dùng sửa lại bản rewrite, bản của họ là bản vàng: agent so hai bản, gọi tên pattern nào bắn sai và guard nào thiếu, ghi vào `calibration/LOG.md`, rồi mới đề xuất sửa skill.

Chỗ dễ hỏng nhất là gộp mọi khác biệt vào một rọ, nên giao thức bắt phân loại ba đường trước:

| Loại khác biệt | Đi đâu | Ngưỡng bằng chứng |
|---|---|---|
| Sở thích cá nhân | Voice memory của agent, **không vào skill** | không bao giờ |
| Lỗi guard | Nới hoặc siết guard của pattern có sẵn | n=1 nếu lỗi gọi tên được |
| Pattern mới | Thêm pattern, đúng khung bốn phần | n≥3 mẫu độc lập |

Không có entry trong log thì không được sửa skill: log là bộ nhớ bằng chứng, sửa mà không có nó là bịa. Pattern sinh ra theo đường này gắn nhãn "Quan sát từ sử dụng (n=…)", mạnh hơn suy luận nhưng yếu hơn corpus.

Một hệ quả cần nói rõ: skill cài cho agent nào thì sẽ dần tune theo giọng của tổ chức đó. Với fork nội bộ thì đó là tính năng, nhưng ai cài từ ngoài cần biết. Giao thức đầy đủ nằm trong `AGENTS.md`.

Ranh giới của cơ chế này: skill chỉ thấy những lượt nó được gọi. Muốn agent học từ chat thường ngày, phải thêm một chỉ dẫn ở tầng memory của chính agent, skill không tự làm được.

## Nền tảng bằng chứng

Không tồn tại nghiên cứu định lượng nào về dấu hiệu văn bản AI trong tiếng Việt ở cấp từ vựng hay cú pháp. Các công trình hiện có về phát hiện văn bản AI tiếng Việt chỉ dùng đặc trưng phân bố xác suất, không liệt kê pattern ngôn ngữ học nào.

Khoảng một phần ba pattern trong skill có nguồn dẫn được; phần còn lại là **suy luận từ cơ chế sinh văn bản**, dựa trên đối chiếu ngữ pháp Anh – Việt. Nguồn quy phạm chắc chắn nhất nằm ở nhóm typography, mà phần lớn lại dùng để **loại bỏ** quy tắc khỏi skill chứ không phải để thêm vào.

Mọi ngưỡng số trong skill là **chưa hiệu chuẩn trên corpus**. Đây là việc chính còn nợ: kiểm chứng trên corpus văn bản AI tiếng Việt thật. Trong lúc chưa có corpus, vòng hiệu chuẩn từ sử dụng thật đang gánh phần này.

## Nguồn tham khảo

Phân hạng theo độ tin cậy. Trộn nguồn quy phạm với bài blog rồi trình bày như nhau là bịa uy tín.

### Hạng A: quy phạm và học thuật

| Nguồn | Dùng cho |
|---|---|
| [Nghị định 30/2020/NĐ-CP, Phụ lục II](https://thuvienphapluat.vn/chinh-sach-phap-luat-moi/vn/bieu-mau/55095/tong-hop-cac-phu-luc-ve-van-ban-hanh-chinh-moi-nhat-ban-hanh-kem-theo-nghi-dinh-30-2020) | Chuẩn viết hoa tên cơ quan tổ chức. Căn cứ cho T1 |
| [Quyết định 1989/QĐ-BGDĐT 2018](https://thuvienphapluat.vn/van-ban/Giao-duc/Quyet-dinh-1989-QD-BGDDT-2018-quy-dinh-chinh-ta-Chuong-trinh-sach-giao-khoa-giao-duc-pho-thong-445355.aspx) · [bản đối chiếu](https://hoatieu.vn/phap-luat/quyet-dinh-1989-qd-bgddt-2018-quy-dinh-chinh-ta-chuong-trinh-sach-giao-khoa-giao-duc-pho-thong-214530) | Điều 8 và 9. Căn cứ để **loại** dấu thanh và i/y khỏi skill |
| [ViDetect – arXiv:2405.03206](https://arxiv.org/abs/2405.03206) | Phát hiện văn bản AI tiếng Việt. **Không** cung cấp pattern ngôn ngữ học nào; dẫn để chứng minh khoảng trống nghiên cứu |
| [VietBinoculars – arXiv:2509.26189](https://arxiv.org/pdf/2509.26189) | Như trên |
| [A Survey on Zero Pronoun Translation – arXiv:2305.10196](https://arxiv.org/pdf/2305.10196) | Cơ sở cho quy tắc đảo chiều về đại từ hồi chỉ và pro-drop |
| [Nghiên cứu dịch câu bị động Anh – Việt – i-jte.org](https://i-jte.org/index.php/journal/article/view/90) | V16. Lưu ý: khảo sát người dịch, không phải mô hình |
| [Danh hoá động từ trong danh ngữ – Tạp chí Giáo dục](https://tcgd.tapchigiaoduc.edu.vn/index.php/tapchi/article/view/4322) | V15 |
| [Cú pháp tiếng Việt nhìn từ ngữ pháp chức năng – VJOL](https://vjol.info.vn/index.php/tdm/article/download/93747/79245/) | V13, cấu trúc đề – thuyết |
| [Tình thái từ – VOER](https://voer.edu.vn/c/tinh-thai-tu/4491bb06/712ccc96) | B14 |
| [Tiểu từ tình thái và tính lịch sự – VUSTA](https://vusta.vn/mot-so-tieu-tu-tinh-thai-bieu-dat-tinh-lich-su-trong-hanh-dong-ngo-loi-bang-tieng-viet-p72715.html) | B14 |
| [Loại từ CON và CÁI – ngonngu.org](http://ngonngu.org/Con_Cai.htm) | V5 |

### Hạng B: bách khoa và báo ngành

[Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) (nguồn của skill tiếng Anh gốc) · [Null anaphora](https://en.wikipedia.org/wiki/Null_anaphora) · [Loại từ](https://vi.wikipedia.org/wiki/Lo%E1%BA%A1i_t%E1%BB%AB) · [Dấu gạch ngang](https://vi.wikipedia.org/wiki/D%E1%BA%A5u_g%E1%BA%A1ch_ngang) · [Dấu ngoặc kép](https://vi.wikipedia.org/wiki/D%E1%BA%A5u_ngo%E1%BA%B7c_k%C3%A9p) · [Quy tắc đặt dấu thanh](https://vi.wikipedia.org/wiki/Quy_t%E1%BA%AFc_%C4%91%E1%BA%B7t_d%E1%BA%A5u_thanh_c%E1%BB%A7a_ch%E1%BB%AF_Qu%E1%BB%91c_ng%E1%BB%AF) · [Từ thuần Việt](https://vi.wikipedia.org/wiki/T%E1%BB%AB_thu%E1%BA%A7n_Vi%E1%BB%87t) · [Phân biệt gạch ngang và gạch nối – Giáo dục TP.HCM](https://giaoduc.edu.vn/phan-biet-dau-gach-ngang-va-gach-noi/) · [Chuyển đổi từ Hán-Việt sang thuần Việt – Người Hà Nội](https://nguoihanoi.vn/chuyen-doi-tu-han-viet-sang-tu-thuan-viet-73914.html)

### Hạng C: cộng đồng, chưa kiểm chứng

Dùng để xác nhận hiện tượng tồn tại, **không** dùng làm căn cứ quy phạm. Phần lớn là bài hướng dẫn prompt của giới marketing.

[Brands Vietnam – dấu hiệu nội dung viết bởi AI](https://help.brandsvietnam.com/vi/article/dau-hieu-nhan-biet-noi-dung-duoc-viet-boi-ai-3zy07d/) (nguồn tiếng Việt duy nhất liệt kê cụm từ cụ thể) · [VnReview](https://vnreview.vn/threads/6-prompt-bat-chatgpt-claude-ai-viet-nhu-nguoi-danh-cho-nganh-marketing-va-truyen-thong.83181/) · [QuanTriMang](https://quantrimang.com/prompt-giup-ai-viet-lai-noi-dung-tu-nhien-214919) · [TinAI](https://tinai.vn/ung-dung-ai/truyen-thong-va-marketing/cach-dung-ai-viet-content-chuan-seo-len-top-google.html) · [Mực Tím – Tuổi Trẻ](https://muctim.tuoitre.vn/nhung-cach-tan-dung-chatgpt-de-hoc-ngoai-ngu-101240829223938035.htm) · [Cặp quan hệ từ – HOCMAI](https://hoctot.hocmai.vn/dau-hieu-nhan-biet-quan-he-tu-va-cap-quan-he-tu.html) · [Quan hệ từ – KidsUp](https://www.kidsup.net/quan-he-tu-la-gi/) · [Đề – Thuyết – Ngày ngày viết chữ](https://ngayngayvietchu.com/thu-phan-tich-cau-tieng-viet-theo-cau-truc-de-thuyet/) · [Từ Hán-Việt và thuần Việt – RDSIC](https://rdsic.edu.vn/blog/blog-2/tu-han-viet-va-tu-thuan-viet-vi-cb.html) · [Biền ngẫu – Từ điển wiki](https://tudienwiki.com/bien-ngau/) · [Đối chiếu câu bị động Anh – Việt – Studocu](https://www.studocu.vn/vn/document/truong-dai-hoc-khoa-hoc-xa-hoi-va-nhan-van/ngon-ngu-hoc/doi-chieu-cau-bi-dong-trong-tieng-anh-va-tieng-viet/86106287) (tài liệu sinh viên, độ tin cậy trung bình)

### Nguồn còn thiếu

Hai nguồn hạng C đang gánh nội dung vốn thuộc hạng A và cần được thay bằng nguồn gốc:

- **Lý thuyết đề – thuyết** (V3, V13) hiện dẫn một trang trình bày lại công trình của Cao Xuân Hạo. Cần trích trực tiếp công trình gốc.
- **Đối chiếu bị động Anh – Việt** (V16) hiện dẫn tài liệu sinh viên. Cần thay bằng nghiên cứu công bố.

Cả hai cần tra cứu tài liệu in nên chưa làm được ngay. Ghi ra đây thay vì giấu đi.

## Lời cảm ơn

Ý tưởng đóng gói, hợp đồng bảo trì và cấu trúc "before / after / không được flag khi" học từ [blader/humanizer](https://github.com/blader/humanizer), skill humanizer tiếng Anh dựa trên hướng dẫn của WikiProject AI Cleanup. Bộ pattern tiếng Việt thì xây mới hoàn toàn.

## Lịch sử phiên bản

- **0.3.0** – Viết lại phần mở đầu README sau nhận xét "khô cứng, vô hồn, tối nghĩa". Bản mới mở bằng một câu lỗi thật rồi mới giải thích, thay vì mô tả hiện tượng bằng danh từ trừu tượng. Ba lỗi guard lộ ra từ lượt này, đều đã sửa: V14 trong profile kỹ thuật nới quá rộng nên câu mở đầu README cũ là danh ngữ trần mà sống sót qua hai lần chạy skill, giờ nới theo vị trí chứ không theo tài liệu; thêm **K4. Mô tả hiện tượng mà không đưa hiện tượng ra**, phanh đối xứng với quy tắc thanh ngữ vực, vì trung tính nói về giọng còn trừu tượng nói về độ cụ thể; mở ngoại lệ hẹp cho ngưỡng 15% khi cách chữa duy nhất là bổ sung ví dụ, với guard là ví dụ phải có sẵn trong repo chứ không sáng tác. K4 cũ đổi số thành K5.
- **0.2.2** – Chạy skill lên toàn bộ 8 file nội dung của repo. Phát hiện T4 dính 25 chỗ trên 6 file, mà hai phần ba trong đó là comma-and nối hai mệnh đề độc lập chứ không phải Oxford comma. T4 bản cũ không mô tả nhánh này nên agent quét đúng regex mà không biết sửa thế nào. Tách T4 thành hai nhánh, thêm bảng chọn hư từ theo quan hệ (*nên* nhân quả, *mà* tương phản, *còn… thì* đối lập cục bộ, *rồi* nối tiếp). Thêm `scripts/scan-tells.sh` để tự soi bằng một lệnh thay vì dựng lại grep mỗi lần.
- **0.2.1** – Chạy chính skill lên README. Sửa bốn lỗi ngôn ngữ (một em dash chú thích giữa câu vi phạm T2, "kết quả của nó" theo V7, "được xây mới" theo V16, một mệnh đề quan hệ thiếu ranh giới theo V3) và vá phần nội dung đã lệch so với repo: cây thư mục thiếu `calibration/` và `scripts/`, số dòng bảng Hán-Việt ghi sai, mục "việc bắt buộc cho v0.2" đã lỗi thời. Thêm mục về vòng tự hiệu chuẩn (tính năng chính của 0.2.0 nhưng chưa có trong README) và cách cài một lệnh cho mọi harness bằng `--agent '*'`.
- **0.2.0** – Giao thức tự nâng cấp cho agent chạy lâu dài: vòng phản hồi trong SKILL.md (bản người dùng sửa lại là bản vàng), giao thức hiệu chuẩn trong AGENTS.md (phân loại sở thích cá nhân / lỗi guard / pattern mới, ngưỡng bằng chứng, nhãn "Quan sát từ sử dụng"), và `calibration/LOG.md` làm bộ nhớ bằng chứng với entry mẫu đầu tiên. Skill cài cho agent nào thì sẽ dần tune theo cách viết của tổ chức đó; changelog phải ghi nhận điều này.
- **0.1.1** – Tự áp skill lên chính văn bản của skill: bỏ toàn bộ em dash và các cụm dịch tính trong phần giải thích. Hiệu chỉnh từ vòng feedback thực tế đầu tiên: thêm quy tắc thanh ngữ vực (hạ giọng quá tay cũng là lỗi, như thổi phồng), V19 thêm chiều sửa chủ động (trả thuật ngữ bị dịch sạch về jargon: "đội ngũ kỹ thuật" → "team dev" trong tài liệu nội bộ IT), nới guard V9 và K2 cho tiếng Việt công sở (cụm mục đích và cụm "nâng cao hiệu quả X" có bổ ngữ cụ thể là bình thường trong báo cáo doanh nghiệp).
- **0.1.0** – Bản đầu. 19 pattern lõi, 6 pattern typography, 2 profile với 21 pattern, 2 file tham chiếu. Cổng thể loại chạy trước mọi pattern. Ba chỗ đi ngược bản tiếng Anh: quy tắc lặp từ, en dash, ngoặc kép. Loại dấu thanh cũ/mới và i/y khỏi skill có chủ đích.

## Giấy phép

MIT
