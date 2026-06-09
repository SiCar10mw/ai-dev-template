# Specs

Spec-first delivery is mandatory. A specific Spec Kit implementation is recommended but swappable.

Every meaningful feature should produce reviewable artifacts:

```text
specify -> plan -> tasks -> implement
```

| Artifact | Purpose |
|---|---|
| `spec.md` | User value, scope, acceptance scenarios, measurable outcomes |
| `plan.md` | Technical approach, constitution check, architecture and test strategy |
| `tasks.md` | Ordered, independently testable work items |

## How to Start a Feature

1. Copy `specs/TEMPLATE/` to `specs/NNN-short-name/`.
2. Fill `spec.md` without implementation details.
3. Fill `plan.md` with the technical approach and constitution check.
4. Fill `tasks.md` with testable tasks.
5. Implement with tests.

## Rules

- Specs are source-of-truth artifacts.
- Assumptions must be written down.
- Tests should map back to acceptance scenarios.
- Do not skip the constitution check.

