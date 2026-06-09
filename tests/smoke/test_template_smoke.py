from ai_dev_template import canonical_json, derive_verdict


def test_template_smoke_imports_and_runs() -> None:
    assert canonical_json(derive_verdict("partial")) == (
        '{"passed":false,"reason":"incomplete evidence","status":"partial"}'
    )

