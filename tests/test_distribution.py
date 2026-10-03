from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DistributionTest(unittest.TestCase):
    def fixture(self, destination: Path) -> Path:
        repo = destination / "repo"
        repo.mkdir()
        for relative in (
            "SKILL.md", "LICENSE", "README.md", "profiles", "references", "calibration",
            "agents", "assets", "scripts", ".claude-plugin", ".codex-plugin",
            ".agents/plugins", ".plugin-skills", ".gitignore",
        ):
            source = ROOT / relative
            if not source.exists():
                continue
            target = repo / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            if source.is_dir():
                shutil.copytree(source, target, symlinks=True)
            else:
                shutil.copy2(source, target)
        return repo

    def package(self, repo: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "scripts/package-plugin.py"], cwd=repo,
            capture_output=True, text=True, check=False,
        )

    def test_metadata_rejects_missing_or_unsafe_support_link(self) -> None:
        for value in (None, "", "http://example.com/help", "https://user:password@example.com/help"):
            with self.subTest(value=value), tempfile.TemporaryDirectory() as temporary:
                repo = self.fixture(Path(temporary))
                path = repo / ".codex-plugin/plugin.json"
                data = json.loads(path.read_text())
                data["interface"]["supportURL"] = value
                path.write_text(json.dumps(data))
                result = self.package(repo)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse((repo / "dist/vietnamizer-plugin.zip").exists())

    def test_metadata_rejects_listing_text_over_submission_limits(self) -> None:
        for field, value in (("shortDescription", "a" * 31), ("longDescription", "a" * 4001),
                             ("defaultPrompt", ["a" * 129]), ("defaultPrompt", ["Same", "Same"])):
            with self.subTest(field=field, value=str(value)[:40]), tempfile.TemporaryDirectory() as temporary:
                repo = self.fixture(Path(temporary))
                path = repo / ".codex-plugin/plugin.json"
                data = json.loads(path.read_text())
                data["interface"][field] = value
                path.write_text(json.dumps(data))
                self.assertNotEqual(self.package(repo).returncode, 0)

    def test_metadata_rejects_invalid_translation_before_packaging(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = self.fixture(Path(temporary))
            path = repo / ".codex-plugin/plugin.json"
            data = json.loads(path.read_text())
            data["extensions"] = {"com.openai": {"publication": {
                "translations": {"vi-VN": {"subtitle": "a" * 31}}
            }}}
            path.write_text(json.dumps(data))
            self.assertNotEqual(self.package(repo).returncode, 0)

    def test_skill_archive_contains_resolvable_ui_assets(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = self.fixture(Path(temporary))
            result = subprocess.run(
                ["bash", "scripts/package-skill.sh"], cwd=repo,
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            with zipfile.ZipFile(repo / "dist/vietnamizer.skill") as archive:
                self.assertIn("vietnamizer/agents/openai.yaml", archive.namelist())
                for asset in ("icon.svg", "icon-dark.svg"):
                    path = f"assets/{asset}"
                    self.assertEqual(archive.read(f"vietnamizer/{path}"), (repo / path).read_bytes())

    def test_source_manifests_resolve_a_plugin_skill_adapter(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = self.fixture(Path(temporary))
            for platform in ("codex", "claude"):
                manifest = json.loads((repo / f".{platform}-plugin/plugin.json").read_text())
                root = repo / manifest["skills"]
                self.assertEqual([path.relative_to(root).as_posix() for path in root.rglob("SKILL.md")], ["vietnamizer/SKILL.md"])

    def test_plugin_archive_contains_both_wordmark_variants(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = self.fixture(Path(temporary))
            result = self.package(repo)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            with zipfile.ZipFile(repo / "dist/vietnamizer-plugin.zip") as archive:
                for asset in ("wordmark.svg", "wordmark-dark.svg"):
                    self.assertIn(f"assets/{asset}", archive.namelist())
                    self.assertEqual(archive.read(f"assets/{asset}"), (repo / "assets" / asset).read_bytes())
                    self.assertEqual(archive.read(f"skills/vietnamizer/assets/{asset}"), (repo / "assets" / asset).read_bytes())

    def test_packaged_brand_colors_meet_marketplace_contrast(self) -> None:
        def luminance(color: str) -> float:
            channels = [int(color[index:index + 2], 16) / 255 for index in (1, 3, 5)]
            linear = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4 for value in channels]
            return sum(value * weight for value, weight in zip(linear, (0.2126, 0.7152, 0.0722)))

        with tempfile.TemporaryDirectory() as temporary:
            repo = self.fixture(Path(temporary))
            result = self.package(repo)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            with zipfile.ZipFile(repo / "dist/vietnamizer-plugin.zip") as archive:
                interface = json.loads(archive.read(".codex-plugin/plugin.json"))["interface"]
            for field, background in (("brandColor", "#FFFFFF"), ("brandColorDark", "#212121")):
                with self.subTest(field=field):
                    foreground, base = luminance(interface[field]), luminance(background)
                    contrast = (max(foreground, base) + 0.05) / (min(foreground, base) + 0.05)
                    self.assertGreaterEqual(contrast, 2.0)

    def test_plugin_archive_loads_one_canonical_skill_without_maintainer_tooling(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = self.fixture(Path(temporary))
            result = self.package(repo)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            with zipfile.ZipFile(repo / "dist/vietnamizer-plugin.zip") as archive:
                names = archive.namelist()
                self.assertEqual([name for name in names if name.endswith("SKILL.md")], ["skills/vietnamizer/SKILL.md"])
                self.assertEqual(archive.read("skills/vietnamizer/SKILL.md"), (repo / "SKILL.md").read_bytes())
                for platform in ("codex", "claude"):
                    manifest = json.loads(archive.read(f".{platform}-plugin/plugin.json"))
                    self.assertEqual(manifest["skills"], "./skills/")
                    self.assertEqual(manifest["name"], "vietnamizer")
                self.assertEqual(archive.read("LICENSE"), (repo / "LICENSE").read_bytes())
                self.assertFalse(any(name.startswith((".agents/", ".specify/", "specs/", "tests/", "output/")) for name in names))
                self.assertFalse(any("/advisor/" in name for name in names))

    def test_plugin_package_rejects_missing_asset_before_replacing_good_archive(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = self.fixture(Path(temporary))
            good = self.package(repo)
            self.assertEqual(good.returncode, 0, good.stdout + good.stderr)
            archive = repo / "dist/vietnamizer-plugin.zip"
            original = archive.read_bytes()
            (repo / "assets/icon.svg").unlink()
            result = self.package(repo)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(archive.read_bytes(), original)

    def test_plugin_package_rejects_asset_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = self.fixture(Path(temporary))
            good = self.package(repo)
            self.assertEqual(good.returncode, 0, good.stdout + good.stderr)
            icon = repo / "assets/icon.svg"
            content = icon.read_bytes()
            canary = Path(temporary) / "external.svg"
            canary.write_bytes(content)
            icon.unlink()
            icon.symlink_to(canary)
            result = self.package(repo)
            self.assertNotEqual(result.returncode, 0)

    def test_metadata_rejects_empty_app_declaration_for_skills_only_plugin(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = self.fixture(Path(temporary))
            manifest = repo / ".codex-plugin/plugin.json"
            data = json.loads(manifest.read_text())
            data["apps"] = []
            manifest.write_text(json.dumps(data))
            result = subprocess.run(
                [sys.executable, "scripts/package-plugin.py", "--check"], cwd=repo,
                capture_output=True, text=True,
            )
            self.assertNotEqual(result.returncode, 0)

    def test_metadata_rejects_stale_plugin_version(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = self.fixture(Path(temporary))
            manifest = repo / ".codex-plugin/plugin.json"
            data = json.loads(manifest.read_text())
            data["version"] = "0.0.0"
            manifest.write_text(json.dumps(data))
            result = subprocess.run(
                [sys.executable, "scripts/package-plugin.py", "--check"], cwd=repo,
                capture_output=True, text=True,
            )
            self.assertNotEqual(result.returncode, 0)

    def test_metadata_rejects_active_svg_content(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = self.fixture(Path(temporary))
            icon = repo / "assets/icon.svg"
            icon.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128"><script>alert(1)</script></svg>')
            result = subprocess.run(
                [sys.executable, "scripts/package-plugin.py", "--check"], cwd=repo,
                capture_output=True, text=True,
            )
            self.assertNotEqual(result.returncode, 0)

    def test_all_packagers_reject_active_wordmark_before_replacing_good_archives(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = self.fixture(Path(temporary))
            good = self.package(repo)
            self.assertEqual(good.returncode, 0, good.stdout + good.stderr)
            originals = {path.name: path.read_bytes() for path in (repo / "dist").glob("*") if path.is_file()}
            (repo / "assets/wordmark.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 144"><script>alert(1)</script></svg>')
            for command in (
                [sys.executable, "scripts/package-plugin.py", "--check"],
                ["bash", "scripts/package-skill.sh"],
                [sys.executable, "scripts/package-plugin.py"],
            ):
                result = subprocess.run(command, cwd=repo, capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0, command)
            for name, content in originals.items():
                self.assertEqual((repo / "dist" / name).read_bytes(), content)

    def test_metadata_rejects_icon_path_outside_shipped_assets(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = self.fixture(Path(temporary))
            shutil.copy2(repo / "assets/icon.svg", repo / "private-icon.svg")
            manifest = repo / ".codex-plugin/plugin.json"
            data = json.loads(manifest.read_text())
            data["interface"]["logo"] = "./private-icon.svg"
            manifest.write_text(json.dumps(data))
            result = subprocess.run([sys.executable, "scripts/package-plugin.py", "--check"], cwd=repo, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)

    def test_metadata_rejects_catalog_identifier_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = self.fixture(Path(temporary))
            catalog = repo / ".agents/plugins/marketplace.json"
            data = json.loads(catalog.read_text())
            data["name"] = "wrong-marketplace"
            catalog.write_text(json.dumps(data))
            result = subprocess.run([sys.executable, "scripts/package-plugin.py", "--check"], cwd=repo, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)

    def test_codex_catalog_is_tracked_candidate_but_generated_skills_stay_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = self.fixture(Path(temporary))
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            for path, ignored in ((".agents/plugins/marketplace.json", False), (".agents/skills/local/SKILL.md", True)):
                result = subprocess.run(
                    ["git", "-c", "core.excludesFile=/dev/null", "check-ignore", "--no-index", "-q", path], cwd=repo,
                )
                self.assertEqual(result.returncode == 0, ignored, path)


if __name__ == "__main__":
    unittest.main()
