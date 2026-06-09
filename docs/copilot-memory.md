# GitHub Copilot Memory

GitHub Copilot Memory is a recommended supplemental feature when it is available in the account or organization.

It is not a replacement for `CONSTITUTION.md`, `STANDARDS.md`, `AGENTS.md`, specs, tests, or committed documentation.

## What It Stores

Copilot Memory can store:

- repository-level facts, such as coding conventions, architectural decisions, build commands, and project-specific rules
- user-level preferences, such as personal interaction preferences

## Where It Applies

GitHub documents Copilot Memory as public preview. It is currently used by:

- Copilot cloud agent
- Copilot code review
- Copilot CLI

Feature availability and admin policy can vary by plan and organization.

## Governance Rules

- Treat Copilot Memory as advisory context.
- Committed repository files remain the source of truth.
- If memory conflicts with `CONSTITUTION.md`, `STANDARDS.md`, specs, tests, or code, ignore the memory and flag the drift.
- Do not rely on memory for secrets, credentials, or approval state.
- Repository owners should periodically review and delete incorrect or stale repository-level facts when the feature is enabled.

## Recommended Memories to Encourage

Copilot may learn these safely because they are backed by committed files:

- `make check` is the local and CI gate.
- `pytest` is intentionally run as the bare console script.
- `pyproject.toml` sets `pythonpath = ["."]` and `testpaths = ["tests"]`.
- The backlog worker never self-merges.
- Deterministic outputs use committed golden fixtures.
- `CONSTITUTION.md` wins on conflicts.

## Memories to Avoid

Do not intentionally create memory for:

- secrets
- credential locations
- private endpoint details
- temporary workarounds
- unmerged branch-only behavior
- approval status

