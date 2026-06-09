#!/usr/bin/env python3
"""Lightweight secret-pattern scan for the template baseline."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_PARTS = {".git", ".venv", "node_modules", "build", "dist", "__pycache__", ".pytest_cache", ".ruff_cache"}
SECRET_PATTERNS = {
    "aws-access-key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "github-token": re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
    "openai-key": re.compile(r"\bsk-[A-Za-z0-9_-]{32,}\b"),
    "private-key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "slack-token": re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b"),
}


def _git_files() -> list[Path]:
    # Fixed executable, no shell, repository-local listing only.
    result = subprocess.run(  # nosec B603
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    if result.returncode != 0:
        return sorted(path for path in ROOT.rglob("*") if path.is_file())
    return [ROOT / line for line in result.stdout.splitlines() if line.strip()]


def _should_skip(path: Path) -> bool:
    try:
        relative_parts = path.relative_to(ROOT).parts
    except ValueError:
        return False
    return any(part in SKIP_PARTS for part in relative_parts)


def scan_file(path: Path) -> list[str]:
    if _should_skip(path):
        return []
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return []
    findings = []
    for name, pattern in SECRET_PATTERNS.items():
        for match in pattern.finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            display_path = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path
            findings.append(f"{display_path}:{line}: potential {name}")
    return findings


def scan_repo() -> list[str]:
    findings = []
    for path in _git_files():
        if path.exists() and path.is_file():
            findings.extend(scan_file(path))
    return findings


def main() -> int:
    findings = scan_repo()
    if findings:
        for finding in findings:
            print(f"FAIL: {finding}", file=sys.stderr)
        return 1
    print("Secret-pattern scan passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
