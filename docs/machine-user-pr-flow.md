# Machine-User Pull Request Flow

The machine-user pull request flow is mandatory for AI-authored changes.

## Recommended Identity Pattern

When the enterprise uses Microsoft 365, the machine-user should be backed by a scoped Microsoft Entra ID service
principal. The service principal must be gated, audited, and least-privilege:

- no hardcoded credentials
- credentials or federated identity held in an approved secret manager
- app permissions scoped to the exact repository and publication tasks
- sign-in and Graph/API activity audited
- external writes require human approval

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
