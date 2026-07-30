# Nhật ký hiệu chuẩn

File này lưu bằng chứng có thể làm thay đổi quy tắc dùng chung của skill. Mỗi quan sát được ghi thành một mục trước khi sửa pattern hoặc trường hợp loại trừ. Hồ sơ văn phong và sở thích cá nhân phải nằm trong memory hoặc knowledge base của agent, tách theo đúng người dùng; không ghi chúng vào đây.

Các mục bên dưới là hồ sơ lịch sử nên giữ nguyên câu trích dẫn và thuật ngữ dùng tại thời điểm ghi nhận, kể cả khi quy tắc sau đó đã được viết lại. Quy trình hiện hành nằm trong `AGENTS.md`, mục “Học từ phản hồi thực tế”.

---

## 2026-07-30 · báo cáo doanh nghiệp (kho vận)

**Nguồn:** bản vàng do Fioenix (người bản ngữ, chủ repo) viết lại output của skill.

**Đoạn skill xuất ra:**
> Đội kỹ thuật đã triển khai hệ thống quản lý kho mới để vận hành gọn hơn. Dữ liệu tồn kho đồng bộ nhanh, các cửa hàng xem được thông tin theo thời gian thực. Riêng độ trễ thì đội vẫn chưa giải quyết được.

**Bản vàng:**
> Nhằm mục đích nâng cao hiệu quả vận hành kho, team dev đã triển khai hệ thống quản lý kho mới. Dữ liệu tồn kho đồng bộ nhanh hơn, các cửa hàng xem được thông tin tồn kho theo thời gian thực. Riêng độ trễ của hệ thống thì team dev vẫn chưa giải quyết được.

**Khác biệt gọi tên được:**

| # | Khác biệt | Phân loại | Quyết định |
|---|---|---|---|
| 1 | "đội kỹ thuật" ↔ "team dev": register công việc IT dùng jargon, skill lại xuất tiếng Việt dịch sạch | Lỗi guard (V19 thiếu chiều sửa chủ động) | Sửa ở v0.1.1: V19 thêm chiều trả thuật ngữ bị dịch sạch về jargon |
| 2 | "vận hành gọn hơn" ↔ "nâng cao hiệu quả vận hành kho": skill hạ giọng quá tay, kéo báo cáo xuống văn nói | Lỗi guard (thiếu quy tắc thanh ngữ vực ở tầng chặn) | Sửa ở v0.1.1: thêm quy tắc chặn thứ tư + nới K2 cho cụm có bổ ngữ cụ thể |
| 3 | Giữ "Nhằm mục đích..." mở câu: skill coi là filler V9, người viết báo cáo thật dùng bình thường khi cụm có nội dung | Lỗi guard (V9 quá gắt với văn doanh nghiệp) | Sửa ở v0.1.1: nới guard V9 |
| 4 | Lặp "tồn kho", lặp "team dev" nguyên cụm qua các câu | Khớp quy tắc đảo chiều có sẵn, output của skill né lặp là sai hướng | Bổ sung ví dụ vào lệnh cấm số 3 của profile kỹ thuật ở v0.1.1 |
| 5 | "độ trễ" ↔ "độ trễ của hệ thống": bản vàng thêm định ngữ cho rõ | Sở thích cá nhân (cả hai đều tự nhiên) | Không sửa skill |

**Ghi chú:** n=1 nhưng người sửa là chủ repo và cả bốn lỗi guard đều gọi tên được, nên đủ ngưỡng theo giao thức. Đây cũng là entry mẫu cho định dạng log.

---

## 2026-07-30 · README của chính repo (tài liệu kỹ thuật)

**Nguồn:** chạy skill lên `README.md` theo yêu cầu của người dùng. Đây là self-application, không phải bản vàng của người thật, nên bằng chứng yếu hơn entry trên.

**Cổng thể loại:** README repo → profile `ky-thuat-doanh-nghiep`, tiểu từ tắt, V13 tắt, V15 và V16 nới, T5 nới mạnh, V19 giữ jargon.

**Bắt được, đều là lỗi thật:**

| Pattern | Chỗ sai | Sửa |
|---|---|---|
| T2 | Em dash chú thích giữa câu: *"phá địa danh và mọi lời thoại — hỏng nội dung"* | Thay bằng *"tức là hỏng nội dung chứ không phải..."* |
| V7 | *"Đừng dùng kết quả của nó như bằng chứng"*, *của* thừa theo khuôn *of* | Bỏ *của nó* |
| V16 | *"Bộ pattern tiếng Việt được xây mới hoàn toàn"* | *"thì xây mới hoàn toàn"* |
| V3 | *"Chép cả cây thư mục vào chỗ harness của bạn tìm skill"*, mệnh đề quan hệ thiếu ranh giới | Viết lại thành *"vào thư mục skill của harness"* |
| T4 | Ba chỗ `, và`: một Oxford comma thật (*"tìm trong lock, không thấy, và báo lỗi"*), hai chỗ comma-and nối mệnh đề kiểu Anh | Thay bằng *nên* và *mà… lại* |

**Cổng thể loại hoạt động đúng, ba lần từ chối sửa:**

- `, và` trong mục Lịch sử phiên bản: changelog nằm trong nhóm thể loại bị chặn. Để nguyên.
- *"một cách nhanh chóng"* và *"Điều quan trọng cần lưu ý là"* trong bảng pattern: đây là ví dụ đang được bàn tới, thuộc ngoại lệ văn bản thứ cấp. Để nguyên.
- Bullet có header và bảng dày đặc: T5 nới mạnh cho README. Để nguyên.

**Phân loại:** cả năm mục đều là **lỗi thật của văn bản**, không phải lỗi guard của skill. Skill bắn đúng, không bắn thừa. Không sửa pattern nào.

**Quan sát đáng ghi:** phần lớn công việc trong lượt này không phải sửa câu mà là vá nội dung đã lệch so với repo (cây thư mục thiếu `calibration/` và `scripts/`, số dòng bảng ghi sai, mục "việc bắt buộc cho v0.2" đã lỗi thời khi repo đang ở 0.2.0). Skill không bắt được loại lỗi này vì nó chỉ soi ngôn ngữ, không đối chiếu văn bản với thực tế. Nếu muốn agent tự bảo trì README, cần một bước kiểm tra riêng: đối chiếu mọi phát biểu về cấu trúc repo với cây thư mục thật. Chưa đủ cơ sở để thành pattern, ghi lại để theo dõi.

---

## 2026-07-30 · toàn bộ file nội dung của repo (tài liệu kỹ thuật)

**Nguồn:** chạy skill lên cả 8 file văn xuôi theo yêu cầu người dùng. Self-application, bằng chứng yếu hơn bản vàng.

**Phát hiện chính, và là lỗi guard thật:** T4 dính **25 chỗ trên 6 file**. Đây không phải lỗi lẻ tẻ mà là một thói quen hệ thống: dấu phẩy trước *và*, mang thẳng từ `, and` tiếng Anh sang.

Quan trọng hơn con số: **phần lớn không phải Oxford comma.** Chỉ khoảng một phần ba là liệt kê ba phần tử. Hai phần ba còn lại là *comma-and nối hai mệnh đề độc lập*, một lỗi khác hẳn mà T4 bản cũ **không mô tả**. T4 chỉ nói "dấu phẩy trước *và* trong liệt kê", nên agent quét đúng regex nhưng không biết phải làm gì với đa số hit.

| Phân loại | Quyết định |
|---|---|
| Lỗi guard: T4 thiếu hẳn nhánh comma-and nối mệnh đề | Sửa ở v0.2.2. Tách T4 thành hai nhánh (a) và (b), thêm bảng chọn hư từ theo quan hệ: *nên* cho nhân quả, *mà* cho tương phản, *còn… thì* cho đối lập cục bộ, *rồi* cho nối tiếp |

n=1 nhưng lỗi gọi tên được và tái diễn 15+ lần trong cùng một corpus, nên đủ ngưỡng.

**Các pattern khác:** V9, V12, V18 sạch hoàn toàn. V15 và V17 chỉ dính trong phần định nghĩa pattern và bảng Hán-Việt, đúng ngoại lệ văn bản thứ cấp. V16 sạch. T2 chỉ còn mention trong backtick.

**Cổng thể loại từ chối sửa 24 chỗ**, tất cả đều đúng: ví dụ trong phần định nghĩa pattern, trích dẫn trong chính log này, và mục Lịch sử phiên bản của README.

**Việc lặp lại đã được đóng gói:** lượt này phải dựng lại bộ lệnh grep từ đầu, giống hệt lượt review README hôm trước. Đã viết thành `scripts/scan-tells.sh` để lần sau chạy một lệnh. Script chỉ lo nhóm quét máy được, không thay được việc đọc.

---

## 2026-07-30 · phần mở đầu README (tài liệu kỹ thuật)

**Nguồn:** nhận xét trực tiếp của Fioenix về output, kèm bản viết lại do một chuyên gia viết tài liệu kỹ thuật thực hiện. Nhận xét nguyên văn: phần mở đầu "rất khô cứng, vô hồn, tối nghĩa".

Đây là nguồn bằng chứng loại 3 theo giao thức, nhưng nhận xét gọi tên được ba triệu chứng riêng biệt nên xử lý như bản vàng.

**Ba khoảng trống, đều là lỗi guard, đều sửa:**

| # | Khoảng trống | Bằng chứng | Sửa |
|---|---|---|---|
| 1 | Guard V14 trong profile kỹ thuật nới quá rộng | Câu mở đầu README cũ (*"Agent skill xoá dấu vết dịch máy và sáo ngữ trong văn bản tiếng Việt."*) là danh ngữ trần đứng làm câu trong văn xuôi, **sống sót qua hai lần chạy skill lên toàn repo** ở v0.2.1 và v0.2.2. Bảng ngưỡng ghi "Nới mạnh" đứng trước danh sách ngoại lệ, mà các ngoại lệ đó đều phi văn xuôi, nên agent đọc thành nới toàn cục | Nới theo **vị trí** chứ không theo tài liệu. Loại trừ tường minh câu mở đầu tài liệu và câu mở đầu mục |
| 2 | Không pattern nào bắt văn trừu tượng thiếu instance | Cả bốn nhóm V, T, B, K đều thao tác trên câu đã có. B1–B4 bắt rỗng kiểu thổi phồng, còn rỗng kiểu trừu tượng thì không ai bắt. Profile K phát biểu "văn trung tính và phẳng chính là giọng người đúng ở đây", mà câu đó đọc được thành giấy phép cho văn trừu tượng | Thêm **K4. Mô tả hiện tượng mà không đưa hiện tượng ra**. Ranh giới cốt lõi: trung tính nói về *giọng*, trừu tượng nói về *độ cụ thể*, hai thứ khác nhau. K4 cũ đổi số thành K5 |
| 3 | Ngưỡng 15% cấm đúng cách chữa duy nhất cho khoảng trống 2 | Chữa văn vô hồn là bổ sung instance, mà bổ sung instance thì gần như luôn vượt 15% và chạm quy tắc "Không bịa". Bản viết lại này vượt 24% chính vì lý do đó. Không mở ngoại lệ thì agent ở chế độ file chỉ còn cách cắt, mà cắt lại làm đoạn trừu tượng thêm | Ngoại lệ hẹp có guard: được vượt ngưỡng khi ví dụ **đã tồn tại ở nơi khác trong cùng tài liệu hoặc cùng repo**, tức chỉ kéo lên tuyến đầu chứ không sáng tác |

**Skill đã có phanh chống hạ giọng quá tay (mục "Đúng thanh ngữ vực" thêm ở v0.1.1) nhưng chưa có phanh đối xứng chống trừu tượng hoá quá tay.** K4 lấp đúng chỗ đó.

**Một ứng viên pattern lõi, KHÔNG thêm vì chưa đủ ngưỡng:**

Câu bị chê "tối nghĩa" nhất là *"Tiếng Việt mã hoá bằng hư từ, tiểu từ và loại từ những thứ tiếng Anh mã hoá bằng biến tố, ngữ điệu và mạo từ."* Bổ ngữ trực tiếp bị đẩy ra sau một cụm phương tiện ba thành phần. Tiếng Anh dịch chuyển danh ngữ nặng ra sau khá thoải mái, tiếng Việt thì không. V10 chỉ lo trật tự trạng ngữ, V18 lo câu lồng và độ dài, không cái nào bắt chỗ này.

Tên tạm: **bổ ngữ trực tiếp bị đẩy ra sau cụm phương tiện dài**. Dấu hiệu: `động từ + bằng/với/thông qua + chuỗi ≥3 thành phần + rồi mới tới bổ ngữ`. Cách sửa: kéo bổ ngữ về sát động từ rồi tách cụm phương tiện thành mệnh đề riêng.

**Quyết định: chưa thêm.** Giao thức yêu cầu pattern mới cần n≥3 mẫu độc lập, hiện mới có n=1. Ghi lại để đối chiếu khi gặp mẫu thứ hai và thứ ba. Ba khoảng trống ở trên thì thêm được vì chúng là *lỗi guard*, ngưỡng n=1 khi lỗi gọi tên được.

---

## 2026-07-30 · phần mở đầu README, vòng hai (bản vàng của người bản ngữ)

**Nguồn:** Fioenix tự viết lại phần mở đầu, dùng **chính câu tôi vừa commit ở v0.3.0** làm ví dụ xấu. Bằng chứng loại 1, mạnh nhất.

**Câu bị bắt:** *"Câu trên đúng ngữ pháp mà đọc lên thấy hụt."*

Hai lỗi trong một câu bảy chữ, cả hai đều nằm ngoài tầm bắt của bộ pattern lúc đó.

### Phát hiện 1: từ ghép bị cắt còn một âm tiết

Nhận xét nguyên văn: *"từ 'hụt' là một từ rất hiếm khi xuất hiện như một từ đơn, thông thường nó phải là một thành phần trong từ ghép như hụt hẫng, hụt hơi, thiếu hụt"*.

Đây là phát biểu về tiếng Việt, không phải về sở thích, và kiểm chứng được bằng khả năng đứng đơn của âm tiết. Cùng cơ chế với V1: model dịch phần đầu rồi dừng, chỉ khác vị trí. V1 rụng bổ ngữ sau động từ, cái này rụng nửa sau của từ ghép.

**Quyết định:** thêm **V20. Từ ghép bị cắt còn một âm tiết**, đặt ở cuối thay vì chèn giữa để không phải đánh số lại 17 pattern. Trỏ chéo với V1.

### Phát hiện 2: over-correction do chính bản vá T4 gây ra

Nhận xét: *"Từ 'mà' và 'nhưng' tuy gần nghĩa nhưng cách dùng phổ biến không giống nhau"*.

Truy ngược thì đây là **vết thương tự gây**. Bản vá T4 ở v0.2.2 đưa danh sách thay thế `nên / mà / còn…thì / rồi` **mà bỏ sót *nhưng***, liên từ đối lập mặc định của văn viết. Agent gom mọi quan hệ tương phản về *mà*. Đo lại toàn repo trước khi sửa:

| File | *mà* | *nhưng* |
|---|---|---|
| SKILL.md | 46 | 8 |
| README.md | 14 | 4 |
| profiles/ky-thuat-doanh-nghiep.md | 7 | 1 |

Gần 6:1 nghiêng về *mà*. Bản vá xoá một tell rồi dựng lên một tell khác: sự đồng nhất từ vựng.

**Đây là lỗi cấp phương pháp, không phải lỗi cấp pattern.** Skill giàu phần *phát hiện* mà nghèo phần *thay bằng gì*. Mỗi pattern có "Dấu hiệu" dài còn "Sửa" thì thường chỉ là một danh sách ngắn, nên agent chọn mục đầu rồi dùng mãi.

**Ba bản vá phương pháp:**

1. **Cặp thay thế phải có điều kiện chọn, không phải danh sách phẳng.** T4 giờ là bảng có cột "ghi chú chọn từ", nêu rõ *nhưng* là mặc định còn *mà* hẹp hơn nhiều.
2. **Mỗi pattern có nguy cơ over-correction phải tự khai báo phanh.** T4 thêm mục "Phanh over-correction" kèm phép đếm cụ thể. Mục "Mật độ khi sửa" thêm dòng về tỉ lệ giữa các lựa chọn thay thế, không chỉ tổng số.
3. **Thêm bước 6 vào Quy trình: soi lại chính bản sửa của mình.** Đếm từ thay thế dùng nhiều nhất, lệch hẳn về một phía là chữa quá tay.

### Phát hiện 3: giao thức thiếu một loại bằng chứng

Cả hai phát hiện trên đều là người bản ngữ nêu quy tắc ngôn ngữ học kèm instance, mà giao thức chỉ có ba loại nguồn: bản vàng, văn bản người bản ngữ, nhận xét về pattern. Không loại nào mô tả đúng trường hợp này.

**Thêm loại 4 vào `AGENTS.md`:** người bản ngữ nêu quy tắc ngôn ngữ học kèm ít nhất một instance. Khác "sở thích cá nhân" ở chỗ đây là phát biểu về *tiếng Việt* chứ không phải về *thị hiếu*. n=1 đủ để thêm pattern mới, với điều kiện quy tắc kiểm chứng được độc lập. Đây là lý do V20 vào được ngay dù chỉ có một instance.

### Ba chỗ tôi sửa khi áp bản của Fioenix

- *"hụt hẫn"* → *"hụt hẫng"* và *"gần nghĩ"* → *"gần nghĩa"*: lỗi gõ.
- *"sáo ngữ (kiểu viết lặp đi lặp lại)"*: bỏ phần chú giải. Sáo ngữ là cụm mòn sáo rỗng chứ không phải lặp lại, và bản thân skill có quy tắc đảo chiều nói lặp từ trong tiếng Việt là chuẩn mực. Giữ chú giải này sẽ mâu thuẫn.
- *"hướng dẫn AI viết thuần Việt hơn"* → *"viết tiếng Việt tự nhiên hơn"*: quy tắc "Đúng thanh ngữ vực" nói đích đến không phải nôm na nhất có thể, nên đặt chữ *thuần Việt* ở câu định vị sẽ cấp phép cho đúng lỗi mà v0.1.1 đã vá. Cần Fioenix xác nhận.

---

## 2026-07-30 · câu hướng dẫn trong SKILL.md (tài liệu kỹ thuật)

**Nguồn:** Fioenix sửa trực tiếp một câu do agent viết. Bản sửa là bản vàng; nhận xét kèm theo là phát biểu của người bản ngữ về cách dùng từ.

**Câu agent viết:**
> Chỉ được rà typography, không áp pattern nào khác.

**Bản vàng:**
> Chỉ được rà soát typography, không áp pattern nào khác.

**Khác biệt gọi tên được:** V20 mới bắt hai trường hợp: âm tiết không đứng riêng được (*rườm*) và âm tiết đứng riêng nhưng đổi nghĩa (*hụt*). Nó chưa bắt trường hợp một tiếng vẫn có nghĩa gần đúng nhưng câu đang cần đơn vị hai tiếng đầy đủ theo register, ở đây là *rà soát* trong văn hướng dẫn.

**Kiểm chứng độc lập:** nhận xét "*rà* gần như không bao giờ đứng đơn" không đúng nếu hiểu thành quy tắc tuyệt đối. Từ điển ghi *rà* là động từ độc lập với nghĩa "duyệt lại, soát lại" và cho ví dụ *"Rà kế hoạch một lần nữa"*. *Rà soát* có nghĩa hẹp hơn: xem kĩ lại, kiểm tra từng chi tiết sau khi đã hoàn thành. Vì vậy không được sửa máy móc mọi `rà + tân ngữ`.

Nguồn đối chiếu:

- https://home.vndic.net/r%C3%A0-vi_vi.html
- https://cdn.tailieu.vn/files/samples/2021/20210810/ganuongmuoixa/128998_251__8085.pdf, trang 19

**Phân loại:** lỗi guard của V20, n=1 đủ vì có bản vàng và ranh giới kiểm chứng được.

**Quyết định:** giữ số V20, đổi tên theo hướng trung tính thành **Đơn vị hai tiếng bị cắt còn một tiếng** và thêm dạng thứ ba. Chỉ flag khi ngữ nghĩa cùng register đòi hỏi đơn vị đầy đủ. Không flag *rà lại tài liệu, rà kỹ, rà một lượt, rà kế hoạch một lần nữa*; các nghĩa chuyên biệt như *rà mìn, rà sóng, rà kim, máy bay rà thấp*; hoặc cách nói nội bộ như *rà code, rà log* khi mẫu giọng cho phép.

**Ghi chú phân loại từ:** không dùng phát biểu "*rà soát* là từ ghép thuộc thể loại từ láy". *Từ ghép* và *từ láy* là hai nhánh phân loại khác nhau; việc xác định chính xác cấu tạo của *rà soát* không cần thiết để phát hiện lỗi này. Tên pattern dùng *đơn vị hai tiếng* để tránh gắn một nhãn ngôn ngữ học chưa được chứng minh.

---

## 2026-07-30 · bảng chọn profile trong SKILL.md (tài liệu kỹ thuật)

**Nguồn:** Fioenix nhận xét trực tiếp về phần hướng dẫn do agent viết.

**Đoạn bị nhận xét:**
> Áp dụng được, nhưng nạp profile và tham số khác nhau.

Bảng ngay sau đó dùng các nhãn *Tiểu từ bật*, *Tiểu từ tắt*, *V15, V16 nới*, *V19: không kết luận* và *lỗi register*.

**Nhận xét của người dùng:** câu dẫn không hiểu được, và toàn bộ bảng phía sau cũng rất tối nghĩa. Đây là lối viết điển hình của AI.

**Khác biệt gọi tên được:** phần hướng dẫn đã biến một quy trình biên tập thành bảng cấu hình. Câu dẫn không nói rõ cái gì được áp dụng; động từ *nạp* mô phỏng thao tác của phần mềm; còn cột *Tham số* chỉ ghi các nhãn nội bộ mà không nêu hành động. Người đọc phải tự biết nội dung của V15, V16, V19 và tự suy ra *bật*, *tắt*, *nới* sẽ thay đổi cách sửa ra sao.

**Phân loại:** ứng viên pattern mới về chỉ dẫn bị nén thành mã cấu hình, hiện có n=1. Chưa đủ bằng chứng để thêm pattern.

**Quyết định:** không thêm pattern mới. Viết lại riêng phần chọn profile thành bốn nhánh hành động. Mỗi nhánh phải nói đủ: thể loại nào thuộc nhánh đó, đọc file nào, phải rà pattern nào, phải giữ gì và phải tránh gì. Đồng thời thay câu *Nạp profile tương ứng* trong quy trình bằng một chỉ dẫn đầy đủ chủ thể và điều kiện.

Khi tự rà bản sửa, phát hiện cổng cũ xếp *SOP* vào cả nhóm bị chặn lẫn nhóm dùng profile kỹ thuật. *Tài liệu API* cũng bị chặn nguyên khối, trong khi profile kỹ thuật lại có quy tắc riêng cho phần văn xuôi của loại tài liệu này. Chốt lại ranh giới theo loại nội dung: biên tập phần văn xuôi bằng profile kỹ thuật; giữ nguyên code, câu lệnh, schema và bảng tham số.

---

## 2026-07-30 · bước 6 của quy trình tự rà (tài liệu kỹ thuật)

**Nguồn:** Fioenix nhận xét trực tiếp về một chỉ dẫn trong `SKILL.md`.

**Đoạn bị nhận xét:**
> Đếm từ thay thế bạn dùng nhiều nhất, so với các lựa chọn còn lại. Lệch hẳn về một phía là dấu hiệu chữa quá tay, quay lại trộn cho đều.

**Nhận xét của người dùng:** câu khó hiểu nên không thể xác định chỉ dẫn đúng hay sai.

**Khác biệt gọi tên được:** câu dùng các khái niệm không có tiêu chí kiểm tra như *lệch hẳn* và *trộn cho đều*. Nghiêm trọng hơn, nó lấy phân bố từ vựng làm thước đo đúng sai. Một từ có thể lặp nhiều lần vì nhiều câu cùng mang một quan hệ nghĩa; đổi từ cho đều sẽ tạo chuỗi đồng nghĩa giả và mâu thuẫn với quy tắc không sửa câu chỉ vì lặp từ.

Truy ngược cho thấy cùng giả định sai còn nằm ở phanh T4 (*mà* nhiều hơn *nhưng* thì coi là chữa quá tay) và mục mật độ khi sửa (*nhưng* phải nhiều hơn *mà*). Tỉ lệ từng đo được trong repo chỉ chứng minh bản vá cũ đã gom nhiều quan hệ khác nhau về một từ; nó không tạo ra một quy tắc phổ quát rằng văn viết đúng phải có tỉ lệ ngược lại.

**Phân loại:** lỗi guard của bản vá phương pháp, n=1 đủ vì chỉ dẫn hiện tại mâu thuẫn trực tiếp với quy tắc lặp từ trong cùng `SKILL.md`.

**Quyết định:** bỏ mọi chỉ tiêu phân bố giữa các từ thay thế. Sau khi sửa, kiểm tra từng chỗ theo chức năng ngữ nghĩa. Giữ nguyên từ lặp nếu từng lần dùng đều đúng; chỉ sửa khi một lựa chọn bị áp máy móc cho những quan hệ nghĩa khác nhau. Cập nhật đồng thời bước 6, phanh T4 và mục mật độ để skill không còn tự mâu thuẫn.

---

## 2026-07-30 · rà lại phần Bốn quy tắc chặn

**Nguồn:** Fioenix yêu cầu đọc kỹ và cập nhật toàn bộ phần `Bốn quy tắc chặn` trong `SKILL.md`.

**Khoảng trống 1: ngưỡng 15% được dùng như điều kiện cứng.** Tỉ lệ độ dài không đo được mức thay đổi về nghĩa. Thêm một hư từ vào câu ngắn có thể vượt 15% mà không thêm thông tin; một bản viết lại dài hơn ít hơn 15% vẫn có thể đổi chủ thể, mức độ chắc chắn hoặc quan hệ nhân quả. Bản thân phần nền tảng bằng chứng cũng nói các ngưỡng số chưa được hiệu chuẩn trên corpus.

**Khoảng trống 2: ba câu hỏi chỉ kiểm tra lỗi thiếu hư từ.** Câu hỏi đầu tiên bắt buộc agent phải gọi tên một hư từ còn thiếu. Điều kiện này phù hợp với một phần V1–V6 nhưng không áp dụng được cho V7–V20, profile B, profile K hoặc typography. Nếu tuân thủ đúng câu chữ thì phần lớn skill sẽ không bao giờ được phép sửa.

**Khoảng trống 3: quy tắc không bịa dùng sai tiêu chí.** Câu *"Không có con số thì cắt câu sáo ngữ"* lấy số liệu làm đại diện cho mọi chi tiết cụ thể. Bản gốc có thể không có con số nhưng vẫn có tên, sự kiện, hành động hoặc kết quả đủ để thay câu sáo rỗng. Điều cần chặn là dữ kiện mới, không phải câu thiếu con số.

**Khoảng trống 4: chưa chặn thay đổi ý.** Phần cũ yêu cầu đúng thanh ngữ vực nhưng chưa cấm rõ việc đổi chủ thể, thời điểm, quan hệ nhân quả, mức độ chắc chắn hoặc mức cam kết.

**Phân loại:** lỗi guard nội bộ, không phải pattern ngôn ngữ mới.

**Quyết định:** giữ bốn lớp an toàn nhưng viết lại thành bốn điều kiện áp dụng cho từng chỗ sửa: gọi tên được lỗi và loại trừ guard; không thêm dữ kiện; giữ nguyên ý và đúng giọng văn; chỉ sửa đúng phạm vi cần thiết. Bỏ ngưỡng 15% như điều kiện cứng. Giữ nguyên nguyên tắc của K4: chỉ được đưa ví dụ có sẵn trong phạm vi người dùng giao xử lý lên gần phần giải thích.

---

## 2026-07-30 · ranh giới ưu tiên của mẫu văn

**Nguồn:** Fioenix nhận xét trực tiếp về một câu trong `SKILL.md`.

**Đoạn bị nhận xét:**
> Mẫu văn thắng mọi quy tắc trong skill này, kể cả T2 và V19. Một người viết đúng chuẩn của họ không phải là một người viết sai.

**Nhận xét của người dùng:** câu không rõ nghĩa.

**Khác biệt gọi tên được:** *thắng mọi quy tắc* là một mệnh đề tuyệt đối nhưng không nói mẫu văn được ưu tiên ở phương diện nào. *Đúng chuẩn của họ* cũng không xác định đó là thói quen phong cách, lỗi lặp lại hay yêu cầu của thể loại. Nếu làm theo mặt chữ, agent có thể giữ lỗi gõ, lỗi ngôn ngữ hoặc vi phạm bốn quy tắc chặn chỉ vì lỗi đó xuất hiện trong mẫu.

**Phân loại:** lỗi guard và thứ tự ưu tiên, không phải pattern ngôn ngữ mới.

**Quyết định:** mẫu văn chỉ được ưu tiên đối với thói quen phong cách xuất hiện nhất quán, như nhịp câu, xưng hô, cách chêm tiếng Anh và kiểu dấu câu. Một trường hợp đơn lẻ không đủ để suy ra thói quen. Thứ tự ưu tiên được ghi rõ: yêu cầu hiện tại của người dùng, quy chuẩn thể loại, thói quen ổn định trong mẫu, rồi mới đến quy tắc phong cách mặc định. Mẫu văn không vượt qua bốn quy tắc chặn và không hợp thức hoá lỗi ngôn ngữ rõ ràng.

---

## 2026-07-30 · tiêu đề LÕI và phạm vi V1–V20

**Nguồn:** Fioenix nhận xét trực tiếp về tiêu đề và câu giải thích trong `SKILL.md`.

**Đoạn bị nhận xét:**
> LÕI: lỗi ngôn ngữ
>
> Nhóm này là lỗi bất kể văn bản thuộc register nào. Sửa chúng không đụng tới giọng người viết.

**Nhận xét của người dùng:** cả tiêu đề lẫn câu giải thích đều khó hiểu.

**Khác biệt gọi tên được:** *lõi* là nhãn kiến trúc nội bộ nhưng không cho biết phần này kiểm tra cái gì. Câu tiếp theo dùng *register* không cần thiết, thiếu chủ thể rõ ràng trong cụm *nhóm này là lỗi* và đưa ra hai mệnh đề tuyệt đối. Nó còn mâu thuẫn với cổng thể loại vì V1–V20 không được chạy trên những thể loại đã bị chặn.

**Phân loại:** lỗi diễn đạt và mô tả sai phạm vi, không phải pattern ngôn ngữ mới.

**Quyết định:** đổi tiêu đề thành **Lỗi dùng từ và cấu trúc câu**. Nói rõ V1–V20 chỉ chạy trên những thể loại mà cổng cho phép biên tập; điểm khác với profile là chúng không phụ thuộc vào giọng cá nhân hay giọng trung tính, nhưng từng pattern vẫn phải qua mục **Không flag**. Bỏ từ *lõi* ở bước 2 của quy trình và cổng typography, thay bằng phạm vi cụ thể V1–V20.

---

## 2026-07-30 · rà toàn bộ V1–V20 sau chuỗi phản hồi về văn phong

**Nguồn:** Fioenix yêu cầu tự rà và cập nhật toàn bộ phần `Lỗi dùng từ và cấu trúc câu` trước khi giao lại review.

**Phạm vi:** phần giới thiệu V1–V20, năm tiêu đề nhóm, nội dung bốn mục của từng pattern và quy tắc về lặp từ ngay sau V20. Không sửa typography T1–T6 hoặc các profile trong lượt này.

**Những lỗi hệ thống được phát hiện:**

1. **Ẩn dụ và câu mô phỏng máy móc:** *động từ đứng trơ, rụng nặng nhất, model dịch rồi dừng, dấu phẩy trơ, phổi muốn ngắt, model luôn với tay vào*. Các câu này tạo cảm giác giải thích nhưng không cho agent một tiêu chí kiểm tra.
2. **Ngưỡng chưa hiệu chuẩn bị dùng như kết luận:** 20 âm tiết ở V2, ba lần *các* ở V8, một phần ba số câu ở V12, 5/6 và 4/6 câu ở V13, 3 lần trên 100 âm tiết ở V15, 45 âm tiết ở V18. Những ngưỡng này mâu thuẫn với phần nền tảng bằng chứng của chính skill.
3. **Khẳng định tuyệt đối làm guard bắn quá rộng:** *không bao giờ để hai của*, *vắng tiếng Anh mới là tell*, *không dân bán lẻ Việt nào...*, *model không bao giờ chọn*. Tất cả đều bỏ qua người đọc, thể loại và mẫu giọng.
4. **Ví dụ không đạt bốn quy tắc chặn:** V5 sửa *mua xe mới*, một câu tiếng Việt tự nhiên; V14 lấy một câu có vị ngữ làm ví dụ cho danh ngữ trần rồi tự thêm *mỗi giây*; V18 tự thêm *điểm bán đông khách*; V6 tự gán quan hệ *anh / em* khi bản gốc không có.
5. **Mô tả sai hoặc thiếu guard:** V7 coi hai chữ *của* là lỗi tự động; V8 coi *các thông tin* luôn sai; V16 xem mọi *bởi + tác nhân* như cùng một cấu trúc; V17 gom cả *mang lại* vào nhóm thay cho *là / có*; V19 lấy cách chêm tiếng Anh làm phép phân biệt *Người thật / Model*.
6. **Hợp đồng bốn mục chưa nhất quán:** V19 không có đủ nhãn **Dấu hiệu, Vì sao, Sửa, Không flag** như AGENTS.md yêu cầu.

**Phân loại:** đợt sửa guard và diễn đạt cho các pattern có sẵn, không thêm pattern mới và không thay số hiệu.

**Quyết định:** viết lại V1–V20 theo cùng một khung bốn mục; bỏ ngưỡng số chưa hiệu chuẩn; thay kết luận tuyệt đối bằng điều kiện theo ngữ cảnh; sửa ví dụ để không thêm dữ kiện và không sửa câu vốn đúng; đổi các tiêu đề nhóm sang tiếng Việt nói rõ đối tượng kiểm tra. V19 chỉ đánh giá độ phù hợp với người đọc và cộng đồng sử dụng, không dùng sự có mặt của tiếng Anh làm bằng chứng người hay AI. Quy tắc lặp từ chuyển từ tuyên bố về khác biệt Anh – Việt sang chỉ dẫn thực tế về thuật ngữ và đối tượng quy chiếu.

---

## 2026-07-30 · V10 coi "một cách nhanh chóng" là lỗi

**Nguồn:** Fioenix nhận xét trực tiếp về bản V10 sau lượt rà toàn bộ V1–V20.

**Nhận xét của người dùng:** *một cách nhanh chóng* là một cụm từ hợp lệ trong tiếng Việt, nên V10 hiện tại chưa đúng.

**Khác biệt gọi tên được:** V10 đã gộp một lựa chọn phong cách hợp lệ với lỗi vị trí trạng ngữ. Việc một cụm có thể rút ngắn mà không đổi nghĩa không làm cụm dài hơn trở thành lỗi ngôn ngữ. Mức độ súc tích còn phụ thuộc thể loại và mẫu giọng, nên nếu cần điều chỉnh thì phải xử lý ở profile hoặc theo yêu cầu người dùng, không đặt trong nhóm V1–V20.

**Phân loại:** lỗi guard của V10, n=1 đủ vì ví dụ bị flag là một cấu trúc tiếng Việt hợp lệ và điều này kiểm tra được ngay bằng phạm vi của pattern.

**Quyết định:** bỏ hoàn toàn *một cách + tính từ* khỏi **Dấu hiệu** và **Sửa** của V10. Thu hẹp V10 vào trường hợp vị trí trạng ngữ làm mơ hồ phạm vi bổ nghĩa hoặc cắt rời chủ thể khỏi động từ. Ghi rõ trong **Không flag** rằng *một cách nhanh chóng, một cách hiệu quả* và các cụm tương tự đều hợp lệ; rút gọn chúng chỉ là lựa chọn phong cách.

---

## 2026-07-30 · tách hẳn "một cách + tính từ" khỏi V10

**Nguồn:** Fioenix tiếp tục review V10 sau bản sửa guard.

**Nhận xét của người dùng:** trạng ngữ chỉ thời gian và *một cách + tính từ* là hai hiện tượng khác nhau, không nên cùng nằm trong V10.

**Khác biệt gọi tên được:** bản sửa trước đã bỏ *một cách + tính từ* khỏi phần phát hiện nhưng vẫn giữ nó trong **Không flag**. Vì vậy V10 vẫn gợi ra một mối quan hệ không tồn tại giữa lựa chọn từ ngữ và vị trí trạng ngữ.

**Phân loại:** lỗi ranh giới pattern.

**Quyết định:** xoá mọi nhắc đến *một cách + tính từ* khỏi V10. V10 chỉ còn xử lý vị trí và phạm vi bổ nghĩa của trạng ngữ. Cấu trúc *một cách + tính từ* không phải lỗi ngôn ngữ; không tạo pattern thay thế cho nó nếu chưa có bằng chứng về một lỗi khác có thể gọi tên và kiểm chứng độc lập.

---

## 2026-07-30 · kiểm chứng lại cách viết hoa tên cơ quan trong T1

**Nguồn:** Fioenix nhận xét trực tiếp về T1 và đề nghị kiểm tra lại ví dụ *Bộ Giáo dục* vì cho rằng *Bộ Giáo Dục* mới phù hợp với tiếng Việt.

**Kiểm chứng độc lập:** Phụ lục II Nghị định 30/2020/NĐ-CP quy định viết hoa chữ cái đầu của các từ, cụm từ chỉ loại hình, chức năng và lĩnh vực hoạt động của cơ quan, tổ chức. Tên chính thức trong văn bản và trang thông tin của Bộ được viết là *Bộ Giáo dục và Đào tạo*. Vì *Giáo dục* và *Đào tạo* là hai cụm chỉ lĩnh vực, chỉ chữ đầu mỗi cụm được viết hoa. Cách viết *Bộ Giáo Dục và Đào Tạo* không phù hợp với chuẩn hành chính này.

**Khác biệt gọi tên được:** ví dụ *Bộ Giáo dục và Đào tạo* trong T1 là đúng, nhưng phần giải thích lại nói quá rộng: tiếng Việt không chỉ viết hoa vì phép đặt câu và danh từ riêng; quy tắc tên cơ quan cũng không thể rút thành mẹo “viết hoa từ có nghĩa”. T1 còn trộn tiêu đề theo Title Case, tên cơ quan viết sai và danh từ chung được viết hoa để nhấn mà chưa nêu cách xác định riêng cho từng trường hợp.

**Phân loại:** nhận xét của người dùng dẫn đến kiểm chứng lại nguồn. Không chấp nhận ví dụ sửa vì trái với tên chính thức, nhưng sửa guard và cách giải thích của T1 vì pattern hiện tại quá tuyệt đối.

**Quyết định:** giữ *Bộ Giáo dục và Đào tạo*; viết lại T1 để phân biệt tiêu đề, tên cơ quan và chữ viết hoa để nhấn. Với tên cơ quan, ưu tiên tên chính thức hoặc tên đã đăng ký; chỉ dùng Phụ lục II làm chuẩn khi biên tập văn bản hành chính. Không suy cách viết hoa chỉ từ số âm tiết hay từ việc một tiếng có nghĩa riêng.

---

## 2026-07-30 · viết lại phần hướng dẫn sửa của T4

**Nguồn:** Fioenix nhận xét trực tiếp rằng phần từ bảng *Loại (b) chọn hư từ theo quan hệ* trở xuống trong T4 tối nghĩa.

**Khác biệt gọi tên được:** bảng cũ buộc người dùng phân biệt những nhãn trừu tượng như *tương phản gắn chặt* và *đối lập cục bộ* nhưng không chỉ ra cách nhận biết trong câu. Bảng cũng bỏ sót trường hợp *và* đang nối hai ý bổ sung và không cần thay. Nếu agent tự chọn *nên, nhưng, mà, còn... thì* chỉ dựa vào bảng, nó có thể thêm quan hệ nhân quả hoặc tương phản mà bản gốc không nêu. Dấu chấm phẩy không cùng hiện tượng với dấu phẩy trước *và* nhưng lại bị ghép vào cuối pattern.

**Phân loại:** lỗi diễn đạt, lỗi guard và lỗi ranh giới pattern.

**Quyết định:** thu hẹp T4 vào dấu phẩy đứng trước *và*. Bỏ bảng chọn hư từ, bỏ phần nói về dấu chấm phẩy và thay bằng một trình tự sửa trực tiếp: xác định đó là liệt kê hay hai vế câu; giữ *và* khi quan hệ chỉ là bổ sung; chỉ đổi liên từ khi chính câu gốc đã thể hiện rõ quan hệ khác; không rõ thì bỏ dấu phẩy, tách câu hoặc để nguyên, tuyệt đối không tự suy ra quan hệ nghĩa.

---

## 2026-07-30 · mở rộng T5 cho khuôn "nhãn: diễn giải"

**Nguồn:** Fioenix nêu một dạng LLM thường viết nhưng skill chưa mô tả đủ: heading hoặc đầu mỗi bullet bị chia thành *cụm từ khóa: diễn giải hoặc slogan*.

**Kiểm chứng độc lập:** dấu hai chấm vẫn xuất hiện hợp lệ trong tiêu đề tiếng Việt hiện nay, chẳng hạn tiêu đề dẫn lời, tiêu đề có phụ đề và các nhãn mang giá trị thật. Vì vậy không thể xem mọi heading có dấu hai chấm là lỗi. Tín hiệu hẹp hơn có thể kiểm tra được là nhiều heading hoặc bullet liên tiếp cùng bị ép vào khuôn nhãn–diễn giải, trong khi nhãn chỉ là một danh ngữ khái quát, không tạo ra trường dữ liệu, loại nội dung hay quan hệ giải thích riêng.

**Khác biệt gọi tên được:** T5 cũ chỉ bắt trường hợp nhãn ở đầu bullet lặp lại nguyên từ ngữ trong phần diễn giải. Nó bỏ sót trường hợp nhãn không lặp chữ nhưng vẫn thừa về chức năng, cũng như cùng khuôn xuất hiện ở heading. Nếu chỉ quét dấu hai chấm thì lại bắn nhầm tiêu đề báo chí, mục từ, nhãn–giá trị, lời thoại, glossary, FAQ và tài liệu tham chiếu.

**Phân loại:** mở rộng guard của pattern T5 có sẵn, không thêm pattern mới.

**Quyết định:** mở rộng **Dấu hiệu** của T5 sang chuỗi heading hoặc bullet dạng *nhãn khái quát: diễn giải/slogan*. Phép thử là bỏ nhãn mà phần sau vẫn làm trọn chức năng của heading hoặc câu. Phần **Sửa** hướng dẫn nhập nhãn vào câu hoặc bỏ nhãn, không xoá dấu hai chấm máy móc. Phần **Không flag** giữ các cấu trúc có hai vế thật: nhãn–giá trị, thuật ngữ–định nghĩa, người nói–lời nói, tiêu đề–phụ đề và các định dạng tham chiếu.

---

## 2026-07-30 · viết lại phần cuối SKILL.md

**Nguồn:** Fioenix yêu cầu review toàn bộ nội dung từ phần *Tín hiệu chạy ngược chiều* đến hết file vì vẫn còn nhiều câu mang giọng văn AI.

**Khác biệt gọi tên được:**

1. Nhiều kết luận tuyệt đối nhưng không có bằng chứng tương ứng: *model gần như không sinh lỗi này*, *người viết không bao giờ bỏ hư từ*, *sự bất nhất là chữ ký của lỗi dịch*.
2. Câu chữ phô trương hoặc đối lập quá mức: *bằng chứng NGƯỜI THẬT VIẾT*, *đúng ngược mục tiêu*, *phanh chống nhồi*, *đừng đụng vào*.
3. Phần *Quy tắc cụm* đặt ngưỡng ba hoặc bốn dấu hiệu và yêu cầu vắng hoàn toàn dấu hiệu người viết dù repo chưa hiệu chỉnh ngưỡng này.
4. Phần *Mật độ khi sửa* đưa ra nhiều chỉ tiêu số nhưng ngay cuối file lại thừa nhận chúng chưa được hiệu chỉnh trên corpus.
5. Phần *Chế độ gọi* và *Vòng phản hồi* trộn tiếng Anh không cần thiết, dùng các cụm như *pattern bắn sai, guard thiếu, voice memory* và chưa nói rõ khi nào chỉ trả bản sửa, khi nào kèm nhận xét.
6. Phần *Nền tảng bằng chứng* tuyên bố bao quát toàn bộ tình hình nghiên cứu và tỉ lệ pattern có nguồn mà không đưa ra phép đếm có thể kiểm tra ngay trong skill.

**Phân loại:** sửa diễn đạt, bỏ ngưỡng chưa hiệu chỉnh và siết guard cho các phần hướng dẫn vận hành; không thêm hoặc đổi số hiệu pattern.

**Quyết định:** viết lại toàn bộ phạm vi thành các phép kiểm tra trực tiếp. Không dùng lỗi gõ hay biến thể chính tả để suy đoán tác giả. Không đặt số lượng dấu hiệu hoặc mật độ từ làm ngưỡng cứng. Phân biệt câu ngắn với câu thiếu từ bằng mức độ rõ nghĩa và thể loại. Quy định đầu ra theo yêu cầu thực tế của người dùng. Phần bằng chứng chỉ nêu những gì repo hiện quản lý được: nguồn trong README, quan sát trong calibration log và các suy luận chưa có corpus hiệu chỉnh.

---

## 2026-07-30 · tách hồ sơ văn phong cá nhân khỏi calibration log

**Nguồn:** Fioenix đặt câu hỏi liệu `calibration/LOG.md` có phải cơ chế cá nhân hoá theo một người dùng hay không và đề nghị agent dùng memory hoặc knowledge base riêng để lưu đặc tính cá nhân.

**Khác biệt gọi tên được:** kiến trúc trong `AGENTS.md` đã phân biệt sở thích cá nhân với lỗi guard, nhưng `SKILL.md` chưa hướng dẫn agent nạp hồ sơ văn phong từ memory trước khi sửa. Phần *Khi người dùng sửa lại kết quả* còn yêu cầu ghi quan sát vào `calibration/LOG.md` ngay sau khi nêu cả ba loại khác biệt, nên có thể bị hiểu là sở thích cá nhân cũng phải vào log chung.

**Phân loại:** lỗi ranh giới giữa bộ nhớ dùng chung của skill và bộ nhớ riêng của agent.

**Quyết định:** `calibration/LOG.md` chỉ lưu bằng chứng có thể sửa quy tắc dùng chung: pattern bỏ sót, trường hợp loại trừ còn thiếu hoặc nhận xét ngôn ngữ có thể kiểm chứng. Hồ sơ văn phong cá nhân phải nằm trong memory hoặc knowledge base của agent, tách theo đúng người dùng. Trước khi sửa, agent nạp lại hồ sơ ấy nếu nền tảng hỗ trợ và danh tính người dùng đã rõ. Khi người dùng sửa kết quả, sở thích cá nhân được ghi lại ở đó nếu chính sách lưu trữ cho phép; không đưa vào calibration log. Yêu cầu hiện tại luôn được ưu tiên hơn memory, không dùng hồ sơ của người này cho người khác và không ghi lại dữ kiện cá nhân không cần thiết cho việc giữ giọng.

---

## 2026-07-30 · tự rà T5 trên các tiêu đề của SKILL.md

**Nguồn:** chạy `scripts/scan-tells.sh` sau khi mở rộng T5 và viết lại các tài liệu còn lại trong repo.

**Dấu hiệu:** tiêu đề chính cùng nhiều tiêu đề nhóm trong `SKILL.md` vẫn theo khuôn *nhãn: diễn giải*, như *“vi-humanizer: viết lại văn bản...”*, *“Nhóm 1: Thiếu hư từ...”* và *“Nhận diện: cái gì không được sửa”*. Phần sau dấu hai chấm đã làm trọn chức năng của tiêu đề; phần trước chỉ là số nhóm hoặc nhãn phân loại.

**Phân loại:** T5 bắt đúng trên chính tài liệu điều khiển. Đây là lỗi diễn đạt của heading, không phải trường hợp loại trừ mới.

**Quyết định:** viết các heading thành một cụm liền mạch và giữ số nhóm trong cấu trúc tài liệu thay vì trong câu chữ. Không sửa những dấu hai chấm có chức năng thật, như nhãn–giá trị hoặc mục phân loại trong danh sách bảo trì.

---

## 2026-07-30 · phần mở đầu SKILL.md mâu thuẫn với quy tắc nhận diện

**Nguồn:** đối chiếu toàn repo theo yêu cầu lấy `SKILL.md` làm chuẩn cho các tài liệu khác.

**Dấu hiệu:** phần mở đầu vẫn khẳng định skill phát hiện *“dấu vết AI viết”*, giải thích hiện tượng bằng khác biệt token giữa tiếng Anh và tiếng Việt, rồi nói con người không mở hoặc kết đoạn bằng sáo ngữ. Phần cuối của chính file lại quy định không dùng kết quả rà soát để kết luận tác giả. README mới cũng đã bỏ cách định vị này.

**Phân loại:** mâu thuẫn nội bộ và diễn đạt vượt quá bằng chứng hiện có. Không phải pattern mới.

**Quyết định:** định vị skill là công cụ biên tập lỗi dịch sát, thiếu từ, sai cấu trúc và sáo ngữ không hợp thể loại. Giữ LLM như một nguồn có thể tạo ra các lỗi này, nhưng không coi lỗi là bằng chứng về tác giả và không giải thích bằng suy đoán về token hay dữ liệu huấn luyện.
