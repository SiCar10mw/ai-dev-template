# Secrets Policy

No secret belongs in this repository ever.

Secret retrieval uses the same two-tier split as the rest of the template:

- **MANDATORY principle**: secrets come from a central secrets manager at runtime and never from tracked files or real
  values in plain `.env` files.
- **RECOMMENDED default tool**: Azure Key Vault for Azure/Microsoft shops.

See `docs/identity.md` for the related centralized identity requirement.

## Step 0 - Required Setup Wizard

Run the setup wizard before operationalization:

```bash
make setup-identity
```

The wizard records the selected central identity provider and secrets manager in secret-free local files:

- `config/identity.json`
- `config/secrets.json`

It prints provider-specific next steps, but it does not create vaults, upload secrets, grant permissions, or call cloud
CLIs. `scripts/operationalize.sh` refuses to proceed until those profile files exist.

## Three-Layer Secret Gate

| Layer | Default Tool |
|---|---|
| Pre-commit | Gitleaks in `.pre-commit-config.yaml` |
| CI | Blocking `gitleaks secret scan` job |
| Full history | Blocking `gitleaks full-history scan` job with `fetch-depth: 0` |

The lightweight `scripts/check_no_secrets.py` scan also runs in `make check` as a local fallback.

## Source Of Secrets

- Use a central secrets manager, managed identity, OIDC, OAuth, or JWT flow.
- `.env.example` shows placeholder shape only; it never contains real values.
- Runtime code resolves logical names through `ai_dev_template.secrets.SecretProvider`.
- `config/secrets.example.json` documents provider selection. Its default order is EnvProvider then KeyringProvider so CI
  remains offline and deterministic after the setup wizard records the selected manager.
- Use OS keyring for local development only.
- Do not store secrets in tracked `.env`, JSON, YAML, TOML, markdown, generated artifacts, logs, or screenshots.

## Recommended Tools

Use Azure Key Vault as the recommended default for Azure/Microsoft environments. Equivalent central managers are
acceptable when they preserve runtime retrieval, least privilege, auditability, and rotation:

- HashiCorp Vault
- AWS Secrets Manager
- GCP Secret Manager
- 1Password or Doppler
- OS keyring for local development only

The default checked-in configuration keeps Azure Key Vault disabled. Projects may enable a Key Vault adapter in their
untracked project config, but CI must not make real cloud calls unless a human deliberately configures that profile.

## Credential Shape

Prefer short-lived scoped credentials:

- OIDC over static keys
- OAuth/JWT over long-lived API tokens
- managed identity or workload identity over client secrets
- least privilege scopes

## Runtime Handling

- Never print secrets to logs or stdout.
- Never place secrets in LLM context.
- Sanitize runtime data before crossing tool, model, file, or command boundaries.
- Redact credentials in error messages and traces.
- Fetch real values at runtime from the configured provider. Do not hardcode values or bypass the provider interface
  with direct package-level secret reads.

## Rotation And Revocation

Every production secret needs:

- owner
- purpose
- scope
- rotation cadence
- revocation procedure
- incident contact

Compromised secrets are revoked before root-cause analysis continues.
