"""Offline-first configuration for the isolated Massive access package."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


PACKAGE_ID = "SKOOP-MASSIVE-ACCESS-001"
PRODUCT_ROOT = Path(r"C:\SKOOP Skaner wykresów")
PACKAGE_ROOT = PRODUCT_ROOT / "PACKAGES" / PACKAGE_ID
DATA_ROOT = Path(r"C:\SKOOP-dane")


class ConfigError(RuntimeError):
    """Raised when an access configuration is unsafe or incomplete."""


def _within(path: Path, root: Path) -> bool:
    candidate = path.resolve(strict=False)
    boundary = root.resolve(strict=False)
    try:
        candidate.relative_to(boundary)
    except ValueError:
        return False
    return True


@dataclass(frozen=True, slots=True)
class AccessConfig:
    """All provider paths and safety limits in one auditable object."""

    package_root: Path = PACKAGE_ROOT
    data_root: Path = DATA_ROOT
    secret_file: Path = DATA_ROOT / "secrets" / "massive_key.txt"
    sandbox_dir: Path = DATA_ROOT / "sandbox" / PACKAGE_ID
    log_dir: Path = DATA_ROOT / "logs" / "massive"
    kill_switch_file: Path = DATA_ROOT / "massive.kill-switch"
    counter_file: Path = DATA_ROOT / "sandbox" / PACKAGE_ID / "traffic-counter.json"
    max_requests: int = 50
    max_retries: int = 1
    timeout_seconds: float = 10.0
    network_enabled: bool = False
    base_url: str = ""
    auth_mode: str = ""

    def validate(self) -> None:
        if self.package_root.resolve(strict=False) != PACKAGE_ROOT.resolve(strict=False):
            raise ConfigError("Package code path differs from the accepted contract.")
        for label, path in (
            ("secret_file", self.secret_file),
            ("sandbox_dir", self.sandbox_dir),
            ("log_dir", self.log_dir),
            ("kill_switch_file", self.kill_switch_file),
            ("counter_file", self.counter_file),
        ):
            if not _within(path, self.data_root):
                raise ConfigError(f"{label} is outside the SKOOP data root.")
        if self.max_requests < 1 or self.max_requests > 50:
            raise ConfigError("The request ceiling must be between 1 and 50.")
        if self.max_retries not in (0, 1):
            raise ConfigError("Gate B allows at most one retry per scenario.")
        if self.timeout_seconds <= 0 or self.timeout_seconds > 60:
            raise ConfigError("Timeout must be in the range (0, 60] seconds.")
        if self.network_enabled:
            if not self.base_url.startswith("https://"):
                raise ConfigError("Network mode requires an explicitly reviewed HTTPS base URL.")
            if self.auth_mode not in {"query", "bearer"}:
                raise ConfigError("Network mode requires reviewed auth_mode=query|bearer.")
        elif self.base_url or self.auth_mode:
            raise ConfigError("Offline mode must not carry live provider connection settings.")

    def ensure_gate_a_directories(self) -> None:
        """Create directories only; never create or read the user's key file."""

        self.validate()
        self.secret_file.parent.mkdir(parents=True, exist_ok=True)
        self.sandbox_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)


DEFAULT_CONFIG = AccessConfig()


def assert_gate_a_default() -> None:
    """Fail if a code change accidentally enables provider traffic by default."""

    DEFAULT_CONFIG.validate()
    if DEFAULT_CONFIG.network_enabled:
        raise ConfigError("Gate A default must keep all external network disabled.")


assert_gate_a_default()
