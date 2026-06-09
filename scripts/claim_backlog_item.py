#!/usr/bin/env python3
"""Atomically claim one backlog item for one worker."""

from __future__ import annotations

import argparse
from pathlib import Path

from ai_dev_template.fleet import claim_one_item


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--queue", default="queue/backlog-queue.json", help="Backlog queue JSON path.")
    parser.add_argument("--claims-dir", default=".fleet/claims", help="Directory for atomic claim locks.")
    parser.add_argument("--worktree-root", default="../.agent-worktrees", help="Root directory for agent worktrees.")
    parser.add_argument("--worker-id", required=True, help="Unique worker id.")
    args = parser.parse_args()

    claim = claim_one_item(Path(args.queue), Path(args.claims_dir), args.worker_id, Path(args.worktree_root))
    if claim is None:
        print("No claim available")
        return 2
    print(f"{claim.item_id} {claim.branch} {claim.worktree}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
