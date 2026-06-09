#!/usr/bin/env python3
"""Fail when implementation changes do not include a documentation update."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

IMPLEMENTATION_PREFIXES = (
    "ai_dev_template/",
    "scripts/",
    "skills/",
    "tests/",
    "specs/",
    ".github/workflows/",
)
IMPLEMENTATION_FILES = {
    "Makefile",
    "pyproject.toml",
    "requirements.txt",
    "requirements-dev.txt",
    ".mcp.json",
    ".mcp.example.json",
    ".vscode/mcp.json",
    ".vscode/mcp.example.json",
    ".pre-commit-config.yaml",
    ".gitleaks.toml",
}
DOC_PREFIXES = ("docs/", "docs-site/docs/", "docs-site/src/", "docs-site/static/", "generated/")
DOC_FILES = {
    "README.md",
    "STANDARDS.md",
    "CONSTITUTION.md",
    "GOVERNANCE.md",
    "AGENTS.md",
    "CLAUDE.md",
    "GEMINI.md",
    "BACKLOG.md",
    "CHANGELOG.md",
    "docs-site/README.md",
    "docs-site/package.json",
    "docs-site/docusaurus.config.js",
    "docs-site/sidebars.js",
}


def _git(args: list[str]) -> list[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def _changed_from_env() -> set[str]:
    raw = os.environ.get("DOCS_IMPACT_CHANGED_FILES", "")
    return {line.strip() for line in raw.splitlines() if line.strip()}


def changed_files(*, staged: bool) -> set[str]:
    env_files = _changed_from_env()
    if env_files:
        return env_files

    if staged:
        return set(_git(["diff", "--name-only", "--cached"]))

    base_ref = os.environ.get("GITHUB_BASE_REF")
    if base_ref:
        for diff_ref in (f"origin/{base_ref}...HEAD", f"{base_ref}...HEAD"):
            files = _git(["diff", "--name-only", diff_ref])
            if files:
                return set(files)

    return set(_git(["diff", "--name-only"])) | set(_git(["diff", "--name-only", "--cached"]))


def is_implementation_change(path: str) -> bool:
    return path in IMPLEMENTATION_FILES or path.startswith(IMPLEMENTATION_PREFIXES)


def is_documentation_change(path: str) -> bool:
    return path in DOC_FILES or path.startswith(DOC_PREFIXES)


def check_docs_impact(files: set[str]) -> list[str]:
    implementation_changes = sorted(path for path in files if is_implementation_change(path))
    documentation_changes = sorted(path for path in files if is_documentation_change(path))
    if implementation_changes and not documentation_changes:
        return [
            "Implementation changes require a documentation update.",
            "Update docs/, docs-site/docs/, README.md, STANDARDS.md, AGENTS.md, CLAUDE.md, "
            "CONSTITUTION.md, BACKLOG.md, CHANGELOG.md, or docs-site configuration.",
            "If there is no audience-facing behavior change, record that decision in docs/docs-impact.md.",
            f"Implementation files detected: {', '.join(implementation_changes)}",
        ]
    return []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--staged", action="store_true", help="Check staged files for the git pre-commit hook.")
    args = parser.parse_args()

    files = changed_files(staged=args.staged)
    errors = check_docs_impact(files)
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("Documentation impact check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
