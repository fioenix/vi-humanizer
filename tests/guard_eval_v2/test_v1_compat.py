from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from guard_eval.models import CheckStatus, GuardDimension, JudgmentSet, NaturalnessReason
from guard_eval.policy import DecisionPolicy
from guard_eval.v2.corpus import CorpusError, file_digest, project_case_to_v1, validate_v1_artifact_lock
from guard_eval.v2.evaluator import apply_v1_policy_compat
from guard_eval.v2.models import RecommendationCaseV2, canonical_digest
from tests.guard_eval_v2.helpers import case_dict


class V1CompatibilityTests(unittest.TestCase):
    def test_byte_lock_detects_one_byte_drift(self) -> None:
        root = Path(tempfile.mkdtemp())
        artifact = root / "eval/guard/policy.json"
        artifact.parent.mkdir(parents=True)
        artifact.write_text("{}\n", encoding="utf-8")
        lock = {"lock_version": "1.0.0", "lock_digest": "", "entries": [{"path": "eval/guard/policy.json", "sha256": file_digest(artifact)}]}
        lock["lock_digest"] = canonical_digest(lock, "lock_digest")
        lock_path = root / "lock.json"
        lock_path.write_text(json.dumps(lock), encoding="utf-8")
        validate_v1_artifact_lock(lock_path, repo_root=root)
        artifact.write_text("{ }\n", encoding="utf-8")
        with self.assertRaises(CorpusError):
            validate_v1_artifact_lock(lock_path, repo_root=root)

    def test_projection_contains_request_state_only(self) -> None:
        case = RecommendationCaseV2.from_dict(case_dict())
        projected = project_case_to_v1(case)
        serialized = repr(projected)
        self.assertNotIn("expected_", serialized)
        self.assertNotIn("provenance", serialized)
        self.assertEqual(projected.candidates[0].candidate_id, "c1")

    def test_frozen_v1_policy_can_apply_to_different_evaluation_corpus(self) -> None:
        case = project_case_to_v1(RecommendationCaseV2.from_dict(case_dict()))
        policy = DecisionPolicy(
            policy_version=None,
            corpus_version_fitted="sha256:" + "1" * 64,
            config_version="sha256:" + "2" * 64,
            question_set_version="sha256:" + "3" * 64,
            model_version="jev-1.13.0",
            needs_edit_thresholds={key: 0.7 for key in NaturalnessReason},
            preference_confidence_threshold=0.7,
            preference_margin_threshold=0.2,
            safety_review_threshold=0.3,
            safety_reject_threshold=0.7,
            selection_order=["fixture"],
            created_at="2026-09-27T00:00:00Z",
        )
        judgment = JudgmentSet(
            case_id=case.case_id,
            case_fingerprint="sha256:" + "a" * 64,
            status=CheckStatus.CHECKED,
            naturalness_scores={key: 0.9 for key in NaturalnessReason},
            preference_probabilities={"keep_original": 0.05, "candidate:c1": 0.9, "none_of_candidates": 0.05},
            preference_choice="candidate:c1",
            preference_confidence=0.9,
            candidate_safety_scores={"c1": {key: 0.05 for key in GuardDimension}},
            model_version="jev-1.13.0",
        )
        result = apply_v1_policy_compat(case, judgment, policy, evaluation_corpus_version="sha256:" + "9" * 64)
        self.assertEqual(result.selected_candidate_id, "c1")


if __name__ == "__main__":
    unittest.main()
