"""Persistent fail-closed request ceiling and kill switch."""
from __future__ import annotations
import json
import os
import threading
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

class TrafficBlocked(RuntimeError):
    pass
class KillSwitchActive(TrafficBlocked):
    pass
class RequestLimitReached(TrafficBlocked):
    pass
class ConcurrentRequestBlocked(TrafficBlocked):
    pass
class GuardStateInvalid(TrafficBlocked):
    pass

class KillSwitch:
    """Absence is OFF. Any existing or unreadable flag means STOP."""
    def __init__(self, flag_file: Path) -> None:
        self.flag_file = flag_file

    def is_active(self) -> bool:
        try:
            return self.flag_file.exists()
        except OSError:
            return True

    def activate(self, reason: str) -> None:
        self.flag_file.parent.mkdir(parents=True, exist_ok=True)
        temp = self.flag_file.with_suffix(self.flag_file.suffix + ".tmp")
        payload = {"state": "ON", "reason": str(reason)[:200],
                   "activated_at_utc": datetime.now(UTC).isoformat()}
        temp.write_text(json.dumps(payload, ensure_ascii=True), encoding="utf-8")
        os.replace(temp, self.flag_file)

    def deactivate(self) -> None:
        try:
            self.flag_file.unlink(missing_ok=True)
        except OSError as exc:
            raise GuardStateInvalid("Kill switch could not be disabled safely.") from exc

@dataclass(frozen=True, slots=True)
class Reservation:
    sequence: int
    reserved_at_utc: str

class TrafficGuard:
    def __init__(self, max_requests: int, counter_file: Path, kill_switch: KillSwitch) -> None:
        if not 1 <= max_requests <= 50:
            raise ValueError("max_requests must be between 1 and 50")
        self.max_requests = max_requests
        self.counter_file = counter_file
        self.kill_switch = kill_switch
        self._lock = threading.Lock()
        self._in_flight = False
        self._count = self._load()

    @property
    def count(self) -> int:
        with self._lock:
            return self._count

    def _load(self) -> int:
        if not self.counter_file.exists():
            return 0
        try:
            count = int(json.loads(self.counter_file.read_text(encoding="utf-8"))["request_count"])
        except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
            self.kill_switch.activate("invalid traffic counter")
            raise GuardStateInvalid("Invalid counter; kill switch activated.") from exc
        if not 0 <= count <= self.max_requests:
            self.kill_switch.activate("counter outside accepted range")
            raise GuardStateInvalid("Counter outside accepted range.")
        return count

    def _persist(self) -> None:
        self.counter_file.parent.mkdir(parents=True, exist_ok=True)
        temp = self.counter_file.with_suffix(self.counter_file.suffix + ".tmp")
        payload = {"package": "SKOOP-MASSIVE-ACCESS-001", "request_count": self._count,
                   "updated_at_utc": datetime.now(UTC).isoformat()}
        temp.write_text(json.dumps(payload, ensure_ascii=True), encoding="utf-8")
        os.replace(temp, self.counter_file)

    def reserve(self) -> Reservation:
        with self._lock:
            if self.kill_switch.is_active():
                raise KillSwitchActive("Kill switch active; zero traffic allowed.")
            if self._in_flight:
                raise ConcurrentRequestBlocked("Another provider request is in flight.")
            if self._count >= self.max_requests:
                self.kill_switch.activate("hard request ceiling reached")
                raise RequestLimitReached("Request ceiling reached.")
            self._count += 1
            self._persist()
            self._in_flight = True
            return Reservation(self._count, datetime.now(UTC).isoformat())

    def complete(self) -> None:
        with self._lock:
            if not self._in_flight:
                self.kill_switch.activate("completion without reservation")
                raise GuardStateInvalid("Invalid lifecycle; kill switch activated.")
            self._in_flight = False
