from pathlib import Path

from ai_dev_template.verdicts import canonical_json, derive_verdict


def test_pass_verdict_matches_committed_golden() -> None:
    golden = Path("tests/fixtures/goldens/verdict_pass.json").read_text(encoding="utf-8").strip()

    actual = canonical_json(derive_verdict("pass"))

    assert actual == golden


def test_unknown_verdict_status_fails_closed() -> None:
    try:
        derive_verdict("unknown")
    except ValueError as exc:
        assert "unsupported status" in str(exc)
    else:
        raise AssertionError("unknown status should fail closed")

