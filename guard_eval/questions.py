from __future__ import annotations

import hashlib
from typing import Any

from guard_eval.config import canonical_json
from guard_eval.models import EvaluationCase, GuardDimension, NaturalnessReason


STATE_FIELDS = ("source_span", "candidates", "context_before", "context_after", "current_intent", "genre")

NATURALNESS_TEMPLATES = {
    NaturalnessReason.LEXICALLY_INCOMPLETE.value: {
        "instructions": "Given the Vietnamese source and its local context, is a word or phrase missing a syllable needed for the intended meaning and register? Judge the source only. Do not rewrite it.",
        "criteria": {
            "true": "A one-syllable form is incomplete for this meaning or role in context, such as hụt where hụt hẫng is required.",
            "false": "The one-syllable word is natural with this meaning, is an intentional abbreviation, or adding a syllable would only be stylistic.",
        },
    },
    NaturalnessReason.UNNATURAL_COLLOCATION.value: {
        "instructions": "Given the Vietnamese source and its local context, is the highlighted wording an unnatural collocation even though its individual words may have meaning? Judge the source only. Do not rewrite it.",
        "criteria": {
            "true": "The surrounding words require a fuller or different conventional expression for the stated intent and genre.",
            "false": "The wording is conventional in context, including the explicit V20 no-flag uses of rời and rà.",
        },
    },
}

PREFERENCE_TEMPLATE = {
    "instructions": "Select exactly one supplied option that best preserves the source meaning, voice, intent, and genre while sounding natural in Vietnamese. Select keep_original when no edit is needed. Select none_of_candidates when an edit is needed but every candidate is inadequate. Never generate or modify text.",
    "option_rule": "keep_original + candidate IDs sorted lexically + none_of_candidates",
    "none_of_candidates_criteria": (
        "The source needs an edit, but every supplied candidate is inadequate because it fails to fix the issue "
        "or loses lexical nuance, image, connotation, voice, intent, or genre. This includes a factually safe "
        "paraphrase that replaces a recoverable Vietnamese expression with a broader synonym."
    ),
}

SAFETY_TEMPLATES = {
    GuardDimension.ADDS_CLAIM.value: ("Does candidate `{candidate_id}` add a factual claim absent from the source?", "It adds a new claim.", "It adds no new claim."),
    GuardDimension.CHANGES_ACTOR_OR_TIME.value: ("Does candidate `{candidate_id}` change the actor or time?", "Actor or time changes.", "Actor and time stay the same."),
    GuardDimension.CHANGES_CAUSALITY_OR_COMMITMENT.value: ("Does candidate `{candidate_id}` change causality, certainty, or commitment?", "Causality, certainty, or commitment changes.", "Those relations and levels stay the same."),
    GuardDimension.CHANGES_ORDER_OR_CONCURRENCY.value: ("Does candidate `{candidate_id}` change event order or concurrency?", "Order or concurrency changes.", "Order and concurrency stay the same."),
    GuardDimension.CHANGES_REGISTER.value: ("Does candidate `{candidate_id}` inappropriately change register or voice for the stated genre and intent?", "Register or voice changes without authorization.", "Register and voice are preserved."),
    GuardDimension.KEEPS_INVALID_PROCESS_METADATA.value: ("Does candidate `{candidate_id}` introduce or keep invalid authoring-process metadata in the deliverable?", "Invalid process metadata remains or is introduced.", "No invalid process metadata is present."),
}


def question_set_version() -> str:
    static_contract = {
        "naturalness": NATURALNESS_TEMPLATES,
        "preference": PREFERENCE_TEMPLATE,
        "safety": SAFETY_TEMPLATES,
        "state_fields": STATE_FIELDS,
        "question_id_rules": ["naturalness:<reason>", "preference", "safety:<candidate_id>:<dimension>"],
    }
    return "sha256:" + hashlib.sha256(canonical_json(static_contract).encode("utf-8")).hexdigest()


def build_state(case: EvaluationCase) -> dict[str, Any]:
    return {
        "source_span": case.source_span,
        "candidates": [
            {"candidate_id": candidate.candidate_id, "candidate_span": candidate.candidate_span}
            for candidate in sorted(case.candidates, key=lambda item: item.candidate_id)
        ],
        "context_before": case.context_before,
        "context_after": case.context_after,
        "current_intent": case.current_intent,
        "genre": case.genre,
    }


def build_questions(case: EvaluationCase) -> dict[str, dict[str, Any]]:
    questions: dict[str, dict[str, Any]] = {}
    for reason in NaturalnessReason:
        template = NATURALNESS_TEMPLATES[reason.value]
        questions[f"naturalness:{reason.value}"] = {
            "type": "noul", "instructions": template["instructions"], "criteria": template["criteria"],
        }
    criteria: dict[str, Any] = {"keep_original": "Keep the original source unchanged."}
    for candidate in sorted(case.candidates, key=lambda item: item.candidate_id):
        criteria[f"candidate:{candidate.candidate_id}"] = f"Use candidate `{candidate.candidate_id}` exactly as supplied in state.candidates."
    criteria["none_of_candidates"] = PREFERENCE_TEMPLATE["none_of_candidates_criteria"]
    questions["preference"] = {"type": "choice", "instructions": PREFERENCE_TEMPLATE["instructions"], "criteria": criteria}
    for candidate in sorted(case.candidates, key=lambda item: item.candidate_id):
        for dimension in GuardDimension:
            instruction, true_criteria, false_criteria = SAFETY_TEMPLATES[dimension.value]
            questions[f"safety:{candidate.candidate_id}:{dimension.value}"] = {
                "type": "noul",
                "instructions": instruction.format(candidate_id=candidate.candidate_id),
                "criteria": {"true": true_criteria, "false": false_criteria},
            }
    return questions
