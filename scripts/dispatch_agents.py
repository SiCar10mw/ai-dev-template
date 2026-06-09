#!/usr/bin/env python3
"""Plan parallel agent dispatch with a concurrency cap and backpressure."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ai_dev_template.fleet import dispatch_plan


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--queue", default="queue/backlog-queue.json", help="Backlog queue JSON path.")
    parser.add_argument("--claims-dir", default=".fleet/claims", help="Directory for atomic claim locks.")
    parser.add_argument("--concurrency-cap", type=int, default=2, help="Maximum concurrent workers.")
    args = parser.parse_args()

    plan = dispatch_plan(Path(args.queue), Path(args.claims_dir), args.concurrency_cap)
    print(json.dumps(plan, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
