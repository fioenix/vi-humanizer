from __future__ import annotations

import unittest

from guard_eval.v2.models import (
    AbsoluteJudgmentV2,
    CandidateAssessment,
    CandidateComponent,
    CaseJudgmentV2,
    CheckStatus,
    RecommendationKind,
    RecommendationCaseV2,
    RankingJudgmentV2,
    JudgmentRunV2,
    RunStatus,
    Split,
    SafetyDimension,
    SourceIssue,
)
from guard_eval.v2.corpus import case_fingerprint, case_set_digest, validate_dev_manifest
from guard_eval.v2.policy import (
    RecommendationPolicyV2, PolicyError, apply_policy, fit_policy, fit_ranking_policy, policy_from_dict,
    policy_version,
)
from guard_eval.v2.questions import absolute_question_set_version, ranking_question_set_version
from tests.guard_eval_v2.helpers import candidate_dict, case_dict


class PolicyContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.case = RecommendationCaseV2.from_dict(case_dict(candidates=[candidate_dict("c1"), candidate_dict("c2")]))
        self.policy = RecommendationPolicyV2.conservative_fixture(
            fitted_corpus_version="sha256:" + "1" * 64,
            config_version="sha256:" + "2" * 64,
            absolute_question_set_version="sha256:" + "3" * 64,
            ranking_question_set_version="sha256:" + "4" * 64,
            model_version="jev-1.13.0",
        )
        self.policy.policy_version = policy_version(self.policy)

    def _judgment(self, *, issue=0.9, component=0.9, safety=0.05, ranking=None):
        return CaseJudgmentV2(
            absolute=AbsoluteJudgmentV2(
                case_id=self.case.case_id,
                case_fingerprint="sha256:" + "a" * 64,
                status=CheckStatus.CHECKED,
                source_context_sufficient=0.9,
                source_issue_scores={
                    SourceIssue.LEXICALLY_INCOMPLETE: issue,
                    SourceIssue.UNNATURAL_COLLOCATION: 0.1,
                },
                candidate_component_scores={
                    cid: {component_key: component for component_key in CandidateComponent}
                    for cid in ("c1", "c2")
                },
                candidate_safety_scores={
                    cid: {dimension: safety for dimension in SafetyDimension}
                    for cid in ("c1", "c2")
                },
                observed_model="jev-1.13.0",
            ),
            ranking=ranking,
        )

    def test_source_below_negative_threshold_is_kept(self) -> None:
        decision = apply_policy(self.case, self._judgment(issue=0.1), self.policy)
        self.assertEqual(decision.recommendation, RecommendationKind.KEEP)

    def test_source_uncertainty_routes_review(self) -> None:
        decision = apply_policy(self.case, self._judgment(issue=0.5), self.policy)
        self.assertEqual(decision.recommendation, RecommendationKind.REVIEW)
        self.assertIn("source_signal_uncertain", decision.reason_codes)

    def test_no_acceptable_candidate_routes_review(self) -> None:
        decision = apply_policy(self.case, self._judgment(component=0.1), self.policy)
        self.assertEqual(decision.recommendation, RecommendationKind.REVIEW)
        self.assertEqual(decision.eligible_candidate_ids, [])

    def test_one_acceptable_candidate_replaces_without_choice(self) -> None:
        judgment = self._judgment()
        judgment.absolute.candidate_component_scores["c2"][CandidateComponent.FIXES_ISSUE] = 0.1
        decision = apply_policy(self.case, judgment, self.policy)
        self.assertEqual(decision.recommendation, RecommendationKind.REPLACE)
        self.assertEqual(decision.selected_candidate_id, "c1")

    def test_choice_cannot_override_absolute_gate_and_must_be_clear(self) -> None:
        ranking = RankingJudgmentV2(
            eligible_candidate_ids=["c1", "c2"],
            probabilities={"c1": 0.55, "c2": 0.45},
            choice="c1",
            confidence=0.55,
            observed_model="jev-1.13.0",
        )
        self.assertEqual(apply_policy(self.case, self._judgment(ranking=ranking), self.policy).recommendation, RecommendationKind.REVIEW)
        ranking.probabilities = {"c1": 0.9, "c2": 0.1}
        ranking.confidence = 0.9
        decision = apply_policy(self.case, self._judgment(ranking=ranking), self.policy)
        self.assertEqual(decision.recommendation, RecommendationKind.REPLACE)
        self.assertEqual(decision.selected_candidate_id, "c1")

    def test_safety_risk_removes_candidate_from_shortlist(self) -> None:
        judgment = self._judgment()
        judgment.absolute.candidate_safety_scores["c1"][SafetyDimension.ADDS_CLAIM] = 0.9
        judgment.absolute.candidate_component_scores["c2"][CandidateComponent.FIXES_ISSUE] = 0.1
        decision = apply_policy(self.case, judgment, self.policy)
        self.assertEqual(decision.recommendation, RecommendationKind.REVIEW)
        self.assertEqual(decision.eligible_candidate_ids, [])

    def test_fit_policy_separates_checked_in_dev_labels(self) -> None:
        corpus = validate_dev_manifest("eval/guard/v2/manifest.json")
        judgments = []
        for case in corpus.dev:
            absolute = AbsoluteJudgmentV2(
                case_id=case.case_id,
                case_fingerprint=case_fingerprint(case),
                status=CheckStatus.CHECKED,
                source_context_sufficient=0.9,
                source_issue_scores={
                    key: 0.9 if value else 0.1 for key, value in case.expected_source_issues.items()
                },
                candidate_component_scores={
                    candidate.candidate_id: {
                        key: 0.9 if value else 0.1
                        for key, value in candidate.expected_components.items()
                    }
                    for candidate in case.candidates
                },
                candidate_safety_scores={
                    candidate.candidate_id: {
                        key: 0.9 if value else 0.1
                        for key, value in candidate.expected_safety.items()
                    }
                    for candidate in case.candidates
                },
                observed_model="jev-1.13.0",
            )
            acceptable = [candidate.candidate_id for candidate in case.candidates if candidate.expected_acceptable]
            ranking = None
            if len(acceptable) >= 2:
                ranking = RankingJudgmentV2(
                    eligible_candidate_ids=sorted(acceptable),
                    probabilities={acceptable[0]: 0.8, acceptable[1]: 0.2},
                    choice=acceptable[0],
                    confidence=0.8,
                    observed_model="jev-1.13.0",
                )
            judgments.append(CaseJudgmentV2(absolute, ranking))
        run = JudgmentRunV2(
            judgment_run_version="2.0.0",
            pipeline_version="v2",
            run_digest="sha256:" + "a" * 64,
            corpus_version=corpus.dev_version,
            case_set_digest=case_set_digest(corpus.dev),
            split=Split.DEV,
            config_version="sha256:" + "b" * 64,
            absolute_question_set_version=absolute_question_set_version(),
            ranking_question_set_version=ranking_question_set_version(),
            requested_model="jev-1.13.0",
            observed_models=["jev-1.13.0"],
            policy_version=None,
            run_status=RunStatus.COMPLETE,
            counts={"total": len(corpus.dev), "checked": len(corpus.dev), "unchecked": 0},
            judgments=judgments,
            completed_at="2026-09-27T00:00:00Z",
        )
        policy = fit_policy(corpus.dev, run)
        policy = fit_ranking_policy(corpus.dev, run, policy)
        for case, judgment in zip(corpus.dev, judgments, strict=True):
            self.assertEqual(apply_policy(case, judgment, policy).recommendation, case.expected_recommendation)
        self.assertTrue(all(
            policy.source_issue_negative_thresholds[key] < policy.source_issue_positive_thresholds[key]
            for key in SourceIssue
        ))
        judgments[0].absolute.case_fingerprint = "sha256:" + "f" * 64
        with self.assertRaisesRegex(PolicyError, "fingerprint"):
            fit_policy(corpus.dev, run)

    def test_fitted_safety_uncertainty_never_passes(self) -> None:
        corpus = validate_dev_manifest("eval/guard/v2/manifest.json")
        judgments = []
        for case in corpus.dev:
            judgments.append(CaseJudgmentV2(AbsoluteJudgmentV2(
                case_id=case.case_id,
                case_fingerprint=case_fingerprint(case),
                status=CheckStatus.CHECKED,
                source_context_sufficient=0.9,
                source_issue_scores={key: 0.9 if value else 0.1 for key, value in case.expected_source_issues.items()},
                candidate_component_scores={
                    candidate.candidate_id: {key: 0.9 if value else 0.1 for key, value in candidate.expected_components.items()}
                    for candidate in case.candidates
                },
                candidate_safety_scores={
                    candidate.candidate_id: {key: 0.9 if value else 0.1 for key, value in candidate.expected_safety.items()}
                    for candidate in case.candidates
                },
                observed_model="jev-1.13.0",
            )))
        run = JudgmentRunV2(
            "2.0.0", "v2", None, corpus.dev_version, case_set_digest(corpus.dev), Split.DEV,
            "sha256:" + "b" * 64, absolute_question_set_version(), ranking_question_set_version(),
            "jev-1.13.0", ["jev-1.13.0"], None, RunStatus.COMPLETE,
            {"total": len(corpus.dev), "checked": len(corpus.dev), "unchecked": 0, "unchecked_by_reason": {}},
            judgments, completed_at="2026-09-27T00:00:00Z",
        )
        policy = fit_policy(corpus.dev, run)
        case = corpus.dev[0]
        judgment = judgments[0]
        safe_id = next(candidate.candidate_id for candidate in case.candidates if not any(candidate.expected_safety.values()))
        dimension = next(iter(SafetyDimension))
        judgment.absolute.candidate_safety_scores[safe_id][dimension] = 0.5
        result = apply_policy(case, judgment, policy)
        self.assertEqual(result.candidate_assessments[safe_id], CandidateAssessment.REVIEW)

    def test_fit_policy_rejects_unavoidable_unacceptable_replace(self) -> None:
        corpus = validate_dev_manifest("eval/guard/v2/manifest.json")
        judgments = []
        for case in corpus.dev:
            component_scores = {
                candidate.candidate_id: {
                    key: 0.9 if value else 0.1
                    for key, value in candidate.expected_components.items()
                }
                for candidate in case.candidates
            }
            if case.case_id == "regression-choi-none":
                component_scores["c1"] = {key: 1.0 for key in CandidateComponent}
            judgments.append(CaseJudgmentV2(AbsoluteJudgmentV2(
                case_id=case.case_id,
                case_fingerprint=case_fingerprint(case),
                status=CheckStatus.CHECKED,
                source_context_sufficient=0.9,
                source_issue_scores={
                    key: (1.0 if case.case_id == "regression-choi-none" else 0.9) if value else 0.1
                    for key, value in case.expected_source_issues.items()
                },
                candidate_component_scores=component_scores,
                candidate_safety_scores={
                    candidate.candidate_id: {
                        key: 0.9 if value else (
                            0.0 if case.case_id == "regression-choi-none" and candidate.candidate_id == "c1" else 0.1
                        )
                        for key, value in candidate.expected_safety.items()
                    }
                    for candidate in case.candidates
                },
                observed_model="jev-1.13.0",
            )))
        run = JudgmentRunV2(
            "2.0.0", "v2", None, corpus.dev_version, case_set_digest(corpus.dev), Split.DEV,
            "sha256:" + "b" * 64, absolute_question_set_version(), ranking_question_set_version(),
            "jev-1.13.0", ["jev-1.13.0"], None, RunStatus.COMPLETE,
            {"total": len(corpus.dev), "checked": len(corpus.dev), "unchecked": 0, "unchecked_by_reason": {}},
            judgments, completed_at="2026-09-27T00:00:00Z",
        )

        with self.assertRaisesRegex(PolicyError, "unacceptable.*replace"):
            fit_policy(corpus.dev, run)

    def test_ranking_fit_rejects_high_confidence_wrong_choice(self) -> None:
        cases = [
            RecommendationCaseV2.from_dict(case_dict(case_id="ranking-correct", candidates=[candidate_dict("c1"), candidate_dict("c2")])),
            RecommendationCaseV2.from_dict(case_dict(case_id="ranking-wrong", candidates=[candidate_dict("c1"), candidate_dict("c2")])),
        ]
        rankings = [
            RankingJudgmentV2(["c1", "c2"], {"c1": 0.7, "c2": 0.3}, "c1", 0.7, observed_model="jev-1.13.0"),
            RankingJudgmentV2(["c1", "c2"], {"c1": 0.05, "c2": 0.95}, "c2", 0.95, observed_model="jev-1.13.0"),
        ]
        judgments = []
        for case, ranking in zip(cases, rankings, strict=True):
            absolute = self._judgment().absolute
            absolute.case_id = case.case_id
            absolute.case_fingerprint = case_fingerprint(case)
            judgments.append(CaseJudgmentV2(absolute, ranking))
        run = JudgmentRunV2(
            "2.0.0", "v2", None, "sha256:" + "1" * 64, case_set_digest(cases), Split.DEV,
            self.policy.config_version, self.policy.absolute_question_set_version,
            self.policy.ranking_question_set_version, "jev-1.13.0", ["jev-1.13.0"], None,
            RunStatus.COMPLETE, {"total": 4, "checked": 4, "unchecked": 0, "unchecked_by_reason": {}},
            judgments, completed_at="2026-09-27T00:00:00Z",
        )
        fitted = fit_ranking_policy(cases, run, self.policy)
        wrong_margin = 0.9
        self.assertFalse(0.95 >= fitted.ranking_confidence_threshold and wrong_margin >= fitted.ranking_margin_threshold)

    def test_ranking_fit_never_trades_unacceptable_replace_for_more_correct_routes(self) -> None:
        unacceptable = case_dict(
            case_id="ranking-unacceptable",
            candidates=[candidate_dict("c1", acceptable=False), candidate_dict("c2", acceptable=False)],
        )
        unacceptable["expected_recommendation"] = "review"
        unacceptable["expected_selected_candidate_id"] = None
        cases = [
            RecommendationCaseV2.from_dict(case_dict(
                case_id="ranking-good-1",
                candidates=[candidate_dict("c1"), candidate_dict("c2")],
            )),
            RecommendationCaseV2.from_dict(case_dict(
                case_id="ranking-good-2",
                candidates=[candidate_dict("c1"), candidate_dict("c2")],
            )),
            RecommendationCaseV2.from_dict(unacceptable),
        ]
        judgments = []
        for case in cases:
            absolute = self._judgment().absolute
            absolute.case_id = case.case_id
            absolute.case_fingerprint = case_fingerprint(case)
            ranking = RankingJudgmentV2(
                ["c1", "c2"], {"c1": 0.9, "c2": 0.1}, "c1", 0.9,
                observed_model="jev-1.13.0",
            )
            judgments.append(CaseJudgmentV2(absolute, ranking))
        run = JudgmentRunV2(
            "2.0.0", "v2", None, "sha256:" + "1" * 64, case_set_digest(cases), Split.DEV,
            self.policy.config_version, self.policy.absolute_question_set_version,
            self.policy.ranking_question_set_version, "jev-1.13.0", ["jev-1.13.0"], None,
            RunStatus.COMPLETE, {"total": 6, "checked": 6, "unchecked": 0, "unchecked_by_reason": {}},
            judgments, completed_at="2026-09-27T00:00:00Z",
        )

        fitted = fit_ranking_policy(cases, run, self.policy)

        result = apply_policy(cases[-1], judgments[-1], fitted)
        self.assertEqual(result.recommendation, RecommendationKind.REVIEW)
        self.assertIsNone(result.selected_candidate_id)

    def test_policy_parser_rejects_extra_fields(self) -> None:
        from guard_eval.v2.models import to_jsonable

        data = to_jsonable(self.policy)
        data["source_span"] = "raw prose must not be ignored"
        with self.assertRaises(PolicyError):
            policy_from_dict(data)


if __name__ == "__main__":
    unittest.main()
