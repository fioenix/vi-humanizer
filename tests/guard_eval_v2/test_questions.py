from __future__ import annotations

import unittest

from guard_eval.v2.models import RecommendationCaseV2
from guard_eval.v2.questions import (
    REQUEST_STATE_FIELDS,
    absolute_question_set_version,
    build_absolute_questions,
    build_ranking_question,
    build_request_state,
    ranking_question_set_version,
)
from tests.guard_eval_v2.helpers import candidate_dict, case_dict


class QuestionContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.case = RecommendationCaseV2.from_dict(case_dict(candidates=[candidate_dict("c2"), candidate_dict("c1")]))

    def test_state_has_only_request_allowlist_and_sorted_candidate_ids(self) -> None:
        state = build_request_state(self.case)
        self.assertEqual(set(state), set(REQUEST_STATE_FIELDS))
        self.assertEqual([item["candidate_id"] for item in state["candidates"]], ["c1", "c2"])
        serialized = repr(state)
        self.assertNotIn("expected_", serialized)
        self.assertNotIn("provenance", serialized)

    def test_absolute_questions_have_direct_components_and_safety(self) -> None:
        questions = build_absolute_questions(self.case)
        self.assertEqual(questions["source_context_sufficient"]["type"], "noul")
        self.assertIn("source_issue:lexically_incomplete", questions)
        self.assertIn("source_issue:unnatural_collocation", questions)
        for candidate_id in ("c1", "c2"):
            for component in ("fixes_issue", "preserves_meaning_and_nuance", "fits_voice_and_genre"):
                self.assertIn(f"candidate_component:{candidate_id}:{component}", questions)
            self.assertEqual(sum(key.startswith(f"safety:{candidate_id}:") for key in questions), 6)
        self.assertFalse(any(question["type"] == "choice" for question in questions.values()))

    def test_preserve_nuance_distinguishes_completion_from_near_synonym(self) -> None:
        questions = build_absolute_questions(self.case)
        question = questions["candidate_component:c1:preserves_meaning_and_nuance"]
        contract = " ".join([
            question["instructions"],
            question["criteria"]["true"],
            question["criteria"]["false"],
        ]).lower()
        self.assertIn("completes a conventional multi-syllable expression", contract)
        self.assertIn("near-synonym", contract)
        self.assertIn("candidate `c1`", contract)
        self.assertNotIn("generate", contract)

    def test_ranking_exists_only_for_shortlist_of_two_or_more(self) -> None:
        self.assertIsNone(build_ranking_question(self.case, []))
        self.assertIsNone(build_ranking_question(self.case, ["c1"]))
        ranking = build_ranking_question(self.case, ["c2", "c1"])
        self.assertEqual(set(ranking["criteria"]), {"candidate:c1", "candidate:c2"})
        self.assertNotIn("keep_original", ranking["criteria"])
        self.assertNotIn("none_of_candidates", ranking["criteria"])

    def test_question_versions_are_stable_and_separate(self) -> None:
        self.assertTrue(absolute_question_set_version().startswith("sha256:"))
        self.assertTrue(ranking_question_set_version().startswith("sha256:"))
        self.assertNotEqual(absolute_question_set_version(), ranking_question_set_version())


if __name__ == "__main__":
    unittest.main()
