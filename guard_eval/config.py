from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


class ConfigError(ValueError):
    """Raised when a versioned evaluation configuration is invalid."""


def canonical_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def canonical_digest(data: dict[str, Any], version_field: str) -> str:
    semantic = {key: value for key, value in data.items() if key != version_field}
    return "sha256:" + hashlib.sha256(canonical_json(semantic).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class EvaluationConfig:
    config_version: str
    model_version: str
    question_set_version: str
    timeout_seconds: float
    max_attempts: int
    backoff_seconds: float


@dataclass(frozen=True)
class PricingSnapshot:
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
        raise ConfigError(f"cannot read config: {type(exc).__name__}") from exc
    if not isinstance(data, dict):
        raise ConfigError("configuration root must be an object")
    return data


def load_evaluation_config(path: str | Path) -> EvaluationConfig:
    data = _read(path)
    expected = canonical_digest(data, "config_version")
    if data.get("config_version") != expected:
        raise ConfigError("config digest mismatch")
    retry = data.get("retry_policy")
    if not isinstance(retry, dict):
        raise ConfigError("retry_policy must be an object")
    timeout = data.get("timeout_seconds")
    attempts = retry.get("max_attempts")
    backoff = retry.get("backoff_seconds")
    if not isinstance(timeout, (int, float)) or isinstance(timeout, bool) or timeout <= 0:
        raise ConfigError("timeout_seconds must be positive")
    if not isinstance(attempts, int) or isinstance(attempts, bool) or not 1 <= attempts <= 10:
        raise ConfigError("max_attempts must be between 1 and 10")
    if not isinstance(backoff, (int, float)) or isinstance(backoff, bool) or not 0 <= backoff <= 60:
        raise ConfigError("backoff_seconds must be finite and between 0 and 60")
    for field in ("model_version", "question_set_version"):
        if not isinstance(data.get(field), str) or not data[field]:
            raise ConfigError(f"{field} must be a non-empty string")
    return EvaluationConfig(expected, data["model_version"], data["question_set_version"], float(timeout), attempts, float(backoff))


def load_pricing_snapshot(path: str | Path, *, expected_model: str | None = None) -> PricingSnapshot:
    data = _read(path)
    expected = canonical_digest(data, "pricing_version")
    if data.get("pricing_version") != expected:
        raise ConfigError("pricing digest mismatch")
    model = data.get("model_version")
    if expected_model is not None and model != expected_model:
        raise ConfigError("pricing model does not match evaluation model")
    costs = (data.get("input_cost_per_million_tokens"), data.get("output_cost_per_million_tokens"))
    if any(not isinstance(value, (int, float)) or isinstance(value, bool) or value < 0 for value in costs):
        raise ConfigError("pricing costs must be non-negative numbers")
    source = data.get("source", "")
    if urlparse(source).scheme != "https":
        raise ConfigError("pricing source must use HTTPS")
    currency = data.get("currency")
    if not isinstance(currency, str) or len(currency) != 3 or not currency.isupper():
        raise ConfigError("currency must be an ISO 4217 code")
    return PricingSnapshot(expected, model, currency, float(costs[0]), float(costs[1]), data["observed_at"], source)
