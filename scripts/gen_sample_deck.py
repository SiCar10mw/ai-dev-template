#!/usr/bin/env python3
"""Generate a generic project brief PowerPoint deck."""

from __future__ import annotations

import argparse
from pathlib import Path

from ai_dev_template.documents import build_project_brief_deck


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="out/powerpoints/project-brief.pptx", help="Output PowerPoint path.")
    args = parser.parse_args()
    output = build_project_brief_deck(Path(args.out))
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
