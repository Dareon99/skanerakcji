"""Only provider connection boundary; disabled by default in Gate A."""
from __future__ import annotations
import time
from dataclasses import dataclass
from enum import StrEnum
from typing import Callable, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urljoin
from urllib.request import Request, urlopen
from access_log import RequestAuditLogger
from config_access import AccessConfig
from secret_loader import fingerprint, load_secret
from traffic_guard import TrafficGuard

class ResultStatus(StrEnum):
    CONFIRMED = "CONFIRMED"
    UNAVAILABLE_IN_CURRENT_PLAN = "UNAVAILABLE_IN_CURRENT_PLAN"
    MISSING_AT_SOURCE = "MISSING_AT_SOURCE"
    UNVERIFIED = "UNVERIFIED"
    TRANSIENT_ERROR = "TRANSIENT_ERROR"
    AUTHORIZATION_FAILED = "AUTHORIZATION_FAILED"

class NetworkDisabled(RuntimeError):
    pass

@dataclass(frozen=True, slots=True)
class HttpResult:
    status_code: int
    body: bytes
    headers: Mapping[str, str]

@dataclass(frozen=True, slots=True)
class ConnectionResult:
    status: ResultStatus
    status_code: int
    body: bytes
    headers: Mapping[str, str]
    latency_ms: int
    request_count: int
    key_fingerprint: str

Transport = Callable[[Request, float], HttpResult]

def classify_status(code: int) -> ResultStatus:
    if 200 <= code < 300:
        return ResultStatus.CONFIRMED
    if code == 401:
        return ResultStatus.AUTHORIZATION_FAILED
    if code == 403:
        return ResultStatus.UNAVAILABLE_IN_CURRENT_PLAN
    if code == 404:
        return ResultStatus.MISSING_AT_SOURCE
    if code == 429 or 500 <= code < 600:
        return ResultStatus.TRANSIENT_ERROR
    return ResultStatus.UNVERIFIED

def default_transport(request: Request, timeout: float) -> HttpResult:
    try:
        with urlopen(request, timeout=timeout) as response:
            return HttpResult(response.status, response.read(2_000_000), dict(response.headers.items()))
    except HTTPError as exc:
        return HttpResult(exc.code, exc.read(2_000_000), dict(exc.headers.items()) if exc.headers else {})
    except (URLError, TimeoutError, OSError) as exc:
        raise ConnectionError("Provider transport failed without request details.") from exc

class MassiveConnection:
    def __init__(self, config: AccessConfig, guard: TrafficGuard,
                 audit_log: RequestAuditLogger, transport: Transport | None = None) -> None:
        config.validate()
        self.config, self.guard, self.audit_log = config, guard, audit_log
        self.transport = transport or default_transport

    def _build(self, path: str, params: Mapping[str, object] | None, secret: str) -> Request:
        if not path.startswith("/"):
            raise ValueError("Endpoint path must start with slash.")
        url = urljoin(self.config.base_url.rstrip("/") + "/", path.lstrip("/"))
        query = dict(params or {})
        headers = {"Accept": "application/json", "User-Agent": "SKOOP-MASSIVE-ACCESS-001"}
        if self.config.auth_mode == "query":
            query["apiKey"] = secret
        elif self.config.auth_mode == "bearer":
            headers["Authorization"] = f"Bearer {secret}"
        else:
            raise ValueError("Unreviewed authentication mode.")
        if query:
            url += "?" + urlencode(query)
        return Request(url, headers=headers, method="GET")

    def request(self, *, endpoint_path: str, category: str,
                params: Mapping[str, object] | None = None,
                priority: str = "SMOKE_TEST") -> ConnectionResult:
        if not self.config.network_enabled:
            raise NetworkDisabled("Gate B blocked: provider network disabled.")
        secret = load_secret(self.config.secret_file)
        request = self._build(endpoint_path, params, secret)
        reservation = self.guard.reserve()
        started = time.monotonic()
        try:
            try:
                http = self.transport(request, self.config.timeout_seconds)
            except ConnectionError:
                latency = int((time.monotonic() - started) * 1000)
                self.audit_log.log_request(endpoint=endpoint_path, category=category,
                    priority=priority, response_code=0, latency_ms=latency,
                    result_count=None, request_count=reservation.sequence,
                    status=ResultStatus.TRANSIENT_ERROR, error_code="TRANSPORT_ERROR")
                raise
            latency = int((time.monotonic() - started) * 1000)
            status = classify_status(http.status_code)
            self.audit_log.log_request(endpoint=endpoint_path, category=category,
                priority=priority, response_code=http.status_code, latency_ms=latency,
                result_count=None, request_count=reservation.sequence, status=status)
            return ConnectionResult(status, http.status_code, http.body, http.headers,
                                    latency, reservation.sequence, fingerprint(secret))
        finally:
            self.guard.complete()
