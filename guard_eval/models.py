from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from enum import Enum
from typing import Any


class ValidationError(ValueError):
    """Raised when a guard-eval artifact violates its public contract."""


class Split(str, Enum):
    DEV = "dev"
    HOLDOUT = "holdout"


class NaturalnessReason(str, Enum):
    LEXICALLY_INCOMPLETE = "lexically_incomplete"
    UNNATURAL_COLLOCATION = "unnatural_collocation"


class GuardDimension(str, Enum):
    ADDS_CLAIM = "adds_claim"
    CHANGES_ACTOR_OR_TIME = "changes_actor_or_time"
    CHANGES_CAUSALITY_OR_COMMITMENT = "changes_causality_or_commitment"
    CHANGES_ORDER_OR_CONCURRENCY = "changes_order_or_concurrency"
    CHANGES_REGISTER = "changes_register"
    KEEPS_INVALID_PROCESS_METADATA = "keeps_invalid_process_metadata"


class CandidateOriginKind(str, Enum):
    HOST_LLM_OUTPUT = "host_llm_output"
    BASELINE_OBSERVATION = "baseline_observation"
    MAINTAINER_FIXTURE = "maintainer_fixture"


class GuardAction(str, Enum):
    PASS = "pass"
    REVIEW = "review"
    REJECT = "reject"


class EditDecision(str, Enum):
    KEEP = "keep"
    REPLACE = "replace"
    REVIEW = "review"


class CheckStatus(str, Enum):
    CHECKED = "checked"
    UNCHECKED = "unchecked"


class RunStatus(str, Enum):
    COMPLETE = "complete"
    INCOMPLETE = "incomplete"
    INVALID = "invalid"


ALLOWED_REASON_CODES = frozenset({
    "missing_api_key", "timeout", "authentication", "rate_limited",
    "overloaded", "connection", "invalid_response", "service_error",
})


def _probability(value: float, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= float(value) <= 1:
        raise ValidationError(f"{name} must be within [0, 1]")


def _digest(value: str | None, name: str, *, nullable: bool = False) -> None:
    if value is None and nullable:
        return
    if not isinstance(value, str) or not value.startswith("sha256:") or len(value) != 71:
        raise ValidationError(f"{name} must be sha256:<64 hex chars>")
    try:
        int(value[7:], 16)
    except ValueError as exc:
        raise ValidationError(f"{name} contains non-hex characters") from exc


def to_jsonable(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return {key: to_jsonable(child) for key, child in asdict(value).items()}
    if isinstance(value, dict):
        return {str(to_jsonable(key)): to_jsonable(child) for key, child in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_jsonable(child) for child in value]
    return value


@dataclass
class CandidateEdit:
    candidate_id: str
    candidate_span: str
    candidate_origin: dict[str, Any]
    expected_dimensions: dict[GuardDimension, bool]
    expected_guard_action: GuardAction

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CandidateEdit:
        required = {"candidate_id", "candidate_span", "candidate_origin", "expected_dimensions", "expected_guard_action"}
        missing = required - data.keys()
        if missing:
            raise ValidationError(f"candidate missing fields: {sorted(missing)}")
        instance = cls(
            candidate_id=data["candidate_id"], candidate_span=data["candidate_span"],
            candidate_origin=dict(data["candidate_origin"]),
            expected_dimensions={GuardDimension(key): value for key, value in data["expected_dimensions"].items()},
            expected_guard_action=GuardAction(data["expected_guard_action"]),
        )
        instance.validate()
        return instance

    def validate(self) -> None:
        if not self.candidate_id or not self.candidate_span.strip():
            raise ValidationError("candidate id and span must be non-empty")
        if set(self.expected_dimensions) != set(GuardDimension):
            raise ValidationError("candidate must label all guard dimensions")
        if any(not isinstance(value, bool) for value in self.expected_dimensions.values()):
            raise ValidationError("expected dimensions must be boolean")
        harmful = any(self.expected_dimensions.values())
        if harmful and self.expected_guard_action is GuardAction.PASS:
            raise ValidationError("harmful candidate cannot have pass guard action")
        if not harmful and self.expected_guard_action is not GuardAction.PASS:
            raise ValidationError("safe candidate must have pass guard action")
        origin = self.candidate_origin
        try:
            kind = CandidateOriginKind(origin["kind"])
        except (KeyError, ValueError, TypeError) as exc:
            raise ValidationError("candidate origin kind is invalid") from exc
        if not origin.get("reference") or not origin.get("authority"):
            raise ValidationError("candidate origin needs reference and authority")
        if kind is CandidateOriginKind.HOST_LLM_OUTPUT and not (origin.get("model_version") and origin.get("workflow_version")):
            raise ValidationError("host LLM origin needs model and workflow versions")
        if kind is CandidateOriginKind.BASELINE_OBSERVATION and not origin.get("workflow_version"):
            raise ValidationError("baseline origin needs workflow version")


@dataclass
class EvaluationCase:
    case_id: str
    split: Split
    source_span: str
    candidates: list[CandidateEdit]
    context_before: str
    context_after: str
    current_intent: str
    genre: str
    inseparable_edit_ids: list[str]
    expected_needs_edit: bool
    expected_naturalness_reasons: list[NaturalnessReason]
    expected_preferred_option: str
    expected_edit_decision: EditDecision
    label_source: dict[str, Any]
    pattern_refs: list[str]
    baseline: dict[str, Any]
    provenance: dict[str, Any]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EvaluationCase:
        required = {field.name for field in cls.__dataclass_fields__.values()}
        missing = required - data.keys()
        if missing:
            raise ValidationError(f"case missing fields: {sorted(missing)}")
        instance = cls(
            case_id=data["case_id"], split=Split(data["split"]), source_span=data["source_span"],
            candidates=[CandidateEdit.from_dict(item) for item in data["candidates"]],
            context_before=data["context_before"], context_after=data["context_after"],
            current_intent=data["current_intent"], genre=data["genre"],
            inseparable_edit_ids=list(data["inseparable_edit_ids"]), expected_needs_edit=data["expected_needs_edit"],
            expected_naturalness_reasons=[NaturalnessReason(item) for item in data["expected_naturalness_reasons"]],
            expected_preferred_option=data["expected_preferred_option"],
            expected_edit_decision=EditDecision(data["expected_edit_decision"]),
            label_source=dict(data["label_source"]), pattern_refs=list(data["pattern_refs"]),
            baseline=dict(data["baseline"]), provenance=dict(data["provenance"]),
        )
        return instance


@dataclass
class JudgmentSet:
    case_id: str
    case_fingerprint: str
    status: CheckStatus
    naturalness_scores: dict[NaturalnessReason, float] | None = None
    preference_probabilities: dict[str, float] | None = None
    preference_choice: str | None = None
    preference_confidence: float | None = None
    candidate_safety_scores: dict[str, dict[GuardDimension, float]] | None = None
    reason_code: str | None = None
    latency_ms: int | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    model_version: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> JudgmentSet:
        return cls(
            case_id=data["case_id"], case_fingerprint=data["case_fingerprint"], status=CheckStatus(data["status"]),
            naturalness_scores=None if data.get("naturalness_scores") is None else {NaturalnessReason(k): v for k, v in data["naturalness_scores"].items()},
            preference_probabilities=data.get("preference_probabilities"), preference_choice=data.get("preference_choice"),
            preference_confidence=data.get("preference_confidence"),
            candidate_safety_scores=None if data.get("candidate_safety_scores") is None else {
                cid: {GuardDimension(k): v for k, v in scores.items()} for cid, scores in data["candidate_safety_scores"].items()
            },
            reason_code=data.get("reason_code"), latency_ms=data.get("latency_ms"), input_tokens=data.get("input_tokens"),
            output_tokens=data.get("output_tokens"), model_version=data.get("model_version"),
        )

    def validate(self, candidate_options: list[str]) -> None:
        _digest(self.case_fingerprint, "case_fingerprint")
        scored_fields = (self.naturalness_scores, self.preference_probabilities, self.preference_choice,
                         self.preference_confidence, self.candidate_safety_scores, self.model_version)
        if self.status is CheckStatus.UNCHECKED:
            if self.reason_code not in ALLOWED_REASON_CODES:
                raise ValidationError("unchecked judgment needs an allowlisted reason")
            if any(value is not None for value in scored_fields):
                raise ValidationError("unchecked judgment cannot carry scores")
            return
        if self.reason_code is not None or any(value is None for value in scored_fields):
            raise ValidationError("checked judgment needs complete scores and no reason code")
        if set(self.naturalness_scores or {}) != set(NaturalnessReason):
            raise ValidationError("checked judgment needs both naturalness scores")
        for key, value in (self.naturalness_scores or {}).items():
            _probability(value, key.value)
        expected_options = {"keep_original", "none_of_candidates", *candidate_options}
        if set(self.preference_probabilities or {}) != expected_options:
            raise ValidationError("preference options do not match candidates")
        for key, value in (self.preference_probabilities or {}).items():
            _probability(value, key)
        if abs(sum((self.preference_probabilities or {}).values()) - 1.0) > 1e-6:
            raise ValidationError("preference probabilities must sum to one")
        if self.preference_choice not in expected_options:
            raise ValidationError("preference choice is outside option allowlist")
        _probability(float(self.preference_confidence), "preference_confidence")
        candidate_ids = {option.removeprefix("candidate:") for option in candidate_options}
        if set(self.candidate_safety_scores or {}) != candidate_ids:
            raise ValidationError("safety scores do not cover every candidate")
        for scores in (self.candidate_safety_scores or {}).values():
            if set(scores) != set(GuardDimension):
                raise ValidationError("safety scores must cover all dimensions")
            for dimension, value in scores.items():
                _probability(value, dimension.value)


@dataclass
class DecisionPolicy:
    policy_version: str | None
    corpus_version_fitted: str
    config_version: str
    question_set_version: str
    model_version: str
    needs_edit_thresholds: dict[NaturalnessReason, float]
    preference_confidence_threshold: float
    preference_margin_threshold: float
    safety_review_threshold: float
    safety_reject_threshold: float
    selection_order: list[str]
    created_at: str

    def validate(self) -> None:
        for name in ("corpus_version_fitted", "config_version", "question_set_version"):
            _digest(getattr(self, name), name)
        _digest(self.policy_version, "policy_version", nullable=True)
        if set(self.needs_edit_thresholds) != set(NaturalnessReason):
            raise ValidationError("policy needs threshold for both naturalness reasons")
        for name, value in {
            **{reason.value: score for reason, score in self.needs_edit_thresholds.items()},
            "preference_confidence_threshold": self.preference_confidence_threshold,
            "preference_margin_threshold": self.preference_margin_threshold,
            "safety_review_threshold": self.safety_review_threshold,
            "safety_reject_threshold": self.safety_reject_threshold,
        }.items():
            _probability(value, name)
        if self.safety_review_threshold > self.safety_reject_threshold:
            raise ValidationError("safety review threshold must not exceed reject threshold")
        if not self.selection_order:
            raise ValidationError("selection order cannot be empty")


@dataclass
class EvaluationRun:
    run_id: str
    started_at: str
    completed_at: str
    split: Split
    corpus_version: str
    config_version: str
    question_set_version: str
    requested_model: str
    observed_models: list[str]
    policy_version: str | None
    pricing_version: str | None
    run_status: RunStatus
    counts: dict[str, Any]
    judgments: list[JudgmentSet] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EvaluationRun:
        return cls(
            run_id=data["run_id"], started_at=data["started_at"], completed_at=data["completed_at"],
            split=Split(data["split"]), corpus_version=data["corpus_version"], config_version=data["config_version"],
            question_set_version=data["question_set_version"], requested_model=data["requested_model"],
            observed_models=list(data["observed_models"]), policy_version=data.get("policy_version"),
            pricing_version=data.get("pricing_version"), run_status=RunStatus(data["run_status"]),
            counts=dict(data["counts"]), judgments=[JudgmentSet.from_dict(item) for item in data["judgments"]],
        )
