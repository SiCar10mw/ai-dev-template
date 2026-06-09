# Agent Fireteam

Every project created from this template ships with a core fireteam. The roster is mandatory; individual model choices
are recommended defaults and may be swapped only within the approved-model boundary.

## Common Binding

Every agent is bound to:

- approved-models-only
- audit-logging
- no-exfil
- sensitivity-aware behavior
- least privilege
- human-gated external writes

## Roster

| Agent | Persona File | Purpose |
|---|---|---|
| orchestrator | `.claude/agents/orchestrator.md` | Routes work and preserves human gates |
| backlog-worker | `.claude/agents/backlog-worker.md` | Runs one Symphony backlog item and stops for review |
| threat-modeler | `.claude/agents/threat-modeler.md` | Red team: abuse cases and attack trees at spec time |
| security-reviewer | `.claude/agents/security-reviewer.md` | Blue team: AppSec review and defensive validation |
| independent-reviewer | `.claude/agents/independent-reviewer.md` | Purple team: refutation and convergence review |
| test-author | `.claude/agents/test-author.md` | Writes failing tests and golden fixtures first |
| release-supply-chain-steward | `.claude/agents/release-supply-chain-steward.md` | Versioning, SBOM/AIBOM, dependency and model upgrade gates |
| observability-fleet-health | `.claude/agents/observability-fleet-health.md` | Pass rate, queue depth, gate hotspots, and fleet budget |
| governance-control-mapper | `.claude/agents/governance-control-mapper.md` | Maps work to AI governance controls |
| privacy-data-classifier | `.claude/agents/privacy-data-classifier.md` | Flags sensitive data and labels outputs |
| spec-author | `.claude/agents/spec-author.md` | Creates Spec-Kit delivery artifacts |
| docs-drift-guardian | `.claude/agents/docs-drift-guardian.md` | Finds docs/code/generated-artifact drift |

## Playbook -> Weapon -> Gate Ladder

| Maturity | Meaning | Template Example |
|---|---|---|
| Playbook | The standard is documented and reviewable. | `docs/`, `AGENTS.md`, persona files |
| Weapon | The standard can be invoked as a tool or agent. | `.claude/agents/*.md`, `scripts/gen_*` |
| Gate | The standard is enforced automatically. | `make check`, CI, pre-commit, drift tripwire |

Every capability should climb this ladder: documented -> automated -> enforced.

## Red / Blue / Purple

| Color | Agent | Role |
|---|---|---|
| Red | `threat-modeler` | Offensive abuse cases and attack trees before build |
| Blue | `security-reviewer` | Defensive AppSec review and gate validation |
| Purple | `independent-reviewer` | Refutation, convergence analysis, and human-adjudicated disagreements |
