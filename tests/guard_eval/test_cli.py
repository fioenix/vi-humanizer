import os
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from guard_eval.cli import main
from guard_eval.config import load_evaluation_config
from guard_eval.corpus import validate_manifest
from guard_eval.typesafe_adapter import TypeSafeAdapter
from tests.guard_eval.test_typesafe_adapter import FakeClient, checked_response
from tests.guard_eval.test_policy import run_for
from guard_eval.models import Split, to_jsonable


class CliContractTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, "-m", "guard_eval", *args], text=True, capture_output=True, env={**os.environ, "PYTHONPATH": "."})

    def test_help_lists_all_subcommands(self):
        result = self.run_cli("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        for command in ("validate", "evaluate", "fit-policy", "report", "all"):
            self.assertIn(command, result.stdout)

    def test_unknown_subcommand_is_contract_error_not_success(self):
        result = self.run_cli("unknown")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("invalid choice", result.stderr.lower())

    def test_validate_does_not_import_typesafe_sdk(self):
        result = subprocess.run(
            [sys.executable, "-c", "import sys; import guard_eval.cli; assert 'typesafe_sdk' not in sys.modules"],
            text=True, capture_output=True, env={**os.environ, "PYTHONPATH": "."},
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_validate_returns_zero_for_valid_corpus_without_credential(self):
        env = {**os.environ, "PYTHONPATH": "."}
        env.pop("TYPESAFE_API_KEY", None)
        result = subprocess.run(
            [sys.executable, "-m", "guard_eval", "validate", "--manifest", "eval/guard/manifest.json"],
            text=True, capture_output=True, env=env,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("8 cases", result.stdout)

    def test_validate_returns_one_for_missing_manifest(self):
        result = self.run_cli("validate", "--manifest", "missing.json")
        self.assertEqual(result.returncode, 1)
        self.assertIn("invalid corpus", result.stderr.lower())

    def test_evaluate_fake_dev_success_and_no_key_incomplete(self):
        corpus = validate_manifest("eval/guard/manifest.json")
        responses = iter([checked_response(case) for case in corpus.dev])
        adapter = TypeSafeAdapter(
            load_evaluation_config("eval/guard/evaluation-config.json"), api_key="test-key",
            client_factory=lambda **_: FakeClient(next(responses)),
        )
        with tempfile.TemporaryDirectory() as directory, patch("guard_eval.cli._make_adapter", return_value=adapter):
            output = Path(directory) / "run.json"
            code = main(["evaluate", "--manifest", "eval/guard/manifest.json", "--config", "eval/guard/evaluation-config.json", "--split", "dev", "--output", str(output)])
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(output.read_text())["run_status"], "complete")

        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {}, clear=True):
            output = Path(directory) / "run.json"
            code = main(["evaluate", "--manifest", "eval/guard/manifest.json", "--config", "eval/guard/evaluation-config.json", "--split", "dev", "--output", str(output)])
            data = json.loads(output.read_text())
            self.assertEqual(code, 2)
            self.assertEqual(data["run_status"], "incomplete")
            self.assertEqual({item["reason_code"] for item in data["judgments"]}, {"missing_api_key"})

    def test_evaluate_rejects_holdout_public_command(self):
        with tempfile.TemporaryDirectory() as directory:
            code = main(["evaluate", "--manifest", "eval/guard/manifest.json", "--config", "eval/guard/evaluation-config.json", "--split", "holdout", "--output", str(Path(directory) / "run.json")])
        self.assertEqual(code, 1)

    def test_fit_policy_report_and_all_contracts(self):
        corpus = validate_manifest("eval/guard/manifest.json")
        config = load_evaluation_config("eval/guard/evaluation-config.json")
        frozen_policy_path = Path("eval/guard/policy.json")
        frozen_policy_bytes = frozen_policy_path.read_bytes()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            dev_run_path = root / "dev-run.json"
            dev_run_path.write_text(json.dumps(to_jsonable(run_for(corpus.dev, corpus, config)), ensure_ascii=False), encoding="utf-8")
            policy_path = root / "candidate-policy.json"
            code = main(["fit-policy", "--manifest", "eval/guard/manifest.json", "--config", "eval/guard/evaluation-config.json", "--run", str(dev_run_path), "--output", str(policy_path)])
            self.assertEqual(code, 0)
            self.assertTrue(policy_path.exists())
            self.assertEqual(frozen_policy_path.read_bytes(), frozen_policy_bytes)

            holdout_run_path = root / "holdout-run.json"
            holdout_run_path.write_text(json.dumps(to_jsonable(run_for(corpus.holdout, corpus, config, split=Split.HOLDOUT)), ensure_ascii=False), encoding="utf-8")
            report_path = root / "report.json"
            code = main(["report", "--manifest", "eval/guard/manifest.json", "--config", "eval/guard/evaluation-config.json", "--policy", str(policy_path), "--pricing", "eval/guard/pricing.json", "--run", str(holdout_run_path), "--output", str(report_path)])
            self.assertEqual(code, 0)
            self.assertIn(json.loads(report_path.read_text())["decision"], {"stop", "continue_shadow", "collect_more_labels"})

            responses = iter([checked_response(case) for case in corpus.holdout])
            adapter = TypeSafeAdapter(config, api_key="test-key", client_factory=lambda **_: FakeClient(next(responses)))
            output_dir = root / "all"
            with patch("guard_eval.cli._make_adapter", return_value=adapter):
                code = main(["all", "--manifest", "eval/guard/manifest.json", "--config", "eval/guard/evaluation-config.json", "--policy", str(policy_path), "--pricing", "eval/guard/pricing.json", "--split", "holdout", "--output-dir", str(output_dir)])
            self.assertEqual(code, 0)
            self.assertTrue((output_dir / "holdout-run.json").exists())
            self.assertTrue((output_dir / "holdout-report.json").exists())

    def test_all_no_key_returns_two_and_never_fits_or_overwrites_policy(self):
        corpus = validate_manifest("eval/guard/manifest.json")
        config = load_evaluation_config("eval/guard/evaluation-config.json")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            dev_run = root / "dev.json"
            dev_run.write_text(json.dumps(to_jsonable(run_for(corpus.dev, corpus, config))), encoding="utf-8")
            policy = root / "policy.json"
            self.assertEqual(main(["fit-policy", "--manifest", "eval/guard/manifest.json", "--config", "eval/guard/evaluation-config.json", "--run", str(dev_run), "--output", str(policy)]), 0)
            before = policy.read_bytes()
            with patch.dict(os.environ, {}, clear=True):
                code = main(["all", "--manifest", "eval/guard/manifest.json", "--config", "eval/guard/evaluation-config.json", "--policy", str(policy), "--pricing", "eval/guard/pricing.json", "--split", "holdout", "--output-dir", str(root / "no-key")])
            self.assertEqual(code, 2)
            self.assertEqual(policy.read_bytes(), before)
            report = json.loads((root / "no-key" / "holdout-report.json").read_text())
            self.assertEqual((report["run_status"], report["decision"]), ("incomplete", None))


if __name__ == "__main__":
    unittest.main()
