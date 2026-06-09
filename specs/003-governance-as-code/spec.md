# Feature Specification: Governance-as-Code — Security-as-Code per Artifact, Mapped to Baseline Standards

**Feature Branch**: `003-governance-as-code`

**Created**: 2026-06-09

**Status**: Draft — ready for planning

**Input**: Every artifact the AI generates must ship with machine-checkable **security-as-code**, and every
feature/story must **provably map to baseline standards** — SOC 2, ISO/IEC 27001, NIST (800-53 + CSF), and
**CSA Cloud Controls Matrix (CCM)** — enforced as a **per-feature gate**, not a document. Governance travels
*with* the artifact. CI runs on **Azure Pipelines**. This is the same OSCAL control-mapping discipline the
product applies to others, turned inward on our own SDLC.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — AI-generated IaC cannot merge without security-as-code (Priority: P1)

When the AI generates Infrastructure-as-Code (e.g. the Azure Bicep foundation), it **cannot be merged**
until a **Checkov** scan passes and the artifact carries a control mapping. The Bicep foundation
(`infra/azure/`) is the first governed exemplar.

**Why P1**: this is the principle made concrete on a real artifact — "if AI generates IaC, it has security
as code."

**Independent Test**: open a change adding/altering IaC with a known misconfiguration → the Checkov gate
fails the merge; fix it → the gate passes and a control mapping is recorded.

**Acceptance Scenarios**:
1. **Given** AI-generated IaC with a security misconfiguration, **When** CI runs, **Then** the Checkov gate
   fails and the merge is blocked.
2. **Given** compliant IaC, **When** CI runs, **Then** Checkov passes and the artifact's findings map to
   SOC 2 / ISO 27001 / NIST / CCM controls.

### User Story 2 — Every feature emits a control-coverage manifest (Priority: P1)

Each feature produces a **generated control-coverage manifest** mapping the gates that ran → the baseline
controls they satisfy (SOC 2, ISO 27001, NIST, CCM). Merge is **blocked** if the manifest is missing or
invalid. "This story meets baseline" becomes *provable*: the gates that ran are the evidence.

**Why P1**: turns "meets baseline" from a claim into machine-verifiable evidence per feature.

**Independent Test**: merge a feature with no manifest → blocked; with a valid manifest → allowed, and the
manifest lists each gate and its mapped controls.

**Acceptance Scenarios**:
1. **Given** a feature with passing gates but no control-coverage manifest, **When** the conformance gate
   runs, **Then** the merge is blocked.
2. **Given** a feature with a valid manifest, **When** it is inspected, **Then** each security gate is mapped
   to specific SOC 2 / ISO 27001 / NIST / CCM control IDs sourced from authoritative catalogs.

### User Story 3 — A security gate per artifact TYPE (Priority: P2)

The AI cannot produce an artifact type without its corresponding security-as-code gate: code → SAST +
AI-SAST closed loop; **IaC → Checkov**; container → image scan; dependencies → SCA; any → secret scan.

**Independent Test**: introduce each artifact type with a planted issue → the type-appropriate gate catches it.

### User Story 4 — CI runs on Azure Pipelines, gates unchanged (Priority: P2)

CI is ported from GitHub Actions to **Azure Pipelines** (`azure-pipelines.yml`); the gates are identical and
also runnable locally via `make check`. Secrets come from Key Vault via the managed identity.

**Independent Test**: the same gates pass on Azure Pipelines and locally; a gate failure blocks the pipeline.

### Edge Cases
- A new artifact type with no defined gate → conformance fails closed (no ungoverned type ships).
- Control catalogs unavailable → mapping step fails (no silent "mapped to nothing").
- A scanner finds nothing → still emits a (passing) mapped manifest entry (absence of findings is recorded, not skipped).
- A finding the team accepts (risk-accepted) → recorded explicitly with justification, never silently suppressed.

## Requirements *(mandatory)*

### Functional Requirements
- **FR-001**: Every AI-generated **IaC** artifact MUST pass a **Checkov** scan (a deterministic gate) before merge.
- **FR-002**: Each security gate's results MUST map to baseline controls across **SOC 2, ISO/IEC 27001,
  NIST (800-53 + CSF), and CSA CCM**.
- **FR-003**: Each feature MUST emit a **generated control-coverage manifest** mapping the gates that ran →
  the control IDs they satisfy; the manifest is a committed/generated evidence artifact.
- **FR-004**: A **per-feature conformance gate** MUST block merge unless (a) the type-appropriate security
  gates pass AND (b) a valid control-coverage manifest is present.
- **FR-005**: Security gates MUST be defined per artifact **type** (code / IaC / container / dependency /
  secret); the AI MUST NOT be able to produce a type without its gate.
- **FR-006**: Control mappings MUST be sourced from **authoritative catalogs** (not model memory) — reusing
  the OSCAL/CCM/ISO control-mapping discipline; counts and IDs are read from catalogs programmatically.
- **FR-007**: CI MUST run on **Azure Pipelines** (`azure-pipelines.yml`); gates MUST be CI-runner-agnostic
  (also runnable via `make check` locally); pipeline secrets come from Key Vault via managed identity.
- **FR-008**: The **deterministic-decider invariant** MUST hold — scanners FIND, a deterministic rule DECIDES
  (consistent with the AI-SAST closed loop).
- **FR-009**: The Azure Bicep foundation (`infra/azure/`) MUST be the first governed IaC artifact — it lands
  *with* its Checkov gate and mapped manifest (the exemplar), never before.
- **FR-010**: Risk-accepted findings MUST be recorded explicitly with justification + owner; suppression is
  never silent.

### Key Entities
- **Security gate** — a per-artifact-type scanner whose pass/fail is decided deterministically.
- **Control-coverage manifest** — generated per feature; maps gates → SOC 2 / ISO 27001 / NIST / CCM controls.
- **Control catalogs** — the authoritative source of control IDs (OSCAL/CCM/ISO), read programmatically.
- **Conformance gate** — the per-feature merge gate over gates + manifest.

## Success Criteria *(mandatory)*
- **SC-001**: 100% of AI-generated IaC artifacts pass Checkov before merge (no un-scanned IaC reaches main).
- **SC-002**: Every merged feature carries a valid control-coverage manifest mapped to SOC 2 / ISO 27001 / NIST / CCM.
- **SC-003**: A feature with a failing security gate OR a missing/invalid manifest is blocked (verifiably red).
- **SC-004**: Control mappings are catalog-sourced and verifiable (no hardcoded control IDs).
- **SC-005**: The full gate set passes identically on Azure Pipelines and locally via `make check`.
- **SC-006**: The Bicep foundation passes its Checkov gate with a mapped manifest — the exemplar proven end-to-end.

## Assumptions
- Standards in scope: **SOC 2, ISO/IEC 27001, NIST 800-53 + CSF, CSA CCM** (alongside the existing NIST AI
  RMF / ISO 42001 for the AI-usage-governance layer).
- **Checkov** is the IaC scanner (multi-IaC: Bicep/ARM/Terraform/K8s), chosen for breadth + control crosswalks.
- The control-coverage manifest extends the existing `generated/governance/governance-evidence.json` into an
  OSCAL-component-shaped evidence node (the saas-assurance recursion).
- The `governance-control-mapper` agent (already in the roster) owns the mapping; the existing code/secret/SCA
  gates are reused; the net-new gate is IaC (Checkov) + the per-feature manifest + the conformance gate.
- Azure Pipelines is the CI runner; `make check` remains the local==CI rail.

## Out of Scope
- Runtime cloud-posture (Azure Policy deny-at-deploy, Defender for Cloud) — a complementary later layer; this
  feature is the **build-time / shift-left** governance.
- The multi-container / ACA decoupling of the product (tracked in saas-assurance spec 008).
