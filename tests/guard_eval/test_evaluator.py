import copy
import unittest

from guard_eval.config import load_evaluation_config
from guard_eval.corpus import case_fingerprint, validate_manifest
from guard_eval.evaluator import evaluate_cases
from guard_eval.models import CheckStatus, JudgmentSet, RunStatus
from guard_eval.questions import question_set_version
from tests.guard_eval.test_typesafe_adapter import checked_response
from guard_eval.typesafe_adapter import TypeSafeAdapter


class EvaluatorContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.corpus = validate_manifest("eval/guard/manifest.json")
        cls.config = load_evaluation_config("eval/guard/evaluation-config.json")

    def adapter(self, response_for):
        class Client:
            def system_one(self, **kwargs):
                return response_for(kwargs)
            def close(self):
                pass
        return TypeSafeAdapter(self.config, api_key="test-key", client_factory=lambda **_: Client())

    def test_one_request_per_case_and_exact_case_completeness(self):
        calls = []
        cases = self.corpus.dev[:2]
        responses = iter([checked_response(case) for case in cases])
        adapter = self.adapter(lambda kwargs: calls.append(kwargs) or next(responses))
        run = evaluate_cases(cases, adapter, split="dev", corpus_version=self.corpus.corpus_version, config=self.config)
        self.assertEqual(run.run_status, RunStatus.COMPLETE)
        self.assertEqual(len(calls), len(cases))
        self.assertEqual({j.case_id for j in run.judgments}, {case.case_id for case in cases})
        self.assertIsNone(run.policy_version)
        self.assertIsNone(run.pricing_version)

    def test_partial_failure_is_incomplete_not_silently_dropped(self):
        cases = self.corpus.dev[:2]
        class Adapter:
            def evaluate(_, case):
                if case is cases[0]:
                    return TypeSafeAdapter(self.config, api_key=None).evaluate(case)
                client = type("Client", (), {"system_one": lambda self_, **kwargs: checked_response(case), "close": lambda self_: None})()
                return TypeSafeAdapter(self.config, api_key="key", client_factory=lambda **_: client).evaluate(case)
        run = evaluate_cases(cases, Adapter(), split="dev", corpus_version=self.corpus.corpus_version, config=self.config)
        self.assertEqual(run.run_status, RunStatus.INCOMPLETE)
        self.assertEqual(run.counts["unchecked"], 1)

    def test_mixed_response_models_make_run_invalid(self):
        cases = self.corpus.dev[:2]
        responses = iter([checked_response(cases[0]), checked_response(cases[1], model="jev-1.14.0")])
        run = evaluate_cases(cases, self.adapter(lambda _: next(responses)), split="dev", corpus_version=self.corpus.corpus_version, config=self.config)
        self.assertEqual(run.run_status, RunStatus.INVALID)

    def test_candidate_and_case_reorder_preserve_judgment_semantics(self):
        original = self.corpus.dev[0]
        reordered = copy.deepcopy(original)
        reordered.candidates.reverse()
        client = type("Client", (), {"system_one": lambda self_, **kwargs: checked_response(original), "close": lambda self_: None})()
        judgment = TypeSafeAdapter(self.config, api_key="key", client_factory=lambda **_: client).evaluate(reordered)
        self.assertEqual(judgment.status, CheckStatus.CHECKED)
        self.assertEqual(judgment.case_fingerprint, case_fingerprint(original))
        self.assertEqual(set(judgment.candidate_safety_scores), {candidate.candidate_id for candidate in original.candidates})


if __name__ == "__main__":
    unittest.main()
