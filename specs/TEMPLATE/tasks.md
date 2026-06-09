# Tasks: Feature Name

## Phase 1 - Specification and Tests

- [ ] T001 Confirm the acceptance scenarios in `spec.md`.
- [ ] T002 Add or update unit tests for pure logic.
- [ ] T003 Add or update negative or regression tests for known failure modes.

## Phase 2 - Implementation

- [ ] T004 Implement the smallest scoped behavior.
- [ ] T005 Validate trust-boundary input handling.
- [ ] T006 Update docs if behavior, setup, agents, or CI changed.

## Phase 3 - Verification

- [ ] T007 Run `make check`.
- [ ] T008 Run independent/adversarial review for substantial changes.
- [ ] T009 Prepare pull request evidence and stop for human approval.

## Dependency Order

Tests and acceptance criteria come before implementation. Verification comes after implementation. Merge comes only after human approval.

