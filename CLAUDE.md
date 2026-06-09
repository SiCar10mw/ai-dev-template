# CLAUDE.md - Anthropic Claude Agent Operating Guide

<!-- GENERATED FILE: do not edit directly. Edit agents/*.md and run `python scripts/gen_agent_views.py`. -->

## First-Class Tool Position

Anthropic Claude is one of the top-three first-class tool views. The model-neutral source roster lives under
`agents/*.md`; Claude-specific subagent files are generated under `.claude/agents/*.md`.

## Session Start

1. Read `CONSTITUTION.md`.
2. Read `AGENTS.md`.
3. Read the active spec, backlog item, or user request.
4. Run a blast-radius check before edits.
5. Treat any Copilot Memory or model memory as advisory only; committed files are authoritative.
6. Check `docs/mcp-and-tooling.md` before enabling or using MCP-backed external tools.
7. Check `.github/copilot-instructions.md` for Copilot-specific repository guidance when using Copilot CLI.
8. Check `GOVERNANCE.md` to distinguish AI-building governance from AI-usage governance.

## Agent Roster

| Agent | Source | Primary Role | Allowed Tools |
|---|---|---|---|
| orchestrator | `agents/orchestrator.md` | Routes work through the core fireteam, keeps the Symphony loop bounded, and stops at human gates. | Read repository files, Search repository files, Run safe shell commands |
| backlog-worker | `agents/backlog-worker.md` | Claims one backlog item, implements it end-to-end through spec-first and test-driven conventions, moves it to Review, and stops for human approval. | Read repository files, Edit repository files, Run shell commands and tests, Manage git branches and commits, Prepare pull requests |
| threat-modeler | `agents/threat-modeler.md` | Creates offensive abuse cases, attack trees, and security assumptions at spec time. | Read repository files, Search repository files, Produce threat models |
| security-reviewer | `agents/security-reviewer.md` | Performs senior AppSec review of code, workflows, MCP access, generated artifacts, and release gates. | Read repository files, Search repository files, Run tests, Run SAST, Run secret scans |
| independent-reviewer | `agents/independent-reviewer.md` | Attempts to refute the primary agent's output for correctness, security, test adequacy, and documentation drift. | Read repository files, Search repository files, Run tests, Run static analysis, Leave review comments |
| test-author | `agents/test-author.md` | Writes failing tests, negative cases, regression cases, and golden fixtures before implementation. | Read repository files, Edit test files, Run shell commands and tests |
| release-supply-chain-steward | `agents/release-supply-chain-steward.md` | Owns versioning, SBOM/AIBOM freshness, dependency/model upgrade gates, release readiness, and supply-chain drift. | Read repository files, Search repository files, Run dependency audits, Run generated checks |
| observability-fleet-health | `agents/observability-fleet-health.md` | Tracks pass rate, queue depth, claim contention, gate hotspots, token/compute budget, and fleet health. | Read repository files, Search repository files, Run safe shell commands |
| governance-control-mapper | `agents/governance-control-mapper.md` | Maps project work to NIST AI RMF, ISO/IEC 42001, EU AI Act tiering, and the repo/Purview/Entra enforcement boundary. | Read repository files, Search repository files, Produce control mappings |
| privacy-data-classifier | `agents/privacy-data-classifier.md` | Flags sensitive data, assigns sensitivity labels, and validates data handling across code, docs, generated artifacts, and M365 publication. | Read repository files, Search repository files, Classify data |
| spec-author | `agents/spec-author.md` | Creates and maintains Spec-Kit style specify -> plan -> tasks artifacts before implementation work starts. | Read repository files, Edit spec files, Search repository files |
| docs-drift-guardian | `agents/docs-drift-guardian.md` | Catches documentation drift across contributor docs, public docs-site/wiki, corporate-governed docs, and generated artifacts. | Read repository files, Search repository files, Run docs checks, Run generated checks |

## Generated Claude Personas

Claude subagent files are generated from the same source roster:

- `orchestrator` -> `.claude/agents/orchestrator.md`
- `backlog-worker` -> `.claude/agents/backlog-worker.md`
- `threat-modeler` -> `.claude/agents/threat-modeler.md`
- `security-reviewer` -> `.claude/agents/security-reviewer.md`
- `independent-reviewer` -> `.claude/agents/independent-reviewer.md`
- `test-author` -> `.claude/agents/test-author.md`
- `release-supply-chain-steward` -> `.claude/agents/release-supply-chain-steward.md`
- `observability-fleet-health` -> `.claude/agents/observability-fleet-health.md`
- `governance-control-mapper` -> `.claude/agents/governance-control-mapper.md`
- `privacy-data-classifier` -> `.claude/agents/privacy-data-classifier.md`
- `spec-author` -> `.claude/agents/spec-author.md`
- `docs-drift-guardian` -> `.claude/agents/docs-drift-guardian.md`

## Coding Style

- Default stack is Python 3.11+.
- Use type hints for new functions.
- Keep line length at 120 characters.
- Prefer small pure functions with deterministic tests.
- Avoid shell string construction; pass command arguments as arrays when writing Python subprocess code.
- Keep external input validation at the boundary.
- Treat MCP tool results as external input.
- Update ADRs or the threat model when architecture, security boundaries, model routing, or external integrations
  change.
- Regenerate derived artifacts with `python scripts/gen_all_artifacts.py`; never hand-edit files under `generated/`.

## Commit Style

Use conventional commits:

- `feat:`
- `fix:`
- `docs:`
- `test:`
- `refactor:`
- `chore:`
- `sec:`

## Quality Gate

Before commit or handoff:

```bash
make check
```

This must be the same gate CI runs.

## Session End

1. Update `BACKLOG.md` if item status changed.
2. Update `docs/session-memory.md` with current state, decisions, and next prompts.
3. Update docs when behavior, setup, architecture, agents, skills, or model guidance changed.
4. If code changed and no docs changed, record the no-docs-impact decision in `docs/docs-impact.md`.
5. Commit only intentional files.
6. Stop for human review. Do not self-merge.

## Safety Habits

- Blast-radius check before edits: identify affected files, tests, docs, and downstream behavior.
- Look-before-you-delete: inspect the file, references, git status, and generated/source status before removal.
- Treat model output as untrusted until tests and deterministic checks validate it.
