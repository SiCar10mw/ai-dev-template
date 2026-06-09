# ADR 0001: Record Architecture Decisions

| Field | Value |
|---|---|
| Status | accepted |
| Date | 2026-06-09 |
| Owners | project maintainers |

## Context

AI-assisted projects can move quickly and lose the reasoning behind durable choices. This creates review friction and
documentation drift.

## Decision

Use Architecture Decision Records for durable choices that affect architecture, security, data boundaries, model/tool
selection, deployment, documentation strategy, or long-lived developer workflow.

## Consequences

Future maintainers can inspect why a decision exists before replacing it. ADRs also give agents a source of truth that is
more reliable than memory.

## Alternatives Considered

- Keep decisions only in chat history: rejected because it is hard to audit.
- Keep decisions only in issue comments: rejected because source control should carry durable project memory.

## Evidence

See `STANDARDS.md`, `CONSTITUTION.md`, and `docs/session-memory.md`.
