# MCP And Tooling

Model Context Protocol (MCP) is the default pattern for connecting agents to external tools, data sources, and services.
The mandatory principle is governed tool access; MCP is the recommended mechanism.

## Mandatory Rules

- External systems are read-only by default.
- MCP tools that can write, publish, share, delete, approve, deploy, or change permissions require explicit human
  approval before use.
- Do not commit tokens, API keys, bearer headers, refresh tokens, private endpoints, or personal workspace IDs.
- Register project-level MCP servers in `.mcp.json` for GitHub Copilot CLI and `.vscode/mcp.json` for VS Code only after
  reviewing the blast radius.
- Prefer enterprise allowlists and registries when available.
- Treat MCP output as external input. Sanitize or validate before feeding it to an LLM, writing files, or invoking
  commands.

## Default Files

| File | Purpose |
|---|---|
| `.mcp.json` | Project-level GitHub Copilot CLI MCP config. Empty by default to avoid unapproved external access. |
| `.mcp.example.json` | Safe example showing Lucid developer-docs MCP access. |
| `.vscode/mcp.json` | Workspace-level VS Code MCP config. Empty by default. |
| `.vscode/mcp.example.json` | VS Code example config. |

## Lucid Default For Diagrams

Lucid Chart is the preferred external diagramming tool when diagram edits need a collaborative visual workspace. Use the
official Lucid MCP server or enterprise-approved Lucid connector when available.

The safe default in this template only includes Lucid developer documentation MCP in example files. Workspace access to
Lucid documents should be configured after a human confirms account, OAuth, sharing, and write permissions.

## Approval Boundary

The following are read-oriented and may be used when credentials and policy allow it:

- search existing Lucid documents
- fetch document metadata or content for review
- export a diagram image for documentation
- search developer documentation

The following require explicit approval each time:

- create a Lucid document
- edit an existing Lucid document
- create a public or anonymous share link
- share a document with collaborators
- publish, delete, or move external assets
