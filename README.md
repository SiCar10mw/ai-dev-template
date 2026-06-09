# AI Development Template

Reusable project starter template for disciplined, AI-assisted, human-governed development.

The template bakes in:

- Constitution-first governance.
- Spec-first delivery.
- Test-driven development.
- Deterministic gates over model judgment.
- Symphony backlog loop.
- Independent/adversarial AI review.
- Machine-user pull request flow.
- Progressive discovery for agent skills.
- Local equals CI quality gates.
- Governed MCP tool access for external tools such as Lucid Chart.
- Mandatory documentation-impact checks for code changes.
- Reproducible DOCX and PowerPoint generation.
- Contributor docs plus a Docusaurus public docs-site scaffold.
- Copilot-native repository instructions, ADRs, threat model, security policy, and issue templates.
- Gitleaks and mypy gates in pre-commit and CI.
- Generated evidence artifacts with a drift tripwire.
- M365 governance integration patterns for Entra, Purview, SharePoint, and Teams.

## Start a New Project

```bash
cp -R ai-dev-template my-new-project
cd my-new-project
./bootstrap.sh
```

The bootstrap script prompts for:

- project name
- machine-user git name
- machine-user git email

It then initializes git if needed and runs the first `make check`.

## First Human Actions

1. Read `STANDARDS.md`.
2. Fill project-specific language in `CONSTITUTION.md` without weakening the mandatory principles.
3. Clear or replace the example item in `BACKLOG.md`.
4. Configure the machine-user identity used for AI-authored branches.
5. Protect `main` so CI and human review are required.
6. Enable or replace the default Docusaurus docs-site.
7. Configure approved MCP servers, such as Lucid Chart, after reviewing least-privilege access.
8. Replace `@owner` in `CODEOWNERS`.
9. Update `docs/threat-model.md` and create ADRs for project-specific architecture choices.
10. Update `GOVERNANCE.md`, `config/approved-models.example.json`, and `config/m365-publisher.example.json`.

## Default Stack

The default stack is Python:

```bash
python -m pip install -e ".[dev]"
make check
```

For other stacks, keep the mandatory principles and replace tools with equivalents. Document substitutions in `STANDARDS.md`.

The default profile is personal/core and does not require M365, Entra ID, Purview, SharePoint, Teams, or an enterprise
tenant. Corporate governance scaffolding is optional:

```bash
make corporate-profile-check
```

## Documentation Gate

Every implementation change must update internal docs, public docs-site/wiki docs, or `docs/docs-impact.md` with a
no-docs-impact decision. The local git hook and CI both run the documentation-impact check.

```bash
git config core.hooksPath .githooks
python scripts/check_docs_impact.py --staged
```

## Document And Wiki Defaults

```bash
make documents
make docs-site-check
cd docs-site && npm ci && npm run build
```

The recommended public wiki generator is Docusaurus. The mandatory rule is not Docusaurus itself; it is that docs are
kept current, audience-scoped, reviewed, and built from repository source.

## Important Files

| File | Purpose |
|---|---|
| `STANDARDS.md` | Mandatory principles vs recommended tools |
| `CONSTITUTION.md` | Non-negotiable project governance |
| `AGENTS.md` | Agent roster and operating rules |
| `CLAUDE.md` | Claude/session-specific operating guide |
| `BACKLOG.md` | Symphony backlog board |
| `specs/` | Spec-first delivery artifacts |
| `tests/` | Unit, integration, smoke, and golden tests |
| `skills/` | Progressive-discovery skill convention |
| `docs/` | Contributor and methodology docs |
| `docs-site/` | Docusaurus public docs/wiki scaffold |
| `.mcp.json` | Project MCP config for GitHub Copilot CLI |
| `.vscode/mcp.json` | VS Code MCP config |
| `config/model-routing.example.json` | Secret-free model role and provider guidance |
| `GOVERNANCE.md` | Two-domain AI-building and AI-usage governance model |
| `.github/copilot-instructions.md` | Repository-wide Copilot instructions |
| `docs/adr/` | Architecture decision records |
| `docs/threat-model.md` | Baseline threat model |
| `SECURITY.md` | Security reporting and baseline policy |
| `generated/` | Committed generated artifacts checked by drift tripwire |
