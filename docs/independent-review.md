# Independent / Adversarial Review

Independent review is mandatory for substantial changes. The second reviewer is asked to refute the first agent's work, not to summarize it.

## Why

AI-generated work can be fluent and wrong. Confidence comes from convergence between independent checks, deterministic gates, and human adjudication.

## Convergence Rubric

| Result | Meaning | Action |
|---|---|---|
| Primary agent, independent reviewer, and deterministic gates agree | High confidence | Human reviews normally |
| Deterministic gates pass, reviewer raises low-risk concerns | Moderate confidence | Human adjudicates findings |
| Reviewer finds correctness, security, or test gaps | Low confidence | Fix or explicitly reject with evidence |
| Reviewer finds MCP/tool-access overreach | Low confidence | Stop until least-privilege and approval are clear |
| Deterministic gates fail | Not releasable | Stop and fix gates |
| Tools disagree materially | Slow down | Human adjudicates before merge |

## Human Role

The human adjudicates tool false-positives and model disagreements. A reviewer finding is not automatically true; it is a claim that needs evidence.

## Required Artifacts

- Primary agent summary.
- Diff or branch.
- Tests and command results.
- Independent review output.
- Human decision on material disagreements.
- Documentation-impact evidence.
