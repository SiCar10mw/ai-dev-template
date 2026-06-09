# Organization Workflow Templates

This directory is the org-level starter set for repositories that adopt the AI development template after initial
creation. Mirror these files into the organization's special `.github` repository under GitHub's workflow templates
location when enabling starter workflows centrally.

The active repository workflows live under `.github/workflows/`. Keep this starter set aligned with those workflows:

- `ci.yml`
- `codeql.yml`
- `sbom.yml`
- `dependency-review.yml`
- `secret-scan.yml`
- `owasp-llm.yml`
- `ai-sast-pr.yml`
- `ai-sast-scheduled.yml`
- `conformance-audit.yml`

Each template has a matching `.properties.json` file for GitHub's starter-workflow metadata.
