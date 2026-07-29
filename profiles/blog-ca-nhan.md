# Profile: blog, bài viết cá nhân, nội dung công việc và marketing

Nạp cùng `SKILL.md` khi cổng thể loại xác định văn bản là blog, bài viết có giọng, nội dung công việc, chat nội bộ, LinkedIn, personal brand, hoặc marketing.

Nhóm này là **lỗi giọng**: có phải lỗi hay không phụ thuộc vào register. Chạy sau khi đã quét xong lõi V1–V19.

Tham số cho profile này: tiểu từ tình thái **bật**. Với nội dung công việc, LinkedIn, personal brand và marketing thì V19 chạy theo chiều "vắng chêm tiếng Anh là tell"; với blog cá nhân thì V19 không kết luận.

---

## Sáo ngữ và thổi phồng

### B1. Sáo ngữ tôn vinh tầm quan trọng

**Dấu hiệu:** *đóng vai trò quan trọng, giữ vai trò then chốt, đóng góp không nhỏ, góp phần không nhỏ, có ý nghĩa hết sức quan trọng, là yếu tố then chốt, mang tính quyết định, không thể phủ nhận rằng, tạo tiền đề vững chắc, đặt nền móng cho, khẳng định vị thế, ghi dấu ấn sâu sắc, là minh chứng rõ nét cho*.
**Vì sao:** lớp đệm ngữ nghĩa rỗng, bỏ cả cụm đi thì câu vẫn còn nguyên thông tin. Model chèn nó vào để làm câu đủ trọng lượng khi không có dữ kiện cụ thể để nói.
**Sửa:** *"Chuyển đổi số đóng vai trò quan trọng trong bán lẻ hiện đại."* → *"Bán lẻ hiện đại phụ thuộc vào hệ thống số: hết hàng tại cửa hàng nhưng còn ở kho thì đơn vẫn chốt được."* **Nếu không có chi tiết cụ thể để thay vào thì cắt câu, không bịa.**
**Không flag:** trích dẫn nguyên văn phát biểu của người khác.

### B2. Ẩn dụ kho sẵn và calque thành ngữ tiếng Anh

**Dấu hiệu:** *hành trình* (khi không ai đi đâu cả), *chìa khoá thành công, chìa khoá để, bức tranh toàn cảnh, cái nhìn toàn cảnh, ngọn hải đăng dẫn lối, đòn bẩy tăng trưởng, bệ phóng, cú hích, làn gió mới, mảnh ghép còn thiếu, kim chỉ nam, xương sống của, trái tim của hệ thống, mở ra cánh cửa, thắp lửa đam mê, chắp cánh ước mơ, đào sâu vấn đề, tạo ra cuộc cách mạng*. Nhóm calque từ tiếng Anh: *vào cuối ngày* (at the end of the day), *mở khoá tiềm năng, thay đổi cuộc chơi, bắt kịp đường cong, câu chuyện thành công, nằm ở chỗ*.
**Vì sao:** ẩn dụ đã chết, dùng để tránh phải nói chính xác điều gì xảy ra. Tell nặng nhất là khi một bài có ba bốn ẩn dụ loại này mà chúng không cùng trường nghĩa: vừa hành trình, vừa bệ phóng, vừa bức tranh.
**Sửa:** *"Đào tạo nội bộ chính là chìa khoá mở ra cánh cửa tăng trưởng, là bệ phóng đưa doanh nghiệp bước vào hành trình chuyển đổi số."* → *"Không đào tạo lại đội vận hành thì phần mềm mới sẽ bị dùng sai trong ba tháng đầu."*
**Không flag:** ẩn dụ đã thành thuật ngữ ngành, *hành trình khách hàng* trong tài liệu UX, *xương sống* trong mô tả hạ tầng mạng. Ẩn dụ được triển khai nhất quán và có chi tiết riêng: đó là dấu hiệu người viết. Thành ngữ Việt thật trùng hình với tiếng Anh (*con dao hai lưỡi*, *giọt nước tràn ly*).

### B3. Mở bài dẫn dắt vòng vo

**Dấu hiệu:** *Trong bối cảnh..., Trong thời đại..., Trong xã hội hiện đại ngày nay, Ngày nay khi..., Cùng với sự phát triển không ngừng của, Với sự bùng nổ của công nghệ, Trước những biến động của thị trường, Trong bài viết này chúng ta sẽ, Hãy cùng tìm hiểu, Dưới đây là một số*. Sáo ngữ Hán-Việt cùng chức năng: *Từ xa xưa, Kể từ thuở, Trải qua bao thăng trầm*.
**Vì sao:** câu mở không mang thông tin, chỉ dựng sân khấu. Tell nặng nhất là khi đoạn mở dài ba bốn câu mà xoá hết vẫn không mất gì.
**Sửa:** cắt thẳng vào nội dung. *"Trong bối cảnh nền kinh tế số phát triển mạnh mẽ, cùng với sự bùng nổ của thương mại điện tử, việc quản lý tồn kho ngày càng trở thành bài toán nan giải. Vậy đâu là lời giải?"* → *"Tồn kho lệch giữa kho tổng và cửa hàng là lý do phổ biến nhất khiến đơn online bị huỷ sau khi khách đã thanh toán."*
**Không flag:** bối cảnh thật sự cần để hiểu bài, và câu mở nêu bối cảnh **cụ thể** có mốc thời gian, số liệu hoặc sự kiện xác định. *"Sau đợt siết tín dụng bất động sản tháng 4/2022"* là bối cảnh; *"Trong bối cảnh nền kinh tế nhiều biến động"* là sáo ngữ. Giáo trình và bài giảng có câu dẫn dắt là chức năng sư phạm hợp lệ.

### B4. Kết bài lạc quan sáo rỗng

**Dấu hiệu:** *hứa hẹn sẽ, tin rằng trong thời gian tới, mở ra tương lai tươi sáng, hướng tới một tương lai bền vững, tiếp tục gặt hái nhiều thành công, sẽ còn tiến xa hơn nữa, cùng chung tay, chắc chắn sẽ mang lại, là bước đi đúng đắn, xứng đáng để bạn trải nghiệm, còn chần chừ gì nữa, Tóm lại, Tựu trung lại, Hy vọng bài viết hữu ích*.
**Vì sao:** model đóng bài bằng một câu chúc tụng vì nó học rằng văn bản cần có kết. Câu đó không kiểm chứng được, không ai chịu trách nhiệm, và thường mâu thuẫn với phần thân bài vốn đang nêu vấn đề.
**Sửa:** **cắt cả đoạn, kết thúc ở dữ kiện cụ thể cuối cùng.** Nếu bản gốc có nêu kế hoạch thật thì dùng cái đó: *"Với những nỗ lực không ngừng, tin rằng doanh nghiệp sẽ tiếp tục gặt hái thành công."* → *"Kế hoạch năm sau là mở thêm 12 cửa hàng, nhưng ban điều hành chưa chốt nguồn vốn."* Không có kế hoạch thật trong bản gốc thì chỉ cắt, không sáng tác.
**Không flag:** câu kết nêu kế hoạch cụ thể có mốc, số, hoặc người chịu trách nhiệm. Thư chúc mừng, diễn văn khai mạc, thông điệp đầu năm, ở đó lời chúc là chức năng chính. Luận văn và báo cáo có mục kết luận theo quy ước.

### B5. Song hành phủ định "không chỉ... mà còn"

**Dấu hiệu:** *không chỉ... mà còn, không những... mà còn, vừa... lại vừa, chẳng những... mà, không đơn thuần là... mà là, Đây không chỉ là..., đây là, hơn cả một..., tưởng chừng... nhưng*. Một lần trong bài dài là bình thường; từ hai lần trở lên, hoặc xuất hiện ở câu mở đoạn, là tell.
**Vì sao:** ánh xạ một-một của *not only... but also* và *it's not just X, it's Y*. Cấu trúc này nâng một mệnh đề tầm thường thành tuyên bố nghe có sức nặng mà không thêm thông tin.
**Sửa:** *"Hệ thống POS mới không chỉ giúp thu ngân nhanh hơn mà còn nâng cao trải nghiệm khách hàng."* → *"Hệ thống POS mới rút thời gian thanh toán từ 90 giây xuống 40 giây, nên hàng đợi giờ cao điểm ngắn hẳn."*
**Không flag:** hai vế thật sự khác loại và vế sau mang thông tin mới. *"Nghị định này không chỉ áp dụng cho doanh nghiệp trong nước mà còn cho chi nhánh nước ngoài"*, hai phạm vi pháp lý khác nhau, giữ nguyên.

### B6. Nghi vấn tu từ mở đoạn kiểu SEO

**Dấu hiệu:** *X là gì? Cùng tìm hiểu ngay!, Vậy đâu là lời giải?, Bạn đã bao giờ tự hỏi...?, Tại sao lại như vậy?, Câu trả lời nằm ở..., Đọc tiếp để biết, Bài viết dưới đây sẽ giúp bạn*.
**Vì sao:** khuôn bài SEO tiếng Việt mà model đã học thuộc: đặt câu hỏi, hứa trả lời, rồi mới trả lời. Tell rõ nhất là câu hỏi được đặt ra chỉ để chính người viết trả lời ngay câu sau.
**Sửa:** *"Vậy tồn kho an toàn là gì? Hãy cùng khám phá trong bài viết dưới đây nhé!"* → *"Tồn kho an toàn là lượng hàng giữ lại để không bị đứt hàng khi nhà cung cấp giao trễ."*
**Không flag:** câu hỏi thật, tức là người viết để nó treo hoặc trả lời bằng một câu bất ngờ. FAQ, ở đó cấu trúc hỏi đáp là thể loại.

### B7. Tụng ca địa phương và doanh nghiệp

**Dấu hiệu:** *mảnh đất và con người, thiên nhiên ưu đãi, được mệnh danh là, viên ngọc quý, nàng thơ, thiên đường, mang đậm bản sắc, đậm đà bản sắc dân tộc, nét đẹp truyền thống ngàn đời, người dân hiền hoà mến khách, non nước hữu tình, sơn thuỷ hữu tình, điểm đến không thể bỏ lỡ, khởi sắc, thay da đổi thịt, vươn mình mạnh mẽ*.
**Vì sao:** cụm loại này gắn được vào bất kỳ tỉnh nào, bất kỳ doanh nghiệp nào mà không sai, nên nó không nói gì. Dấu hiệu nặng: một đoạn có ba cụm trở lên và không có một danh từ riêng cụ thể nào ngoài tên địa danh.
**Sửa:** thay bằng chi tiết quan sát được trong bản gốc. *"Được mệnh danh là viên ngọc quý của miền Trung, nơi đây sở hữu vẻ đẹp non nước hữu tình."* → *"Bãi biển dài 3 km, phía bắc có ghềnh đá nên sóng lặng hơn."* Không có chi tiết trong bản gốc thì cắt.
**Không flag:** đang trích văn bản quảng bá chính thức, hoặc đang phân tích chính lối viết đó. *thay da đổi thịt*, *khởi sắc* khi có số liệu chứng minh ngay sau đó.

### B8. Danh xưng phóng đại

**Dấu hiệu:** *hàng đầu Việt Nam, top đầu, số 1 thị trường, uy tín nhất, tiên phong trong lĩnh vực, đơn vị dẫn đầu, chất lượng vượt trội, giải pháp toàn diện, giải pháp đột phá, đáp ứng mọi nhu cầu, cam kết mang đến trải nghiệm tốt nhất, đội ngũ giàu kinh nghiệm, quy trình chuyên nghiệp, giá cả cạnh tranh*.
**Vì sao:** toàn bộ nhóm này là tuyên bố không kiểm chứng được và không có nguồn.
**Sửa:** thay bằng một con số hoặc một khách hàng cụ thể **có trong bản gốc**. Không có thì cắt.
**Không flag:** tuyên bố kèm dẫn chứng hoặc xếp hạng từ bên thứ ba được nêu tên. Trích slogan chính thức trong bài phân tích về slogan đó.

### B9. Hán-Việt hoá tên gọi đời thường

**Dấu hiệu:** chọn từ Hán-Việt trang trọng ở chỗ thuần Việt tự nhiên hơn: *phương tiện di chuyển* thay *xe*, *thực phẩm* thay *đồ ăn*, *trang phục* thay *quần áo*, *nơi cư trú* thay *chỗ ở*, *thân nhân* thay *người nhà*, *sở hữu* thay *có*, *tiến hành* thay *làm*.
**Vì sao:** model chọn từ trang trọng nhất trong nhóm nghĩa tương đương vì nó có xác suất cao trong corpus hành chính và báo chí. Trong văn có giọng thì lựa chọn đó nghe như người ngoài đang đọc báo cáo.
**Sửa:** tra `references/han-viet-thuan-viet.md`. **Đọc cột thứ ba trước khi thay**, nó nêu điều kiện phải giữ nguyên Hán-Việt. Cấm dùng bảng đó như find-and-replace.
**Không flag:** năm phép thử trong file tham chiếu, chỉ cần một phép cho kết quả "giữ" là dừng. Đặc biệt: người viết lớn tuổi hoặc xuất thân khu vực nhà nước và học thuật dùng mật độ Hán-Việt cao **và nhất quán**: đó là giọng người, không phải tell. Mục tiêu là chỉnh tỷ lệ cho khớp thể loại, không phải loại bỏ Hán-Việt.

### B10. Thành ngữ dùng lệch và mật độ thành ngữ bất thường

**Dấu hiệu:** thành ngữ, tục ngữ, điển cố rải dày để tỏ ra có vốn văn hoá, nhưng dùng lệch nghĩa hoặc lệch ngữ cảnh. Hoặc mật độ cao bất thường trong một đoạn ngắn.
**Vì sao:** model rải thành ngữ vì corpus tiếng Việt gắn chúng với văn viết "hay". Người viết thật dùng thành ngữ thưa và đúng chỗ.
**Sửa:** cắt bớt, giữ lại cái nào dùng đúng nghĩa và hợp ngữ cảnh nhất.
**Không flag:** **khi nghi một thành ngữ bị dùng sai mà không chắc, hãy nêu nghi vấn cho người dùng thay vì tự sửa.** Nghĩa thành ngữ có biến thể vùng miền, và người kiểm tra cũng có thể sai. Không bao giờ tự sửa xuất xứ hay điển tích khi không chắc.

## Nhịp và cấu trúc

### B11. Nhịp ba cân âm tiết và biền ngẫu giả

**Dấu hiệu:** liệt kê ba thành phần *A, B và C* trong đó cả ba **cùng số âm tiết** và cùng cấu trúc ngữ pháp: *"nhanh chóng, chính xác và hiệu quả"*, *"tối ưu chi phí, nâng cao chất lượng và mở rộng thị trường"*. Biền ngẫu giả là dạng nặng hơn: từ ba cặp vế song song đều tăm tắp trở lên.
**Vì sao:** tiếng Việt đơn lập nên số âm tiết là biến hiển thị rõ. Khi ba thành phần đều cân âm tiết, đoạn văn có nhịp khẩu hiệu. Model rơi vào nhịp đều vì các cụm hai âm tiết Hán-Việt có xác suất cao nhất.
**Sửa:** phá nhịp bằng cách bỏ một thành phần hoặc thay bằng dữ kiện. *"Giải pháp giúp tối ưu chi phí, nâng cao chất lượng và mở rộng thị trường."* → *"Giải pháp cắt được khoảng 8% chi phí vận hành. Nó không giúp gì cho chất lượng sản phẩm."*
**Không flag:** ba thành phần là danh sách dữ kiện thật (ba chi nhánh, ba giai đoạn, ba điều khoản). Ranh giới: nhịp ba mang **thông tin** thì giữ, nhịp ba mang **nhạc điệu** thì cắt.

### B12. Cụm bốn âm tiết Hán-Việt tự chế

**Dấu hiệu:** cụm bốn âm tiết nghe như thành ngữ nhưng không tồn tại trong kho thành ngữ tiếng Việt: *kiến tạo giá trị, vươn tầm quốc tế, khơi nguồn cảm hứng, đồng hành phát triển, nâng tầm trải nghiệm*.
**Vì sao:** model tạo ra chúng bằng cách ghép hai cụm hai âm tiết Hán-Việt có xác suất cao. Chúng nghe trang trọng nhưng không có nội hàm.
**Sửa:** thay bằng câu nói thẳng việc gì xảy ra.
**Không flag:** **đây là false positive nguy hiểm nhất trong nhóm.** Rất nhiều cụm bốn âm tiết Hán-Việt là thuật ngữ chính sách có định nghĩa chính thức: *phát triển bền vững, an sinh xã hội, chuyển đổi số, cải cách hành chính, tăng trưởng xanh*. Không đụng vào chúng.

### B13. Nhịp câu đều đặn bất thường

**Dấu hiệu:** đo theo **âm tiết**, không theo từ. Chỉ áp dụng khi đoạn có từ 6 câu trở lên. Nghi ngờ khi độ dài câu gần như không dao động và không có câu nào dưới 8 âm tiết.
**Vì sao:** người Việt viết tự nhiên hay chêm câu cụt 3–6 âm tiết (*"Không đơn giản vậy."*, *"Thế thôi."*) giữa các câu dài. Model tối ưu theo xác suất trung bình nên hội tụ về độ dài trung vị và gần như không sinh câu cụt.
**Sửa:** gộp hai câu ngắn thành một câu dài, tách một ý ra thành câu cụt. Sửa V12 và V13 thường tự phá nhịp đều, nên **làm cấu trúc trước, chỉnh nhịp sau**.
**Không flag:** đoạn dưới 6 câu: mẫu quá nhỏ. Tác giả có phong cách câu đều đã xác nhận qua mẫu văn. **Chỉ số này một mình là bằng chứng yếu, chỉ dùng để cộng dồn.** Ngưỡng chưa hiệu chuẩn trên corpus tiếng Việt.

## Giọng và quan hệ

### B14. Rụng tiểu từ tình thái cuối câu

**Dấu hiệu:** đoạn hội thoại, email, tin nhắn, hướng dẫn nội bộ dài trên 5 câu mà **không có một tiểu từ nào** trong tập *nhé, nhỉ, thôi, đấy, cơ, mà, chứ, ạ, à, vậy, đi, với, rồi, nào*. Câu khuyên, nhờ, rủ, trấn an nhưng kết thúc bằng dấu chấm trơ.
**Vì sao:** tiếng Anh mã hoá thái độ bằng ngữ điệu và trợ động từ tình thái; tiếng Việt bằng tiểu từ bám cuối câu. Khi dịch, trợ động từ đã hoá thành *nên / có thể / sẽ* ở giữa câu, cuối câu không còn gì để đặt vào, lớp thái độ biến mất hoàn toàn.
**Sửa:** *"Bạn nên kiểm tra lại cấu hình trước khi triển khai. Nếu vẫn còn lỗi, hãy liên hệ đội hạ tầng."* → *"Bạn kiểm tra lại cấu hình trước khi triển khai nhé. Vẫn lỗi thì cứ liên hệ đội hạ tầng."* Chọn tiểu từ theo hành động lời nói: khuyên hoặc nhờ nhẹ dùng *nhé*; khẳng định có sức thuyết phục dùng *đấy* hoặc *chứ*; rủ cùng làm dùng *thôi* hoặc *nào*; hỏi tìm đồng tình dùng *nhỉ*; kính trọng dùng *ạ*. Khi gắn tiểu từ, thường phải bỏ bớt trợ động từ nặng ở giữa câu (*nên, hãy, sẽ*) vì tiểu từ đã gánh chức năng đó.
**Không flag:** chỉ thêm tiểu từ ở câu mang **hành động lời nói** rõ rệt, không phải mọi câu. Mật độ 1 trên 3–5 câu; dày hơn là nhại giọng.

### B15. Xưng hô lơ lửng và phẳng

**Dấu hiệu:** ba đại từ *chúng ta*, *bạn*, *chúng tôi* xuất hiện trong cùng một đoạn ngắn mà không có quan hệ xã hội nào giải thích được. *Bạn* dùng ở chỗ tiếng Việt thật sẽ dùng anh / chị / em / quý khách. *Chúng ta* theo nghĩa "người ta nói chung", không thực sự bao gồm người đọc. Hoặc toàn văn bản không có đại từ nào trong khi nội dung rõ ràng là một người nói với một người.
**Vì sao:** tiếng Anh có *I / you* trung tính, không mã hoá quan hệ. Tiếng Việt buộc chọn cặp phản ánh tuổi, vai vế, mức thân sơ. Model không có thông tin đó nên né bằng cặp trung tính giả, hoặc bỏ hẳn, hoặc đổi qua đổi lại.
**Sửa:** **chọn cặp xưng hô trước khi sửa câu nào cả**, rồi giữ nhất quán tuyệt đối. Đổi cặp giữa chừng là tell mạnh hơn cả chọn sai cặp. *Chúng ta* chỉ giữ khi thật sự bao gồm người đọc vào cùng hành động; nếu chỉ là *we* khái quát thì bỏ hẳn và viết vô nhân xưng.
**Không flag** (đây là chỗ rủi ro cao nhất của cả skill): **không được suy đoán tuổi tác hay vai vế để áp xưng hô.** Ngữ cảnh không cho biết quan hệ thì giữ nguyên và ghi chú cho người dùng tự chọn. Đổi *bạn* thành *em* khi không biết vai vế có thể xúc phạm người nhận. Tài liệu hướng dẫn, UX copy, giáo trình, quảng cáo đại chúng dùng *bạn* là quy ước hợp lệ. Bài học thuật dùng *chúng tôi* cho nhóm tác giả là đúng chuẩn.

### B16. Giả thân mật

**Dấu hiệu:** *nhà mình, bên mình, shop mình, các bạn ơi, mọi người ơi, mình xin phép chia sẻ, mình để ý thấy rằng, thú thật là, không biết mọi người thế nào chứ mình*. Tell là: **xưng hô gần gũi nhưng nội dung hoàn toàn chung chung**, không một chi tiết cá nhân nào đi kèm.
**Vì sao:** cách xưng hô này chỉ tự nhiên khi có quan hệ thật. Model dùng nó như lớp sơn thân thiện phủ lên nội dung vô danh.
**Sửa:** *"Các bạn ơi, thú thật là mình đã tìm hiểu rất nhiều và mình để ý thấy rằng việc chọn đúng sản phẩm thực sự rất quan trọng."* → *"Mình dùng loại này bốn tháng, giặt máy khoảng hai mươi lần. Cổ áo bắt đầu giãn, nhưng màu thì chưa bạc."* Chỉ viết được bản sửa như vậy khi bản gốc có chi tiết đó; không có thì cắt phần sáo rỗng, giữ lại phần thật.
**Không flag:** chủ shop nhỏ hoặc người sáng tạo nội dung cá nhân dùng cách xưng hô đó như giọng thật, **có kèm chi tiết cụ thể chứng minh trải nghiệm**. Xoá *nhà mình* khỏi bài của một chủ shop là xoá luôn danh tính người viết.

### B17. Trộn register không chủ đích

**Dấu hiệu:** văn nói lẫn vào văn trang trọng (*cực kỳ, siêu, cứ thế mà, nói chung là, xịn, ngon lành, luôn* cuối câu) hoặc văn hành chính lẫn vào blog cá nhân (*nhằm mục đích, trên tinh thần, theo đó, nêu trên, công tác, tiến hành thực hiện*). Nặng nhất là trộn trong cùng một câu.
**Vì sao:** model chọn register theo từng câu chứ không theo cả văn bản, nên độ trang trọng dao động trong cùng một đoạn. Người viết thật cũng trộn register, nhưng trộn **có chủ đích** và thường ở chỗ chuyển giọng rõ ràng, không rải đều.
**Sửa:** chọn một mức trang trọng cho cả văn bản dựa trên người đọc, rồi kéo các câu lệch về mức đó.
**Không flag** (đây là rủi ro over-edit nghiêm trọng): áp pattern này máy móc sẽ biến giọng Nam Bộ hoặc giọng Trung thành giọng Bắc chuẩn tin tức. Đó là thiệt hại không phục hồi được. Cũng không flag khi người viết cố tình phá giọng để tạo hiệu ứng và chỗ phá giọng nằm gọn trong một câu. Văn bản nội bộ của đội ngũ trẻ suồng sã **nhất quán** từ đầu đến cuối là đúng chuẩn của họ.

---

## Giọng và cá tính

Tránh được dấu vết dịch mới là một nửa việc. Văn vô hồn, trung tính đều tăm tắp cũng lộ liễu không kém.

Khi văn bản là blog, tuỳ bút, quan điểm cá nhân, hoặc bài viết personal brand, hãy để người viết có: ý kiến rõ ràng, chỗ chưa chắc chắn, cảm xúc lẫn lộn chưa gỡ, chỗ nói đùa, câu chen ngang, và nhịp không đều. Câu dài cạnh câu hai chữ. Một đoạn mười dòng rồi một đoạn một dòng.

Ba ràng buộc:

1. **Thêm được thái độ, không thêm dữ kiện.** Ý kiến và phản ứng là giọng, không phải sự thật. Bạn được phép để người viết tỏ thái độ về những gì bản gốc đã nêu. Bạn không được thêm bất kỳ dữ kiện, tên, số, ngày tháng nào mới.
2. **Không nhại.** Rắc *thì, mà, nhé, đấy* vào mọi câu cho ra văn giả dân dã, cũng máy móc y hệt, chỉ đổi chiều. Xem phần mật độ trong `SKILL.md`.
3. **Không áp mục này lên văn trung tính.** Với báo cáo, tài liệu tham chiếu, nội dung học thuật thì trung tính và phẳng **chính là** giọng người đúng. Ở đó dùng `profiles/ky-thuat-doanh-nghiep.md`.
