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
| security-reviewer | `.claude/agents/security-reviewer.md` | Performs adversarial AppSec review |
| independent-reviewer | `.claude/agents/independent-reviewer.md` | Attempts to refute the primary output |
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
