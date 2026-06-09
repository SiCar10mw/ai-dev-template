#!/usr/bin/env python3
"""Fail when committed generated artifacts are stale."""

from __future__ import annotations

import filecmp
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from ai_dev_template.artifacts import generate_artifacts

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"


def stale_artifacts(expected_dir: Path, actual_dir: Path) -> list[str]:
    """Return stale, missing, or unexpected generated artifact paths."""
    errors = []
    expected_files = sorted(path for path in expected_dir.rglob("*") if path.is_file())
    actual_files = sorted(path for path in actual_dir.rglob("*") if path.is_file())
    expected_rel = {path.relative_to(expected_dir) for path in expected_files}
    actual_rel = {path.relative_to(actual_dir) for path in actual_files}

    for missing in sorted(expected_rel - actual_rel):
        errors.append(f"missing committed generated artifact: {missing}")
    for unexpected in sorted(actual_rel - expected_rel):
        errors.append(f"unexpected committed generated artifact: {unexpected}")
    for relative in sorted(expected_rel & actual_rel):
        if not filecmp.cmp(expected_dir / relative, actual_dir / relative, shallow=False):
            errors.append(f"stale generated artifact: {relative}")
    return errors


def check_generated_artifacts() -> list[str]:
    """Regenerate artifacts in a temp directory and compare them to committed artifacts."""
    if not GENERATED.exists():
        return ["generated/ directory is missing; run python scripts/gen_all_artifacts.py"]

    with TemporaryDirectory() as tmp:
        expected = Path(tmp) / "generated"
        generate_artifacts(ROOT, expected)
        errors = stale_artifacts(expected, GENERATED)
    if errors:
        return [*errors, "run python scripts/gen_all_artifacts.py and commit the regenerated artifacts"]
    return []


def main() -> int:
    errors = check_generated_artifacts()
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("Generated artifact drift check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
