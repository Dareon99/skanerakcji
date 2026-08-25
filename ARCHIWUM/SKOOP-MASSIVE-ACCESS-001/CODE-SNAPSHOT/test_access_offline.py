"""Gate A tests. Every provider response is an in-memory fake."""
from __future__ import annotations
import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from access_log import RequestAuditLogger, endpoint_label
from config_access import DEFAULT_CONFIG, ConfigError
from massive_connection import (HttpResult, MassiveConnection, NetworkDisabled,
                                ResultStatus, classify_status)
from massive_fetch import MassiveFetch, SCENARIOS
from sandbox_store import SandboxStore, SandboxViolation, ensure_within
from secret_loader import load_secret, redact_text, sanitize_url
from smoke_test import GateBBlocked, verify_authorization
from traffic_guard import (ConcurrentRequestBlocked, GuardStateInvalid, KillSwitch,
                           RequestLimitReached, TrafficGuard)

FAKE_KEY = "offline_fake_key_1234567890"

class GateATests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def config(self, *, online: bool = False):
        return replace(DEFAULT_CONFIG, data_root=self.root,
            secret_file=self.root / "secrets" / "massive_key.txt",
            sandbox_dir=self.root / "sandbox", log_dir=self.root / "logs",
            kill_switch_file=self.root / "kill.flag",
            counter_file=self.root / "counter.json", network_enabled=online,
            base_url="https://example.invalid" if online else "",
            auth_mode="query" if online else "")

    def components(self, config):
        switch = KillSwitch(config.kill_switch_file)
        guard = TrafficGuard(config.max_requests, config.counter_file, switch)
        audit = RequestAuditLogger(config.log_dir)
        return switch, guard, audit

    def test_default_is_offline_and_paths_are_guarded(self):
        DEFAULT_CONFIG.validate()
        self.assertFalse(DEFAULT_CONFIG.network_enabled)
        bad = replace(self.config(), log_dir=Path(r"C:\outside"))
        with self.assertRaises(ConfigError):
            bad.validate()

    def test_secret_redaction(self):
        key_file = self.root / "key.txt"
        key_file.write_text(FAKE_KEY, encoding="utf-8")
        self.assertEqual(load_secret(key_file), FAKE_KEY)
        url = sanitize_url("https://example.invalid/x?apiKey=" + FAKE_KEY, FAKE_KEY)
        text = redact_text("Authorization: " + FAKE_KEY, FAKE_KEY)
        self.assertNotIn(FAKE_KEY, url + text)
        self.assertEqual(endpoint_label("https://host/path?apiKey=bad"), "https://host/path")

    def test_six_status_classification(self):
        expected = {200: ResultStatus.CONFIRMED, 401: ResultStatus.AUTHORIZATION_FAILED,
            403: ResultStatus.UNAVAILABLE_IN_CURRENT_PLAN,
            404: ResultStatus.MISSING_AT_SOURCE, 429: ResultStatus.TRANSIENT_ERROR,
            500: ResultStatus.TRANSIENT_ERROR, 418: ResultStatus.UNVERIFIED}
        for code, status in expected.items():
            with self.subTest(code=code):
                self.assertIs(classify_status(code), status)

    def test_offline_default_never_calls_transport_or_reads_key(self):
        config = self.config()
        called = []
        _, guard, audit = self.components(config)
        connection = MassiveConnection(config, guard, audit,
            transport=lambda request, timeout: called.append(request))
        with self.assertRaises(NetworkDisabled):
            connection.request(endpoint_path="/blocked", category="test")
        audit.close()
        self.assertEqual(called, [])
        self.assertFalse(config.secret_file.exists())

    def test_fake_transport_is_counted_and_secret_not_logged(self):
        config = self.config(online=True)
        config.secret_file.parent.mkdir(parents=True)
        config.secret_file.write_text(FAKE_KEY, encoding="utf-8")
        seen = []
        def fake(request, timeout):
            seen.append(request.full_url)
            return HttpResult(200, b'{"results":[]}', {"X-RateLimit-Test": "offline"})
        _, guard, audit = self.components(config)
        result = MassiveConnection(config, guard, audit, fake).request(
            endpoint_path="/mock", category="offline")
        audit.close()
        self.assertEqual(result.request_count, 1)
        self.assertIn(FAKE_KEY, seen[0])
        self.assertNotIn(FAKE_KEY, (config.log_dir / "massive-access.jsonl").read_text())

    def test_limit_concurrency_and_kill_switch(self):
        switch = KillSwitch(self.root / "kill.flag")
        guard = TrafficGuard(2, self.root / "counter.json", switch)
        guard.reserve()
        with self.assertRaises(ConcurrentRequestBlocked):
            guard.reserve()
        guard.complete()
        guard.reserve(); guard.complete()
        with self.assertRaises(RequestLimitReached):
            guard.reserve()
        self.assertTrue(switch.is_active())
        self.assertTrue(KillSwitch(self.root / "kill.flag").is_active())

    def test_invalid_counter_fails_closed(self):
        counter = self.root / "counter.json"
        counter.write_text("not-json", encoding="utf-8")
        switch = KillSwitch(self.root / "kill.flag")
        with self.assertRaises(GuardStateInvalid):
            TrafficGuard(50, counter, switch)
        self.assertTrue(switch.is_active())

    def test_sandbox_and_fetch_summary(self):
        store = SandboxStore(self.root / "sandbox")
        store.write_json("offline.json", {"ok": True})
        with self.assertRaises(SandboxViolation):
            ensure_within(self.root / "escape.json", self.root / "sandbox")
        config = self.config(online=True)
        config.secret_file.parent.mkdir(parents=True)
        config.secret_file.write_text(FAKE_KEY, encoding="utf-8")
        _, guard, audit = self.components(config)
        fake = lambda request, timeout: HttpResult(200, b'{"a":1,"next_url":"x"}', {})
        result = MassiveFetch(MassiveConnection(config, guard, audit, fake)).fetch_one(
            SCENARIOS[0], endpoint_path="/mock")
        audit.close(); store.record_fetch(result)
        self.assertTrue(result.next_page_present)
        self.assertEqual(store.count_rows(), 1)

    def test_gate_b_authorization_is_exact(self):
        path = self.root / "authorization.txt"
        path.write_text("NO", encoding="utf-8")
        with self.assertRaises(GateBBlocked):
            verify_authorization(path)

if __name__ == "__main__":
    unittest.main(verbosity=2)
