# AI Governance Mapping

This bridge document maps mandatory principles and baseline tools to governance frameworks and enforcement locations.
It is a starting control map, not a legal opinion or certification statement.

| Mandatory Principle / Evidence | Recommended Baseline Tool | NIST AI RMF Anchor | ISO/IEC 42001 Anchor | EU AI Act Tiering Anchor | Enforced Where |
|---|---|---|---|---|---|
| Constitution-first governance | `CONSTITUTION.md`, `GOVERNANCE.md` | Govern | AIMS policy and governance | All tiers: governance baseline | Repo CI |
| Least privilege / read-only by default | MCP configs, machine-user PR flow | Govern, Manage | access control and operational controls | high-risk deployer/operator control | Repo CI; corporate profile: Entra |
| Deterministic authority | verdict code, golden tests | Measure, Manage | evaluation and operational control | no autonomous final decision | Repo CI |
| Evidence integrity | generated governance evidence | Govern, Measure | documented information and evidence | technical documentation and records | Repo CI; corporate profile: SharePoint |
| Trust-boundary sanitization | `ai_dev_template/sanitize.py` | Map, Manage | risk treatment controls | data governance and robustness support | Repo CI |
| Source-of-truth authority | committed config/docs/tests | Govern | documented information control | records and instructions for use | Repo CI |
| Copilot Memory is advisory only | `docs/copilot-memory.md` | Govern | governance of AI tool use | user oversight support | Repo CI |
| Model/provider routing is approved and secret-free | `config/approved-models.example.json` | Govern, Map | AI system inventory and use policy | risk classification support | Repo CI; corporate profile: Entra |
| Governed MCP access | `.mcp.json`, `.vscode/mcp.json` | Map, Manage | external tool control | deployer operational control | Repo CI; corporate profile: Entra |
| Copilot repository instructions | `.github/copilot-instructions.md` | Govern | competence and operational guidance | user instructions support | Repo CI |
| ADRs and threat model | `docs/adr/`, `docs/threat-model.md` | Map | risk assessment | high-risk assessment support | Repo CI |
| AIBOM as AI inventory | `generated/aibom/aibom.json` | Govern, Map | AI inventory | AI system inventory and classification | Repo CI; corporate profile: SharePoint |
| Human approval before merge/deploy/publish | PR template, backlog worker | Govern, Manage | roles, responsibility, approvals | human oversight | Repo CI, human process |
| Machine-user identity | scoped machine user; optional Entra service principal | Govern, Manage | identity and access management | accountability and traceability | Repo CI; corporate profile: Entra |
| Audit logging | agent handoff notes, generated evidence | Govern, Measure | monitoring and records | logging and traceability | Repo CI; corporate profile: Entra/Purview |
| Sensitivity labels and DLP | repo sanitizer; optional Microsoft Purview | Map, Manage | data governance controls | data governance obligations | Repo CI; corporate profile: Purview |
| Secret hygiene | Gitleaks, pre-commit, CI | Govern, Manage | information security controls | cybersecurity support | Repo CI |
| Static type enforcement | mypy | Measure | verification and validation | quality and robustness support | Repo CI |
| Local equals CI | `make check`, workflow parity | Measure, Manage | operational control | quality management support | Repo CI |
| Generated artifacts never hand-edited | `scripts/gen_*`, drift tripwire | Govern, Measure | documented information integrity | technical documentation accuracy | Repo CI |
| Documentation impact gate | `scripts/check_docs_impact.py` | Govern | documented information control | instructions and transparency | Repo CI |
| Three-tier docs boundary | docs-site, `docs/`, optional M365 | Govern, Manage | communications and documented information | transparency and user information | Repo CI; corporate profile: SharePoint |
| Personal-scale default | `scripts/check_profile_boundary.py` | Govern, Manage | operational control | proportional governance | Repo CI |

## Seeded Obvious Rows

- AIBOM = AI inventory.
- Threat model = risk assessment.
- Human approval = human oversight.
- Deterministic verdict = no autonomous decisions.
- Audit log = traceability.
