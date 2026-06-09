from ai_dev_template.documents import build_project_brief_deck, build_reference_docx


def test_reference_docx_generation(tmp_path):
    output = build_reference_docx(tmp_path / "reference.docx")
    assert output.exists()
    assert output.stat().st_size > 1000


def test_project_brief_deck_generation(tmp_path):
    output = build_project_brief_deck(tmp_path / "project-brief.pptx")
    assert output.exists()
    assert output.stat().st_size > 1000
