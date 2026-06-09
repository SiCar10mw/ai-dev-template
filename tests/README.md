# Tests

Tests are split by scope.

| Bucket | Scope | Examples |
|---|---|---|
| `unit/` | One function or module | Sanitization, deterministic verdicts, golden tripwires |
| `integration/` | Components wired together | CLI skill invocation |
| `smoke/` | End-to-end health | Import and gate health |
| `fixtures/` | Shared committed fixtures | Golden expected outputs |

## Mandatory Rules

- Tests are offline by default.
- Tests own their fixtures.
- Tests must not depend on sibling side effects.
- Tests must not depend on gitignored artifacts.
- Tests must not depend on today's date.
- Deterministic outputs should have committed golden fixtures.
- Use the bare `pytest` console script locally because CI uses the bare `pytest` console script.

## Commands

```bash
pytest
make check
```

