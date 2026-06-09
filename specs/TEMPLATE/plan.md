# Implementation Plan: Feature Name

**Spec**: `spec.md`

## Summary

Implement the smallest behavior that satisfies the primary user story and proves it with deterministic tests.

## Technical Context

| Field | Decision |
|---|---|
| Language / runtime | Python 3.11+ default, substitute as project stack requires |
| Testing | `pytest` default, equivalent allowed when stack changes |
| Linting | `ruff` default, equivalent allowed when stack changes |
| Security scan | `bandit` default, equivalent allowed when stack changes |
| Dependency audit | `pip-audit` default, equivalent allowed when stack changes |
| External writes | None without explicit human approval |

## Constitution Check

| Principle | Pass / Issue | Evidence |
|---|---|---|
| Least privilege / read-only by default | Pass | No external writes planned |
| Deterministic authority | Pass | Tests and code decide behavior |
| Evidence integrity | Pass | Artifacts remain in repo |
| Trust-boundary sanitization | Pass | Inputs validated at boundary |
| Source-of-truth authority | Pass | Configs/specs/tests are authoritative |
| Quality gates | Pass | `make check` required |
| Honest docs | Pass | Docs updated with behavior |

## Test Strategy

- Unit tests for pure logic.
- Integration tests for wiring.
- Smoke tests for end-to-end health.
- Negative or regression tests for failure modes.
- Golden tests for deterministic outputs when applicable.

## Project Structure

```text
ai_dev_template/
tests/
docs/
specs/
```

## Risks

- Requirements drift if the spec is not updated.
- False confidence if tests only cover the happy path.

