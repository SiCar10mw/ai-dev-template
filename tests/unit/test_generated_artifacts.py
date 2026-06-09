from pathlib import Path

from scripts.check_generated_artifacts import stale_artifacts


def test_generated_artifact_tripwire_detects_stale_file(tmp_path: Path) -> None:
    expected = tmp_path / "expected"
    actual = tmp_path / "actual"
    expected.mkdir()
    actual.mkdir()
    (expected / "artifact.txt").write_text("fresh\n", encoding="utf-8")
    (actual / "artifact.txt").write_text("stale\n", encoding="utf-8")

    assert stale_artifacts(expected, actual) == ["stale generated artifact: artifact.txt"]


def test_generated_artifact_tripwire_accepts_matching_file(tmp_path: Path) -> None:
    expected = tmp_path / "expected"
    actual = tmp_path / "actual"
    expected.mkdir()
    actual.mkdir()
    (expected / "artifact.txt").write_text("fresh\n", encoding="utf-8")
    (actual / "artifact.txt").write_text("fresh\n", encoding="utf-8")

    assert stale_artifacts(expected, actual) == []
