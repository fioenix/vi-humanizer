from __future__ import annotations

import copy
import json
import re
import unittest
from pathlib import Path

from advisor.models import validate_advisor_request, validate_ranking_request
from advisor.questions import (
    ABSOLUTE_QUESTION_SET_VERSION,
    RANKING_QUESTION_SET_VERSION,
    build_absolute_payload,
    build_ranking_payload,
)


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = Path(__file__).parent / "fixtures" / "valid-v20.json"


def request_with_three_candidates() -> dict[str, object]:
    request = json.loads(FIXTURE.read_text(encoding="utf-8"))
    request["candidates"] = {
        "candidate_b": {"text": "Câu này nghe vẫn còn hụt hẫng."},
        "candidate_a": {"text": "Câu này đọc lên thấy hụt hẫng."},
        "candidate_c": {"text": "Câu này khiến người đọc thấy hụt hẫng."},
    }
    return request


class AdvisorQuestionsTest(unittest.TestCase):
    def test_absolute_payload_uses_candidate_map_and_stable_state_paths(self) -> None:
        payload = build_absolute_payload(validate_advisor_request(request_with_three_candidates()))

        self.assertIsInstance(payload["state"]["candidates"], dict)
        self.assertEqual(list(payload["state"]["candidates"]), ["candidate_a", "candidate_b", "candidate_c"])
        candidate_questions = {
            key: question
            for key, question in payload["questions"].items()
            if key.startswith("candidate.")
        }
        self.assertEqual(len(candidate_questions), 27)
        for question_id, question in candidate_questions.items():
            candidate_id = question_id.split(".")[1]
            self.assertIn(f"candidates.{candidate_id}.text", question["instructions"])
            self.assertNotRegex(question["instructions"], r"candidates\.\d+")

    def test_absolute_payload_has_exact_issue_component_and_safety_inventory(self) -> None:
        request = json.loads(FIXTURE.read_text(encoding="utf-8"))
        questions = build_absolute_payload(validate_advisor_request(request))["questions"]

        self.assertEqual(
            set(questions),
            {
                "source.context_sufficient",
                "source.lexically_incomplete",
                "source.unnatural_collocation",
                "candidate.candidate_1.fixes_issue",
                "candidate.candidate_1.preserves_meaning_and_nuance",
                "candidate.candidate_1.fits_voice_and_genre",
                "candidate.candidate_1.adds_claim",
                "candidate.candidate_1.changes_actor_or_time",
                "candidate.candidate_1.changes_causality_or_commitment",
                "candidate.candidate_1.changes_order_or_concurrency",
                "candidate.candidate_1.changes_register",
                "candidate.candidate_1.keeps_invalid_process_metadata",
            },
        )

    def test_candidate_insertion_order_does_not_change_payload_bytes(self) -> None:
        request = request_with_three_candidates()
        reordered = copy.deepcopy(request)
        reordered["candidates"] = dict(reversed(list(request["candidates"].items())))

        first = build_absolute_payload(validate_advisor_request(request))
        second = build_absolute_payload(validate_advisor_request(reordered))

        self.assertEqual(first, second)

    def test_target_at_each_batch_position_keeps_its_own_stable_path(self) -> None:
        for ordered_ids in (
            ["target", "candidate_b", "candidate_c"],
            ["candidate_b", "target", "candidate_c"],
            ["candidate_b", "candidate_c", "target"],
        ):
            request = json.loads(FIXTURE.read_text(encoding="utf-8"))
            request["candidates"] = {
                candidate_id: {"text": f"Bản sửa dành cho {candidate_id}."}
                for candidate_id in ordered_ids
            }
            payload = build_absolute_payload(validate_advisor_request(request))
            target_questions = [
                question
                for key, question in payload["questions"].items()
                if key.startswith("candidate.target.")
            ]
            self.assertEqual(len(target_questions), 9)
            self.assertTrue(
                all("candidates.target.text" in question["instructions"] for question in target_questions)
            )

    def test_ranking_payload_uses_only_the_sorted_shortlist(self) -> None:
        request = request_with_three_candidates()
        request["eligible_candidate_ids"] = ["candidate_c", "candidate_a"]

        payload = build_ranking_payload(validate_ranking_request(request))

        self.assertEqual(list(payload["state"]["candidates"]), ["candidate_a", "candidate_c"])
        question = payload["questions"]["candidate_ranking"]
        self.assertEqual(list(question["criteria"]), ["candidate_a", "candidate_c"])
        self.assertNotIn("keep_original", question["criteria"])
        for candidate_id, criterion in question["criteria"].items():
            self.assertIn(f"candidates.{candidate_id}.text", criterion)

    def test_runtime_question_versions_are_sha256_and_do_not_reuse_frozen_v2_versions(self) -> None:
        frozen = json.loads((ROOT / "eval/guard/v2/evaluation-config.json").read_text(encoding="utf-8"))

        self.assertRegex(ABSOLUTE_QUESTION_SET_VERSION, r"^sha256:[0-9a-f]{64}$")
        self.assertRegex(RANKING_QUESTION_SET_VERSION, r"^sha256:[0-9a-f]{64}$")
        self.assertNotEqual(ABSOLUTE_QUESTION_SET_VERSION, frozen["absolute_question_set_version"])
        self.assertNotEqual(RANKING_QUESTION_SET_VERSION, frozen["ranking_question_set_version"])


if __name__ == "__main__":
    unittest.main()
