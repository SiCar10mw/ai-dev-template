#!/usr/bin/env python3
"""Generate the source-controlled architecture diagram."""

from __future__ import annotations

import argparse
from pathlib import Path

from ai_dev_template.artifacts import build_architecture_diagram

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        default="generated/architecture/project-architecture.mmd",
        help="Output Mermaid path.",
    )
    args = parser.parse_args()
    output = ROOT / args.out
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(build_architecture_diagram(), encoding="utf-8")
    print(output.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
