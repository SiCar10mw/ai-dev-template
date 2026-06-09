#!/usr/bin/env python3
"""Verify an AI-SAST patch proposal in an isolated temporary copy."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from ai_dev_template.ai_sast import (
    Finding,
    PatchProposal,
    finding_from_json,
    findings_from_payload,
    load_ai_sast_config,
    load_json_path,
    patch_proposal_from_json,
    patch_proposals_from_payload,
    propose_patches_for_confirmed,
    scan_budget_from_config,
    select_scanner,
)

DEFAULT_TARGETS = ["ai_dev_template", "scripts", "skills"]
COPY_IGNORE_PATTERNS = (
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "htmlcov",
    "node_modules",
)


@dataclass(frozen=True)
class CommandEvidence:
    """Small deterministic command evidence record."""

    command: tuple[str, ...]
    exit_code: int
    stdout: str
    stderr: str

    def to_json(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""
        return asdict(self)


@dataclass(frozen=True)
class FixVerificationResult:
    """Deterministic fix verification result."""

    passed: bool
    patch_applied: bool
    finding_gone: bool
    tests_passed: bool
    finding_fingerprint: str
    scanner: str
    targets: tuple[str, ...]
    after_findings_count: int
    matching_after_findings: tuple[str, ...]
    patch_apply: CommandEvidence
    test_run: CommandEvidence | None
    isolation: str = "temporary copy"

    def to_json(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""
        data = asdict(self)
        data["patch_apply"] = self.patch_apply.to_json()
        data["test_run"] = self.test_run.to_json() if self.test_run else None
        return data


def _truncate(value: str, limit: int = 4000) -> str:
    if len(value) <= limit:
        return value
    return value[:limit] + "\n[truncated]\n"


def _run(command: Sequence[str], *, cwd: Path, input_text: str | None = None) -> CommandEvidence:
    completed = subprocess.run(  # nosec B603
        list(command),
        cwd=cwd,
        input=input_text,
        text=True,
        capture_output=True,
        check=False,
    )
    return CommandEvidence(
        command=tuple(command),
        exit_code=completed.returncode,
        stdout=_truncate(completed.stdout),
        stderr=_truncate(completed.stderr),
    )


def _copy_to_isolated_tree(repo_root: Path, temp_parent: Path) -> Path:
    isolated_root = temp_parent / "repo"
    shutil.copytree(
        repo_root,
        isolated_root,
        symlinks=True,
        ignore=shutil.ignore_patterns(*COPY_IGNORE_PATTERNS),
    )
    return isolated_root


def _finding_still_present(original: Finding, findings: Sequence[Finding]) -> list[Finding]:
    return [
        finding
        for finding in findings
        if finding.confirmed and finding.fingerprint == original.fingerprint
    ]


def verify_fix(
    *,
    repo_root: Path,
    finding: Finding,
    proposal: PatchProposal,
    scanner_name: str,
    targets: Sequence[str],
    test_command: Sequence[str],
    config: dict[str, Any],
) -> FixVerificationResult:
    """Apply a candidate patch in a temp copy, re-scan, and run tests."""
    with tempfile.TemporaryDirectory(prefix="ai-sast-verify-") as temp_name:
        isolated_root = _copy_to_isolated_tree(repo_root, Path(temp_name))
        patch_apply = _run(
            ("git", "apply", "--whitespace=nowarn", "-"),
            cwd=isolated_root,
            input_text=proposal.patch,
        )
        if patch_apply.exit_code != 0:
            return FixVerificationResult(
                passed=False,
                patch_applied=False,
                finding_gone=False,
                tests_passed=False,
                finding_fingerprint=finding.fingerprint,
                scanner=scanner_name,
                targets=tuple(targets),
                after_findings_count=0,
                matching_after_findings=(),
                patch_apply=patch_apply,
                test_run=None,
            )

        budget = scan_budget_from_config(config)
        scanner = select_scanner(scanner_name, config=config, budget=budget, root=isolated_root)
        after_findings = scanner.scan(targets)
        matching_after_findings = _finding_still_present(finding, after_findings)
        finding_gone = not matching_after_findings

        test_run = _run(test_command, cwd=isolated_root)
        tests_passed = test_run.exit_code == 0
        passed = finding_gone and tests_passed

        return FixVerificationResult(
            passed=passed,
            patch_applied=True,
            finding_gone=finding_gone,
            tests_passed=tests_passed,
            finding_fingerprint=finding.fingerprint,
            scanner=scanner.__class__.__name__,
            targets=tuple(targets),
            after_findings_count=len(after_findings),
            matching_after_findings=tuple(item.fingerprint for item in matching_after_findings),
            patch_apply=patch_apply,
            test_run=test_run,
        )


def _load_one_finding(path: Path, fingerprint: str | None) -> Finding:
    payload = load_json_path(path)
    if isinstance(payload, dict) and "cwe" in payload:
        finding = finding_from_json(payload)
        if fingerprint and finding.fingerprint != fingerprint:
            raise ValueError("AI-SAST finding fingerprint did not match --fingerprint")
        return finding

    findings = findings_from_payload(payload)
    if fingerprint:
        matches = [finding for finding in findings if finding.fingerprint == fingerprint]
    else:
        matches = findings
    if len(matches) != 1:
        raise ValueError("AI-SAST fix verification requires exactly one finding; pass --fingerprint to disambiguate")
    return matches[0]


def _load_one_proposal(path: Path, fingerprint: str | None) -> PatchProposal:
    payload = load_json_path(path)
    if isinstance(payload, dict) and "finding_fingerprint" in payload and "patch" in payload:
        proposal = patch_proposal_from_json(payload)
        if fingerprint and proposal.finding_fingerprint != fingerprint:
            raise ValueError("AI-SAST patch proposal fingerprint did not match --fingerprint")
        return proposal

    proposals = patch_proposals_from_payload(payload)
    if fingerprint:
        matches = [proposal for proposal in proposals if proposal.finding_fingerprint == fingerprint]
    else:
        matches = proposals
    if len(matches) != 1:
        raise ValueError(
            "AI-SAST fix verification requires exactly one patch proposal; pass --fingerprint to disambiguate"
        )
    return matches[0]


def _resolve_path(path_value: str, root: Path) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path
    return root / path


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="Run a deterministic MockScanner closed-loop check.")
    parser.add_argument("--repo-root", default=".", help="Repository root containing the files to copy.")
    parser.add_argument("--config", default="config/ai-sast.example.json", help="AI-SAST config path.")
    parser.add_argument("--finding", help="Finding JSON or findings report JSON.")
    parser.add_argument("--proposal", help="Patch proposal JSON or findings report JSON with patch_proposals.")
    parser.add_argument("--fingerprint", help="Finding fingerprint to select from report JSON.")
    parser.add_argument("--scanner", default="mock", choices=["auto", "mock", "mythos"], help="Scanner to re-run.")
    parser.add_argument("--targets", nargs="*", help="Files or directories to re-scan in the isolated copy.")
    parser.add_argument("--output", help="Write fix verification evidence JSON to this path.")
    parser.add_argument(
        "--test-command",
        nargs=argparse.REMAINDER,
        help="Test command to run in the isolated copy. Defaults to pytest.",
    )
    return parser.parse_args()


def _run_self_test() -> int:
    marker = "_".join(("AI", "SAST", "MOCK", "CONFIRMED", "HIGH"))
    with tempfile.TemporaryDirectory(prefix="ai-sast-self-test-") as temp_name:
        repo_root = Path(temp_name)
        target = repo_root / "vulnerable.py"
        target.write_text(f"# {marker}\nprint('ok')\n", encoding="utf-8")
        regression = repo_root / "regression_test.py"
        regression.write_text(
            "from pathlib import Path\n"
            f"assert {marker!r} not in Path('vulnerable.py').read_text(encoding='utf-8')\n",
            encoding="utf-8",
        )

        scanner = select_scanner("mock", config={}, root=repo_root)
        findings = scanner.scan(["vulnerable.py"])
        proposals = propose_patches_for_confirmed(scanner, findings, ["vulnerable.py"])
        if len(findings) != 1 or len(proposals) != 1:
            print("AI-SAST verify_fix self-test failed to create one finding and one proposal", file=sys.stderr)
            return 1

        result = verify_fix(
            repo_root=repo_root,
            finding=findings[0],
            proposal=proposals[0],
            scanner_name="mock",
            targets=["vulnerable.py"],
            test_command=[sys.executable, "regression_test.py"],
            config={},
        )
        original_unchanged = marker in target.read_text(encoding="utf-8")
        if result.passed and original_unchanged and not proposals[0].auto_apply:
            print("AI-SAST verify_fix self-test passed: patch verified in temporary copy only")
            return 0

        print(json.dumps(result.to_json(), indent=2, sort_keys=True), file=sys.stderr)
        if not original_unchanged:
            print("AI-SAST verify_fix self-test modified the source tree", file=sys.stderr)
        return 1


def main() -> int:
    args = _parse_args()
    if args.self_test:
        return _run_self_test()

    repo_root = Path(args.repo_root).resolve()
    if not args.finding or not args.proposal:
        raise SystemExit("--finding and --proposal are required unless --self-test is used")

    finding = _load_one_finding(_resolve_path(args.finding, repo_root), args.fingerprint)
    proposal = _load_one_proposal(_resolve_path(args.proposal, repo_root), args.fingerprint or finding.fingerprint)
    if proposal.finding_fingerprint != finding.fingerprint:
        raise SystemExit("AI-SAST patch proposal does not match the selected finding fingerprint")

    config = load_ai_sast_config(_resolve_path(args.config, repo_root))
    targets = list(args.targets or [str(target) for target in config.get("targets", DEFAULT_TARGETS)])
    test_command = list(args.test_command or ["pytest"])
    if not test_command:
        raise SystemExit("--test-command requires at least one command argument")

    result = verify_fix(
        repo_root=repo_root,
        finding=finding,
        proposal=proposal,
        scanner_name=str(args.scanner),
        targets=targets,
        test_command=test_command,
        config=config,
    )
    if args.output:
        _write_json(_resolve_path(args.output, repo_root), result.to_json())

    if result.passed:
        print("AI-SAST fix verification passed: finding gone and tests passed")
        return 0

    print("AI-SAST fix verification failed: finding must be gone and tests must pass", file=sys.stderr)
    print(json.dumps(result.to_json(), indent=2, sort_keys=True), file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
