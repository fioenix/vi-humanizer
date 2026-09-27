from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from .models import canonical_digest, validate_digest


class ConfigError(ValueError):
    """Raised when a versioned v2 configuration is invalid."""


@dataclass(frozen=True)
class EvaluationConfigV2:
    config_version: str
    model_version: str
    absolute_question_set_version: str
    ranking_question_set_version: str
    timeout_seconds: float
    max_attempts: int
    backoff_seconds: float
    max_candidates: int


@dataclass(frozen=True)
class PricingSnapshotV2:
    pricing_version: str
    model_version: str
    currency: str
    input_cost_per_million_tokens: float
    output_cost_per_million_tokens: float
    observed_at: str
    source: str


def _read(path: str | Path) -> dict[str, Any]:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ConfigError(f"cannot read configuration: {type(exc).__name__}") from exc
    if not isinstance(data, dict):
        raise ConfigError("configuration root must be an object")
    return data


def _digest(value: str, name: str) -> None:
    try:
        validate_digest(value, name)
    except ValueError as exc:
        raise ConfigError(str(exc)) from exc


def load_evaluation_config(path: str | Path) -> EvaluationConfigV2:
    data = _read(path)
    required = {
        "config_version", "model_version", "absolute_question_set_version",
        "ranking_question_set_version", "timeout_seconds", "retry_policy", "max_candidates",
    }
    if set(data) != required:
        raise ConfigError("evaluation config fields mismatch")
    expected = canonical_digest(data, "config_version")
    if data.get("config_version") != expected:
        raise ConfigError("config digest mismatch")
    if data.get("model_version") != "jev-1.13.0":
        raise ConfigError("model_version must pin exact jev-1.13.0")
    for field in ("absolute_question_set_version", "ranking_question_set_version"):
        if not isinstance(data.get(field), str):
            raise ConfigError(f"{field} must be a digest")
        _digest(data[field], field)
    retry = data.get("retry_policy")
    if not isinstance(retry, dict):
        raise ConfigError("retry_policy must be an object")
    if set(retry) != {"max_attempts", "backoff_seconds"}:
        raise ConfigError("retry_policy fields mismatch")
    timeout = data.get("timeout_seconds")
    attempts = retry.get("max_attempts")
    backoff = retry.get("backoff_seconds")
    max_candidates = data.get("max_candidates")
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not math.isfinite(timeout) or timeout <= 0:
        raise ConfigError("timeout_seconds must be positive")
    if isinstance(attempts, bool) or not isinstance(attempts, int) or not 1 <= attempts <= 10:
        raise ConfigError("max_attempts must be between 1 and 10")
    if isinstance(backoff, bool) or not isinstance(backoff, (int, float)) or not math.isfinite(backoff) or not 0 <= backoff <= 60:
        raise ConfigError("backoff_seconds must be between 0 and 60")
    if isinstance(max_candidates, bool) or not isinstance(max_candidates, int) or max_candidates != 3:
        raise ConfigError("max_candidates must be exactly 3")
    return EvaluationConfigV2(
        config_version=expected,
        model_version=data["model_version"],
        absolute_question_set_version=data["absolute_question_set_version"],
        ranking_question_set_version=data["ranking_question_set_version"],
        timeout_seconds=float(timeout),
        max_attempts=attempts,
        backoff_seconds=float(backoff),
        max_candidates=max_candidates,
    )


def load_pricing_snapshot(path: str | Path, *, expected_model: str | None = None) -> PricingSnapshotV2:
    data = _read(path)
    required = {
        "pricing_version", "model_version", "currency", "input_cost_per_million_tokens",
        "output_cost_per_million_tokens", "observed_at", "source",
    }
    if set(data) != required:
        raise ConfigError("pricing fields mismatch")
    expected = canonical_digest(data, "pricing_version")
    if data.get("pricing_version") != expected:
        raise ConfigError("pricing digest mismatch")
    model = data.get("model_version")
    if model != "jev-1.13.0":
        raise ConfigError("pricing model_version must pin exact jev-1.13.0")
    if expected_model is not None and model != expected_model:
        raise ConfigError("pricing model does not match evaluation model")
    costs = (data.get("input_cost_per_million_tokens"), data.get("output_cost_per_million_tokens"))
    if any(
        isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0
        for value in costs
    ):
        raise ConfigError("pricing costs must be non-negative numbers")
    currency = data.get("currency")
    if not isinstance(currency, str) or len(currency) != 3 or not currency.isupper():
        raise ConfigError("currency must be an ISO 4217 code")
    source = data.get("source", "")
    if urlparse(source).scheme != "https":
        raise ConfigError("pricing source must use HTTPS")
    observed_at = data.get("observed_at")
    if not isinstance(observed_at, str):
        raise ConfigError("observed_at must be an RFC3339 UTC timestamp")
    try:
        parsed_at = datetime.fromisoformat(observed_at.removesuffix("Z") + ("+00:00" if observed_at.endswith("Z") else ""))
    except ValueError as exc:
        raise ConfigError("observed_at must be an RFC3339 UTC timestamp") from exc
    if parsed_at.tzinfo is None:
        raise ConfigError("observed_at must include a timezone")
    return PricingSnapshotV2(
        pricing_version=expected,
        model_version=model,
        currency=currency,
        input_cost_per_million_tokens=float(costs[0]),
        output_cost_per_million_tokens=float(costs[1]),
        observed_at=observed_at,
        source=source,
    )
