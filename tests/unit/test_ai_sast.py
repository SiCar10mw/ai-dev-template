from pathlib import Path

from ai_dev_template.ai_sast import Baseline, MockScanner, apply_policy, propose_patches_for_confirmed


def _marker(*parts: str) -> str:
    return "AI_SAST_MOCK_" + "_".join(parts)


def _write_marker(path: Path, marker: str) -> Path:
    path.write_text(f"# {marker}\n", encoding="utf-8")
    return path


def test_ai_sast_blocks_on_confirmed_high_finding(tmp_path: Path) -> None:
    target = _write_marker(tmp_path / "blocked.py", _marker("CONFIRMED", "HIGH"))

    findings = MockScanner().scan([target])
    result = apply_policy(findings, "high", Baseline.empty())

    assert not result.passed
    assert len(result.blocking_findings) == 1
    assert result.blocking_findings[0].confirmed
    assert result.blocking_findings[0].severity == "high"


def test_ai_sast_passes_when_confirmed_high_is_baseline_suppressed(tmp_path: Path) -> None:
    target = _write_marker(tmp_path / "suppressed.py", _marker("CONFIRMED", "HIGH"))

    findings = MockScanner().scan([target])
    baseline = Baseline(fingerprints=frozenset({findings[0].fingerprint}))
    result = apply_policy(findings, "high", baseline)

    assert result.passed
    assert result.ignored_findings == tuple(findings)


def test_ai_sast_ignores_low_and_unconfirmed_findings(tmp_path: Path) -> None:
    low_target = _write_marker(tmp_path / "low.py", _marker("CONFIRMED", "LOW"))
    unconfirmed_target = _write_marker(tmp_path / "unconfirmed.py", _marker("UNCONFIRMED", "HIGH"))

    findings = MockScanner().scan([low_target, unconfirmed_target])
    result = apply_policy(findings, "high", Baseline.empty())

    assert result.passed
    assert len(result.ignored_findings) == 2
    assert {finding.confirmed for finding in result.ignored_findings} == {False, True}


def test_mock_scanner_proposes_patch_for_confirmed_finding_without_applying(tmp_path: Path) -> None:
    marker = _marker("CONFIRMED", "HIGH")
    target = _write_marker(tmp_path / "blocked.py", marker)
    scanner = MockScanner(root=tmp_path)

    findings = scanner.scan(["blocked.py"])
    proposals = propose_patches_for_confirmed(scanner, findings, ["blocked.py"])

    assert len(proposals) == 1
    assert proposals[0].finding_fingerprint == findings[0].fingerprint
    assert proposals[0].auto_apply is False
    assert proposals[0].human_gate == "pull_request_review"
    assert "--- a/blocked.py" in proposals[0].patch
    assert f"-# {marker}" in proposals[0].patch
    assert marker in target.read_text(encoding="utf-8")
