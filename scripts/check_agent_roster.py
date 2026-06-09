#!/usr/bin/env python3
"""Validate model-neutral agent roster sources and generated tool views."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.gen_agent_views import AGENT_ORDER, diff_generated_views, load_agents  # noqa: E402

REQUIRED_BINDINGS = ("approved-models-only", "audit-logging", "no-exfil", "sensitivity-aware")


def check_agent_roster(root: Path = ROOT) -> list[str]:
    """Return roster-source and generated-view errors."""
    errors: list[str] = []
    try:
        agents = load_agents(root)
    except ValueError as exc:
        return [str(exc)]

    found = [agent.name for agent in agents]
    if found != list(AGENT_ORDER):
        errors.append("agents/ roster order does not match AGENT_ORDER")

    for agent in agents:
        body = agent.body
        for phrase in REQUIRED_BINDINGS:
            if phrase not in body:
                errors.append(f"{agent.source_label} missing agent binding: {phrase}")
        if "## Role" not in body:
            errors.append(f"{agent.source_label} missing Role section")
        if "## Common Binding" not in body:
            errors.append(f"{agent.source_label} missing Common Binding section")
        if "## Behavior" not in body:
            errors.append(f"{agent.source_label} missing Behavior section")
        if "## Allowed Tools" not in body:
            errors.append(f"{agent.source_label} missing Allowed Tools section")

    errors.extend(diff_generated_views(root))
    return errors


def main() -> int:
    errors = check_agent_roster()
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("Agent roster source and generated views are current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
