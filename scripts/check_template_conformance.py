"""Conformance checks for the reusable development template."""

from __future__ import annotations

import ast
import json
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "STANDARDS.md",
    "CONSTITUTION.md",
    "GOVERNANCE.md",
    "AGENTS.md",
    "CLAUDE.md",
    "GEMINI.md",
    "SECURITY.md",
    "SECRETS.md",
    "CODEOWNERS",
    ".env.example",
    "BACKLOG.md",
    ".claude/agents/backlog-worker.md",
    ".claude/agents/independent-reviewer.md",
    ".claude/agents/orchestrator.md",
    ".claude/agents/security-reviewer.md",
    ".claude/agents/governance-control-mapper.md",
    ".claude/agents/privacy-data-classifier.md",
    ".claude/agents/spec-author.md",
    ".claude/agents/docs-drift-guardian.md",
    ".claude/agents/threat-modeler.md",
    ".claude/agents/test-author.md",
    ".claude/agents/release-supply-chain-steward.md",
    ".claude/agents/observability-fleet-health.md",
    ".github/copilot-instructions.md",
    ".github/instructions/python.instructions.md",
    ".github/instructions/docs.instructions.md",
    ".github/instructions/security.instructions.md",
    ".github/ISSUE_TEMPLATE/bug_report.md",
    ".github/ISSUE_TEMPLATE/feature_request.md",
    ".github/ISSUE_TEMPLATE/docs_drift.md",
    "specs/README.md",
    "specs/TEMPLATE/spec.md",
    "specs/TEMPLATE/plan.md",
    "specs/TEMPLATE/tasks.md",
    "tests/fixtures/goldens/verdict_pass.json",
    "docs/machine-user-pr-flow.md",
    "docs/independent-review.md",
    "review-prompt.md",
    "docs/docs-boundary.md",
    "docs/methodology.md",
    "docs/copilot-memory.md",
    "docs/agent-fireteam.md",
    "docs/documentation-gate.md",
    "docs/generated-artifacts.md",
    "docs/parallel-agents.md",
    "docs/docs-impact.md",
    "docs/mcp-and-tooling.md",
    "docs/diagramming.md",
    "docs/document-generation.md",
    "docs/model-routing.md",
    "docs/ai-governance-mapping.md",
    "docs/m365-integration.md",
    "docs/threat-model.md",
    "docs/release.md",
    "docs/adr/README.md",
    "docs/adr/TEMPLATE.md",
    "docs/adr/0001-record-architecture-decisions.md",
    "config/model-routing.example.json",
    "config/approved-models.example.json",
    "config/m365-publisher.example.json",
    "config/mandatory-principles.json",
    "config/fleet.example.json",
    "queue/backlog-queue.example.json",
    "skills/README.md",
    "skills/example_skill/SKILL.md",
    ".mcp.json",
    ".mcp.example.json",
    ".vscode/mcp.json",
    ".vscode/mcp.example.json",
    ".vscode/settings.json",
    ".vscode/extensions.json",
    ".githooks/pre-commit",
    ".pre-commit-config.yaml",
    ".gitleaks.toml",
    ".github/workflows/ci.yml",
    ".github/workflows/docs-site.yml",
    ".github/pull_request_template.md",
    "Makefile",
    "scripts/check_docs_impact.py",
    "scripts/check_docs_site.py",
    "scripts/check_generated_artifacts.py",
    "scripts/check_principle_tripwires.py",
    "scripts/check_profile_boundary.py",
    "scripts/check_no_secrets.py",
    "scripts/claim_backlog_item.py",
    "scripts/dispatch_agents.py",
    "scripts/merge_queue.py",
    "scripts/gen_all_artifacts.py",
    "scripts/gen_aibom.py",
    "scripts/gen_governance_evidence.py",
    "scripts/gen_architecture_diagram.py",
    "scripts/gen_exec_deck.py",
    "scripts/gen_committee_deck.py",
    "scripts/gen_reference_docx.py",
    "scripts/gen_sample_deck.py",
    "scripts/publish_m365_stub.py",
    "generated/aibom/aibom.json",
    "generated/governance/governance-evidence.json",
    "generated/architecture/project-architecture.mmd",
    "generated/documents/reference.docx",
    "generated/decks/executive-brief.pptx",
    "generated/decks/committee-brief.pptx",
    "generated/m365/publish-plan.json",
    "docs-site/README.md",
    "docs-site/package.json",
    "docs-site/package-lock.json",
    "docs-site/docusaurus.config.js",
    "docs-site/sidebars.js",
    "docs-site/docs/index.md",
]

MANDATORY_PHRASES = [
    "least privilege",
    "deterministic authority",
    "evidence integrity",
    "trust-boundary",
    "source-of-truth",
    "quality gates",
    "honest documentation",
    "documentation impact",
    "model/provider routing",
    "governed mcp",
    "secrets are never committed",
    "architecture/security decisions",
    "gitleaks",
    "mypy",
    "generated artifacts",
    "two-domain governance",
    "three-tier docs boundary",
    "personal-scale default",
    "parallel agents",
    "security starts at spec time",
    "secrets never enter",
]


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def check_required_files() -> list[str]:
    return [f"missing required file: {path}" for path in REQUIRED_FILES if not (ROOT / path).exists()]


def check_standards() -> list[str]:
    standards = _read("STANDARDS.md").lower()
    errors = []
    if "mandatory" not in standards or "recommended" not in standards:
        errors.append("STANDARDS.md must distinguish MANDATORY and RECOMMENDED tiers")
    for phrase in MANDATORY_PHRASES:
        if phrase not in standards:
            errors.append(f"STANDARDS.md missing principle phrase: {phrase}")
    return errors


def check_pytest_config() -> list[str]:
    data = tomllib.loads(_read("pyproject.toml"))
    pytest_options = data.get("tool", {}).get("pytest", {}).get("ini_options", {})
    errors = []
    if pytest_options.get("pythonpath") != ["."]:
        errors.append('pyproject.toml must set [tool.pytest.ini_options] pythonpath = ["."]')
    if pytest_options.get("testpaths") != ["tests"]:
        errors.append('pyproject.toml must set [tool.pytest.ini_options] testpaths = ["tests"]')
    return errors


def check_make_ci_parity() -> list[str]:
    makefile = _read("Makefile")
    workflow = _read(".github/workflows/ci.yml")
    ci_script = _read("scripts/ci_check.sh")
    if "./scripts/ci_check.sh" not in makefile:
        return ["Makefile check target must call ./scripts/ci_check.sh"]
    if "make check" not in workflow:
        return ["CI workflow must run make check as the full local==CI gate"]
    for command in (
        "python scripts/check_docs_impact.py",
        "python scripts/check_principle_tripwires.py",
        "python scripts/check_profile_boundary.py",
        "python scripts/check_docs_site.py",
        "python scripts/check_generated_artifacts.py",
        "python scripts/check_no_secrets.py",
        "pre-commit run gitleaks --all-files --config .pre-commit-config.yaml",
        "mypy ai_dev_template scripts skills",
    ):
        if command not in ci_script:
            return [f"scripts/ci_check.sh missing required command: {command}"]
    return []


def check_skill_metadata() -> list[str]:
    skill = _read("skills/example_skill/SKILL.md")
    required = ["name:", "description:", "when_to_use:"]
    return [f"example skill metadata missing: {field}" for field in required if field not in skill]


def check_type_hints() -> list[str]:
    errors = []
    for path in (ROOT / "ai_dev_template").glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.returns is None:
                errors.append(f"{path.relative_to(ROOT)}:{node.lineno} missing return type annotation")
    if not (ROOT / "ai_dev_template" / "py.typed").exists():
        errors.append("ai_dev_template/py.typed missing")
    return errors


def check_backlog_human_only() -> list[str]:
    backlog = _read("BACKLOG.md")
    if "🙋 Human-only" not in backlog:
        return ["BACKLOG.md must contain the Human-only section"]
    if not re.search(r"📋 Backlog.*🔨 In Progress.*👀 Review.*✅ Done", backlog, re.DOTALL):
        return ["BACKLOG.md must preserve the required board order"]
    return []


def check_mcp_configs() -> list[str]:
    errors = []
    root_mcp = json.loads(_read(".mcp.json"))
    vscode_mcp = json.loads(_read(".vscode/mcp.json"))
    if root_mcp != {"mcpServers": {}}:
        errors.append(".mcp.json must start with no external servers enabled")
    if vscode_mcp != {"servers": {}}:
        errors.append(".vscode/mcp.json must start with no external servers enabled")
    examples = _read(".mcp.example.json") + _read(".vscode/mcp.example.json")
    forbidden = ("sk-", "ghp_", "bearer ", "api_key_value", "password123")
    for token in forbidden:
        if token in examples.lower():
            errors.append(f"MCP example appears to contain a secret-like token: {token}")
    return errors


def check_docs_site_config() -> list[str]:
    package = json.loads(_read("docs-site/package.json"))
    scripts = package.get("scripts", {})
    dependencies = package.get("dependencies", {})
    errors = []
    if scripts.get("build") != "docusaurus build":
        errors.append('docs-site/package.json must expose "build": "docusaurus build"')
    if "@docusaurus/core" not in dependencies:
        errors.append("docs-site/package.json missing @docusaurus/core")
    return errors


def check_agent_roster() -> list[str]:
    agents = _read("AGENTS.md")
    errors = []
    for agent in (
        "orchestrator",
        "backlog-worker",
        "security-reviewer",
        "independent-reviewer",
        "governance-control-mapper",
        "privacy-data-classifier",
        "spec-author",
        "docs-drift-guardian",
        "threat-modeler",
        "test-author",
        "release-supply-chain-steward",
        "observability-fleet-health",
    ):
        if agent not in agents:
            errors.append(f"AGENTS.md missing required fireteam agent: {agent}")
    for path in (ROOT / ".claude" / "agents").glob("*.md"):
        text = path.read_text(encoding="utf-8")
        for phrase in ("approved-models-only", "audit-logging", "no-exfil", "sensitivity-aware"):
            if phrase not in text:
                errors.append(f"{path.relative_to(ROOT)} missing agent binding: {phrase}")
    return errors


def check_generated_artifact_gate() -> list[str]:
    ci_script = _read("scripts/ci_check.sh")
    precommit = _read(".pre-commit-config.yaml")
    if "python scripts/check_generated_artifacts.py" not in ci_script:
        return ["scripts/ci_check.sh must run generated artifact drift check"]
    if "generated-artifacts" not in precommit:
        return [".pre-commit-config.yaml must include generated artifact drift hook"]
    return []


def check_gitleaks_and_mypy() -> list[str]:
    precommit = _read(".pre-commit-config.yaml").lower()
    workflow = _read(".github/workflows/ci.yml").lower()
    ci_script = _read("scripts/ci_check.sh").lower()
    errors = []
    if "gitleaks" not in precommit:
        errors.append(".pre-commit-config.yaml must include gitleaks")
    if "gitleaks" not in workflow:
        errors.append(".github/workflows/ci.yml must include a blocking gitleaks job")
    if "full-history" not in workflow:
        errors.append(".github/workflows/ci.yml must include a blocking full-history secret scan job")
    if "mypy ai_dev_template scripts skills" not in precommit:
        errors.append(".pre-commit-config.yaml must include mypy")
    if "make type-check" not in workflow:
        errors.append(".github/workflows/ci.yml must include a blocking type-check job")
    if "mypy ai_dev_template scripts skills" not in ci_script:
        errors.append("scripts/ci_check.sh must run mypy")
    return errors


def check_spec_security_left() -> list[str]:
    spec = _read("specs/TEMPLATE/spec.md").lower()
    constitution = _read("CONSTITUTION.md").lower()
    errors = []
    for phrase in ("threat model", "abuse cases", "assume breach"):
        if phrase not in spec:
            errors.append(f"spec template missing security-from-left phrase: {phrase}")
    if "assume breach" not in constitution:
        errors.append("CONSTITUTION.md must state assume breach")
    return errors


def main() -> int:
    errors = []
    for check in (
        check_required_files,
        check_standards,
        check_pytest_config,
        check_make_ci_parity,
        check_skill_metadata,
        check_type_hints,
        check_backlog_human_only,
        check_mcp_configs,
        check_docs_site_config,
        check_agent_roster,
        check_generated_artifact_gate,
        check_gitleaks_and_mypy,
        check_spec_security_left,
    ):
        errors.extend(check())

    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("Template conformance checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
