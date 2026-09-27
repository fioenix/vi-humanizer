from __future__ import annotations

import hashlib
from typing import Any

from .models import CandidateComponent, RecommendationCaseV2, SafetyDimension, SourceIssue, canonical_json


REQUEST_STATE_FIELDS = (
    "source_span",
    "candidates",
    "context_before",
    "context_after",
    "current_intent",
    "genre",
)

CONTEXT_TEMPLATE = {
    "instructions": (
        "Do the Vietnamese source span, local context, current intent, and genre contain enough "
        "information to judge this exact wording without guessing its intended meaning or voice?"
    ),
    "criteria": {
        "true": "The intended meaning, voice, and role of the highlighted wording are clear enough to judge.",
        "false": "A judgment would require guessing meaning, actor, nuance, voice, or genre conventions.",
    },
}

SOURCE_ISSUE_TEMPLATES = {
    SourceIssue.LEXICALLY_INCOMPLETE.value: {
        "instructions": (
            "Does the Vietnamese source contain a one-syllable word or phrase that is incomplete for "
            "its intended meaning and role in this context? Judge the source only. Do not rewrite it."
        ),
        "criteria": {
            "true": "A conventional additional syllable or component is required for the intended meaning in context.",
            "false": "The shorter form is natural here, intentionally abbreviated, or expansion would only be stylistic.",
        },
    },
    SourceIssue.UNNATURAL_COLLOCATION.value: {
        "instructions": (
            "Does the highlighted Vietnamese wording form an unnatural collocation for the stated "
            "intent and genre, even if each individual word has meaning? Do not rewrite it."
        ),
        "criteria": {
            "true": "Vietnamese convention requires a different or fuller combination for this exact use.",
            "false": "The combination is conventional and natural in this context and genre.",
        },
    },
}

CANDIDATE_COMPONENT_TEMPLATES = {
    CandidateComponent.FIXES_ISSUE.value: (
        "Would replacing only the source span with candidate `{candidate_id}` correct the specific "
        "incomplete or unnatural Vietnamese expression in the source?",
        "It corrects the targeted language problem.",
        "It does not correct the problem or changes unrelated wording only.",
    ),
    CandidateComponent.PRESERVES_MEANING_AND_NUANCE.value: (
        "Does candidate `{candidate_id}` preserve the intended meaning, image, connotation, emphasis, "
        "and lexical nuance of the source? Judge only the supplied candidate. Distinguish a minimal "
        "change that completes a conventional multi-syllable expression from a near-synonym "
        "replacement that shifts the intended lexical nuance.",
        "Meaning and lexical nuance are preserved; a necessary lexical completion may add the "
        "conventional missing syllable without changing the intended word.",
        "Meaning, image, connotation, emphasis, or lexical nuance is lost or changed, including when "
        "a near-synonym sounds fluent but replaces the intended word.",
    ),
    CandidateComponent.FITS_VOICE_AND_GENRE.value: (
        "Does candidate `{candidate_id}` fit the stated voice, current intent, and genre without an "
        "unauthorized style change?",
        "It fits the voice, intent, and genre.",
        "It changes voice or does not fit the stated genre or intent.",
    ),
}

SAFETY_TEMPLATES = {
    SafetyDimension.ADDS_CLAIM.value: ("Does candidate `{candidate_id}` add or remove a factual claim?", "A factual claim changes.", "No factual claim changes."),
    SafetyDimension.CHANGES_ACTOR_OR_TIME.value: ("Does candidate `{candidate_id}` change the actor or time?", "Actor or time changes.", "Actor and time stay the same."),
    SafetyDimension.CHANGES_CAUSALITY_OR_COMMITMENT.value: ("Does candidate `{candidate_id}` change causality, certainty, or commitment?", "Causality, certainty, or commitment changes.", "Those relations and levels stay the same."),
    SafetyDimension.CHANGES_ORDER_OR_CONCURRENCY.value: ("Does candidate `{candidate_id}` change event order or concurrency?", "Order or concurrency changes.", "Order and concurrency stay the same."),
    SafetyDimension.CHANGES_REGISTER.value: ("Does candidate `{candidate_id}` inappropriately change register or voice?", "Register or voice changes without authorization.", "Register and voice are preserved."),
    SafetyDimension.KEEPS_INVALID_PROCESS_METADATA.value: ("Does candidate `{candidate_id}` introduce or keep invalid authoring-process metadata?", "Invalid process metadata remains or is introduced.", "No invalid process metadata is present."),
}

RANKING_TEMPLATE = {
    "instructions": (
        "Among only the eligible candidates supplied, select the best replacement for the source. "
        "Prioritize natural Vietnamese, preservation of intent, voice and lexical nuance, and the "
        "smallest necessary change. Never generate or modify text."
    ),
    "option_rule": "sorted eligible candidate IDs only; at least two",
}


def _digest(contract: dict[str, Any]) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(contract).encode("utf-8")).hexdigest()


def absolute_question_set_version() -> str:
    return _digest({
        "state_fields": REQUEST_STATE_FIELDS,
        "context": CONTEXT_TEMPLATE,
        "source_issues": SOURCE_ISSUE_TEMPLATES,
        "candidate_components": CANDIDATE_COMPONENT_TEMPLATES,
        "safety": SAFETY_TEMPLATES,
        "id_rules": [
            "source_context_sufficient",
            "source_issue:<issue>",
            "candidate_component:<candidate_id>:<component>",
            "safety:<candidate_id>:<dimension>",
        ],
    })


def ranking_question_set_version() -> str:
    return _digest({
        "state_fields": REQUEST_STATE_FIELDS,
        "ranking": RANKING_TEMPLATE,
        "id_rule": "candidate_ranking",
        "option_rule": "candidate:<sorted eligible candidate id>",
    })


def build_request_state(case: RecommendationCaseV2, eligible_candidate_ids: list[str] | None = None) -> dict[str, Any]:
    eligible = None if eligible_candidate_ids is None else set(eligible_candidate_ids)
    candidates = [candidate for candidate in case.candidates if eligible is None or candidate.candidate_id in eligible]
    return {
        "source_span": case.source_span,
        "candidates": [
            {"candidate_id": candidate.candidate_id, "candidate_span": candidate.candidate_span}
            for candidate in sorted(candidates, key=lambda item: item.candidate_id)
        ],
        "context_before": case.context_before,
        "context_after": case.context_after,
        "current_intent": case.current_intent,
        "genre": case.genre,
    }


def build_absolute_questions(case: RecommendationCaseV2) -> dict[str, dict[str, Any]]:
    questions: dict[str, dict[str, Any]] = {
        "source_context_sufficient": {"type": "noul", **CONTEXT_TEMPLATE},
    }
    for issue in SourceIssue:
        questions[f"source_issue:{issue.value}"] = {
            "type": "noul", **SOURCE_ISSUE_TEMPLATES[issue.value],
        }
    for candidate in sorted(case.candidates, key=lambda item: item.candidate_id):
        for component in CandidateComponent:
            instruction, true_criteria, false_criteria = CANDIDATE_COMPONENT_TEMPLATES[component.value]
            questions[f"candidate_component:{candidate.candidate_id}:{component.value}"] = {
                "type": "noul",
                "instructions": instruction.format(candidate_id=candidate.candidate_id),
                "criteria": {"true": true_criteria, "false": false_criteria},
            }
        for dimension in SafetyDimension:
            instruction, true_criteria, false_criteria = SAFETY_TEMPLATES[dimension.value]
            questions[f"safety:{candidate.candidate_id}:{dimension.value}"] = {
                "type": "noul",
                "instructions": instruction.format(candidate_id=candidate.candidate_id),
                "criteria": {"true": true_criteria, "false": false_criteria},
            }
    return questions


def build_ranking_question(case: RecommendationCaseV2, eligible_candidate_ids: list[str]) -> dict[str, Any] | None:
    candidate_ids = {candidate.candidate_id for candidate in case.candidates}
    eligible = sorted(set(eligible_candidate_ids))
    if not set(eligible) <= candidate_ids:
        raise ValueError("ranking shortlist contains an unknown candidate")
    if len(eligible) < 2:
        return None
    return {
        "type": "choice",
        "instructions": RANKING_TEMPLATE["instructions"],
        "criteria": {
            f"candidate:{candidate_id}": f"Use candidate `{candidate_id}` exactly as supplied."
            for candidate_id in eligible
        },
    }
