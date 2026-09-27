from __future__ import annotations

import json
from collections.abc import Iterable
from typing import Any

from .models import ALLOWED_RECOMMENDATION_REASONS, ALLOWED_SERVICE_REASONS, to_jsonable


class PrivacyError(ValueError):
    """Raised when a generated artifact contains forbidden content."""


FORBIDDEN_KEYS = frozenset({
    "source_span",
    "candidate_span",
    "candidates",
    "candidate_origin",
    "context_before",
    "context_after",
    "current_intent",
    "expected_recommendation",
    "expected_source_issues",
    "expected_acceptable",
    "expected_components",
    "expected_safety",
    "label_authority",
    "provenance",
    "lineage",
    "baseline",
    "api_key",
    "request_body",
    "response_body",
    "exception",
})


def _keys(value: Any) -> Iterable[str]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield str(key)
            yield from _keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from _keys(child)


def _reason_codes(value: Any) -> Iterable[str]:
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "reason_code" and child is not None:
                yield str(child)
            elif key == "reason_codes" and isinstance(child, list):
                yield from (str(item) for item in child)
            yield from _reason_codes(child)
    elif isinstance(value, list):
        for child in value:
            yield from _reason_codes(child)


def validate_artifact_privacy(
    artifact: Any,
    *,
    raw_strings: Iterable[str] = (),
    identity_tokens: Iterable[str] = (),
    serialized_override: str | None = None,
) -> None:
    data = to_jsonable(artifact)
    leaked_keys = FORBIDDEN_KEYS.intersection(_keys(data))
    if leaked_keys:
        raise PrivacyError(f"artifact contains forbidden keys: {sorted(leaked_keys)}")
    allowed_reasons = ALLOWED_SERVICE_REASONS | ALLOWED_RECOMMENDATION_REASONS
    invalid_reasons = sorted({reason for reason in _reason_codes(data) if reason not in allowed_reasons})
    if invalid_reasons:
        raise PrivacyError(f"artifact contains non-allowlisted reason codes: {invalid_reasons}")
    serialized = serialized_override
    if serialized is None:
        serialized = json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for value in [*raw_strings, *identity_tokens]:
        if value and value in serialized:
            raise PrivacyError("artifact contains a forbidden raw string")
