from __future__ import annotations

import unittest

from guard_eval.v2.config import EvaluationConfigV2
from guard_eval.v2.corpus import case_fingerprint, validate_dev_manifest
from guard_eval.v2.evaluator import add_rankings, evaluate_absolute_cases
from guard_eval.v2.models import (
    AbsoluteJudgmentV2,
    CandidateComponent,
    CheckStatus,
    RecommendationCaseV2,
    RunStatus,
    SafetyDimension,
    SourceIssue,
)
from guard_eval.v2.policy import RecommendationPolicyV2
from guard_eval.v2.questions import absolute_question_set_version, ranking_question_set_version
from tests.guard_eval_v2.helpers import candidate_dict, case_dict


class FakeAdapter:
    def __init__(self, *, observed_model="jev-1.13.0"):
        self.observed_model = observed_model
        self.ranking_calls = []

    def evaluate_absolute(self, case):
        return AbsoluteJudgmentV2(
            case_id=case.case_id,
            case_fingerprint=case_fingerprint(case),
            status=CheckStatus.CHECKED,
            source_context_sufficient=0.9,
            source_issue_scores={issue: 0.9 for issue in SourceIssue},
            candidate_component_scores={c.candidate_id: {key: 0.9 for key in CandidateComponent} for c in case.candidates},
            candidate_safety_scores={c.candidate_id: {key: 0.05 for key in SafetyDimension} for c in case.candidates},
            observed_model=self.observed_model,
        )

    def evaluate_ranking(self, case, eligible_ids):
        self.ranking_calls.append((case.case_id, list(eligible_ids)))
        from guard_eval.v2.models import RankingJudgmentV2
        return RankingJudgmentV2(
            eligible_candidate_ids=list(eligible_ids),
            probabilities={item: 1 / len(eligible_ids) for item in eligible_ids},
            choice=eligible_ids[0], confidence=1 / len(eligible_ids), observed_model=self.observed_model,
        )


class EvaluatorContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = EvaluationConfigV2(
            "sha256:" + "1" * 64, "jev-1.13.0",
            absolute_question_set_version(), ranking_question_set_version(), 30, 2, 0.1, 3,
        )
        self.cases = [
            RecommendationCaseV2.from_dict(case_dict(case_id="case-1", candidates=[candidate_dict("c1"), candidate_dict("c2")])),
            RecommendationCaseV2.from_dict(case_dict(case_id="case-2", candidates=[candidate_dict("c1")])),
        ]

    def test_absolute_run_is_complete_and_policy_free(self) -> None:
        run = evaluate_absolute_cases(
            self.cases, FakeAdapter(), split="dev", corpus_version="sha256:" + "9" * 64, config=self.config,
        )
        self.assertEqual(run.run_status, RunStatus.COMPLETE)
        self.assertIsNone(run.policy_version)
        self.assertEqual(run.counts["checked"], 2)

    def test_mixed_observed_model_invalidates_run(self) -> None:
        run = evaluate_absolute_cases(
            self.cases, FakeAdapter(observed_model="jev-other"), split="dev",
            corpus_version="sha256:" + "9" * 64, config=self.config,
        )
        self.assertEqual(run.run_status, RunStatus.INVALID)

    def test_ranking_runs_only_for_shortlists_of_two_or_more(self) -> None:
        adapter = FakeAdapter()
        run = evaluate_absolute_cases(
            self.cases, adapter, split="dev", corpus_version="sha256:" + "9" * 64, config=self.config,
        )
        policy = RecommendationPolicyV2.conservative_fixture(
            fitted_corpus_version=run.corpus_version,
            config_version=run.config_version,
            absolute_question_set_version=run.absolute_question_set_version,
            ranking_question_set_version=run.ranking_question_set_version,
            model_version=run.requested_model,
        )
        ranked = add_rankings(self.cases, run, adapter, policy)
        self.assertEqual(adapter.ranking_calls, [("case-1", ["c1", "c2"])])
        self.assertIsNotNone(ranked.judgments[0].ranking)
        self.assertIsNone(ranked.judgments[1].ranking)

    def test_cached_unchecked_ranking_is_idempotent(self) -> None:
        class UncheckedAdapter(FakeAdapter):
            def evaluate_ranking(self, case, eligible_ids):
                from guard_eval.v2.models import RankingJudgmentV2

                self.ranking_calls.append((case.case_id, list(eligible_ids)))
                return RankingJudgmentV2(
                    eligible_candidate_ids=list(eligible_ids),
                    probabilities={}, choice="", confidence=0.0,
                    status=CheckStatus.UNCHECKED, reason_code="timeout",
                )

        adapter = UncheckedAdapter()
        run = evaluate_absolute_cases(
            self.cases, adapter, split="dev", corpus_version="sha256:" + "9" * 64, config=self.config,
        )
        policy = RecommendationPolicyV2.conservative_fixture(
            fitted_corpus_version=run.corpus_version,
            config_version=run.config_version,
            absolute_question_set_version=run.absolute_question_set_version,
            ranking_question_set_version=run.ranking_question_set_version,
            model_version=run.requested_model,
        )
        first = add_rankings(self.cases, run, adapter, policy)
        counts = dict(first.counts)
        digest = first.run_digest
        second = add_rankings(self.cases, first, adapter, policy)
        self.assertEqual(second.counts, counts)
        self.assertEqual(second.run_digest, digest)
        self.assertEqual(len(adapter.ranking_calls), 1)

    def test_candidate_limit_is_checked_before_adapter_calls(self) -> None:
        config = EvaluationConfigV2(
            self.config.config_version, self.config.model_version,
            self.config.absolute_question_set_version, self.config.ranking_question_set_version,
            30, 2, 0.1, 1,
        )
        adapter = FakeAdapter()
        with self.assertRaisesRegex(ValueError, "max_candidates"):
            evaluate_absolute_cases(
                self.cases, adapter, split="dev", corpus_version="sha256:" + "9" * 64, config=config,
            )

    def test_keep_source_never_spends_ranking_quota(self) -> None:
        class KeepAdapter(FakeAdapter):
            def evaluate_absolute(self, case):
                judgment = super().evaluate_absolute(case)
                judgment.source_issue_scores = {issue: 0.1 for issue in SourceIssue}
                return judgment

        adapter = KeepAdapter()
        run = evaluate_absolute_cases(
            [self.cases[0]], adapter, split="dev", corpus_version="sha256:" + "9" * 64, config=self.config,
        )
        policy = RecommendationPolicyV2.conservative_fixture(
            fitted_corpus_version=run.corpus_version,
            config_version=run.config_version,
            absolute_question_set_version=run.absolute_question_set_version,
            ranking_question_set_version=run.ranking_question_set_version,
            model_version=run.requested_model,
        )
        ranked = add_rankings([self.cases[0]], run, adapter, policy)
        self.assertEqual(adapter.ranking_calls, [])
        self.assertIsNone(ranked.judgments[0].ranking)

    def test_checked_in_dev_has_rankable_candidates_on_a_known_positive_source(self) -> None:
        corpus = validate_dev_manifest("eval/guard/v2/manifest.json")
        case = next(item for item in corpus.dev if item.case_id == "dev-hut-hang")

        class LabelShapedAdapter(FakeAdapter):
            def evaluate_absolute(self, observed_case):
                return AbsoluteJudgmentV2(
                    case_id=observed_case.case_id,
                    case_fingerprint=case_fingerprint(observed_case),
                    status=CheckStatus.CHECKED,
                    source_context_sufficient=0.9,
                    source_issue_scores={
                        SourceIssue.LEXICALLY_INCOMPLETE: 0.9,
                        SourceIssue.UNNATURAL_COLLOCATION: 0.1,
                    },
                    candidate_component_scores={
                        candidate.candidate_id: {
                            component: 0.9 if candidate.expected_acceptable else 0.1
                            for component in CandidateComponent
                        }
                        for candidate in observed_case.candidates
                    },
                    candidate_safety_scores={
                        candidate.candidate_id: {
                            dimension: 0.95 if candidate.expected_safety[dimension] else 0.05
                            for dimension in SafetyDimension
                        }
                        for candidate in observed_case.candidates
                    },
                    observed_model=self.observed_model,
                )

        adapter = LabelShapedAdapter()
        run = evaluate_absolute_cases(
            [case], adapter, split="dev", corpus_version=corpus.dev_version, config=self.config,
        )
        policy = RecommendationPolicyV2.conservative_fixture(
            fitted_corpus_version=run.corpus_version,
            config_version=run.config_version,
            absolute_question_set_version=run.absolute_question_set_version,
            ranking_question_set_version=run.ranking_question_set_version,
            model_version=run.requested_model,
        )
        ranked = add_rankings([case], run, adapter, policy)

        self.assertEqual(adapter.ranking_calls, [("dev-hut-hang", ["c1", "c3"])])
        self.assertIsNotNone(ranked.judgments[0].ranking)


if __name__ == "__main__":
    unittest.main()
