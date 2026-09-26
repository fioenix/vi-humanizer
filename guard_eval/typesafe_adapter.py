from __future__ import annotations

import os
import time
from collections.abc import Callable, Mapping
from typing import Any

from guard_eval.config import EvaluationConfig
from guard_eval.corpus import case_fingerprint
from guard_eval.models import CheckStatus, GuardDimension, JudgmentSet, NaturalnessReason, ValidationError
from guard_eval.questions import build_questions, build_state


_FROM_ENV = object()


class TypeSafeAdapter:
    """Small, lazy boundary around the TypeSafe SDK.

    The adapter returns only typed judgments. It never returns request state, raw
    exceptions, or generated prose.
    """

    def __init__(
        self,
        config: EvaluationConfig,
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

    def evaluate(self, case: Any) -> JudgmentSet:
        fingerprint = case_fingerprint(case)
        if not self.api_key or not self.api_key.strip():
            return self._unchecked(case.case_id, fingerprint, "missing_api_key")
        started = self.clock()
        client = None
        try:
            client = self._client()
            response = client.system_one(
                state=build_state(case),
                questions=build_questions(case),
                model=self.config.model_version,
                timeout=self.config.timeout_seconds,
            )
            latency = max(0, round((self.clock() - started) * 1000))
            judgment = self._parse(case, fingerprint, response, latency)
            judgment.validate([f"candidate:{candidate.candidate_id}" for candidate in case.candidates])
            return judgment
        except (KeyError, AttributeError, TypeError, ValueError, ValidationError):
            return self._unchecked(case.case_id, fingerprint, "invalid_response", started)
        except BaseException as exc:
            return self._unchecked(case.case_id, fingerprint, self._reason_for(exc), started)
        finally:
            if client is not None and hasattr(client, "close"):
                try:
                    client.close()
                except Exception:
                    pass

    def _parse(self, case: Any, fingerprint: str, response: Any, latency_ms: int) -> JudgmentSet:
        answers = response.answers
        naturalness = {
            reason: float(answers[f"naturalness:{reason.value}"].noul) for reason in NaturalnessReason
        }
        preference = answers["preference"]
        safety = {
            candidate.candidate_id: {
                dimension: float(answers[f"safety:{candidate.candidate_id}:{dimension.value}"].noul)
                for dimension in GuardDimension
            }
            for candidate in case.candidates
        }
        usage = response.usage
        return JudgmentSet(
            case_id=case.case_id,
            case_fingerprint=fingerprint,
            status=CheckStatus.CHECKED,
            naturalness_scores=naturalness,
            preference_probabilities={str(key): float(value) for key, value in preference.probabilities.items()},
            preference_choice=str(preference.choice),
            preference_confidence=float(preference.confidence),
            candidate_safety_scores=safety,
            reason_code=None,
            latency_ms=latency_ms,
            input_tokens=usage.input_tokens,
            output_tokens=usage.output_tokens,
            model_version=str(response.model),
        )

    def _unchecked(self, case_id: str, fingerprint: str, reason: str, started: float | None = None) -> JudgmentSet:
        latency = None if started is None else max(0, round((self.clock() - started) * 1000))
        return JudgmentSet(case_id=case_id, case_fingerprint=fingerprint, status=CheckStatus.UNCHECKED, reason_code=reason, latency_ms=latency)

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
