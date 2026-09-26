import copy
import unittest
from unittest.mock import patch

from guard_eval.corpus import validate_manifest
from guard_eval.models import GuardDimension, NaturalnessReason
from guard_eval.questions import PREFERENCE_TEMPLATE, build_questions, build_state, question_set_version


class QuestionContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.case = validate_manifest("eval/guard/manifest.json").dev[0]

    def test_builds_two_nouls_one_choice_and_six_safety_nouls_per_candidate(self):
        questions = build_questions(self.case)
        self.assertEqual(len(questions), 3 + len(self.case.candidates) * len(GuardDimension))
        for reason in NaturalnessReason:
            self.assertEqual(questions[f"naturalness:{reason.value}"]["type"], "noul")
        options = set(questions["preference"]["criteria"])
        self.assertEqual(options, {"keep_original", "none_of_candidates", *[f"candidate:{c.candidate_id}" for c in self.case.candidates]})

    def test_state_has_only_request_allowlist(self):
        state = build_state(self.case)
        self.assertEqual(set(state), {"source_span", "candidates", "context_before", "context_after", "current_intent", "genre"})
        self.assertEqual(set(state["candidates"][0]), {"candidate_id", "candidate_span"})
        text = repr(state)
        for forbidden in ("expected_", "candidate_origin", "baseline", "label_source", "provenance", "case_id"):
            self.assertNotIn(forbidden, text)

    def test_question_set_version_is_order_and_case_invariant(self):
        reordered = copy.deepcopy(self.case)
        reordered.candidates.reverse()
        self.assertEqual(question_set_version(), question_set_version())
        self.assertEqual(list(build_questions(self.case)), list(build_questions(reordered)))
        self.assertTrue(question_set_version().startswith("sha256:"))

    def test_none_of_candidates_covers_safe_paraphrase_that_loses_lexical_nuance(self):
        none_case = next(
            case
            for case in validate_manifest("eval/guard/manifest.json").dev
            if case.expected_preferred_option == "none_of_candidates"
        )
        criterion = build_questions(none_case)["preference"]["criteria"]["none_of_candidates"]
        self.assertIn("broader synonym", criterion)
        self.assertIn("lexical nuance", criterion)

    def test_dynamic_preference_criteria_are_versioned_with_the_template(self):
        before = question_set_version()
        replacement = "Versioned replacement criterion."
        with patch.dict(PREFERENCE_TEMPLATE, {"none_of_candidates_criteria": replacement}):
            criterion = build_questions(self.case)["preference"]["criteria"]["none_of_candidates"]
            self.assertEqual(criterion, replacement)
            self.assertNotEqual(question_set_version(), before)


if __name__ == "__main__":
    unittest.main()
