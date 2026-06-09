from scripts.check_docs_impact import check_docs_impact


def test_docs_impact_fails_for_code_without_docs():
    errors = check_docs_impact({"ai_dev_template/verdicts.py"})
    assert errors
    assert "documentation update" in errors[0]


def test_docs_impact_passes_when_docs_change_with_code():
    errors = check_docs_impact({"ai_dev_template/verdicts.py", "docs/docs-impact.md"})
    assert errors == []
