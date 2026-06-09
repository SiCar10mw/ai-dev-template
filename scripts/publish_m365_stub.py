#!/usr/bin/env python3
"""Build a dry-run M365 publication plan for generated artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def build_publish_plan(config_path: Path, artifact_root: Path) -> dict[str, Any]:
    """Return a dry-run publish plan without writing to Microsoft 365."""
    config = json.loads(config_path.read_text(encoding="utf-8"))
    artifacts = sorted(
        str(path.relative_to(artifact_root))
        for path in artifact_root.rglob("*")
        if path.is_file()
    )
    return {
        "mode": "dry-run",
        "publisher": "scripts/publish_m365_stub.py",
        "config": str(config_path.relative_to(ROOT)),
        "artifact_root": str(artifact_root.relative_to(ROOT)),
        "targets": config.get("publish_targets", []),
        "artifacts": artifacts,
        "external_writes": False,
        "requires_human_approval_for_real_publish": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="config/m365-publisher.example.json", help="Publisher config path.")
    parser.add_argument("--artifact-root", default="generated", help="Generated artifact directory.")
    parser.add_argument("--out", default="out/m365/publish-plan.json", help="Dry-run output path.")
    parser.add_argument("--dry-run", action="store_true", help="Required; this stub never performs external writes.")
    args = parser.parse_args()

    if not args.dry_run:
        raise SystemExit(
            "Refusing external publication. Re-run with --dry-run or replace this stub with approved code."
        )

    output = ROOT / args.out
    output.parent.mkdir(parents=True, exist_ok=True)
    plan = build_publish_plan(ROOT / args.config, ROOT / args.artifact_root)
    output.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(output.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
