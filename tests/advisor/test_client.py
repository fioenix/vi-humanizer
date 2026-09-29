from __future__ import annotations

import json
import socket
import unittest
from urllib.error import URLError

from advisor.client import (
    ENDPOINT,
    TIMEOUT_SECONDS,
    AdvisorUnavailable,
    HttpResponse,
    TypeSafeClient,
)
from advisor.models import PINNED_MODEL
from advisor.questions import build_probe_payload


def response_body(*, model: str = PINNED_MODEL) -> bytes:
    return json.dumps(
        {
            "model": model,
            "answers": {"probe.complete": {"type": "noul", "noul": 0.98}},
            "usage": {"input_tokens": 42, "output_tokens": 7},
        }
    ).encode("utf-8")


class RecordingTransport:
    def __init__(self, response: HttpResponse | Exception) -> None:
        self.response = response
        self.calls: list[tuple[str, dict[str, str], bytes, float]] = []

    def __call__(self, url: str, headers: dict[str, str], body: bytes, timeout: float) -> HttpResponse:
        self.calls.append((url, headers, body, timeout))
        if isinstance(self.response, Exception):
            raise self.response
        return self.response


class TypeSafeClientTest(unittest.TestCase):
    def test_missing_or_blank_key_never_calls_transport(self) -> None:
        transport = RecordingTransport(HttpResponse(200, response_body()))

        for key in (None, "", "   "):
            with self.subTest(key=key):
                with self.assertRaises(AdvisorUnavailable) as caught:
                    TypeSafeClient(api_key=key, transport=transport).evaluate(build_probe_payload())
                self.assertEqual(caught.exception.reason_code, "missing_api_key")

        self.assertEqual(transport.calls, [])

    def test_sends_one_fixed_endpoint_request_with_environment_key_as_bearer(self) -> None:
        transport = RecordingTransport(HttpResponse(200, response_body()))
        payload = build_probe_payload()

        result = TypeSafeClient(api_key="secret-value", transport=transport).evaluate(payload)

        self.assertEqual(result.model, PINNED_MODEL)
        self.assertEqual(result.usage, {"input_tokens": 42, "output_tokens": 7})
        self.assertEqual(len(transport.calls), 1)
        url, headers, body, timeout = transport.calls[0]
        self.assertEqual(url, ENDPOINT)
        self.assertEqual(headers["Authorization"], "Bearer secret-value")
        self.assertEqual(headers["Content-Type"], "application/json")
        self.assertEqual(json.loads(body), payload)
        self.assertEqual(timeout, TIMEOUT_SECONDS)

    def test_maps_http_statuses_to_allowlisted_reason_codes(self) -> None:
        cases = {
            401: "authentication",
            429: "rate_limited",
            529: "overloaded",
            422: "service_error",
            500: "service_error",
        }
        for status, expected in cases.items():
            with self.subTest(status=status):
                transport = RecordingTransport(HttpResponse(status, b'raw-provider-body-canary'))
                with self.assertRaises(AdvisorUnavailable) as caught:
                    TypeSafeClient(api_key="secret", transport=transport).evaluate(build_probe_payload())
                self.assertEqual(caught.exception.reason_code, expected)
                self.assertNotIn("canary", str(caught.exception))
                self.assertEqual(len(transport.calls), 1)

    def test_maps_timeout_and_connection_failures_without_raw_exception(self) -> None:
        for error, expected in (
            (TimeoutError("raw-timeout-canary"), "timeout"),
            (socket.timeout("raw-socket-canary"), "timeout"),
            (URLError("raw-network-canary"), "connection"),
            (OSError("raw-os-canary"), "connection"),
        ):
            with self.subTest(error=type(error).__name__):
                with self.assertRaises(AdvisorUnavailable) as caught:
                    TypeSafeClient(
                        api_key="secret",
                        transport=RecordingTransport(error),
                    ).evaluate(build_probe_payload())
                self.assertEqual(caught.exception.reason_code, expected)
                self.assertNotIn("canary", str(caught.exception))

    def test_rejects_malformed_or_model_mismatched_response(self) -> None:
        cases = (
            (b"not-json", "invalid_response"),
            (json.dumps({"model": PINNED_MODEL, "answers": {}, "usage": {}}).encode(), "invalid_response"),
            (response_body(model="jev-latest"), "model_mismatch"),
        )
        for body, expected in cases:
            with self.subTest(expected=expected):
                with self.assertRaises(AdvisorUnavailable) as caught:
                    TypeSafeClient(
                        api_key="secret",
                        transport=RecordingTransport(HttpResponse(200, body)),
                    ).evaluate(build_probe_payload())
                self.assertEqual(caught.exception.reason_code, expected)


if __name__ == "__main__":
    unittest.main()
