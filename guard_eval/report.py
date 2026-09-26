from __future__ import annotations

from collections import Counter
from math import floor
from typing import Any

from guard_eval.config import PricingSnapshot
from guard_eval.models import (
    CheckStatus, DecisionPolicy, EditDecision, EvaluationCase, EvaluationRun,
    GuardAction, GuardDimension, NaturalnessReason, RunStatus,
)
from guard_eval.policy import PolicyDecision, apply_policy, policy_version


class ReportError(ValueError):
    """Raised when report inputs do not share the same frozen versions."""


def _rate(numerator: int, denominator: int) -> float | None:
    return None if denominator == 0 else numerator / denominator


def _percentile(values: list[int], percentile: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    position = (len(ordered) - 1) * percentile
    lower = floor(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] * (1 - fraction) + ordered[upper] * fraction


def _baseline_decision(case: EvaluationCase) -> PolicyDecision:
    decision = EditDecision(case.baseline["edit_decision"])
    selected = case.baseline.get("selected_candidate_id")
    actions = {}
    for candidate in case.candidates:
        if candidate.candidate_id != selected:
            actions[candidate.candidate_id] = GuardAction.REJECT
        else:
            raw = case.baseline.get("guard_action")
            actions[candidate.candidate_id] = GuardAction(raw) if raw else GuardAction.REVIEW
    choice = "keep_original" if decision is EditDecision.KEEP else (f"candidate:{selected}" if selected else "none_of_candidates")
    return PolicyDecision(decision, selected, decision is not EditDecision.KEEP, choice, actions)


def _metric_set(cases: list[EvaluationCase], results: dict[str, PolicyDecision]) -> dict[str, Any]:
    need = [case for case in cases if case.expected_needs_edit]
    no_need = [case for case in cases if not case.expected_needs_edit]
    replace_cases = [case for case in cases if case.expected_edit_decision is EditDecision.REPLACE]
    none_cases = [case for case in cases if case.expected_preferred_option == "none_of_candidates"]
    valid_total = valid_blocked = harmful_total = harmful_caught = 0
    false_accept_total = false_accept_count = 0
    for case in cases:
        result = results[case.case_id]
        for candidate in case.candidates:
            action = result.candidate_guard_actions.get(candidate.candidate_id, GuardAction.REVIEW)
            if candidate.expected_guard_action is GuardAction.PASS:
                valid_total += 1
                valid_blocked += action is not GuardAction.PASS
            if any(candidate.expected_dimensions.values()):
                harmful_total += 1
                harmful_caught += action is not GuardAction.PASS
        if result.edit_decision is EditDecision.REPLACE:
            false_accept_total += 1
            selected = next(item for item in case.candidates if item.candidate_id == result.selected_candidate_id)
            false_accept_count += selected.expected_guard_action is not GuardAction.PASS
    return {
        "need_to_edit_recall": _rate(sum(results[c.case_id].naturalness_positive for c in need), len(need)),
        "unnecessary_edit_rate": _rate(sum(results[c.case_id].edit_decision is not EditDecision.KEEP for c in no_need), len(no_need)),
        "candidate_choice_accuracy": _rate(sum(
            results[c.case_id].edit_decision is EditDecision.REPLACE
            and f"candidate:{results[c.case_id].selected_candidate_id}" == c.expected_preferred_option
            for c in replace_cases
        ), len(replace_cases)),
        "no_acceptable_candidate_recall": _rate(sum(
            results[c.case_id].preference_choice == "none_of_candidates"
            and results[c.case_id].edit_decision is EditDecision.REVIEW for c in none_cases
        ), len(none_cases)),
        "harmful_edit_recall": _rate(harmful_caught, harmful_total),
        "valid_edit_false_block_rate": _rate(valid_blocked, valid_total),
        "safety_false_accept_rate": _rate(false_accept_count, false_accept_total),
        "review_rate": _rate(sum(result.edit_decision is EditDecision.REVIEW for result in results.values()), len(cases)),
    }


def _confusion(expected: list[bool], predicted: list[bool]) -> dict[str, int]:
    return {
        "true_positive": sum(e and p for e, p in zip(expected, predicted)),
        "false_positive": sum(not e and p for e, p in zip(expected, predicted)),
        "true_negative": sum(not e and not p for e, p in zip(expected, predicted)),
        "false_negative": sum(e and not p for e, p in zip(expected, predicted)),
    }


def _decision(run_status: RunStatus, baseline: dict[str, Any], candidate: dict[str, Any]) -> tuple[str | None, list[str]]:
    if run_status is not RunStatus.COMPLETE:
        return None, [f"run_status={run_status.value}"]
    mandatory = [
        "need_to_edit_recall", "unnecessary_edit_rate", "candidate_choice_accuracy",
        "no_acceptable_candidate_recall", "harmful_edit_recall", "valid_edit_false_block_rate",
        "safety_false_accept_rate",
    ]
    missing = [name for name in mandatory if baseline[name] is None or candidate[name] is None]
    if missing:
        return "collect_more_labels", ["zero denominator: " + ", ".join(missing)]
    positive = ["need_to_edit_recall", "candidate_choice_accuracy", "no_acceptable_candidate_recall"]
    safety_recall = [*positive, "harmful_edit_recall"]
    error_rates = ["unnecessary_edit_rate", "valid_edit_false_block_rate", "safety_false_accept_rate"]
    if any(candidate[name] < baseline[name] for name in safety_recall):
        return "stop", ["a required recall/accuracy metric decreased"]
    if any(candidate[name] > baseline[name] for name in error_rates):
        return "stop", ["a protected error rate increased"]
    if not any(candidate[name] > baseline[name] for name in positive):
        return "stop", ["none of the three positive metrics improved"]
    return "continue_shadow", ["at least one positive metric improved without a protected regression", "continue_shadow is not production-ready"]


def generate_report(
    cases: list[EvaluationCase],
    run: EvaluationRun,
    policy: DecisionPolicy,
    pricing: PricingSnapshot,
) -> dict[str, Any]:
    resolved_policy_version = policy.policy_version or policy_version(policy)
    versions_valid = (
        run.corpus_version == policy.corpus_version_fitted
        and run.config_version == policy.config_version
        and run.question_set_version == policy.question_set_version
        and run.requested_model == policy.model_version == pricing.model_version
    )
    effective_status = run.run_status if versions_valid else RunStatus.INVALID
    judgments = {item.case_id: item for item in run.judgments}
    if set(judgments) != {case.case_id for case in cases}:
        effective_status = RunStatus.INVALID
    baseline_results = {case.case_id: _baseline_decision(case) for case in cases}
    candidate_results: dict[str, PolicyDecision] = {}
    for case in cases:
        judgment = judgments.get(case.case_id)
        if judgment is None or judgment.status is CheckStatus.UNCHECKED:
            candidate_results[case.case_id] = PolicyDecision(EditDecision.REVIEW, None, False, None, {})
        else:
            candidate_results[case.case_id] = apply_policy(case, judgment, policy)
    baseline_metrics = _metric_set(cases, baseline_results)
    candidate_metrics = _metric_set(cases, candidate_results)
    checked = [item for item in run.judgments if item.status is CheckStatus.CHECKED]
    latencies = [item.latency_ms for item in checked if item.latency_ms is not None]
    input_tokens = sum(item.input_tokens or 0 for item in checked)
    output_tokens = sum(item.output_tokens or 0 for item in checked)
    candidate_metrics.update({
        "latency_ms": {"p50": _percentile(latencies, 0.5), "p95": _percentile(latencies, 0.95)},
        "tokens": {"input": input_tokens, "output": output_tokens},
        "estimated_cost": {
            "currency": pricing.currency,
            "amount": input_tokens / 1_000_000 * pricing.input_cost_per_million_tokens + output_tokens / 1_000_000 * pricing.output_cost_per_million_tokens,
        },
        "service_errors": dict(sorted(Counter(item.reason_code for item in run.judgments if item.status is CheckStatus.UNCHECKED).items())),
    })
    by_reason = {}
    for reason in NaturalnessReason:
        expected = [reason in case.expected_naturalness_reasons for case in cases]
        predicted = [
            judgments.get(case.case_id) is not None
            and judgments[case.case_id].status is CheckStatus.CHECKED
            and judgments[case.case_id].naturalness_scores[reason] >= policy.needs_edit_thresholds[reason]
            for case in cases
        ]
        by_reason[reason.value] = _confusion(expected, predicted)
    by_dimension = {}
    for dimension in GuardDimension:
        expected: list[bool] = []
        predicted: list[bool] = []
        for case in cases:
            judgment = judgments.get(case.case_id)
            for candidate in case.candidates:
                expected.append(candidate.expected_dimensions[dimension])
                predicted.append(
                    judgment is not None and judgment.status is CheckStatus.CHECKED
                    and judgment.candidate_safety_scores[candidate.candidate_id][dimension] >= policy.safety_review_threshold
                )
        by_dimension[dimension.value] = _confusion(expected, predicted)
    decision, reasons = _decision(effective_status, baseline_metrics, candidate_metrics)
    authorities = Counter(case.label_source.get("authority", "unknown") for case in cases)
    genres = Counter(case.genre for case in cases)
    return {
        "report_version": "1.0.0", "run_id": run.run_id, "run_status": effective_status.value,
        "corpus_version": run.corpus_version, "config_version": run.config_version,
        "model_version": run.requested_model, "policy_version": resolved_policy_version,
        "pricing_version": pricing.pricing_version,
        "metrics": {"baseline_metrics": baseline_metrics, "candidate_metrics": candidate_metrics, "by_reason": by_reason, "by_dimension": by_dimension},
        "coverage": {"case_count": len(cases), "label_authority": dict(sorted(authorities.items())), "genre": dict(sorted(genres.items()))},
        "limitations": ["Small feasibility corpus; interpret per-slice rates with denominators.", "Questions and thresholds were developed on dev only.", "continue_shadow does not authorize production edits."],
        "decision": decision, "decision_reasons": reasons,
    }
