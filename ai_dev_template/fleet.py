"""Fleet-safe agent dispatch primitives."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class BacklogItem:
    """A queue item available to one worker."""

    item_id: str
    title: str
    paths: tuple[str, ...]


@dataclass(frozen=True)
class Claim:
    """A successful atomic claim."""

    item_id: str
    worker_id: str
    branch: str
    worktree: str
    lock_path: Path


def load_queue(queue_path: Path) -> list[BacklogItem]:
    """Load backlog queue items from JSON."""
    data = json.loads(queue_path.read_text(encoding="utf-8"))
    items = []
    for raw in data.get("items", []):
        if raw.get("status") != "backlog":
            continue
        item_id = str(raw["id"])
        paths = tuple(str(path) for path in raw.get("paths", []))
        items.append(BacklogItem(item_id=item_id, title=str(raw.get("title", item_id)), paths=paths))
    return items


def _branch_name(worker_id: str, item_id: str) -> str:
    safe_worker = "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in worker_id.lower())
    safe_item = "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in item_id.lower())
    return f"agent/{safe_worker}/{safe_item}"


def _claim_payload(item: BacklogItem, worker_id: str, worktree_root: Path) -> dict[str, Any]:
    branch = _branch_name(worker_id, item.item_id)
    return {
        "item_id": item.item_id,
        "title": item.title,
        "worker_id": worker_id,
        "branch": branch,
        "worktree": str(worktree_root / branch.replace("/", "-")),
        "paths": list(item.paths),
    }


def claim_one_item(queue_path: Path, claims_dir: Path, worker_id: str, worktree_root: Path) -> Claim | None:
    """Atomically claim exactly one backlog item.

    The claim operation uses O_CREAT | O_EXCL, so two workers racing for the same item cannot both win.
    """
    claims_dir.mkdir(parents=True, exist_ok=True)
    worktree_root.mkdir(parents=True, exist_ok=True)
    for item in load_queue(queue_path):
        lock_path = claims_dir / f"{item.item_id}.json"
        payload = _claim_payload(item, worker_id, worktree_root)
        try:
            fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError:
            continue
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
        return Claim(
            item_id=item.item_id,
            worker_id=worker_id,
            branch=str(payload["branch"]),
            worktree=str(payload["worktree"]),
            lock_path=lock_path,
        )
    return None


def active_claims(claims_dir: Path) -> list[dict[str, Any]]:
    """Return active claim payloads."""
    if not claims_dir.exists():
        return []
    claims = []
    for path in sorted(claims_dir.glob("*.json")):
        claims.append(json.loads(path.read_text(encoding="utf-8")))
    return claims


def dispatch_plan(queue_path: Path, claims_dir: Path, concurrency_cap: int) -> dict[str, Any]:
    """Build a deterministic dispatch plan with backpressure."""
    if concurrency_cap < 1:
        raise ValueError("concurrency_cap must be >= 1")
    active = active_claims(claims_dir)
    available_slots = max(concurrency_cap - len(active), 0)
    queued = [
        item.item_id
        for item in load_queue(queue_path)
        if not (claims_dir / f"{item.item_id}.json").exists()
    ]
    return {
        "concurrency_cap": concurrency_cap,
        "active": len(active),
        "available_slots": available_slots,
        "dispatch_now": queued[:available_slots],
        "backpressure_queue": queued[available_slots:],
    }


def enqueue_merge(merge_queue: Path, pr_id: str, branch: str) -> Path:
    """Serialize a PR merge request into a local merge queue."""
    merge_queue.mkdir(parents=True, exist_ok=True)
    path = merge_queue / f"{pr_id}.json"
    payload = {"pr_id": pr_id, "branch": branch, "status": "queued"}
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return path
