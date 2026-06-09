---
applyTo: "{.github/**,.mcp.json,.mcp.example.json,.vscode/mcp.json,.vscode/mcp.example.json,scripts/**}"
---

Prefer least privilege and read-only defaults. Never commit secrets or private endpoints. MCP-backed creates, edits,
shares, publishes, deletes, deployments, approvals, merges, and permission changes require explicit human approval.
Gitleaks, mypy, generated-artifact drift, and SAST gates are blocking.
