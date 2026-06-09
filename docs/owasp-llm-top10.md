# OWASP Top 10 For LLM Applications Gate

This template enforces the Addendum 3 OWASP LLM mapping as a deterministic coverage gate. The risk IDs below follow
the OWASP Top 10 for LLM Applications v1.1 / 2023-24 numbering used by the addendum. OWASP's 2025 project page
renumbers and broadens several items, so this document keeps the requested IDs and records the closest current-control
note where the template does not host a full LLM application runtime.

Run the gate locally:

```bash
make owasp-llm
```

`make check` and `.github/workflows/owasp-llm.yml` also run `python scripts/check_owasp_llm.py`.

## Enforced Mapping

| OWASP ID | Addendum Risk | Enforced Gate In This Template |
|---|---|---|
| LLM01 | Prompt Injection | `ai_dev_template/sanitize.py` removes prompt-injection patterns, `tests/unit/test_sanitize.py` covers encoded injection text, and `pytest` is wired through `scripts/ci_check.sh`. |
| LLM02 | Insecure Output Handling | `escape_llm_output_for_html` escapes model output before HTML rendering, with active-markup regression coverage in `tests/unit/test_sanitize.py`. |
| LLM03 | Training Data Poisoning | Closest existing control: source/evidence integrity. The spec template requires threat modeling around generated evidence, and `scripts/check_generated_artifacts.py` fails stale generated artifacts. This template does not train or fine-tune models by default. |
| LLM04 | Model Denial of Service | Closest existing control: bounded model-mediated scanning. `ai_dev_template/ai_sast.py` defines `ScanBudget`, and AI-SAST workflows set file and byte budgets. |
| LLM05 | Supply Chain Vulnerabilities | `generated/aibom/aibom.json`, `pip-audit`, `.github/workflows/dependency-review.yml`, and `.github/workflows/sbom.yml` provide supply-chain inventory and review gates. |
| LLM06 | Sensitive Information Disclosure | `scripts/check_no_secrets.py`, Gitleaks, and CI secret scans block committed secrets; `sanitize_for_llm` redacts common PII patterns before LLM context. |
| LLM07 | Insecure Plugin Design | Closest existing control: MCP and profile-boundary gates. Default MCP configs are empty, tests assert that state, and `scripts/check_profile_boundary.py` blocks enterprise-only dependencies in core gates. |
| LLM08 | Excessive Agency | `CONSTITUTION.md`, agent personas, and `scripts/operationalize.sh` enforce read-only defaults, least privilege, repo-scoped changes, dry-run support, and human confirmation before outward writes. |
| LLM09 | Overreliance | `ai_dev_template/verdicts.py`, golden verdict tests, release docs, and human-approval gates keep LLM output advisory. Deterministic tools decide gate and release truth. |
| LLM10 | Model Theft | Closest existing control: approved model routing plus no-secret enforcement. Model/provider config is secret-free, secret scans block leaked credentials, and AI-SAST budgets also cover the 2025 unbounded-consumption renaming note. |

## Drift Rule

`scripts/check_owasp_llm.py` is the source of enforcement for this table. If a row points to a gate that is renamed,
replaced, or moved, update the checker and this document together. Removing a mapped gate makes `make check` fail.
