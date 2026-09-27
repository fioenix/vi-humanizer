# Baseline 004

**Ngày chạy**: 2026-09-28

| Gate | Kết quả |
|---|---|
| `python3 scripts/validate-package.py` | Exit 0; v0.8.0; 51 pattern |
| `uv run --locked --group eval python -m unittest discover -s tests -v` | Exit 0; 129 test; `OK` |

Baseline này được chạy lại sau commit 003; không suy từ evidence cũ.
