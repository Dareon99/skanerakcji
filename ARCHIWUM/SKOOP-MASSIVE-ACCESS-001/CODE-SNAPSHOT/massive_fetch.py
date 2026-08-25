"""One-page, budget-respecting scenario fetches for controlled Gate B."""
from __future__ import annotations
import json
from dataclasses import dataclass
from typing import Mapping
from massive_connection import MassiveConnection, ResultStatus

@dataclass(frozen=True, slots=True)
class Scenario:
    scenario_id: str
    category: str
    purpose: str

SCENARIOS = (
    Scenario("S0", "authorization", "Reviewed authorization read"),
    Scenario("S1", "instrument_catalog", "One active-instrument page"),
    Scenario("S2", "instrument_details", "One reference record"),
    Scenario("S3", "classification", "SIC, sector and industry"),
    Scenario("S4", "capitalization", "Market cap and share counts"),
    Scenario("S5", "financials", "Quarterly and TTM earnings"),
    Scenario("S6", "ipo", "IPO calendar and status"),
    Scenario("S7", "candles_1d", "Short daily range"),
    Scenario("S7b", "grouped_daily", "Grouped daily response"),
    Scenario("S8", "candles_30m", "Short 30-minute range"),
    Scenario("S9", "market_calendar", "Sessions and holidays"),
    Scenario("S10", "fx", "One FX pair"),
    Scenario("S11", "corporate_actions", "Splits and dividends"),
    Scenario("S12", "history_depth", "Old daily range"),
)
SCENARIO_IDS = tuple(s.scenario_id for s in SCENARIOS)

@dataclass(frozen=True, slots=True)
class FetchResult:
    scenario_id: str
    category: str
    status: ResultStatus
    status_code: int
    latency_ms: int
    request_count: int
    key_fingerprint: str
    top_level_fields: tuple[str, ...]
    next_page_present: bool
    rate_limit_headers: Mapping[str, str]

def field_shape(value: object, prefix: str = "", depth: int = 0) -> set[str]:
    """Return field names and paths only; never retain provider values."""
    if depth > 3:
        return set()
    fields: set[str] = set()
    if isinstance(value, dict):
        for raw_key in sorted(value, key=str):
            key = str(raw_key)
            path = f"{prefix}.{key}" if prefix else key
            fields.add(path)
            child = value[raw_key]
            if isinstance(child, (dict, list)):
                fields.update(field_shape(child, path, depth + 1))
    elif isinstance(value, list):
        list_path = f"{prefix}[]" if prefix else "[]"
        fields.add(list_path)
        if value:
            fields.update(field_shape(value[0], list_path, depth + 1))
    return fields

class MassiveFetch:
    def __init__(self, connection: MassiveConnection) -> None:
        self.connection = connection

    def fetch_one(self, scenario: Scenario, *, endpoint_path: str,
                  params: Mapping[str, object] | None = None) -> FetchResult:
        if scenario.scenario_id not in SCENARIO_IDS:
            raise ValueError("Scenario outside accepted map.")
        result = self.connection.request(endpoint_path=endpoint_path,
            category=scenario.category, params=params, priority="SMOKE_TEST")
        fields: tuple[str, ...] = ()
        next_page = False
        if result.body:
            try:
                payload = json.loads(result.body.decode("utf-8"))
                if isinstance(payload, (dict, list)):
                    fields = tuple(sorted(field_shape(payload)))
                if isinstance(payload, dict):
                    next_page = any(k in payload for k in ("next_url", "next_page", "cursor"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                pass
        rate = {str(k): str(v) for k, v in result.headers.items()
                if "rate" in str(k).lower() or "limit" in str(k).lower()}
        return FetchResult(scenario.scenario_id, scenario.category, result.status,
            result.status_code, result.latency_ms, result.request_count,
            result.key_fingerprint, fields, next_page, rate)
