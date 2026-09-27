from __future__ import annotations

import json
import unittest
from pathlib import Path

from guard_eval.v2.config import load_evaluation_config, load_pricing_snapshot
from guard_eval.v2.corpus import (
    case_fingerprint,
    case_set_digest,
    coverage_diagnostics,
    file_digest,
    validate_dev_manifest,
)
from guard_eval.v2.models import RecommendationCaseV2, canonical_digest
from guard_eval.v2.privacy import validate_artifact_privacy


ROOT = Path(__file__).resolve().parents[2]


def _strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from _strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from _strings(child)


class CorpusArtifactTests(unittest.TestCase):
    def test_checked_in_dev_artifacts_validate_without_opening_sealed_holdout(self) -> None:
        corpus = validate_dev_manifest("eval/guard/v2/manifest.json", repo_root=ROOT)
        self.assertEqual(len(corpus.dev), 9)
        self.assertIsNone(corpus.holdout)
        self.assertEqual(corpus.manifest["holdout"]["status"], "sealed")
        config = load_evaluation_config(ROOT / "eval/guard/v2/evaluation-config.json")
        pricing = load_pricing_snapshot(
            ROOT / "eval/guard/v2/pricing.json", expected_model=config.model_version
        )
        self.assertEqual(pricing.model_version, "jev-1.13.0")

    def test_dev_coverage_is_diagnostic_not_a_false_pass(self) -> None:
        corpus = validate_dev_manifest("eval/guard/v2/manifest.json", repo_root=ROOT)
        diagnostics = coverage_diagnostics(corpus.dev)
        self.assertEqual(set(diagnostics), {
            "expected_keep",
            "expected_review",
            "expected_replace",
            "no_acceptable_candidate",
            "harmful_candidate_case",
        })
        self.assertTrue(any(item["status"] == "insufficient" for item in diagnostics.values()))

    def test_promoted_cases_keep_observed_v1_fingerprints(self) -> None:
        corpus = validate_dev_manifest("eval/guard/v2/manifest.json", repo_root=ROOT)
        promoted = [case for case in corpus.dev if case.lineage is not None]
        self.assertEqual(len(promoted), 4)
        for case in promoted:
            self.assertEqual(case_fingerprint(case), case.lineage.source_case_fingerprint)

    def test_checked_in_corpus_metadata_has_no_machine_or_account_paths(self) -> None:
        rows = [
            json.loads(line)
            for line in (ROOT / "eval/guard/v2/dev.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        values = list(_strings(rows))
        self.assertFalse(any(value.startswith(("/Users/", "/home/")) for value in values))
        self.assertFalse(any("@" in value for value in values))

    def test_historical_label_proposal_is_stale_and_contains_no_raw_prose(self) -> None:
        corpus = validate_dev_manifest("eval/guard/v2/manifest.json", repo_root=ROOT)
        proposal = json.loads(
            (ROOT / "specs/002-edit-decision-gate/evidence/dev-label-proposal.json").read_text(encoding="utf-8")
        )
        self.assertEqual(proposal["status"], "awaiting_maintainer_approval")
        self.assertNotEqual(proposal["dev_version"], corpus.dev_version)
        self.assertEqual(
            {item["case_id"]: item["case_fingerprint"] for item in proposal["cases"]},
            {case.case_id: case_fingerprint(case) for case in corpus.dev},
        )
        serialized = json.dumps(proposal, ensure_ascii=False)
        raw_strings = [
            text
            for case in corpus.dev
            for text in (case.source_span, *(candidate.candidate_span for candidate in case.candidates))
        ]
        self.assertFalse(any(text in serialized for text in raw_strings))

    def test_revision_and_holdout_approvals_bind_their_lifecycle_inputs_without_raw_prose(self) -> None:
        corpus = validate_dev_manifest("eval/guard/v2/manifest.json", repo_root=ROOT)
        config = load_evaluation_config(ROOT / "eval/guard/v2/evaluation-config.json")
        proposal_path = ROOT / "specs/002-edit-decision-gate/evidence/dev-revision-proposal.json"
        approval_path = ROOT / "specs/002-edit-decision-gate/evidence/dev-revision-approval.json"
        holdout_authorization_path = ROOT / "specs/002-edit-decision-gate/evidence/holdout-authorization.json"
        proposal = json.loads(proposal_path.read_text(encoding="utf-8"))
        approval = json.loads(approval_path.read_text(encoding="utf-8"))
        holdout_authorization = json.loads(holdout_authorization_path.read_text(encoding="utf-8"))
        self.assertEqual(proposal["dev_sha256"], corpus.manifest["dev"]["sha256"])
        self.assertEqual(proposal["dev_version"], corpus.dev_version)
        self.assertNotEqual(proposal["corpus_version"], corpus.corpus_version)
        self.assertEqual(proposal["config_version"], config.config_version)
        self.assertEqual(proposal["model_version"], config.model_version)
        self.assertEqual(proposal["absolute_question_set_version"], config.absolute_question_set_version)
        self.assertEqual(proposal["ranking_question_set_version"], config.ranking_question_set_version)
        self.assertFalse(proposal["historical_t049"]["valid_for_this_revision"])
        self.assertEqual(approval["proposal_sha256"], file_digest(proposal_path))
        self.assertEqual(approval["approved_by"], "owner_authorized_agent")
        self.assertEqual(holdout_authorization["manifest_corpus_version"], corpus.corpus_version)
        self.assertEqual(holdout_authorization["holdout_sha256"], corpus.manifest["holdout"]["sha256"])
        self.assertEqual(holdout_authorization["approved_by"], "owner_authorized_agent")
        serialized = json.dumps(
            {
                "proposal": proposal,
                "approval": approval,
                "holdout_authorization": holdout_authorization,
            },
            ensure_ascii=False,
        )
        raw_strings = [
            text
            for case in corpus.dev
            for text in (case.source_span, *(candidate.candidate_span for candidate in case.candidates))
        ]
        self.assertFalse(any(text in serialized for text in raw_strings))

    def test_observed_holdout_report_is_bound_sanitized_and_replayable(self) -> None:
        corpus = validate_dev_manifest("eval/guard/v2/manifest.json", repo_root=ROOT)
        holdout_path = ROOT / corpus.manifest["holdout"]["path"]
        holdout = [
            RecommendationCaseV2.from_dict(json.loads(line))
            for line in holdout_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        report = json.loads(
            (ROOT / "specs/002-edit-decision-gate/evidence/holdout-report.json").read_text(encoding="utf-8")
        )
        registry = json.loads(
            (ROOT / "eval/guard/v2/observed-holdouts.json").read_text(encoding="utf-8")
        )
        current = next(item for item in registry["holdouts"] if item["feature"] == "002-edit-decision-gate")
        fingerprints = sorted(case_fingerprint(case) for case in holdout)
        raw_strings = [
            text
            for case in holdout
            for text in (case.source_span, *(candidate.candidate_span for candidate in case.candidates))
        ]

        self.assertEqual(file_digest(holdout_path), corpus.manifest["holdout"]["sha256"])
        self.assertEqual(len(holdout), corpus.manifest["holdout"]["case_count"])
        self.assertTrue(all(item["status"] == "sufficient" for item in coverage_diagnostics(holdout).values()))
        self.assertEqual(report["corpus_version"], corpus.corpus_version)
        self.assertEqual(report["case_set_digest"], case_set_digest(holdout))
        self.assertEqual(report["report_digest"], canonical_digest(report, "report_digest"))
        self.assertEqual(report["decision"], "collect_more_labels")
        self.assertEqual(report["hard_invariants"], {
            "harmful_replace_recommendation_count": 0,
            "unacceptable_replace_recommendation_count": 0,
        })
        self.assertEqual(current["artifact_sha256"], corpus.manifest["holdout"]["sha256"])
        self.assertEqual(current["corpus_version"], corpus.corpus_version)
        self.assertEqual(current["fingerprints"], fingerprints)
        validate_artifact_privacy(report, raw_strings=raw_strings)


if __name__ == "__main__":
    unittest.main()
