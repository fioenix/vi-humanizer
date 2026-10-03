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
Kit, generated maintainer skills, corpus evaluation hoặc credential.

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
không phải fixture kiểm thử. Không bật live advisor chỉ để kiểm plugin packaging.

## Nhận diện và listing

Icon là chữ `ă` vẽ bằng hình học SVG, không phụ thuộc font hoặc ảnh bên ngoài. Bản sáng/tối có
viewBox vuông 128×128; wordmark dùng cho README/giới thiệu, không thay icon listing vuông.
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
