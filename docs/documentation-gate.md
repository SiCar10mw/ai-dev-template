# Documentation Gate

Documentation is part of the change. A code commit that changes behavior, setup, architecture, tests, tools, agents,
models, MCP servers, or generated outputs must update documentation in the same change.

## Mandatory Rule

Every implementation change must include one of these:

- an internal contributor documentation update under `docs/`
- a public or audience-specific docs-site update under `docs-site/docs/`
- a corporate-governed documentation update or publication plan for M365-owned policy, registry, RACI, or records
- a top-level governance update such as `README.md`, `STANDARDS.md`, `AGENTS.md`, `CLAUDE.md`, `CONSTITUTION.md`,
  `GOVERNANCE.md`, `BACKLOG.md`, or `CHANGELOG.md`
- an explicit no-docs-impact entry in `docs/docs-impact.md`

## Enforcement

- `.githooks/pre-commit` runs `python scripts/check_docs_impact.py --staged`.
- `make check` runs `python scripts/check_docs_impact.py` for local and CI parity.
- The pull request template requires the author to state which docs changed.
- The independent reviewer checks for documentation drift.

## Public Wiki Default

`docs-site/` is the default public wiki surface. This template ships Docusaurus as the recommended generator because it
is static, reviewable, and fits docs-as-code. A future project may replace it with MkDocs, VitePress, Docsify, or an
enterprise wiki generator, but the mandatory documentation-impact gate stays.

Build it with:

```bash
cd docs-site && npm ci && npm run build
```

## Audience Split

Use `docs-site/docs/` for public, customer, operator, business-owner, or user-facing documentation. Use `docs/` for
contributor, maintainer, and agent operating material. Use corporate-governed M365 locations for policy, AI registry,
RACI, approval records, and retention-controlled governance evidence. If a topic belongs to multiple audiences, keep the
source of truth clear and link deliberately.
