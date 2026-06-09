#!/usr/bin/env python3
"""Validate that the public docs-site scaffold is buildable in principle."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "docs-site/README.md",
    "docs-site/package.json",
    "docs-site/package-lock.json",
    "docs-site/docusaurus.config.js",
    "docs-site/sidebars.js",
    "docs-site/docs/index.md",
]


def check_required_files() -> list[str]:
    return [f"missing docs-site file: {path}" for path in REQUIRED_FILES if not (ROOT / path).exists()]


def check_package_json() -> list[str]:
    package_path = ROOT / "docs-site" / "package.json"
    if not package_path.exists():
        return []
    package = json.loads(package_path.read_text(encoding="utf-8"))
    scripts = package.get("scripts", {})
    dependencies = package.get("dependencies", {})
    errors = []
    if scripts.get("build") != "docusaurus build":
        errors.append('docs-site/package.json must expose "build": "docusaurus build"')
    if "@docusaurus/core" not in dependencies or "@docusaurus/preset-classic" not in dependencies:
        errors.append("docs-site/package.json must include Docusaurus core and classic preset dependencies")
    return errors


def main() -> int:
    errors = [*check_required_files(), *check_package_json()]
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("Docs-site scaffold checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
