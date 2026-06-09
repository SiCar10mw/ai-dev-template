#!/usr/bin/env python3
"""Verify OWASP Top 10 for LLM Applications coverage is enforced by gates."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Evidence:
    """A file and required strings that prove one gate exists."""

    path: str
    required_text: tuple[str, ...]
    label: str


@dataclass(frozen=True)
class RiskMapping:
    """One OWASP LLM risk mapped to deterministic repository evidence."""

    risk_id: str
    title: str
    evidence: tuple[Evidence, ...]


OWASP_LLM_MAPPINGS: tuple[RiskMapping, ...] = (
    RiskMapping(
        risk_id="LLM01",
        title="Prompt Injection",
        evidence=(
            Evidence("ai_dev_template/sanitize.py", ("sanitize_for_llm", "_INJECTION_PATTERNS"), "input sanitizer"),
            Evidence(
                "tests/unit/test_sanitize.py",
                ("ignore%2520previous", "sanitize_for_llm"),
                "injection-pattern regression test",
            ),
            Evidence("scripts/ci_check.sh", ("pytest --cov=ai_dev_template",), "pytest gate wiring"),
        ),
    ),
    RiskMapping(
        risk_id="LLM02",
        title="Insecure Output Handling",
        evidence=(
            Evidence(
                "ai_dev_template/sanitize.py",
                ("escape_llm_output_for_html", "html.escape"),
                "output escaping helper",
            ),
            Evidence(
                "tests/unit/test_sanitize.py",
                ("test_escape_llm_output_for_html_escapes_active_markup", "&lt;script&gt;"),
                "output-escaping regression test",
            ),
            Evidence("scripts/ci_check.sh", ("pytest --cov=ai_dev_template",), "pytest gate wiring"),
        ),
    ),
    RiskMapping(
        risk_id="LLM03",
        title="Training Data Poisoning",
        evidence=(
            Evidence(
                "specs/TEMPLATE/spec.md",
                ("Threat Model and Abuse Cases", "generated evidence"),
                "spec-time poisoning note through source/evidence integrity",
            ),
            Evidence(
                "scripts/check_generated_artifacts.py",
                ("stale generated artifact", "generate_artifacts"),
                "generated artifact drift gate",
            ),
            Evidence(
                "scripts/ci_check.sh",
                ("python scripts/check_generated_artifacts.py",),
                "generated artifact gate wiring",
            ),
        ),
    ),
    RiskMapping(
        risk_id="LLM04",
        title="Model Denial of Service",
        evidence=(
            Evidence("ai_dev_template/ai_sast.py", ("ScanBudget", "max_total_bytes"), "bounded model scan input"),
            Evidence(".github/workflows/ai-sast-pr.yml", ("AI_SAST_MAX_TOTAL_BYTES",), "AI-SAST PR budget"),
            Evidence(
                ".github/workflows/ai-sast-scheduled.yml",
                ("AI_SAST_MAX_TOTAL_BYTES",),
                "AI-SAST scheduled budget",
            ),
        ),
    ),
    RiskMapping(
        risk_id="LLM05",
        title="Supply Chain Vulnerabilities",
        evidence=(
            Evidence("generated/aibom/aibom.json", ('"artifact": "AIBOM"',), "committed AIBOM"),
            Evidence(
                "scripts/ci_check.sh",
                ("pip-audit --requirement requirements.txt --disable-pip --no-deps",),
                "dependency audit gate",
            ),
            Evidence(".github/workflows/dependency-review.yml", ("dependency-review-action",), "dependency review"),
            Evidence(".github/workflows/sbom.yml", ("sbom", "gen_aibom.py"), "SBOM/AIBOM workflow"),
        ),
    ),
    RiskMapping(
        risk_id="LLM06",
        title="Sensitive Information Disclosure",
        evidence=(
            Evidence("scripts/check_no_secrets.py", ("SECRET_PATTERNS",), "secret-pattern scan"),
            Evidence(".pre-commit-config.yaml", ("gitleaks",), "gitleaks pre-commit hook"),
            Evidence("scripts/ci_check.sh", ("python scripts/check_no_secrets.py",), "secret scan gate wiring"),
            Evidence("ai_dev_template/sanitize.py", ("_PII_PATTERNS",), "PII redaction before LLM context"),
            Evidence("tests/unit/test_sanitize.py", ("test_sanitize_redacts_pii",), "no-PII-to-LLM regression test"),
        ),
    ),
    RiskMapping(
        risk_id="LLM07",
        title="Insecure Plugin Design",
        evidence=(
            Evidence("tests/unit/test_mcp_config.py", ('{"mcpServers": {}}', '{"servers": {}}'), "empty MCP defaults"),
            Evidence("scripts/check_profile_boundary.py", ("ENTERPRISE_ONLY_MARKERS",), "profile boundary gate"),
            Evidence("scripts/ci_check.sh", ("python scripts/check_profile_boundary.py",), "profile boundary wiring"),
        ),
    ),
    RiskMapping(
        risk_id="LLM08",
        title="Excessive Agency",
        evidence=(
            Evidence(
                "CONSTITUTION.md",
                ("External systems are read-only by default", "explicit human approval"),
                "read-only-default principle",
            ),
            Evidence(
                "agents/backlog-worker.md",
                ("No external-system writes without explicit human approval",),
                "human-gated writes",
            ),
            Evidence(
                "scripts/operationalize.sh",
                ("repo-scoped", "confirm", "--dry-run"),
                "repo-scoped operationalization prompt",
            ),
        ),
    ),
    RiskMapping(
        risk_id="LLM09",
        title="Overreliance",
        evidence=(
            Evidence("ai_dev_template/verdicts.py", ("derive_verdict", "raise ValueError"), "deterministic verdicts"),
            Evidence(
                "tests/unit/test_verdict_golden.py",
                ("test_unknown_verdict_status_fails_closed", "verdict_pass.json"),
                "golden verdict gate",
            ),
            Evidence("docs/release.md", ("not by an LLM",), "human release decision documentation"),
        ),
    ),
    RiskMapping(
        risk_id="LLM10",
        title="Model Theft",
        evidence=(
            Evidence("config/approved-models.example.json", ("model_id", "provider"), "approved model catalog"),
            Evidence(
                "config/model-routing.example.json",
                ("api_key", "environment or secret manager"),
                "secret-free routing",
            ),
            Evidence("scripts/check_no_secrets.py", ("openai-key", "github-token"), "credential leak scan"),
            Evidence("ai_dev_template/ai_sast.py", ("max_total_bytes",), "unbounded-consumption compatibility note"),
        ),
    ),
)

GLOBAL_EVIDENCE: tuple[Evidence, ...] = (
    Evidence("docs/owasp-llm-top10.md", tuple(mapping.risk_id for mapping in OWASP_LLM_MAPPINGS), "mapping docs"),
    Evidence("Makefile", ("owasp-llm:", "python scripts/check_owasp_llm.py"), "Makefile target"),
    Evidence("scripts/ci_check.sh", ("python scripts/check_owasp_llm.py",), "local make check wiring"),
    Evidence(".github/workflows/owasp-llm.yml", ("workflow_call", "python scripts/check_owasp_llm.py"), "CI job"),
    Evidence("agents/threat-modeler.md", ("check_owasp_llm.py", "OWASP"), "spec-time threat-modeler reference"),
)


def _read(root: Path, relative: str) -> str:
    return (root / relative).read_text(encoding="utf-8")


def _check_evidence(root: Path, evidence: Evidence, *, owner: str) -> list[str]:
    path = root / evidence.path
    if not path.exists():
        return [f"{owner}: missing {evidence.label}: {evidence.path}"]
    text = _read(root, evidence.path)
    return [
        f"{owner}: {evidence.path} missing {evidence.label} marker: {marker}"
        for marker in evidence.required_text
        if marker not in text
    ]


def check_owasp_llm(root: Path = ROOT) -> list[str]:
    """Return coverage errors for the OWASP LLM gate mapping."""
    errors: list[str] = []
    expected_ids = {f"LLM{index:02d}" for index in range(1, 11)}
    actual_ids = {mapping.risk_id for mapping in OWASP_LLM_MAPPINGS}
    if actual_ids != expected_ids:
        errors.append(f"OWASP mapping IDs must be exactly LLM01..LLM10; got {sorted(actual_ids)}")

    for mapping in OWASP_LLM_MAPPINGS:
        for evidence in mapping.evidence:
            errors.extend(_check_evidence(root, evidence, owner=f"{mapping.risk_id} {mapping.title}"))

    for evidence in GLOBAL_EVIDENCE:
        errors.extend(_check_evidence(root, evidence, owner="global OWASP LLM gate"))
    return errors


def main() -> int:
    errors = check_owasp_llm()
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("OWASP LLM gate coverage check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
