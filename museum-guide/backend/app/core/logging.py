"""Logging có che bí mật: không bao giờ ghi API key / token vào log."""
from __future__ import annotations

import logging
import re

_PATTERNS = [
    re.compile(r"(Bearer\s+)[A-Za-z0-9._\-]{8,}", re.I),
    re.compile(r"(xi-api-key['\"]?\s*[:=]\s*['\"]?)[A-Za-z0-9._\-]{8,}", re.I),
    re.compile(r"((?:api[_-]?key|token|secret)['\"]?\s*[:=]\s*['\"]?)[A-Za-z0-9._\-]{8,}", re.I),
    re.compile(r"\b(sk_[A-Za-z0-9]{10,})\b"),
]


def redact(text: str) -> str:
    for p in _PATTERNS:
        text = p.sub(lambda m: (m.group(1) if m.groups() and m.lastindex else "") + "***REDACTED***", text)
    return text


class RedactingFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        try:
            record.msg = redact(record.getMessage())
            record.args = ()
        except Exception:  # pragma: no cover
            pass
        return True


def setup_logging(level: int = logging.INFO) -> None:
    root = logging.getLogger()
    if any(isinstance(f, RedactingFilter) for h in root.handlers for f in h.filters):
        return
    h = logging.StreamHandler()
    h.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    h.addFilter(RedactingFilter())
    root.addHandler(h)
    root.setLevel(level)
