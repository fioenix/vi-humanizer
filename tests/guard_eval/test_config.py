import json
import tempfile
import unittest
from pathlib import Path

from guard_eval.config import ConfigError, canonical_digest, load_evaluation_config, load_pricing_snapshot


class ConfigContractTests(unittest.TestCase):
    def write(self, payload):
        tmp = tempfile.TemporaryDirectory()
        path = Path(tmp.name) / "config.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        self.addCleanup(tmp.cleanup)
        return path

    def test_canonical_digest_ignores_declared_version_field(self):
        left = canonical_digest({"config_version": "sha256:" + "0" * 64, "model_version": "jev-1.13.0"}, "config_version")
        right = canonical_digest({"config_version": None, "model_version": "jev-1.13.0"}, "config_version")
        self.assertEqual(left, right)
        self.assertTrue(left.startswith("sha256:"))

    def test_config_rejects_digest_mismatch_and_invalid_request_controls(self):
        payload = {"config_version": "sha256:" + "0" * 64, "model_version": "jev-1.13.0", "question_set_version": "sha256:" + "a" * 64, "timeout_seconds": 0, "retry_policy": {"max_attempts": -1, "backoff_seconds": 0}}
        with self.assertRaises(ConfigError):
            load_evaluation_config(self.write(payload))

    def test_pricing_requires_matching_model_nonnegative_cost_and_https(self):
        payload = {"pricing_version": None, "model_version": "other", "currency": "USD", "input_cost_per_million_tokens": -1, "output_cost_per_million_tokens": 0, "observed_at": "2026-09-26T00:00:00Z", "source": "http://example.com"}
        payload["pricing_version"] = canonical_digest(payload, "pricing_version")
        with self.assertRaises(ConfigError):
            load_pricing_snapshot(self.write(payload), expected_model="jev-1.13.0")


if __name__ == "__main__":
    unittest.main()
