from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from dataclasses import asdict, dataclass, field, is_dataclass
from enum import Enum
from typing import Any


class ValidationError(ValueError):
    """Raised when a v2 corpus or artifact violates its contract."""


class Split(str, Enum):
    DEV = "dev"
    HOLDOUT = "holdout"


class RecommendationKind(str, Enum):
    KEEP = "keep"
    REVIEW = "review"
    REPLACE = "replace"


class SourceIssue(str, Enum):
    LEXICALLY_INCOMPLETE = "lexically_incomplete"
    UNNATURAL_COLLOCATION = "unnatural_collocation"


class CandidateComponent(str, Enum):
    FIXES_ISSUE = "fixes_issue"
    PRESERVES_MEANING_AND_NUANCE = "preserves_meaning_and_nuance"
    FITS_VOICE_AND_GENRE = "fits_voice_and_genre"


class SafetyDimension(str, Enum):
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


class CheckStatus(str, Enum):
    CHECKED = "checked"
    UNCHECKED = "unchecked"


class RunStatus(str, Enum):
    COMPLETE = "complete"
    INCOMPLETE = "incomplete"
    INVALID = "invalid"


class CandidateAssessment(str, Enum):
    PASS = "pass"
    REVIEW = "review"
    REJECT = "reject"


ALLOWED_SERVICE_REASONS = frozenset({
    "missing_api_key",
    "timeout",
    "authentication",
    "rate_limited",
    "overloaded",
    "connection",
    "invalid_response",
    "service_error",
})

ALLOWED_RECOMMENDATION_REASONS = frozenset({
    "source_already_sufficient",
    "insufficient_context",
    "source_signal_uncertain",
    "source_signal_conflict",
    "no_acceptable_candidate",
    "single_acceptable_candidate",
    "ranked_candidate_selected",
    "ranking_uncertain",
    "service_unchecked",
})

ALLOWED_GENRES = frozenset({"blog cá nhân", "tài liệu kỹ thuật"})
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def canonical_json(value: Any) -> str:
    return json.dumps(to_jsonable(value), ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def canonical_digest(data: dict[str, Any], version_field: str | None = None) -> str:
    semantic = dict(data)
    if version_field is not None:
        semantic.pop(version_field, None)
    return "sha256:" + hashlib.sha256(canonical_json(semantic).encode("utf-8")).hexdigest()


def validate_digest(value: str | None, name: str, *, nullable: bool = False) -> None:
    if value is None and nullable:
        return
    if not isinstance(value, str) or not value.startswith("sha256:") or len(value) != 71:
        raise ValidationError(f"{name} must be sha256:<64 hex chars>")
    try:
        int(value[7:], 16)
    except ValueError as exc:
        raise ValidationError(f"{name} contains non-hex characters") from exc


def validate_probability(value: float, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= float(value) <= 1:
        raise ValidationError(f"{name} must be within [0, 1]")


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


def normalize_text(value: str) -> str:
    return " ".join(unicodedata.normalize("NFC", value).split())


def _require_exact(data: dict[str, Any], fields: set[str], name: str) -> None:
    missing = fields - data.keys()
    extra = data.keys() - fields
    if missing or extra:
        raise ValidationError(f"{name} fields mismatch: missing={sorted(missing)}, extra={sorted(extra)}")


@dataclass(frozen=True)
class CandidateV2:
    candidate_id: str
    candidate_span: str
    candidate_origin: dict[str, Any]
    expected_acceptable: bool
    expected_components: dict[CandidateComponent, bool]
    expected_safety: dict[SafetyDimension, bool]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CandidateV2:
        fields = {
            "candidate_id", "candidate_span", "candidate_origin", "expected_acceptable",
            "expected_components", "expected_safety",
        }
        _require_exact(data, fields, "candidate")
        try:
            item = cls(
                candidate_id=data["candidate_id"],
                candidate_span=data["candidate_span"],
                candidate_origin=dict(data["candidate_origin"]),
                expected_acceptable=data["expected_acceptable"],
                expected_components={CandidateComponent(k): v for k, v in data["expected_components"].items()},
                expected_safety={SafetyDimension(k): v for k, v in data["expected_safety"].items()},
            )
        except (TypeError, ValueError) as exc:
            raise ValidationError("candidate has invalid enum or object fields") from exc
        item.validate()
        return item

    def validate(self) -> None:
        if not isinstance(self.candidate_id, str) or SLUG_RE.fullmatch(self.candidate_id) is None:
            raise ValidationError("candidate_id must be a stable lowercase slug")
        if not isinstance(self.candidate_span, str) or not normalize_text(self.candidate_span):
            raise ValidationError("candidate_span must be non-empty")
        if not isinstance(self.expected_acceptable, bool):
            raise ValidationError("expected_acceptable must be boolean")
        if set(self.expected_components) != set(CandidateComponent):
            raise ValidationError("candidate must label every component")
        if set(self.expected_safety) != set(SafetyDimension):
            raise ValidationError("candidate must label every safety dimension")
        if any(not isinstance(value, bool) for value in [*self.expected_components.values(), *self.expected_safety.values()]):
            raise ValidationError("candidate labels must be boolean")
        derived = all(self.expected_components.values()) and not any(self.expected_safety.values())
        if self.expected_acceptable is not derived:
            raise ValidationError("expected_acceptable conflicts with component or safety labels")
        try:
            kind = CandidateOriginKind(self.candidate_origin["kind"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValidationError("candidate_origin kind is invalid") from exc
        if not self.candidate_origin.get("reference") or not self.candidate_origin.get("authority"):
            raise ValidationError("candidate_origin needs reference and authority")
        if kind is CandidateOriginKind.HOST_LLM_OUTPUT and not (
            self.candidate_origin.get("model_version") and self.candidate_origin.get("workflow_version")
        ):
            raise ValidationError("host LLM origin needs model and workflow versions")


@dataclass(frozen=True)
class PromotionLineage:
    kind: str
    source_feature: str
    source_split: str
    source_case_id: str
    source_case_fingerprint: str
    source_corpus_version: str
    source_artifact_path: str
    source_artifact_sha256: str
    promotion_decision_ref: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PromotionLineage:
        fields = {field.name for field in cls.__dataclass_fields__.values()}
        _require_exact(data, fields, "lineage")
        item = cls(**data)
        if item.kind != "promoted_observed_holdout" or item.source_split != "holdout":
            raise ValidationError("promotion lineage kind and source split are fixed")
        for name in ("source_case_fingerprint", "source_corpus_version", "source_artifact_sha256"):
            validate_digest(getattr(item, name), name)
        return item


@dataclass(frozen=True)
class RecommendationCaseV2:
    schema_version: str
    case_id: str
    split: Split
    source_span: str
    context_before: str
    context_after: str
    current_intent: str
    genre: str
    candidates: list[CandidateV2]
    expected_recommendation: RecommendationKind
    expected_selected_candidate_id: str | None
    expected_source_issues: dict[SourceIssue, bool]
    label_authority: dict[str, Any]
    provenance: dict[str, Any]
    lineage: PromotionLineage | None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RecommendationCaseV2:
        fields = {field.name for field in cls.__dataclass_fields__.values()}
        _require_exact(data, fields, "case")
        try:
            item = cls(
                schema_version=data["schema_version"],
                case_id=data["case_id"],
                split=Split(data["split"]),
                source_span=data["source_span"],
                context_before=data["context_before"],
                context_after=data["context_after"],
                current_intent=data["current_intent"],
                genre=data["genre"],
                candidates=[CandidateV2.from_dict(value) for value in data["candidates"]],
                expected_recommendation=RecommendationKind(data["expected_recommendation"]),
                expected_selected_candidate_id=data["expected_selected_candidate_id"],
                expected_source_issues={SourceIssue(k): v for k, v in data["expected_source_issues"].items()},
                label_authority=dict(data["label_authority"]),
                provenance=dict(data["provenance"]),
                lineage=None if data["lineage"] is None else PromotionLineage.from_dict(data["lineage"]),
            )
        except (TypeError, ValueError) as exc:
            raise ValidationError("case has invalid enum or object fields") from exc
        item.validate()
        return item

    def validate(self) -> None:
        if self.schema_version != "2.0.0":
            raise ValidationError("unsupported case schema version")
        if not isinstance(self.case_id, str) or SLUG_RE.fullmatch(self.case_id) is None:
            raise ValidationError("case_id must be a stable lowercase slug")
        if not isinstance(self.context_before, str) or not isinstance(self.context_after, str):
            raise ValidationError("case context fields must be strings")
        for name, value in {
            "case_id": self.case_id,
            "source_span": self.source_span,
            "current_intent": self.current_intent,
            "genre": self.genre,
        }.items():
            if not isinstance(value, str) or not normalize_text(value):
                raise ValidationError(f"{name} must be non-empty")
        if self.genre not in ALLOWED_GENRES:
            raise ValidationError("genre is outside the corpus allowlist")
        if not 1 <= len(self.candidates) <= 3:
            raise ValidationError("case must contain one to three candidates")
        ids = [candidate.candidate_id for candidate in self.candidates]
        spans = [normalize_text(candidate.candidate_span) for candidate in self.candidates]
        if len(set(ids)) != len(ids) or len(set(spans)) != len(spans):
            raise ValidationError("candidate ids and normalized spans must be unique")
        if normalize_text(self.source_span) in spans:
            raise ValidationError("candidate cannot be a source no-op")
        if set(self.expected_source_issues) != set(SourceIssue):
            raise ValidationError("case must label every source issue")
        if any(not isinstance(value, bool) for value in self.expected_source_issues.values()):
            raise ValidationError("source issue labels must be boolean")
        acceptable = {candidate.candidate_id for candidate in self.candidates if candidate.expected_acceptable}
        if self.expected_recommendation is RecommendationKind.REPLACE:
            if self.expected_selected_candidate_id not in acceptable:
                raise ValidationError("replace needs one selected candidate from the acceptable set")
        elif self.expected_selected_candidate_id is not None:
            raise ValidationError("only replace may select a candidate")
        if self.lineage is not None and self.split is not Split.DEV:
            raise ValidationError("promoted observed holdout is valid only in dev")
        if not self.label_authority.get("authority") or not self.label_authority.get("reference"):
            raise ValidationError("label_authority needs authority and reference")
        if not self.provenance.get("kind") or not self.provenance.get("reference"):
            raise ValidationError("provenance needs kind and reference")
        if self.provenance["kind"] not in {
            "public_repository_example", "promoted_public_repository_example", "neutral_fixture"
        }:
            raise ValidationError("provenance kind must be public or neutral")


@dataclass
class AbsoluteJudgmentV2:
    case_id: str
    case_fingerprint: str
    status: CheckStatus
    source_context_sufficient: float | None = None
    source_issue_scores: dict[SourceIssue, float] | None = None
    candidate_component_scores: dict[str, dict[CandidateComponent, float]] | None = None
    candidate_safety_scores: dict[str, dict[SafetyDimension, float]] | None = None
    reason_code: str | None = None
    latency_ms: int | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    observed_model: str | None = None

    def validate(self) -> None:
        if not isinstance(self.case_id, str) or not self.case_id:
            raise ValidationError("absolute judgment needs a case id")
        validate_digest(self.case_fingerprint, "case_fingerprint")
        if self.latency_ms is not None and (
            isinstance(self.latency_ms, bool) or not isinstance(self.latency_ms, int) or self.latency_ms < 0
        ):
            raise ValidationError("latency_ms must be null or a non-negative integer")
        unchecked_payload = (
            self.source_context_sufficient,
            self.source_issue_scores,
            self.candidate_component_scores,
            self.candidate_safety_scores,
            self.input_tokens,
            self.output_tokens,
            self.observed_model,
        )
        if self.status is CheckStatus.UNCHECKED:
            if self.reason_code not in ALLOWED_SERVICE_REASONS or any(value is not None for value in unchecked_payload):
                raise ValidationError("unchecked absolute judgment needs one reason and no scores")
            return
        required = (
            self.source_context_sufficient,
            self.source_issue_scores,
            self.candidate_component_scores,
            self.candidate_safety_scores,
            self.observed_model,
        )
        if self.reason_code is not None or any(value is None for value in required):
            raise ValidationError("checked absolute judgment needs complete scores and no reason")
        validate_probability(self.source_context_sufficient, "source_context_sufficient")
        if set(self.source_issue_scores or {}) != set(SourceIssue):
            raise ValidationError("source issue scores must cover every issue")
        for issue, value in (self.source_issue_scores or {}).items():
            validate_probability(value, issue.value)
        components = self.candidate_component_scores or {}
        safety = self.candidate_safety_scores or {}
        if not components or set(components) != set(safety):
            raise ValidationError("component and safety scores must cover the same candidates")
        for candidate_id, scores in components.items():
            if not candidate_id or set(scores) != set(CandidateComponent):
                raise ValidationError("component scores must cover every component")
            for component, value in scores.items():
                validate_probability(value, component.value)
        for scores in safety.values():
            if set(scores) != set(SafetyDimension):
                raise ValidationError("safety scores must cover every dimension")
            for dimension, value in scores.items():
                validate_probability(value, dimension.value)
        for name, value in (("input_tokens", self.input_tokens), ("output_tokens", self.output_tokens)):
            if value is not None and (isinstance(value, bool) or not isinstance(value, int) or value < 0):
                raise ValidationError(f"{name} must be null or a non-negative integer")
        if not isinstance(self.observed_model, str) or not self.observed_model:
            raise ValidationError("checked absolute judgment needs observed_model")


@dataclass
class RankingJudgmentV2:
    eligible_candidate_ids: list[str]
    probabilities: dict[str, float]
    choice: str
    confidence: float
    status: CheckStatus = CheckStatus.CHECKED
    reason_code: str | None = None
    latency_ms: int | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    observed_model: str | None = None

    def validate(self) -> None:
        eligible = self.eligible_candidate_ids
        if len(eligible) < 2 or eligible != sorted(set(eligible)):
            raise ValidationError("ranking shortlist needs at least two sorted unique candidates")
        if self.latency_ms is not None and (
            isinstance(self.latency_ms, bool) or not isinstance(self.latency_ms, int) or self.latency_ms < 0
        ):
            raise ValidationError("latency_ms must be null or a non-negative integer")
        if self.status is CheckStatus.UNCHECKED:
            scored = (self.probabilities, self.choice, self.confidence, self.input_tokens, self.output_tokens, self.observed_model)
            if self.reason_code not in ALLOWED_SERVICE_REASONS or scored != ({}, "", 0.0, None, None, None):
                raise ValidationError("unchecked ranking needs one reason and no scores")
            return
        if self.reason_code is not None or set(self.probabilities) != set(eligible) or self.choice not in self.probabilities:
            raise ValidationError("checked ranking options must match shortlist")
        for candidate_id, value in self.probabilities.items():
            validate_probability(value, candidate_id)
        if abs(sum(self.probabilities.values()) - 1.0) > 1e-6:
            raise ValidationError("ranking probabilities must sum to one")
        validate_probability(self.confidence, "ranking confidence")
        for name, value in (("input_tokens", self.input_tokens), ("output_tokens", self.output_tokens)):
            if value is not None and (isinstance(value, bool) or not isinstance(value, int) or value < 0):
                raise ValidationError(f"{name} must be null or a non-negative integer")
        if not isinstance(self.observed_model, str) or not self.observed_model:
            raise ValidationError("checked ranking needs observed_model")


@dataclass
class CaseJudgmentV2:
    absolute: AbsoluteJudgmentV2
    ranking: RankingJudgmentV2 | None = None


@dataclass
class JudgmentRunV2:
    judgment_run_version: str
    pipeline_version: str
    run_digest: str | None
    corpus_version: str
    case_set_digest: str
    split: Split | str
    config_version: str
    absolute_question_set_version: str
    ranking_question_set_version: str
    requested_model: str
    observed_models: list[str]
    policy_version: str | None
    run_status: RunStatus
    counts: dict[str, Any]
    judgments: list[Any] = field(default_factory=list)
    started_at: str = ""
    completed_at: str = ""

    def validate(self) -> None:
        for name in (
            "corpus_version", "case_set_digest", "config_version",
            "absolute_question_set_version", "ranking_question_set_version",
        ):
            validate_digest(getattr(self, name), name)
        validate_digest(self.run_digest, "run_digest", nullable=True)
        if self.pipeline_version not in {"v1_compat", "v2"}:
            raise ValidationError("pipeline_version is invalid")
        if self.judgment_run_version != "2.0.0":
            raise ValidationError("judgment run version is invalid")
        Split(self.split)
        if self.policy_version is not None:
            raise ValidationError("raw judgment run must have policy_version=null")
        observed_models: set[str] = set()
        checked = 0
        total = 0
        unchecked_reasons: dict[str, int] = {}
        for judgment in self.judgments:
            total += 1
            judgment.absolute.validate()
            if judgment.absolute.status is CheckStatus.CHECKED:
                checked += 1
                observed_models.add(str(judgment.absolute.observed_model))
            else:
                reason = str(judgment.absolute.reason_code)
                unchecked_reasons[reason] = unchecked_reasons.get(reason, 0) + 1
            if judgment.ranking is not None:
                total += 1
                if judgment.absolute.status is not CheckStatus.CHECKED:
                    raise ValidationError("ranking cannot accompany an unchecked absolute judgment")
                judgment.ranking.validate()
                if judgment.ranking.status is CheckStatus.CHECKED:
                    checked += 1
                    observed_models.add(str(judgment.ranking.observed_model))
                else:
                    reason = str(judgment.ranking.reason_code)
                    unchecked_reasons[reason] = unchecked_reasons.get(reason, 0) + 1
        actual_unchecked = sum(unchecked_reasons.values())
        expected_counts = {
            "total": total,
            "checked": checked,
            "unchecked": actual_unchecked,
            "unchecked_by_reason": dict(sorted(unchecked_reasons.items())),
        }
        if self.counts != expected_counts:
            raise ValidationError("judgment run counts do not match judgment statuses")
        if self.observed_models != sorted(observed_models):
            raise ValidationError("observed_models do not match checked judgments")
        if self.run_status is RunStatus.COMPLETE and actual_unchecked:
            raise ValidationError("complete run cannot contain unchecked judgments")
        if self.run_status is RunStatus.INCOMPLETE and not actual_unchecked:
            raise ValidationError("incomplete run needs an unchecked judgment")
        if self.run_status is not RunStatus.INVALID and any(model != self.requested_model for model in observed_models):
            raise ValidationError("non-invalid run contains a model mismatch")


def judgment_run_digest(run: JudgmentRunV2) -> str:
    data = to_jsonable(run)
    for key in ("run_digest", "started_at", "completed_at"):
        data.pop(key, None)
    return canonical_digest(data)


@dataclass
class PolicyRecommendationV2:
    case_id: str
    case_fingerprint: str
    recommendation: RecommendationKind
    selected_candidate_id: str | None
    reason_codes: list[str]
    candidate_assessments: dict[str, CandidateAssessment]
    eligible_candidate_ids: list[str]

    def validate(self) -> None:
        if not isinstance(self.case_id, str) or not self.case_id:
            raise ValidationError("policy recommendation needs a case id")
        validate_digest(self.case_fingerprint, "case_fingerprint")
        if not self.reason_codes or any(reason not in ALLOWED_RECOMMENDATION_REASONS for reason in self.reason_codes):
            raise ValidationError("policy recommendation reason code is invalid")
        if any(not candidate_id for candidate_id in self.candidate_assessments):
            raise ValidationError("candidate assessment ids must be non-empty")
        if self.eligible_candidate_ids != sorted(set(self.eligible_candidate_ids)):
            raise ValidationError("eligible candidate ids must be sorted and unique")
        if any(self.candidate_assessments.get(candidate_id) is not CandidateAssessment.PASS for candidate_id in self.eligible_candidate_ids):
            raise ValidationError("eligible candidates must have pass assessment")
        if self.recommendation is RecommendationKind.REPLACE:
            if self.selected_candidate_id not in self.eligible_candidate_ids:
                raise ValidationError("replace must select an eligible candidate")
        elif self.selected_candidate_id is not None:
            raise ValidationError("keep/review cannot select a candidate")

    def validate_against_case(self, case: RecommendationCaseV2) -> None:
        self.validate()
        from .corpus import case_fingerprint

        expected_ids = {candidate.candidate_id for candidate in case.candidates}
        if self.case_id != case.case_id or self.case_fingerprint != case_fingerprint(case):
            raise ValidationError("policy recommendation does not match its case")
        if set(self.candidate_assessments) != expected_ids:
            raise ValidationError("policy recommendation candidate assessments do not match case candidates")


@dataclass
class RecommendationRunV2:
    recommendation_run_version: str
    recommendation_run_digest: str | None
    pipeline_version: str
    judgment_run_digest: str
    evaluation_corpus_version: str
    policy_version: str
    policy_fitted_corpus_version: str
    run_status: RunStatus
    recommendations: list[PolicyRecommendationV2]


def recommendation_run_digest(run: RecommendationRunV2) -> str:
    return canonical_digest(to_jsonable(run), "recommendation_run_digest")


def absolute_judgment_from_dict(data: dict[str, Any]) -> AbsoluteJudgmentV2:
    _require_exact(data, {
        "case_id", "case_fingerprint", "status", "source_context_sufficient", "source_issue_scores",
        "candidate_component_scores", "candidate_safety_scores", "reason_code", "latency_ms",
        "input_tokens", "output_tokens", "observed_model",
    }, "absolute judgment")
    return AbsoluteJudgmentV2(
        case_id=data["case_id"],
        case_fingerprint=data["case_fingerprint"],
        status=CheckStatus(data["status"]),
        source_context_sufficient=data.get("source_context_sufficient"),
        source_issue_scores=None if data.get("source_issue_scores") is None else {
            SourceIssue(k): v for k, v in data["source_issue_scores"].items()
        },
        candidate_component_scores=None if data.get("candidate_component_scores") is None else {
            candidate_id: {CandidateComponent(k): v for k, v in scores.items()}
            for candidate_id, scores in data["candidate_component_scores"].items()
        },
        candidate_safety_scores=None if data.get("candidate_safety_scores") is None else {
            candidate_id: {SafetyDimension(k): v for k, v in scores.items()}
            for candidate_id, scores in data["candidate_safety_scores"].items()
        },
        reason_code=data.get("reason_code"),
        latency_ms=data.get("latency_ms"),
        input_tokens=data.get("input_tokens"),
        output_tokens=data.get("output_tokens"),
        observed_model=data.get("observed_model"),
    )


def ranking_judgment_from_dict(data: dict[str, Any]) -> RankingJudgmentV2:
    _require_exact(data, {
        "eligible_candidate_ids", "probabilities", "choice", "confidence", "status", "reason_code",
        "latency_ms", "input_tokens", "output_tokens", "observed_model",
    }, "ranking judgment")
    return RankingJudgmentV2(
        eligible_candidate_ids=list(data["eligible_candidate_ids"]),
        probabilities=dict(data["probabilities"]),
        choice=data["choice"],
        confidence=data["confidence"],
        status=CheckStatus(data.get("status", "checked")),
        reason_code=data.get("reason_code"),
        latency_ms=data.get("latency_ms"),
        input_tokens=data.get("input_tokens"),
        output_tokens=data.get("output_tokens"),
        observed_model=data.get("observed_model"),
    )


def judgment_run_from_dict(data: dict[str, Any]) -> JudgmentRunV2:
    _require_exact(data, {
        "judgment_run_version", "pipeline_version", "run_digest", "corpus_version", "case_set_digest",
        "split", "config_version", "absolute_question_set_version", "ranking_question_set_version",
        "requested_model", "observed_models", "policy_version", "run_status", "counts", "judgments",
        "started_at", "completed_at",
    }, "judgment run")
    for item in data["judgments"]:
        _require_exact(item, {"absolute", "ranking"}, "case judgment")
    judgments = [
        CaseJudgmentV2(
            absolute=absolute_judgment_from_dict(item["absolute"]),
            ranking=None if item.get("ranking") is None else ranking_judgment_from_dict(item["ranking"]),
        )
        for item in data["judgments"]
    ]
    run = JudgmentRunV2(
        judgment_run_version=data["judgment_run_version"],
        pipeline_version=data["pipeline_version"],
        run_digest=data["run_digest"],
        corpus_version=data["corpus_version"],
        case_set_digest=data["case_set_digest"],
        split=Split(data["split"]),
        config_version=data["config_version"],
        absolute_question_set_version=data["absolute_question_set_version"],
        ranking_question_set_version=data["ranking_question_set_version"],
        requested_model=data["requested_model"],
        observed_models=list(data["observed_models"]),
        policy_version=data.get("policy_version"),
        run_status=RunStatus(data["run_status"]),
        counts=dict(data["counts"]),
        judgments=judgments,
        started_at=data["started_at"],
        completed_at=data["completed_at"],
    )
    run.validate()
    if run.run_digest != judgment_run_digest(run):
        raise ValidationError("judgment run digest mismatch")
    return run


def policy_recommendation_from_dict(data: dict[str, Any]) -> PolicyRecommendationV2:
    _require_exact(data, {
        "case_id", "case_fingerprint", "recommendation", "selected_candidate_id", "reason_codes",
        "candidate_assessments", "eligible_candidate_ids",
    }, "policy recommendation")
    return PolicyRecommendationV2(
        case_id=data["case_id"],
        case_fingerprint=data["case_fingerprint"],
        recommendation=RecommendationKind(data["recommendation"]),
        selected_candidate_id=data.get("selected_candidate_id"),
        reason_codes=list(data["reason_codes"]),
        candidate_assessments={k: CandidateAssessment(v) for k, v in data["candidate_assessments"].items()},
        eligible_candidate_ids=list(data["eligible_candidate_ids"]),
    )


def recommendation_run_from_dict(data: dict[str, Any]) -> RecommendationRunV2:
    _require_exact(data, {
        "recommendation_run_version", "recommendation_run_digest", "pipeline_version", "judgment_run_digest",
        "evaluation_corpus_version", "policy_version", "policy_fitted_corpus_version", "run_status",
        "recommendations",
    }, "recommendation run")
    run = RecommendationRunV2(
        recommendation_run_version=data["recommendation_run_version"],
        recommendation_run_digest=data["recommendation_run_digest"],
        pipeline_version=data["pipeline_version"],
        judgment_run_digest=data["judgment_run_digest"],
        evaluation_corpus_version=data["evaluation_corpus_version"],
        policy_version=data["policy_version"],
        policy_fitted_corpus_version=data["policy_fitted_corpus_version"],
        run_status=RunStatus(data["run_status"]),
        recommendations=[policy_recommendation_from_dict(item) for item in data["recommendations"]],
    )
    for name in (
        "recommendation_run_digest", "judgment_run_digest", "evaluation_corpus_version",
        "policy_version", "policy_fitted_corpus_version",
    ):
        validate_digest(getattr(run, name), name)
    if run.pipeline_version not in {"v1_compat", "v2"}:
        raise ValidationError("recommendation run pipeline_version is invalid")
    if run.recommendation_run_version != "2.0.0":
        raise ValidationError("recommendation run version is invalid")
    if len({item.case_id for item in run.recommendations}) != len(run.recommendations):
        raise ValidationError("recommendation run case ids must be unique")
    for item in run.recommendations:
        item.validate()
    if run.run_status is not RunStatus.COMPLETE and run.recommendations:
        raise ValidationError("incomplete or invalid recommendation run cannot contain recommendations")
    if run.recommendation_run_digest != recommendation_run_digest(run):
        raise ValidationError("recommendation run digest mismatch")
    return run
