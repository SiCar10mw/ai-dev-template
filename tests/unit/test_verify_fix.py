import difflib
import sys
from pathlib import Path

from ai_dev_template.ai_sast import MockScanner, PatchProposal, propose_patches_for_confirmed
from scripts.verify_fix import verify_fix

MARKER = "_".join(("AI", "SAST", "MOCK", "CONFIRMED", "HIGH"))


def _write_mock_repo(tmp_path: Path, *, regression_passes: bool) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    (root / "vulnerable.py").write_text(f"# {MARKER}\nprint('ok')\n", encoding="utf-8")
    assertion = f"assert {MARKER!r} not in Path('vulnerable.py').read_text(encoding='utf-8')"
    if not regression_passes:
        assertion = "raise SystemExit(1)"
    (root / "regression_test.py").write_text(
        "from pathlib import Path\n" f"{assertion}\n",
        encoding="utf-8",
    )
    return root


def _finding_and_good_proposal(root: Path) -> tuple[MockScanner, PatchProposal]:
    scanner = MockScanner(root=root)
    findings = scanner.scan(["vulnerable.py"])
    proposals = propose_patches_for_confirmed(scanner, findings, ["vulnerable.py"])
    assert len(findings) == 1
    assert len(proposals) == 1
    return scanner, proposals[0]


def _non_fixing_proposal(fingerprint: str) -> PatchProposal:
    old_lines = [f"# {MARKER}\n", "print('ok')\n"]
    new_lines = [f"# {MARKER}\n", "print('still vulnerable')\n"]
    patch = "".join(
        difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile="a/vulnerable.py",
            tofile="b/vulnerable.py",
        )
    )
    return PatchProposal(
        finding_fingerprint=fingerprint,
        patch=patch,
        rationale="This patch applies but leaves the mock finding marker in place.",
        proposer="unit-test",
    )


def test_verify_fix_passes_when_finding_is_gone_and_tests_pass(tmp_path: Path) -> None:
    root = _write_mock_repo(tmp_path, regression_passes=True)
    scanner, proposal = _finding_and_good_proposal(root)
    finding = scanner.scan(["vulnerable.py"])[0]

    result = verify_fix(
        repo_root=root,
        finding=finding,
        proposal=proposal,
        scanner_name="mock",
        targets=["vulnerable.py"],
        test_command=[sys.executable, "regression_test.py"],
        config={},
    )

    assert result.passed
    assert result.patch_applied
    assert result.finding_gone
    assert result.tests_passed
    assert MARKER in (root / "vulnerable.py").read_text(encoding="utf-8")


def test_verify_fix_fails_when_patch_applies_but_finding_remains(tmp_path: Path) -> None:
    root = _write_mock_repo(tmp_path, regression_passes=True)
    scanner = MockScanner(root=root)
    finding = scanner.scan(["vulnerable.py"])[0]

    result = verify_fix(
        repo_root=root,
        finding=finding,
        proposal=_non_fixing_proposal(finding.fingerprint),
        scanner_name="mock",
        targets=["vulnerable.py"],
        test_command=[sys.executable, "-c", "raise SystemExit(0)"],
        config={},
    )

    assert not result.passed
    assert result.patch_applied
    assert not result.finding_gone
    assert result.tests_passed


def test_verify_fix_fails_when_tests_regress_even_if_finding_is_gone(tmp_path: Path) -> None:
    root = _write_mock_repo(tmp_path, regression_passes=False)
    scanner, proposal = _finding_and_good_proposal(root)
    finding = scanner.scan(["vulnerable.py"])[0]

    result = verify_fix(
        repo_root=root,
        finding=finding,
        proposal=proposal,
        scanner_name="mock",
        targets=["vulnerable.py"],
        test_command=[sys.executable, "regression_test.py"],
        config={},
    )

    assert not result.passed
    assert result.patch_applied
    assert result.finding_gone
    assert not result.tests_passed
