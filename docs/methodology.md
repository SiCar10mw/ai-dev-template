# Methodology

This file records the reusable development method that every project created from this template inherits.

## Verbatim Methodology

1. Progressive discovery (agent selects capability by metadata) vs progressive loading (UI paints cached summary instantly, streams detail behind a spinner) — distinct.
2. Symphony backlog loop — human curates; worker runs one item and stops for approval; never self-merges.
3. Independent / adversarial review — second AI against the first's work; trust convergence, not any single agent (including the one that wrote the code).
4. Quality rails — deterministic-verdict golden tripwires; gate-before-merge; local==CI (bare test runner + path config); blast-radius check before edits; self-contained tests; machine-user PR flow; look-before-you-delete; docs boundary.
5. Spec-first delivery governed by a short constitution that wins on any conflict.

## What This Means in Practice

- A feature without a spec is not ready for implementation.
- A code change without tests is not ready for review.
- A claim without deterministic evidence is not a gate result.
- A bot-authored pull request is not approved until a human approves it.
- A second AI review increases confidence only when disagreements are adjudicated by a human.
- Documentation is part of the change, not an afterthought; implementation changes fail the docs-impact gate when docs
  are not updated.
- MCP and diagram tooling are external-system boundaries and follow least-privilege, approval, and sanitization rules.
- Derived artifacts follow generate-don't-maintain: `scripts/gen_*` writes them and CI fails if committed artifacts are
  stale.
- Capabilities climb playbook -> weapon -> gate: documented, invokable, then enforced.
