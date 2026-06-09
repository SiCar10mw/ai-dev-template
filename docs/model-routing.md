# Model Routing And Provider Settings

Projects may use the top-three first-class model/tool profiles directly or through enterprise routing:

- Anthropic Claude
- Google Gemini
- OpenAI Codex/GPT

GitHub Copilot remains a fourth generated tool view for repositories that use Copilot instructions or Copilot CLI. The
source of truth is repository configuration plus enterprise policy, not model memory.

## Mandatory Rules

- Provider credentials are never committed.
- Authorization headers, bearer tokens, API keys, OAuth refresh tokens, and private model endpoints stay in environment
  variables or approved secret managers.
- Model choice does not grant authority. Deterministic tools decide verdicts, releases, approval state, and gate status.
- Independent review should use a different first-class model family from the primary pass when available.
- If model availability changes, update `config/model-routing.example.json` or the project-specific routing file.

## Default Configuration

`config/model-routing.example.json` documents the default first-class profiles and preferred roles for:

- primary coding
- independent review
- documentation

Copy it to a project-specific config file only if the project needs concrete provider names. Keep secrets out of both.

The example config covers one Claude profile, one Gemini profile, and one GPT/Codex profile. Projects may replace the
placeholder `model_id` values with enterprise-approved model IDs, but the committed file must stay secret-free.

## Security Review Finder

`config/model-routing.example.json` also defines a specialist `security_review` role for AI-SAST. The default profile is
Anthropic Mythos / Claude Fable 5 with a pinned model ID, strict JSON output, and low temperature.

That model is only a finder. It produces candidate findings for `ai_dev_template/ai_sast.py`; it never decides merge
status. `scripts/check_ai_sast.py` applies the deterministic policy over confirmed findings, severity threshold, and
`.ai-sast-baseline.json`.

## Provider Headers

Headers and provider-specific settings belong in the runtime client, environment, or enterprise config. Use committed
files only to document which variables are expected and which component consumes them.

## Copilot and Gemini Pro

GitHub Copilot is a CLIENT that can serve any approved model — including **Gemini 3.1 Pro**. Copilot's model selection is governed by the same `approved-models` list, and the Copilot instructions are model-agnostic: they hold regardless of which top-three model Copilot is running.
