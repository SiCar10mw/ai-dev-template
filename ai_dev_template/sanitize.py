"""Trust-boundary sanitization helpers."""

from __future__ import annotations

import html
import re
from urllib.parse import unquote

_INJECTION_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"ignore\s+previous\s+instructions",
        r"system\s+prompt",
        r"developer\s+message",
        r"exfiltrate",
    )
]


def _decode_to_fixed_point(value: str, limit: int = 5) -> str:
    decoded = value
    for _ in range(limit):
        next_value = html.unescape(unquote(decoded))
        if next_value == decoded:
            return decoded
        decoded = next_value
    return decoded


def sanitize_for_llm(value: str) -> str:
    """Return text safe to place near an LLM context boundary."""
    decoded = _decode_to_fixed_point(value)
    sanitized = decoded
    for pattern in _INJECTION_PATTERNS:
        sanitized = pattern.sub("[removed]", sanitized)
    return sanitized

