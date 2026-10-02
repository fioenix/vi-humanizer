from __future__ import annotations

import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_FIXTURE_PATHS = (
    "SKILL.md",
    "LICENSE",
    "README.md",
    ".claude-plugin",
    "advisor",
    "calibration",
    "profiles",
    "references",
    "scripts",
)


class PackageSecurityTest(unittest.TestCase):
    def copy_package_fixture(self, destination: Path) -> Path:
        repo = destination / "vi-humanizer"
        repo.mkdir()
        for relative in PACKAGE_FIXTURE_PATHS:
            source = ROOT / relative
            target = repo / relative
            if source.is_dir():
                shutil.copytree(source, target, symlinks=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
        return repo

    def run_packager(
        self,
        repo: Path,
        env: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["bash", "scripts/package-skill.sh"],
            cwd=repo,
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )

    def install_python_shim(self, directory: Path, body: str) -> Path:
        shim_directory = directory / "bin"
        shim_directory.mkdir()
        shim = shim_directory / "python3"
        shim.write_text("#!/usr/bin/env bash\nset -euo pipefail\n" + body, encoding="utf-8")
        shim.chmod(0o755)
        return shim_directory

    def run_archive_validator(
        self,
        repo: Path,
        archive: Path,
        payload_root: Path,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                "python3",
                "scripts/validate-package.py",
                "--archive",
                str(archive),
                "--payload-root",
                str(payload_root),
            ],
            cwd=repo,
            capture_output=True,
            text=True,
            check=False,
        )

    def run_payload_validator(
        self,
        repo: Path,
        payload_root: Path,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                "python3",
                "scripts/validate-package.py",
                "--payload-root",
                str(payload_root),
            ],
            cwd=repo,
            capture_output=True,
            text=True,
            check=False,
        )

    def run_package_validator(self, repo: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", "scripts/validate-package.py"],
            cwd=repo,
            capture_output=True,
            text=True,
            check=False,
        )

    def run_tell_scanner(self, repo: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["bash", "scripts/scan-tells.sh"],
            cwd=repo,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_rejects_payload_symlink_to_file_outside_repository(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary = Path(temporary_directory)
            repo = self.copy_package_fixture(temporary)
            canary = temporary / "release-host-secret.txt"
            canary.write_text("outside-canary-7f3a", encoding="utf-8")
            (repo / "profiles" / "security-probe.md").symlink_to(canary)

            result = self.run_packager(repo)

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            archive = repo / "dist" / "vi-humanizer.skill"
            if archive.exists():
                with zipfile.ZipFile(archive) as package:
                    archived_bytes = b"".join(
                        package.read(name)
                        for name in package.namelist()
                        if not name.endswith("/")
                    )
                self.assertNotIn(canary.read_bytes(), archived_bytes)

    def test_payload_roots_keep_their_declared_file_types(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo = self.copy_package_fixture(Path(temporary_directory))
            shutil.rmtree(repo / "profiles")
            (repo / "profiles").write_text("not a directory", encoding="utf-8")

            result = self.run_payload_validator(repo, repo)

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_rejects_unknown_marketplace_schema_url(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo = self.copy_package_fixture(Path(temporary_directory))
            manifest_path = repo / ".claude-plugin" / "marketplace.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["$schema"] = (
                "https://json.schemastore.org/claude-code-marketplace-manifest.json"
            )
            manifest_path.write_text(
                json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            result = self.run_package_validator(repo)

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_validator_rejects_stale_style_registry_pattern_range(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo = self.copy_package_fixture(Path(temporary_directory))
            registry_path = repo / "references" / "bo-giai-phong-cach.md"
            registry = registry_path.read_text(encoding="utf-8")
            registry, replacements = re.subn(
                r"Pattern K1–K\d+",
                "Pattern K1–K5",
                registry,
                count=1,
            )
            self.assertEqual(replacements, 1)
            registry_path.write_text(registry, encoding="utf-8")

            result = self.run_package_validator(repo)

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("registry", result.stderr.lower())

    def test_validator_rejects_style_card_missing_required_field(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo = self.copy_package_fixture(Path(temporary_directory))
            card_path = (
                repo
                / "profiles"
                / "blog-ca-nhan"
                / "styles"
                / "ke-trai-nghiem.md"
            )
            card = card_path.read_text(encoding="utf-8")
            card = card.replace("- **Cách kết:**", "- **Điểm dừng:**", 1)
            card_path.write_text(card, encoding="utf-8")

            result = self.run_package_validator(repo)

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("ke-trai-nghiem", result.stderr)
            self.assertIn("Cách kết", result.stderr)

    def test_validator_rejects_extra_style_card_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo = self.copy_package_fixture(Path(temporary_directory))
            extra_card = (
                repo
                / "profiles"
                / "blog-ca-nhan"
                / "styles"
                / "ban-nhap-noi-bo.md"
            )
            extra_card.write_text("Không được đi vào public payload.\n", encoding="utf-8")

            result = self.run_package_validator(repo)

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("ban-nhap-noi-bo.md", result.stderr)

    def test_validator_rejects_extra_reference_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo = self.copy_package_fixture(Path(temporary_directory))
            extra_reference = repo / "references" / "ghi-chu-rieng.md"
            extra_reference.write_text(
                "Không được đi vào public payload.\n",
                encoding="utf-8",
            )

            result = self.run_packager(repo)

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("ghi-chu-rieng.md", result.stderr)

    def test_validator_rejects_extra_calibration_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo = self.copy_package_fixture(Path(temporary_directory))
            extra_calibration = repo / "calibration" / "raw-user-prose.md"
            extra_calibration.write_text(
                "Không được đi vào public payload.\n",
                encoding="utf-8",
            )

            result = self.run_packager(repo)

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("raw-user-prose.md", result.stderr)

    def test_validator_rejects_credential_shaped_payload_content(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo = self.copy_package_fixture(Path(temporary_directory))
            canary = "ghp_" + "A" * 32
            log_path = repo / "calibration" / "LOG.md"
            with log_path.open("a", encoding="utf-8") as log:
                log.write(f"\n{canary}\n")

            result = self.run_packager(repo)

            output = result.stdout + result.stderr
            self.assertNotEqual(result.returncode, 0, output)
            self.assertIn("credential", output.lower())
            self.assertNotIn(canary, output)

    def test_validator_rejects_machine_path_in_payload_content(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo = self.copy_package_fixture(Path(temporary_directory))
            private_path = "/" + "Users" + "/private-account/project"
            log_path = repo / "calibration" / "LOG.md"
            with log_path.open("a", encoding="utf-8") as log:
                log.write(f"\n{private_path}\n")

            result = self.run_packager(repo)

            output = result.stdout + result.stderr
            self.assertNotEqual(result.returncode, 0, output)
            self.assertIn("machine path", output.lower())
            self.assertNotIn(private_path, output)

    def test_packager_rejects_style_card_under_incompatible_profile(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo = self.copy_package_fixture(Path(temporary_directory))
            source = (
                repo
                / "profiles"
                / "ky-thuat-doanh-nghiep"
                / "styles"
                / "huong-dan-ky-thuat.md"
            )
            incompatible = (
                repo
                / "profiles"
                / "blog-ca-nhan"
                / "styles"
                / "huong-dan-ky-thuat.md"
            )
            shutil.copy2(source, incompatible)

            result = self.run_packager(repo)

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("huong-dan-ky-thuat.md", result.stderr)

    def test_default_tell_scan_includes_nested_profile_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo = self.copy_package_fixture(Path(temporary_directory))
            card_path = (
                repo
                / "profiles"
                / "blog-ca-nhan"
                / "styles"
                / "ke-trai-nghiem.md"
            )
            with card_path.open("a", encoding="utf-8") as card:
                card.write("\nĐiều quan trọng cần lưu ý rằng đây là probe.\n")

            result = self.run_tell_scanner(repo)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn(
                "profiles/blog-ca-nhan/styles/ke-trai-nghiem.md",
                result.stdout,
            )

    def test_copy_preserves_a_symlink_created_after_source_validation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary = Path(temporary_directory)
            repo = self.copy_package_fixture(temporary)
            canary = temporary / "release-host-secret.txt"
            canary.write_text("outside-canary-after-validation", encoding="utf-8")
            marker = temporary / "source-validation-finished"
            saved_skill = temporary / "original-SKILL.md"
            shim_directory = self.install_python_shim(
                temporary,
                "\n".join(
                    [
                        f"if [[ ! -e {shlex.quote(str(marker))} ]]; then",
                        f"  touch {shlex.quote(str(marker))}",
                        f"  mv {shlex.quote(str(repo / 'SKILL.md'))} {shlex.quote(str(saved_skill))}",
                        f"  ln -s {shlex.quote(str(canary))} {shlex.quote(str(repo / 'SKILL.md'))}",
                        "  exit 0",
                        "fi",
                        f"exec {shlex.quote(sys.executable)} \"$@\"",
                    ]
                ),
            )
            env = os.environ.copy()
            env["PATH"] = f"{shim_directory}{os.pathsep}{env['PATH']}"

            result = self.run_packager(repo, env=env)

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            archive = repo / "dist" / "vi-humanizer.skill"
            if archive.exists():
                self.assertNotIn(canary.read_bytes(), archive.read_bytes())

    def test_failed_archive_validation_keeps_the_previous_release_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary = Path(temporary_directory)
            repo = self.copy_package_fixture(temporary)
            archive = repo / "dist" / "vi-humanizer.skill"
            archive.parent.mkdir()
            previous_release = b"known-good-release-artifact"
            archive.write_bytes(previous_release)
            shim_directory = self.install_python_shim(
                temporary,
                "\n".join(
                    [
                        "if [[ \" $* \" == *\" --archive \"* ]]; then",
                        "  exit 9",
                        "fi",
                        f"exec {shlex.quote(sys.executable)} \"$@\"",
                    ]
                ),
            )
            env = os.environ.copy()
            env["PATH"] = f"{shim_directory}{os.pathsep}{env['PATH']}"

            result = self.run_packager(repo, env=env)

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(archive.read_bytes(), previous_release)

    def test_packages_the_existing_regular_payload(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo = self.copy_package_fixture(Path(temporary_directory))

            result = self.run_packager(repo)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            archive = repo / "dist" / "vi-humanizer.skill"
            with zipfile.ZipFile(archive) as package:
                names = set(package.namelist())
            self.assertIn("vi-humanizer/SKILL.md", names)
            self.assertTrue(any(name.startswith("vi-humanizer/profiles/") for name in names))
            self.assertTrue(any(name.startswith("vi-humanizer/references/") for name in names))
            self.assertTrue(any(name.startswith("vi-humanizer/calibration/") for name in names))

    def test_packages_the_license_notice_in_both_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo = self.copy_package_fixture(Path(temporary_directory))

            result = self.run_packager(repo)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            for archive_name, license_path in (
                ("vi-humanizer.skill", "vi-humanizer/LICENSE"),
                ("vi-humanizer-claude-org.zip", "LICENSE"),
            ):
                with self.subTest(archive=archive_name):
                    with zipfile.ZipFile(repo / "dist" / archive_name) as package:
                        self.assertIn(license_path, package.namelist())
                        self.assertEqual(package.read(license_path), (repo / "LICENSE").read_bytes())

    def test_packager_rejects_missing_license(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo = self.copy_package_fixture(Path(temporary_directory))
            (repo / "LICENSE").unlink()

            result = self.run_packager(repo)

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("LICENSE", result.stderr)

    def test_packages_exact_public_advisor_runtime_in_both_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo = self.copy_package_fixture(Path(temporary_directory))

            result = self.run_packager(repo)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            expected = {
                "advisor/__init__.py",
                "advisor/__main__.py",
                "advisor/cli.py",
                "advisor/client.py",
                "advisor/models.py",
                "advisor/questions.py",
            }
            for archive_name, prefix in (
                ("vi-humanizer.skill", "vi-humanizer/"),
                ("vi-humanizer-claude-org.zip", ""),
            ):
                with zipfile.ZipFile(repo / "dist" / archive_name) as package:
                    names = {
                        name.removeprefix(prefix)
                        for name in package.namelist()
                        if name.startswith(prefix + "advisor/") and not name.endswith("/")
                    }
                    all_names = set(package.namelist())
                self.assertEqual(names, expected)
                self.assertIn(prefix + "references/typesafe-advisor.md", all_names)
                self.assertFalse(any("__pycache__" in name or name.startswith(prefix + "tests/") for name in all_names))
                self.assertFalse(any(name.startswith(prefix + "guard_eval/") or name.startswith(prefix + "eval/") for name in all_names))

    def test_package_does_not_capture_typesafe_key_from_environment(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo = self.copy_package_fixture(Path(temporary_directory))
            env = os.environ.copy()
            env["TYPESAFE_API_KEY"] = "PACKAGE-SECRET-CANARY-005"

            result = self.run_packager(repo, env=env)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            for archive_name in ("vi-humanizer.skill", "vi-humanizer-claude-org.zip"):
                archive = repo / "dist" / archive_name
                self.assertNotIn(b"PACKAGE-SECRET-CANARY-005", archive.read_bytes())

    def test_packages_claude_org_upload_with_skill_at_archive_root(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo = self.copy_package_fixture(Path(temporary_directory))

            result = self.run_packager(repo)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            archive = repo / "dist" / "vi-humanizer-claude-org.zip"
            with zipfile.ZipFile(archive) as package:
                names = set(package.namelist())
            self.assertIn("SKILL.md", names)
            self.assertTrue(any(name.startswith("profiles/") for name in names))
            self.assertTrue(any(name.startswith("references/") for name in names))
            self.assertTrue(any(name.startswith("calibration/") for name in names))
            self.assertFalse(any(name.startswith("vi-humanizer/") for name in names))
            self.assertFalse(any(name.startswith(".claude-plugin/") for name in names))
            self.assertNotIn("README.md", names)

    def test_packages_profile_rules_with_their_compatible_style_cards(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo = self.copy_package_fixture(Path(temporary_directory))

            result = self.run_packager(repo)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            archive = repo / "dist" / "vi-humanizer-claude-org.zip"
            with zipfile.ZipFile(archive) as package:
                names = set(package.namelist())
            expected_files = {
                "profiles/blog-ca-nhan/rules.md",
                "profiles/blog-ca-nhan/styles/ke-trai-nghiem.md",
                "profiles/blog-ca-nhan/styles/phoi-hop-cong-viec.md",
                "profiles/blog-ca-nhan/styles/chuyen-mon-cong-khai.md",
                "profiles/blog-ca-nhan/styles/marketing-thuyet-phuc.md",
                "profiles/ky-thuat-doanh-nghiep/rules.md",
                "profiles/ky-thuat-doanh-nghiep/styles/huong-dan-ky-thuat.md",
                "profiles/ky-thuat-doanh-nghiep/styles/van-hanh-doanh-nghiep.md",
                "profiles/ky-thuat-doanh-nghiep/styles/hoc-thuat-phan-tich.md",
            }
            actual_profile_files = {
                name
                for name in names
                if name.startswith("profiles/") and not name.endswith("/")
            }
            self.assertEqual(actual_profile_files, expected_files)
            self.assertNotIn("profiles/blog-ca-nhan.md", names)
            self.assertNotIn("profiles/ky-thuat-doanh-nghiep.md", names)

    def test_validates_archive_bytes_against_the_staged_payload(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo = self.copy_package_fixture(Path(temporary_directory))
            package_result = self.run_packager(repo)
            self.assertEqual(
                package_result.returncode,
                0,
                package_result.stdout + package_result.stderr,
            )
            archive = repo / "dist" / "vi-humanizer.skill"

            result = self.run_archive_validator(repo, archive, repo)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
