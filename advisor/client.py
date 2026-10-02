from __future__ import annotations

import json
import socket
import time
from dataclasses import dataclass
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

from .models import ContractError, PINNED_MODEL, canonical_json, validate_usage


ENDPOINT = "https://api.typesafe.ai/v1/systemone"
TIMEOUT_SECONDS = 8.0
MAX_RESPONSE_BYTES = 1024 * 1024


@dataclass(frozen=True)
class HttpResponse:
    status: int
    body: bytes


@dataclass(frozen=True)
class ProviderResponse:
    model: str
    answers: dict[str, Any]
    usage: dict[str, int]
    latency_ms: int


class AdvisorUnavailable(RuntimeError):
    def __init__(self, reason_code: str, *, latency_ms: int | None = None) -> None:
        super().__init__(reason_code)
        self.reason_code = reason_code
        self.latency_ms = latency_ms


Transport = Callable[[str, dict[str, str], bytes, float], HttpResponse]


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(
        self,
        req: Request,
        fp: Any,
        code: int,
        msg: str,
        headers: Any,
        newurl: str,
    ) -> None:
        return None


def _default_transport(url: str, headers: dict[str, str], body: bytes, timeout: float) -> HttpResponse:
    request = Request(url, data=body, headers=headers, method="POST")
    opener = build_opener(_NoRedirect())
    try:
        with opener.open(request, timeout=timeout) as response:
            return HttpResponse(response.status, response.read(MAX_RESPONSE_BYTES + 1))
    except HTTPError as error:
        try:
            return HttpResponse(error.code, b"")
        finally:
            error.close()


def _http_reason(status: int) -> str:
    if status in (401, 403):
        return "authentication"
    if status == 429:
        return "rate_limited"
    if status == 529:
        return "overloaded"
    return "service_error"


class TypeSafeClient:
    def __init__(self, *, api_key: str | None, transport: Transport | None = None) -> None:
        self._api_key = api_key.strip() if isinstance(api_key, str) else ""
        self._transport = transport or _default_transport

    def evaluate(self, payload: dict[str, Any]) -> ProviderResponse:
        if not self._api_key:
            raise AdvisorUnavailable("missing_api_key")

        body = canonical_json(payload).encode("utf-8")
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        started = time.monotonic()
        try:
            response = self._transport(ENDPOINT, headers, body, TIMEOUT_SECONDS)
        except (TimeoutError, socket.timeout):
            raise AdvisorUnavailable("timeout", latency_ms=self._latency(started)) from None
        except (URLError, OSError):
            raise AdvisorUnavailable("connection", latency_ms=self._latency(started)) from None

        latency_ms = self._latency(started)
        if response.status != 200:
            raise AdvisorUnavailable(_http_reason(response.status), latency_ms=latency_ms)
        if len(response.body) > MAX_RESPONSE_BYTES:
            raise AdvisorUnavailable("invalid_response", latency_ms=latency_ms)

        try:
            decoded = json.loads(response.body.decode("utf-8"))
            if not isinstance(decoded, dict) or set(decoded) != {"model", "answers", "usage"}:
                raise ContractError("invalid provider response")
            if decoded["model"] != PINNED_MODEL:
                raise AdvisorUnavailable("model_mismatch", latency_ms=latency_ms)
            if not isinstance(decoded["answers"], dict) or not decoded["answers"]:
                raise ContractError("invalid provider answers")
            usage = validate_usage(decoded["usage"])
        except AdvisorUnavailable:
            raise
        except (UnicodeDecodeError, json.JSONDecodeError, ContractError, TypeError, ValueError):
            raise AdvisorUnavailable("invalid_response", latency_ms=latency_ms) from None

        return ProviderResponse(
            model=decoded["model"],
            answers=decoded["answers"],
            usage=usage,
            latency_ms=latency_ms,
        )

    @staticmethod
    def _latency(started: float) -> int:
        return max(0, round((time.monotonic() - started) * 1000))
