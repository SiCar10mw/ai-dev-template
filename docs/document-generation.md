# Document Generation

This template includes document-generation defaults so project documents, decks, and public docs stay reproducible.

## Recommended Defaults

| Output | Default Tool |
|---|---|
| DOCX deliverables | `python-docx` |
| Markdown-to-DOCX conversion | Pandoc, when the project needs full Markdown fidelity |
| PowerPoint decks | `python-pptx` |
| Public wiki/docs site | Docusaurus in `docs-site/` |
| Diagrams | Lucid Chart via MCP, with source-controlled fallback diagrams |

## Commands

```bash
make documents
make reference-docx
make project-brief-deck
make docs-site-check
```

Committed evidence artifacts go under `generated/` and are never hand-edited. Local drafts go under `out/`, which is
gitignored. Commit source inputs, scripts, templates, docs, and generated evidence that the drift tripwire checks.

## Rules

- Generated documents must be reproducible from committed source.
- If a generated artifact is evidence, store it in-repo with schema or format expectations documented.
- If a generated artifact is only a local draft, keep it in `out/`.
- Run `python scripts/check_generated_artifacts.py` before committing generated evidence.
- Do not allow an LLM to invent document status. Current, target, draft, and future states must be labeled.
- The documentation-impact gate applies to scripts that generate documents and to the documents that explain them.
