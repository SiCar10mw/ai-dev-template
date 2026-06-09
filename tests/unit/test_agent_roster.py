import shutil
from pathlib import Path

from scripts.check_agent_roster import check_agent_roster
from scripts.gen_agent_views import diff_generated_views, write_views

ROOT = Path(__file__).resolve().parents[2]


def test_agent_roster_source_and_generated_views_are_current() -> None:
    assert check_agent_roster(ROOT) == []


def test_agent_roster_tripwire_detects_stale_generated_view(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    shutil.copytree(ROOT / "agents", root / "agents")
    write_views(root)
    (root / "AGENTS.md").write_text("stale\n", encoding="utf-8")

    errors = diff_generated_views(root)

    assert any("AGENTS.md" in error for error in errors)


def test_codex_view_embeds_full_persona_behavior() -> None:
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

    assert "## Embedded Personas" in agents
    assert "### Backlog Worker" in agents
    assert "You are the worker for the Symphony backlog loop." in agents
