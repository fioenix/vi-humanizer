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
    "profiles/blog-ca-nhan/rules.md": 320,
    "profiles/ky-thuat-doanh-nghiep/rules.md": 220,
}

# Tiền tố pattern và file sở hữu. Mỗi tiền tố phải đánh số liên tục từ 1.
PATTERN_OWNERS = {
    "V": "SKILL.md",   # lỗi dùng từ và cấu trúc câu
    "T": "SKILL.md",   # typography
    "B": "profiles/blog-ca-nhan/rules.md",
    "K": "profiles/ky-thuat-doanh-nghiep/rules.md",
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
    "profiles/blog-ca-nhan/rules.md": {
        card_id: f"profiles/blog-ca-nhan/styles/{card_id}.md"
        for card_id in STYLE_CARDS[:4]
    },
    "profiles/ky-thuat-doanh-nghiep/rules.md": {
        card_id: f"profiles/ky-thuat-doanh-nghiep/styles/{card_id}.md"
        for card_id in STYLE_CARDS[4:]
    },
}
EXPECTED_PROFILE_FILES = {
    PurePosixPath(profile_path).relative_to("profiles").as_posix()
    for profile_path in STYLE_PROFILE_CARDS
} | {
    PurePosixPath(card_path).relative_to("profiles").as_posix()
    for cards in STYLE_PROFILE_CARDS.values()
    for card_path in cards.values()
}
EXPECTED_PROFILE_DIRECTORIES = {
    PurePosixPath(relative).parent.as_posix()
    for relative in EXPECTED_PROFILE_FILES
} | {
    PurePosixPath(relative).parent.parent.as_posix()
    for relative in EXPECTED_PROFILE_FILES
    if PurePosixPath(relative).parent.name == "styles"
}
PACKAGE_PAYLOAD = {"SKILL.md", "profiles", "references", "calibration", "advisor"}
ADVISOR_FILES = {
    "advisor/__init__.py",
    "advisor/__main__.py",
    "advisor/cli.py",
    "advisor/client.py",
    "advisor/models.py",
    "advisor/questions.py",
}
PACKAGE_COPY_SOURCES = (PACKAGE_PAYLOAD - {"advisor"}) | ADVISOR_FILES
MARKETPLACE_SCHEMA = "https://json.schemastore.org/claude-code-marketplace.json"

errors: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


def ignored_generated_entry(path: Path) -> bool:
    return path.name == ".DS_Store" or "__pycache__" in path.parts or path.suffix == ".pyc"


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

    profiles_root = root / "profiles"
    if not profiles_root.is_dir() or profiles_root.is_symlink():
        return
    profile_entries = [
        entry
        for entry in profiles_root.rglob("*")
        if entry.name != ".DS_Store"
    ]
    actual_files = {
        entry.relative_to(profiles_root).as_posix()
        for entry in profile_entries
        if not entry.is_dir()
    }
    actual_directories = {
        entry.relative_to(profiles_root).as_posix()
        for entry in profile_entries
        if entry.is_dir()
    }
    missing_files = sorted(EXPECTED_PROFILE_FILES - actual_files)
    extra_files = sorted(actual_files - EXPECTED_PROFILE_FILES)
    missing_directories = sorted(EXPECTED_PROFILE_DIRECTORIES - actual_directories)
    extra_directories = sorted(actual_directories - EXPECTED_PROFILE_DIRECTORIES)
    if missing_files:
        fail(f"Profiles thiếu file canonical: {missing_files}")
    if extra_files:
        fail(f"Profiles chứa file ngoài inventory canonical: {extra_files}")
    if missing_directories:
        fail(f"Profiles thiếu thư mục canonical: {missing_directories}")
    if extra_directories:
        fail(f"Profiles chứa thư mục ngoài inventory canonical: {extra_directories}")

    advisor_root = root / "advisor"
    if not advisor_root.is_dir() or advisor_root.is_symlink():
        return
    actual_advisor_files = {
        entry.relative_to(root).as_posix()
        for entry in advisor_root.rglob("*")
        if entry.is_file() and not entry.is_symlink() and not ignored_generated_entry(entry)
    }
    actual_advisor_directories = {
        entry.relative_to(root).as_posix()
        for entry in advisor_root.rglob("*")
        if entry.is_dir() and not ignored_generated_entry(entry)
    }
    if actual_advisor_files != ADVISOR_FILES:
        fail(
            "Advisor runtime phải khớp exact inventory: "
            f"mong đợi {sorted(ADVISOR_FILES)}, đang là {sorted(actual_advisor_files)}"
        )
    if actual_advisor_directories:
        fail(f"Advisor runtime chứa thư mục ngoài inventory: {sorted(actual_advisor_directories)}")


def payload_inventory(root: Path, archive_root: str | None = "vi-humanizer") -> dict[str, Path | None]:
    inventory: dict[str, Path | None] = {}
    if archive_root:
        inventory[f"{archive_root}/"] = None
    for relative in sorted(PACKAGE_PAYLOAD):
        path = root / relative
        entries = [path]
        if path.is_dir():
            entries.extend(sorted(path.rglob("*")))
        for entry in entries:
            if ignored_generated_entry(entry):
                continue
            archive_name = entry.relative_to(root).as_posix()
            if archive_root:
                archive_name = f"{archive_root}/{archive_name}"
            if entry.is_dir():
                archive_name += "/"
            inventory[archive_name] = entry
    return inventory


def validate_archive(
    archive_path: Path,
    payload_root: Path,
    archive_root: str | None = "vi-humanizer",
) -> None:
    validate_payload_tree(payload_root)
    if errors:
        return

    expected = payload_inventory(payload_root, archive_root)
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
        len(arguments) in (4, 5)
        and arguments[0] == "--archive"
        and arguments[2] == "--payload-root"
        and (len(arguments) == 4 or arguments[4] == "--root-layout")
    ):
        archive_path = Path(arguments[1])
        payload_root = Path(arguments[3])
        archive_root = None if len(arguments) == 5 else "vi-humanizer"
        validate_archive(archive_path, payload_root, archive_root)
        exit_on_errors()
        print(f"Archive đóng gói hợp lệ: {archive_path}")
        raise SystemExit(0)
    else:
        print(
            "Dùng: validate-package.py [--payload-root <thư-mục> | "
            "--archive <file> --payload-root <thư-mục> [--root-layout]]",
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

marketplace_path = ROOT / ".claude-plugin" / "marketplace.json"
marketplace = (
    json.loads(marketplace_path.read_text(encoding="utf-8"))
    if marketplace_path.exists()
    else {}
)
if not marketplace:
    fail("Thiếu .claude-plugin/marketplace.json")
elif marketplace.get("$schema") != MARKETPLACE_SCHEMA:
    fail(f"marketplace.json phải dùng schema chính thức: {MARKETPLACE_SCHEMA}")

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

blog_profile = read("profiles/blog-ca-nhan/rules.md")
technical_profile = read("profiles/ky-thuat-doanh-nghiep/rules.md")
style_registry = read(STYLE_REGISTRY)
registry_rows = re.findall(
    r"(?m)^\| `([a-z0-9]+(?:-[a-z0-9]+)*)` \| `([a-z0-9]+(?:-[a-z0-9]+)*)` \| `(profiles/.+/styles/.+\.md)` \|$",
    style_registry,
)
expected_registry_rows = [
    (card_id, PurePosixPath(profile_path).parent.name, card_path)
    for profile_path, cards in STYLE_PROFILE_CARDS.items()
    for card_id, card_path in cards.items()
]
if registry_rows != expected_registry_rows:
    fail(
        "Style registry phải khớp exact card/profile/path canonical: "
        f"mong đợi {expected_registry_rows}, đang là {registry_rows}"
    )
for card_id, _profile_id, card_path in expected_registry_rows:
    card = read(card_path)
    if not re.search(rf"(?m)^# `{re.escape(card_id)}`: ", card):
        fail(f"Style card `{card_id}` thiếu heading canonical trong {card_path}")
    missing_fields = [field for field in STYLE_CARD_FIELDS if f"- **{field}:**" not in card]
    if missing_fields:
        fail(f"Style card `{card_id}` thiếu field: {missing_fields}")
    if f"`{card_path}`" not in skill:
        fail(f"SKILL.md chưa trỏ tới style card `{card_path}`")
if f"`{STYLE_REGISTRY}`" not in skill:
    fail(f"SKILL.md chưa trỏ tới `{STYLE_REGISTRY}`")
if f"`{STYLE_REGISTRY}`" not in readme:
    fail(f"README.md chưa trỏ tới `{STYLE_REGISTRY}`")
for card_id in STYLE_CARDS:
    if f"`{card_id}`" not in readme:
        fail(f"README.md thiếu style card `{card_id}`")

k_count = len(pattern_numbers(technical_profile, "K"))
technical_registry_rows = [
    line
    for line in style_registry.splitlines()
    if line.startswith("| `ky-thuat-doanh-nghiep` |")
]
if len(technical_registry_rows) != 1:
    fail("Style registry phải có đúng một dòng cho base profile ky-thuat-doanh-nghiep")
elif f"Pattern K1–K{k_count}" not in technical_registry_rows[0]:
    fail(
        "Style registry phải đồng bộ dải pattern kỹ thuật: "
        f"mong đợi Pattern K1–K{k_count}"
    )

# --- Pattern cross-reference -------------------------------------------

if "V23" not in pattern_block(blog_profile, "B5"):
    fail("B5 phải phân vai với V23")
if "K7" not in pattern_block(blog_profile, "B8"):
    fail("B8 phải phân vai với K7")
if "B8" not in pattern_block(technical_profile, "K7"):
    fail("K7 phải phân vai với B8")
for profile_path in STYLE_PROFILE_CARDS:
    profile = read(profile_path)
    if f"`{STYLE_REGISTRY}`" not in profile:
        fail(f"{profile_path} chưa trỏ tới `{STYLE_REGISTRY}`")

# --- Package payload ----------------------------------------------------

package_script = read("scripts/package-skill.sh")
copied_payload: set[str] = set()
for line in package_script.splitlines():
    if not re.match(r"^cp(?:\s|$)", line):
        continue
    copied_payload.update(re.findall(r'\$ROOT/([A-Za-z0-9._/-]+)', line))
if copied_payload != PACKAGE_COPY_SOURCES:
    fail(
        "package-skill.sh phải chỉ chép public payload "
        f"{sorted(PACKAGE_COPY_SOURCES)}, đang là {sorted(copied_payload)}"
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

for target in sorted(set(re.findall(r"`((?:profiles|references|scripts)/[\w./-]+)`", skill))):
    if not (ROOT / target).exists():
        fail(f"SKILL.md trỏ tới file không tồn tại: {target}")

# --- Kết quả -------------------------------------------------------------

exit_on_errors()

print(f"Gói vi-humanizer v{skill_version} hợp lệ, gồm {len(declared)} pattern")
