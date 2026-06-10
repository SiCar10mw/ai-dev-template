# Harnessing The Three

## Current Behavior

`ai_dev_template.spawn` is the single-dispatch execution primitive for the first-class model fleet. It turns a model
choice into a local CLI invocation and returns the worker's stdout to the caller.

The orchestration layer is model-agnostic. The model is a swappable worker selected either directly by adapter key or
indirectly through `config/model-routing.json` when present, otherwise `config/model-routing.example.json`.

`ai_dev_template.fleet` is the bounded parallel layer built on top of `spawn()`. It does not reimplement model
dispatch. The new concepts are bounded concurrency and per-worker isolation for mutating jobs.

## Adapter Map

The current adapters are:

| Adapter key | CLI argv |
|---|---|
| `claude` | `["claude", "-p", task]` |
| `gemini` | `["gemini", "-p", task]` |
| `codex` | `["codex", "exec", task]` |

Arguments are passed as a list with `shell=False`. The task string is not interpolated through a shell.

Use direct dispatch when the operator has already chosen the worker:

```bash
python -m ai_dev_template.spawn --model claude --task "Summarize the current tests"
python -m ai_dev_template.spawn --model gemini --task "Review this spec for gaps"
python -m ai_dev_template.spawn --model codex --task "Draft a focused unit test"
```

Use role dispatch when the repository routing config should choose the first available preferred worker:

```bash
python -m ai_dev_template.spawn --role primary_coding --task "Implement the next scoped task"
python -m ai_dev_template.spawn --role independent_review --task "Try to refute this diff"
```

Role dispatch reads the role's `preferred_order`, maps first-class profiles such as `anthropic_claude`,
`google_gemini`, and `openai_codex_gpt` to the local adapters, and falls through only when a preferred CLI is not
installed on `PATH`.

## Operator Authentication

The repository does not store provider credentials. Each operator must install and authenticate the relevant local CLI
before dispatch:

| Worker | Operator requirement |
|---|---|
| Claude | Claude Code CLI installed and signed in. |
| Gemini | `gemini` CLI installed with a Google / GEMINI API key available to that CLI, for example through `GEMINI_API_KEY` from an approved secret source. |
| Codex | Codex CLI installed and authenticated with OpenAI/ChatGPT. |

Missing CLIs produce a clear local error naming the adapter and the required install/auth action. Authentication failures
come from the invoked CLI and should be fixed by the operator without committing secrets.

## Parallel Layer

### Fan-Out

Use fan-out to pit the first-class workers against the same task and compare their outputs. Each model runs through
`spawn(model, task)`, concurrently, with a real `ThreadPoolExecutor(max_workers=...)` cap. A single model failure is
captured as that model's string value and does not kill the batch.

```bash
python -m ai_dev_template.fleet fan-out --task "Review this spec for gaps" --models claude,gemini,codex
```

Programmatic use:

```python
from ai_dev_template.fleet import fan_out

outputs = fan_out("Review this spec for gaps", ["claude", "gemini", "codex"], max_workers=3)
```

### Parallel

Use parallel for the worker pool: N different jobs at once, bounded by `max_workers`. Each job names a model, task,
optional label, and whether it is isolated.

```json
[
  {
    "label": "review-docs",
    "model": "claude",
    "task": "Review docs/fleet.md for drift",
    "isolated": false
  },
  {
    "label": "mutating-fix",
    "model": "codex",
    "task": "Make the smallest code change for the assigned task",
    "isolated": true
  }
]
```

```bash
python -m ai_dev_template.fleet parallel --jobs jobs.json
```

Programmatic use:

```python
from ai_dev_template.fleet import Job, parallel

results = parallel(
    [
        Job(model="claude", task="Review the spec", label="review", isolated=False),
        Job(model="codex", task="Patch the failing test", label="patch", isolated=True),
    ],
    max_workers=2,
)
```

`parallel()` returns results in the same order as the input jobs. Each result has `label`, `model`, `output`, `ok`, and
`error`. Worker exceptions become `ok=False` results, and the rest of the batch continues.

### Worktree Isolation

Worktree isolation is only for mutating workers. A job with `isolated=True` runs in its own branch and git worktree:

```bash
git worktree add ../<repo>-<label> -b fleet/<label> main
```

After the worker returns, the fleet layer removes that worktree and deletes the temporary branch:

```bash
git worktree remove --force ../<repo>-<label>
git branch -D fleet/<label>
```

Read-only jobs, such as review and analysis, run without a worktree. This keeps mutating workers from colliding while
avoiding unnecessary git operations for analysis-only work.
