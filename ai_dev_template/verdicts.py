"""Deterministic verdict helpers used by the template tests."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Verdict:
    """A small deterministic output whose JSON form is guarded by a golden test."""

    status: str
    passed: bool
    reason: str


def derive_verdict(status: str) -> Verdict:
    """Derive a deterministic verdict from a status string."""
    normalized = status.strip().lower()
    if normalized == "pass":
        return Verdict(status="pass", passed=True, reason="positive evidence")
    if normalized == "fail":
        return Verdict(status="fail", passed=False, reason="negative evidence")
    if normalized == "partial":
        return Verdict(status="partial", passed=False, reason="incomplete evidence")
    raise ValueError(f"unsupported status: {status!r}")


def canonical_json(verdict: Verdict) -> str:
    """Serialize a verdict in canonical byte-stable JSON form."""
    return json.dumps(asdict(verdict), sort_keys=True, separators=(",", ":"))

