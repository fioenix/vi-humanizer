from __future__ import annotations

import hashlib
from typing import Any

from .models import (
    CANDIDATE_COMPONENTS,
    PINNED_MODEL,
    SAFETY_DIMENSIONS,
    SOURCE_ISSUES,
    canonical_json,
)


PROBE_STATE = {"text": "Hôm nay trời dịu."}
PROBE_QUESTION = {
    "type": "noul",
    "instructions": "Is `text` a complete Vietnamese sentence?",
    "criteria": {
        "true": "The sentence is complete enough to understand without missing words.",
        "false": "The sentence is incomplete or cannot be understood.",
    },
}

SOURCE_TEMPLATES = {
    "context_sufficient": (
        "Do source.text, context.before, context.after, current_intent and genre contain enough "
        "information to judge the highlighted Vietnamese wording without guessing?"
    ),
    "lexically_incomplete": (
        "Is source.text lexically incomplete for its intended meaning and role in this context? "
        "Judge the source only and do not rewrite it."
    ),
    "unnatural_collocation": (
        "Does source.text form an unnatural Vietnamese collocation for the stated intent and genre, "
        "even if each individual word has meaning? Do not rewrite it."
    ),
}

COMPONENT_TEMPLATES = {
    "fixes_issue": "Would candidates.{candidate_id}.text correct the specific V20 issue in source.text?",
    "preserves_meaning_and_nuance": (
        "Does candidates.{candidate_id}.text preserve the meaning, image, connotation, emphasis and "
        "lexical nuance of source.text?"
    ),
    "fits_voice_and_genre": (
        "Does candidates.{candidate_id}.text fit current_intent and genre without an unauthorized "
        "change of voice?"
    ),
}

SAFETY_TEMPLATES = {
    "adds_claim": "Does candidates.{candidate_id}.text add or remove a factual claim compared with source.text?",
    "changes_actor_or_time": "Does candidates.{candidate_id}.text change the actor or time compared with source.text?",
    "changes_causality_or_commitment": (
        "Does candidates.{candidate_id}.text change causality, certainty or commitment compared with source.text?"
    ),
    "changes_order_or_concurrency": (
        "Does candidates.{candidate_id}.text change event order or concurrency compared with source.text?"
    ),
    "changes_register": (
        "Does candidates.{candidate_id}.text inappropriately change register or voice compared with source.text?"
    ),
    "keeps_invalid_process_metadata": (
        "Does candidates.{candidate_id}.text introduce or keep invalid authoring-process metadata?"
    ),
}


def _digest(value: object) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


ABSOLUTE_QUESTION_SET_VERSION = _digest(
    {
        "source": SOURCE_TEMPLATES,
        "components": COMPONENT_TEMPLATES,
        "safety": SAFETY_TEMPLATES,
        "ids": "source.<signal>|candidate.<stable_id>.<signal>",
        "state": "stable-key-map-v1",
    }
)
RANKING_QUESTION_SET_VERSION = _digest(
    {
        "instructions": "Choose the best exact candidate among an Agent-approved shortlist.",
        "criteria": "candidates.<stable_id>.text",
        "state": "stable-key-map-v1",
    }
)
PROBE_QUESTION_SET_VERSION = _digest({"probe": PROBE_QUESTION, "state": PROBE_STATE})


def _state(request: dict[str, Any], candidate_ids: list[str] | None = None) -> dict[str, Any]:
    allowed = set(candidate_ids) if candidate_ids is not None else set(request["candidates"])
    return {
        "source": request["source"],
        "context": request["context"],
        "current_intent": request["current_intent"],
        "genre": request["genre"],
        "candidates": {
            candidate_id: request["candidates"][candidate_id]
            for candidate_id in sorted(allowed)
        },
    }


def _noul(instructions: str, *, risk: bool = False) -> dict[str, Any]:
    return {
        "type": "noul",
        "instructions": instructions,
        "criteria": {
            "true": "The proposition is supported by the supplied state.",
            "false": "The proposition is not supported by the supplied state.",
            **({} if not risk else {}),
        },
    }


def build_probe_payload() -> dict[str, Any]:
    return {"state": PROBE_STATE, "model": PINNED_MODEL, "questions": {"probe.complete": PROBE_QUESTION}}


def build_absolute_payload(request: dict[str, Any]) -> dict[str, Any]:
    questions: dict[str, dict[str, Any]] = {
        "source.context_sufficient": _noul(SOURCE_TEMPLATES["context_sufficient"]),
        "source.lexically_incomplete": _noul(SOURCE_TEMPLATES["lexically_incomplete"]),
        "source.unnatural_collocation": _noul(SOURCE_TEMPLATES["unnatural_collocation"]),
    }
    for candidate_id in sorted(request["candidates"]):
        for component in CANDIDATE_COMPONENTS:
            questions[f"candidate.{candidate_id}.{component}"] = _noul(
                COMPONENT_TEMPLATES[component].format(candidate_id=candidate_id)
            )
        for dimension in SAFETY_DIMENSIONS:
            questions[f"candidate.{candidate_id}.{dimension}"] = _noul(
                SAFETY_TEMPLATES[dimension].format(candidate_id=candidate_id), risk=True
            )
    return {"state": _state(request), "model": PINNED_MODEL, "questions": questions}


def build_ranking_payload(request: dict[str, Any]) -> dict[str, Any]:
    eligible = request["eligible_candidate_ids"]
    question = {
        "type": "choice",
        "instructions": (
            "Choose the best exact replacement among only the eligible candidates. Prioritize "
            "natural Vietnamese, preserved meaning and voice, and the smallest necessary change. "
            "Do not generate or modify text."
        ),
        "criteria": {
            candidate_id: f"Use candidates.{candidate_id}.text exactly as supplied."
            for candidate_id in eligible
        },
    }
    return {
        "state": _state(request, eligible),
        "model": PINNED_MODEL,
        "questions": {"candidate_ranking": question},
    }
