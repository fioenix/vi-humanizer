from __future__ import annotations

import io
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

from advisor.cli import run
from advisor.client import AdvisorUnavailable, ProviderResponse
from advisor.models import (
    CANDIDATE_COMPONENTS,
    PINNED_MODEL,
    SAFETY_DIMENSIONS,
    SOURCE_ISSUES,
    case_binding,
    validate_advisor_request,
)
from advisor.questions import ABSOLUTE_QUESTION_SET_VERSION, RANKING_QUESTION_SET_VERSION


ROOT = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).parent / "fixtures"


def read_fixture(name: str = "valid-v20.json") -> dict[str, object]:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


class FakeClient:
    def __init__(self, response: ProviderResponse | AdvisorUnavailable) -> None:
        self.response = response
        self.payloads: list[dict[str, object]] = []

    def evaluate(self, payload: dict[str, object]) -> ProviderResponse:
        self.payloads.append(payload)
        if isinstance(self.response, AdvisorUnavailable):
            raise self.response
        return self.response


def run_cli(
    command: str,
    *,
    request: dict[str, object] | None = None,
    client: FakeClient | None = None,
    api_key: str | None = "test-key",
) -> tuple[int, dict[str, object], str]:
    stdout = io.StringIO()
    stderr = io.StringIO()
    stdin = io.StringIO("" if request is None else json.dumps(request, ensure_ascii=False))
    environ = {} if api_key is None else {"TYPESAFE_API_KEY": api_key}

    def client_factory(*, api_key: str | None) -> FakeClient:
        if client is None:
            raise AssertionError("client factory should not be called")
        return client

    code = run(
        [command],
        environ=environ,
        stdin=stdin,
        stdout=stdout,
        stderr=stderr,
        client_factory=client_factory,
    )
    output = json.loads(stdout.getvalue())
    return code, output, stderr.getvalue()


def absolute_response(request: dict[str, object]) -> ProviderResponse:
    answers: dict[str, dict[str, object]] = {
        "source.context_sufficient": {"type": "noul", "noul": 0.91},
        **{
            f"source.{issue}": {"type": "noul", "noul": 0.77}
            for issue in SOURCE_ISSUES
        },
    }
    for candidate_id in request["candidates"]:
        for component in CANDIDATE_COMPONENTS:
            answers[f"candidate.{candidate_id}.{component}"] = {"type": "noul", "noul": 0.84}
        for dimension in SAFETY_DIMENSIONS:
            answers[f"candidate.{candidate_id}.{dimension}"] = {"type": "noul", "noul": 0.06}
    return ProviderResponse(
        model=PINNED_MODEL,
        answers=answers,
        usage={"input_tokens": 100, "output_tokens": 30},
        latency_ms=18,
    )


class AdvisorCliTest(unittest.TestCase):
    def test_no_key_probe_returns_core_only_exit_two_without_client(self) -> None:
        code, output, stderr = run_cli("probe", api_key=None)

        self.assertEqual(code, 2)
        self.assertEqual(output["state"], "core_only")
        self.assertEqual(output["reason_code"], "missing_api_key")
        self.assertIsNone(output["observed_model"])
        self.assertEqual(stderr, "")

    def test_no_key_subprocess_does_not_need_sdk_or_network(self) -> None:
        environ = os.environ.copy()
        environ.pop("TYPESAFE_API_KEY", None)

        result = subprocess.run(
            [sys.executable, "-m", "advisor", "probe"],
            cwd=ROOT,
            env=environ,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output["state"], "core_only")
        self.assertEqual(output["reason_code"], "missing_api_key")
        self.assertEqual(result.stderr, "")

    def test_invalid_input_exits_one_without_echoing_protected_canary(self) -> None:
        request = read_fixture("protected-canary.json")

        code, output, stderr = run_cli("assess", request=request, api_key=None)

        serialized = json.dumps(output, ensure_ascii=False) + stderr
        self.assertEqual(code, 1)
        self.assertEqual(output, {"reason_code": "invalid_input", "schema_version": "1.0.0", "status": "invalid"})
        self.assertNotIn("PRIVATE-CANARY", serialized)

    def test_probe_requires_a_real_typed_pinned_response(self) -> None:
        client = FakeClient(
            ProviderResponse(
                model=PINNED_MODEL,
                answers={"probe.complete": {"type": "noul", "noul": 0.98}},
                usage={"input_tokens": 42, "output_tokens": 7},
                latency_ms=12,
            )
        )

        code, output, _ = run_cli("probe", client=client)

        self.assertEqual(code, 0)
        self.assertEqual(output["state"], "advisor_verified")
        self.assertEqual(output["observed_model"], PINNED_MODEL)
        self.assertEqual(output["usage"], {"input_tokens": 42, "output_tokens": 7})
        self.assertRegex(output["checked_at"], r"^\d{4}-\d{2}-\d{2}T")
        self.assertEqual(len(client.payloads), 1)

    def test_probe_failure_is_unchecked_and_never_reflects_raw_exception(self) -> None:
        client = FakeClient(AdvisorUnavailable("rate_limited", latency_ms=25))

        code, output, stderr = run_cli("probe", client=client)

        self.assertEqual(code, 2)
        self.assertEqual(output["state"], "advisor_unchecked")
        self.assertEqual(output["reason_code"], "rate_limited")
        self.assertEqual(output["latency_ms"], 25)
        self.assertEqual(stderr, "")

    def test_assess_returns_exact_signal_maps_without_prose_or_action(self) -> None:
        request = read_fixture()
        client = FakeClient(absolute_response(request))

        code, output, _ = run_cli("assess", request=request, client=client)

        self.assertEqual(code, 0)
        self.assertEqual(output["status"], "checked")
        self.assertEqual(output["case_id"], request["case_id"])
        self.assertEqual(output["case_binding"], case_binding(validate_advisor_request(request)))
        self.assertEqual(output["question_set_version"], ABSOLUTE_QUESTION_SET_VERSION)
        self.assertEqual(set(output["source_issue_scores"]), set(SOURCE_ISSUES))
        self.assertEqual(set(output["candidate_component_scores"]["candidate_1"]), set(CANDIDATE_COMPONENTS))
        self.assertEqual(set(output["candidate_safety_scores"]["candidate_1"]), set(SAFETY_DIMENSIONS))
        serialized = json.dumps(output, ensure_ascii=False)
        self.assertNotIn("Câu này", serialized)
        for forbidden_key in ("action", "keep", "replace", "reject", "selected_candidate", "prose"):
            self.assertNotIn(forbidden_key, output)

    def test_assess_missing_key_returns_unchecked_with_binding(self) -> None:
        request = read_fixture()

        code, output, _ = run_cli("assess", request=request, api_key=None)

        self.assertEqual(code, 2)
        self.assertEqual(output["status"], "unchecked")
        self.assertEqual(output["reason_code"], "missing_api_key")
        self.assertEqual(output["case_binding"], case_binding(validate_advisor_request(request)))
        self.assertIsNone(output["source_issue_scores"])

    def test_assess_rejects_missing_or_extra_answers_as_invalid_response(self) -> None:
        request = read_fixture()
        response = absolute_response(request)
        response.answers.pop("source.lexically_incomplete")
        client = FakeClient(response)

        code, output, _ = run_cli("assess", request=request, client=client)

        self.assertEqual(code, 2)
        self.assertEqual(output["status"], "unchecked")
        self.assertEqual(output["reason_code"], "invalid_response")

    def test_rank_returns_exact_shortlist_distribution_without_original_option(self) -> None:
        request = read_fixture()
        request["candidates"]["candidate_2"] = {"text": "Câu này nghe còn hụt hẫng."}
        request["eligible_candidate_ids"] = ["candidate_2", "candidate_1"]
        client = FakeClient(
            ProviderResponse(
                model=PINNED_MODEL,
                answers={
                    "candidate_ranking": {
                        "type": "choice",
                        "choice": "candidate_1",
                        "probabilities": {"candidate_1": 0.72, "candidate_2": 0.28},
                        "confidence": 0.55,
                    }
                },
                usage={"input_tokens": 80, "output_tokens": 20},
                latency_ms=14,
            )
        )

        code, output, _ = run_cli("rank", request=request, client=client)

        self.assertEqual(code, 0)
        self.assertEqual(output["ranking_question_set_version"], RANKING_QUESTION_SET_VERSION)
        self.assertNotIn("question_set_version", output)
        self.assertEqual(output["eligible_candidate_ids"], ["candidate_1", "candidate_2"])
        self.assertEqual(set(output["probabilities"]), {"candidate_1", "candidate_2"})
        self.assertEqual(output["choice"], "candidate_1")
        self.assertNotIn("keep_original", json.dumps(output))

    def test_rank_rejects_unknown_or_single_candidate_shortlists_before_network(self) -> None:
        for shortlist in (["candidate_1"], ["candidate_1", "unknown"]):
            with self.subTest(shortlist=shortlist):
                request = read_fixture()
                request["eligible_candidate_ids"] = shortlist
                code, output, _ = run_cli("rank", request=request, api_key=None)
                self.assertEqual(code, 1)
                self.assertEqual(output["reason_code"], "invalid_input")


if __name__ == "__main__":
    unittest.main()
