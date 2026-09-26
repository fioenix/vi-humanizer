from __future__ import annotations

import hashlib
import itertools
from dataclasses import dataclass, replace
from typing import Any

from guard_eval.config import canonical_json
from guard_eval.corpus import case_fingerprint
from guard_eval.models import (
    CheckStatus, DecisionPolicy, EditDecision, EvaluationCase, EvaluationRun,
    GuardAction, GuardDimension, JudgmentSet, NaturalnessReason, RunStatus, Split,
    to_jsonable,
)


class PolicyError(ValueError):
    """Raised when policy fitting or application inputs are not trustworthy."""


SELECTION_ORDER = [
    "need_to_edit_recall",
    "candidate_choice_accuracy",
    "unacceptable_candidate_replace_rate",
    "unnecessary_edit_rate",
    "valid_edit_false_block_rate",
    "safety_false_accept_rate",
    "review_rate",
    "conservative_thresholds",
]


@dataclass(frozen=True)
class PolicyDecision:
    edit_decision: EditDecision
    selected_candidate_id: str | None
    naturalness_positive: bool
    preference_choice: str | None
    candidate_guard_actions: dict[str, GuardAction]


def policy_version(policy: DecisionPolicy) -> str:
    data = to_jsonable(policy)
    semantic = {key: value for key, value in data.items() if key != "policy_version"}
    return "sha256:" + hashlib.sha256(canonical_json(semantic).encode("utf-8")).hexdigest()


def guard_action(judgment: JudgmentSet, candidate_id: str, policy: DecisionPolicy) -> GuardAction:
    scores = judgment.candidate_safety_scores[candidate_id]
    maximum = max(scores.values())
    if maximum >= policy.safety_reject_threshold:
        return GuardAction.REJECT
    if maximum >= policy.safety_review_threshold:
        return GuardAction.REVIEW
    return GuardAction.PASS


def _preference_is_confident(judgment: JudgmentSet, policy: DecisionPolicy) -> bool:
    probabilities = judgment.preference_probabilities or {}
    if judgment.preference_choice not in probabilities or judgment.preference_confidence is None:
        return False
    ordered = sorted(probabilities.values(), reverse=True)
    margin = ordered[0] - ordered[1] if len(ordered) > 1 else ordered[0]
    choice_is_top = probabilities[judgment.preference_choice] == ordered[0]
    return (
        choice_is_top
        and judgment.preference_confidence >= policy.preference_confidence_threshold
        and margin >= policy.preference_margin_threshold
    )


def apply_policy(case: EvaluationCase, judgment: JudgmentSet, policy: DecisionPolicy) -> PolicyDecision:
    candidate_ids = {candidate.candidate_id for candidate in case.candidates}
    if judgment.status is CheckStatus.UNCHECKED:
        return PolicyDecision(EditDecision.REVIEW, None, False, None, {})
    actions = {candidate_id: guard_action(judgment, candidate_id, policy) for candidate_id in sorted(candidate_ids)}
    positive = any(
        judgment.naturalness_scores[reason] >= policy.needs_edit_thresholds[reason]
        for reason in NaturalnessReason
    )
    confident = _preference_is_confident(judgment, policy)
    choice = judgment.preference_choice
    if not positive and confident and choice == "keep_original":
        return PolicyDecision(EditDecision.KEEP, None, positive, choice, actions)
    if positive and confident and isinstance(choice, str) and choice.startswith("candidate:"):
        candidate_id = choice.removeprefix("candidate:")
        if candidate_id in candidate_ids and actions[candidate_id] is GuardAction.PASS:
            return PolicyDecision(EditDecision.REPLACE, candidate_id, positive, choice, actions)
    return PolicyDecision(EditDecision.REVIEW, None, positive, choice, actions)


def _rate(numerator: int, denominator: int) -> float | None:
    return None if denominator == 0 else numerator / denominator


def _fit_metrics(cases: list[EvaluationCase], judgments: dict[str, JudgmentSet], policy: DecisionPolicy) -> dict[str, float | None]:
    results = {case.case_id: apply_policy(case, judgments[case.case_id], policy) for case in cases}
    need_cases = [case for case in cases if case.expected_needs_edit]
    no_need = [case for case in cases if not case.expected_needs_edit]
    replace_cases = [case for case in cases if case.expected_edit_decision is EditDecision.REPLACE]
    none_cases = [case for case in cases if case.expected_preferred_option == "none_of_candidates"]
    need_recall = _rate(sum(results[c.case_id].naturalness_positive for c in need_cases), len(need_cases))
    unnecessary = _rate(sum(results[c.case_id].edit_decision is not EditDecision.KEEP for c in no_need), len(no_need))
    choice_accuracy = _rate(sum(
        results[c.case_id].edit_decision is EditDecision.REPLACE
        and f"candidate:{results[c.case_id].selected_candidate_id}" == c.expected_preferred_option
        for c in replace_cases
    ), len(replace_cases))
    valid_total = valid_blocked = harmful_total = harmful_caught = 0
    false_accept_num = false_accept_den = 0
    for case in cases:
        result = results[case.case_id]
        for candidate in case.candidates:
            action = result.candidate_guard_actions[candidate.candidate_id]
            if candidate.expected_guard_action is GuardAction.PASS:
                valid_total += 1
                valid_blocked += action is not GuardAction.PASS
            if any(candidate.expected_dimensions.values()):
                harmful_total += 1
                harmful_caught += action is not GuardAction.PASS
        if result.edit_decision is EditDecision.REPLACE:
            false_accept_den += 1
            selected = next(item for item in case.candidates if item.candidate_id == result.selected_candidate_id)
            false_accept_num += selected.expected_guard_action is not GuardAction.PASS
    return {
        "need_to_edit_recall": need_recall,
        "candidate_choice_accuracy": choice_accuracy,
        "unacceptable_candidate_replace_rate": _rate(
            sum(results[c.case_id].edit_decision is EditDecision.REPLACE for c in none_cases), len(none_cases)
        ),
        "unnecessary_edit_rate": unnecessary,
        "valid_edit_false_block_rate": _rate(valid_blocked, valid_total),
        "safety_false_accept_rate": _rate(false_accept_num, false_accept_den),
        "harmful_edit_recall": _rate(harmful_caught, harmful_total),
        "review_rate": _rate(sum(result.edit_decision is EditDecision.REVIEW for result in results.values()), len(cases)),
    }


def _score(metrics: dict[str, float | None], policy: DecisionPolicy) -> tuple[Any, ...]:
    value = lambda name, default: default if metrics[name] is None else metrics[name]
    conservative = (
        sum(policy.needs_edit_thresholds.values()),
        policy.preference_confidence_threshold,
        policy.preference_margin_threshold,
        -policy.safety_review_threshold,
        -policy.safety_reject_threshold,
    )
    return (
        value("need_to_edit_recall", -1.0),
        value("candidate_choice_accuracy", -1.0),
        -value("unacceptable_candidate_replace_rate", 1.0),
        -value("unnecessary_edit_rate", 1.0),
        -value("valid_edit_false_block_rate", 1.0),
        -value("safety_false_accept_rate", 1.0),
        -value("review_rate", 1.0),
        conservative,
    )


def _observed(values: list[float]) -> list[float]:
    return sorted({0.0, 1.0, *[float(value) for value in values]})


def fit_policy(cases: list[EvaluationCase], run: EvaluationRun) -> DecisionPolicy:
    if run.split is not Split.DEV or run.run_status is not RunStatus.COMPLETE:
        raise PolicyError("policy can be fit only from a complete dev run")
    judgments = {item.case_id: item for item in run.judgments}
    if set(judgments) != {case.case_id for case in cases} or any(
        item.status is not CheckStatus.CHECKED or item.case_fingerprint != case_fingerprint(case)
        for case in cases for item in [judgments.get(case.case_id)] if item is not None
    ):
        raise PolicyError("dev run does not exactly match cases")
    if run.observed_models != [run.requested_model]:
        raise PolicyError("dev run has mixed or unexpected model versions")
    natural_values = {
        reason: _observed([item.naturalness_scores[reason] for item in run.judgments]) for reason in NaturalnessReason
    }
    confidences = _observed([item.preference_confidence for item in run.judgments])
    margins = _observed([
        sorted(item.preference_probabilities.values(), reverse=True)[0] - sorted(item.preference_probabilities.values(), reverse=True)[1]
        for item in run.judgments
    ])
    safety_values = _observed([
        score for item in run.judgments for scores in item.candidate_safety_scores.values() for score in scores.values()
    ])
    best: tuple[tuple[Any, ...], DecisionPolicy] | None = None
    for lexical, collocation, confidence, margin, review, reject in itertools.product(
        natural_values[NaturalnessReason.LEXICALLY_INCOMPLETE],
        natural_values[NaturalnessReason.UNNATURAL_COLLOCATION],
        confidences, margins, safety_values, safety_values,
    ):
        if review > reject:
            continue
        candidate = DecisionPolicy(
            policy_version=None, corpus_version_fitted=run.corpus_version,
            config_version=run.config_version, question_set_version=run.question_set_version,
            model_version=run.requested_model,
            needs_edit_thresholds={
                NaturalnessReason.LEXICALLY_INCOMPLETE: lexical,
                NaturalnessReason.UNNATURAL_COLLOCATION: collocation,
            },
            preference_confidence_threshold=confidence, preference_margin_threshold=margin,
            safety_review_threshold=review, safety_reject_threshold=reject,
            selection_order=SELECTION_ORDER, created_at=run.completed_at,
        )
        candidate.validate()
        ranked = _score(_fit_metrics(cases, judgments, candidate), candidate)
        if best is None or ranked > best[0]:
            best = (ranked, candidate)
    if best is None:
        raise PolicyError("no valid threshold combination")
    selected = best[1]
    return replace(selected, policy_version=policy_version(selected))


def load_policy(path: str) -> DecisionPolicy:
    import json
    from pathlib import Path

    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        policy = DecisionPolicy(
            policy_version=data["policy_version"], corpus_version_fitted=data["corpus_version_fitted"],
            config_version=data["config_version"], question_set_version=data["question_set_version"],
            model_version=data["model_version"],
            needs_edit_thresholds={NaturalnessReason(key): value for key, value in data["needs_edit_thresholds"].items()},
            preference_confidence_threshold=data["preference_confidence_threshold"],
            preference_margin_threshold=data["preference_margin_threshold"],
            safety_review_threshold=data["safety_review_threshold"], safety_reject_threshold=data["safety_reject_threshold"],
            selection_order=list(data["selection_order"]), created_at=data["created_at"],
        )
        policy.validate()
    except (OSError, KeyError, TypeError, ValueError) as exc:
        raise PolicyError(f"invalid policy: {type(exc).__name__}") from exc
    if policy.policy_version != policy_version(policy):
        raise PolicyError("policy digest mismatch")
    return policy
