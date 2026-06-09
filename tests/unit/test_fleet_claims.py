import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from ai_dev_template.fleet import claim_one_item, dispatch_plan, enqueue_merge


def _write_queue(path: Path, count: int = 1) -> None:
    items = [
        {
            "id": f"ITEM-{index:03d}",
            "title": f"Item {index}",
            "status": "backlog",
            "paths": [f"file-{index}.txt"],
        }
        for index in range(1, count + 1)
    ]
    path.write_text(json.dumps({"items": items}), encoding="utf-8")


def test_two_workers_cannot_claim_the_same_item(tmp_path: Path) -> None:
    queue = tmp_path / "queue.json"
    claims = tmp_path / "claims"
    worktrees = tmp_path / "worktrees"
    _write_queue(queue, count=1)

    def claim(worker_id: str) -> str | None:
        result = claim_one_item(queue, claims, worker_id, worktrees)
        return None if result is None else result.item_id

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(claim, ["worker-a", "worker-b"]))

    assert results.count("ITEM-001") == 1
    assert results.count(None) == 1
    assert len(list(claims.glob("*.json"))) == 1


def test_dispatch_plan_applies_concurrency_cap_and_backpressure(tmp_path: Path) -> None:
    queue = tmp_path / "queue.json"
    claims = tmp_path / "claims"
    worktrees = tmp_path / "worktrees"
    _write_queue(queue, count=3)
    claim_one_item(queue, claims, "worker-a", worktrees)

    plan = dispatch_plan(queue, claims, concurrency_cap=2)

    assert plan["available_slots"] == 1
    assert len(plan["dispatch_now"]) == 1
    assert len(plan["backpressure_queue"]) == 1


def test_merge_queue_refuses_duplicate_pr_id(tmp_path: Path) -> None:
    queue = tmp_path / "merge-queue"
    enqueue_merge(queue, "17", "agent/worker/item")

    try:
        enqueue_merge(queue, "17", "agent/worker/item")
    except FileExistsError:
        duplicate_blocked = True
    else:
        duplicate_blocked = False

    assert duplicate_blocked
