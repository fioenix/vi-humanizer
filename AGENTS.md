# AGENTS.md

Hướng dẫn dành cho agent làm việc trong repo này.

## Repo này chứa gì

Đây là một agent skill viết bằng Markdown, không có bước build. `SKILL.md` là tài liệu điều khiển chính; các profile và bảng tra bổ sung quy tắc theo thể loại hoặc cung cấp ví dụ chi tiết.

Skill được viết riêng cho tiếng Việt, không phải bản dịch của một skill tiếng Anh. Nhiều lỗi trong repo xuất hiện khi cấu trúc tiếng Anh được giữ nguyên rồi thay bằng từ tiếng Việt. Vì vậy, đừng nhập một quy tắc từ skill tiếng Anh vào đây nếu chưa kiểm tra xem nó có đúng với tiếng Việt hay không.

## Vai trò của từng file

| File | Vai trò |
|---|---|
| `SKILL.md` | Kiểm tra thể loại, quy trình, V1–V25, T1–T6 và cách trả kết quả. **Đây là nguồn chuẩn.** |
| `profiles/blog-ca-nhan.md` | B1–B17 cho blog, bài cá nhân, nội dung công việc và marketing |
| `profiles/ky-thuat-doanh-nghiep.md` | K1–K7 cùng các giới hạn riêng của tài liệu kỹ thuật, doanh nghiệp và học thuật |
| `references/han-viet-thuan-viet.md` | Bảng tra Hán-Việt và thuần Việt, kèm điều kiện phải giữ nguyên thuật ngữ |
| `references/bang-tra-cuu.md` | Bảng tra hư từ, loại từ, tiểu từ và câu hỏi chẩn đoán |
| `references/bo-giai-phong-cach.md` | Năm chiều ngữ cảnh, thứ tự ưu tiên và bảy style card; không sở hữu pattern |
| `calibration/LOG.md` | Nhật ký bằng chứng dùng để sửa quy tắc chung; không lưu hồ sơ văn phong cá nhân |
| `calibration/ca-kiem-thu.md` | Ca kiểm thử chạy tay cho từng pattern, gồm cả ca chống sửa quá tay |
| `README.md` | Hướng dẫn cài đặt, mô tả kiến trúc, danh mục pattern, nguồn và lịch sử phiên bản |
| `agents/openai.yaml` | Tên hiển thị và lời gọi mặc định trên các nền tảng tương thích |
| `.claude-plugin/plugin.json` | Manifest của plugin Claude Code |
| `.claude-plugin/marketplace.json` | Manifest marketplace của repo |
| `scripts/validate-package.py` | Kiểm tra version, số hiệu pattern, bảng README và giới hạn dòng |
| `scripts/package-skill.sh` | Đóng gói `dist/vi-humanizer.skill` |
| `scripts/scan-tells.sh` | Tìm những dấu hiệu có thể quét bằng biểu thức chính quy để người biên tập xem lại |
| `.specify/` | Cấu hình, template và script của Spec Kit; constitution trong `.specify/memory/constitution.md` chi phối spec, plan và implementation |
| `specs/` | Đặc tả, checklist, plan và task của từng feature; Spec Kit là nguồn chuẩn cho các artifact này |
| `.agents/skills/` | Các skill Spec Kit do `specify init` tạo cho Codex; không được đóng gói vào `vi-humanizer.skill` |
| `guard_eval/` | Harness Python đánh giá need-to-edit, candidate preference và safety ở shadow mode |
| `eval/guard/` | Corpus đã gắn nhãn, manifest, evaluation config, pricing snapshot và policy đã duyệt |
| `tests/guard_eval/` | Test unit/contract/integration offline; CI không gọi TypeSafe |
| `artifacts/guard-eval/` | Raw run local bị gitignore; artifact không được chứa raw prose, secret hoặc raw exception |
| `guard_eval/v2/` | Lane v2 tách absolute judgment, deterministic policy và paired comparison khỏi v1 |
| `eval/guard/v2/` | Dev corpus v2, config/pricing, lock bytes v1 và registry holdout đã quan sát |
| `tests/guard_eval_v2/` | Test offline cho schema, policy, corpus governance, CLI và report v2 |
| `artifacts/guard-eval-v2/` | Raw judgment/recommendation run v2 local, bị gitignore |

## Evaluation harness

- Candidate phải được host LLM chạy vi-humanizer, baseline observation hoặc maintainer fixture tạo
  trước. Jev chỉ thẩm định; không prompt hoặc adapter nào được yêu cầu Jev sinh, nối hay sửa prose.
- `eval/guard/dev.jsonl` dùng để phát triển câu hỏi và fit threshold. `holdout.jsonl` chỉ được đọc
  sau khi policy đã khóa; không sửa corpus, questions hoặc threshold sau khi xem kết quả holdout.
- `evaluation-config.json` khóa model và question-set version. `pricing.json` chỉ phục vụ tính cost,
  không được tham gia route. `policy.json` chỉ được ghi sau live dev run và review của maintainer
  hoặc agent được owner ủy quyền rõ; artifact phải ghi đúng actor thật.
- `candidate_origin`, nhãn, baseline, provenance và split không được gửi cho TypeSafe. Generated
  run/report không được chứa raw prose, credential, request body hoặc raw exception.
- Thiếu key hoặc lỗi dịch vụ phải ra `unchecked`/exit 2. Không được đổi thành pass và không được
  làm hỏng workflow Markdown hay gói `vi-humanizer.skill`.
- V2 không dùng Choice để quyết định giữ bản gốc hoặc cứu candidate đã trượt cổng tuyệt đối. Choice
  chỉ xếp hạng shortlist có ít nhất hai candidate. Policy tất định chỉ tạo shadow recommendation;
  host Agent/LLM mới có quyền quyết định có biên tập prose hay không.
- Trước khi maintainer hoặc agent được owner ủy quyền rõ duyệt holdout riêng, manifest v2 phải giữ descriptor `pending`; `validate`
  được phép kiểm dev nhưng `holdout` và `compare` không được đọc file holdout hay dùng quota.

## Ranh giới giữa quy tắc chung và profile

Đây là quyết định kiến trúc quan trọng nhất của repo.

- V1–V25 trong `SKILL.md` kiểm tra cách dùng từ và cấu trúc câu. Chúng chỉ chạy trên các thể loại được phép biên tập, đồng thời phải tuân theo mục **Không flag** của từng pattern.
- B1–B17 và K1–K7 phụ thuộc vào thể loại, người đọc và giọng văn. Chúng nằm trong `profiles/`.

Nếu một cách viết tự nhiên trong công văn nhưng dễ thành sáo ngữ trong blog, hãy xử lý nó ở profile. Không đưa vào V1–V25 như một lỗi áp dụng cho mọi văn bản.

Style card không phải tầng pattern thứ năm. Nó chỉ giải các lựa chọn đều hợp lệ sau khi cổng thể loại
đã chọn đúng profile. `references/bo-giai-phong-cach.md` là nguồn chuẩn cho registry; `SKILL.md` sở
hữu thứ tự gọi resolver, còn README chỉ liệt kê inventory. Không sao chép toàn bộ card sang profile.

## Hợp đồng bảo trì

- **Số hiệu pattern:** bốn tiền tố `V`, `T`, `B`, `K` đều bắt đầu từ 1 và tăng liên tục. `V` và `T` thuộc `SKILL.md`; `B` thuộc profile blog; `K` thuộc profile kỹ thuật. Khi thêm, bỏ hoặc đổi số, phải cập nhật bảng pattern trong `README.md` cùng lúc.
- **Ngưỡng thêm pattern:** một dấu hiệu chỉ được thành pattern riêng khi không pattern nào hiện có ngụ ý nó. Còn lại thì mở rộng mục **Dấu hiệu** của pattern gần nhất. Khi hai pattern chạm nhau, pattern hẹp hơn phải có một câu phân vai trỏ sang pattern kia, như K6 trỏ sang V21 cho phần lời chào và lời mời làm tiếp.
- **Version:** `metadata.version` trong `SKILL.md`, mục mới nhất của phần Lịch sử phiên bản trong `README.md` và `version` trong `.claude-plugin/plugin.json` phải giống nhau. Giữ version bên trong `metadata`; không đặt khoá `version` ở cấp cao nhất của frontmatter vì một số nền tảng không nhận khoá này. `marketplace.json` không có version để tránh hai nguồn dữ liệu.
- **Giới hạn dòng:** `SKILL.md` tối đa 550 dòng, profile blog tối đa 320 dòng, profile kỹ thuật tối đa 220 dòng. Các file trong `references/` không bị giới hạn.
- **Nguồn:** khi thêm pattern dựa trên tài liệu bên ngoài, phải thêm nguồn vào `README.md` và ghi đúng mức độ tin cậy. Nếu chỉ là suy luận, phải nói rõ là suy luận. Không tự tạo nguồn hoặc số liệu tần suất.
- **Kiểm tra trước khi phát hành:** chạy `python3 scripts/validate-package.py`, `npx skills add . --list` và `claude plugin validate .`.

## Khi sửa nội dung

- Giữ YAML frontmatter hợp lệ và đúng thụt lề.
- Mỗi pattern phải có đủ bốn mục: **Dấu hiệu**, **Vì sao**, **Sửa**, **Không flag**. Mục cuối ngăn skill sửa nhầm văn bản vốn đã đúng nên quan trọng ngang phần phát hiện.
- Ví dụ trước và sau khi sửa phải là tiếng Việt tự nhiên. Không dịch nguyên ví dụ từ skill tiếng Anh.
- Không dùng ngưỡng số làm điều kiện kết luận nếu ngưỡng đó chưa được kiểm chứng trên một bộ ngữ liệu phù hợp.
- Không biến lựa chọn phong cách thành lỗi ngôn ngữ. Chỉ đưa một cách viết vào quy tắc chung khi có thể chỉ ra điều gì sai và xác định được trường hợp cần loại trừ.
- Tự rà lại phần vừa viết bằng chính `SKILL.md`. Chú ý câu thiếu từ, câu bị nén thành nhãn cấu hình, thuật ngữ tiếng Anh không cần thiết và cách diễn đạt hạ giọng quá mức.
- Ví dụ minh hoạ không dùng tên đơn vị hành chính đã sáp nhập theo Nghị quyết 202/2025/QH15, có hiệu lực từ ngày 01/07/2025.

## Học từ phản hồi thực tế

Phản hồi của người dùng có thể giúp sửa skill, nhưng không phải khác biệt nào cũng được đưa vào quy tắc chung.

**Nguồn bằng chứng, xếp từ mạnh đến yếu:**

1. Bản do người dùng viết lại từ kết quả của skill.
2. Văn bản do người bản ngữ tự viết trong một tình huống sử dụng thật.
3. Nhận xét trực tiếp của người dùng về một pattern.
4. Quy tắc tiếng Việt do người bản ngữ nêu ra, kèm ít nhất một ví dụ và có thể kiểm tra độc lập.

Trước khi sửa skill, phải xếp quan sát vào đúng nhóm:

| Nhóm | Cách nhận biết | Nơi xử lý |
|---|---|---|
| Sở thích cá nhân | Cả hai cách viết đều tự nhiên; khác nhau ở nhịp câu, xưng hô, mức trang trọng hoặc cách dùng từ | Memory hoặc knowledge base của agent, tách theo đúng người dùng |
| Pattern sửa nhầm hoặc bỏ sót | Quy tắc chung sửa một câu vốn đúng, hoặc bỏ qua một lỗi có thể gọi tên | `calibration/LOG.md`, rồi điều chỉnh **Không flag** hoặc phần phát hiện |
| Hiện tượng mới | Một lỗi chưa có pattern nào mô tả và xuất hiện trong nhiều mẫu độc lập | `calibration/LOG.md`, rồi cân nhắc thêm pattern |

### Hồ sơ văn phong cá nhân

Không ghi sở thích của một người vào `calibration/LOG.md`. Nếu nền tảng có memory hoặc knowledge base và chính sách lưu trữ cho phép, agent có thể lưu một hồ sơ ngắn cho đúng người dùng, gồm những đặc tính cần thiết để giữ giọng: cách xưng hô, nhịp câu, mức dùng từ Hán-Việt, cách chêm tiếng Anh, viết hoa và dấu câu.

Mỗi đặc tính cần có phạm vi áp dụng và một ví dụ ngắn. Không chép nguyên văn bản, không lưu dữ kiện cá nhân không liên quan, không dùng hồ sơ của người này cho người khác. Yêu cầu trong lượt hiện tại luôn được ưu tiên hơn memory cũ.

Trước khi dùng skill, agent nên nạp lại hồ sơ của đúng người dùng nếu xác định được danh tính. Không có hồ sơ hoặc không chắc người dùng là ai thì tiếp tục biên tập theo thể loại, không tự suy đoán.

### Nhật ký hiệu chuẩn dùng chung

`calibration/LOG.md` chỉ ghi bằng chứng có thể làm thay đổi quy tắc dùng chung. Mỗi mục cần có ngày, thể loại, đoạn trước khi sửa, bản đối chiếu, tên khác biệt, pattern liên quan, cách phân loại và quyết định.

Ghi bằng chứng trước khi sửa quy tắc. Một trường hợp sửa nhầm có thể đủ để bổ sung trường hợp loại trừ nếu lỗi được gọi tên rõ và có thể kiểm tra lại. Pattern mới cần nhiều mẫu độc lập, trừ khi người bản ngữ nêu một quy tắc ngôn ngữ có thể kiểm chứng ngay bằng nguồn đáng tin cậy.

Không dùng quan sát của một cá nhân để âm thầm điều chỉnh skill theo giọng của họ hoặc của tổ chức họ. Nếu một bản fork cố ý phục vụ riêng một tổ chức, phải nói rõ phạm vi đó trong changelog và không trình bày nó như quy tắc chung của tiếng Việt.

## Những việc còn thiếu

- Repo chưa có bộ ngữ liệu đủ để đặt ngưỡng tần suất cho các dấu hiệu. Số lần xuất hiện chỉ dùng để tìm chỗ cần đọc kỹ hơn.
- Một số nguồn trong README vẫn là nguồn trình bày lại. Xem mục “Nguồn còn thiếu” trước khi nâng mức độ tin cậy.
- Skill không tự kiểm tra được những phát biểu về cấu trúc repo. Mỗi khi thêm, đổi tên hoặc xoá file, phải đối chiếu lại `README.md` và `AGENTS.md` với cây thư mục thật.
