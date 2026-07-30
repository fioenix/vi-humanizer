# AGENTS.md

Hướng dẫn cho AI coding agent làm việc trong repo này.

## Repo này là gì

Một agent skill viết hoàn toàn bằng Markdown, không có bước build. Runtime artifact là `SKILL.md` cùng ba thư mục nó trỏ tới: `profiles/`, `references/` và `calibration/`.

Đây **không** phải bản dịch của skill humanizer tiếng Anh. Phần lớn pattern ở đây bắt lỗi dịch **từ** tiếng Anh sang tiếng Việt, thứ mà một skill viết bằng tiếng Anh về nguyên tắc không phát hiện được. Ba pattern đi ngược hẳn bản gốc (quy tắc lặp từ, en dash, ngoặc kép), đọc phần "Ba chỗ skill này đi ngược bản tiếng Anh" trong README trước khi sửa chúng.

## Các file

| File | Vai trò |
|---|---|
| `SKILL.md` | Cổng thể loại, quy trình, lõi V1–V19, typography T1–T6, phần nhận diện. **Nguồn sự thật.** |
| `profiles/blog-ca-nhan.md` | B1–B17, lỗi giọng cho văn có giọng |
| `profiles/ky-thuat-doanh-nghiep.md` | K1–K5, chủ yếu là lệnh cấm và điều chỉnh ngưỡng |
| `references/han-viet-thuan-viet.md` | Bảng tra Hán-Việt ↔ thuần Việt |
| `references/bang-tra-cuu.md` | Bổ ngữ kết quả, cặp hô ứng, loại từ, tiểu từ, checklist |
| `calibration/LOG.md` | Bộ nhớ bằng chứng cho vòng tự hiệu chuẩn. Ghi trước, sửa skill sau |
| `README.md` | Cho người đọc: cài đặt, bảng pattern, nguồn tham khảo, lịch sử phiên bản |
| `.claude-plugin/plugin.json` | Manifest plugin Claude Code |
| `.claude-plugin/marketplace.json` | Marketplace một repo |
| `scripts/validate-package.py` | Kiểm tra đồng bộ, chạy trong CI |
| `scripts/package-skill.sh` | Đóng gói `dist/vi-humanizer.skill` cho Claude Desktop và claude.ai |
| `scripts/scan-tells.sh` | Quét các pattern regex được trên chính văn bản của repo |

## Trục phân chia

Đây là quyết định kiến trúc quan trọng nhất của repo. Đừng phá nó khi thêm pattern.

- **Lỗi ngôn ngữ** sai ở cấp hư từ và cấu trúc câu, là lỗi bất kể văn bản thuộc thể loại nào. Sửa chúng không đụng tới giọng người viết. → `SKILL.md`
- **Lỗi giọng** phụ thuộc hoàn toàn vào register. → `profiles/`

Nếu một pattern mới có thể là lỗi ở blog nhưng là chuẩn ở công văn, nó thuộc profile, không thuộc lõi.

## Hợp đồng bảo trì

- **Đánh số pattern.** Bốn tiền tố, mỗi tiền tố đánh số liên tục từ 1 và do đúng một file sở hữu: `V` và `T` trong `SKILL.md`, `B` trong profile blog, `K` trong profile kỹ thuật. Thêm, bớt hay đánh số lại thì phải cập nhật bảng pattern trong README trong cùng một thay đổi. Giữ số hiệu ổn định trừ khi cố ý đánh số lại.
- **Version.** Ba nơi phải khớp: `metadata.version` trong `SKILL.md`, mục đầu tiên của Lịch sử phiên bản trong `README.md` và `version` trong `plugin.json`. Giữ version dưới `metadata`; khoá `version` ở cấp cao nhất của frontmatter không portable giữa các harness. `marketplace.json` cố ý không có version để `plugin.json` là nguồn duy nhất.
- **Ngân sách dòng.** `SKILL.md` tối đa 550 dòng, profile blog 320, profile kỹ thuật 220. Ngân sách buộc pattern phải cô đặc. `references/` không giới hạn vì là bảng tra.
- **Nguồn.** Mọi pattern mới có nguồn thì thêm nguồn vào README kèm phân hạng. Không có nguồn thì nói rõ là suy luận. **Không bịa nguồn, không bịa số liệu tần suất.**
- **Kiểm tra trước khi publish:** `python3 scripts/validate-package.py`, `npx skills add . --list`, `claude plugin validate .`

## Khi sửa nội dung skill

- Giữ YAML frontmatter hợp lệ, đúng thụt lề.
- Phần dưới frontmatter là sản phẩm. Sửa nó như sửa một tài liệu hướng dẫn cẩn thận, không phải như sửa code.
- Mỗi pattern giữ đủ bốn phần: **Dấu hiệu**, **Vì sao**, **Sửa**, **Không flag**. Phần "Không flag" quan trọng ngang phần phát hiện: nó chặn skill phá văn bản người thật viết.
- Văn trong skill phải qua được chính skill này. Không em dash, không "một cách + tính từ" thừa, không hạ giọng quá tay. Trước khi commit, tự soi lại phần văn mình vừa viết bằng đúng bộ pattern trong đó.
- Ví dụ Before/After phải là tiếng Việt tự nhiên. Không dịch ví dụ từ skill tiếng Anh.
- Ví dụ minh hoạ tránh dùng tên đơn vị hành chính đã sáp nhập theo NQ 202/2025/QH15 (hiệu lực 01/07/2025).

## Nâng cấp từ sử dụng thật (giao thức cho agent tự bảo trì)

Skill này được thiết kế để một agent chạy lâu dài (ví dụ Hermes) tự nâng cấp nó dựa trên cách người thật viết và sửa. Giao thức:

**Nguồn bằng chứng, xếp theo độ mạnh:**
1. **Bản vàng**: người dùng sửa lại output của skill. Đây là bằng chứng mạnh nhất.
2. Văn bản người bản ngữ tự viết trong công việc, thu được khi skill được gọi.
3. Nhận xét trực tiếp của người dùng về một pattern.

**Phân loại trước khi đụng vào skill.** Mỗi khác biệt giữa output và bản vàng rơi vào đúng một trong ba loại:

| Loại | Nhận biết | Hành động | Ngưỡng |
|---|---|---|---|
| Sở thích cá nhân | Cả hai bản đều là tiếng Việt tự nhiên, khác biệt là lựa chọn phong cách | Ghi vào voice memory của agent. **Không sửa skill** | Không bao giờ vào skill |
| Lỗi guard | Skill sửa sai chỗ người thật viết đúng, hoặc bỏ sót chỗ lộ rõ | Nới hoặc siết guard của pattern có sẵn | n=1 đủ, nếu người sửa là người bản ngữ và lỗi gọi tên được |
| Pattern mới | Một tell lặp lại mà chưa pattern nào bắt | Thêm pattern, đúng khung bốn phần | n≥3 mẫu độc lập, khác văn bản, khác ngày |

**Ghi log trước, sửa sau.** Mỗi quan sát ghi một entry vào `calibration/LOG.md`: ngày, register, đoạn trước, bản vàng, khác biệt gọi tên được, pattern liên quan, phân loại, quyết định. Log là bộ nhớ bằng chứng của skill; sửa skill mà không có entry tương ứng là bịa.

**Nhãn độ tin cậy mới.** Pattern hoặc guard sinh ra từ giao thức này gắn nhãn "Quan sát từ sử dụng (n=…)" thay vì "Suy luận từ cơ chế LLM". Đây là nhãn mạnh hơn suy luận nhưng yếu hơn corpus. Còn n thì phải là số đếm được trong log.

**Kỷ luật đóng gói giữ nguyên.** Mỗi lần sửa: chạy validator, bump version ba nơi, thêm dòng changelog nói rõ sửa gì và từ bằng chứng nào. Không gộp nhiều thay đổi không liên quan vào một version.

**Cảnh báo bias.** Học từ một nhóm người dùng làm skill lệch về register của nhóm đó. Với fork nội bộ thì đó là tính năng, không phải lỗi, nhưng phải ghi nhận trong changelog để người cài từ ngoài biết skill đã được tune cho tổ chức nào.

**Phần agent phải tự lo, skill không làm được:** skill chỉ thấy các lượt nó được gọi. Muốn học từ chat thường ngày, agent cần một chỉ dẫn ở tầng memory/system prompt của chính nó, đại ý: "Khi thấy người dùng viết hoặc sửa văn bản tiếng Việt theo cách mâu thuẫn với vi-humanizer, ghi một entry vào calibration/LOG.md của repo skill."

## Việc còn tồn

- Ngưỡng số trong skill chưa hiệu chuẩn trên corpus văn bản AI tiếng Việt thật. Đây là việc lớn nhất còn nợ.
- Hai nguồn hạng C đang gánh nội dung hạng A, xem mục "Nguồn còn thiếu" trong README.
- Skill không đối chiếu được phát biểu về cấu trúc repo với cây thư mục thật, nên phần mô tả kiến trúc trong README và AGENTS.md phải soát tay mỗi khi thêm file.
