# Developers

Document public or partner-facing developer guidance here.

Internal contributor process belongs in `docs/`.

## Project Bootstrap

Start new projects by running `./bootstrap.sh` from the template checkout. The script creates a fresh project directory,
initializes a new local git repository without the template remote, creates a venv, installs dependencies, and runs
`make check`.

## Agent Roster

Agent personas are maintained once in `agents/*.md` and generated for Anthropic Claude, Google Gemini, OpenAI Codex/GPT,
and GitHub Copilot with `python scripts/gen_agent_views.py`.
