# Agent Fireteam

Every project created from this template ships with a core fireteam. The roster is mandatory and model-neutral in
`agents/*.md`; individual model choices are recommended defaults and may be swapped only within the approved-model
boundary.

## Generated Tool Views

`agents/*.md` is the single source of truth. Run `python scripts/gen_agent_views.py` after changing a persona. The
drift tripwire `python scripts/check_agent_roster.py` fails the build if any generated view diverges.

| Rank | Tool View | Generated Files |
|---|---|---|
| 1 | Anthropic Claude | `CLAUDE.md`, `.claude/agents/*.md` |
| 2 | Google Gemini | `GEMINI.md` |
| 3 | OpenAI Codex/GPT | `AGENTS.md` |
| 4 | GitHub Copilot | `.github/copilot-instructions.md` |

## Common Binding

Every agent is bound to:

- approved-models-only
- audit-logging
- no-exfil
- sensitivity-aware behavior
- least privilege
- human-gated external writes

## Roster

| Agent | Source Persona | Purpose |
|---|---|---|
| orchestrator | `agents/orchestrator.md` | Routes work and preserves human gates |
| backlog-worker | `agents/backlog-worker.md` | Runs one Symphony backlog item and stops for review |
| threat-modeler | `agents/threat-modeler.md` | Red team: abuse cases and attack trees at spec time |
| security-reviewer | `agents/security-reviewer.md` | Blue team: AppSec review and defensive validation |
| independent-reviewer | `agents/independent-reviewer.md` | Purple team: refutation and convergence review |
| test-author | `agents/test-author.md` | Writes failing tests and golden fixtures first |
| release-supply-chain-steward | `agents/release-supply-chain-steward.md` | Versioning, SBOM/AIBOM, dependency and model upgrade gates |
| observability-fleet-health | `agents/observability-fleet-health.md` | Pass rate, queue depth, gate hotspots, and fleet budget |
| governance-control-mapper | `agents/governance-control-mapper.md` | Maps work to AI governance controls |
| privacy-data-classifier | `agents/privacy-data-classifier.md` | Flags sensitive data and labels outputs |
| spec-author | `agents/spec-author.md` | Creates Spec-Kit delivery artifacts |
| docs-drift-guardian | `agents/docs-drift-guardian.md` | Finds docs/code/generated-artifact drift |

## Playbook -> Weapon -> Gate Ladder

| Maturity | Meaning | Template Example |
|---|---|---|
| Playbook | The standard is documented and reviewable. | `docs/`, `AGENTS.md`, persona files |
| Weapon | The standard can be invoked as a tool or agent. | generated tool views, `scripts/gen_*` |
| Gate | The standard is enforced automatically. | `make check`, CI, pre-commit, drift tripwire |

Every capability should climb this ladder: documented -> automated -> enforced.

## Red / Blue / Purple

| Color | Agent | Role |
|---|---|---|
| Red | `threat-modeler` | Offensive abuse cases and attack trees before build |
| Blue | `security-reviewer` | Defensive AppSec review and gate validation |
| Purple | `independent-reviewer` | Refutation, convergence analysis, and human-adjudicated disagreements |
