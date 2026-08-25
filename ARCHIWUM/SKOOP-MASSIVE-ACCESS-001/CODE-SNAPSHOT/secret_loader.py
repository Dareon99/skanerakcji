"""Local secret loading and redaction. No logging side effects."""
from __future__ import annotations
import hashlib
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

MASK = "***REDACTED***"
SENSITIVE = {"apikey", "api_key", "key", "token", "access_token", "authorization"}

class SecretError(RuntimeError):
    pass

def load_secret(path: Path) -> str:
    try:
        value = path.read_text(encoding="utf-8").strip()
    except FileNotFoundError as exc:
        raise SecretError("Massive key file is missing; access remains stopped.") from exc
    except OSError as exc:
        raise SecretError("Massive key file is unreadable; access remains stopped.") from exc
    if len(value) < 16 or any(c.isspace() for c in value):
        raise SecretError("Massive key is invalid; access remains stopped.")
    return value

def fingerprint(secret: str) -> str:
    if not secret:
        raise SecretError("Cannot fingerprint an empty key.")
    return hashlib.sha256(secret.encode()).hexdigest()[:8]

def sanitize_url(url: str, secret: str | None = None) -> str:
    source = url.replace(secret, MASK) if secret else url
    try:
        parts = urlsplit(source)
        query = [(k, MASK if k.lower() in SENSITIVE else v)
                 for k, v in parse_qsl(parts.query, keep_blank_values=True)]
        return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), ""))
    except ValueError:
        return "[INVALID_URL_REDACTED]"

def redact_text(text: str, secret: str | None = None) -> str:
    safe = text.replace(secret, MASK) if secret else text
    for marker in ("authorization:", "api_key=", "apikey=", "token="):
        pos = safe.lower().find(marker)
        while pos >= 0:
            start = pos + len(marker)
            stops = []
            for delimiter in ("&", " ", "\\n", "\\r"):
                found = safe.find(delimiter, start)
                if found >= 0:
                    stops.append(found)
            end = min(stops) if stops else len(safe)
            safe = safe[:start] + MASK + safe[end:]
            pos = safe.lower().find(marker, start + len(MASK))
    return safe
