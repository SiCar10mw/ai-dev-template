# Tasks: Centralized Identity And Secrets

## Phase 1 - Specification and Tests

- [x] T001 Confirm acceptance scenarios in `spec.md`.
- [x] T002 Add unit tests for provider resolution and fallback behavior.
- [x] T003 Add negative conformance tests for placeholder-only `.env.example` and provider-based secret access.

## Phase 2 - Implementation

- [x] T004 Implement `ai_dev_template/secrets.py` with EnvProvider, KeyringProvider, and KeyVaultProvider.
- [x] T005 Add `config/secrets.example.json` with offline default resolution.
- [x] T006 Wire conformance checks for placeholder `.env.example`, secrets config, and direct secret access.
- [x] T007 Update AI-SAST secret lookup to use the provider interface.
- [x] T008 Update identity/secrets standards and docs.

## Phase 3 - Verification

- [x] T009 Regenerate generated artifacts if source hashes change.
- [x] T010 Run focused tests.
- [x] T011 Run `make check`.
- [x] T012 Prepare handoff evidence and stop for human approval.

## Dependency Order

Tests and acceptance criteria come before implementation. Verification comes after implementation. Merge comes only after
human approval.
