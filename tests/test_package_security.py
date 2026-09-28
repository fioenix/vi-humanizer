from __future__ import annotations

import os
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
    "README.md",
    ".claude-plugin",
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
