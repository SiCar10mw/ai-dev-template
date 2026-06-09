# First Run — Validate the Stack End-to-End

Before you rely on this template for real work, prove it survives contact with **your** environment. This
is your **range day**: one real pass through the whole loop on your machine, in your AI cockpit (VS Code +
GitHub Copilot, or Claude Code / Codex / Gemini). **Keys are optional** — your AI tool drives, and AI-SAST
defaults to its MockScanner, so you don't need model API keys for this run.

## Phase 0 — Prereqs
- [ ] Your AI cockpit is signed in (GitHub Copilot in VS Code, or Claude Code / Codex CLI)
- [ ] `python3 --version` → 3.11+ · `git` and `gh` both work · `gh auth login` done

## Phase 1 — Prove `local == CI`
From the repo root:
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
make check
```
✅ **Expected:** green — conformance audit, principle tripwires, secret-scan, ruff, mypy, pytest, bandit,
pip-audit. ❌ **If red:** capture the exact failing line — that's finding #1.

## Phase 2 — Operationalize
```bash
cat docs/operationalize.md          # read it first
make operationalize --dry-run       # or ./scripts/operationalize.sh --dry-run
make operationalize                 # confirm at the prompt
```
✅ **Expected:** the dry-run prints a plan and writes nothing; the real run enables branch protection +
required checks + the merge queue on your repo (secrets are set only if present in your env/keyring).

## Phase 3 — Drive one feature from your AI tool
In your cockpit's **agent mode**, pick a model (Claude / Gemini 3.1 Pro / GPT-Codex — this exercises
model-routing) and give a small, throwaway-but-real task:

> "Read AGENTS.md and CONSTITUTION.md, then add a typed helper + a passing pytest, following the repo
> conventions. Touch nothing else."

Watch: does it **read the governance files first**? follow the roster/conventions? write a **test**? Then:
```bash
make check
git checkout -b feat/first-run && git add -A && git commit -m "feat: first-run helper"
git push -u origin feat/first-run && gh pr create --fill
```
✅ **Expected:** typed code + a passing test. ❌ **Capture** if it ignored conventions or skipped the test —
that's the real signal.

## Phase 4 — Watch the gates, then break one on purpose
- Watch CI: lint · test · secret-scan · AI-SAST · conformance (`gh pr checks`).
- **Break it deliberately:** add a commit with a *fake* API key — a `sk-`-prefixed string of 20+ random
  characters — and push it. ✅ The **secret-scan should block the merge.** Then remove it.
- Review → approve → merge (the queue serializes it).

> A gate you've only ever seen pass is unverified. The real test of a guardrail is that it goes **red when
> it should** — so the deliberate break above is the most important step on this page.

## Phase 5 — Debrief
Write down:
1. **What broke** (exact errors + which phase)
2. **What surprised you** (your tool's behavior, a gate firing or not firing)
3. **What felt clunky** (too many steps? a confusing command?)
4. **The one thing you'd fix first**

That list is your *actual* next backlog — usually not what you predicted.
