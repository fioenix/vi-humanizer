from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from typing import Any

from .models import (
    AbsoluteJudgmentV2,
    CandidateAssessment,
    CandidateComponent,
    CaseJudgmentV2,
    CheckStatus,
    RecommendationKind,
    RecommendationCaseV2,
    RecommendationRunV2,
    JudgmentRunV2,
    PolicyRecommendationV2,
    SafetyDimension,
    SourceIssue,
    RunStatus,
    ValidationError,
    canonical_digest,
    recommendation_run_digest,
    to_jsonable,
    validate_digest,
    validate_probability,
)
from .corpus import case_fingerprint, case_set_digest


class PolicyError(ValueError):
    """Raised when policy inputs cannot support deterministic replay."""


SELECTION_ORDER = [
    "no_harmful_or_unacceptable_replace",
    "recommendation_accuracy",
    "selected_candidate_accuracy",
    "signal_accuracy",
    "fewer_reviews",
    "wider_signal_separation",
    "ranking_route_accuracy",
    "stricter_ranking_thresholds",
]


@dataclass
class RecommendationPolicyV2:
    policy_version: str | None
    pipeline_version: str
    fitted_corpus_version: str
    config_version: str
    absolute_question_set_version: str
    ranking_question_set_version: str
    model_version: str
    context_threshold: float
    source_issue_negative_thresholds: dict[SourceIssue, float]
    source_issue_positive_thresholds: dict[SourceIssue, float]
    candidate_component_negative_thresholds: dict[CandidateComponent, float]
    candidate_component_positive_thresholds: dict[CandidateComponent, float]
    safety_review_thresholds: dict[SafetyDimension, float]
    safety_reject_thresholds: dict[SafetyDimension, float]
    ranking_confidence_threshold: float
    ranking_margin_threshold: float
    selection_order: list[str]
    created_at: str

    @classmethod
    def conservative_fixture(
        cls,
        *,
        fitted_corpus_version: str,
        config_version: str,
        absolute_question_set_version: str,
        ranking_question_set_version: str,
        model_version: str,
    ) -> RecommendationPolicyV2:
        return cls(
            policy_version=None,
            pipeline_version="v2",
            fitted_corpus_version=fitted_corpus_version,
            config_version=config_version,
            absolute_question_set_version=absolute_question_set_version,
            ranking_question_set_version=ranking_question_set_version,
            model_version=model_version,
            context_threshold=0.7,
            source_issue_negative_thresholds={key: 0.3 for key in SourceIssue},
            source_issue_positive_thresholds={key: 0.7 for key in SourceIssue},
            candidate_component_negative_thresholds={key: 0.3 for key in CandidateComponent},
            candidate_component_positive_thresholds={key: 0.7 for key in CandidateComponent},
            safety_review_thresholds={key: 0.3 for key in SafetyDimension},
            safety_reject_thresholds={key: 0.7 for key in SafetyDimension},
            ranking_confidence_threshold=0.7,
            ranking_margin_threshold=0.2,
            selection_order=list(SELECTION_ORDER),
            created_at=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        )

    def validate(self) -> None:
        if self.pipeline_version != "v2":
            raise ValidationError("v2 policy pipeline_version must be v2")
        for name in (
            "fitted_corpus_version", "config_version", "absolute_question_set_version",
            "ranking_question_set_version",
        ):
            validate_digest(getattr(self, name), name)
        validate_digest(self.policy_version, "policy_version", nullable=True)
        validate_probability(self.context_threshold, "context_threshold")
        paired = (
            (self.source_issue_negative_thresholds, self.source_issue_positive_thresholds, set(SourceIssue)),
            (self.candidate_component_negative_thresholds, self.candidate_component_positive_thresholds, set(CandidateComponent)),
            (self.safety_review_thresholds, self.safety_reject_thresholds, set(SafetyDimension)),
        )
        for low, high, expected in paired:
            if set(low) != expected or set(high) != expected:
                raise ValidationError("policy threshold keys do not match contract")
            for key in expected:
                validate_probability(low[key], f"{key.value}:low")
                validate_probability(high[key], f"{key.value}:high")
                if low[key] > high[key]:
                    raise ValidationError("negative/review threshold cannot exceed positive/reject threshold")
        validate_probability(self.ranking_confidence_threshold, "ranking_confidence_threshold")
        validate_probability(self.ranking_margin_threshold, "ranking_margin_threshold")
        if self.selection_order != SELECTION_ORDER:
            raise ValidationError("policy selection_order does not match the fitter contract")


def policy_version(policy: RecommendationPolicyV2) -> str:
    return canonical_digest(to_jsonable(policy), "policy_version")


def safety_assessment(absolute: AbsoluteJudgmentV2, candidate_id: str, policy: RecommendationPolicyV2) -> CandidateAssessment:
    scores = (absolute.candidate_safety_scores or {})[candidate_id]
    if any(scores[key] >= policy.safety_reject_thresholds[key] for key in SafetyDimension):
        return CandidateAssessment.REJECT
    if any(scores[key] > policy.safety_review_thresholds[key] for key in SafetyDimension):
        return CandidateAssessment.REVIEW
    return CandidateAssessment.PASS


def candidate_assessment(absolute: AbsoluteJudgmentV2, candidate_id: str, policy: RecommendationPolicyV2) -> CandidateAssessment:
    safety = safety_assessment(absolute, candidate_id, policy)
    if safety is not CandidateAssessment.PASS:
        return safety
    scores = (absolute.candidate_component_scores or {})[candidate_id]
    if any(scores[key] <= policy.candidate_component_negative_thresholds[key] for key in CandidateComponent):
        return CandidateAssessment.REJECT
    if any(scores[key] < policy.candidate_component_positive_thresholds[key] for key in CandidateComponent):
        return CandidateAssessment.REVIEW
    return CandidateAssessment.PASS


def eligible_candidate_ids(case: RecommendationCaseV2, absolute: AbsoluteJudgmentV2, policy: RecommendationPolicyV2) -> list[str]:
    if absolute.status is not CheckStatus.CHECKED:
        return []
    if _source_state(absolute, policy) != "needs_edit":
        return []
    eligible: list[str] = []
    for candidate in sorted(case.candidates, key=lambda item: item.candidate_id):
        candidate_id = candidate.candidate_id
        components = (absolute.candidate_component_scores or {}).get(candidate_id, {})
        if set(components) != set(CandidateComponent):
            continue
        if candidate_assessment(absolute, candidate_id, policy) is not CandidateAssessment.PASS:
            continue
        eligible.append(candidate_id)
    return eligible


def _source_state(absolute: AbsoluteJudgmentV2, policy: RecommendationPolicyV2) -> str:
    if absolute.source_context_sufficient is None or absolute.source_context_sufficient < policy.context_threshold:
        return "insufficient_context"
    scores = absolute.source_issue_scores or {}
    if set(scores) != set(SourceIssue):
        return "source_signal_conflict"
    if any(
        policy.source_issue_negative_thresholds[key] < scores[key] < policy.source_issue_positive_thresholds[key]
        for key in SourceIssue
    ):
        return "source_signal_uncertain"
    if any(scores[key] >= policy.source_issue_positive_thresholds[key] for key in SourceIssue):
        return "needs_edit"
    if all(scores[key] <= policy.source_issue_negative_thresholds[key] for key in SourceIssue):
        return "source_already_sufficient"
    return "source_signal_conflict"


def apply_policy(case: RecommendationCaseV2, judgment: CaseJudgmentV2, policy: RecommendationPolicyV2) -> PolicyRecommendationV2:
    policy.validate()
    absolute = judgment.absolute
    if absolute.status is CheckStatus.UNCHECKED:
        return PolicyRecommendationV2(
            case.case_id, absolute.case_fingerprint, RecommendationKind.REVIEW, None,
            ["service_unchecked"], {}, [],
        )
    assessments = {
        candidate.candidate_id: candidate_assessment(absolute, candidate.candidate_id, policy)
        for candidate in sorted(case.candidates, key=lambda item: item.candidate_id)
    }
    source_state = _source_state(absolute, policy)
    if source_state != "needs_edit":
        recommendation = RecommendationKind.KEEP if source_state == "source_already_sufficient" else RecommendationKind.REVIEW
        return PolicyRecommendationV2(
            case.case_id, absolute.case_fingerprint, recommendation, None,
            [source_state], assessments, [],
        )
    eligible = eligible_candidate_ids(case, absolute, policy)
    if not eligible:
        return PolicyRecommendationV2(
            case.case_id, absolute.case_fingerprint, RecommendationKind.REVIEW, None,
            ["no_acceptable_candidate"], assessments, [],
        )
    if len(eligible) == 1:
        return PolicyRecommendationV2(
            case.case_id, absolute.case_fingerprint, RecommendationKind.REPLACE, eligible[0],
            ["single_acceptable_candidate"], assessments, eligible,
        )
    ranking = judgment.ranking
    if (
        ranking is None
        or ranking.status is not CheckStatus.CHECKED
        or ranking.eligible_candidate_ids != eligible
        or set(ranking.probabilities) != set(eligible)
    ):
        return PolicyRecommendationV2(
            case.case_id, absolute.case_fingerprint, RecommendationKind.REVIEW, None,
            ["ranking_uncertain"], assessments, eligible,
        )
    ordered = sorted(ranking.probabilities.values(), reverse=True)
    margin = ordered[0] - ordered[1]
    winner_is_top = ranking.probabilities.get(ranking.choice) == ordered[0]
    if (
        not winner_is_top
        or ranking.confidence < policy.ranking_confidence_threshold
        or margin < policy.ranking_margin_threshold
    ):
        return PolicyRecommendationV2(
            case.case_id, absolute.case_fingerprint, RecommendationKind.REVIEW, None,
            ["ranking_uncertain"], assessments, eligible,
        )
    return PolicyRecommendationV2(
        case.case_id, absolute.case_fingerprint, RecommendationKind.REPLACE, ranking.choice,
        ["ranked_candidate_selected"], assessments, eligible,
    )


def fit_policy(cases: list[RecommendationCaseV2], run: Any) -> RecommendationPolicyV2:
    """Fit a conservative observed-value policy from complete dev judgments.

    This iteration intentionally fits absolute thresholds first. Ranking evidence
    is collected only after this policy has produced one final shortlist per case.
    """
    if str(run.split) not in {"dev", "Split.DEV"} or run.run_status.value != "complete":
        raise PolicyError("policy can be fit only from a complete dev run")
    if len(run.judgments) != len(cases):
        raise PolicyError("dev run does not cover every case")
    by_id = {case.case_id: case for case in cases}
    if set(by_id) != {item.absolute.case_id for item in run.judgments}:
        raise PolicyError("dev run case ids do not match corpus")
    if run.case_set_digest != case_set_digest(cases) or any(
        item.absolute.case_fingerprint != case_fingerprint(by_id[item.absolute.case_id])
        for item in run.judgments
    ):
        raise PolicyError("dev run fingerprints do not match corpus")

    def band(observations: list[tuple[float, bool]], name: str) -> tuple[float, float]:
        positives = [score for score, label in observations if label]
        negatives = [score for score, label in observations if not label]
        if not positives or not negatives:
            raise PolicyError(f"{name} needs positive and negative dev labels")
        values = sorted({0.0, 1.0, *(score for score, _ in observations)})
        best: tuple[tuple[int, int, float], tuple[float, float]] | None = None
        for low in values:
            for high in values:
                if low >= high:
                    continue
                correct = sum((not label and score <= low) or (label and score >= high) for score, label in observations)
                review = sum(low < score < high for score, _ in observations)
                rank = (correct, -review, high - low)
                if best is None or rank > best[0]:
                    best = (rank, (low, high))
        assert best is not None
        return best[1]

    source_bands = {
        issue: band([
            (item.absolute.source_issue_scores[issue], by_id[item.absolute.case_id].expected_source_issues[issue])
            for item in run.judgments
        ], issue.value)
        for issue in SourceIssue
    }
    component_bands = {
        component: band([
            (
                item.absolute.candidate_component_scores[candidate.candidate_id][component],
                candidate.expected_components[component],
            )
            for item in run.judgments
            for candidate in by_id[item.absolute.case_id].candidates
        ], component.value)
        for component in CandidateComponent
    }
    safety_bands = {
        dimension: band([
            (
                item.absolute.candidate_safety_scores[candidate.candidate_id][dimension],
                candidate.expected_safety[dimension],
            )
            for item in run.judgments
            for candidate in by_id[item.absolute.case_id].candidates
        ], dimension.value)
        for dimension in SafetyDimension
    }
    context_scores = [item.absolute.source_context_sufficient for item in run.judgments]
    if any(score is None for score in context_scores):
        raise PolicyError("dev run is missing context sufficiency scores")
    policy = RecommendationPolicyV2(
        policy_version=None,
        pipeline_version="v2",
        fitted_corpus_version=run.corpus_version,
        config_version=run.config_version,
        absolute_question_set_version=run.absolute_question_set_version,
        ranking_question_set_version=run.ranking_question_set_version,
        model_version=run.requested_model,
        context_threshold=min(float(score) for score in context_scores if score is not None),
        source_issue_negative_thresholds={key: value[0] for key, value in source_bands.items()},
        source_issue_positive_thresholds={key: value[1] for key, value in source_bands.items()},
        candidate_component_negative_thresholds={key: value[0] for key, value in component_bands.items()},
        candidate_component_positive_thresholds={key: value[1] for key, value in component_bands.items()},
        safety_review_thresholds={key: value[0] for key, value in safety_bands.items()},
        safety_reject_thresholds={key: value[1] for key, value in safety_bands.items()},
        ranking_confidence_threshold=1.0,
        ranking_margin_threshold=1.0,
        selection_order=list(SELECTION_ORDER),
        created_at=run.completed_at,
    )
    policy.validate()

    judgments = {item.absolute.case_id: item for item in run.judgments}

    def unsafe_replacements(candidate_policy: RecommendationPolicyV2) -> list[tuple[RecommendationCaseV2, Any, Any]]:
        violations = []
        for case in cases:
            result = apply_policy(case, judgments[case.case_id], candidate_policy)
            if result.recommendation is not RecommendationKind.REPLACE:
                continue
            selected = next(
                candidate for candidate in case.candidates
                if candidate.candidate_id == result.selected_candidate_id
            )
            if not selected.expected_acceptable or any(selected.expected_safety.values()):
                violations.append((case, selected, judgments[case.case_id].absolute))
        return violations

    def policy_rank(candidate_policy: RecommendationPolicyV2) -> tuple[int, int, int, int, int, float]:
        results = [apply_policy(case, judgments[case.case_id], candidate_policy) for case in cases]
        violations = len(unsafe_replacements(candidate_policy))
        recommendation_accuracy = sum(
            result.recommendation is case.expected_recommendation
            for case, result in zip(cases, results, strict=True)
        )
        selected_accuracy = sum(
            case.expected_recommendation is RecommendationKind.REPLACE
            and result.selected_candidate_id == case.expected_selected_candidate_id
            for case, result in zip(cases, results, strict=True)
        )
        signal_accuracy = 0
        for case, result in zip(cases, results, strict=True):
            signal_accuracy += sum(
                (result.candidate_assessments[candidate.candidate_id] is CandidateAssessment.PASS)
                is candidate.expected_acceptable
                for candidate in case.candidates
            )
        review_count = sum(result.recommendation is RecommendationKind.REVIEW for result in results)
        separation = sum(
            candidate_policy.source_issue_positive_thresholds[key]
            - candidate_policy.source_issue_negative_thresholds[key]
            for key in SourceIssue
        ) + sum(
            candidate_policy.candidate_component_positive_thresholds[key]
            - candidate_policy.candidate_component_negative_thresholds[key]
            for key in CandidateComponent
        )
        return (
            -violations,
            recommendation_accuracy,
            selected_accuracy,
            signal_accuracy,
            -review_count,
            separation,
        )

    while True:
        violations = unsafe_replacements(policy)
        if not violations:
            return policy
        alternatives: list[RecommendationPolicyV2] = []
        for _, selected, absolute in violations:
            for component, expected in selected.expected_components.items():
                if expected:
                    continue
                score = absolute.candidate_component_scores[selected.candidate_id][component]
                higher = sorted({
                    item.absolute.candidate_component_scores[candidate.candidate_id][component]
                    for item in run.judgments
                    for candidate in by_id[item.absolute.case_id].candidates
                    if item.absolute.candidate_component_scores[candidate.candidate_id][component] > score
                })
                if higher:
                    thresholds = dict(policy.candidate_component_positive_thresholds)
                    thresholds[component] = higher[0]
                    alternatives.append(replace(
                        policy,
                        candidate_component_positive_thresholds=thresholds,
                        policy_version=None,
                    ))
            for dimension, expected in selected.expected_safety.items():
                if not expected:
                    continue
                score = absolute.candidate_safety_scores[selected.candidate_id][dimension]
                lower = sorted({
                    item.absolute.candidate_safety_scores[candidate.candidate_id][dimension]
                    for item in run.judgments
                    for candidate in by_id[item.absolute.case_id].candidates
                    if item.absolute.candidate_safety_scores[candidate.candidate_id][dimension] < score
                }, reverse=True)
                if lower:
                    thresholds = dict(policy.safety_review_thresholds)
                    thresholds[dimension] = lower[0]
                    alternatives.append(replace(
                        policy,
                        safety_review_thresholds=thresholds,
                        policy_version=None,
                    ))
        current_rank = policy_rank(policy)
        improving = [candidate for candidate in alternatives if policy_rank(candidate) > current_rank]
        if not improving:
            raise PolicyError("unacceptable replace recommendation cannot be eliminated by fitted thresholds")
        policy = max(improving, key=policy_rank)
        policy.validate()


def fit_ranking_policy(
    cases: list[RecommendationCaseV2],
    run: JudgmentRunV2,
    absolute_policy: RecommendationPolicyV2,
) -> RecommendationPolicyV2:
    by_id = {case.case_id: case for case in cases}
    observations: list[tuple[float, float, bool]] = []
    for item in run.judgments:
        ranking = item.ranking
        if ranking is None or ranking.status is not CheckStatus.CHECKED:
            continue
        ordered = sorted(ranking.probabilities.values(), reverse=True)
        margin = ordered[0] - ordered[1]
        case = by_id[item.absolute.case_id]
        top = max(ranking.probabilities.values())
        correct = (
            case.expected_recommendation is RecommendationKind.REPLACE
            and ranking.choice == case.expected_selected_candidate_id
            and ranking.probabilities.get(ranking.choice) == top
        )
        observations.append((ranking.confidence, margin, correct))
    if not observations:
        raise PolicyError("ranking thresholds need checked dev ranking evidence")
    if not any(item[2] for item in observations):
        raise PolicyError("ranking dev evidence has no correct choice")
    values_confidence = sorted({0.0, 1.0, *(item[0] for item in observations)})
    values_margin = sorted({0.0, 1.0, *(item[1] for item in observations)})
    best: tuple[tuple[int, int, int, int, int, int, float], RecommendationPolicyV2] | None = None
    for confidence in values_confidence:
        for margin in values_margin:
            candidate_policy = replace(
                absolute_policy,
                ranking_confidence_threshold=confidence,
                ranking_margin_threshold=margin,
                created_at=run.completed_at,
                policy_version=None,
            )
            results = [
                apply_policy(case, item, candidate_policy)
                for case, item in zip(cases, run.judgments, strict=True)
            ]
            unsafe = False
            for case, result in zip(cases, results, strict=True):
                if result.recommendation is not RecommendationKind.REPLACE:
                    continue
                selected = next(
                    candidate for candidate in case.candidates
                    if candidate.candidate_id == result.selected_candidate_id
                )
                if not selected.expected_acceptable or any(selected.expected_safety.values()):
                    unsafe = True
                    break
            if unsafe:
                continue
            admitted = [
                (conf >= confidence and observed_margin >= margin, correct)
                for conf, observed_margin, correct in observations
            ]
            if any(passes and not is_correct for passes, is_correct in admitted):
                continue
            correct_routes = sum((is_correct and passes) or (not is_correct and not passes) for passes, is_correct in admitted)
            incorrect_admitted = sum(passes and not is_correct for passes, is_correct in admitted)
            correct_admitted = sum(passes and is_correct for passes, is_correct in admitted)
            recommendation_accuracy = sum(
                result.recommendation is case.expected_recommendation
                for case, result in zip(cases, results, strict=True)
            )
            selected_accuracy = sum(
                case.expected_recommendation is RecommendationKind.REPLACE
                and result.selected_candidate_id == case.expected_selected_candidate_id
                for case, result in zip(cases, results, strict=True)
            )
            review_count = sum(result.recommendation is RecommendationKind.REVIEW for result in results)
            rank = (
                recommendation_accuracy,
                selected_accuracy,
                -review_count,
                correct_routes,
                -incorrect_admitted,
                correct_admitted,
                confidence + margin,
            )
            if best is None or rank > best[0]:
                best = (rank, candidate_policy)
    if best is None:
        raise PolicyError("ranking thresholds cannot avoid an unacceptable replace recommendation")
    selected = best[1]
    selected.validate()
    return replace(selected, policy_version=policy_version(selected))


def policy_from_dict(data: dict[str, Any]) -> RecommendationPolicyV2:
    try:
        expected_fields = {
            "policy_version", "pipeline_version", "fitted_corpus_version", "config_version",
            "absolute_question_set_version", "ranking_question_set_version", "model_version",
            "context_threshold", "source_issue_negative_thresholds", "source_issue_positive_thresholds",
            "candidate_component_negative_thresholds", "candidate_component_positive_thresholds",
            "safety_review_thresholds", "safety_reject_thresholds", "ranking_confidence_threshold",
            "ranking_margin_threshold", "selection_order", "created_at",
        }
        if set(data) != expected_fields:
            raise ValidationError("policy fields do not match the exact contract")
        policy = RecommendationPolicyV2(
            policy_version=data["policy_version"],
            pipeline_version=data["pipeline_version"],
            fitted_corpus_version=data["fitted_corpus_version"],
            config_version=data["config_version"],
            absolute_question_set_version=data["absolute_question_set_version"],
            ranking_question_set_version=data["ranking_question_set_version"],
            model_version=data["model_version"],
            context_threshold=data["context_threshold"],
            source_issue_negative_thresholds={SourceIssue(k): v for k, v in data["source_issue_negative_thresholds"].items()},
            source_issue_positive_thresholds={SourceIssue(k): v for k, v in data["source_issue_positive_thresholds"].items()},
            candidate_component_negative_thresholds={CandidateComponent(k): v for k, v in data["candidate_component_negative_thresholds"].items()},
            candidate_component_positive_thresholds={CandidateComponent(k): v for k, v in data["candidate_component_positive_thresholds"].items()},
            safety_review_thresholds={SafetyDimension(k): v for k, v in data["safety_review_thresholds"].items()},
            safety_reject_thresholds={SafetyDimension(k): v for k, v in data["safety_reject_thresholds"].items()},
            ranking_confidence_threshold=data["ranking_confidence_threshold"],
            ranking_margin_threshold=data["ranking_margin_threshold"],
            selection_order=list(data["selection_order"]),
            created_at=data["created_at"],
        )
        policy.validate()
    except (KeyError, TypeError, ValueError, ValidationError) as exc:
        raise PolicyError(f"invalid v2 policy: {type(exc).__name__}") from exc
    if policy.policy_version != policy_version(policy):
        raise PolicyError("policy digest mismatch")
    return policy


def apply_policy_run(cases: list[RecommendationCaseV2], run: JudgmentRunV2, policy: RecommendationPolicyV2) -> RecommendationRunV2:
    if (
        run.pipeline_version != "v2"
        or run.config_version != policy.config_version
        or run.absolute_question_set_version != policy.absolute_question_set_version
        or run.ranking_question_set_version != policy.ranking_question_set_version
        or run.requested_model != policy.model_version
    ):
        raise PolicyError("run and policy contracts do not match")
    by_id = {case.case_id: case for case in cases}
    judgments = {item.absolute.case_id: item for item in run.judgments}
    if (
        set(by_id) != set(judgments)
        or run.case_set_digest != case_set_digest(cases)
        or any(judgments[case_id].absolute.case_fingerprint != case_fingerprint(case) for case_id, case in by_id.items())
    ):
        raise PolicyError("run and corpus case sets do not match")
    recommendations = [] if run.run_status is not RunStatus.COMPLETE else [
        apply_policy(by_id[case_id], judgments[case_id], policy) for case_id in sorted(by_id)
    ]
    for recommendation in recommendations:
        recommendation.validate_against_case(by_id[recommendation.case_id])
    result = RecommendationRunV2(
        recommendation_run_version="2.0.0",
        recommendation_run_digest=None,
        pipeline_version="v2",
        judgment_run_digest=run.run_digest,
        evaluation_corpus_version=run.corpus_version,
        policy_version=policy.policy_version,
        policy_fitted_corpus_version=policy.fitted_corpus_version,
        run_status=run.run_status,
        recommendations=recommendations,
    )
    result.recommendation_run_digest = recommendation_run_digest(result)
    return result
