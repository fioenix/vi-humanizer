#!/usr/bin/env python3
"""Kiểm tra tính toàn vẹn của gói vi-humanizer, không phụ thuộc thư viện ngoài."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent

# Ngân sách dòng cho từng loại file. references/ không giới hạn vì là bảng tra cứu.
LINE_BUDGETS = {
    "SKILL.md": 550,
    "profiles/blog-ca-nhan.md": 320,
    "profiles/ky-thuat-doanh-nghiep.md": 220,
}

# Tiền tố pattern và file sở hữu. Mỗi tiền tố phải đánh số liên tục từ 1.
PATTERN_OWNERS = {
    "V": "SKILL.md",   # lỗi dùng từ và cấu trúc câu
    "T": "SKILL.md",   # typography
    "B": "profiles/blog-ca-nhan.md",
    "K": "profiles/ky-thuat-doanh-nghiep.md",
}

errors: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


def read(relative: str) -> str:
    path = ROOT / relative
    if not path.exists():
        fail(f"Thiếu file bắt buộc: {relative}")
        return ""
    return path.read_text(encoding="utf-8")


def pattern_numbers(text: str, prefix: str) -> list[int]:
    return [int(n) for n in re.findall(rf"(?m)^### {prefix}(\d+)\.", text)]


skill = read("SKILL.md")
readme = read("README.md")

plugin_path = ROOT / ".claude-plugin" / "plugin.json"
plugin = json.loads(plugin_path.read_text(encoding="utf-8")) if plugin_path.exists() else {}
if not plugin:
    fail("Thiếu .claude-plugin/plugin.json")

# --- Frontmatter ---------------------------------------------------------

skill_version = ""
frontmatter_match = re.match(r"\A---\n(.*?)\n---\n", skill, re.DOTALL)
if not frontmatter_match:
    fail("SKILL.md phải mở đầu bằng YAML frontmatter")
else:
    frontmatter = frontmatter_match.group(1)

    # Một số nền tảng Agent Skills không hỗ trợ các khoá này ở cấp cao nhất.
    for key in ("compatibility:", "allowed-tools:", "version:"):
        if re.search(rf"(?m)^{re.escape(key)}", frontmatter):
            fail(f"Khoá frontmatter không portable ở cấp cao nhất: {key[:-1]}")

    version_match = re.search(r'(?m)^\s+version:\s*["\']([^"\']+)["\']\s*$', frontmatter)
    if not version_match:
        fail("SKILL.md thiếu metadata.version")
    else:
        skill_version = version_match.group(1)

# --- Đồng bộ version -----------------------------------------------------

readme_version_match = re.search(r"(?m)^- \*\*([0-9]+\.[0-9]+\.[0-9]+)\*\*", readme)
if not readme_version_match:
    fail("README.md thiếu mục Lịch sử phiên bản")

versions = {
    "SKILL.md": skill_version,
    "README.md": readme_version_match.group(1) if readme_version_match else "",
    "plugin.json": str(plugin.get("version", "")),
}
if len(set(versions.values())) != 1:
    fail(f"Version lệch nhau: {versions}")

# --- Đánh số pattern liên tục -------------------------------------------

declared: set[str] = set()
for prefix, owner in PATTERN_OWNERS.items():
    text = read(owner)
    numbers = pattern_numbers(text, prefix)
    if not numbers:
        fail(f"Không tìm thấy pattern nào có tiền tố {prefix} trong {owner}")
        continue
    if numbers != list(range(1, len(numbers) + 1)):
        fail(f"Pattern {prefix} trong {owner} phải đánh số liên tục từ 1, đang là {numbers}")
    declared.update(f"{prefix}{n}" for n in numbers)

# --- README phải liệt kê đủ pattern -------------------------------------

documented = set(re.findall(r"(?m)^\| ([VTBK]\d+) \|", readme))
missing = declared - documented
extra = documented - declared
if missing:
    fail(f"README thiếu pattern trong bảng: {sorted(missing)}")
if extra:
    fail(f"README liệt kê pattern không tồn tại: {sorted(extra)}")

# --- Ngân sách dòng ------------------------------------------------------

for relative, budget in LINE_BUDGETS.items():
    text = read(relative)
    if not text:
        continue
    count = len(text.splitlines())
    if count > budget:
        fail(f"{relative} dài {count} dòng, vượt ngân sách {budget}")

# --- Mọi file được SKILL.md trỏ tới đều phải tồn tại ---------------------

for target in sorted(set(re.findall(r"`((?:profiles|references|scripts)/[\w.-]+)`", skill))):
    if not (ROOT / target).exists():
        fail(f"SKILL.md trỏ tới file không tồn tại: {target}")

# --- Kết quả -------------------------------------------------------------

if errors:
    for message in errors:
        print(f"LỖI: {message}", file=sys.stderr)
    raise SystemExit(1)

print(f"Gói vi-humanizer v{skill_version} hợp lệ, gồm {len(declared)} pattern")
