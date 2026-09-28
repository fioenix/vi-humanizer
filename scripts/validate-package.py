#!/usr/bin/env python3
"""Kiểm tra tính toàn vẹn của gói vi-humanizer, không phụ thuộc thư viện ngoài."""

from __future__ import annotations

import json
import re
import stat
import sys
import zipfile
from pathlib import Path, PurePosixPath


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
PATTERN_FIELDS = ["Dấu hiệu", "Vì sao", "Sửa", "Không flag"]

STYLE_CARDS = [
    "ke-trai-nghiem",
    "phoi-hop-cong-viec",
    "chuyen-mon-cong-khai",
    "marketing-thuyet-phuc",
    "huong-dan-ky-thuat",
    "van-hanh-doanh-nghiep",
    "hoc-thuat-phan-tich",
]
STYLE_REGISTRY = "references/bo-giai-phong-cach.md"
STYLE_CARD_FIELDS = [
    "Dùng khi",
    "Thanh ngữ vực",
    "Xưng hô",
    "Nhịp",
    "Thuật ngữ",
    "Cách kết",
    "Không tự thêm",
    "Ca kiểm thử",
]
STYLE_PROFILE_CARDS = {
    "profiles/blog-ca-nhan.md": STYLE_CARDS[:4],
    "profiles/ky-thuat-doanh-nghiep.md": STYLE_CARDS[4:],
}
PACKAGE_PAYLOAD = {"SKILL.md", "profiles", "references", "calibration"}

errors: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


def validate_payload_tree(root: Path) -> None:
    """Chỉ cho phép thư mục và file thường nằm bên trong payload root."""

    try:
        resolved_root = root.resolve(strict=True)
    except OSError as error:
        fail(f"Không đọc được payload root {root}: {error}")
        return

    def validate_entry(path: Path, expected_kind: str | None = None) -> None:
        relative = path.relative_to(root)
        try:
            mode = path.lstat().st_mode
        except OSError as error:
            fail(f"Không đọc được entry đóng gói {relative}: {error}")
            return

        if stat.S_ISLNK(mode):
            fail(f"Payload không được chứa liên kết tượng trưng: {relative}")
            return
        if expected_kind == "file" and not stat.S_ISREG(mode):
            fail(f"Payload root phải là file thường: {relative}")
            return
        if expected_kind == "directory" and not stat.S_ISDIR(mode):
            fail(f"Payload root phải là thư mục: {relative}")
            return
        if not stat.S_ISDIR(mode) and not stat.S_ISREG(mode):
            fail(f"Payload chỉ được chứa thư mục và file thường: {relative}")
            return

        try:
            path.resolve(strict=True).relative_to(resolved_root)
        except (OSError, ValueError):
            fail(f"Entry đóng gói nằm ngoài payload root: {relative}")
            return

        if stat.S_ISDIR(mode):
            try:
                children = sorted(path.iterdir(), key=lambda child: child.name)
            except OSError as error:
                fail(f"Không đọc được thư mục đóng gói {relative}: {error}")
                return
            for child in children:
                validate_entry(child)

    for relative in sorted(PACKAGE_PAYLOAD):
        path = root / relative
        if not path.exists() and not path.is_symlink():
            fail(f"Thiếu payload bắt buộc: {relative}")
            continue
        expected_kind = "file" if relative == "SKILL.md" else "directory"
        validate_entry(path, expected_kind)


def payload_inventory(root: Path) -> dict[str, Path | None]:
    inventory: dict[str, Path | None] = {"vi-humanizer/": None}
    for relative in sorted(PACKAGE_PAYLOAD):
        path = root / relative
        entries = [path]
        if path.is_dir():
            entries.extend(sorted(path.rglob("*")))
        for entry in entries:
            if entry.name == ".DS_Store":
                continue
            archive_name = f"vi-humanizer/{entry.relative_to(root).as_posix()}"
            if entry.is_dir():
                archive_name += "/"
            inventory[archive_name] = entry
    return inventory


def validate_archive(archive_path: Path, payload_root: Path) -> None:
    validate_payload_tree(payload_root)
    if errors:
        return

    expected = payload_inventory(payload_root)
    try:
        with zipfile.ZipFile(archive_path) as archive:
            entries = archive.infolist()
            names = [entry.filename for entry in entries]
            if len(names) != len(set(names)):
                fail("Archive chứa entry trùng tên")

            actual_names = set(names)
            expected_names = set(expected)
            missing = sorted(expected_names - actual_names)
            extra = sorted(actual_names - expected_names)
            if missing:
                fail(f"Archive thiếu entry: {missing}")
            if extra:
                fail(f"Archive chứa entry ngoài public payload: {extra}")

            for entry in entries:
                archive_name = PurePosixPath(entry.filename)
                if archive_name.is_absolute() or ".." in archive_name.parts:
                    fail(f"Archive chứa đường dẫn không an toàn: {entry.filename}")
                    continue

                mode = (entry.external_attr >> 16) & 0xFFFF
                file_type = stat.S_IFMT(mode)
                allowed_type = stat.S_IFDIR if entry.is_dir() else stat.S_IFREG
                if file_type not in (0, allowed_type):
                    fail(f"Archive chứa entry không phải file hoặc thư mục thường: {entry.filename}")
                    continue

                source = expected.get(entry.filename)
                if source is None or entry.is_dir():
                    continue
                try:
                    archived_bytes = archive.read(entry)
                    source_bytes = source.read_bytes()
                except (OSError, RuntimeError, zipfile.BadZipFile) as error:
                    fail(f"Không đọc được entry archive {entry.filename}: {error}")
                    continue
                if archived_bytes != source_bytes:
                    fail(f"Nội dung archive lệch staged payload: {entry.filename}")
    except (OSError, zipfile.BadZipFile) as error:
        fail(f"Không đọc được archive {archive_path}: {error}")


def exit_on_errors() -> None:
    if not errors:
        return
    for message in errors:
        print(f"LỖI: {message}", file=sys.stderr)
    raise SystemExit(1)


def read(relative: str) -> str:
    path = ROOT / relative
    if not path.exists():
        fail(f"Thiếu file bắt buộc: {relative}")
        return ""
    return path.read_text(encoding="utf-8")


def pattern_numbers(text: str, prefix: str) -> list[int]:
    return [int(n) for n in re.findall(rf"(?m)^### {prefix}(\d+)\.", text)]


def pattern_block(text: str, pattern_id: str) -> str:
    match = re.search(
        rf"(?ms)^### {re.escape(pattern_id)}\..*?(?=^### [VTBK]\d+\.|\Z)",
        text,
    )
    return match.group(0) if match else ""


if sys.argv[1:]:
    arguments = sys.argv[1:]
    if len(arguments) == 2 and arguments[0] == "--payload-root":
        payload_root = Path(arguments[1])
        validate_payload_tree(payload_root)
        exit_on_errors()
        print(f"Payload đóng gói hợp lệ: {payload_root}")
        raise SystemExit(0)
    if (
        len(arguments) == 4
        and arguments[0] == "--archive"
        and arguments[2] == "--payload-root"
    ):
        archive_path = Path(arguments[1])
        payload_root = Path(arguments[3])
        validate_archive(archive_path, payload_root)
        exit_on_errors()
        print(f"Archive đóng gói hợp lệ: {archive_path}")
        raise SystemExit(0)
    else:
        print(
            "Dùng: validate-package.py [--payload-root <thư-mục> | "
            "--archive <file> --payload-root <thư-mục>]",
            file=sys.stderr,
        )
        raise SystemExit(2)

validate_payload_tree(ROOT)
exit_on_errors()

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
    for number in numbers:
        pattern_id = f"{prefix}{number}"
        declared.add(pattern_id)
        block = pattern_block(text, pattern_id)
        missing_fields = [field for field in PATTERN_FIELDS if f"**{field}:**" not in block]
        if missing_fields:
            fail(f"Pattern {pattern_id} trong {owner} thiếu mục: {missing_fields}")

# --- README phải liệt kê đủ pattern -------------------------------------

documented = set(re.findall(r"(?m)^\| ([VTBK]\d+) \|", readme))
missing = declared - documented
extra = documented - declared
if missing:
    fail(f"README thiếu pattern trong bảng: {sorted(missing)}")
if extra:
    fail(f"README liệt kê pattern không tồn tại: {sorted(extra)}")

# --- Registry phong cách -------------------------------------------------

style_registry = read(STYLE_REGISTRY)
style_cards = re.findall(r"(?m)^### `([a-z0-9]+(?:-[a-z0-9]+)*)` — ", style_registry)
if style_cards != STYLE_CARDS:
    fail(f"Style card phải đúng thứ tự canonical {STYLE_CARDS}, đang là {style_cards}")
for index, card_id in enumerate(style_cards):
    start = style_registry.index(f"### `{card_id}` — ")
    if index + 1 < len(style_cards):
        end = style_registry.index(f"### `{style_cards[index + 1]}` — ")
        block = style_registry[start:end]
    else:
        block = style_registry[start:]
    missing_fields = [field for field in STYLE_CARD_FIELDS if f"- **{field}:**" not in block]
    if missing_fields:
        fail(f"Style card `{card_id}` thiếu field: {missing_fields}")
if f"`{STYLE_REGISTRY}`" not in skill:
    fail(f"SKILL.md chưa trỏ tới `{STYLE_REGISTRY}`")
if f"`{STYLE_REGISTRY}`" not in readme:
    fail(f"README.md chưa trỏ tới `{STYLE_REGISTRY}`")
for card_id in STYLE_CARDS:
    if f"`{card_id}`" not in readme:
        fail(f"README.md thiếu style card `{card_id}`")

# --- Pattern cross-reference -------------------------------------------

blog_profile = read("profiles/blog-ca-nhan.md")
technical_profile = read("profiles/ky-thuat-doanh-nghiep.md")
if "V23" not in pattern_block(blog_profile, "B5"):
    fail("B5 phải phân vai với V23")
if "K7" not in pattern_block(blog_profile, "B8"):
    fail("B8 phải phân vai với K7")
if "B8" not in pattern_block(technical_profile, "K7"):
    fail("K7 phải phân vai với B8")
for profile_path, card_ids in STYLE_PROFILE_CARDS.items():
    profile = read(profile_path)
    if f"`{STYLE_REGISTRY}`" not in profile:
        fail(f"{profile_path} chưa trỏ tới `{STYLE_REGISTRY}`")
    for card_id in card_ids:
        if f"`{card_id}`" not in profile:
            fail(f"{profile_path} thiếu style card tương thích `{card_id}`")

# --- Package payload ----------------------------------------------------

package_script = read("scripts/package-skill.sh")
copied_payload: set[str] = set()
for line in package_script.splitlines():
    if not re.match(r"^cp(?:\s|$)", line):
        continue
    copied_payload.update(re.findall(r'\$ROOT/([A-Za-z0-9._/-]+)', line))
if copied_payload != PACKAGE_PAYLOAD:
    fail(
        "package-skill.sh phải chỉ chép public payload "
        f"{sorted(PACKAGE_PAYLOAD)}, đang là {sorted(copied_payload)}"
    )

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

exit_on_errors()

print(f"Gói vi-humanizer v{skill_version} hợp lệ, gồm {len(declared)} pattern")
