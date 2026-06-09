# Feature Specification: Centralized Identity And Secrets

**Status**: Draft

**Created**: 2026-06-09

**Input**: Addendum for centralized identity and secrets management in this repository.

## User Scenarios and Testing

### User Story 1 - Mandatory Identity And Secrets Standards (P1)

As a project maintainer, I can point contributors to vendor-neutral mandatory principles for centralized identity and
central secrets management, with Microsoft Entra ID and Azure Key Vault documented as recommended defaults.

**Why this priority**: The repository needs clear governance guidance without provisioning any cloud resource or making
enterprise services required for personal-scale checks.

**Independent Test**: Run template conformance and unit tests that validate identity/secrets docs, example config, and
provider-based secret access offline.

**Acceptance Scenarios**:

1. Given the repository standards, when conformance runs, then centralized identity and central secrets manager
   principles are present with recommended defaults and vendor-neutral alternatives.
2. Given `.env.example`, when conformance runs, then only placeholder shapes are accepted.
3. Given package code, when conformance runs, then direct secret-like environment reads outside the provider interface
   are rejected.
4. Given no cloud configuration, when tests run, then EnvProvider and KeyringProvider resolve offline and CI makes no
   Key Vault call.

### User Story 2 - Required Setup Wizard (P1)

As a project maintainer, I am walked through identity and secrets choices during onboarding before operationalization can
run, so the documented standard becomes an explicit repo-local setup decision instead of optional reading.

**Why this priority**: Identity and secret-manager choices affect every later external write. The template must force an
auditable choice before GitHub operationalization, while still making no cloud calls or provisioning resources.

**Independent Test**: Run the setup wizard in `--non-interactive --dry-run` mode and assert it writes
`config/identity.json` and `config/secrets.json`, rejects missing/invalid choices, and does not invoke provider CLIs.
Run operationalize dry-run without those profiles and assert it refuses before invoking `gh`.

**Acceptance Scenarios**:

1. Given no profile files, when `scripts/operationalize.sh --dry-run --repo OWNER/REPO` runs, then it fails with
   "run `make setup-identity` first" and does not invoke `gh`.
2. Given non-interactive setup flags, when `scripts/setup_identity.sh --non-interactive --dry-run --idp entra --secrets
   azure-key-vault` runs, then it writes the selected profile files and prints Entra/Key Vault next steps without cloud
   calls.
3. Given a missing or invalid required choice, when setup runs in non-interactive mode, then it exits non-zero and writes
   no active profile files.
4. Given bootstrap onboarding, when a new project is created, then the identity/secrets setup wizard runs before the
   initial check gate.

## Requirements

### Functional Requirements

- **FR-001**: The system must document centralized identity as a mandatory vendor-neutral principle.
- **FR-002**: The system must document Microsoft Entra ID as the recommended default identity tool and name Okta,
  Google Cloud IAM / Workspace, and AWS IAM Identity Center as alternatives.
- **FR-003**: The system must document central secrets management as a mandatory vendor-neutral principle.
- **FR-004**: The system must document Azure Key Vault as the recommended default secrets manager and name HashiCorp
  Vault, AWS Secrets Manager, GCP Secret Manager, 1Password/Doppler, and OS keyring for local-only use as alternatives.
- **FR-005**: The system must provide a `SecretProvider.get(name) -> str | None` interface with EnvProvider,
  KeyringProvider, and KeyVaultProvider implementations.
- **FR-006**: The default provider selection must remain offline by using EnvProvider and KeyringProvider when no
  central manager is configured.
- **FR-007**: Template conformance must reject real values in `.env.example` and direct package secret reads that bypass
  the provider interface.
- **FR-008**: The system must provide `scripts/setup_identity.sh` and `make setup-identity` as a terminal wizard with
  required identity-provider and secrets-manager prompts.
- **FR-009**: The setup wizard must support `--non-interactive --idp <x> --secrets <y>` and `--dry-run`.
- **FR-010**: The setup wizard must write secret-free `config/identity.json` and `config/secrets.json` profiles derived
  from example config files.
- **FR-011**: The setup wizard must print provider-specific next steps and make no cloud calls or provisioning changes.
- **FR-012**: `scripts/operationalize.sh` must refuse to proceed until both setup profiles exist and must tell users to
  run `make setup-identity` first.
- **FR-013**: `bootstrap.sh` must run the setup wizard as part of onboarding before the initial check gate.

## Threat Model and Abuse Cases

### Assume Breach Baseline

- External systems are read-only by default.
- Least privilege applies to every identity, token, MCP server, workflow, and generated output.
- Secrets are never placed in repository files, logs, stdout, generated artifacts, or LLM context.

### Abuse Cases

1. An attacker commits a real token to `.env.example` disguised as a sample value.
2. A developer bypasses the provider interface and hardcodes or directly reads a long-lived credential.
3. A Key Vault adapter is selected in CI and unexpectedly attempts a cloud call.
4. A machine-user identity uses static credentials or broad privileges instead of managed, audited access.
5. A contributor skips setup and operationalizes a repository without an explicit identity/secrets decision.
6. A setup script invokes provider CLIs or provisions cloud resources before a human approves those actions.

### Attack Tree

- Goal: exfiltrate or misuse project credentials.
  - Commit a real value to tracked files.
  - Bypass provider resolution with direct environment reads.
  - Replace central identity with local/ad-hoc accounts.
  - Configure a cloud provider as mandatory for offline checks.
  - Bypass the setup wizard and run external-write operationalization.
  - Smuggle provisioning into an onboarding script.

### Required Mitigations

- Placeholder-only `.env.example` conformance check.
- Provider-interface conformance check for package secret access.
- Offline default provider chain.
- Key Vault adapter requires explicit configuration or injected test client.
- Documentation keeps mandatory principles separate from recommended vendor defaults.
- Required setup profiles gate operationalization.
- Setup wizard tests fake provider CLIs and assert no provider command is invoked.

### Key Entities

- **SecretProvider**: Pluggable interface used by code to resolve runtime secrets.
- **Central IdP**: Human and machine identity source of truth.
- **Central Secrets Manager**: Runtime source of truth for secrets outside local development.

## Success Criteria

- **SC-001**: Focused unit tests for EnvProvider, KeyringProvider, KeyVaultProvider, fallback behavior, and conformance
  tripwires pass offline.
- **SC-002**: `make check` passes locally.
- **SC-003**: Current behavior is documented without provisioning cloud resources.
- **SC-004**: Setup and operationalization tests pass offline, including non-interactive dry-run and refusal paths.

## Assumptions

- No cloud resources are provisioned by this change.
- Azure Key Vault is a recommended adapter example only unless a project explicitly configures it.
- `--dry-run` for setup means no external/cloud calls; it still records the local repo profile for CI and scripts.
