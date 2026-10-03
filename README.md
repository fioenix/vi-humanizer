# Vietnamizer

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/icon-dark.svg">
  <img src="assets/icon.svg" alt="vietnamizer — dấu tiếng Việt" width="80" height="80">
</picture>

> **Sửa tiếng Việt tự nhiên hơn, giữ nguyên ý và giọng người viết.**

Vietnamizer là skill dành cho Claude, Codex và các agent hỗ trợ Skills CLI. Skill xác định thể
loại cùng người đọc trước, gọi tên lỗi rồi chỉ sửa phần thực sự có vấn đề. Blog vẫn giữ cá tính;
README vẫn giữ thuật ngữ kỹ thuật; báo cáo doanh nghiệp không bị kéo thành lời trò chuyện.

Skill dùng được cho bản nháp do AI tạo, bản dịch sát tiếng Anh, nội dung do người viết song ngữ soạn
hoặc bất kỳ đoạn tiếng Việt nào đọc chưa thuận miệng. Đây không phải công cụ phát hiện AI và không
dùng lỗi ngôn ngữ để đoán tác giả.

## Ba ví dụ đã được hiệu chỉnh

| Mục tiêu | Trước | Sau khi biên tập |
|---|---|---|
| Hoàn chỉnh ý | *Đã thử ba cách mà vẫn không giải quyết vấn đề.* | *Đã thử ba cách mà vẫn không giải quyết **được** vấn đề.* |
| Khôi phục từ bị thiếu | *Câu này đúng ngữ pháp nhưng đọc lên thấy hụt.* | *Câu này đúng ngữ pháp nhưng đọc lên thấy **hụt hẫng**.* |
| Giữ đúng giọng công việc | *Đội kỹ thuật đã triển khai hệ thống quản lý kho mới để vận hành gọn hơn.* | *Nhằm mục đích nâng cao hiệu quả vận hành kho, **team dev** đã triển khai hệ thống quản lý kho mới.* |

Các cặp trên lấy từ [nhật ký hiệu chuẩn](calibration/LOG.md) và những ví dụ đã khóa trong
`SKILL.md`. Đây không phải bảng tìm–thay cố định: skill chỉ sửa khi ngữ cảnh, thể loại và mẫu giọng
cho thấy bản gốc thật sự có vấn đề.

## Cài nhanh

Tên mới từ bản **0.9.7**: Vietnamizer, định danh `vietnamizer` (trước đây là
`vi-humanizer`). Các lệnh dưới đây dùng source đã đổi tên; trước khi source được merge,
hãy dùng checkout của nhánh thay đổi thay vì cài từ `main`. Bản 0.9.7 chưa phát hành;
asset của các release cũ vẫn mang tên `vi-humanizer.*` và chứa định danh cũ.
Xem [hướng dẫn chuyển tên](docs/rename-vietnamizer-2026-10-03.md).

### Codex và các agent dùng Skills CLI

```bash
npx skills add fioenix/vietnamizer --global
```

Cài cho mọi agent mà Skills CLI hỗ trợ:

```bash
npx skills add fioenix/vietnamizer \
  --skill vietnamizer \
  --agent '*' \
  --global \
  --yes
```

Bỏ `--global` nếu muốn cài trong phạm vi dự án. Có thể xem skill mà CLI tìm được trước khi cài:

```bash
npx skills add fioenix/vietnamizer --list
```

Skills CLI nhận repository, URL hoặc đường dẫn cục bộ làm nguồn. Cờ `--agent '*'` chọn mọi agent được hỗ trợ; cờ `--copy` buộc CLI sao chép file thay vì tạo liên kết tượng trưng.

### Claude Code plugin

```text
/plugin marketplace add fioenix/vietnamizer
/plugin install vietnamizer@vietnamizer
```

Sau khi cài, gọi skill bằng `/vietnamizer:vietnamizer`.

### Codex plugin và Marketplace

Từ v0.9.7, repo có catalog Codex riêng bên cạnh catalog Claude Code:

```bash
codex plugin marketplace add fioenix/vietnamizer
codex plugin add vietnamizer@vietnamizer
```

Trong ứng dụng hỗ trợ repo marketplace, chọn nguồn `vietnamizer` trong trang Plugins rồi cài
plugin. Khả năng hiển thị tùy client; Skills CLI ở trên vẫn là đường cài độc lập. Catalog của
repo không đồng nghĩa plugin đã được duyệt vào directory chính thức của OpenAI hoặc Anthropic.

Xem [hướng dẫn phân phối và kiểm thử](docs/plugin-distribution.md),
[quyền riêng tư](PRIVACY.md) và [điều kiện sử dụng](TERMS.md).

### Claude và Claude Desktop

[Tải gói skill từ trang Releases](https://github.com/fioenix/vietnamizer/releases/latest),
mở **Customize → Skills → + Create skill → Upload a skill**, chọn file vừa tải rồi bật skill.
Claude cần bật **Code execution and file creation** để dùng custom skill. Xem thêm
[hướng dẫn chính thức của Claude](https://support.claude.com/en/articles/12512180-use-skills-in-claude).

### Claude Org

[Tải gói Claude Org từ trang Releases](https://github.com/fioenix/vietnamizer/releases/latest),
mở **Organization settings → Plugins & skills → Add → Upload a skill**, rồi chọn file ZIP. Gói này
đặt `SKILL.md` và `LICENSE` ở thư mục gốc, cùng các file cần khi skill chạy.

### Đóng gói từ source

Người bảo trì repo có thể tự tạo lại cả hai artifact:

```bash
./scripts/package-skill.sh
```

Kết quả nằm ở `dist/vietnamizer.skill` và `dist/vietnamizer-claude-org.zip`.

Để tạo gói plugin chung cho Codex và Claude Code:

```bash
python3 scripts/package-plugin.py
```

Kết quả là `dist/vietnamizer-plugin.zip`, có hai manifest và một skill trong
`skills/vietnamizer/`. Script tạo gói từ source chuẩn; không bảo trì bản Markdown thứ hai.

### Cài thủ công

Chép `LICENSE`, `SKILL.md` cùng `profiles/`, `references/`, `calibration/`, `agents/`, `assets/` và optional runtime `advisor/` vào
thư mục skill của agent:

```bash
git clone https://github.com/fioenix/vietnamizer.git /duong/dan/toi/skills/vietnamizer
```

## Dùng ngay

```text
/vietnamizer

[văn bản cần biên tập]
```

Khi cần sửa file, nêu rõ phạm vi:

```text
Dùng vietnamizer để sửa phần văn xuôi trong docs/bai-viet.md.
Giữ nguyên code, bảng tham số và các trích dẫn.
```

## Phạm vi

Skill xử lý ba lớp:

- V1–V25 kiểm tra cách dùng từ và cấu trúc câu, chẳng hạn thiếu bổ ngữ kết quả, thiếu loại từ, dịch sát giới từ, đặt trạng ngữ gây mơ hồ hoặc để sót lời chào của trợ lý trong tài liệu.
- B1–B17 và K1–K7 kiểm tra sự phù hợp với thể loại. Blog, tin nhắn, README và bài nghiên cứu không dùng cùng một giọng.
- T1–T6 kiểm tra typography. Với văn xuôi thông thường, chỉ áp dụng khi đồng thời có ít nhất một lỗi
  V1–V25; với thể loại được giới hạn ở typography-only thì không cần lỗi V đi kèm.

Trước khi sửa, skill xác định thể loại, đọc profile phù hợp và kiểm tra mẫu văn hoặc hồ sơ cá nhân của đúng người dùng nếu nền tảng cung cấp memory hay knowledge base.

Skill không dùng kết quả rà soát để xác định tác giả. Người viết song ngữ cũng có thể giữ cấu trúc tiếng Anh trong câu tiếng Việt; LLM cũng có thể tạo ra câu hoàn toàn tự nhiên.

### TypeSafe/Jev là lớp tăng cường tùy chọn

`vietnamizer` không cần TypeSafe, `typesafe-sdk`, API key hoặc kết nối mạng để biên tập. Nếu không
cấu hình gì thêm, toàn bộ quy trình thể loại, pattern, style card và năm quy tắc chốt chặn vẫn chạy
bình thường. Public package có thêm optional CLI `advisor/`, viết bằng Python standard library;
core Markdown không import hoặc phụ thuộc CLI này.

Muốn bật trên host local, cần Python 3.10+, HTTPS và cơ chế inject secret. Lưu API key bằng secret
manager của host, inject nó thành `TYPESAFE_API_KEY` cho process chạy agent, rồi từ thư mục skill
chạy `python3 -m advisor probe`. Không dán key vào prompt, command argument, file repo hoặc ZIP;
không có cờ `enabled` thứ hai. Chỉ typed response thật với model `jev-1.13.0` mới tạo trạng thái
`advisor_verified`; có key hoặc config mới chỉ là opt-in, chưa phải bằng chứng integration đang chạy.

Advisor chỉ dùng cho hai tín hiệu V20, sau khi host LLM đã tạo candidate. Jev trả signal có cấu trúc
nhưng không sinh/sửa câu chữ và không quyết định thay source; host Agent vẫn chọn giữ hay sửa. Nếu
thiếu key, host capability hoặc dịch vụ không phản hồi, CLI trả `core_only`/`advisor_unchecked` và
core tiếp tục; đó là *chưa kiểm tra*, không phải `pass`. TypeSafe agent skill chỉ cung cấp tài liệu
cho coding agent, không tự tạo runtime connector. ZIP Claude Org có `advisor/` nhưng vẫn core-only
nếu môi trường Org không cho chạy Python, gọi mạng hoặc inject secret. Hướng dẫn đầy đủ nằm trong
[`references/typesafe-advisor.md`](references/typesafe-advisor.md).

Riêng evaluation harness live mới cần dependency tùy chọn qua `uv sync --locked --group eval`;
validator và test offline không gọi TypeSafe.

## Giữ giọng và chọn phong cách

### Giữ giọng của một người cụ thể

Có thể đưa mẫu văn ngay trong yêu cầu:

```text
Đây là hai đoạn tôi tự viết:
[mẫu văn]

Hãy sửa đoạn dưới theo cùng cách xưng hô, nhịp câu và mức độ trang trọng:
[văn bản cần sửa]
```

Mẫu văn chỉ được ưu tiên đối với thói quen xuất hiện nhất quán, như cách xưng hô, nhịp câu, cách chêm tiếng Anh hoặc dùng dấu câu. Nó không hợp thức hoá lỗi ngôn ngữ rõ ràng và không vượt qua năm quy tắc chốt chặn trong `SKILL.md`.

Nếu agent có memory hoặc knowledge base, nó nên đọc hồ sơ văn phong của đúng người dùng trước khi sửa. Hồ sơ này phải tách riêng theo người, chỉ lưu đặc tính cần thiết cho việc giữ giọng và luôn nhường chỗ cho yêu cầu hiện tại.

### Chọn phong cách theo mục đích

`vietnamizer` không còn gom mọi văn bản vào hai giọng *cá nhân* và *trung tính*. Hai profile đó vẫn
giữ vai trò cổng pattern, còn bộ giải phong cách chọn một card theo mục đích, người đọc, quan hệ,
thanh ngữ vực, kênh và mẫu giọng. Một phần văn bản chỉ dùng tối đa một card; file pha nhiều chức
năng được chia theo phần, không ép chung một giọng.

| Style card | Dùng cho | Base profile |
|---|---|---|
| [`ke-trai-nghiem`](profiles/blog-ca-nhan/styles/ke-trai-nghiem.md) | Blog, bài kể có người viết hiện diện | `blog-ca-nhan` |
| [`phoi-hop-cong-viec`](profiles/blog-ca-nhan/styles/phoi-hop-cong-viec.md) | Chat, bình luận và lời nhờ trong công việc | `blog-ca-nhan` |
| [`chuyen-mon-cong-khai`](profiles/blog-ca-nhan/styles/chuyen-mon-cong-khai.md) | LinkedIn, bài quan điểm hoặc chia sẻ chuyên môn | `blog-ca-nhan` |
| [`marketing-thuyet-phuc`](profiles/blog-ca-nhan/styles/marketing-thuyet-phuc.md) | Nội dung giới thiệu có mục tiêu và CTA thật | `blog-ca-nhan` |
| [`huong-dan-ky-thuat`](profiles/ky-thuat-doanh-nghiep/styles/huong-dan-ky-thuat.md) | README, văn xuôi API và hướng dẫn xử lý lỗi | `ky-thuat-doanh-nghiep` |
| [`van-hanh-doanh-nghiep`](profiles/ky-thuat-doanh-nghiep/styles/van-hanh-doanh-nghiep.md) | SOP, báo cáo, biên bản và bàn giao | `ky-thuat-doanh-nghiep` |
| [`hoc-thuat-phan-tich`](profiles/ky-thuat-doanh-nghiep/styles/hoc-thuat-phan-tich.md) | Giáo trình, đề án và nghiên cứu | `ky-thuat-doanh-nghiep` |

Card không phải khuôn để “làm màu” và không tự tạo lý do sửa. Yêu cầu hiện tại được ưu tiên;
ràng buộc thể loại và năm quy tắc chốt chặn vẫn giới hạn mọi thay đổi; mẫu/hồ sơ chỉ được dùng khi
đúng người, đúng phạm vi và có đặc tính ổn định. Chi tiết chuẩn nằm trong
`references/bo-giai-phong-cach.md`.

## Kiến trúc

`SKILL.md` là nguồn chuẩn. Các file còn lại bổ sung quy tắc theo thể loại, ví dụ hoặc dữ liệu bảo trì:

```text
SKILL.md                                      quy trình, V1–V25, T1–T6 và cách trả kết quả
profiles/blog-ca-nhan/rules.md                B1–B17 cho văn bản có giọng cá nhân
profiles/blog-ca-nhan/styles/                 bốn style card có tác giả hiện diện
profiles/ky-thuat-doanh-nghiep/rules.md       K1–K7 và giới hạn của văn kỹ thuật, học thuật
profiles/ky-thuat-doanh-nghiep/styles/        ba style card kỹ thuật, vận hành và học thuật
references/han-viet-thuan-viet.md             bảng tra và điều kiện phải giữ thuật ngữ
references/bang-tra-cuu.md                    bảng tra hư từ, loại từ, tiểu từ và câu hỏi chẩn đoán
references/bo-giai-phong-cach.md              bộ giải ngữ cảnh, precedence và registry đường dẫn
references/typesafe-advisor.md                setup, authority, privacy và fallback của advisor
calibration/LOG.md                            bằng chứng dùng để sửa quy tắc chung
calibration/ca-kiem-thu.md                    ca kiểm thử chạy tay cho từng pattern
advisor/                                      optional TypeSafe CLI; core Markdown không phụ thuộc
agents/openai.yaml                            tên hiển thị và lời gọi mặc định
assets/                                       icon sáng/tối và wordmark SVG gốc
.codex-plugin/plugin.json                     manifest và nhận diện plugin Codex
.plugin-skills/vietnamizer/SKILL.md          adapter source, nạp root SKILL.md; không sao chép rule
.claude-plugin/                              manifest và catalog Claude Code
.agents/plugins/marketplace.json             catalog Codex được track, không phải tooling sinh local
scripts/validate-package.py                   kiểm tra tính đồng bộ của gói
scripts/package-skill.sh                      tạo hai artifact cài đặt
scripts/package-plugin.py                     kiểm metadata và tạo ZIP plugin hai nền tảng
docs/plugin-distribution.md                   đường cài, kiểm thử và giới hạn publication
scripts/scan-tells.sh                         tìm những chỗ có thể rà bằng biểu thức chính quy
.specify/                                     constitution, template và script của Spec Kit
specs/                                        đặc tả, checklist, plan và task theo từng feature
guard_eval/                                   evaluation harness cho edit guard, không thuộc gói skill
eval/guard/                                   corpus, manifest, config, pricing và policy đã duyệt
tests/guard_eval/                             test offline; external evaluator luôn được fake trong CI
artifacts/guard-eval/                         raw run local, bị gitignore và không chứa raw prose
guard_eval/v2/                                lane tạo shadow recommendation theo component
eval/guard/v2/                                dev corpus v2, lock v1 và registry holdout đã quan sát
tests/guard_eval_v2/                          contract/integration test offline cho lane v2
tests/advisor/                                contract/integration test offline cho public advisor
artifacts/guard-eval-v2/                      raw run v2 local, bị gitignore
pyproject.toml, uv.lock                       môi trường Python 3.12 khóa version cho harness
```

Các file từ `.specify/` trở xuống phục vụ quy trình phát triển và không nằm trong gói
`vietnamizer.skill`.

Generated agent skills, Spec Kit integration state, raw run và scratch output được giữ local.
Xem [hướng dẫn đóng góp](CONTRIBUTING.md) để cài tooling maintainer và chạy kiểm tra offline.

Bộ giải phong cách dùng đúng bảy card trong bảng cách dùng ở trên. Nội dung chuẩn của từng card nằm
trong thư mục `styles/` của profile tương thích; `references/bo-giai-phong-cach.md` chỉ sở hữu cách
chọn card, thứ tự ưu tiên và registry đường dẫn.

### Evaluation harness cho edit guard

Harness v1 giữ nguyên để làm baseline. Lane v2 bổ sung tín hiệu về *có nên sửa hay không* và
*candidate nào đủ chuẩn*: host LLM tạo sẵn từ một đến ba candidate; Jev chỉ chấm hai dấu hiệu ở
nguồn, ba thành phần chất lượng và sáu chiều safety cho từng candidate. Policy tất định suy ra
shortlist và shadow recommendation `keep`, `replace` hoặc `review`; Choice chỉ xếp hạng khi có ít
nhất hai candidate đã qua cổng. Jev không sinh, nối hoặc sửa văn bản, còn host Agent/LLM giữ quyền
quyết định cuối cùng và thực hiện biên tập.

Cài môi trường và chạy toàn bộ đường offline:

```bash
uv sync --locked --group eval
uv run --locked python -m unittest discover -s tests -p 'test_*.py' -v
env -u TYPESAFE_API_KEY uv run --locked python -m guard_eval validate \
  --manifest eval/guard/manifest.json
env -u TYPESAFE_API_KEY uv run --locked python -m guard_eval.v2 validate \
  --manifest eval/guard/v2/manifest.json
```

`candidate_origin` phân biệt `host_llm_output`, `baseline_observation` và
`maintainer_fixture`; origin, ground truth và baseline không được gửi cho evaluator. Live dev và
holdout run cần maintainer hoặc agent được owner ủy quyền rõ cho phép dùng credential/quota riêng.
Mỗi lane chỉ ghi policy sau khi dev labels và candidate policy đã được review. Holdout v2 đã được
niêm phong, chạy một lần và ghi vào registry; report trả `collect_more_labels`, nên v2 vẫn chỉ là
evidence lane, chưa được bật làm runtime gate. Raw run nằm dưới `artifacts/guard-eval*/`; chỉ báo cáo holdout
đã loại raw prose mới được đưa vào `specs/.../evidence/`.

Trước khi chạy pattern, skill kiểm tra thể loại. Pháp quy, hợp đồng, thơ, văn cổ phong và nghi lễ chỉ
được rà T1–T6. Code, schema, dữ liệu có cấu trúc, bảng tham số, trích dẫn nguyên văn, tên riêng và ví
dụ đang được bàn tới là vùng bảo toàn từng byte. Xem danh sách và ngoại lệ đầy đủ trong `SKILL.md`.

## Danh mục pattern

### Cách dùng từ và cấu trúc câu (V1–V25)

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
| V21 | Tàn dư lượt hội thoại của trợ lý | *Chắc chắn rồi! Dưới đây là ba bước...* → *Ba bước triển khai...* |
| V22 | Rào trước về nguồn rồi đưa phỏng đoán | *Không có thông tin công bố. Nhiều khả năng công ty bắt đầu từ đầu những năm 2000.* → giữ điều nguồn nói, bỏ phần đoán |
| V23 | Phản biện một ý không có đối tượng | Bỏ vỏ *không ai phủ nhận...* khi mạch văn không có ý nào cần phản biện |
| V24 | Chồng từ chỉ khả năng cùng chức năng | *có khả năng có thể* → giữ một mức khả năng; không đụng các từ có phạm vi nghĩa khác nhau |
| V25 | Làm mơ hồ quan hệ đã có trong nguồn | Khôi phục *phụ thuộc ở runtime* thay vì *có quan hệ* khi nguồn trong phạm vi đã nêu rõ |

### Typography (T1–T6)

| # | Pattern |
|---|---|
| T1 | Viết hoa theo kiểu tiêu đề tiếng Anh |
| T2 | Em dash và gạch ngang chú thích giữa câu |
| T3 | Ngoặc kép không nhất quán |
| T4 | Dấu phẩy đứng trước "và" |
| T5 | Định dạng thay cho cấu trúc câu |
| T6 | Emoji |

Với văn xuôi thông thường, typography chỉ được sửa khi văn bản đồng thời có ít nhất một pattern
V1–V25. Thể loại được cổng đầu vào giới hạn ở T1–T6 là ngoại lệ; vùng bảo toàn vẫn giữ nguyên từng byte.

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
| B8 | Danh xưng và thẩm quyền phóng đại |
| B9 | Hán-Việt hoá tên gọi đời thường |
| B10 | Thành ngữ dùng lệch và mật độ thành ngữ bất thường |
| B11 | Nhịp ba cân âm tiết và biền ngẫu giả |
| B12 | Cụm bốn âm tiết Hán-Việt tự chế |
| B13 | Nhịp câu đều đặn bất thường |
| B14 | Rụng tiểu từ tình thái cuối câu |
| B15 | Xưng hô lơ lửng và phẳng |
| B16 | Giả thân mật |
| B17 | Trộn mức độ trang trọng không chủ đích |

### Tài liệu kỹ thuật, doanh nghiệp và học thuật (K1–K7)

| # | Pattern |
|---|---|
| K1 | Viết theo diff thay vì mô tả hiện trạng |
| K2 | Sáo ngữ thể chế rỗng ngoài văn bản pháp quy |
| K3 | Bộ đề mục Hán-Việt đối xứng rỗng |
| K4 | Mô tả hiện tượng mà không đưa hiện tượng ra |
| K5 | Câu dẫn nhập rỗng sau đề mục |
| K6 | Siêu dữ liệu về quá trình tạo ra văn bản |
| K7 | Dẫn uy tín vô danh thay cho bằng chứng |

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

### Nguồn gợi ý giả thuyết

- [`blader/humanizer` 3.0.0](https://github.com/blader/humanizer/tree/v3.0.0) chỉ được dùng để nêu
  giả thuyết cho V23–V25, phần mở rộng B8 và K7. Quyết định tiếng Việt dựa trên các ca dương/âm và
  bằng chứng ghi ngày 28/09/2026 trong `calibration/LOG.md`; repo upstream không được coi là nguồn
  quy phạm tiếng Việt.

### Nguồn còn thiếu

- V3 và V13 cần thêm nguồn gốc về lý thuyết đề–thuyết thay cho các bài trình bày lại.
- V16 cần thêm nghiên cứu công bố trực tiếp về đối chiếu câu bị động Anh–Việt.

## Tác giả và ghi nhận

`vietnamizer` do Fioenix thiết kế và duy trì. Codex và Claude Code được dùng làm agent kỹ thuật để
hỗ trợ nghiên cứu, triển khai, kiểm thử và review.

Cách đóng gói và khung **Dấu hiệu / Vì sao / Sửa / Không flag** tham khảo
[blader/humanizer](https://github.com/blader/humanizer) cùng hướng dẫn của WikiProject AI Cleanup.
Các pattern tiếng Việt được xây dựng riêng cho repo này.

## Lịch sử phiên bản

- **0.9.7** – Đưa `LICENSE` vào cả hai archive, giữ MIT notice cho tooling Spec Kit và chuyển
  generated Codex integration cùng state từng checkout ra khỏi Git tracking. Bổ sung ignore
  hẹp cho tooling local, environment, scratch output và cache; thêm hướng dẫn contributor cùng
  gate CI chặn file tracked bị ignore. Thêm icon SVG sáng/tối, metadata UI, catalog Codex và ZIP plugin chung với
  Claude Code; cả hai dùng một nguồn skill chuẩn. Bổ sung thông tin quyền riêng tư, điều kiện
  sử dụng và kiểm tra asset/metadata trước đóng gói.
  Đổi thương hiệu từ vi-humanizer sang Vietnamizer, đồng bộ định danh skill/plugin/catalog,
  repo và tên gói tải thành `vietnamizer`. Quy tắc biên tập giữ nguyên.
- **0.9.6** – Đóng gói optional TypeSafe advisor CLI cho host local: probe thật mới xác nhận
  readiness, assess/rank chỉ trả typed signal cho lát cắt V20, còn host Agent giữ quyền quyết định
  và viết câu cuối. Core vẫn chạy không key, không mạng và không SDK; cả `.skill` lẫn ZIP Claude
  Org chứa adapter nhưng không chứa secret hoặc mạo nhận capability của host. README đưa ba ví dụ
  đã hiệu chỉnh và các đường cài trực tiếp từ artifact phát hành lên đầu trang.
- **0.9.5** – Tổ chức hai base profile thành thư mục cha–con: `rules.md` giữ B/K pattern, còn bảy
  style card nằm trong `styles/` của profile tương thích. Gói Claude Org nay hiển thị riêng từng
  phong cách; resolver và bảng tra dùng chung vẫn nằm trong `references/`. Nếu prompt hoặc công cụ
  đang đọc trực tiếp `profiles/blog-ca-nhan.md` hay `profiles/ky-thuat-doanh-nghiep.md`, hãy chuyển
  sang file `rules.md` trong thư mục profile cùng tên.
- **0.9.1** – Sửa cổng typography-only để các thể loại bị giới hạn có thể chạy T1–T6 mà không cần
  một lỗi V đi kèm; tách code, schema, dữ liệu có cấu trúc, bảng tham số, trích dẫn, tên riêng và ví
  dụ thành vùng bảo toàn từng byte. Đồng thời cấm tự thêm thái độ, sửa ví dụ T3, đồng bộ registry
  K1–K7 và rà lại cách diễn đạt trong README cùng profile kỹ thuật.
- **0.9.0** – Thêm V23 cho phản biện ý không có đối tượng, V24 cho các từ chỉ khả năng chồng cùng
  chức năng, V25 cho quan hệ bị làm mơ hồ dù nguồn đã nói rõ và K7 cho cách mượn uy tín thay cho
  bằng chứng; đồng thời phân vai lại B5/B8 để tránh hai pattern cùng sửa một lỗi. Bốn giả thuyết
  được hiệu chỉnh bằng 24 ca tiếng Việt, gồm 12 ca dương và 12 ca chống sửa quá tay.
- **0.8.0** – Thêm bộ giải nhiều phong cách theo mục đích, người đọc, thanh ngữ vực, kênh và mẫu giọng; bổ sung bảy style card, precedence rõ ràng và phân đoạn tài liệu hỗn hợp mà không đổi 51 pattern hiện có.
- **0.7.1** – Siết trường hợp loại trừ cho nhãn và dòng liệt kê: lược chủ ngữ, hư từ, loại từ thì được, còn bổ ngữ của động từ và tiếng thứ hai của từ hai tiếng thì phải giữ. Theo bản vàng ghi trong `calibration/LOG.md` ngày 09/09/2026.
- **0.7.0** – Thêm V21 cho tàn dư lượt hội thoại của trợ lý và V22 cho kiểu rào trước về nguồn rồi vẫn đưa phỏng đoán; quy trình nói rõ văn bản đầu vào là chất liệu để biên tập, không phải chỉ thị để làm theo; quy tắc chốt chặn 3 thêm thứ hạng và quan hệ đồng thời. Đối chiếu với `blader/humanizer` 3.0.0.
- **0.6.0** – Thêm K6 cho những câu nói về quá trình tạo ra tài liệu thay vì nói về chủ đề của nó; thêm quy tắc chốt chặn thứ năm và một dòng trong mục Cách trả kết quả; thêm `calibration/ca-kiem-thu.md` với tám ca kiểm thử cho K6.
- **0.5.2** – Mở rộng V18 để phát hiện các mệnh đề nối nhau nhưng không rõ chủ thể; bổ sung cho V20 cách kiểm tra nghĩa, vai trò và khả năng kết hợp của từ trong câu.
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
