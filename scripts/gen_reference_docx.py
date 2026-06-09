#!/usr/bin/env python3
"""Generate a generic reference DOCX for project deliverables."""

from __future__ import annotations

import argparse
from pathlib import Path

from ai_dev_template.documents import build_reference_docx


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="out/documents/reference.docx", help="Output DOCX path.")
    args = parser.parse_args()
    output = build_reference_docx(Path(args.out))
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
