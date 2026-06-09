"""Example metadata-discoverable CLI skill."""

from __future__ import annotations

import argparse
import sys

from ai_dev_template.verdicts import canonical_json, derive_verdict


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Emit deterministic verdict JSON.")
    parser.add_argument("--status", choices=["pass", "fail", "partial"], required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    sys.stdout.write(canonical_json(derive_verdict(args.status)) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

