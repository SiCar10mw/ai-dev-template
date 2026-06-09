#!/usr/bin/env python3
"""Generate the AI Bill of Materials."""

from __future__ import annotations

import argparse
from pathlib import Path

from ai_dev_template.artifacts import build_aibom, write_json

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="generated/aibom/aibom.json", help="Output JSON path.")
    args = parser.parse_args()
    output = write_json(ROOT / args.out, build_aibom(ROOT))
    print(output.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
