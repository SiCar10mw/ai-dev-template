#!/usr/bin/env python3
"""Verify the default profile has no enterprise dependency and corporate controls are optional."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENTERPRISE_ONLY_MARKERS = (
    "publish_m365_stub",
    "AZURE_TENANT_ID",
    "AZURE_CLIENT_ID",
    "AZURE_CLIENT_SECRET",
    "sharepoint",
    "purview",
    "teams",
    "entra",
    "graph api",
)


def check_personal_profile(root: Path = ROOT) -> list[str]:
    """Fail if core local/CI checks require enterprise-only systems."""
    ci_script = (root / "scripts" / "ci_check.sh").read_text(encoding="utf-8").lower()
    errors = []
    for marker in ENTERPRISE_ONLY_MARKERS:
        if marker.lower() in ci_script:
            errors.append(f"personal make check must not require enterprise marker: {marker}")
    return errors


def check_corporate_profile(root: Path = ROOT) -> list[str]:
    """Validate corporate profile scaffolding without contacting enterprise services."""
    errors = []
    required = [
        "docs/m365-integration.md",
        "config/m365-publisher.example.json",
        "scripts/publish_m365_stub.py",
    ]
    for relative in required:
        if not (root / relative).exists():
            errors.append(f"missing corporate profile scaffold: {relative}")

    config_path = root / "config" / "m365-publisher.example.json"
    if config_path.exists():
        config = json.loads(config_path.read_text(encoding="utf-8"))
        targets = config.get("publish_targets", [])
        if not isinstance(targets, list) or not targets:
            errors.append("corporate profile must define example publish_targets")
        text = config_path.read_text(encoding="utf-8").lower()
        for forbidden in ("secret_value", "password", "bearer ", "client_secret="):
            if forbidden in text:
                errors.append(f"corporate profile example contains forbidden secret marker: {forbidden}")
    return errors


def main() -> int:
    profile = os.environ.get("AI_DEV_PROFILE", "personal").lower()
    errors = check_personal_profile()
    if profile == "corporate":
        errors.extend(check_corporate_profile())
    elif profile not in {"personal", "core"}:
        errors.append(f"unknown AI_DEV_PROFILE: {profile}")

    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(f"Profile boundary check passed for {profile}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
