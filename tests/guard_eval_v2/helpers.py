from __future__ import annotations

from typing import Any


def candidate_dict(candidate_id: str = "c1", *, acceptable: bool = True) -> dict[str, Any]:
    return {
        "candidate_id": candidate_id,
        "candidate_span": f"phương án {candidate_id}",
        "candidate_origin": {
            "kind": "maintainer_fixture",
            "reference": "tests/guard_eval_v2/fixtures",
            "authority": "maintainer",
        },
        "expected_acceptable": acceptable,
        "expected_components": {
            "fixes_issue": acceptable,
            "preserves_meaning_and_nuance": True,
            "fits_voice_and_genre": True,
        },
        "expected_safety": {
            "adds_claim": False,
            "changes_actor_or_time": False,
            "changes_causality_or_commitment": False,
            "changes_order_or_concurrency": False,
            "changes_register": False,
            "keeps_invalid_process_metadata": False,
        },
    }


def case_dict(*, case_id: str = "case-1", split: str = "dev", candidates: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    return {
        "schema_version": "2.0.0",
        "case_id": case_id,
        "split": split,
        "source_span": "Tôi thấy hơi hụt.",
        "context_before": "",
        "context_after": "",
        "current_intent": "Diễn tả cảm giác chưa trọn vẹn.",
        "genre": "blog cá nhân",
        "candidates": [candidate_dict()] if candidates is None else candidates,
        "expected_recommendation": "replace",
        "expected_selected_candidate_id": "c1",
        "expected_source_issues": {
            "lexically_incomplete": True,
            "unnatural_collocation": False,
        },
        "label_authority": {
            "authority": "maintainer",
            "reference": "neutral-fixture",
            "confirmed_at": "2026-09-27T00:00:00Z",
        },
        "provenance": {
            "kind": "neutral_fixture",
            "reference": "tests/guard_eval_v2/fixtures",
        },
        "lineage": None,
    }
