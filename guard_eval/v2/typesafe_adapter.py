from __future__ import annotations

import os
import time
from collections.abc import Callable
from typing import Any

from .config import EvaluationConfigV2
from .corpus import case_fingerprint
from .models import (
    AbsoluteJudgmentV2,
    CandidateComponent,
    CheckStatus,
    RankingJudgmentV2,
    SafetyDimension,
    SourceIssue,
    ValidationError,
    validate_probability,
)
from .questions import build_absolute_questions, build_ranking_question, build_request_state


_FROM_ENV = object()


class TypeSafeAdapterV2:
    """Lazy TypeSafe boundary that returns typed judgments and no prose."""

    def __init__(
        self,
        config: EvaluationConfigV2,
        *,
        api_key: str | None | object = _FROM_ENV,
        client_factory: Callable[..., Any] | None = None,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.config = config
        self.api_key = os.environ.get("TYPESAFE_API_KEY") if api_key is _FROM_ENV else api_key
        self.client_factory = client_factory
        self.clock = clock

    def _client(self) -> Any:
        if self.client_factory is not None:
            return self.client_factory(api_key=self.api_key, model=self.config.model_version)
        from typesafe_sdk import RetryPolicy, TypeSafeClient

        retry = RetryPolicy(
            max_retries=max(0, self.config.max_attempts - 1),
            backoff_initial=self.config.backoff_seconds,
            backoff_max=max(self.config.backoff_seconds, self.config.backoff_seconds * 4),
            timeout=self.config.timeout_seconds,
        )
        return TypeSafeClient(
            api_key=self.api_key,
            model=self.config.model_version,
            retry=retry,
            timeout=self.config.timeout_seconds,
        )

    def evaluate_absolute(self, case: Any) -> AbsoluteJudgmentV2:
        fingerprint = case_fingerprint(case)
        if not self.api_key or not str(self.api_key).strip():
            return self._unchecked(case.case_id, fingerprint, "missing_api_key")
        started = self.clock()
        client = None
        try:
            client = self._client()
            response = client.system_one(
                state=build_request_state(case),
                questions=build_absolute_questions(case),
                model=self.config.model_version,
                timeout=self.config.timeout_seconds,
            )
            answers = response.answers
            context = float(answers["source_context_sufficient"].noul)
            validate_probability(context, "source_context_sufficient")
            issues = {issue: float(answers[f"source_issue:{issue.value}"].noul) for issue in SourceIssue}
            components = {
                candidate.candidate_id: {
                    component: float(answers[f"candidate_component:{candidate.candidate_id}:{component.value}"].noul)
                    for component in CandidateComponent
                }
                for candidate in case.candidates
            }
            safety = {
                candidate.candidate_id: {
                    dimension: float(answers[f"safety:{candidate.candidate_id}:{dimension.value}"].noul)
                    for dimension in SafetyDimension
                }
                for candidate in case.candidates
            }
            for name, value in [
                *((issue.value, score) for issue, score in issues.items()),
                *((component.value, score) for scores in components.values() for component, score in scores.items()),
                *((dimension.value, score) for scores in safety.values() for dimension, score in scores.items()),
            ]:
                validate_probability(value, name)
            latency = max(0, round((self.clock() - started) * 1000))
            judgment = AbsoluteJudgmentV2(
                case_id=case.case_id,
                case_fingerprint=fingerprint,
                status=CheckStatus.CHECKED,
                source_context_sufficient=context,
                source_issue_scores=issues,
                candidate_component_scores=components,
                candidate_safety_scores=safety,
                latency_ms=latency,
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                observed_model=str(response.model),
            )
            judgment.validate()
            return judgment
        except (KeyError, AttributeError, TypeError, ValueError, ValidationError):
            return self._unchecked(case.case_id, fingerprint, "invalid_response", started)
        except Exception as exc:
            return self._unchecked(case.case_id, fingerprint, self._reason_for(exc), started)
        finally:
            self._close(client)

    def evaluate_ranking(self, case: Any, eligible_candidate_ids: list[str]) -> RankingJudgmentV2:
        question = build_ranking_question(case, eligible_candidate_ids)
        if question is None:
            raise ValueError("ranking requires at least two eligible candidates")
        eligible = sorted(set(eligible_candidate_ids))
        if not self.api_key or not str(self.api_key).strip():
            return self._unchecked_ranking(eligible, "missing_api_key")
        started = self.clock()
        client = None
        try:
            client = self._client()
            response = client.system_one(
                state=build_request_state(case, eligible_candidate_ids),
                questions={"candidate_ranking": question},
                model=self.config.model_version,
                timeout=self.config.timeout_seconds,
            )
            answer = response.answers["candidate_ranking"]
            probabilities = {
                str(key).removeprefix("candidate:"): float(value)
                for key, value in answer.probabilities.items()
            }
            if set(probabilities) != set(eligible):
                raise ValidationError("ranking options mismatch")
            for candidate_id, value in probabilities.items():
                validate_probability(value, candidate_id)
            if abs(sum(probabilities.values()) - 1.0) > 1e-6:
                raise ValidationError("ranking probabilities must sum to one")
            choice = str(answer.choice).removeprefix("candidate:")
            confidence = float(answer.confidence)
            if choice not in probabilities:
                raise ValidationError("ranking choice is outside shortlist")
            validate_probability(confidence, "ranking confidence")
            judgment = RankingJudgmentV2(
                eligible_candidate_ids=eligible,
                probabilities=probabilities,
                choice=choice,
                confidence=confidence,
                latency_ms=max(0, round((self.clock() - started) * 1000)),
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                observed_model=str(response.model),
            )
            judgment.validate()
            return judgment
        except (KeyError, AttributeError, TypeError, ValueError, ValidationError):
            return self._unchecked_ranking(eligible, "invalid_response", started)
        except Exception as exc:
            return self._unchecked_ranking(eligible, self._reason_for(exc), started)
        finally:
            self._close(client)

    def _unchecked(self, case_id: str, fingerprint: str, reason: str, started: float | None = None) -> AbsoluteJudgmentV2:
        return AbsoluteJudgmentV2(
            case_id=case_id,
            case_fingerprint=fingerprint,
            status=CheckStatus.UNCHECKED,
            reason_code=reason,
            latency_ms=None if started is None else max(0, round((self.clock() - started) * 1000)),
        )

    def _unchecked_ranking(self, eligible: list[str], reason: str, started: float | None = None) -> RankingJudgmentV2:
        return RankingJudgmentV2(
            eligible_candidate_ids=eligible,
            probabilities={},
            choice="",
            confidence=0.0,
            status=CheckStatus.UNCHECKED,
            reason_code=reason,
            latency_ms=None if started is None else max(0, round((self.clock() - started) * 1000)),
        )

    @staticmethod
    def _close(client: Any) -> None:
        if client is not None and hasattr(client, "close"):
            try:
                client.close()
            except Exception:
                pass

    @staticmethod
    def _reason_for(error: BaseException) -> str:
        name = type(error).__name__.lower()
        status = getattr(error, "status", None)
        if isinstance(error, TimeoutError) or "timeout" in name:
            return "timeout"
        if status in {401, 403} or "authentication" in name or "permission" in name:
            return "authentication"
        if status == 429 or "ratelimit" in name or "rate_limit" in name:
            return "rate_limited"
        if status in {502, 503, 529} or "overload" in name:
            return "overloaded"
        if isinstance(error, ConnectionError) or "connection" in name:
            return "connection"
        if "responsevalidation" in name:
            return "invalid_response"
        return "service_error"
