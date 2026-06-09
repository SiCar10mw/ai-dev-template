# M365 Integration

This is an optional corporate profile. The default personal/core profile must pass `make check` without M365, Entra,
Purview, SharePoint, Teams, or any enterprise tenant.

This template respects the documentation boundary. Repository files define source, generated artifacts are produced by
scripts, and corporate-governed outputs can be published through Microsoft 365 controls when the enterprise uses M365.

Validate only the corporate scaffold with:

```bash
make corporate-profile-check
```

## Identity

The recommended machine-user identity is a Microsoft Entra ID app registration with a service principal in the tenant.

Rules:

- use least-privilege app permissions
- prefer certificates, federated identity, or managed identity over client secrets
- store credentials in an approved secret manager
- audit sign-ins and privileged operations
- never hardcode tenant IDs, client IDs, secrets, certificates, or tokens in source

## Data Governance

Microsoft Purview sensitivity labels and DLP policies are tenant-level controls. They complement repository sanitizers;
they do not replace code-level validation.

Use Purview for:

- sensitivity labels on generated decks and DOCX
- DLP policies for SharePoint, Teams, Exchange, endpoints, and cloud apps
- retention and records management
- corporate AI registry and policy evidence where applicable

## Output Flow

The output flow is:

1. regenerate artifacts with `python scripts/gen_all_artifacts.py`
2. validate drift with `python scripts/check_generated_artifacts.py`
3. create an operational dry-run publish plan with `python scripts/publish_m365_stub.py --dry-run`
4. human approves publication
5. approved automation republishes to SharePoint/Teams with labels and retention

The included publisher is a stub. It does not write to Microsoft 365. Production projects should replace it with an
approved Graph API, SharePoint, or Teams publisher that uses the Entra machine-user identity and tenant DLP controls.
Real publication must stay behind the corporate profile and explicit human approval.
