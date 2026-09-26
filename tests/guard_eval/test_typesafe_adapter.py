import os
import unittest
from types import SimpleNamespace

from guard_eval.config import load_evaluation_config
from guard_eval.corpus import validate_manifest
from guard_eval.models import CheckStatus, GuardDimension, NaturalnessReason
from guard_eval.typesafe_adapter import TypeSafeAdapter


class FakeClient:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.calls = []

    def system_one(self, **kwargs):
        self.calls.append(kwargs)
        if self.error:
            raise self.error
        return self.response

    def close(self):
        pass


def checked_response(case, model="jev-1.13.0"):
    probabilities = {"keep_original": 0.05, "none_of_candidates": 0.05}
    probabilities.update({f"candidate:{candidate.candidate_id}": 0.9 if i == 0 else 0.0 for i, candidate in enumerate(case.candidates)})
    answers = {
        f"naturalness:{reason.value}": SimpleNamespace(noul=0.8) for reason in NaturalnessReason
    }
    answers["preference"] = SimpleNamespace(choice=f"candidate:{case.candidates[0].candidate_id}", confidence=0.9, probabilities=probabilities)
    for candidate in case.candidates:
        for dimension in GuardDimension:
            answers[f"safety:{candidate.candidate_id}:{dimension.value}"] = SimpleNamespace(noul=0.1)
    return SimpleNamespace(model=model, usage=SimpleNamespace(input_tokens=120, output_tokens=20), answers=answers)


class AdapterContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.case = validate_manifest("eval/guard/manifest.json").dev[0]
        cls.config = load_evaluation_config("eval/guard/evaluation-config.json")

    def test_complete_response_becomes_checked_privacy_safe_judgment(self):
        client = FakeClient(checked_response(self.case))
        adapter = TypeSafeAdapter(self.config, api_key="test-key", client_factory=lambda **_: client)
        judgment = adapter.evaluate(self.case)
        self.assertEqual(judgment.status, CheckStatus.CHECKED)
        self.assertEqual(len(client.calls), 1)
        self.assertEqual(set(judgment.candidate_safety_scores), {c.candidate_id for c in self.case.candidates})
        serialized = repr(judgment)
        for forbidden in ("source_span", "candidate_span", "request_body", "exception", "test-key"):
            self.assertNotIn(forbidden, serialized)

    def test_missing_key_returns_unchecked_without_constructing_client(self):
        adapter = TypeSafeAdapter(self.config, api_key=None, client_factory=lambda **_: self.fail("client created"))
        judgment = adapter.evaluate(self.case)
        self.assertEqual((judgment.status, judgment.reason_code), (CheckStatus.UNCHECKED, "missing_api_key"))

    def test_service_failures_map_to_allowlisted_reasons_without_raw_message(self):
        cases = [
            (TimeoutError("raw secret timeout"), "timeout"),
            (type("TypeSafeAuthenticationError", (Exception,), {})("raw auth"), "authentication"),
            (type("TypeSafeRateLimitError", (Exception,), {"status": 429})("raw rate"), "rate_limited"),
            (type("TypeSafeInternalServerError", (Exception,), {"status": 529})("raw overload"), "overloaded"),
            (ConnectionError("raw connection"), "connection"),
            (RuntimeError("raw other"), "service_error"),
        ]
        for error, expected in cases:
            with self.subTest(expected=expected):
                client = FakeClient(error=error)
                result = TypeSafeAdapter(self.config, api_key="test-key", client_factory=lambda **_: client).evaluate(self.case)
                self.assertEqual(result.reason_code, expected)
                self.assertNotIn("raw", repr(result))

    def test_malformed_or_out_of_allowlist_response_is_unchecked(self):
        response = checked_response(self.case)
        response.answers["preference"] = SimpleNamespace(choice="generated_text", confidence=0.9, probabilities={"generated_text": 1.0})
        result = TypeSafeAdapter(self.config, api_key="test-key", client_factory=lambda **_: FakeClient(response)).evaluate(self.case)
        self.assertEqual((result.status, result.reason_code), (CheckStatus.UNCHECKED, "invalid_response"))


if __name__ == "__main__":
    unittest.main()
