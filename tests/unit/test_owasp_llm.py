from pathlib import Path

from scripts.check_owasp_llm import OWASP_LLM_MAPPINGS, check_owasp_llm

ROOT = Path(__file__).resolve().parents[2]


def test_owasp_llm_mapping_covers_all_items() -> None:
    assert {mapping.risk_id for mapping in OWASP_LLM_MAPPINGS} == {f"LLM{index:02d}" for index in range(1, 11)}


def test_owasp_llm_gate_passes_for_template() -> None:
    assert check_owasp_llm(ROOT) == []


def test_owasp_llm_gate_fails_when_required_evidence_is_missing(tmp_path: Path) -> None:
    errors = check_owasp_llm(tmp_path)

    assert any("LLM01 Prompt Injection: missing input sanitizer" in error for error in errors)
    assert any("global OWASP LLM gate: missing mapping docs" in error for error in errors)
