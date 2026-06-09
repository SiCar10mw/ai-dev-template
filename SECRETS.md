# Secrets Policy

No secret belongs in this repository ever.

## Three-Layer Secret Gate

| Layer | Default Tool |
|---|---|
| Pre-commit | Gitleaks in `.pre-commit-config.yaml` |
| CI | Blocking `gitleaks secret scan` job |
| Full history | Blocking `gitleaks full-history scan` job with `fetch-depth: 0` |

The lightweight `scripts/check_no_secrets.py` scan also runs in `make check` as a local fallback.

## Source Of Secrets

- Use a secret manager, OS keyring, managed identity, OIDC, OAuth, or JWT flow.
- `.env.example` shows variable names only; it never contains real values.
- Do not store secrets in tracked `.env`, JSON, YAML, TOML, markdown, generated artifacts, logs, or screenshots.

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

## Rotation And Revocation

Every production secret needs:

- owner
- purpose
- scope
- rotation cadence
- revocation procedure
- incident contact

Compromised secrets are revoked before root-cause analysis continues.
