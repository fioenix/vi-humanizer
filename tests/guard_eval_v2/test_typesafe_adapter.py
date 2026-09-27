from __future__ import annotations

import types
import unittest

from guard_eval.v2.config import EvaluationConfigV2
from guard_eval.v2.models import CheckStatus, RecommendationCaseV2
from guard_eval.v2.questions import absolute_question_set_version, ranking_question_set_version
from guard_eval.v2.typesafe_adapter import TypeSafeAdapterV2
from tests.guard_eval_v2.helpers import candidate_dict, case_dict


def answer(*, noul=None, probabilities=None, choice=None, confidence=None):
    return types.SimpleNamespace(noul=noul, probabilities=probabilities, choice=choice, confidence=confidence)


class FakeClient:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.calls = []

    def system_one(self, **kwargs):
        self.calls.append(kwargs)
        return next(self.responses)

    def close(self):
        return None


class AdapterContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.case = RecommendationCaseV2.from_dict(case_dict(candidates=[candidate_dict("c1"), candidate_dict("c2")]))
        self.config = EvaluationConfigV2(
            config_version="sha256:" + "1" * 64,
            model_version="jev-1.13.0",
            absolute_question_set_version=absolute_question_set_version(),
            ranking_question_set_version=ranking_question_set_version(),
            timeout_seconds=30,
            max_attempts=2,
            backoff_seconds=0.1,
            max_candidates=3,
        )

    def _absolute_response(self):
        answers = {
            "source_context_sufficient": answer(noul=0.9),
            "source_issue:lexically_incomplete": answer(noul=0.8),
            "source_issue:unnatural_collocation": answer(noul=0.1),
        }
        for candidate_id in ("c1", "c2"):
            for component in ("fixes_issue", "preserves_meaning_and_nuance", "fits_voice_and_genre"):
                answers[f"candidate_component:{candidate_id}:{component}"] = answer(noul=0.9)
            for dimension in (
                "adds_claim", "changes_actor_or_time", "changes_causality_or_commitment",
                "changes_order_or_concurrency", "changes_register", "keeps_invalid_process_metadata",
            ):
                answers[f"safety:{candidate_id}:{dimension}"] = answer(noul=0.05)
        return types.SimpleNamespace(
            answers=answers,
            usage=types.SimpleNamespace(input_tokens=100, output_tokens=20),
            model="jev-1.13.0",
        )

    def test_missing_key_returns_unchecked_without_constructing_client(self) -> None:
        called = False

        def factory(**kwargs):
            nonlocal called
            called = True
            return FakeClient([])

        adapter = TypeSafeAdapterV2(self.config, api_key=None, client_factory=factory)
        result = adapter.evaluate_absolute(self.case)
        self.assertEqual(result.status, CheckStatus.UNCHECKED)
        self.assertEqual(result.reason_code, "missing_api_key")
        self.assertFalse(called)

    def test_parses_absolute_and_ranking_without_raw_response(self) -> None:
        ranking_response = types.SimpleNamespace(
            answers={"candidate_ranking": answer(
                probabilities={"candidate:c1": 0.8, "candidate:c2": 0.2},
                choice="candidate:c1", confidence=0.8,
            )},
            usage=types.SimpleNamespace(input_tokens=50, output_tokens=10),
            model="jev-1.13.0",
        )
        client = FakeClient([self._absolute_response(), ranking_response])
        adapter = TypeSafeAdapterV2(self.config, api_key="test", client_factory=lambda **kwargs: client)
        absolute = adapter.evaluate_absolute(self.case)
        ranking = adapter.evaluate_ranking(self.case, ["c1", "c2"])
        self.assertEqual(absolute.status, CheckStatus.CHECKED)
        self.assertEqual(ranking.choice, "c1")
        self.assertEqual(absolute.observed_model, "jev-1.13.0")
        self.assertNotIn("answers", vars(absolute))
        self.assertEqual(len(client.calls), 2)

    def test_model_mismatch_or_malformed_response_is_unchecked(self) -> None:
        response = self._absolute_response()
        response.model = "jev-other"
        adapter = TypeSafeAdapterV2(self.config, api_key="test", client_factory=lambda **kwargs: FakeClient([response]))
        result = adapter.evaluate_absolute(self.case)
        self.assertEqual(result.status, CheckStatus.CHECKED)
        self.assertEqual(result.observed_model, "jev-other")
        blank = self._absolute_response()
        blank.model = ""
        blank_result = TypeSafeAdapterV2(
            self.config, api_key="test", client_factory=lambda **kwargs: FakeClient([blank])
        ).evaluate_absolute(self.case)
        self.assertEqual(blank_result.status, CheckStatus.UNCHECKED)
        self.assertEqual(blank_result.reason_code, "invalid_response")
        invalid_usage = self._absolute_response()
        invalid_usage.usage.input_tokens = -1
        usage_result = TypeSafeAdapterV2(
            self.config, api_key="test", client_factory=lambda **kwargs: FakeClient([invalid_usage])
        ).evaluate_absolute(self.case)
        self.assertEqual(usage_result.status, CheckStatus.UNCHECKED)

    def test_operator_interrupt_is_never_downgraded_to_unchecked(self) -> None:
        class InterruptClient:
            @staticmethod
            def system_one(**kwargs):
                raise KeyboardInterrupt()

            @staticmethod
            def close():
                return None

        adapter = TypeSafeAdapterV2(
            self.config, api_key="test", client_factory=lambda **kwargs: InterruptClient()
        )
        with self.assertRaises(KeyboardInterrupt):
            adapter.evaluate_absolute(self.case)


if __name__ == "__main__":
    unittest.main()
