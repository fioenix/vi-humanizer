# Bằng chứng revision 0.9.5

**Ngày chạy:** 2026-09-29

**Phạm vi:** chuyển hai base profile sang cấu trúc `rules.md` + `styles/`, giữ resolver dùng chung trong `references/`

**Trạng thái:** đủ gate để tạo commit nguyên tử; không push

## TDD và inventory contract

- Ca `test_validator_rejects_extra_style_card_file` đã fail trước khi validator khóa exact inventory,
  sau đó pass.
- Ca `test_packager_rejects_style_card_under_incompatible_profile` đã fail trước khi validator khóa
  quan hệ profile–style, sau đó pass.
- Ca thiếu field bắt buộc, layout profile mới và recursive tell scan đều pass.
- Validator so exact file và directory inventory dưới `profiles/`; file thừa hoặc card nằm sai profile
  đều làm package fail trước khi archive được thay thế.

## Gate cuối từ bytes hiện hành

| Lệnh | Kết quả |
|---|---|
| `python3 scripts/validate-package.py` | PASS — `v0.9.5`, 55 pattern |
| `python3 -m unittest discover -v` | PASS — 144 test, 0 failure |
| `./scripts/package-skill.sh` | PASS — source tree và cả hai archive được validator đọc lại từng byte |
| `npx skills add . --list` | PASS — tìm thấy đúng skill `vi-humanizer` |
| `claude plugin validate .` | PASS — marketplace manifest hợp lệ |
| `git diff --check` | PASS |

Hai thông báo `unchecked`/`collect_more_labels` trong test evaluator là kết quả contract mong đợi khi
không dùng credential; toàn bộ test vẫn kết thúc `OK`.

## Archive và public inventory

| Artifact | SHA-256 | Layout |
|---|---|---|
| `dist/vi-humanizer.skill` | `dfe653187432a37744a76daa6bdb406e50b312c8f02dd92b654ecb2f9928b43c` | root `vi-humanizer/` |
| `dist/vi-humanizer-claude-org.zip` | `ca358f6ceac3e12dc72a676ec713697750cc7d27bc6da9a0b6285681f1083be5` | `SKILL.md` ở archive root |

Claude Org archive có 15 public file: `SKILL.md`, hai file calibration, ba reference, hai
`rules.md` và bảy style card. Không có `README.md`, `.claude-plugin/`, `.agents/`, `specs/`,
`tests/`, `scripts/`, `output/`, `research/` hoặc artifact evaluator.

### SHA-256 public source

```text
bad8ba2a921b33b0ed9d6d7e6aa696065f3a6a9380f27f9f4c09be291c5cb94f  SKILL.md
91d375b8886e689da3d58ce0d707dc31002969e7309b8913dd05fa4ec48bb7a0  calibration/LOG.md
e3af6438e558dfc16cadc105ac8c050a7d962a0e3a8fef9a59e350d90fff90f2  calibration/ca-kiem-thu.md
c808707eeb6c1410c7466518773e8a7b85c36c0708e6665f90e7c6f9c4d1e769  profiles/blog-ca-nhan/rules.md
c4383f9e6adcb4b878d7e1a673bb52f458ab656e3a05f76242d7032cc96aa34d  profiles/blog-ca-nhan/styles/chuyen-mon-cong-khai.md
5fd999ceff17bcdfd6de8bbd0397b776d301bcf2107fe8ffb59d9c7764101b6e  profiles/blog-ca-nhan/styles/ke-trai-nghiem.md
3df8554731ed4145ddc88c2afd6f8dd7a6307e31c58295dc47e3d31433164b5f  profiles/blog-ca-nhan/styles/marketing-thuyet-phuc.md
c7d9a8fe5af9a88f77dab8635b7c69285c519b798495c821c178a3c0327f5f92  profiles/blog-ca-nhan/styles/phoi-hop-cong-viec.md
8df9e59a7f97d479ef666355033a155cd0dc765cebf0fc0114b1a20a3c546703  profiles/ky-thuat-doanh-nghiep/rules.md
5a0d7ce925895af4487fc4a4bc9341250e545f817db4bc7ff723f5b60f6aded5  profiles/ky-thuat-doanh-nghiep/styles/hoc-thuat-phan-tich.md
58e433e8c94e1b78aa7723ce43d65fcb62c43b443596aaf2464b0daad149514f  profiles/ky-thuat-doanh-nghiep/styles/huong-dan-ky-thuat.md
1a6f182234d4705c1e8a7106e56b141ed7ab1186f016476f0c0c818e9d6531f6  profiles/ky-thuat-doanh-nghiep/styles/van-hanh-doanh-nghiep.md
49b59386a239fab9c2355c038c2cb9840e5f87a6a8431ee0bc508627c2c9fb0e  references/bang-tra-cuu.md
17b40f8acffb809501f09b971cc515ab7fdfb39f1719a5f23bb90a88268af281  references/bo-giai-phong-cach.md
b2daba8810ce47e0647db4bcc53208418788949647520f29659ebeddf15a359f  references/han-viet-thuan-viet.md
```

## Privacy và review

- Scan public payload không thấy machine path, tên tổ chức riêng hoặc giá trị có hình dạng secret.
- Không có API key, request body, raw exception hoặc prose từ evaluator trong archive.
- Review độc lập không tìm thấy finding Critical; hai finding Important về exact inventory và
  Spec Kit drift đã được sửa trước khi chạy lại gate cuối.
- TypeSafe/evaluator không đổi trong revision này.

Revision được tích hợp bằng chính commit chứa file bằng chứng và trạng thái task này. Việc push cần
lệnh riêng của owner.
