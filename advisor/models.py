from __future__ import annotations

import copy
import hashlib
import json
import re
import unicodedata
from typing import Any


SCHEMA_VERSION = "1.0.0"
PINNED_MODEL = "jev-1.13.0"
STABLE_ID = re.compile(r"^[a-z][a-z0-9_]{0,63}$")
GENRES = {"blog-ca-nhan", "ky-thuat-doanh-nghiep"}

SOURCE_ISSUES = ("lexically_incomplete", "unnatural_collocation")
CANDIDATE_COMPONENTS = (
    "fixes_issue",
    "preserves_meaning_and_nuance",
    "fits_voice_and_genre",
)
SAFETY_DIMENSIONS = (
    "adds_claim",
    "changes_actor_or_time",
    "changes_causality_or_commitment",
    "changes_order_or_concurrency",
    "changes_register",
    "keeps_invalid_process_metadata",
)


class ContractError(ValueError):
    """A caller supplied data outside the public advisor contract."""


def canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _require_exact_keys(value: object, expected: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != expected:
        raise ContractError(f"invalid {label} schema")
    return value


def _require_text(value: object, label: str, *, allow_empty: bool = False) -> str:
    if not isinstance(value, str) or (not allow_empty and not value.strip()):
        raise ContractError(f"invalid {label}")
    if unicodedata.normalize("NFC", value) != value:
        raise ContractError(f"invalid {label} normalization")
    return value


def _comparison_text(value: str) -> str:
    return " ".join(unicodedata.normalize("NFC", value).split())


def validate_advisor_request(value: object) -> dict[str, Any]:
    request = _require_exact_keys(
        value,
        {"schema_version", "case_id", "source", "context", "current_intent", "genre", "candidates"},
        "advisor request",
    )
    if request["schema_version"] != SCHEMA_VERSION:
        raise ContractError("unsupported schema version")
    if not isinstance(request["case_id"], str) or not STABLE_ID.fullmatch(request["case_id"]):
        raise ContractError("invalid case id")

    source = _require_exact_keys(request["source"], {"pattern", "text"}, "source")
    if source["pattern"] != "V20":
        raise ContractError("unsupported source pattern")
    source_text = _require_text(source["text"], "source text")

    context = _require_exact_keys(request["context"], {"before", "after"}, "context")
    _require_text(context["before"], "context before", allow_empty=True)
    _require_text(context["after"], "context after", allow_empty=True)
    _require_text(request["current_intent"], "current intent")
    if request["genre"] not in GENRES:
        raise ContractError("invalid genre")

    candidates = request["candidates"]
    if not isinstance(candidates, dict) or not 1 <= len(candidates) <= 3:
        raise ContractError("candidates must contain one to three entries")
    seen = {_comparison_text(source_text)}
    canonical_candidates: dict[str, dict[str, str]] = {}
    for candidate_id in sorted(candidates):
        if not isinstance(candidate_id, str) or not STABLE_ID.fullmatch(candidate_id):
            raise ContractError("invalid candidate id")
        candidate = _require_exact_keys(candidates[candidate_id], {"text"}, "candidate")
        text = _require_text(candidate["text"], "candidate text")
        comparable = _comparison_text(text)
        if comparable in seen:
            raise ContractError("duplicate source or candidate text")
        seen.add(comparable)
        canonical_candidates[candidate_id] = {"text": text}

    validated = copy.deepcopy(request)
    validated["candidates"] = canonical_candidates
    return validated


def validate_ranking_request(value: object) -> dict[str, Any]:
    ranking = _require_exact_keys(
        value,
        {
            "schema_version",
            "case_id",
            "source",
            "context",
            "current_intent",
            "genre",
            "candidates",
            "eligible_candidate_ids",
        },
        "ranking request",
    )
    base = {key: item for key, item in ranking.items() if key != "eligible_candidate_ids"}
    validated = validate_advisor_request(base)
    eligible = ranking["eligible_candidate_ids"]
    if not isinstance(eligible, list) or not 2 <= len(eligible) <= 3:
        raise ContractError("ranking requires two to three candidate ids")
    if any(not isinstance(item, str) for item in eligible) or len(set(eligible)) != len(eligible):
        raise ContractError("invalid ranking candidate ids")
    if not set(eligible) <= set(validated["candidates"]):
        raise ContractError("ranking contains an unknown candidate id")
    validated["eligible_candidate_ids"] = sorted(eligible)
    return validated


def case_binding(request: dict[str, Any]) -> str:
    semantic = {
        "source": request["source"],
        "context": request["context"],
        "current_intent": request["current_intent"],
        "genre": request["genre"],
        "candidates": request["candidates"],
    }
    return "sha256:" + hashlib.sha256(canonical_json(semantic).encode("utf-8")).hexdigest()


def valid_probability(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and 0.0 <= float(value) <= 1.0


def validate_usage(value: object) -> dict[str, int]:
    usage = _require_exact_keys(value, {"input_tokens", "output_tokens"}, "usage")
    for key in ("input_tokens", "output_tokens"):
        if not isinstance(usage[key], int) or isinstance(usage[key], bool) or usage[key] < 0:
            raise ContractError("invalid usage")
    return {"input_tokens": usage["input_tokens"], "output_tokens": usage["output_tokens"]}
