#!/usr/bin/env python3
"""Verify mandatory principles are present in standards and have build-failing tripwires."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "config" / "mandatory-principles.json"


def load_principles(root: Path = ROOT) -> list[dict[str, Any]]:
    """Load the mandatory-principles registry."""
    data = json.loads((root / "config" / "mandatory-principles.json").read_text(encoding="utf-8"))
    principles = data.get("principles", [])
    if not isinstance(principles, list):
        raise ValueError("config/mandatory-principles.json principles must be a list")
    return principles


def standards_principles(root: Path = ROOT) -> list[str]:
    """Parse the first STANDARDS.md mandatory-principles table."""
    text = (root / "STANDARDS.md").read_text(encoding="utf-8")
    rows: list[str] = []
    in_table = False
    for line in text.splitlines():
        if line.startswith("| MANDATORY Principle |"):
            in_table = True
            continue
        if in_table and line.startswith("## "):
            break
        if not in_table or not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if not cells or cells[0].startswith("---"):
            continue
        rows.append(cells[0])
    return rows


def enforcement_corpus(root: Path = ROOT) -> str:
    """Return text from files that can enforce or prove tripwires."""
    paths = [
        ".pre-commit-config.yaml",
        ".github/workflows/ci.yml",
        ".github/pull_request_template.md",
        "Makefile",
        "scripts/ci_check.sh",
        "scripts/check_template_conformance.py",
        "scripts/check_generated_artifacts.py",
        "scripts/check_docs_impact.py",
        "scripts/check_profile_boundary.py",
        "tests/unit/test_generated_artifacts.py",
        "tests/unit/test_docs_impact.py",
        "tests/unit/test_verdict_golden.py",
        "tests/unit/test_sanitize.py",
        "tests/unit/test_principle_tripwires.py",
        "docs/agent-fireteam.md",
        "docs/machine-user-pr-flow.md",
        "docs/docs-boundary.md",
        "docs/m365-integration.md",
    ]
    text = []
    for relative in paths:
        path = root / relative
        if path.exists():
            text.append(path.read_text(encoding="utf-8"))
    text.extend(path.name for path in (root / "tests").rglob("*.py"))
    text.extend(str(path.relative_to(root)) for path in (root / ".claude" / "agents").glob("*.md"))
    return "\n".join(text).lower()


def check_principles_have_tripwires(principles: list[dict[str, Any]]) -> list[str]:
    """Fail if any principle lacks tripwires or a negative probe."""
    errors = []
    ids = set()
    for principle in principles:
        pid = str(principle.get("id", ""))
        statement = str(principle.get("statement", ""))
        if not pid:
            errors.append(f"principle missing id: {statement}")
        if pid in ids:
            errors.append(f"duplicate principle id: {pid}")
        ids.add(pid)
        if not statement:
            errors.append(f"{pid} missing statement")
        if not principle.get("tripwires"):
            errors.append(f"{pid} has no tripwire")
        if not principle.get("negative_probe"):
            errors.append(f"{pid} has no negative probe")
        if principle.get("profile") not in {"core", "corporate"}:
            errors.append(f"{pid} profile must be core or corporate")
    return errors


def check_standards_registry_alignment(
    principles: list[dict[str, Any]],
    standards_rows: list[str],
) -> list[str]:
    """Fail if STANDARDS.md and the principle registry drift."""
    registry_statements = {str(principle.get("statement", "")) for principle in principles}
    standards_statements = set(standards_rows)
    errors = []
    for missing in sorted(registry_statements - standards_statements):
        errors.append(f"registry principle missing from STANDARDS.md: {missing}")
    for missing in sorted(standards_statements - registry_statements):
        errors.append(f"STANDARDS.md principle missing from registry: {missing}")
    return errors


def tripwire_is_resolvable(tripwire: str, corpus: str, root: Path = ROOT) -> bool:
    """Return whether a tripwire points to a real file, command, job, test, or conformance marker."""
    candidate = tripwire.split(":", 1)[0]
    if candidate.endswith((".py", ".md", ".json", ".toml", ".yaml", ".yml")) and (root / candidate).exists():
        return True
    if candidate.startswith(("tests/", "generated/", "config/", "docs/", ".github/", ".claude/")):
        return (root / candidate).exists()
    normalized = re.sub(r"[^a-z0-9_. -]+", " ", tripwire.lower()).strip()
    tokens = [token for token in normalized.split() if len(token) >= 4]
    if not tokens:
        return False
    return any(token in corpus for token in tokens)


def check_tripwire_references(principles: list[dict[str, Any]], root: Path = ROOT) -> list[str]:
    """Fail if tripwire references are not discoverable in enforcement files."""
    corpus = enforcement_corpus(root)
    errors = []
    for principle in principles:
        pid = str(principle.get("id", ""))
        for tripwire in principle.get("tripwires", []):
            if not tripwire_is_resolvable(str(tripwire), corpus, root):
                errors.append(f"{pid} has unresolved tripwire reference: {tripwire}")
    return errors


def main() -> int:
    principles = load_principles()
    errors = [
        *check_principles_have_tripwires(principles),
        *check_standards_registry_alignment(principles, standards_principles()),
        *check_tripwire_references(principles),
    ]
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("Mandatory principle tripwire audit passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
