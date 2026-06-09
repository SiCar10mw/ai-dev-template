# Implementation Plan: AI-SAST Security Gate

**Spec**: `spec.md`

## Summary

Add a pluggable AI-SAST finder and deterministic checker. Keep CI offline by default through MockScanner and route real
runtime scanning through the configured Anthropic Mythos / Claude Fable 5 security-review profile.

## Technical Context

| Field | Decision |
|---|---|
| Language / runtime | Python 3.11+ |
| Testing | `pytest` unit tests |
| Linting | `ruff` |
| Security scan | Bandit plus AI-SAST Mock gate |
| Dependency audit | `pip-audit` |
| External writes | Scheduled GitHub issue creation only after human review merges the workflow |

## Constitution Check

| Principle | Pass / Issue | Evidence |
|---|---|---|
| Least privilege / read-only by default | Pass | PR workflow read-only; scheduled workflow has issues write only |
| Deterministic authority | Pass | `scripts/check_ai_sast.py` decides gate status |
| Evidence integrity | Pass | Findings JSON and baseline are reproducible JSON |
| Trust-boundary sanitization | Pass | Model inputs are bounded and sanitized |
| Source-of-truth authority | Pass | Config, docs, and baseline live in repo |
| Quality gates | Pass | `make check` includes Mock AI-SAST |
| Honest docs | Pass | `docs/ai-sast.md` documents current behavior and caveats |

## Test Strategy

- Unit test confirmed high finding blocks.
- Unit test baseline suppression passes.
- Unit test low and unconfirmed findings do not block.
- Run `make check` offline.

## Project Structure

```text
ai_dev_template/ai_sast.py
scripts/check_ai_sast.py
config/ai-sast.example.json
.ai-sast-baseline.json
.github/workflows/ai-sast-pr.yml
.github/workflows/ai-sast-scheduled.yml
docs/ai-sast.md
tests/unit/test_ai_sast.py
```

## Risks

- Real provider model IDs may need enterprise replacement before runtime use.
- Scheduled issue creation is an external write when the workflow runs in GitHub and must remain human-governed.
