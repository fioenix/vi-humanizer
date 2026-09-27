# Bằng chứng release gate 003

**Ngày chạy**: 2026-09-28
**Version**: 0.8.0
**Pattern inventory**: 51

| Gate | Kết quả |
|---|---|
| `uv run --locked --group eval python -m unittest discover -s tests -v` | Exit 0; 129 test; `OK` |
| `python3 scripts/validate-package.py` | Exit 0; `Gói vi-humanizer v0.8.0 hợp lệ, gồm 51 pattern` |
| `npx skills add . --list` | Exit 0; tìm thấy đúng skill `vi-humanizer` |
| `claude plugin validate .` | Exit 0; `Validation passed` |
| `git diff --check` | Exit 0; không có lỗi whitespace |

SHA-256 của diff tại thời điểm chạy gate:

```text
ca5f263c3e15f0f2cb43f482353951ae55954d2e0ffa1f4d588b5f8fd95ef8a6
```

SHA-256 của các consumer chính:

```text
284b5872dbb3ae4eecf065605cda718bb454b765e3876fb994e2b1001c82e4a3  SKILL.md
9b1cb14282db6728af180e44bce036a8a27f7627e78eb104ccb5a9c34e14ecfa  README.md
dee0a9a3a88a0a93d6ade7e895357185a614cd80c9806aab134c8ff14ad30849  .claude-plugin/plugin.json
3287b3da62780c2e8a393e2252312bd4ad7c9306596fa4d54d48e3ed6102c27b  references/bo-giai-phong-cach.md
82dd3cee3e7dd5cf10c64a53cf36c51dce23746d3addf6b0c753f6f6cd6ccc9c  profiles/blog-ca-nhan.md
7381a472fbe6bbe6e2951fc6a2621556159a565d69aa6566f3702a2fe99e8e24  profiles/ky-thuat-doanh-nghiep.md
7211b5f6eca024243aae849a4fcd241e1e917dd682e3d1d81fb3a065caf32f61  scripts/validate-package.py
```

Các gate trên được chạy lại độc lập trên working tree hiện tại; không suy từ checkbox trong
`tasks.md`.
