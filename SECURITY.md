# Security Policy

## Supported Versions

The active `main` branch is supported for security fixes unless the project defines release branches.

## Reporting

Report suspected vulnerabilities through the repository's private vulnerability reporting channel, security contact, or
enterprise intake process. Do not open a public issue containing exploit details, credentials, private endpoints, or
sensitive system information.

## Baseline Security Rules

- External systems are read-only by default.
- Assume breach during design, implementation, and review.
- MCP tools that write, publish, share, delete, deploy, approve, merge, or change permissions require explicit human
  approval.
- Secrets must not be committed.
- Gitleaks runs in pre-commit and CI.
- Gitleaks also runs as a full-history scan in CI.
- mypy runs in pre-commit and CI so type hints are checked.
- Generated evidence artifacts are drift-checked before merge.
- Threat modeling and abuse cases start at spec time.
- Security-sensitive changes require tests, docs impact, and independent review.
- Deterministic gates decide release and merge readiness.

## Local Checks

```bash
make check
```

The gate includes conformance, documentation impact, docs-site scaffold checks, secret-pattern scanning, lint, tests,
SAST, and dependency audit.
