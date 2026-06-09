from scripts.check_profile_boundary import check_corporate_profile, check_personal_profile


def test_personal_profile_rejects_enterprise_dependency_in_core_gate(tmp_path) -> None:
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    (scripts / "ci_check.sh").write_text("python scripts/publish_m365_stub.py\n", encoding="utf-8")

    errors = check_personal_profile(tmp_path)

    assert errors
    assert "enterprise marker" in errors[0]


def test_corporate_profile_validates_scaffold(tmp_path) -> None:
    errors = check_corporate_profile(tmp_path)

    assert errors
    assert "missing corporate profile scaffold" in errors[0]
