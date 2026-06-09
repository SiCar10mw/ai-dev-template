"""Generate deterministic project governance artifacts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from ai_dev_template.documents import build_deck, build_reference_docx

ROOT_FILES = [
    "STANDARDS.md",
    "CONSTITUTION.md",
    "AGENTS.md",
    "GOVERNANCE.md",
    "SECURITY.md",
    "pyproject.toml",
    ".github/workflows/ci.yml",
    ".pre-commit-config.yaml",
]


def sha256_file(path: Path) -> str:
    """Return the SHA-256 digest for a file."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, data: dict[str, Any]) -> Path:
    """Write deterministic JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def build_architecture_diagram() -> str:
    """Return a source-controlled Mermaid architecture diagram."""
    return """flowchart LR
    Human[Human owner] --> Backlog[Symphony backlog]
    Backlog --> Agents[Core agent fireteam]
    Agents --> Specs[Spec-first artifacts]
    Specs --> Code[Code and tests]
    Code --> Gates[Local equals CI gates]
    Gates --> Generated[Generated evidence artifacts]
    Generated --> Docs[Docs and docs-site]
    Generated --> M365[M365 governed publication]
    Gates --> PR[Human-reviewed pull request]
"""


def build_aibom(root: Path) -> dict[str, Any]:
    """Build an AI Bill of Materials from repository source files."""
    agent_files = sorted(str(path.relative_to(root)) for path in (root / ".claude" / "agents").glob("*.md"))
    skill_files = sorted(str(path.relative_to(root)) for path in (root / "skills").glob("*/SKILL.md"))
    mcp_files = [".mcp.json", ".mcp.example.json", ".vscode/mcp.json", ".vscode/mcp.example.json"]
    model_files = ["config/model-routing.example.json", "config/approved-models.example.json"]
    return {
        "artifact": "AIBOM",
        "schema_version": "0.1",
        "generated_by": "scripts/gen_aibom.py",
        "agents": agent_files,
        "skills": skill_files,
        "mcp_configs": [path for path in mcp_files if (root / path).exists()],
        "model_configs": [path for path in model_files if (root / path).exists()],
        "quality_gates": [
            "template conformance",
            "documentation impact",
            "generated artifact drift",
            "gitleaks secret scan",
            "mypy type check",
            "ruff lint",
            "bare pytest with coverage",
            "bandit SAST",
            "pip-audit dependency audit",
        ],
    }


def build_governance_evidence(root: Path) -> dict[str, Any]:
    """Build deterministic governance evidence from the current repository."""
    files = {path: sha256_file(root / path) for path in ROOT_FILES if (root / path).exists()}
    return {
        "artifact": "governance-evidence",
        "schema_version": "0.1",
        "generated_by": "scripts/gen_governance_evidence.py",
        "enforced_in": {
            "repo_ci": [
                "make check",
                "gitleaks",
                "mypy",
                "generated artifact drift tripwire",
                "documentation impact gate",
            ],
            "pre_commit": [".pre-commit-config.yaml", ".githooks/pre-commit"],
            "corporate_controls": ["Microsoft Purview", "Microsoft Entra ID", "SharePoint/Teams retention"],
        },
        "source_hashes": files,
    }


def build_m365_publish_plan(generated_files: list[Path], output_dir: Path) -> dict[str, Any]:
    """Build a dry-run M365 publication plan for generated artifacts."""
    return {
        "artifact": "m365-publish-plan",
        "schema_version": "0.1",
        "generated_by": "scripts/gen_all_artifacts.py",
        "mode": "dry-run",
        "external_writes": False,
        "requires_human_approval_for_real_publish": True,
        "targets": [
            "SharePoint governed evidence library",
            "Teams governance committee channel",
        ],
        "artifacts": [str(path.relative_to(output_dir)) for path in generated_files],
    }


def generate_artifacts(root: Path, output_dir: Path) -> list[Path]:
    """Generate all committed derived artifacts."""
    output_dir.mkdir(parents=True, exist_ok=True)
    written = [
        write_json(output_dir / "aibom" / "aibom.json", build_aibom(root)),
        write_json(output_dir / "governance" / "governance-evidence.json", build_governance_evidence(root)),
    ]

    architecture = output_dir / "architecture" / "project-architecture.mmd"
    architecture.parent.mkdir(parents=True, exist_ok=True)
    architecture.write_text(build_architecture_diagram(), encoding="utf-8")
    written.append(architecture)

    written.append(build_reference_docx(output_dir / "documents" / "reference.docx"))
    written.append(
        build_deck(
            "Executive Brief",
            [
                ("Decision", "Human-governed AI-assisted delivery\nDeterministic gates\nGenerated evidence"),
                ("Risk", "Least privilege\nSensitive-data controls\nNo autonomous release decisions"),
                ("Next", "Review backlog\nRun make check\nPublish governed outputs through M365"),
            ],
            output_dir / "decks" / "executive-brief.pptx",
        )
    )
    written.append(
        build_deck(
            "Committee Brief",
            [
                ("Governance Domains", "AI-building SDLC\nAI-usage reference implementation\nCorporate controls"),
                ("Control Evidence", "AIBOM\nThreat model\nHuman approval\nAudit logging"),
                ("Operating Model", "Playbook to weapon to gate\nIndependent review\nGenerated artifacts"),
            ],
            output_dir / "decks" / "committee-brief.pptx",
        )
    )
    written.append(write_json(output_dir / "m365" / "publish-plan.json", build_m365_publish_plan(written, output_dir)))
    return sorted(written)
