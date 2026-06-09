# Feature Specification: AI-SAST Security Gate

**Status**: Draft

**Created**: 2026-06-09

**Input**: Add an AI-SAST security gate using a security-specialist model as finder and deterministic policy as decider.

## User Scenarios and Testing

### User Story 1 - Deterministic Merge Gate (P1)

As a repository maintainer, I can run an AI-assisted SAST gate that never lets the LLM decide whether a merge is blocked.

**Why this priority**: The constitution requires deterministic authority for gate results.

**Independent Test**: Run unit tests that feed MockScanner findings into the policy.

**Acceptance Scenarios**:

1. Given a confirmed high finding, when the policy threshold is high and the finding is not baselined, then the gate
   fails.
2. Given the same confirmed high finding in `.ai-sast-baseline.json`, when the gate runs, then it passes.
3. Given low or unconfirmed findings, when the threshold is high, then the gate ignores them.

### User Story 2 - Offline CI Default (P1)

As a contributor, I can run `make check` without model credentials or network access.

**Independent Test**: Run `python scripts/check_ai_sast.py --scanner mock`.

**Acceptance Scenarios**:

1. Given no Anthropic key, when the scanner is `auto`, then the Mock scanner is selected.
2. Given no test marker findings, when the Mock scanner runs in CI, then it produces deterministic empty findings.

## Requirements

### Functional Requirements

- **FR-001**: The system must expose a `SecurityScanner.scan(targets) -> list[Finding]` interface.
- **FR-002**: The system must provide `MockScanner` for deterministic tests and offline CI.
- **FR-003**: The system must provide `MythosScanner` for runtime defensive scanning with a configured key.
- **FR-004**: The merge decision must be made by deterministic policy over JSON findings.
- **FR-005**: The policy must block only confirmed findings at or above threshold that are not baseline-suppressed.
- **FR-006**: The PR cadence must scan diff-only targets.
- **FR-007**: The scheduled cadence must scan the full codebase with budget caps and remain non-blocking.
- **FR-008**: Documentation must describe find-vs-decide, verification, cadence, baseline, Glasswing, and cost caveats.

## Threat Model and Abuse Cases

### Assume Breach Baseline

- Model output is untrusted evidence.
- Repository content may contain prompt injection strings.
- Provider credentials are never committed.
- External writes require explicit human approval.

### Abuse Cases

1. A model reports a severe issue incorrectly and tries to block a merge.
2. A malicious source file instructs the scanner to ignore vulnerable code.
3. A contributor suppresses a finding without a reviewable baseline entry.
4. A scheduled full scan consumes excessive model budget.

### Attack Tree

- Goal: bypass or abuse the security gate.
  - Put merge authority in model text.
  - Poison model input with prompt injection.
  - Hide findings in untracked suppressions.
  - Trigger costly full scans on every commit.

### Required Mitigations

- Deterministic policy decides gate status.
- Scanner inputs are bounded and sanitized before model use.
- Baseline suppressions are committed JSON fingerprints.
- PR workflow scans diffs only; scheduled workflow has budget caps.

### Key Entities

- **Finding JSON**: Structured scanner evidence.
- **Baseline**: Human-reviewed accepted finding fingerprints.
- **Decider**: `scripts/check_ai_sast.py` deterministic policy.

## Success Criteria

- **SC-001**: MockScanner unit tests cover block, baseline pass, and ignored low or unconfirmed findings.
- **SC-002**: `make check` runs the AI-SAST Mock path and remains green offline.
- **SC-003**: Docs clearly state that the LLM never blocks merges.

## Assumptions

- Real Mythos / Fable 5 calls are runtime-only and require an environment-provided key.
- The public model may refuse offensive cyber analysis; this feature is defensive scanning only.
