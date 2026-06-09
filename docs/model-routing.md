# Model Routing And Provider Settings

Projects may use GPT, Anthropic, Gemini, or other models through GitHub Copilot CLI, VS Code, enterprise model routing,
or approved direct provider clients. The source of truth is repository configuration plus enterprise policy, not model
memory.

## Mandatory Rules

- Provider credentials are never committed.
- Authorization headers, bearer tokens, API keys, OAuth refresh tokens, and private model endpoints stay in environment
  variables or approved secret managers.
- Model choice does not grant authority. Deterministic tools decide verdicts, releases, approval state, and gate status.
- Independent review should use a different model family from the primary pass when available.
- If model availability changes, update `config/model-routing.example.json` or the project-specific routing file.

## Default Configuration

`config/model-routing.example.json` documents preferred roles for:

- primary coding
- independent review
- documentation

Copy it to a project-specific config file only if the project needs concrete provider names. Keep secrets out of both.

## Provider Headers

Headers and provider-specific settings belong in the runtime client, environment, or enterprise config. Use committed
files only to document which variables are expected and which component consumes them.
