# Centralized Identity Management

## Mandatory Principle

Human and machine identity must come from a central identity provider. Do not create local, ad-hoc, shared, or
repository-specific accounts to bypass SSO, conditional access, least privilege, or audit logging.

This principle is mandatory and vendor-neutral:

- humans authenticate through SSO / IdP-backed accounts
- machine-users authenticate as managed identities, service principals, GitHub Apps, or workload identities
- permissions are scoped to the exact repository, workflow, environment, and external system
- access is conditional-access gated where the enterprise supports it
- tokens are short-lived and issued at runtime
- activity is attributable in audit logs
- high-impact writes still require human approval

## Step 0 - Required Setup Wizard

Run the terminal wizard before operationalizing the repository:

```bash
make setup-identity
```

The wizard requires two choices: one central identity provider and one secrets manager. It writes the secret-free local
profiles `config/identity.json` and `config/secrets.json`, then prints provider-specific next steps. It does not create
cloud resources, call provider CLIs, provision identities, upload secrets, or grant permissions.

For CI or scripted onboarding, use non-interactive mode:

```bash
bash scripts/setup_identity.sh --non-interactive --dry-run --idp entra --secrets azure-key-vault
```

`--dry-run` means no external/cloud commands are invoked. The local profile files are still written so later scripts can
verify that the required choice was made.

## Recommended Default

For Azure and Microsoft 365 organizations, use Microsoft Entra ID as the default central identity provider. The
machine-user that authors pull requests should be backed by a managed identity or service principal with:

- repository-scoped permissions
- conditional access or workload identity controls
- full sign-in and API audit logs
- short-lived runtime tokens
- no long-lived static credential in repository files, CI variables, logs, or generated artifacts

## Vendor-Neutral Alternatives

Projects may substitute an equivalent central IdP while preserving the same principle:

- Okta
- Google Cloud IAM / Workspace
- AWS IAM Identity Center
- GitHub App or workload identity for repository automation

The tool can flex. Central identity, managed machine identity, least privilege, short-lived credentials, and auditability
do not flex.

## Machine-User Pull Request Flow

See `docs/machine-user-pr-flow.md` for the pull request operating model. The machine-user may author branches and pull
requests, but it may not self-approve, self-merge, deploy, publish, delete production data, or rotate credentials.

## Secrets Boundary

Identity proves who is acting. Secret management controls how runtime credentials are retrieved. See `SECRETS.md` for
the central secrets manager requirement and `config/secrets.example.json` for the offline-first provider configuration
shape.

## No Provisioning

This repository documents the standard and provides offline checks. It does not provision Microsoft Entra ID, Azure Key
Vault, or any alternative cloud resource. Follow the next steps printed by `make setup-identity` in the chosen provider
only after a human has approved the relevant identity, secret, and permission changes.
