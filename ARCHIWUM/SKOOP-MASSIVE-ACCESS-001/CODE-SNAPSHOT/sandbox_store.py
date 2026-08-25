"""Evidence writes restricted to the accepted SKOOP sandbox."""
from __future__ import annotations
import json
import os
import re
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Mapping

SAFE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,79}$")
class SandboxViolation(RuntimeError):
    pass

def ensure_within(path: Path, root: Path) -> Path:
    candidate, boundary = path.resolve(strict=False), root.resolve(strict=False)
    try:
        candidate.relative_to(boundary)
    except ValueError as exc:
        raise SandboxViolation("Write outside accepted sandbox.") from exc
    return candidate

class SandboxStore:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve(strict=False)
        self.root.mkdir(parents=True, exist_ok=True)
        self.database = ensure_within(self.root / "smoke-evidence.sqlite", self.root)
        db = sqlite3.connect(self.database)
        try:
            db.execute("""CREATE TABLE IF NOT EXISTS scenario_evidence (
                scenario_id TEXT PRIMARY KEY, category TEXT NOT NULL, status TEXT NOT NULL,
                status_code INTEGER NOT NULL, latency_ms INTEGER NOT NULL,
                request_count INTEGER NOT NULL, key_fingerprint TEXT NOT NULL,
                fields_json TEXT NOT NULL, next_page INTEGER NOT NULL,
                rate_headers_json TEXT NOT NULL, recorded_at_utc TEXT NOT NULL)""")
            db.commit()
        finally:
            db.close()

    def record_fetch(self, result: Any) -> None:
        status = result.status.value if hasattr(result.status, "value") else str(result.status)
        row = (result.scenario_id, result.category, status, int(result.status_code),
               int(result.latency_ms), int(result.request_count), str(result.key_fingerprint),
               json.dumps(list(result.top_level_fields), ensure_ascii=True),
               int(bool(result.next_page_present)),
               json.dumps(dict(result.rate_limit_headers), ensure_ascii=True),
               datetime.now(UTC).isoformat())
        db = sqlite3.connect(self.database)
        try:
            db.execute("INSERT OR REPLACE INTO scenario_evidence VALUES (?,?,?,?,?,?,?,?,?,?,?)", row)

            db.commit()
        finally:
            db.close()
    def write_json(self, name: str, payload: Mapping[str, Any]) -> Path:
        if not SAFE_NAME.fullmatch(name):
            raise SandboxViolation("Unsafe evidence filename.")
        if not name.endswith(".json"):
            name += ".json"
        target = ensure_within(self.root / name, self.root)
        temp = ensure_within(target.with_suffix(target.suffix + ".tmp"), self.root)
        temp.write_text(json.dumps(dict(payload), ensure_ascii=True, indent=2,
                                   sort_keys=True) + "\n", encoding="utf-8")
        os.replace(temp, target)
        return target

    def count_rows(self) -> int:
        db = sqlite3.connect(self.database)
        try:
            return int(db.execute("SELECT COUNT(*) FROM scenario_evidence").fetchone()[0])
        finally:
            db.close()
