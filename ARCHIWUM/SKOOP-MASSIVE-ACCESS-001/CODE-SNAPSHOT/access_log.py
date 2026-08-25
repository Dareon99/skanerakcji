"""Rotating JSON request log with a strict safe-field allowlist."""
from __future__ import annotations
import json
import logging
from datetime import UTC, datetime, timedelta
from logging.handlers import RotatingFileHandler
from pathlib import Path
from urllib.parse import urlsplit

PRIORITIES = {"P0", "P1", "P2", "P3", "SMOKE_TEST"}

def endpoint_label(endpoint: str) -> str:
    try:
        parts = urlsplit(endpoint)
    except ValueError:
        return "[INVALID_ENDPOINT]"
    if parts.scheme or parts.netloc:
        return f"{parts.scheme}://{parts.netloc}{parts.path}"
    return parts.path.split("?", 1)[0]

class RequestAuditLogger:
    def __init__(self, log_dir: Path, retention_days: int = 30) -> None:
        if retention_days != 30:
            raise ValueError("Contract requires 30-day retention.")
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.path = self.log_dir / "massive-access.jsonl"
        self._logger = logging.getLogger(f"skoop_massive_{id(self)}")
        self._logger.setLevel(logging.INFO)
        self._logger.propagate = False
        handler = RotatingFileHandler(self.path, maxBytes=5_000_000,
                                      backupCount=30, encoding="utf-8")
        handler.setFormatter(logging.Formatter("%(message)s"))
        self._logger.handlers[:] = [handler]
        self._cleanup(retention_days)

    def _cleanup(self, days: int) -> None:
        cutoff = datetime.now(UTC) - timedelta(days=days)
        for candidate in self.log_dir.glob("massive-access.jsonl*"):
            try:
                if datetime.fromtimestamp(candidate.stat().st_mtime, tz=UTC) < cutoff:
                    candidate.unlink()
            except OSError:
                continue

    def log_request(self, *, endpoint: str, category: str, priority: str,
                    response_code: int, latency_ms: int, result_count: int | None,
                    request_count: int, status: str, error_code: str | None = None) -> None:
        if priority not in PRIORITIES:
            raise ValueError("Unknown priority.")
        record = {
            "time_utc": datetime.now(UTC).isoformat(),
            "endpoint": endpoint_label(endpoint),
            "category": category[:80], "priority": priority,
            "response_code": int(response_code), "latency_ms": max(0, int(latency_ms)),
            "result_count": None if result_count is None else max(0, int(result_count)),
            "request_count": max(0, int(request_count)), "status": status[:80],
            "error_code": None if error_code is None else error_code[:80],
        }
        self._logger.info(json.dumps(record, ensure_ascii=True, separators=(",", ":")))
        for handler in self._logger.handlers:
            handler.flush()

    def close(self) -> None:
        for handler in self._logger.handlers[:]:
            handler.close()
            self._logger.removeHandler(handler)
