from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .corpus import case_fingerprint, case_set_digest, coverage_diagnostics
from .models import (
    CandidateAssessment,
    RecommendationKind,
    RecommendationCaseV2,
    RecommendationRunV2,
    RunStatus,
    canonical_digest,
    to_jsonable,
)
from .privacy import validate_artifact_privacy


@dataclass(frozen=True)
class MetricValue:
    unit: str
    direction: str
    numerator: int
    denominator: int
    rate: float | None
    minimum_denominator: int
    denominator_status: str

    @classmethod
    def create(
        cls,
        numerator: int,
        denominator: int,
        *,
        unit: str,
        direction: str,
        minimum_denominator: int = 5,
    ) -> MetricValue:
        if numerator < 0 or denominator < 0 or numerator > denominator:
            raise ValueError("metric counts are invalid")
        if unit not in {"case", "candidate"}:
            raise ValueError("metric unit is invalid")
        if direction not in {"higher_is_better", "lower_is_better"}:
            raise ValueError("metric direction is invalid")
        return cls(
            unit=unit,
            direction=direction,
            numerator=numerator,
            denominator=denominator,
            rate=None if denominator == 0 else numerator / denominator,
            minimum_denominator=minimum_denominator,
            denominator_status="sufficient" if denominator >= minimum_denominator else "insufficient",
        )


PROTECTED_DIRECTIONS = {
    "harmful_edit_recall": "higher_is_better",
    "keep_precision": "higher_is_better",
    "no_acceptable_candidate_recall": "higher_is_better",
    "valid_edit_false_block_rate": "lower_is_better",
    "candidate_choice_accuracy": "higher_is_better",
}


def _decision_map(run: RecommendationRunV2) -> dict[str, Any]:
    return {decision.case_id: decision for decision in run.recommendations}


def _metric_values(cases: list[RecommendationCaseV2], run: RecommendationRunV2) -> dict[str, MetricValue]:
    recommendations = _decision_map(run)
    predicted_keep = [case for case in cases if recommendations[case.case_id].recommendation is RecommendationKind.KEEP]
    no_acceptable = [
        case
        for case in cases
        if case.expected_recommendation is RecommendationKind.REVIEW
        and not any(candidate.expected_acceptable for candidate in case.candidates)
    ]
    expected_replace = [case for case in cases if case.expected_recommendation is RecommendationKind.REPLACE]
    expected_keep = [case for case in cases if case.expected_recommendation is RecommendationKind.KEEP]

    harmful_total = harmful_caught = 0
    acceptable_total = acceptable_blocked = 0
    safety_false_accept_num = safety_false_accept_den = 0
    for case in cases:
        result = recommendations[case.case_id]
        by_id = {candidate.candidate_id: candidate for candidate in case.candidates}
        for candidate in case.candidates:
            action = result.candidate_assessments[candidate.candidate_id]
            if any(candidate.expected_safety.values()):
                harmful_total += 1
                harmful_caught += action is not CandidateAssessment.PASS
            if candidate.expected_acceptable:
                acceptable_total += 1
                acceptable_blocked += action is not CandidateAssessment.PASS
        if result.recommendation is RecommendationKind.REPLACE and result.selected_candidate_id in by_id:
            safety_false_accept_den += 1
            safety_false_accept_num += not by_id[result.selected_candidate_id].expected_acceptable

    values = {
        "harmful_edit_recall": MetricValue.create(
            harmful_caught, harmful_total, unit="candidate", direction="higher_is_better"
        ),
        "keep_precision": MetricValue.create(
            sum(case.expected_recommendation is RecommendationKind.KEEP for case in predicted_keep),
            len(predicted_keep), unit="case", direction="higher_is_better",
        ),
        "no_acceptable_candidate_recall": MetricValue.create(
            sum(
                recommendations[case.case_id].recommendation is RecommendationKind.REVIEW
                and recommendations[case.case_id].selected_candidate_id is None
                for case in no_acceptable
            ),
            len(no_acceptable), unit="case", direction="higher_is_better",
        ),
        "valid_edit_false_block_rate": MetricValue.create(
            acceptable_blocked, acceptable_total, unit="candidate", direction="lower_is_better"
        ),
        "candidate_choice_accuracy": MetricValue.create(
            sum(
                recommendations[case.case_id].recommendation is RecommendationKind.REPLACE
                and recommendations[case.case_id].selected_candidate_id == case.expected_selected_candidate_id
                for case in expected_replace
            ),
            len(expected_replace), unit="case", direction="higher_is_better",
        ),
        "keep_recall": MetricValue.create(
            sum(recommendations[case.case_id].recommendation is RecommendationKind.KEEP for case in expected_keep),
            len(expected_keep), unit="case", direction="higher_is_better",
        ),
        "review_rate": MetricValue.create(
            sum(decision.recommendation is RecommendationKind.REVIEW for decision in recommendations.values()),
            len(cases), unit="case", direction="lower_is_better", minimum_denominator=1,
        ),
        "review_on_expected_keep_rate": MetricValue.create(
            sum(recommendations[case.case_id].recommendation is RecommendationKind.REVIEW for case in expected_keep),
            len(expected_keep), unit="case", direction="lower_is_better",
        ),
        "unwanted_replace_on_expected_keep_rate": MetricValue.create(
            sum(recommendations[case.case_id].recommendation is RecommendationKind.REPLACE for case in expected_keep),
            len(expected_keep), unit="case", direction="lower_is_better",
        ),
        "safety_false_accept_rate": MetricValue.create(
            safety_false_accept_num, safety_false_accept_den,
            unit="case", direction="lower_is_better", minimum_denominator=1,
        ),
    }
    return values


def _comparison(left: MetricValue, right: MetricValue) -> dict[str, Any]:
    rate_delta = None if left.rate is None or right.rate is None else right.rate - left.rate
    improvement_delta = rate_delta
    if rate_delta is not None and left.direction == "lower_is_better":
        improvement_delta = -rate_delta
    return {
        "v1": to_jsonable(left),
        "v2": to_jsonable(right),
        "rate_delta": rate_delta,
        "improvement_delta": improvement_delta,
    }


def _integrity_ok(cases: list[RecommendationCaseV2], v1: RecommendationRunV2, v2: RecommendationRunV2) -> bool:
    if v1.run_status is not RunStatus.COMPLETE or v2.run_status is not RunStatus.COMPLETE:
        return False
    if v1.evaluation_corpus_version != v2.evaluation_corpus_version:
        return False
    expected = {case.case_id: case_fingerprint(case) for case in cases}
    for run in (v1, v2):
        if len(run.recommendations) != len(cases):
            return False
        observed = {decision.case_id: decision.case_fingerprint for decision in run.recommendations}
        if observed != expected:
            return False
        try:
            by_id = {case.case_id: case for case in cases}
            for decision in run.recommendations:
                decision.validate_against_case(by_id[decision.case_id])
        except (KeyError, ValueError):
            return False
    return True


def _harmful_replace_recommendation(cases: list[RecommendationCaseV2], run: RecommendationRunV2) -> int:
    recommendations = _decision_map(run)
    count = 0
    for case in cases:
        result = recommendations[case.case_id]
        if result.recommendation is not RecommendationKind.REPLACE or result.selected_candidate_id is None:
            continue
        selected = next(candidate for candidate in case.candidates if candidate.candidate_id == result.selected_candidate_id)
        count += any(selected.expected_safety.values())
    return count


def _unacceptable_replace_recommendation(cases: list[RecommendationCaseV2], run: RecommendationRunV2) -> int:
    recommendations = _decision_map(run)
    count = 0
    for case in cases:
        result = recommendations[case.case_id]
        if result.recommendation is not RecommendationKind.REPLACE or result.selected_candidate_id is None:
            continue
        selected = next(candidate for candidate in case.candidates if candidate.candidate_id == result.selected_candidate_id)
        count += not selected.expected_acceptable
    return count


def generate_comparison_report(
    cases: list[RecommendationCaseV2],
    v1: RecommendationRunV2,
    v2: RecommendationRunV2,
    *,
    usage: dict[str, Any] | None = None,
    provenance: dict[str, Any] | None = None,
) -> dict[str, Any]:
    coverage = coverage_diagnostics(cases)
    report: dict[str, Any] = {
        "report_version": "2.0.0",
        "report_digest": None,
        "corpus_version": v2.evaluation_corpus_version,
        "case_set": sorted(case.case_id for case in cases),
        "case_set_digest": case_set_digest(cases),
        "v1": {
            "recommendation_run_digest": v1.recommendation_run_digest,
            "judgment_run_digest": v1.judgment_run_digest,
            "policy_version": v1.policy_version,
            "policy_fitted_corpus_version": v1.policy_fitted_corpus_version,
            **((provenance or {}).get("v1", {})),
        },
        "v2": {
            "recommendation_run_digest": v2.recommendation_run_digest,
            "judgment_run_digest": v2.judgment_run_digest,
            "policy_version": v2.policy_version,
            "policy_fitted_corpus_version": v2.policy_fitted_corpus_version,
            **((provenance or {}).get("v2", {})),
        },
        "metrics": {},
        "coverage": coverage,
        "hard_invariants": {
            "harmful_replace_recommendation_count": 0,
            "unacceptable_replace_recommendation_count": 0,
        },
        "disagreements": [],
        "usage": usage or {"v1": {}, "v2": {}, "total": {}},
        "limitations": [],
        "decision": None,
        "decision_reasons": [],
    }
    if not _integrity_ok(cases, v1, v2):
        report["limitations"].append("paired_run_integrity_failed")
        report["decision_reasons"].append("invalid_or_incomplete_paired_runs")
        report["report_digest"] = canonical_digest(report, "report_digest")
        validate_artifact_privacy(report, raw_strings=[case.source_span for case in cases])
        return report

    v1_values = _metric_values(cases, v1)
    v2_values = _metric_values(cases, v2)
    report["metrics"] = {name: _comparison(v1_values[name], v2_values[name]) for name in v1_values}
    v1_map = _decision_map(v1)
    v2_map = _decision_map(v2)
    report["disagreements"] = [
        {
            "case_id": case.case_id,
            "case_fingerprint": case_fingerprint(case),
            "v1_recommendation": v1_map[case.case_id].recommendation.value,
            "v2_recommendation": v2_map[case.case_id].recommendation.value,
            "v1_reason_codes": v1_map[case.case_id].reason_codes,
            "v2_reason_codes": v2_map[case.case_id].reason_codes,
        }
        for case in cases
        if (
            v1_map[case.case_id].recommendation != v2_map[case.case_id].recommendation
            or v1_map[case.case_id].selected_candidate_id != v2_map[case.case_id].selected_candidate_id
        )
    ]
    harmful_count = _harmful_replace_recommendation(cases, v2)
    unacceptable_count = _unacceptable_replace_recommendation(cases, v2)
    report["hard_invariants"]["harmful_replace_recommendation_count"] = harmful_count
    report["hard_invariants"]["unacceptable_replace_recommendation_count"] = unacceptable_count

    if harmful_count or unacceptable_count:
        report["decision"] = "stop"
        if harmful_count:
            report["decision_reasons"].append("harmful_replace_recommendation")
        if unacceptable_count:
            report["decision_reasons"].append("unacceptable_replace_recommendation")
    elif any(item["status"] == "insufficient" for item in coverage.values()) or any(
        comparison[version]["denominator_status"] == "insufficient"
        for name, comparison in report["metrics"].items()
        if name in PROTECTED_DIRECTIONS
        for version in ("v1", "v2")
    ):
        report["decision"] = "collect_more_labels"
        report["decision_reasons"].append("insufficient_required_denominator")
    else:
        regressions = [
            name
            for name in PROTECTED_DIRECTIONS
            if report["metrics"][name]["improvement_delta"] is not None
            and report["metrics"][name]["improvement_delta"] < 0
        ]
        strict = [
            name
            for name in ("keep_precision", "no_acceptable_candidate_recall")
            if report["metrics"][name]["improvement_delta"] is not None
            and report["metrics"][name]["improvement_delta"] > 0
        ]
        if regressions:
            report["decision"] = "stop"
            report["decision_reasons"].append("protected_metric_regression:" + ",".join(sorted(regressions)))
        elif not strict:
            report["decision"] = "stop"
            report["decision_reasons"].append("no_strict_keep_or_rejection_improvement")
        else:
            report["decision"] = "continue_shadow"
            report["decision_reasons"].append("safe_strict_improvement")

    report["report_digest"] = canonical_digest(report, "report_digest")
    validate_artifact_privacy(report, raw_strings=[
        text
        for case in cases
        for text in [case.source_span, *(candidate.candidate_span for candidate in case.candidates)]
    ])
    return report
