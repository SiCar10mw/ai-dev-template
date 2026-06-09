#!/usr/bin/env python3
"""Queue a pull request for serialized merge."""

from __future__ import annotations

import argparse
from pathlib import Path

from ai_dev_template.fleet import enqueue_merge


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--queue-dir", default=".fleet/merge-queue", help="Merge queue directory.")
    parser.add_argument("--pr-id", required=True, help="Pull request id or number.")
    parser.add_argument("--branch", required=True, help="Per-agent branch to merge.")
    args = parser.parse_args()

    path = enqueue_merge(Path(args.queue_dir), args.pr_id, args.branch)
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
