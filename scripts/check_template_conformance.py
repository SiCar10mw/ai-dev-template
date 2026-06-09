"""Conformance checks for the reusable development template."""

from __future__ import annotations

import ast
import json
import re
import subprocess
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
    "docs/identity.md",
    "CODEOWNERS",
    ".env.example",
    "BACKLOG.md",
    "agents/backlog-worker.md",
    "agents/independent-reviewer.md",
    "agents/orchestrator.md",
    "agents/security-reviewer.md",
    "agents/governance-control-mapper.md",
    "agents/privacy-data-classifier.md",
    "agents/spec-author.md",
    "agents/docs-drift-guardian.md",
    "agents/threat-modeler.md",
    "agents/test-author.md",
    "agents/release-supply-chain-steward.md",
    "agents/observability-fleet-health.md",
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
    "docs/owasp-llm-top10.md",
    "docs/operationalize.md",
    "docs/m365-integration.md",
    "docs/threat-model.md",
    "docs/release.md",
    "docs/adr/README.md",
    "docs/adr/TEMPLATE.md",
    "docs/adr/0001-record-architecture-decisions.md",
    "config/model-routing.example.json",
    "config/identity.example.json",
    "config/secrets.example.json",
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
    ".github/workflows/codeql.yml",
    ".github/workflows/sbom.yml",
    ".github/workflows/dependency-review.yml",
    ".github/workflows/secret-scan.yml",
    ".github/workflows/owasp-llm.yml",
    ".github/workflows/ai-sast-pr.yml",
    ".github/workflows/ai-sast-scheduled.yml",
    ".github/workflows/conformance-audit.yml",
    ".github/workflows/docs-site.yml",
    ".github/pull_request_template.md",
    "Makefile",
    "scripts/__init__.py",
    "scripts/check_docs_impact.py",
    "scripts/check_docs_site.py",
    "scripts/check_generated_artifacts.py",
    "scripts/check_principle_tripwires.py",
    "scripts/check_profile_boundary.py",
    "scripts/check_no_secrets.py",
    "scripts/check_owasp_llm.py",
    "scripts/check_agent_roster.py",
    "scripts/setup_identity.sh",
    "scripts/operationalize.sh",
    "scripts/claim_backlog_item.py",
    "scripts/dispatch_agents.py",
    "scripts/merge_queue.py",
    "scripts/gen_agent_views.py",
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
    "workflow_templates/README.md",
    "workflow_templates/ci.yml",
    "workflow_templates/ci.properties.json",
    "workflow_templates/codeql.yml",
    "workflow_templates/codeql.properties.json",
    "workflow_templates/sbom.yml",
    "workflow_templates/sbom.properties.json",
    "workflow_templates/dependency-review.yml",
    "workflow_templates/dependency-review.properties.json",
    "workflow_templates/secret-scan.yml",
    "workflow_templates/secret-scan.properties.json",
    "workflow_templates/owasp-llm.yml",
    "workflow_templates/owasp-llm.properties.json",
    "workflow_templates/ai-sast-pr.yml",
    "workflow_templates/ai-sast-pr.properties.json",
    "workflow_templates/ai-sast-scheduled.yml",
    "workflow_templates/ai-sast-scheduled.properties.json",
    "workflow_templates/conformance-audit.yml",
    "workflow_templates/conformance-audit.properties.json",
    "workflow_templates/ai-dev-template.svg",
]

GITHUB_NATIVE_WORKFLOWS = (
    "ci",
    "codeql",
    "sbom",
    "dependency-review",
    "secret-scan",
    "owasp-llm",
    "ai-sast-pr",
    "ai-sast-scheduled",
    "conformance-audit",
)

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
    "centralized identity",
    "central secrets manager",
    "governed mcp",
    "secrets are never committed",
    "architecture/security decisions",
    "gitleaks",
    "mypy",
    "generated artifacts",
    "one roster",
    "top three",
    "two-domain governance",
    "three-tier docs boundary",
    "personal-scale default",
    "parallel agents",
    "security starts at spec time",
    "secrets never enter",
    "owasp llm",
    "github operationalization",
]

ENV_EXAMPLE_KEY = re.compile(r"^[A-Z][A-Z0-9_]*$")
SECRET_NAME = re.compile(r"(API_KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL|CLIENT_SECRET)", re.IGNORECASE)
SECRET_VALUE_PATTERNS = (
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{32,}\b"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b"),
)


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
        "python scripts/check_owasp_llm.py",
        "python scripts/check_docs_site.py",
        "python scripts/check_generated_artifacts.py",
        "python scripts/check_no_secrets.py",
        "pre-commit run gitleaks --all-files --config .pre-commit-config.yaml",
        "mypy ai_dev_template scripts skills",
        "pip-audit --requirement requirements.txt --disable-pip --no-deps",
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


def _strip_optional_quotes(value: str) -> str:
    stripped = value.strip()
    if len(stripped) >= 2 and stripped[0] == stripped[-1] and stripped[0] in {"'", '"'}:
        return stripped[1:-1]
    return stripped


def _is_placeholder_value(value: str) -> bool:
    stripped = _strip_optional_quotes(value)
    lowered = stripped.lower()
    if stripped == "":
        return True
    if stripped.startswith("<") and stripped.endswith(">"):
        return True
    return lowered in {"placeholder", "replace_me", "changeme", "example", "example-value"}


def _looks_like_real_secret_value(value: str) -> bool:
    return any(pattern.search(value) for pattern in SECRET_VALUE_PATTERNS)


def check_env_example_shapes(root: Path = ROOT) -> list[str]:
    """Fail if .env.example contains real-looking values instead of placeholders."""
    path = root / ".env.example"
    if not path.exists():
        return ["missing required file: .env.example"]

    errors = []
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line.removeprefix("export ").strip()
        if "=" not in line:
            errors.append(f".env.example:{line_number} must use KEY=<placeholder> shape")
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if not ENV_EXAMPLE_KEY.fullmatch(key):
            errors.append(f".env.example:{line_number} has invalid variable name: {key}")
        if _looks_like_real_secret_value(value) or not _is_placeholder_value(value):
            errors.append(f".env.example:{line_number} must contain only placeholder shapes, not real values")
    return errors


def _walk_strings(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        strings: list[str] = []
        for key, item in value.items():
            strings.extend(_walk_strings(key))
            strings.extend(_walk_strings(item))
        return strings
    if isinstance(value, list):
        strings = []
        for item in value:
            strings.extend(_walk_strings(item))
        return strings
    return []


def check_secrets_config(root: Path = ROOT) -> list[str]:
    """Fail if the example secret-provider config is not offline by default."""
    path = root / "config" / "secrets.example.json"
    if not path.exists():
        return ["missing required file: config/secrets.example.json"]

    data = json.loads(path.read_text(encoding="utf-8"))
    errors = []
    if not isinstance(data, dict):
        return ["config/secrets.example.json must be a JSON object"]
    if data.get("default_provider") != "auto":
        errors.append('config/secrets.example.json must set default_provider to "auto"')
    if data.get("selected_manager") != "unconfigured":
        errors.append('config/secrets.example.json must set selected_manager to "unconfigured"')
    if data.get("contains_credentials") is not False:
        errors.append("config/secrets.example.json must declare contains_credentials false")
    if data.get("resolution_order") != ["env", "keyring"]:
        errors.append("config/secrets.example.json must default to offline env/keyring resolution")
    providers = data.get("providers", {})
    if not isinstance(providers, dict):
        return [*errors, "config/secrets.example.json providers must be an object"]
    for required in (
        "env",
        "keyring",
        "azure_key_vault",
        "hashicorp_vault",
        "aws_secrets_manager",
        "gcp_secret_manager",
        "onepassword_doppler",
        "os_keyring",
    ):
        if required not in providers:
            errors.append(f"config/secrets.example.json missing provider: {required}")
    azure = providers.get("azure_key_vault", {})
    if isinstance(azure, dict) and azure.get("enabled") is not False:
        errors.append("config/secrets.example.json must keep azure_key_vault disabled by default")
    for value in _walk_strings(data):
        if _looks_like_real_secret_value(value):
            errors.append("config/secrets.example.json contains a real-looking secret value")
            break
    return errors


def check_identity_config(root: Path = ROOT) -> list[str]:
    """Fail if the identity-provider example config is missing required onboarding choices."""
    path = root / "config" / "identity.example.json"
    if not path.exists():
        return ["missing required file: config/identity.example.json"]

    data = json.loads(path.read_text(encoding="utf-8"))
    errors = []
    if not isinstance(data, dict):
        return ["config/identity.example.json must be a JSON object"]
    if data.get("selected_provider") != "unconfigured":
        errors.append('config/identity.example.json must set selected_provider to "unconfigured"')
    if data.get("contains_credentials") is not False:
        errors.append("config/identity.example.json must declare contains_credentials false")
    providers = data.get("providers", {})
    if not isinstance(providers, dict):
        return [*errors, "config/identity.example.json providers must be an object"]
    for required in (
        "microsoft_entra_id",
        "okta",
        "google_cloud_iam_workspace",
        "aws_iam_identity_center",
        "local_dev_only",
    ):
        if required not in providers:
            errors.append(f"config/identity.example.json missing provider: {required}")
    for value in _walk_strings(data):
        if _looks_like_real_secret_value(value):
            errors.append("config/identity.example.json contains a real-looking secret value")
            break
    return errors


def _constant_string(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _is_os_environ(node: ast.AST) -> bool:
    return (
        isinstance(node, ast.Attribute)
        and node.attr == "environ"
        and isinstance(node.value, ast.Name)
        and node.value.id == "os"
    )


def _secret_name_from_env_call(node: ast.Call) -> str | None:
    if not node.args:
        return None
    if (
        isinstance(node.func, ast.Attribute)
        and node.func.attr == "get"
        and _is_os_environ(node.func.value)
    ):
        return _constant_string(node.args[0])
    if (
        isinstance(node.func, ast.Attribute)
        and node.func.attr == "getenv"
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "os"
    ):
        return _constant_string(node.args[0])
    return None


def check_secret_access_patterns(root: Path = ROOT) -> list[str]:
    """Fail when package code bypasses SecretProvider for secret-like environment names."""
    package = root / "ai_dev_template"
    if not package.exists():
        return ["missing required package: ai_dev_template"]

    errors = []
    for path in sorted(package.glob("*.py")):
        if path.name == "secrets.py":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            secret_name = None
            if isinstance(node, ast.Call):
                secret_name = _secret_name_from_env_call(node)
            elif isinstance(node, ast.Subscript) and _is_os_environ(node.value):
                secret_name = _constant_string(node.slice)
            if secret_name and SECRET_NAME.search(secret_name):
                line_number = getattr(node, "lineno", 0)
                errors.append(
                    f"{path.relative_to(root)}:{line_number} must load {secret_name} through SecretProvider"
                )
    return errors


def check_model_profiles() -> list[str]:
    approved = json.loads(_read("config/approved-models.example.json"))
    routing = json.loads(_read("config/model-routing.example.json"))
    errors = []
    required_profiles = {
        "anthropic_claude": "claude",
        "google_gemini": "gemini",
        "openai_codex_gpt": "gpt-codex",
    }

    approved_profiles = approved.get("default_profiles", {})
    routing_tools = routing.get("first_class_tools", [])
    if not isinstance(approved_profiles, dict):
        errors.append("config/approved-models.example.json default_profiles must be an object")
        approved_profiles = {}
    if not isinstance(routing_tools, list):
        errors.append("config/model-routing.example.json first_class_tools must be a list")
        routing_tools = []

    routed_profiles = {
        str(tool.get("profile"))
        for tool in routing_tools
        if isinstance(tool, dict) and "profile" in tool
    }
    for profile, family in required_profiles.items():
        approved_profile = approved_profiles.get(profile, {})
        if not isinstance(approved_profile, dict):
            errors.append(f"config/approved-models.example.json missing default profile: {profile}")
            continue
        if approved_profile.get("model_family") != family:
            errors.append(f"config/approved-models.example.json {profile} must use model_family {family}")
        if not str(approved_profile.get("model_id", "")).strip():
            errors.append(f"config/approved-models.example.json {profile} must define a non-secret model_id")
        if profile not in routed_profiles:
            errors.append(f"config/model-routing.example.json missing first-class profile: {profile}")
    fourth_view = routing.get("fourth_view", {})
    if not isinstance(fourth_view, dict) or fourth_view.get("profile") != "github_copilot":
        errors.append("config/model-routing.example.json must keep GitHub Copilot as the fourth view")
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
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "check_agent_roster.py")],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return []
    messages = [
        line.removeprefix("FAIL: ")
        for line in [*result.stderr.splitlines(), *result.stdout.splitlines()]
        if line.strip()
    ]
    return messages or ["agent roster source/generated-view drift check failed"]


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


def check_github_native_operationalization() -> list[str]:
    docs = _read("docs/operationalize.md")
    makefile = _read("Makefile")
    script = _read("scripts/operationalize.sh")
    errors = []

    for name in GITHUB_NATIVE_WORKFLOWS:
        workflow_path = f".github/workflows/{name}.yml"
        template_path = f"workflow_templates/{name}.yml"
        properties_path = f"workflow_templates/{name}.properties.json"
        workflow = _read(workflow_path)
        if "workflow_call" not in workflow:
            errors.append(f"{workflow_path} must be reusable through workflow_call")
        if not (ROOT / template_path).exists():
            errors.append(f"missing organization workflow template: {template_path}")
        if not (ROOT / properties_path).exists():
            errors.append(f"missing organization workflow template metadata: {properties_path}")
        if f"`{name}.yml`" not in docs:
            errors.append(f"docs/operationalize.md must reference workflow: {name}.yml")

    if "operationalize:" not in makefile or "scripts/operationalize.sh" not in makefile:
        errors.append("Makefile must expose make operationalize")

    required_script_markers = (
        "--dry-run",
        "read -r -p",
        'gh secret set "$secret" --repo "$REPO"',
        '"/repos/$REPO/',
        "Dry-run complete. No gh commands were invoked.",
    )
    for marker in required_script_markers:
        if marker not in script:
            errors.append(f"scripts/operationalize.sh missing repo-scoped marker: {marker}")

    forbidden_script_markers = ("--org", "/orgs/", "gh config set")
    for marker in forbidden_script_markers:
        if marker in script:
            errors.append(f"scripts/operationalize.sh must not touch global/org state: {marker}")
    return errors


def check_identity_setup_wizard() -> list[str]:
    """Fail if required identity/secrets onboarding is no longer wired into setup and operationalization."""
    makefile = _read("Makefile")
    bootstrap = _read("bootstrap.sh")
    operationalize = _read("scripts/operationalize.sh")
    setup = _read("scripts/setup_identity.sh")
    docs = _read("docs/identity.md") + _read("docs/operationalize.md") + _read("docs/first-run.md")
    errors = []

    required_setup_markers = (
        "--non-interactive",
        "--idp",
        "--secrets",
        "Choose your IDENTITY PROVIDER",
        "Choose your SECRETS MANAGER",
        "No cloud calls were made",
        "config/identity.json",
        "config/secrets.json",
    )
    for marker in required_setup_markers:
        if marker not in setup:
            errors.append(f"scripts/setup_identity.sh missing required marker: {marker}")

    if "setup-identity:" not in makefile or "scripts/setup_identity.sh" not in makefile:
        errors.append("Makefile must expose make setup-identity")
    if "scripts/setup_identity.sh" not in bootstrap:
        errors.append("bootstrap.sh must run setup_identity.sh during onboarding")
    if (
        "make setup-identity" not in operationalize
        or "identity/secrets profile has not been chosen" not in operationalize
    ):
        errors.append("scripts/operationalize.sh must refuse before setup-identity is run")
    if "make setup-identity" not in docs or "step 0" not in docs.lower():
        errors.append("identity, operationalize, and first-run docs must reference setup-identity as step 0")
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
        check_env_example_shapes,
        check_identity_config,
        check_secrets_config,
        check_secret_access_patterns,
        check_model_profiles,
        check_docs_site_config,
        check_agent_roster,
        check_generated_artifact_gate,
        check_gitleaks_and_mypy,
        check_spec_security_left,
        check_github_native_operationalization,
        check_identity_setup_wizard,
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
