#!/usr/bin/env python3
"""Generate the governance committee brief deck."""

from __future__ import annotations

import argparse
from pathlib import Path

from ai_dev_template.documents import build_deck

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="generated/decks/committee-brief.pptx", help="Output PowerPoint path.")
    args = parser.parse_args()
    output = build_deck(
        "Committee Brief",
        [
            ("Governance Domains", "AI-building SDLC\nAI-usage reference implementation\nCorporate controls"),
            ("Control Evidence", "AIBOM\nThreat model\nHuman approval\nAudit logging"),
            ("Operating Model", "Playbook to weapon to gate\nIndependent review\nGenerated artifacts"),
        ],
        ROOT / args.out,
    )
    print(output.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
