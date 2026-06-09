# Machine-User Pull Request Flow

The machine-user pull request flow is mandatory for AI-authored changes.

## Recommended Identity Pattern

The machine-user must be backed by a central identity provider, not a local or ad-hoc account. When the enterprise uses
Microsoft 365, the recommended default is a scoped Microsoft Entra ID managed identity or service principal. Equivalent
central identity providers such as Okta, Google Cloud IAM / Workspace, AWS IAM Identity Center, GitHub Apps, or workload
identity may be substituted when they preserve the same controls.

The machine identity must be gated, audited, and least-privilege:

- no hardcoded credentials
- credentials or federated identity held in an approved secret manager
- app permissions scoped to the exact repository and publication tasks
- sign-in and Graph/API activity audited
- short-lived tokens
- conditional access where supported
- external writes require human approval

See `docs/identity.md` for the centralized identity principle and `SECRETS.md` for runtime credential retrieval.

## Roles

| Role | Responsibility |
|---|---|
| Human maintainer | Curates backlog, sets priorities, reviews results, approves direction |
| Machine user / bot | Authors branches and pull requests, runs gates, responds to review |
| Separate admin or maintainer identity | Submits final approval and merge action |

## Rules

- The bot may author a pull request.
- The bot may update the pull request after review.
- The bot may not self-approve.
- The bot may not self-merge.
- A human approves via chat or review.
- A separate authorized identity submits the platform approval or merge.
- Branch protection must require CI and review before merge.

## Required PR Evidence

- Scope summary.
- Tests added or updated.
- Negative or regression cases.
- `make check` result.
- gitleaks, mypy, and generated-artifact drift gate results.
- Docs updated or explicit reason no docs changed.
- Independent review result for substantial changes.
