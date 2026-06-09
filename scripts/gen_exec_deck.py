#!/usr/bin/env python3
"""Generate the executive brief deck."""

from __future__ import annotations

import argparse
from pathlib import Path

from ai_dev_template.documents import build_deck

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="generated/decks/executive-brief.pptx", help="Output PowerPoint path.")
    args = parser.parse_args()
    output = build_deck(
        "Executive Brief",
        [
            ("Decision", "Human-governed AI-assisted delivery\nDeterministic gates\nGenerated evidence"),
            ("Risk", "Least privilege\nSensitive-data controls\nNo autonomous release decisions"),
            ("Next", "Review backlog\nRun make check\nPublish governed outputs through M365"),
        ],
        ROOT / args.out,
    )
    print(output.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
