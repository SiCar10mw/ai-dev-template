# Tasks: AI-SAST Security Gate

## Phase 1 - Specification and Tests

- [x] T001 Confirm acceptance scenarios in `spec.md`.
- [x] T002 Add unit tests for confirmed high blocking behavior.
- [x] T003 Add regression tests for baseline suppression and ignored findings.

## Phase 2 - Implementation

- [x] T004 Implement `SecurityScanner`, `Finding`, `MockScanner`, and `MythosScanner`.
- [x] T005 Implement deterministic policy and `scripts/check_ai_sast.py`.
- [x] T006 Add config, model routing, baseline, and workflow cadences.
- [x] T007 Update docs for find-vs-decide, verification, cadence, baseline, OWASP LLM mapping, and caveats.

## Phase 3 - Verification

- [x] T008 Run focused AI-SAST tests.
- [x] T009 Run `make check`.
- [x] T010 Prepare handoff evidence and stop for human approval.

## Dependency Order

Tests and policy semantics precede workflow wiring. Merge remains human-approved.
