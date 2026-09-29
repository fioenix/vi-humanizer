from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Callable, TextIO

from .client import AdvisorUnavailable, ProviderResponse, TypeSafeClient
from .models import (
    CANDIDATE_COMPONENTS,
    PINNED_MODEL,
    SAFETY_DIMENSIONS,
    SCHEMA_VERSION,
    SOURCE_ISSUES,
    ContractError,
    case_binding,
    valid_probability,
    validate_advisor_request,
    validate_ranking_request,
)
from .questions import (
    ABSOLUTE_QUESTION_SET_VERSION,
    PROBE_QUESTION_SET_VERSION,
    RANKING_QUESTION_SET_VERSION,
    build_absolute_payload,
    build_probe_payload,
    build_ranking_payload,
)


ClientFactory = Callable[..., TypeSafeClient]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _write(stream: TextIO, value: dict[str, Any]) -> None:
    stream.write(json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + "\n")


def _invalid() -> dict[str, Any]:
    return {"schema_version": SCHEMA_VERSION, "status": "invalid", "reason_code": "invalid_input"}


def _probe_result(
    *,
    state: str,
    reason_code: str | None,
    response: ProviderResponse | None = None,
) -> dict[str, Any]:
    attempted = response is not None or state == "advisor_unchecked"
    return {
        "schema_version": SCHEMA_VERSION,
        "state": state,
        "reason_code": reason_code,
        "observed_model": None if response is None else response.model,
        "question_set_version": PROBE_QUESTION_SET_VERSION,
        "checked_at": _now() if attempted else None,
        "latency_ms": None if response is None else response.latency_ms,
        "usage": None if response is None else response.usage,
    }


def _unchecked_assess(request: dict[str, Any], reason: str, latency_ms: int | None) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "unchecked",
        "case_id": request["case_id"],
        "case_binding": case_binding(request),
        "question_set_version": ABSOLUTE_QUESTION_SET_VERSION,
        "observed_model": None,
        "source_context_sufficient": None,
        "source_issue_scores": None,
        "candidate_component_scores": None,
        "candidate_safety_scores": None,
        "reason_code": reason,
        "latency_ms": latency_ms,
        "usage": None,
    }


def _unchecked_rank(request: dict[str, Any], reason: str, latency_ms: int | None) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "unchecked",
        "case_id": request["case_id"],
        "case_binding": case_binding(request),
        "ranking_question_set_version": RANKING_QUESTION_SET_VERSION,
        "observed_model": None,
        "eligible_candidate_ids": request["eligible_candidate_ids"],
        "choice": None,
        "probabilities": None,
        "confidence": None,
        "reason_code": reason,
        "latency_ms": latency_ms,
        "usage": None,
    }


def _noul(answers: dict[str, Any], question_id: str) -> float:
    if question_id not in answers:
        raise ContractError("missing answer")
    answer = answers[question_id]
    if not isinstance(answer, dict) or set(answer) != {"type", "noul"}:
        raise ContractError("invalid noul answer")
    if answer["type"] != "noul" or not valid_probability(answer["noul"]):
        raise ContractError("invalid noul value")
    return float(answer["noul"])


def _parse_probe(response: ProviderResponse) -> None:
    if response.model != PINNED_MODEL or set(response.answers) != {"probe.complete"}:
        raise ContractError("invalid probe response")
    _noul(response.answers, "probe.complete")


def _parse_absolute(request: dict[str, Any], response: ProviderResponse) -> dict[str, Any]:
    expected = {
        "source.context_sufficient",
        *(f"source.{issue}" for issue in SOURCE_ISSUES),
        *(
            f"candidate.{candidate_id}.{signal}"
            for candidate_id in request["candidates"]
            for signal in (*CANDIDATE_COMPONENTS, *SAFETY_DIMENSIONS)
        ),
    }
    if response.model != PINNED_MODEL or set(response.answers) != expected:
        raise ContractError("invalid absolute response")
    components = {
        candidate_id: {
            component: _noul(response.answers, f"candidate.{candidate_id}.{component}")
            for component in CANDIDATE_COMPONENTS
        }
        for candidate_id in request["candidates"]
    }
    safety = {
        candidate_id: {
            dimension: _noul(response.answers, f"candidate.{candidate_id}.{dimension}")
            for dimension in SAFETY_DIMENSIONS
        }
        for candidate_id in request["candidates"]
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "checked",
        "case_id": request["case_id"],
        "case_binding": case_binding(request),
        "question_set_version": ABSOLUTE_QUESTION_SET_VERSION,
        "observed_model": response.model,
        "source_context_sufficient": _noul(response.answers, "source.context_sufficient"),
        "source_issue_scores": {
            issue: _noul(response.answers, f"source.{issue}") for issue in SOURCE_ISSUES
        },
        "candidate_component_scores": components,
        "candidate_safety_scores": safety,
        "reason_code": None,
        "latency_ms": response.latency_ms,
        "usage": response.usage,
    }


def _parse_ranking(request: dict[str, Any], response: ProviderResponse) -> dict[str, Any]:
    if response.model != PINNED_MODEL or set(response.answers) != {"candidate_ranking"}:
        raise ContractError("invalid ranking response")
    answer = response.answers["candidate_ranking"]
    if not isinstance(answer, dict) or set(answer) != {"type", "choice", "probabilities", "confidence"}:
        raise ContractError("invalid choice answer")
    eligible = request["eligible_candidate_ids"]
    probabilities = answer["probabilities"]
    if (
        answer["type"] != "choice"
        or answer["choice"] not in eligible
        or not isinstance(probabilities, dict)
        or set(probabilities) != set(eligible)
        or not all(valid_probability(value) for value in probabilities.values())
        or abs(sum(float(value) for value in probabilities.values()) - 1.0) > 1e-6
        or not valid_probability(answer["confidence"])
    ):
        raise ContractError("invalid choice value")
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "checked",
        "case_id": request["case_id"],
        "case_binding": case_binding(request),
        "ranking_question_set_version": RANKING_QUESTION_SET_VERSION,
        "observed_model": response.model,
        "eligible_candidate_ids": eligible,
        "choice": answer["choice"],
        "probabilities": {key: float(probabilities[key]) for key in eligible},
        "confidence": float(answer["confidence"]),
        "reason_code": None,
        "latency_ms": response.latency_ms,
        "usage": response.usage,
    }


def run(
    argv: list[str] | None = None,
    *,
    environ: dict[str, str] | None = None,
    stdin: TextIO | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
    client_factory: ClientFactory = TypeSafeClient,
) -> int:
    del stderr  # Contract errors use sanitized JSON on stdout only.
    args = list(sys.argv[1:] if argv is None else argv)
    env = os.environ if environ is None else environ
    input_stream = sys.stdin if stdin is None else stdin
    output_stream = sys.stdout if stdout is None else stdout
    if len(args) != 1 or args[0] not in {"probe", "assess", "rank"}:
        _write(output_stream, _invalid())
        return 1
    command = args[0]
    api_key = env.get("TYPESAFE_API_KEY")

    request: dict[str, Any] | None = None
    if command != "probe":
        try:
            raw = json.load(input_stream)
            request = validate_advisor_request(raw) if command == "assess" else validate_ranking_request(raw)
        except (json.JSONDecodeError, UnicodeDecodeError, ContractError, TypeError, ValueError):
            _write(output_stream, _invalid())
            return 1

    if not isinstance(api_key, str) or not api_key.strip():
        if command == "probe":
            _write(output_stream, _probe_result(state="core_only", reason_code="missing_api_key"))
        elif command == "assess":
            _write(output_stream, _unchecked_assess(request, "missing_api_key", None))
        else:
            _write(output_stream, _unchecked_rank(request, "missing_api_key", None))
        return 2

    client = client_factory(api_key=api_key)
    try:
        if command == "probe":
            response = client.evaluate(build_probe_payload())
            _parse_probe(response)
            output = _probe_result(state="advisor_verified", reason_code=None, response=response)
        elif command == "assess":
            response = client.evaluate(build_absolute_payload(request))
            output = _parse_absolute(request, response)
        else:
            response = client.evaluate(build_ranking_payload(request))
            output = _parse_ranking(request, response)
    except AdvisorUnavailable as error:
        if command == "probe":
            output = _probe_result(state="advisor_unchecked", reason_code=error.reason_code)
            output["latency_ms"] = error.latency_ms
        elif command == "assess":
            output = _unchecked_assess(request, error.reason_code, error.latency_ms)
        else:
            output = _unchecked_rank(request, error.reason_code, error.latency_ms)
        _write(output_stream, output)
        return 2
    except (ContractError, TypeError, ValueError, KeyError):
        if command == "probe":
            output = _probe_result(state="advisor_unchecked", reason_code="invalid_response")
        elif command == "assess":
            output = _unchecked_assess(request, "invalid_response", None)
        else:
            output = _unchecked_rank(request, "invalid_response", None)
        _write(output_stream, output)
        return 2

    _write(output_stream, output)
    return 0


def main() -> None:
    raise SystemExit(run())
