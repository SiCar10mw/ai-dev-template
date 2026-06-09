# Tasks: AI-SAST Security Gate

## Phase 1 - Specification and Tests

- [x] T001 Confirm acceptance scenarios in `spec.md`.
- [x] T002 Add unit tests for confirmed high blocking behavior.
- [x] T003 Add regression tests for baseline suppression and ignored findings.
- [x] T011 Extend spec acceptance scenarios for closed-loop patch proposal and deterministic fix verification.
- [x] T012 Add unit tests proving MockScanner proposes patches without applying them.
- [x] T013 Add unit tests proving `verify_fix` passes only when the finding is gone and tests pass.

## Phase 2 - Implementation

- [x] T004 Implement `SecurityScanner`, `Finding`, `MockScanner`, and `MythosScanner`.
- [x] T005 Implement deterministic policy and `scripts/check_ai_sast.py`.
- [x] T006 Add config, model routing, baseline, and workflow cadences.
- [x] T007 Update docs for find-vs-decide, verification, cadence, baseline, OWASP LLM mapping, and caveats.
- [x] T014 Implement `PatchProposal`, patch proposer protocol, MockScanner proposals, and security-review model proposals.
- [x] T015 Implement `scripts/verify_fix.py` with temporary-copy patch apply, re-scan, and regression command verification.
- [x] T016 Wire `scripts/verify_fix.py --self-test` into `make check`.

## Phase 3 - Verification

- [x] T008 Run focused AI-SAST tests.
- [x] T009 Run `make check`.
- [x] T010 Prepare handoff evidence and stop for human approval.
- [x] T017 Update docs for the closed loop and Anthropic reference harness comparison.

## Dependency Order

Tests and policy semantics precede workflow wiring. Patch proposals remain proposal-only, and merge remains
human-approved.
