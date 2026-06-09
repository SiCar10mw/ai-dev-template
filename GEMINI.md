# GEMINI.md - Agent Operating Guide

This file mirrors the repository operating rules for Gemini-backed sessions.

1. Read `CONSTITUTION.md`.
2. Read `STANDARDS.md` and `AGENTS.md`.
3. Treat repository files as authoritative over model memory.
4. Use spec-first and test-driven delivery.
5. Update docs, `docs-site/docs/`, or `docs/docs-impact.md` for implementation changes.
6. Run `make check` before handoff.
7. Regenerate derived artifacts with `python scripts/gen_all_artifacts.py`; never hand-edit `generated/`.
8. Stop for human approval before external writes, MCP writes, publishing, deployment, approval, merge, deletion, or
   credential rotation.
