# Đóng góp cho vietnamizer

Người dùng có thể gửi ca sửa sai hoặc đề xuất sửa bằng issue và pull request. Một ca hữu ích gồm
thể loại, người đọc, đoạn gốc, kết quả của skill, bản đối chiếu và lý do khác biệt. Chỉ gửi văn bản
mày có quyền công bố; thay dữ kiện riêng bằng ví dụ giả lập trước khi gửi.

`SKILL.md` sở hữu quy tắc chung; `profiles/` sở hữu quy tắc theo thể loại. Xem [AGENTS.md](AGENTS.md)
trước khi sửa rule. Sở thích văn phong cá nhân không được đưa vào calibration dùng chung.

## Chạy kiểm tra offline

Skill Markdown dùng trực tiếp, không cần build. Test đóng gói dùng Python 3.12 và standard library;
không cần SDK, `uv` hoặc TypeSafe API key.

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 scripts/validate-package.py
npx --yes skills@1.5.20 add . --list
claude plugin validate .
./scripts/package-skill.sh
python3 scripts/package-plugin.py
```

Skill packager cần `zip` và `unzip`; plugin packager dựng tiếp một ZIP chung cho hai nền tảng.
Các archive nằm trong `dist/`. Mỗi archive phải có `LICENSE`,
đúng public inventory và nội dung khớp source.

Vietnamizer không chứa mã tích hợp TypeSafe. Skill chỉ hướng dẫn dùng khả năng chính chủ
đã có trên host khi hữu ích và có quyền gửi dữ liệu. Không khôi phục runtime từ đặc tả cũ.
Các corpus, config và evidence cũ là hồ sơ lịch sử đã ngừng dùng, không phải harness thực thi.

## Tooling Spec Kit cho maintainer

Repo giữ constitution, template, script, workflow và `specs/` để review quyết định phát triển.
Generated skills và integration state thuộc từng checkout, được `.gitignore` chặn.

Cài CLI từ tag đã dùng cho tooling hiện tại rồi tạo Codex integration trong clone:

```bash
uv tool install 'git+https://github.com/github/spec-kit.git@v1.0.5'
specify integration install codex --script sh --integration-options='--skills'
```

CLI sẽ tạo `.agents/skills/`, `.specify/init-options.json`, `.specify/integration.json` và
`.specify/integrations/codex.manifest.json`. Các file này không được commit. Script và template
chung đã có sẵn; thông báo giữ nguyên shared infrastructure khi bootstrap là hành vi mong đợi.
Không chạy `specify init --here --force` chỉ để cài integration vì lệnh đó còn refresh tooling chung.

Tooling được vendor từ GitHub Spec Kit v1.0.5 giữ [MIT notice của upstream](.specify/LICENSE).
[Source licence tại tag đó](https://github.com/github/spec-kit/blob/v1.0.5/LICENSE).

## File được chia sẻ và file local

- Giữ source, fixtures, corpus có provenance, policy/config đã duyệt, lockfile và evidence public
  trong Git. `specs/*/research.md` là tài liệu thiết kế; `specs/*/evidence/` chứa báo cáo đã duyệt.
- `artifacts/` dành cho raw evaluation runs; `output/` và root `research/` dành cho scratch output.
  Các thư mục này, `dist/`, agent local state, cache và environment files được ignore.
- `.agents/skills/` là tooling sinh local; `.agents/plugins/marketplace.json` là catalog phân phối
  phải được track. Không ignore toàn bộ `.agents/` khi thêm integration mới.
- `.env.example` và `.env.*.example` được phép commit khi chỉ chứa placeholder.
- Corpus holdout đã được quan sát là evidence lịch sử. Trạng thái workflow `sealed` không làm file
  public trở thành bí mật; đánh giá độc lập tương lai phải dùng tập mới với quyền truy cập phù hợp.

## Trước khi gửi pull request

Giữ diff trong phạm vi thay đổi, kèm lệnh kiểm tra và kết quả mới. Khi sửa rule, ghi bằng chứng
vào `calibration/LOG.md` trước và thêm ca chống sửa quá tay. Khi đổi cây file, cập nhật README và
AGENTS trong cùng diff. Thay đổi package phải giữ manifest, version và archive validation đồng bộ.

CI kiểm offline tests, package validation và tracked paths. `.gitignore` chỉ giảm khả năng commit
nhầm; nó không chặn `git add -f` và không thay thế review dữ liệu hoặc secret scanning.
