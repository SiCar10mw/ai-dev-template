# Governance Model

This template governs two domains. They are related, but they are never conflated.

## Personal-Scale Default

The default profile is personal/core. It requires no M365 tenant, Microsoft Entra ID app registration, Microsoft Purview
policy, SharePoint site, Teams channel, or corporate registry. `make check` must stay green for a solo developer with
only the repository, Python tooling, Node for docs-site builds, and the documented open-source gates.

Corporate governance integrations are recommended add-ons. Enable them deliberately with a project profile such as
`AI_DEV_PROFILE=corporate`, never by making enterprise services a hidden dependency of the core gate.

## Domain 1: Governing AI-Building

AI-building governance covers the software development lifecycle used to build, maintain, and review this project.

The SDLC is governed by the 12 mandatory principles in `CONSTITUTION.md`:

1. least privilege / read-only by default
2. deterministic authority
3. evidence integrity
4. trust-boundary sanitization
5. source-of-truth authority
6. quality gates
7. honest documentation
8. documentation impact gate
9. human-gated high-impact changes
10. spec-first and test-driven delivery
11. safe editing habits
12. generated-artifact drift control

These principles are enforced through repo files, local gates, pre-commit, CI, generated artifacts, and human review.

## Domain 2: Governing AI-Usage

AI-usage governance covers acceptable use, model approval, AI registry entries, human oversight, data handling, and
publication controls.

This repository is the reference implementation for AI-usage governance. In the core profile it demonstrates repo-local
controls. In the optional corporate profile it can also demonstrate:

- approved model routing
- agent binding to no-exfil and sensitivity-aware behavior
- human approval before high-impact actions
- AIBOM generation as an AI inventory pattern
- Microsoft Purview labels and DLP as tenant-level data controls
- Microsoft Entra ID service principals as scoped machine-user identities
- SharePoint/Teams publication as a governed output channel

## Enforcement Boundary

| Control Surface | Enforces |
|---|---|
| Repo CI and pre-commit | SDLC gates, generated artifact drift, type checks, secret scanning |
| Corporate profile: Microsoft Entra ID | machine-user identity, app registration, service principal scope, sign-in audit |
| Corporate profile: Microsoft Purview | sensitivity labels, DLP, retention, tenant-level data governance |
| Corporate profile: SharePoint/Teams | governed publication, retention, access control, RACI |
| Human review | approvals, exception decisions, adjudication of tool/model disagreements |
