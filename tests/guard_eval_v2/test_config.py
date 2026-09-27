from __future__ import annotations

import json
import math
import tempfile
import unittest
from pathlib import Path

from guard_eval.v2.config import ConfigError, canonical_digest, load_evaluation_config, load_pricing_snapshot


class ConfigContractTests(unittest.TestCase):
    def _write(self, data: dict) -> Path:
        directory = Path(tempfile.mkdtemp())
        path = directory / "config.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def test_config_requires_exact_model_dual_question_versions_and_controls(self) -> None:
        data = {
            "config_version": "",
            "model_version": "jev-1.13.0",
            "absolute_question_set_version": "sha256:" + "1" * 64,
            "ranking_question_set_version": "sha256:" + "2" * 64,
            "timeout_seconds": 30,
            "retry_policy": {"max_attempts": 2, "backoff_seconds": 0.5},
            "max_candidates": 3,
        }
        data["config_version"] = canonical_digest(data, "config_version")
        loaded = load_evaluation_config(self._write(data))
        self.assertEqual(loaded.model_version, "jev-1.13.0")
        data["model_version"] = "jev-latest"
        data["config_version"] = canonical_digest(data, "config_version")
        with self.assertRaises(ConfigError):
            load_evaluation_config(self._write(data))

    def test_config_rejects_digest_mismatch_and_bad_limits(self) -> None:
        data = {
            "config_version": "sha256:" + "0" * 64,
            "model_version": "jev-1.13.0",
            "absolute_question_set_version": "sha256:" + "1" * 64,
            "ranking_question_set_version": "sha256:" + "2" * 64,
            "timeout_seconds": 0,
            "retry_policy": {"max_attempts": 0, "backoff_seconds": -1},
            "max_candidates": 4,
        }
        with self.assertRaises(ConfigError):
            load_evaluation_config(self._write(data))

    def test_config_rejects_extra_fields_nan_and_noncanonical_candidate_limit(self) -> None:
        data = {
            "config_version": "",
            "model_version": "jev-1.13.0",
            "absolute_question_set_version": "sha256:" + "1" * 64,
            "ranking_question_set_version": "sha256:" + "2" * 64,
            "timeout_seconds": 30,
            "retry_policy": {"max_attempts": 2, "backoff_seconds": 0.5},
            "max_candidates": 3,
            "api_key": "forbidden",
        }
        data["config_version"] = canonical_digest(data, "config_version")
        with self.assertRaises(ConfigError):
            load_evaluation_config(self._write(data))
        data.pop("api_key")
        data["timeout_seconds"] = math.nan
        data["config_version"] = canonical_digest(data, "config_version")
        with self.assertRaises(ConfigError):
            load_evaluation_config(self._write(data))
        data["timeout_seconds"] = 30
        data["max_candidates"] = 1
        data["config_version"] = canonical_digest(data, "config_version")
        with self.assertRaises(ConfigError):
            load_evaluation_config(self._write(data))

    def test_pricing_requires_matching_model_https_and_nonnegative_cost(self) -> None:
        data = {
            "pricing_version": "",
            "model_version": "jev-1.13.0",
            "currency": "USD",
            "input_cost_per_million_tokens": 1.0,
            "output_cost_per_million_tokens": 2.0,
            "observed_at": "2026-09-27T00:00:00Z",
            "source": "https://docs.typesafe.ai/pricing",
        }
        data["pricing_version"] = canonical_digest(data, "pricing_version")
        self.assertEqual(load_pricing_snapshot(self._write(data), expected_model="jev-1.13.0").currency, "USD")
        data["output_cost_per_million_tokens"] = -1
        data["pricing_version"] = canonical_digest(data, "pricing_version")
        with self.assertRaises(ConfigError):
            load_pricing_snapshot(self._write(data))


if __name__ == "__main__":
    unittest.main()
