# Threat Model

This baseline threat model is generic. Assume breach. Project teams should update it during bootstrap and whenever architecture,
external tools, data boundaries, or deployment targets change.

## Assets

| Asset | Why It Matters |
|---|---|
| Source code | Defines behavior and security controls |
| Tests and golden fixtures | Define deterministic truth |
| Docs and docs-site | Communicate current behavior and operating procedures |
| MCP configs | Grant agents access to external tools and data |
| Generated documents | May contain evidence, decisions, or stakeholder-facing claims |
| Secrets and credentials | Enable external access and must never be committed |

## Trust Boundaries

- Human instructions enter the repository workflow.
- AI agents read and edit local files.
- MCP servers expose external tools and data.
- CI executes repository scripts.
- Public docs-site exposes curated content to its audience.

## Baseline Threats

| Threat | Control |
|---|---|
| Prompt injection through external content | Trust-boundary sanitization and deterministic validation |
| LLM makes a false verdict or release claim | Deterministic authority principle |
| MCP over-permissioned external writes | Empty default MCP configs, least privilege, explicit human approval |
| OWASP LLM risk mapping drifts from enforced gates | `scripts/check_owasp_llm.py` and `docs/owasp-llm-top10.md` |
| Docs drift from shipped behavior | Documentation-impact gate and independent review |
| Secrets committed to source | Secret-pattern scan, SECURITY.md, review checklist |
| Local tests pass but CI fails | `make check` equals CI and bare `pytest` path config |
| Bot self-approves or self-merges | Machine-user PR flow and human gate |

## Review Cadence

Review this file when adding a new external integration, MCP server, deployment target, authentication flow, document
generator, or privileged workflow.
