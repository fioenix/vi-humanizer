from __future__ import annotations

import unittest

import guard_eval.v2.models as models
from guard_eval.v2.models import (
    AbsoluteJudgmentV2,
    CandidateComponent,
    CheckStatus,
    RecommendationKind,
    RecommendationCaseV2,
    JudgmentRunV2,
    RankingJudgmentV2,
    RunStatus,
    SafetyDimension,
    SourceIssue,
    ValidationError,
    canonical_digest,
    to_jsonable,
)
from tests.guard_eval_v2.helpers import candidate_dict, case_dict


class ModelContractTests(unittest.TestCase):
    def test_v2_contract_exposes_recommendation_terms_without_action_aliases(self) -> None:
        expected_symbols = {
            "RecommendationKind",
            "CandidateAssessment",
            "RecommendationCaseV2",
            "PolicyRecommendationV2",
            "RecommendationRunV2",
            "recommendation_run_digest",
            "recommendation_run_from_dict",
        }
        old_symbols = {
            "DecisionAction",
            "CandidateAction",
            "DecisionCaseV2",
            "PolicyDecisionV2",
            "DecisionRunV2",
            "decision_run_digest",
            "decision_run_from_dict",
        }
        self.assertEqual(
            {name for name in expected_symbols if hasattr(models, name)},
            expected_symbols,
        )
        self.assertEqual({name for name in old_symbols if hasattr(models, name)}, set())

        old_data = case_dict()
        old_data["expected_action"] = old_data.pop("expected_recommendation")
        with self.assertRaises(ValidationError):
            models.RecommendationCaseV2.from_dict(old_data)
        case = models.RecommendationCaseV2.from_dict(case_dict())
        self.assertEqual(case.expected_recommendation, models.RecommendationKind.REPLACE)

    def test_enum_values_match_contract(self) -> None:
        self.assertEqual({item.value for item in RecommendationKind}, {"keep", "review", "replace"})
        self.assertEqual({item.value for item in SourceIssue}, {"lexically_incomplete", "unnatural_collocation"})
        self.assertEqual(len(CandidateComponent), 3)
        self.assertEqual(len(SafetyDimension), 6)

    def test_case_requires_all_fields_and_one_to_three_candidates(self) -> None:
        data = case_dict()
        missing = dict(data)
        missing.pop("genre")
        with self.assertRaises(ValidationError):
            RecommendationCaseV2.from_dict(missing)
        with self.assertRaises(ValidationError):
            RecommendationCaseV2.from_dict(case_dict(candidates=[]))
        four = [candidate_dict(f"c{i}") for i in range(4)]
        with self.assertRaises(ValidationError):
            RecommendationCaseV2.from_dict(case_dict(candidates=four))

    def test_candidate_requires_exact_component_and_safety_keys(self) -> None:
        data = case_dict()
        data["candidates"][0]["expected_components"].pop("fixes_issue")
        with self.assertRaises(ValidationError):
            RecommendationCaseV2.from_dict(data)

    def test_candidate_acceptability_label_is_consistent(self) -> None:
        data = case_dict()
        data["candidates"][0]["expected_acceptable"] = False
        with self.assertRaises(ValidationError):
            RecommendationCaseV2.from_dict(data)

    def test_case_and_candidate_ids_genre_and_context_are_bounded(self) -> None:
        for field, value in (("case_id", "Case 1"), ("genre", "private org memo"), ("context_before", 7)):
            data = case_dict()
            data[field] = value
            with self.assertRaises(ValidationError):
                RecommendationCaseV2.from_dict(data)
        data = case_dict()
        data["candidates"][0]["candidate_id"] = "candidate:1"
        with self.assertRaises(ValidationError):
            RecommendationCaseV2.from_dict(data)

    def test_canonical_digest_ignores_declared_version_field(self) -> None:
        left = {"version": "sha256:" + "0" * 64, "value": 1}
        right = {"version": "sha256:" + "f" * 64, "value": 1}
        self.assertEqual(canonical_digest(left, "version"), canonical_digest(right, "version"))

    def test_raw_run_requires_null_policy_and_serializes_without_prose(self) -> None:
        run = JudgmentRunV2(
            judgment_run_version="2.0.0",
            pipeline_version="v2",
            run_digest=None,
            corpus_version="sha256:" + "1" * 64,
            case_set_digest="sha256:" + "2" * 64,
            split="dev",
            config_version="sha256:" + "3" * 64,
            absolute_question_set_version="sha256:" + "4" * 64,
            ranking_question_set_version="sha256:" + "5" * 64,
            requested_model="jev-1.13.0",
            observed_models=[],
            policy_version=None,
            run_status=RunStatus.COMPLETE,
            counts={"total": 0, "checked": 0, "unchecked": 0, "unchecked_by_reason": {}},
            judgments=[],
            started_at="2026-09-27T00:00:00Z",
            completed_at="2026-09-27T00:00:01Z",
        )
        run.validate()
        self.assertIsNone(to_jsonable(run)["policy_version"])
        run.policy_version = "sha256:" + "9" * 64
        with self.assertRaises(ValidationError):
            run.validate()

    def test_unchecked_status_is_explicit(self) -> None:
        self.assertEqual(CheckStatus.UNCHECKED.value, "unchecked")

    def test_unchecked_judgments_cannot_carry_scores_or_ranking_choice(self) -> None:
        absolute = AbsoluteJudgmentV2(
            case_id="case-1",
            case_fingerprint="sha256:" + "a" * 64,
            status=CheckStatus.UNCHECKED,
            source_context_sufficient=0.9,
            reason_code="timeout",
        )
        with self.assertRaises(ValidationError):
            absolute.validate()
        ranking = RankingJudgmentV2(
            eligible_candidate_ids=["c1", "c2"],
            probabilities={"c1": 0.8, "c2": 0.2},
            choice="c1",
            confidence=0.8,
            status=CheckStatus.UNCHECKED,
            reason_code="timeout",
        )
        with self.assertRaises(ValidationError):
            ranking.validate()

    def test_run_status_and_counts_are_derived_from_judgments(self) -> None:
        absolute = AbsoluteJudgmentV2(
            case_id="case-1",
            case_fingerprint="sha256:" + "a" * 64,
            status=CheckStatus.UNCHECKED,
            reason_code="timeout",
        )
        from guard_eval.v2.models import CaseJudgmentV2

        run = JudgmentRunV2(
            judgment_run_version="2.0.0",
            pipeline_version="v2",
            run_digest=None,
            corpus_version="sha256:" + "1" * 64,
            case_set_digest="sha256:" + "2" * 64,
            split="dev",
            config_version="sha256:" + "3" * 64,
            absolute_question_set_version="sha256:" + "4" * 64,
            ranking_question_set_version="sha256:" + "5" * 64,
            requested_model="jev-1.13.0",
            observed_models=[],
            policy_version=None,
            run_status=RunStatus.COMPLETE,
            counts={"total": 1, "checked": 1, "unchecked": 0, "unchecked_by_reason": {}},
            judgments=[CaseJudgmentV2(absolute)],
        )
        with self.assertRaisesRegex(ValidationError, "counts|complete"):
            run.validate()

    def test_raw_run_parser_rejects_extra_nested_fields(self) -> None:
        from guard_eval.v2.models import judgment_run_from_dict

        data = {
            "judgment_run_version": "2.0.0", "pipeline_version": "v2", "run_digest": None,
            "corpus_version": "sha256:" + "1" * 64, "case_set_digest": "sha256:" + "2" * 64,
            "split": "dev", "config_version": "sha256:" + "3" * 64,
            "absolute_question_set_version": "sha256:" + "4" * 64,
            "ranking_question_set_version": "sha256:" + "5" * 64,
            "requested_model": "jev-1.13.0", "observed_models": [], "policy_version": None,
            "run_status": "complete",
            "counts": {"total": 0, "checked": 0, "unchecked": 0, "unchecked_by_reason": {}},
            "judgments": [{"absolute": {}, "ranking": None, "request_body": "forbidden"}],
            "started_at": "", "completed_at": "",
        }
        with self.assertRaises(ValidationError):
            judgment_run_from_dict(data)


if __name__ == "__main__":
    unittest.main()
    RankingJudgmentV2,
