#!/usr/bin/env python3
"""Validate listing metadata and build a plugin from the validated skill archive."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path, PurePosixPath

from distribution_assets import ASSETS, validate_svg


ROOT = Path(__file__).resolve().parents[1]


def local_file(relative: str) -> Path:
    path = PurePosixPath(relative)
    if not relative.startswith("./") or path.is_absolute() or ".." in path.parts:
        raise ValueError("Asset path must be ./-relative and contained in the package")
    candidate = ROOT / path
    if any((ROOT / Path(*path.parts[:index])).is_symlink() for index in range(1, len(path.parts) + 1)):
        raise ValueError("Asset must not be a symlink")
    candidate.resolve(strict=True).relative_to(ROOT.resolve())
    if not candidate.is_file() or candidate.stat().st_size > 5 * 1024 * 1024:
        raise ValueError("Asset must be a regular file no larger than 5 MiB")
    return candidate


def icon_file(relative: str) -> Path:
    if relative not in {f"./assets/{name}" for name, square in ASSETS.items() if square}:
        raise ValueError("Listing icon must resolve to a shipped square asset")
    return local_file(relative)


def validate_metadata() -> dict[str, dict]:
    version = re.search(r'^  version: "([^"]+)"$', (ROOT / "SKILL.md").read_text(), re.MULTILINE)
    if not version:
        raise ValueError("Missing canonical skill version")
    manifests = {}
    for platform in ("codex", "claude"):
        relative = f".{platform}-plugin/plugin.json"
        manifest = json.loads(local_file(f"./{relative}").read_text())
        if manifest.get("name") != "vietnamizer" or manifest.get("version") != version[1]:
            raise ValueError("Plugin identity/version differs from the canonical skill")
        if manifest.get("skills") != "./.plugin-skills/":
            raise ValueError("Source plugins must reference the canonical workflow adapter")
        if any(field in manifest for field in ("apps", "mcpServers", "hooks")):
            raise ValueError("Skills-only plugins do not declare apps, MCP servers or hooks")
        manifests[platform] = manifest
    local_file("./.plugin-skills/vietnamizer/SKILL.md")
    for name, square in ASSETS.items():
        validate_svg(local_file(f"./assets/{name}"), square=square)
    interface = manifests["codex"]["interface"]
    for field in ("composerIcon", "logo", "logoDark"):
        validate_svg(icon_file(interface[field]))
    validate_svg(icon_file(manifests["claude"]["icon"]))
    ui = (ROOT / "agents/openai.yaml").read_text()
    for field in ("icon_small", "icon_large"):
        match = re.search(rf'^  {field}: "([^"]+)"$', ui, re.MULTILINE)
        if not match:
            raise ValueError("Skill UI icon is missing")
        validate_svg(icon_file(match[1]))
    catalog = json.loads(local_file("./.agents/plugins/marketplace.json").read_text())
    entries = catalog.get("plugins", [])
    if catalog.get("name") != "vietnamizer" or len(entries) != 1 or entries[0].get("name") != "vietnamizer" or entries[0].get("source") != {"source": "local", "path": "./"}:
        raise ValueError("Codex catalog must resolve the source plugin at the repo root")
    claude = json.loads(local_file("./.claude-plugin/marketplace.json").read_text())
    if claude.get("name") != "vietnamizer" or len(claude.get("plugins", [])) != 1 or claude["plugins"][0].get("source") != "./" or claude["plugins"][0].get("name") != "vietnamizer":
        raise ValueError("Claude catalog must resolve the source plugin at the repo root")
    return manifests


def build(manifests: dict[str, dict]) -> None:
    subprocess.run(["bash", str(ROOT / "scripts/package-skill.sh")], check=True)
    files = {}
    with zipfile.ZipFile(ROOT / "dist/vietnamizer.skill") as skill:
        for entry in skill.infolist():
            if not entry.is_dir():
                relative = entry.filename.removeprefix("vietnamizer/")
                files[f"skills/vietnamizer/{relative}"] = skill.read(entry)
    files["LICENSE"] = (ROOT / "LICENSE").read_bytes()
    for name in sorted(ASSETS):
        files[f"assets/{name}"] = (ROOT / "assets" / name).read_bytes()
    for platform, manifest in manifests.items():
        packaged = {**manifest, "skills": "./skills/"}
        files[f".{platform}-plugin/plugin.json"] = (json.dumps(packaged, ensure_ascii=False, indent=2) + "\n").encode()
    dist = ROOT / "dist"
    with tempfile.TemporaryDirectory(prefix=".plugin-", dir=dist) as temporary:
        candidate = Path(temporary) / "vietnamizer-plugin.zip"
        with zipfile.ZipFile(candidate, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for name, content in sorted(files.items()):
                archive.writestr(name, content)
        with zipfile.ZipFile(candidate) as archive:
            if set(archive.namelist()) != set(files) or archive.testzip() is not None:
                raise ValueError("Plugin archive inventory/CRC validation failed")
            if any(archive.read(name) != content for name, content in files.items()):
                raise ValueError("Plugin archive byte parity failed")
        candidate.replace(dist / "vietnamizer-plugin.zip")
    print("Plugin archive validated: dist/vietnamizer-plugin.zip")


def main() -> int:
    if sys.argv[1:] not in ([], ["--check"]):
        print("Usage: package-plugin.py [--check]", file=sys.stderr)
        return 2
    try:
        manifests = validate_metadata()
        if not sys.argv[1:]:
            build(manifests)
    except (OSError, ValueError, KeyError, TypeError, ET.ParseError, zipfile.BadZipFile, subprocess.CalledProcessError):
        print("Distribution validation failed; check versions, catalogs and local asset paths.", file=sys.stderr)
        return 1
    print("Distribution metadata valid for Codex and Claude Code")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
