"""Gate B runner: inert until every explicit authorization check passes."""
from __future__ import annotations
import argparse
import json
from dataclasses import replace
from pathlib import Path
from access_log import RequestAuditLogger
from config_access import DEFAULT_CONFIG, PACKAGE_ID
from massive_connection import MassiveConnection, ResultStatus
from massive_fetch import SCENARIOS, MassiveFetch
from sandbox_store import SandboxStore
from traffic_guard import KillSwitch, TrafficGuard

AUTHORIZATION_TEXT = f"{PACKAGE_ID}\nGATE_B_AUTHORIZED\nMAX_REQUESTS=50\n"
class GateBBlocked(RuntimeError):
    pass

def verify_authorization(path: Path) -> None:
    try:
        content = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    except OSError as exc:
        raise GateBBlocked("Gate B authorization missing or unreadable.") from exc
    if content != AUTHORIZATION_TEXT:
        raise GateBBlocked("Gate B authorization is invalid.")

def load_plan(path: Path) -> dict[str, dict[str, object]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise GateBBlocked("Reviewed endpoint plan missing or invalid.") from exc
    required = {s.scenario_id for s in SCENARIOS}
    if not isinstance(data, dict) or set(data) != required:
        raise GateBBlocked("Plan must contain exactly S0-S12 including S7b.")
    for scenario_id, item in data.items():
        if not isinstance(item, dict) or not str(item.get("endpoint_path", "")).startswith("/"):
            raise GateBBlocked(f"Plan endpoint {scenario_id} is not reviewed.")
        if not isinstance(item.get("params", {}), dict):
            raise GateBBlocked(f"Plan params {scenario_id} are invalid.")
    return data

def run_gate_b(*, authorization_file: Path, plan_file: Path,
               base_url: str, auth_mode: str) -> dict[str, object]:
    verify_authorization(authorization_file)
    plan = load_plan(plan_file)
    config = replace(DEFAULT_CONFIG, network_enabled=True,
                     base_url=base_url, auth_mode=auth_mode)
    config.validate()
    switch = KillSwitch(config.kill_switch_file)
    if switch.is_active():
        raise GateBBlocked("Kill switch active or ambiguous.")
    audit = RequestAuditLogger(config.log_dir)
    guard = TrafficGuard(config.max_requests, config.counter_file, switch)
    fetch = MassiveFetch(MassiveConnection(config, guard, audit))
    store = SandboxStore(config.sandbox_dir)
    results = []
    try:
        for scenario in SCENARIOS:
            item = plan[scenario.scenario_id]
            attempt = 0
            while True:
                attempt += 1
                result = fetch.fetch_one(scenario,
                    endpoint_path=str(item["endpoint_path"]), params=item.get("params", {}))
                store.record_fetch(result)
                results.append({"scenario_id": result.scenario_id,
                    "status": result.status.value, "status_code": result.status_code,
                    "request_count": result.request_count, "attempt": attempt})
                if result.status is ResultStatus.AUTHORIZATION_FAILED:
                    switch.activate("authorization failed")
                    raise GateBBlocked("Authorization failed; kill switch activated.")
                if result.status is not ResultStatus.TRANSIENT_ERROR or attempt > config.max_retries:
                    break
        summary = {"package": PACKAGE_ID, "requests": guard.count,
                   "s13": "PASSIVE_HEADERS_ONLY", "results": results}
        store.write_json("GATE-B-SUMMARY.json", summary)
        return summary
    finally:
        audit.close()

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-gate-b", action="store_true")
    parser.add_argument("--authorization-file", type=Path)
    parser.add_argument("--plan-file", type=Path)
    parser.add_argument("--base-url")
    parser.add_argument("--auth-mode", choices=("query", "bearer"))
    args = parser.parse_args()
    if not args.run_gate_b:
        raise GateBBlocked("Gate B blocked: explicit flag absent.")
    if not all((args.authorization_file, args.plan_file, args.base_url, args.auth_mode)):
        raise GateBBlocked("Gate B inputs incomplete.")
    print(json.dumps(run_gate_b(authorization_file=args.authorization_file,
        plan_file=args.plan_file, base_url=args.base_url,
        auth_mode=args.auth_mode), ensure_ascii=True, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
