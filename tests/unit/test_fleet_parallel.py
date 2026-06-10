import subprocess
import threading
import time
from pathlib import Path
from typing import Any

import ai_dev_template.fleet as fleet_module
from ai_dev_template.fleet import Job, fan_out, parallel


def test_fan_out_runs_all_models_and_collects_outputs() -> None:
    calls: list[tuple[str, str]] = []

    def fake_spawn(model: str, task: str) -> str:
        calls.append((model, task))
        return f"{model} handled {task}"

    result = fan_out("same task", ["claude", "gemini", "codex"], max_workers=2, spawn_fn=fake_spawn)

    assert result == {
        "claude": "claude handled same task",
        "gemini": "gemini handled same task",
        "codex": "codex handled same task",
    }
    assert sorted(calls) == [
        ("claude", "same task"),
        ("codex", "same task"),
        ("gemini", "same task"),
    ]


def test_fan_out_captures_model_error_and_survives_batch() -> None:
    def fake_spawn(model: str, task: str) -> str:
        if model == "gemini":
            raise RuntimeError(f"{model} failed {task}")
        return f"{model} ok"

    result = fan_out("same task", ["claude", "gemini", "codex"], max_workers=3, spawn_fn=fake_spawn)

    assert result["claude"] == "claude ok"
    assert result["codex"] == "codex ok"
    assert result["gemini"] == "gemini failed same task"


def test_parallel_respects_max_workers() -> None:
    active = 0
    max_seen = 0
    lock = threading.Lock()

    def fake_spawn(model: str, task: str) -> str:
        nonlocal active, max_seen
        with lock:
            active += 1
            max_seen = max(max_seen, active)
        try:
            time.sleep(0.02)
            return f"{model}:{task}"
        finally:
            with lock:
                active -= 1

    jobs = [Job(model="codex", task=f"task-{index}", label=f"job-{index}") for index in range(6)]

    results = parallel(jobs, max_workers=2, spawn_fn=fake_spawn)

    assert max_seen <= 2
    assert [result.output for result in results] == [f"codex:task-{index}" for index in range(6)]
    assert all(result.ok for result in results)


def test_parallel_isolated_job_invokes_worktree_create_and_cleanup(
    tmp_path: Path, monkeypatch: Any
) -> None:
    repo = tmp_path / "ai-dev-template"
    repo.mkdir()
    git_calls: list[dict[str, Any]] = []

    def fake_run(argv: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        git_calls.append({"argv": argv, **kwargs})
        return subprocess.CompletedProcess(argv, 0, stdout="", stderr="")

    monkeypatch.setattr(fleet_module.subprocess, "run", fake_run)
    spawn_calls: list[dict[str, Any]] = []

    def fake_spawn(model: str, task: str, *, cwd: Path) -> str:
        spawn_calls.append({"model": model, "task": task, "cwd": cwd})
        return "isolated output"

    results = parallel(
        [Job(model="codex", task="mutate files", isolated=True, label="mutating-a")],
        max_workers=1,
        spawn_fn=fake_spawn,
        repo=repo,
    )

    worktree = tmp_path / "ai-dev-template-mutating-a"
    assert results[0].ok is True
    assert results[0].output == "isolated output"
    assert spawn_calls == [{"model": "codex", "task": "mutate files", "cwd": worktree}]
    assert [call["argv"] for call in git_calls] == [
        ["git", "worktree", "add", str(worktree), "-b", "fleet/mutating-a", "main"],
        ["git", "worktree", "remove", "--force", str(worktree)],
        ["git", "branch", "-D", "fleet/mutating-a"],
    ]
    assert all(call["cwd"] == repo for call in git_calls)
    assert all(call["check"] is True for call in git_calls)
    assert all(call["shell"] is False for call in git_calls)


def test_parallel_non_isolated_job_does_not_invoke_git(monkeypatch: Any) -> None:
    def fail_if_git_runs(*_args: Any, **_kwargs: Any) -> subprocess.CompletedProcess[str]:
        raise AssertionError("read-only jobs must not create worktrees")

    monkeypatch.setattr(fleet_module.subprocess, "run", fail_if_git_runs)

    results = parallel(
        [Job(model="claude", task="review only", isolated=False, label="review")],
        spawn_fn=lambda model, task: f"{model}:{task}",
    )

    assert results[0].ok is True
    assert results[0].output == "claude:review only"


def test_parallel_raising_job_is_result_error_and_order_is_preserved() -> None:
    jobs = [
        Job(model="claude", task="first", label="a"),
        Job(model="gemini", task="boom", label="b"),
        Job(model="codex", task="last", label="c"),
    ]

    def fake_spawn(model: str, task: str) -> str:
        if task == "boom":
            raise RuntimeError("worker exploded")
        return f"{model}:{task}"

    results = parallel(jobs, max_workers=3, spawn_fn=fake_spawn)

    assert [result.label for result in results] == ["a", "b", "c"]
    assert [result.model for result in results] == ["claude", "gemini", "codex"]
    assert results[0].ok is True
    assert results[0].output == "claude:first"
    assert results[1].ok is False
    assert results[1].output == ""
    assert results[1].error == "worker exploded"
    assert results[2].ok is True
    assert results[2].output == "codex:last"
