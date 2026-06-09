# One-Command Operationalization

This runbook turns a cloned repository into a running, gated, governed GitHub repository without touching organization or
global state.

## Current Behavior

`make operationalize` runs `scripts/operationalize.sh`. The script:

- refuses to proceed until `make setup-identity` has recorded `config/identity.json` and `config/secrets.json`
- prints a repo-scoped plan first
- supports `--dry-run`
- prompts for confirmation before any outward GitHub write
- sets repository Actions secrets when local env or keyring values are present
- applies branch protection on the selected branch
- creates or updates a repository merge-queue ruleset
- enables and confirms repository workflows

The script does not run `gh auth login`, change `gh` global config, write org settings, or touch enterprise state.

## Required Local Setup

1. Clone the repository.
2. Install the Python development dependencies:

   ```bash
   python -m pip install -e ".[dev]"
   ```

3. Complete step 0 for operationalization by choosing the identity provider and secrets manager:

   ```bash
   make setup-identity
   ```

   This is required. The wizard records secret-free local profile files and prints provider-specific next steps. It does
   not provision cloud resources or upload secrets.

4. Authenticate the GitHub CLI for the target repository:

   ```bash
   gh auth login
   ```

5. Provide any repo secrets through environment variables or local keyring entries:

   ```bash
   export ANTHROPIC_API_KEY=...
   export OPENAI_API_KEY=...
   export GEMINI_API_KEY=...
   export MYTHOS_API_KEY=...
   export MACHINE_USER_TOKEN=...
   ```

   `AI_DEV_MACHINE_USER_TOKEN` and `GH_MACHINE_USER_TOKEN` are also accepted as local aliases for
   `MACHINE_USER_TOKEN`.

   Missing local values are skipped. Secret values are never printed.

## Dry Run

Run the plan without API calls:

```bash
bash scripts/operationalize.sh --dry-run --repo OWNER/REPO
```

The dry run is idempotent and does not invoke `gh`, but it still refuses if identity/secrets setup has not been recorded.
If you see the setup preflight failure, run `make setup-identity` first.

## Apply

Run the repo-scoped operationalization:

```bash
make operationalize
```

The script prints the plan and then waits for the exact confirmation phrase:

```text
apply repo operationalization
```

Only after that confirmation does it perform repository writes through `gh secret set --repo OWNER/REPO` and
`/repos/OWNER/REPO/...` API paths.

## Active Workflow Set

The repository ships these active workflows under `.github/workflows/`:

| Workflow | Purpose |
|---|---|
| `ci.yml` | Full local-equals-CI `make check` gate |
| `codeql.yml` | CodeQL static analysis |
| `sbom.yml` | SBOM plus generated AIBOM inventory evidence |
| `dependency-review.yml` | Pull request dependency review |
| `secret-scan.yml` | Gitleaks current-content and full-history scans |
| `owasp-llm.yml` | OWASP LLM mapping coverage gate |
| `ai-sast-pr.yml` | Blocking AI-SAST pull request gate |
| `ai-sast-scheduled.yml` | Scheduled non-blocking full AI-SAST scan |
| `conformance-audit.yml` | Template conformance and OWASP coverage audit |

The same workflow names are mirrored in `workflow_templates/` for organization-level starter workflows.

## Human Decisions

Humans still decide:

- which repository receives operationalization
- which local secrets are available for upload
- whether branch protection should use the default required status checks or `AI_DEV_REQUIRED_STATUS_CHECKS`
- whether the merge queue ruleset should be applied
- when to approve, merge, publish, deploy, or rotate credentials
