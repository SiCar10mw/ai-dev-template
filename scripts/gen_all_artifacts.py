#!/usr/bin/env python3
"""Generate all committed derived artifacts."""

from __future__ import annotations

import argparse
from pathlib import Path

from ai_dev_template.artifacts import generate_artifacts

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", default="generated", help="Output directory for generated artifacts.")
    args = parser.parse_args()
    artifacts = generate_artifacts(ROOT, ROOT / args.out_dir)
    for artifact in artifacts:
        print(artifact.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
