# vi-humanizer

Các AI agents hiện tại có thể viết những đoạn tiếng Việt trôi chảy và đúng ngữ pháp. Tuy vậy, văn phong của chúng vẫn thường có những chỗ người Việt Nam hiếm khi mắc phải: câu giữ nguyên khung tiếng Anh, hư từ hoặc loại từ bị bỏ sót, thuật ngữ quen thuộc bị dịch thành một cách gọi xa lạ, giọng văn thay đổi giữa các đoạn, còn phần mở đầu và kết luận thì đầy những câu sáo rỗng. Từng lỗi riêng lẻ rất nhỏ, nhưng khi xuất hiện cùng nhau, chúng khiến văn bản trở nên khô cứng, thiếu tự nhiên hoặc không đúng với giọng văn của người thật.

Một yêu cầu chung chung như “viết lại cho tự nhiên hơn” thường không giải quyết được vấn đề này. AI có thể thay cả câu, hạ giọng văn hoặc thêm chi tiết để bản mới nghe mượt hơn, nhưng đồng thời làm lệch ý và mất giọng của tác giả. `vi-humanizer` được tạo ra để biên tập theo một nguyên tắc khác: xác định thể loại và người đọc trước, gọi tên từng lỗi cần sửa, rồi chỉ thay phần thực sự có vấn đề. Blog vẫn được giữ cá tính; README vẫn giữ thuật ngữ kỹ thuật; báo cáo doanh nghiệp không bị kéo thành lời trò chuyện.

Bạn có thể dùng skill này để rà một bản nháp do AI tạo, chỉnh tài liệu dịch từ tiếng Anh, sửa nội dung do người viết song ngữ soạn hoặc kiểm tra lại một bài tiếng Việt đang đọc chưa thuận miệng. Chẳng hạn, câu *“Đã thử ba cách mà vẫn không giải quyết vấn đề”* có thể thiếu chữ *được*. Nếu ý là đã thử nhưng chưa thành công thì câu văn đúng là *“vẫn không giải quyết **được** vấn đề”*. Chữ *được* không phải thành phần vô ích; nó là một từ phổ biến trong tiếng Việt, mang hàm ý hoàn tất nghĩa kết quả của động từ.

`vi-humanizer` không phải công cụ phát hiện AI. Những lỗi trên cũng xuất hiện trong bản dịch và văn bản do người thật viết, còn LLM vẫn có thể tạo ra một câu hoàn toàn tự nhiên. Mục tiêu của skill là làm cho văn bản đúng nghĩa, đúng thể loại và vẫn giữ được giọng riêng của người viết, không phải đoán xem là con người hay AI đã tạo ra nó.

*P/S:* Bản thân skill này cũng được viết bởi AI và tự trong vòng lặp nâng cấp chính nó, nên không tránh khỏi đôi chỗ nhỏ vẫn còn "rất AI", nhưng ít nhất toàn bộ lối hành văn tự nhiên và "con người" hơn đáng kể.

## Phạm vi

Skill xử lý ba lớp:

- V1–V20 kiểm tra cách dùng từ và cấu trúc câu, chẳng hạn thiếu bổ ngữ kết quả, thiếu loại từ, dịch sát giới từ hoặc đặt trạng ngữ gây mơ hồ.
- B1–B17 và K1–K5 kiểm tra sự phù hợp với thể loại. Blog, tin nhắn, README và bài nghiên cứu không dùng cùng một giọng.
- T1–T6 kiểm tra typography khi văn bản đồng thời có ít nhất một lỗi thuộc V1–V20.

Trước khi sửa, skill xác định thể loại, đọc profile phù hợp và kiểm tra mẫu văn hoặc hồ sơ cá nhân của đúng người dùng nếu nền tảng cung cấp memory hay knowledge base.

Skill không dùng kết quả rà soát để xác định tác giả. Người viết song ngữ cũng có thể giữ cấu trúc tiếng Anh trong câu tiếng Việt; LLM cũng có thể tạo ra câu hoàn toàn tự nhiên.

## Cài đặt

### Skills CLI

Cài toàn cục:

```bash
npx skills add fioenix/vi-humanizer --global
```

Cài cho mọi agent mà Skills CLI hỗ trợ:

```bash
npx skills add fioenix/vi-humanizer \
  --skill vi-humanizer \
  --agent '*' \
  --global \
  --yes
```

Bỏ `--global` nếu muốn cài trong phạm vi dự án. Có thể xem skill mà CLI tìm được trước khi cài:

```bash
npx skills add fioenix/vi-humanizer --list
```

Skills CLI nhận repository, URL hoặc đường dẫn cục bộ làm nguồn. Cờ `--agent '*'` chọn mọi agent được hỗ trợ; cờ `--copy` buộc CLI sao chép file thay vì tạo liên kết tượng trưng.

### Claude Code plugin

```text
/plugin marketplace add fioenix/vi-humanizer
/plugin install vi-humanizer@vi-humanizer
```

Sau khi cài, gọi skill bằng `/vi-humanizer:vi-humanizer`.

### Claude Desktop và claude.ai

Tạo file `.skill` bằng lệnh:

```bash
./scripts/package-skill.sh
```

Kết quả nằm ở `dist/vi-humanizer.skill`. Gói gồm `SKILL.md`, `profiles/`, `references/` và `calibration/`; các file dành cho người bảo trì repo không được đưa vào gói.

### Cài thủ công

Chép `SKILL.md` cùng ba thư mục `profiles/`, `references/` và `calibration/` vào thư mục skill của agent:

```bash
git clone https://github.com/fioenix/vi-humanizer.git /duong/dan/toi/skills/vi-humanizer
```

## Cách dùng

```text
/vi-humanizer

[văn bản cần biên tập]
```

Khi cần sửa file, nêu rõ phạm vi:

```text
Dùng vi-humanizer để sửa phần văn xuôi trong docs/bai-viet.md.
Giữ nguyên code, bảng tham số và các trích dẫn.
```

### Giữ giọng của một người cụ thể

Có thể đưa mẫu văn ngay trong yêu cầu:

```text
Đây là hai đoạn tôi tự viết:
[mẫu văn]

Hãy sửa đoạn dưới theo cùng cách xưng hô, nhịp câu và mức độ trang trọng:
[văn bản cần sửa]
```

Mẫu văn chỉ được ưu tiên đối với thói quen xuất hiện nhất quán, như cách xưng hô, nhịp câu, cách chêm tiếng Anh hoặc dùng dấu câu. Nó không hợp thức hoá lỗi ngôn ngữ rõ ràng và không vượt qua bốn quy tắc chốt chặn trong `SKILL.md`.

Nếu agent có memory hoặc knowledge base, nó nên đọc hồ sơ văn phong của đúng người dùng trước khi sửa. Hồ sơ này phải tách riêng theo người, chỉ lưu đặc tính cần thiết cho việc giữ giọng và luôn nhường chỗ cho yêu cầu hiện tại.

## Kiến trúc

`SKILL.md` là nguồn chuẩn. Các file còn lại bổ sung quy tắc theo thể loại, ví dụ hoặc dữ liệu bảo trì:

```text
SKILL.md                            quy trình, V1–V20, T1–T6 và cách trả kết quả
profiles/blog-ca-nhan.md            B1–B17 cho văn bản có giọng cá nhân
profiles/ky-thuat-doanh-nghiep.md   K1–K5 và giới hạn của văn kỹ thuật, học thuật
references/han-viet-thuan-viet.md   bảng tra và điều kiện phải giữ thuật ngữ
references/bang-tra-cuu.md          bảng tra hư từ, loại từ, tiểu từ và câu hỏi chẩn đoán
calibration/LOG.md                  bằng chứng dùng để sửa quy tắc chung
agents/openai.yaml                  tên hiển thị và lời gọi mặc định
scripts/validate-package.py         kiểm tra tính đồng bộ của gói
scripts/package-skill.sh            tạo dist/vi-humanizer.skill
scripts/scan-tells.sh               tìm những chỗ có thể rà bằng biểu thức chính quy
```

Trước khi chạy pattern, skill kiểm tra thể loại. Pháp quy, hợp đồng, thơ, văn cổ phong, nghi lễ, code, schema, bảng tham số và trích dẫn nguyên văn có những quy ước riêng nên bị loại khỏi phần biên tập tương ứng. Xem danh sách và ngoại lệ đầy đủ trong `SKILL.md`.

## Danh mục pattern

### Cách dùng từ và cấu trúc câu (V1–V20)

| # | Pattern | Ví dụ hoặc phép kiểm tra |
|---|---|---|
| V1 | Thiếu bổ ngữ kết quả và bổ ngữ hướng | *không giải quyết vấn đề* → *không giải quyết **được** vấn đề* khi ý là chưa thành công |
| V2 | Cặp liên từ bị thiếu từ ở vế sau | *Vì A, B* → *Vì A **nên** B* nếu câu cần nói rõ quan hệ nhân quả |
| V3 | Thiếu "là" trong câu định nghĩa hoặc lựa chọn | *Cách đơn giản nhất tăng worker* → *Cách đơn giản nhất **là** tăng worker* |
| V4 | Thiếu hoặc lạm dụng từ chỉ thời gian và trạng thái | Xem câu có cần *đã, đang, rồi, vẫn, chưa* để phân biệt diễn biến hay không |
| V5 | Thiếu hoặc sai loại từ | *nuôi ba mèo* → *nuôi ba **con** mèo* |
| V6 | Câu hỏi hoặc lời nhờ không đúng ý định giao tiếp | Phân biệt câu hỏi có hoặc không với câu hỏi cần nội dung cụ thể |
| V7 | "của" thừa trong cụm danh từ | *hiệu suất của hệ thống* → *hiệu suất hệ thống* nếu không có quan hệ sở hữu |
| V8 | "các" và "những" được thêm theo dấu số nhiều | Bỏ khi số nhiều đã rõ và phạm vi không đổi |
| V9 | Cụm giới từ dài do dịch sát | *trong quá trình kiểm tra* → *khi kiểm tra* nếu nghĩa giữ nguyên |
| V10 | Trạng ngữ đặt ở vị trí gây khó hiểu | Chuyển vị trí khi người đọc không biết trạng ngữ bổ nghĩa cho hành động nào |
| V11 | Câu dẫn không mang thêm thông tin | Bỏ *Điều quan trọng cần lưu ý là* nếu phần sau tự đứng được |
| V12 | Lặp từ nối ở đầu câu | Xem lại chuỗi câu cùng mở bằng *Ngoài ra, Tuy nhiên, Do đó* |
| V13 | Đoạn văn lặp cứng một kiểu mở câu | Chỉ sửa ở cấp đoạn khi khuôn lặp làm đứt mạch thông tin |
| V14 | Danh ngữ đứng riêng như một câu | *Một giải pháp linh hoạt cho nhiều kho.* → viết thành câu hoặc dùng làm heading đúng chức năng |
| V15 | Danh hoá thừa và động từ ít nội dung | *tiến hành thực hiện việc rà soát* → *rà soát* |
| V16 | Câu bị động dịch sát "được / bị ... bởi" | *được hoàn thành bởi phòng kế toán* → *phòng kế toán hoàn thành* khi tác nhân là trọng tâm |
| V17 | Dùng cụm dài thay cho "là" hoặc "có" | *đóng vai trò là trung tâm* → *là trung tâm* nếu không cần nhấn chức năng |
| V18 | Câu lồng nhiều tầng, "mà" và "điều này" không rõ | Tách câu nhưng giữ nguyên chủ thể và quan hệ nhân quả |
| V19 | Chêm tiếng Anh không hợp người đọc hoặc lĩnh vực | Giữ thuật ngữ theo cách dùng thật của cộng đồng, không tự thêm hoặc xoá đồng loạt |
| V20 | Từ hoặc cụm từ bị thiếu một tiếng | *đọc lên thấy hụt* → *đọc lên thấy **hụt hẫng*** khi đúng với ý câu |

### Typography (T1–T6)

| # | Pattern |
|---|---|
| T1 | Viết hoa theo kiểu tiêu đề tiếng Anh |
| T2 | Em dash và gạch ngang chú thích giữa câu |
| T3 | Ngoặc kép không nhất quán |
| T4 | Dấu phẩy đứng trước "và" |
| T5 | Định dạng thay cho cấu trúc câu |
| T6 | Emoji |

Typography chỉ được sửa khi văn bản đồng thời có ít nhất một pattern V1–V20. Quy tắc này tránh việc skill thay đổi dấu câu hoặc định dạng chỉ vì sở thích.

### Blog, bài cá nhân, nội dung công việc và marketing (B1–B17)

| # | Pattern |
|---|---|
| B1 | Sáo ngữ tôn vinh tầm quan trọng |
| B2 | Ẩn dụ có sẵn và thành ngữ dịch sát từ tiếng Anh |
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
| B17 | Trộn mức độ trang trọng không chủ đích |

### Tài liệu kỹ thuật, doanh nghiệp và học thuật (K1–K5)

| # | Pattern |
|---|---|
| K1 | Viết theo diff thay vì mô tả hiện trạng |
| K2 | Sáo ngữ thể chế rỗng ngoài văn bản pháp quy |
| K3 | Bộ đề mục Hán-Việt đối xứng rỗng |
| K4 | Mô tả hiện tượng mà không đưa hiện tượng ra |
| K5 | Câu dẫn nhập rỗng sau đề mục |

Profile này còn yêu cầu không thêm tiểu từ, ý kiến hoặc ngôi thứ nhất; không thay thuật ngữ chỉ để tránh lặp; không thuần Việt hoá thuật ngữ đã được định nghĩa.

## Những điểm khác với skill humanizer tiếng Anh

**Lặp từ không tự động là lỗi.** Trong tài liệu kỹ thuật, một thuật ngữ cần được gọi nhất quán. Ở văn xuôi, việc lặp danh từ cũng có thể giúp người đọc biết câu sau vẫn nói về cùng đối tượng. Chỉ thay khi bản thân từ đang sai hoặc chuỗi đồng nghĩa làm đối tượng bị đổi tên liên tục.

**En dash không bị cấm.** Dấu `–` có những chức năng hợp lệ trong tiếng Việt, như lời thoại, gạch đầu dòng, quan hệ giữa hai tên riêng và khoảng thời gian. T2 chỉ xem xét em dash `—` cùng các dấu ngang được dùng để chèn chú thích giữa câu.

**Ngoặc kép không bị ép về một hình dạng duy nhất.** Word, Google Docs và hệ điều hành có thể tự chuyển ngoặc thẳng thành ngoặc cong. T3 kiểm tra sự nhất quán trong cùng văn bản, không sửa theo sở thích của công cụ.

## Những khác biệt chính tả không dùng để suy đoán tác giả

Skill không tự động chọn giữa dấu thanh kiểu cũ và mới, như *hòa / hoà*, hoặc giữa *i / y*, như *kĩ / kỹ*. Đây là khác biệt chuẩn chính tả và quy ước xuất bản. Skill chỉ giữ cách viết nhất quán trong phạm vi văn bản, trừ khi người dùng yêu cầu theo một chuẩn cụ thể.

Khoảng trắng trước dấu câu, lỗi gõ và biến thể chính tả cũng không được dùng làm bằng chứng về tác giả. Có thể sửa chúng khi người dùng yêu cầu làm sạch văn bản, nhưng không suy ra ai đã viết.

## Memory cá nhân và nhật ký hiệu chuẩn

Hai cơ chế này phục vụ hai mục đích khác nhau.

### Memory hoặc knowledge base của agent

Đây là nơi phù hợp để lưu đặc tính riêng của một người dùng, nếu nền tảng và chính sách lưu trữ cho phép. Hồ sơ nên ngắn và chỉ chứa thông tin cần cho việc giữ giọng:

- cách xưng hô;
- nhịp và độ dài câu thường dùng;
- mức dùng từ Hán-Việt;
- cách chêm tiếng Anh;
- thói quen viết hoa và dấu câu;
- phạm vi áp dụng cùng một ví dụ ngắn.

Agent phải xác định đúng người trước khi nạp hồ sơ, không dùng hồ sơ của người này cho người khác và không lưu dữ kiện cá nhân không liên quan. Yêu cầu hiện tại luôn được ưu tiên hơn memory cũ.

### `calibration/LOG.md`

Đây là nhật ký bằng chứng dùng để bảo trì quy tắc chung của skill, không phải hồ sơ cá nhân. Chỉ ghi vào log khi phản hồi cho thấy:

- một pattern sửa nhầm câu vốn đúng;
- mục **Không flag** còn thiếu trường hợp loại trừ;
- skill bỏ sót một lỗi có thể gọi tên;
- người bản ngữ nêu một quy tắc tiếng Việt có thể kiểm tra độc lập.

Khác biệt chỉ thuộc sở thích cá nhân không được đưa vào log. Nhờ ranh giới này, skill không âm thầm học giọng của một người rồi áp lên mọi người dùng khác.

Quy trình đầy đủ nằm trong `AGENTS.md`.

## Mức độ tin cậy và nguồn

Mỗi quy tắc phải chỉ rõ nó dựa trên tài liệu, quan sát có bản đối chiếu trong `calibration/LOG.md` hay suy luận từ khác biệt giữa tiếng Anh và tiếng Việt. Repo chưa có bộ ngữ liệu đủ để đặt ngưỡng tần suất, nên số lần xuất hiện chỉ giúp tìm chỗ cần đọc lại.

### Nguồn quy phạm và học thuật

| Nguồn | Nội dung được dùng |
|---|---|
| [Nghị định 30/2020/NĐ-CP, Phụ lục II](https://thuvienphapluat.vn/chinh-sach-phap-luat-moi/vn/bieu-mau/55095/tong-hop-cac-phu-luc-ve-van-ban-hanh-chinh-moi-nhat-ban-hanh-kem-theo-nghi-dinh-30-2020) | Cách viết hoa tên cơ quan trong văn bản hành chính, dùng cho T1 |
| [Quyết định 1989/QĐ-BGDĐT năm 2018](https://thuvienphapluat.vn/van-ban/Giao-duc/Quyet-dinh-1989-QD-BGDDT-2018-quy-dinh-chinh-ta-Chuong-trinh-sach-giao-khoa-giao-duc-pho-thong-445355.aspx) | Điều 8 và 9, dùng để xác định phạm vi của dấu thanh và i/y |
| [ViDetect, arXiv:2405.03206](https://arxiv.org/abs/2405.03206) | Nghiên cứu phát hiện văn bản AI tiếng Việt; không dùng làm danh sách pattern ngôn ngữ |
| [VietBinoculars, arXiv:2509.26189](https://arxiv.org/abs/2509.26189) | Nghiên cứu phát hiện văn bản AI tiếng Việt; không dùng làm danh sách pattern ngôn ngữ |
| [A Survey on Zero Pronoun Translation, arXiv:2305.10196](https://arxiv.org/abs/2305.10196) | Tham khảo về lược đại từ và dịch thuật |
| [Nghiên cứu dịch câu bị động Anh–Việt](https://i-jte.org/index.php/journal/article/view/90) | Tham khảo cho V16; đối tượng nghiên cứu là người dịch |
| [Danh hoá động từ trong danh ngữ](https://tcgd.tapchigiaoduc.edu.vn/index.php/tapchi/article/view/4322) | Tham khảo cho V15 |
| [Cú pháp tiếng Việt nhìn từ ngữ pháp chức năng](https://vjol.info.vn/index.php/tdm/article/download/93747/79245/) | Tham khảo cho cấu trúc đề–thuyết ở V13 |
| [Tình thái từ](https://voer.edu.vn/c/tinh-thai-tu/4491bb06/712ccc96) và [tiểu từ tình thái trong hành động ngỏ lời](https://vusta.vn/mot-so-tieu-tu-tinh-thai-bieu-dat-tinh-lich-su-trong-hanh-dong-ngo-loi-bang-tieng-viet-p72715.html) | Tham khảo cho B14 |
| [Loại từ CON và CÁI](http://ngonngu.org/Con_Cai.htm) | Tham khảo cho V5 |

### Nguồn trình bày lại và nguồn cộng đồng

Những nguồn dưới đây giúp tìm thuật ngữ hoặc ghi nhận hiện tượng, không được dùng riêng làm căn cứ quy phạm:

- [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)
- [Wikipedia: Loại từ](https://vi.wikipedia.org/wiki/Lo%E1%BA%A1i_t%E1%BB%AB)
- [Wikipedia: Dấu gạch ngang](https://vi.wikipedia.org/wiki/D%E1%BA%A5u_g%E1%BA%A1ch_ngang)
- [Wikipedia: Dấu ngoặc kép](https://vi.wikipedia.org/wiki/D%E1%BA%A5u_ngo%E1%BA%B7c_k%C3%A9p)
- [Phân biệt gạch ngang và gạch nối, Giáo dục TP.HCM](https://giaoduc.edu.vn/phan-biet-dau-gach-ngang-va-gach-noi/)
- [Brands Vietnam: dấu hiệu nội dung viết bởi AI](https://help.brandsvietnam.com/vi/article/dau-hieu-nhan-biet-noi-dung-duoc-viet-boi-ai-3zy07d/)
- [Cặp quan hệ từ, HOCMAI](https://hoctot.hocmai.vn/dau-hieu-nhan-biet-quan-he-tu-va-cap-quan-he-tu.html)
- [Đề–thuyết, Ngày ngày viết chữ](https://ngayngayvietchu.com/thu-phan-tich-cau-tieng-viet-theo-cau-truc-de-thuyet/)

### Nguồn còn thiếu

- V3 và V13 cần thêm nguồn gốc về lý thuyết đề–thuyết thay cho các bài trình bày lại.
- V16 cần thêm nghiên cứu công bố trực tiếp về đối chiếu câu bị động Anh–Việt.

## Lời cảm ơn

Cách đóng gói và khung **Dấu hiệu / Vì sao / Sửa / Không flag** tham khảo [blader/humanizer](https://github.com/blader/humanizer) cùng hướng dẫn của WikiProject AI Cleanup. Các pattern tiếng Việt được xây dựng riêng cho repo này.

## Lịch sử phiên bản

- **0.5.1** – Chỉnh lại vài chỗ diễn đạt trong `SKILL.md`. Không thêm bớt pattern và không đổi hành vi.
- **0.5.0** – Viết lại toàn bộ tài liệu theo `SKILL.md`; bỏ các ngưỡng chưa hiệu chỉnh và những kết luận tuyệt đối; tách hồ sơ văn phong cá nhân sang memory hoặc knowledge base của agent; xác định `calibration/LOG.md` chỉ là nhật ký bằng chứng cho quy tắc dùng chung; đồng bộ lại profile, bảng tra, manifest và script quét.
- **0.4.0** – Thêm V20 để xử lý từ hoặc cụm từ bị thiếu một tiếng; sửa quy trình tự kiểm tra để tránh dùng lặp một cách chữa; mở rộng giao thức tiếp nhận quy tắc tiếng Việt do người bản ngữ nêu ra.
- **0.3.0** – Viết lại phần mở đầu README; bổ sung K4 về đoạn giải thích thiếu ví dụ và đổi pattern câu dẫn nhập thành K5.
- **0.2.2** – Mở rộng T4 cho dấu phẩy đứng trước *và*; thêm `scripts/scan-tells.sh`.
- **0.2.1** – Tự áp skill lên README; sửa lỗi diễn đạt và đồng bộ phần mô tả cấu trúc repo.
- **0.2.0** – Thêm giao thức hiệu chuẩn bằng phản hồi thực tế và `calibration/LOG.md`.
- **0.1.1** – Bổ sung các trường hợp loại trừ cho văn bản doanh nghiệp và thuật ngữ nội bộ.
- **0.1.0** – Bản đầu gồm V1–V19, T1–T6, B1–B17, K1–K4 và hai file tham chiếu.

## Giấy phép

MIT
