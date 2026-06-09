# Project Standards

This template has two tiers. The distinction is mandatory.

1. **MANDATORY principles** are non-negotiable. Every project built from this template must implement them, regardless of language, runtime, framework, cloud, editor, or AI tool. A project that omits one is non-conformant.
2. **RECOMMENDED default tools** are the preferred stack shipped by this template. Use them by default. If the project stack requires a different tool, substitute the closest equivalent while preserving the mandatory principle.

Example: Python projects use `ruff` and `pytest`; a TypeScript project might use `eslint` and `vitest`. The tools can change. The principles cannot.

| MANDATORY Principle | RECOMMENDED Default Tool / File / Convention |
|---|---|
| Constitution-first governance: numbered project principles take precedence and conflicts are flagged to a human. | `CONSTITUTION.md`, `GOVERNANCE.md`, `CLAUDE.md`, `AGENTS.md` |
| Two-domain governance: AI-building SDLC governance and AI-usage governance are related but never conflated. | `GOVERNANCE.md`, `docs/ai-governance-mapping.md` |
| Least privilege and read-only-by-default for external systems; writes require explicit human approval. | `CONSTITUTION.md`, `agents/backlog-worker.md`, PR template language |
| Deterministic authority: anything that must be true is decided by code, rules, tests, schemas, or CI, not by an LLM. | `ai_dev_template/verdicts.py`, verdict-golden tests, CI gates |
| Evidence integrity: generated artifacts are timestamped when appropriate, schema-conformant when a schema exists, and kept in-repo. | `tests/fixtures/goldens/`, `docs/methodology.md`, `scripts/check_template_conformance.py` |
| Trust-boundary sanitization: external input is sanitized before LLM consumption or command/file boundaries. | `ai_dev_template/sanitize.py`, unit tests |
| Source-of-truth authority: repository files, configs, catalogs, schemas, and tests beat memory or model recall. | `CONSTITUTION.md`, `AGENTS.md`, `docs/methodology.md` |
| Copilot Memory, when available, is supplemental context only; committed files remain authoritative. | `docs/copilot-memory.md`, GitHub Copilot Memory settings |
| Model/provider routing is explicit, secret-free, and subordinate to deterministic gates. | `config/model-routing.example.json`, `config/approved-models.example.json`, `docs/model-routing.md` |
| Centralized identity management: human and machine identities come from a central identity provider; machine identities are managed, scoped, conditional-access gated, audited, and short-lived. | `docs/identity.md`; recommended default Microsoft Entra ID; alternatives include Okta, Google Cloud IAM / Workspace, and AWS IAM Identity Center |
| Governed MCP tool access: external tools are registered, least-privilege, and human-approved before writes. | `.mcp.json`, `.vscode/mcp.json`, `docs/mcp-and-tooling.md` |
| Copilot-native repository instructions are committed and aligned with the constitution. | `.github/copilot-instructions.md`, `.github/instructions/*.instructions.md`, `AGENTS.md` |
| Durable architecture/security decisions are recorded in source control. | `docs/adr/`, `docs/threat-model.md`, `docs/release.md` |
| Secrets are never committed and never enter VCS. | Gitleaks, `.pre-commit-config.yaml`, `.gitleaks.toml`, blocking `secrets` CI job |
| Central secrets manager: secrets come from a central secrets manager at runtime; tracked files and plain `.env` files contain only placeholder shape, never real values. | `SECRETS.md`, `config/secrets.example.json`, `ai_dev_template/secrets.py`; recommended default Azure Key Vault; alternatives include HashiCorp Vault, AWS Secrets Manager, GCP Secret Manager, 1Password/Doppler, and OS keyring for local only |
| Static type hints are checked, not merely requested by convention. | mypy, `.pre-commit-config.yaml`, blocking `type-check` CI job |
| Quality gates before commit or merge: typed, linted, green, offline tests. | `pyproject.toml`, `ruff`, `mypy`, `pytest`, `bandit`, `pip-audit`, `Makefile`, `.github/workflows/ci.yml` |
| Local equals CI: the same commands run locally and in CI; bare test runner behavior matches `python -m pytest`. | `scripts/ci_check.sh`, `Makefile`, `pyproject.toml` with `pythonpath = ["."]` and `testpaths = ["tests"]` |
| Deterministic-output tripwire: important deterministic outputs have committed golden fixtures. | `tests/fixtures/goldens/verdict_pass.json`, `tests/unit/test_verdict_golden.py` |
| Generated artifacts are generated, never hand-edited, and stale generated artifacts fail the build. | `scripts/gen_*`, `generated/`, `scripts/check_generated_artifacts.py`, generated-artifact tests |
| AIBOM is generated as AI inventory evidence. | `scripts/gen_aibom.py`, `generated/aibom/aibom.json` |
| Governance evidence is generated from repository source. | `scripts/gen_governance_evidence.py`, `generated/governance/governance-evidence.json` |
| Self-contained tests: tests own fixtures, avoid network and credentials, and do not depend on sibling side effects, gitignored artifacts, or today's date. | `tests/README.md`, sample tests under `tests/unit`, `tests/integration`, `tests/smoke` |
| Gate-before-merge: secrets, type check, generated drift, lint, tests with coverage, SAST, and dependency audit block merge. | `.github/workflows/ci.yml` |
| Machine-user pull request flow: bot may author PRs; human approves; bot cannot self-approve or self-merge. | `docs/machine-user-pr-flow.md`, `agents/backlog-worker.md` |
| Machine-user identity is scoped, gated, and audited without hardcoded credentials. | GitHub machine user, GitHub App, workload identity, or Microsoft Entra ID service principal in corporate profile |
| Symphony backlog loop: human curates; worker claims one item, moves it through the board, and stops for approval. | `BACKLOG.md`, `agents/backlog-worker.md` |
| Core agent fireteam ships with every project. | `agents/*.md`, generated tool views, `docs/agent-fireteam.md` |
| One roster, generated for the top three first-class tools: Anthropic Claude, Google Gemini, and OpenAI Codex/GPT. | `agents/*.md`, `scripts/gen_agent_views.py`, `scripts/check_agent_roster.py`, `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` |
| Agents are approved-models-only, audit-logged, no-exfil, and sensitivity-aware. | `config/approved-models.example.json`, `agents/*.md`, `docs/agent-fireteam.md` |
| Playbook -> weapon -> gate maturity: every capability climbs documented -> automated -> enforced. | `docs/agent-fireteam.md`, scripts, CI |
| OWASP LLM risk coverage maps every OWASP-LLM item to an enforced gate, not prose-only assurance. | `docs/owasp-llm-top10.md`, `scripts/check_owasp_llm.py`, `.github/workflows/owasp-llm.yml` |
| GitHub operationalization is repo-scoped, dry-runable, idempotent, and human-gated before outward writes. | `scripts/operationalize.sh`, `docs/operationalize.md`, `tests/unit/test_operationalize.py` |
| Independent/adversarial review: a second AI attempts to refute the first AI's output; humans adjudicate disagreements. | `agents/independent-reviewer.md`, `docs/independent-review.md`, `review-prompt.md` |
| Spec-first delivery: every meaningful feature flows through specify -> plan -> tasks -> implement. | `specs/TEMPLATE/`, `specs/README.md` |
| Honest documentation: current and target state are labeled separately and docs must match code. | `docs/docs-boundary.md`, `docs-site/`, docs build convention |
| Documentation impact gate: every implementation change includes internal docs, public docs-site/wiki docs, or an explicit no-docs-impact decision. | `scripts/check_docs_impact.py`, `.githooks/pre-commit`, `.github/pull_request_template.md`, `docs/documentation-gate.md` |
| Three-tier docs boundary: public, contributor, and corporate-governed docs are deliberately separated without making corporate systems a core dependency. | `docs-site/`, `docs/`, optional M365 SharePoint/Teams profile, `docs/docs-boundary.md` |
| Public wiki/docs-site is curated by audience and built from repository source. | `docs-site/` Docusaurus scaffold, `scripts/check_docs_site.py`, `.github/workflows/docs-site.yml` |
| Corporate-governed docs are profile-gated add-ons for policy, registry, RACI, retention, and access control. | Optional M365 SharePoint/Teams + Purview profile, `docs/m365-integration.md` |
| Document generation is reproducible from committed source. | `python-docx`, `python-pptx`, Pandoc convention, `scripts/gen_reference_docx.py`, `scripts/gen_sample_deck.py` |
| Diagram source of truth is explicit and maintainable. | Lucid Chart via approved MCP/connector, Mermaid/PlantUML/Graphviz/code fallback, `docs/diagramming.md` |
| Corporate tenant data governance is optional and complements, never replaces, in-repo sanitization. | Optional Microsoft Purview sensitivity labels and DLP profile, `docs/m365-integration.md` |
| Governed generated-output publication is dry-run by default and real external publication is profile-gated. | Optional SharePoint/Teams publisher stub, `scripts/publish_m365_stub.py` |
| Framework anchoring maps principles to AI governance frameworks and enforcement locations. | `docs/ai-governance-mapping.md` |
| Personal-scale default: core checks run without M365, Entra, Purview, or any enterprise tenant. | `scripts/check_profile_boundary.py`, optional corporate profile docs |
| Parallel agents are isolated, atomically claimed, concurrency-capped, budgeted, and merge-serialized. | git worktrees, `scripts/claim_backlog_item.py`, `scripts/dispatch_agents.py`, `scripts/merge_queue.py`, `docs/parallel-agents.md` |
| Security starts at spec time with assume breach, abuse cases, and threat modeling. | `agents/threat-modeler.md`, `specs/TEMPLATE/spec.md`, red/blue/purple fireteam |
| Secrets never enter repository files, logs, stdout, generated artifacts, or LLM context. | `SECRETS.md`, `.env.example`, Gitleaks pre-commit, CI, full-history scan, runtime sanitizer |
| Blast-radius check before edits. | `docs/safety-habits.md`, `CLAUDE.md`, `AGENTS.md` |
| Look-before-you-delete. | `docs/safety-habits.md`, `CLAUDE.md`, `agents/backlog-worker.md` |
| Progressive discovery for agent capabilities, distinct from progressive loading in UI. | `skills/README.md`, `skills/example_skill/SKILL.md`, `docs/methodology.md` |

## Stack Substitution Rule

When replacing a recommended tool, document the replacement in this file and preserve the same gate. Examples:

| Default | Acceptable Equivalent | Principle Preserved |
|---|---|---|
| `ruff` | `eslint`, `golangci-lint`, `clippy` | Lint before merge |
| `mypy` | `pyright`, `tsc --noEmit`, `go vet`, `cargo check` | Static type enforcement |
| `pytest` | `vitest`, `go test`, `cargo test` | Offline deterministic test gate |
| `bandit` | `semgrep`, `gosec`, `cargo-audit` | SAST gate |
| `pip-audit` | `npm audit`, `osv-scanner`, `cargo audit` | Dependency audit gate |
| Gitleaks | `detect-secrets`, `trufflehog`, enterprise secret scanner | Secrets never enter VCS |
| Docusaurus | MkDocs, VitePress, Docsify | Curated public docs boundary |
| Lucid Chart MCP | Mermaid, PlantUML, Graphviz, draw.io, Miro | Maintainable diagram source of truth |
| `python-docx` / `python-pptx` | Pandoc, Quarto, Office templates, Google Docs API | Reproducible document generation |
| Microsoft Entra ID service principal | GitHub App, workload identity, managed identity | Scoped machine-user identity |
| Microsoft Entra ID | Okta, Google Cloud IAM / Workspace, AWS IAM Identity Center | Central identity and managed machine-user identity |
| Azure Key Vault | HashiCorp Vault, AWS Secrets Manager, GCP Secret Manager, 1Password/Doppler, OS keyring for local only | Central secrets manager |
| Microsoft Purview labels + DLP | Enterprise DLP/classification equivalent | Tenant-level data governance |
| SharePoint/Teams | Confluence, Google Drive, enterprise records system | Corporate-governed publication |
| git worktrees | containers, ephemeral VMs | Parallel-agent isolation |
| lock-file queue | database queue, issue queue with atomic API claim | Atomic backlog claim |
