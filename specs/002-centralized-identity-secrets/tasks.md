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

## Phase 4 - Required Setup Wizard Addendum

- [x] T013 Add `config/identity.example.json` and extend `config/secrets.example.json` with selectable manager metadata.
- [x] T014 Add failing setup and operationalize tests for required choices, dry-run profile writes, no provider CLI
  calls, and refusal before setup.
- [x] T015 Implement `scripts/setup_identity.sh` with interactive required prompts and non-interactive flags.
- [x] T016 Add `make setup-identity`.
- [x] T017 Run setup from `bootstrap.sh` during onboarding.
- [x] T018 Gate `scripts/operationalize.sh` on `config/identity.json` and `config/secrets.json`.
- [x] T019 Update identity, operationalize, and first-run docs to make setup step 0.
- [x] T020 Run focused tests and `make check`.

## Dependency Order

Tests and acceptance criteria come before implementation. Verification comes after implementation. Merge comes only after
human approval.
