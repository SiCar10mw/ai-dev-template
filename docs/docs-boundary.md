# Docs Boundary

This repository deliberately separates public, contributor, and corporate-governed documentation.

## Boundary

| Location | Audience | Purpose |
|---|---|---|
| `docs-site/` | Public or curated project audience | Product, user, API, wiki, or operational documentation selected for external readers |
| `docs/` | Contributors, maintainers, agents | Methodology, internal process, setup, review, safety, and governance |
| M365 SharePoint/Teams | Corporate governed audience | Policy, AI registry, RACI, approvals, retention-controlled committee evidence |

## Mandatory Decision

The three-tier boundary is mandatory. The site generator and Microsoft 365 scaffolding are recommended defaults. This template ships `docs-site/` as a Docusaurus scaffold because many projects need a public wiki, and it ships `docs/m365-integration.md` because many enterprises govern policy, registry, RACI, and records in M365.

## Rules

- Keep contributor process docs close to code in `docs/`.
- Keep public-facing docs in `docs-site/`.
- Keep policy, AI registry, RACI, approval records, and retention-controlled evidence in corporate-governed M365 locations.
- Do not publish internal-only process notes to the public site by accident.
- Do not duplicate facts manually across both places unless necessary.
- If code behavior changes, update the authoritative doc in the same pull request.
- If there is no docs impact, record that decision in `docs/docs-impact.md`.
