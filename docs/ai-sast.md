# AI-SAST Security Gate

AI-SAST adds a pluggable AI finder to the repository SAST posture without giving the model merge authority.

## Current Behavior

`ai_dev_template/ai_sast.py` defines the finder interface:

```text
SecurityScanner.scan(targets) -> list[Finding]
Finding = cwe, severity, file, line, confidence, rationale, confirmed, verification, fingerprint
```

The model output is evidence only. `scripts/check_ai_sast.py` is the deterministic decider and blocks only when all of
these are true:

1. The finding is confirmed by the adversarial verification pass.
2. The severity is greater than or equal to the configured threshold.
3. The finding fingerprint is not accepted in `.ai-sast-baseline.json`.

The default config is `config/ai-sast.example.json`. It selects `auto`, which uses `MockScanner` when
`ANTHROPIC_API_KEY` is not present. CI therefore stays offline and deterministic by default.

## Find Versus Decide

The finder may be `MockScanner` or `MythosScanner`.

- `MockScanner` is deterministic and used for tests and offline CI. It recognizes test-only marker strings and otherwise
  returns no findings for normal source.
- `MythosScanner` reads the `security_review` role from `config/model-routing.example.json`, uses the pinned
  Anthropic Mythos / Claude Fable 5 profile, requests strict JSON, and uses low temperature.

The decider never asks the model whether to block. It loads JSON and applies a reproducible policy over normalized
severity, the `confirmed` boolean, and baseline fingerprints.

## Adversarial Verification Rubric

Every candidate finding receives a second pass before it can become confirmed.

- A candidate survives only when the verifier can point to code-local evidence for the CWE, file, and line.
- Speculative issues, style concerns, unreachable paths, or findings that depend on missing context remain unconfirmed.
- The verifier records a short `verification` reason in the output JSON.
- `MockScanner` performs a deterministic marker cross-check. `MythosScanner` performs a bounded second model pass over
  the candidate and nearby code snippet.

Only confirmed findings can affect the deterministic policy.

## Cadences

Pull requests run `.github/workflows/ai-sast-pr.yml` on diff-only targets. This workflow is blocking because it runs the
deterministic decider after the finder emits JSON.

Scheduled scans run `.github/workflows/ai-sast-scheduled.yml` on the full repository with a file and byte budget cap.
Scheduled scans are non-blocking. When confirmed findings are present, the workflow opens a triage issue for humans.

The default budget avoids full-model scans on every commit. Use PR diff-only scanning for merge protection and scheduled
full scans for slower backlog discovery.

## Baseline

Accepted findings belong in `.ai-sast-baseline.json`:

```json
{
  "schema_version": "0.1",
  "accepted_findings": [
    {
      "fingerprint": "sha256-fingerprint",
      "reason": "Accepted by human review with compensating control"
    }
  ]
}
```

Baseline entries are deterministic suppressions, not model decisions. They require human review like other security
exceptions.

## OWASP LLM Mapping

AI-SAST findings primarily report CWE IDs, but the review lens should also consider the OWASP Top 10 for Large Language
Model Applications, especially LLM01 Prompt Injection, LLM02 Insecure Output Handling, LLM05 Supply Chain
Vulnerabilities, LLM06 Sensitive Information Disclosure, LLM07 Insecure Plugin Design, LLM08 Excessive Agency, and
LLM09 Overreliance. The OWASP project page points to the current Top 10 and notes that the GenAI Security Project now
covers broader generative AI security guidance: https://owasp.org/www-project-top-10-for-large-language-model-applications/

## Caveats

Public Fable 5 security policy gates offensive cyber content through Project Glasswing. That is acceptable for this
feature because the scanner is used for defensive code review. It may refuse offensive analysis or exploit development
requests; those refusals should not weaken the deterministic gate.

Mythos / Fable 5 is expected to be materially more expensive than the default coding model. Keep PR scans diff-only,
apply the configured byte budget, and reserve full scans for the scheduled cadence or explicit human-requested triage.
