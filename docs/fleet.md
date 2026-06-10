# Harnessing The Three

## Current Behavior

`ai_dev_template.spawn` is the single-dispatch execution primitive for the first-class model fleet. It turns a model
choice into a local CLI invocation and returns the worker's stdout to the caller.

The orchestration layer is model-agnostic. The model is a swappable worker selected either directly by adapter key or
indirectly through `config/model-routing.json` when present, otherwise `config/model-routing.example.json`.

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

## Future Layer

This primitive dispatches one task to one worker. Parallel fan-out, concurrency caps, isolated worktrees, atomic claims,
and merge serialization are a later layer above this primitive, not part of `spawn()`.
