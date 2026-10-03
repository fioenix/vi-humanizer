# Phân phối plugin vietnamizer

Bằng chứng kiểm tên mới: [rename-vietnamizer-2026-10-03.md](rename-vietnamizer-2026-10-03.md).
Báo cáo [plugin-readiness-2026-10-03.md](plugin-readiness-2026-10-03.md) ghi snapshot tên cũ trước migration.

## Một nội dung, nhiều đường cài

Root `SKILL.md` là nguồn chuẩn. Manifest source của Codex và Claude Code trỏ tới adapter mỏng
trong `.plugin-skills/`; adapter nạp file chuẩn và resolve resource từ root plugin. Gói plugin
được sinh với layout `skills/vietnamizer/`, manifest trỏ tới `./skills/`. Không commit bản skill
thứ hai. Các file trong `agents/` và `assets/` đi cùng skill để UI không mất icon khi cài riêng.

| Artifact | Mục đích | Layout |
|---|---|---|
| `vietnamizer.skill` | Custom skill và cài skill thông thường | `vietnamizer/SKILL.md` |
| `vietnamizer-claude-org.zip` | Upload skill vào Claude Org | `SKILL.md` ở root |
| `vietnamizer-plugin.zip` | Gói plugin Codex/Claude Code | Hai manifest, một `skills/vietnamizer/SKILL.md` |

Tạo cả ba artifact bằng `python3 scripts/package-plugin.py`. `dist/` là output sinh ra, không
commit. Plugin ZIP chỉ chứa public payload, MIT notice, nhận diện và manifest; không chứa Spec
Kit, generated maintainer skills, CLI advisor, corpus evaluation hoặc credential.

Từ v0.9.7, repo cũng không còn advisor, SDK hoặc evaluation harness TypeSafe. Hướng dẫn
được đóng gói chỉ mô tả cách tận dụng skill chính chủ đã có khi hữu ích và có quyền gửi dữ liệu.

Catalog source trỏ tới root repo, vẫn gồm tooling maintainer và hồ sơ lịch sử. Validator local
và inventory ZIP không thay thế portal Validate cho commit GitHub thực tế; không suy ra directory
approval hoặc bắt buộc tách repo chỉ từ kết quả đóng gói.

## Kiểm từ clone trước khi phát hành

```bash
python3 scripts/validate-package.py
python3 scripts/package-plugin.py --check
python3 scripts/package-plugin.py
claude plugin validate .
claude plugin validate .claude-plugin/plugin.json --strict
npx --yes skills@1.5.20 add . --list
```

`--check` không dựng archive. Cần kiểm thêm đường cài trên profile tạm: thêm marketplace từ
clone, cài `vietnamizer@vietnamizer`, kiểm plugin cache có manifest đúng version và skill nạp
đúng tên. Với Codex có thể dùng app-server `skills/list` để kiểm discovery mà không gọi model.
Với Claude Code, cài xong mở session mới và kiểm `/vietnamizer:vietnamizer`; metadata validator
hoặc thông báo install thành công không tự chứng minh UI đã hiển thị hay invocation chạy được.

Không đưa credential hoặc raw input của người dùng vào log kiểm. Profile thật của maintainer
không phải fixture kiểm thử. Không gọi dịch vụ TypeSafe chỉ để kiểm plugin packaging.

## Nhận diện và listing

Nguồn chuẩn: [Plugin guidelines](https://developers.openai.com/plugins/plugin-guidelines)
và [Submit plugins](https://developers.openai.com/plugins/deploy/submission).

Base subtitle và description Codex dùng tiếng Anh theo hướng dẫn submission. Bản dịch tiếng
Việt nằm trong `extensions.com.openai.publication.translations`; importer hiện giữ bản dịch
nhưng chưa dùng chúng để đổi nội dung Directory hiển thị. Skill và listing Claude vẫn dùng
tiếng Việt. Giữ category `Productivity`: mô tả rõ biên tập tài liệu, tin nhắn và bản dịch theo
thể loại, không chỉ nêu một lời hứa “tự nhiên hơn”. Không bảo đảm category sẽ được chấp thuận.

Gate riêng của repo yêu cầu đủ URL website, hỗ trợ, privacy và terms với HTTPS, không chứa
credential. Đây là tiêu chuẩn phân phối của Vietnamizer; không phải khẳng định schema bắt
buộc cả bốn URL đối với mọi skills-only plugin. Kiểm riêng nội dung tiếng Anh và quyền sử dụng
tài sản khi review; validator không suy ra được hai điều này từ định dạng.

Không ghi đè gói 0.9.7 đã công bố bằng candidate 0.9.8. Kiểm gói mới, tích hợp source và phát
hành phiên bản mới trước khi dùng nó để cập nhật listing. Scan, publisher verification và
eligibility trên portal là các cổng riêng, không được thay bằng kết quả kiểm offline.

Icon là chữ `ă` vẽ bằng hình học SVG, không phụ thuộc font hoặc ảnh bên ngoài. Bản sáng/tối có
viewBox vuông 128×128; wordmark dùng cho README/giới thiệu, không thay icon listing vuông.
Màu dùng các token FINOLABS đã duyệt: `fn-violet` (`#9750C4`), `fn-mint` (`#7FE2CE`),
`ink-900` (`#0B0B17`), `ink-50` (`#F7F7FB`), `ink-300` (`#BCBCD0`) và `ink-500` (`#5B5B79`).
Icon có nền trong suốt: bản sáng dùng violet, bản tối dùng mint. Metadata Codex dùng violet
cho `brandColor` và mint cho `brandColorDark`; skill UI dùng violet cho trường màu duy nhất. SVG/JSON/YAML
chứa giá trị token được xuất cố định để gói cài không phụ thuộc CSS hoặc repo FINOLABS bên ngoài.
Hai wordmark `assets/wordmark.svg` và `assets/wordmark-dark.svg` có nền trong suốt;
chữ `ă` dùng violet FINOLABS `#9750C4` ở bản sáng và mint `#7FE2CE` ở bản tối,
không dùng gradient ở cả hai chế độ.
Tên và tagline dùng màu chữ trung tính phù hợp từng chế độ. SVG không tải tài nguyên bên ngoài.
Metadata Codex có logo, composer icon, màu và starter prompts; metadata Claude có icon cùng
đường dẫn tài liệu, hỗ trợ, quyền riêng tư và điều kiện sử dụng. Các URL `main` chỉ có nội dung
public sau khi thay đổi tương ứng đã merge.

## Repo marketplace không phải directory chính thức

`.agents/plugins/marketplace.json` và `.claude-plugin/marketplace.json` là catalog do maintainer
kiểm soát. Người dùng có thể đăng ký repo và cài plugin; đây không phải dấu hiệu OpenAI hoặc
Anthropic đã review hay bảo chứng plugin.

Gửi vào directory chính thức là bước riêng, cần quyền tài khoản publisher, kiểm lại yêu cầu
submission tại thời điểm gửi và owner duyệt trước khi nộp. Không tạo MCP server, auth flow,
screenshots giả hoặc capability không có thật chỉ để lấp trường metadata.

Nguồn định dạng:

- [OpenAI: plugin package và marketplace](https://developers.openai.com/plugins/build/plugins).
- [OpenAI: listing metadata và icon](https://developers.openai.com/plugins/deploy/submission).
- [Claude Code: plugin manifest](https://code.claude.com/docs/en/plugins-reference).
