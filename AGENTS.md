# AGENTS.md

Hướng dẫn cho AI coding agent làm việc trong repo này.

## Repo này là gì

Một agent skill viết hoàn toàn bằng Markdown, không có bước build. Runtime artifact là `SKILL.md` cùng hai thư mục `profiles/` và `references/` mà nó trỏ tới.

Đây **không** phải bản dịch của skill humanizer tiếng Anh. Phần lớn pattern ở đây bắt lỗi dịch **từ** tiếng Anh sang tiếng Việt, thứ mà một skill viết bằng tiếng Anh về nguyên tắc không phát hiện được. Ba pattern đi ngược hẳn bản gốc (quy tắc lặp từ, en dash, ngoặc kép) — đọc phần "Ba chỗ skill này đi ngược bản tiếng Anh" trong README trước khi sửa chúng.

## Các file

| File | Vai trò |
|---|---|
| `SKILL.md` | Cổng thể loại, quy trình, lõi V1–V19, typography T1–T6, phần nhận diện. **Nguồn sự thật.** |
| `profiles/blog-ca-nhan.md` | B1–B17, lỗi giọng cho văn có giọng |
| `profiles/ky-thuat-doanh-nghiep.md` | K1–K4, chủ yếu là lệnh cấm và điều chỉnh ngưỡng |
| `references/han-viet-thuan-viet.md` | Bảng tra Hán-Việt ↔ thuần Việt |
| `references/bang-tra-cuu.md` | Bổ ngữ kết quả, cặp hô ứng, loại từ, tiểu từ, checklist |
| `README.md` | Cho người đọc: cài đặt, bảng pattern, nguồn tham khảo, lịch sử phiên bản |
| `.claude-plugin/plugin.json` | Manifest plugin Claude Code |
| `.claude-plugin/marketplace.json` | Marketplace một repo |
| `scripts/validate-package.py` | Kiểm tra đồng bộ, chạy trong CI |

## Trục phân chia

Đây là quyết định kiến trúc quan trọng nhất của repo. Đừng phá nó khi thêm pattern.

- **Lỗi ngôn ngữ** sai ở cấp hư từ và cấu trúc câu, là lỗi bất kể văn bản thuộc thể loại nào. Sửa chúng không đụng tới giọng người viết. → `SKILL.md`
- **Lỗi giọng** phụ thuộc hoàn toàn vào register. → `profiles/`

Nếu một pattern mới có thể là lỗi ở blog nhưng là chuẩn ở công văn, nó thuộc profile, không thuộc lõi.

## Hợp đồng bảo trì

- **Đánh số pattern.** Bốn tiền tố, mỗi tiền tố đánh số liên tục từ 1 và do đúng một file sở hữu: `V` và `T` trong `SKILL.md`, `B` trong profile blog, `K` trong profile kỹ thuật. Thêm, bớt hay đánh số lại thì phải cập nhật bảng pattern trong README trong cùng một thay đổi. Giữ số hiệu ổn định trừ khi cố ý đánh số lại.
- **Version.** Ba nơi phải khớp: `metadata.version` trong `SKILL.md`, mục đầu tiên của Lịch sử phiên bản trong `README.md`, và `version` trong `plugin.json`. Giữ version dưới `metadata`; khoá `version` ở cấp cao nhất của frontmatter không portable giữa các harness. `marketplace.json` cố ý không có version để `plugin.json` là nguồn duy nhất.
- **Ngân sách dòng.** `SKILL.md` tối đa 550 dòng, profile blog 320, profile kỹ thuật 220. Ngân sách buộc pattern phải cô đặc. `references/` không giới hạn vì là bảng tra.
- **Nguồn.** Mọi pattern mới có nguồn thì thêm nguồn vào README kèm phân hạng. Không có nguồn thì nói rõ là suy luận. **Không bịa nguồn, không bịa số liệu tần suất.**
- **Kiểm tra trước khi publish:** `python3 scripts/validate-package.py`, `npx skills add . --list`, `claude plugin validate .`

## Khi sửa nội dung skill

- Giữ YAML frontmatter hợp lệ, đúng thụt lề.
- Phần dưới frontmatter là sản phẩm. Sửa nó như sửa một tài liệu hướng dẫn cẩn thận, không phải như sửa code.
- Mỗi pattern giữ đủ bốn phần: **Dấu hiệu**, **Vì sao**, **Sửa**, **Không flag**. Phần "Không flag" quan trọng ngang phần phát hiện — đây là thứ chặn skill phá văn bản người thật viết.
- Ví dụ Before/After phải là tiếng Việt tự nhiên. Không dịch ví dụ từ skill tiếng Anh.
- Ví dụ minh hoạ tránh dùng tên đơn vị hành chính đã sáp nhập theo NQ 202/2025/QH15 (hiệu lực 01/07/2025).

## Việc còn tồn

- Ngưỡng số trong skill chưa hiệu chuẩn trên corpus văn bản AI tiếng Việt thật. Đây là việc chính của v0.2.
- Hai nguồn hạng C đang gánh nội dung hạng A, xem mục "Nguồn còn thiếu" trong README.
- Chưa kiểm chứng thực nghiệm việc các harness có nạp đủ `profiles/` và `references/` hay không.
