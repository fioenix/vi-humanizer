from __future__ import annotations

import unittest

from guard_eval.v2.models import (
    CandidateAssessment,
    RecommendationKind,
    RecommendationCaseV2,
    RecommendationRunV2,
    PolicyRecommendationV2,
    RunStatus,
)
from guard_eval.v2.corpus import case_fingerprint
from guard_eval.v2.report import MetricValue, generate_comparison_report
from tests.guard_eval_v2.helpers import candidate_dict, case_dict


def make_case(case_id: str, action: str, *, harmful: bool = False) -> RecommendationCaseV2:
    acceptable = action == "replace"
    candidate = candidate_dict("c1", acceptable=acceptable)
    if harmful:
        candidate["expected_acceptable"] = False
        candidate["expected_components"]["fixes_issue"] = True
        candidate["expected_safety"]["adds_claim"] = True
    data = case_dict(case_id=case_id, candidates=[candidate])
    data["expected_recommendation"] = action
    data["expected_selected_candidate_id"] = "c1" if action == "replace" else None
    if action == "keep":
        data["expected_source_issues"] = {"lexically_incomplete": False, "unnatural_collocation": False}
    return RecommendationCaseV2.from_dict(data)


def decision(case: RecommendationCaseV2, action: RecommendationKind, *, candidate_action: CandidateAssessment, selected: str | None = None) -> PolicyRecommendationV2:
    return PolicyRecommendationV2(
        case_id=case.case_id,
        case_fingerprint=case_fingerprint(case),
        recommendation=action,
        selected_candidate_id=selected,
        reason_codes=[
            "source_already_sufficient" if action is RecommendationKind.KEEP
            else "ranked_candidate_selected" if action is RecommendationKind.REPLACE
            else "no_acceptable_candidate"
        ],
        candidate_assessments={"c1": candidate_action},
        eligible_candidate_ids=["c1"] if action is RecommendationKind.REPLACE else [],
    )


def run(pipeline: str, decisions: list[PolicyRecommendationV2], *, status: RunStatus = RunStatus.COMPLETE) -> RecommendationRunV2:
    return RecommendationRunV2(
        recommendation_run_version="2.0.0",
        recommendation_run_digest="sha256:" + ("1" if pipeline == "v1_compat" else "2") * 64,
        pipeline_version=pipeline,
        judgment_run_digest="sha256:" + ("3" if pipeline == "v1_compat" else "4") * 64,
        evaluation_corpus_version="sha256:" + "5" * 64,
        policy_version="sha256:" + "6" * 64,
        policy_fitted_corpus_version="sha256:" + "7" * 64,
        run_status=status,
        recommendations=decisions,
    )


class ReportContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.cases = [
            *[make_case(f"keep-{i}", "keep", harmful=True) for i in range(5)],
            *[make_case(f"review-{i}", "review") for i in range(5)],
            *[make_case(f"replace-{i}", "replace") for i in range(5)],
        ]

    def _paired(self):
        v1 = []
        v2 = []
        for case in self.cases:
            if case.expected_recommendation is RecommendationKind.KEEP:
                v1.append(decision(case, RecommendationKind.KEEP, candidate_action=CandidateAssessment.REVIEW))
                v2.append(decision(case, RecommendationKind.KEEP, candidate_action=CandidateAssessment.REVIEW))
            elif case.expected_recommendation is RecommendationKind.REVIEW:
                v1.append(decision(case, RecommendationKind.REPLACE, candidate_action=CandidateAssessment.PASS, selected="c1"))
                v2.append(decision(case, RecommendationKind.REVIEW, candidate_action=CandidateAssessment.PASS))
            else:
                v1.append(decision(case, RecommendationKind.REPLACE, candidate_action=CandidateAssessment.PASS, selected="c1"))
                v2.append(decision(case, RecommendationKind.REPLACE, candidate_action=CandidateAssessment.PASS, selected="c1"))
        return run("v1_compat", v1), run("v2", v2)

    def test_metric_value_has_numerator_denominator_rate_unit_and_direction(self) -> None:
        metric = MetricValue.create(3, 4, unit="case", direction="higher_is_better", minimum_denominator=5)
        self.assertEqual(metric.rate, 0.75)
        self.assertEqual(metric.denominator_status, "insufficient")
        with self.assertRaises(ValueError):
            MetricValue.create(5, 4, unit="case", direction="higher_is_better", minimum_denominator=5)

    def test_safe_strict_improvement_continues_shadow(self) -> None:
        v1, v2 = self._paired()
        report = generate_comparison_report(self.cases, v1, v2)
        self.assertEqual(report["decision"], "continue_shadow")
        self.assertEqual(report["coverage"]["expected_keep"]["count"], 5)
        metric = report["metrics"]["no_acceptable_candidate_recall"]
        self.assertEqual(metric["v1"]["denominator"], 5)
        self.assertGreater(metric["improvement_delta"], 0)

    def test_protected_regression_or_harmful_auto_replace_stops(self) -> None:
        v1, v2 = self._paired()
        harmful_case = self.cases[0]
        v2.recommendations[0] = decision(
            harmful_case, RecommendationKind.REPLACE, candidate_action=CandidateAssessment.PASS, selected="c1"
        )
        report = generate_comparison_report(self.cases, v1, v2)
        self.assertEqual(report["decision"], "stop")
        self.assertEqual(report["hard_invariants"]["harmful_replace_recommendation_count"], 1)

    def test_unacceptable_replace_is_a_hard_stop_even_when_coverage_becomes_insufficient(self) -> None:
        v1, v2 = self._paired()
        unacceptable_case = next(
            case for case in self.cases
            if case.expected_recommendation is RecommendationKind.REVIEW
        )
        index = self.cases.index(unacceptable_case)
        v2.recommendations[index] = decision(
            unacceptable_case,
            RecommendationKind.REPLACE,
            candidate_action=CandidateAssessment.PASS,
            selected="c1",
        )
        report = generate_comparison_report(self.cases, v1, v2)
        self.assertEqual(report["decision"], "stop")
        self.assertEqual(
            report["hard_invariants"]["unacceptable_replace_recommendation_count"],
            1,
        )

    def test_insufficient_coverage_collects_more_labels(self) -> None:
        cases = self.cases[:4]
        decisions = [decision(case, RecommendationKind.KEEP, candidate_action=CandidateAssessment.REVIEW) for case in cases]
        report = generate_comparison_report(cases, run("v1_compat", decisions), run("v2", decisions))
        self.assertEqual(report["decision"], "collect_more_labels")

    def test_incomplete_or_case_mismatch_has_no_decision(self) -> None:
        v1, v2 = self._paired()
        v2.run_status = RunStatus.INCOMPLETE
        report = generate_comparison_report(self.cases, v1, v2)
        self.assertIsNone(report["decision"])
        v2.run_status = RunStatus.COMPLETE
        v2.recommendations.pop()
        report = generate_comparison_report(self.cases, v1, v2)
        self.assertIsNone(report["decision"])

    def test_disagreements_never_contain_raw_prose(self) -> None:
        v1, v2 = self._paired()
        report = generate_comparison_report(self.cases, v1, v2)
        serialized = repr(report["disagreements"])
        for case in self.cases:
            self.assertNotIn(case.source_span, serialized)
        for item in report["disagreements"]:
            self.assertEqual(set(item), {
                "case_id",
                "case_fingerprint",
                "v1_recommendation",
                "v2_recommendation",
                "v1_reason_codes",
                "v2_reason_codes",
            })


if __name__ == "__main__":
    unittest.main()
