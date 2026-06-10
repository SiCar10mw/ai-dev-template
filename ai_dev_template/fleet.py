"""Fleet-safe agent dispatch primitives."""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import subprocess
import sys
from collections.abc import Callable, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from ai_dev_template.spawn import spawn

REPO = Path(__file__).resolve().parents[1]
SpawnFunction = Callable[..., str]
GitRunner = Callable[..., subprocess.CompletedProcess[str]]


@dataclass(frozen=True)
class Job:
    """A unit of work for one model worker."""

    model: str
    task: str
    isolated: bool = False
    label: str = ""


@dataclass(frozen=True)
class Result:
    """The outcome of one fleet job."""

    label: str
    model: str
    output: str
    ok: bool
    error: str


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


def fan_out(task: str, models: list[str], *, max_workers: int = 4, spawn_fn: SpawnFunction = spawn) -> dict[str, str]:
    """Run the same task across the requested models with bounded concurrency."""
    _validate_max_workers(max_workers)
    if not models:
        return {}

    outputs_by_index: dict[int, str] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(spawn_fn, model, task): index
            for index, model in enumerate(models)
        }
        for future in concurrent.futures.as_completed(futures):
            index = futures[future]
            try:
                outputs_by_index[index] = future.result()
            except Exception as exc:  # noqa: BLE001 - one failed worker must not abort the fleet.
                outputs_by_index[index] = _error_string(exc)

    return {model: outputs_by_index[index] for index, model in enumerate(models)}


def parallel(
    jobs: list[Job],
    *,
    max_workers: int = 4,
    spawn_fn: SpawnFunction = spawn,
    repo: Path = REPO,
) -> list[Result]:
    """Run model jobs with bounded concurrency and per-mutating-worker worktree isolation."""
    _validate_max_workers(max_workers)
    if not jobs:
        return []

    results: list[Result | None] = [None] * len(jobs)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(_run_job, index, job, spawn_fn, repo): index
            for index, job in enumerate(jobs)
        }
        for future in concurrent.futures.as_completed(futures):
            index = futures[future]
            try:
                results[index] = future.result()
            except Exception as exc:  # noqa: BLE001 - one failed worker must not abort the fleet.
                job = jobs[index]
                results[index] = Result(
                    label=job.label,
                    model=job.model,
                    output="",
                    ok=False,
                    error=_error_string(exc),
                )

    return [_require_result(result) for result in results]


def _run_job(index: int, job: Job, spawn_fn: SpawnFunction, repo: Path) -> Result:
    if not job.isolated:
        return _spawn_result(job, spawn_fn)

    safe_label = _worktree_label(job, index)
    branch = f"fleet/{safe_label}"
    worktree = repo.parent / f"{repo.name}-{safe_label}"
    created = False
    cleanup_errors: list[str] = []

    try:
        _run_git(["git", "worktree", "add", str(worktree), "-b", branch, "main"], cwd=repo)
        created = True
        result = _spawn_result(job, spawn_fn, cwd=worktree)
    except Exception as exc:  # noqa: BLE001 - convert per-job failures into Result.
        result = Result(label=job.label, model=job.model, output="", ok=False, error=_error_string(exc))
    finally:
        if created:
            cleanup_errors.extend(_cleanup_worktree(repo, worktree, branch))

    if cleanup_errors:
        combined_error = "; ".join([error for error in [result.error, *cleanup_errors] if error])
        return Result(label=result.label, model=result.model, output=result.output, ok=False, error=combined_error)
    return result


def _spawn_result(job: Job, spawn_fn: SpawnFunction, cwd: Path | None = None) -> Result:
    try:
        if cwd is None:
            output = spawn_fn(job.model, job.task)
        else:
            output = spawn_fn(job.model, job.task, cwd=cwd)
    except Exception as exc:  # noqa: BLE001 - convert per-job failures into Result.
        return Result(label=job.label, model=job.model, output="", ok=False, error=_error_string(exc))
    return Result(label=job.label, model=job.model, output=output, ok=True, error="")


def _cleanup_worktree(repo: Path, worktree: Path, branch: str) -> list[str]:
    errors: list[str] = []
    for argv in (
        ["git", "worktree", "remove", "--force", str(worktree)],
        ["git", "branch", "-D", branch],
    ):
        try:
            _run_git(argv, cwd=repo)
        except Exception as exc:  # noqa: BLE001 - preserve the original job result and report cleanup failures.
            errors.append(_error_string(exc))
    return errors


def _run_git(argv: list[str], *, cwd: Path, runner: GitRunner | None = None) -> subprocess.CompletedProcess[str]:
    git_runner = subprocess.run if runner is None else runner
    return git_runner(argv, cwd=cwd, check=True, capture_output=True, text=True, shell=False)


def _validate_max_workers(max_workers: int) -> None:
    if max_workers < 1:
        raise ValueError("max_workers must be >= 1")


def _worktree_label(job: Job, index: int) -> str:
    raw_label = job.label or f"{job.model}-{index + 1}"
    safe = "".join(ch.lower() if ch.isalnum() or ch in "._-" else "-" for ch in raw_label)
    safe = safe.strip(".-")
    if not safe:
        raise ValueError("isolated job label must contain at least one safe character")
    return safe


def _error_string(exc: BaseException) -> str:
    message = str(exc)
    if isinstance(exc, subprocess.CalledProcessError):
        stderr = exc.stderr.decode() if isinstance(exc.stderr, bytes) else exc.stderr
        stdout = exc.stdout.decode() if isinstance(exc.stdout, bytes) else exc.stdout
        detail = stderr or stdout
        if detail:
            message = f"{message}: {detail.strip()}"
    return message or exc.__class__.__name__


def _require_result(result: Result | None) -> Result:
    if result is None:
        raise RuntimeError("fleet job did not produce a result")
    return result


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


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point for bounded fleet dispatch."""
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    fan_out_parser = subparsers.add_parser("fan-out", help="Run the same task across multiple models.")
    fan_out_parser.add_argument("--task", required=True)
    fan_out_parser.add_argument("--models", required=True, help="Comma-separated model adapter keys.")
    fan_out_parser.add_argument("--max-workers", type=int, default=4)

    parallel_parser = subparsers.add_parser("parallel", help="Run a JSON job list with bounded concurrency.")
    parallel_parser.add_argument("--jobs", required=True, type=Path)
    parallel_parser.add_argument("--max-workers", type=int, default=4)

    args = parser.parse_args(argv)
    try:
        if args.command == "fan-out":
            models = [model.strip() for model in args.models.split(",") if model.strip()]
            output: Any = fan_out(args.task, models, max_workers=args.max_workers)
        else:
            output = [asdict(result) for result in parallel(_load_jobs(args.jobs), max_workers=args.max_workers)]
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    json.dump(output, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


def _load_jobs(path: Path) -> list[Job]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("jobs")
    if not isinstance(data, list):
        raise ValueError("jobs file must contain a JSON list or an object with a jobs list")

    jobs: list[Job] = []
    for index, raw_job in enumerate(data, start=1):
        if not isinstance(raw_job, dict):
            raise ValueError(f"job {index} must be a JSON object")
        model = raw_job.get("model")
        task = raw_job.get("task")
        isolated = raw_job.get("isolated", False)
        label = raw_job.get("label", "")
        if not isinstance(model, str) or not model.strip():
            raise ValueError(f"job {index} model must be a non-empty string")
        if not isinstance(task, str) or not task.strip():
            raise ValueError(f"job {index} task must be a non-empty string")
        if not isinstance(isolated, bool):
            raise ValueError(f"job {index} isolated must be a boolean")
        if not isinstance(label, str):
            raise ValueError(f"job {index} label must be a string")
        jobs.append(Job(model=model.strip(), task=task, isolated=isolated, label=label))
    return jobs


if __name__ == "__main__":
    raise SystemExit(main())
