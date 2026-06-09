import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def run_bootstrap(tmp_path: Path, project_name: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["BOOTSTRAP_TEST_SKIP_INSTALL"] = "1"
    env["BOOTSTRAP_TEST_SKIP_CHECK"] = "1"
    answers = "\n".join(
        (
            project_name,
            str(tmp_path),
            "Machine User",
            "machine-user@example.invalid",
            "1",
            "1",
            "",
        )
    )
    return subprocess.run(
        [str(ROOT / "bootstrap.sh")],
        cwd=ROOT,
        input=answers,
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )


def git_stdout(target: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(target), *args],
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout.strip()


def test_bootstrap_excludes_template_git_history_and_ignored_artifacts(tmp_path: Path) -> None:
    result = run_bootstrap(tmp_path, "Bootstrap Safe Copy")

    assert result.returncode == 0, result.stderr
    target = tmp_path / "bootstrap-safe-copy"
    assert target.is_dir()
    assert (target / ".git").is_dir()
    assert (target / ".venv").is_dir()

    assert git_stdout(target, "branch", "--show-current") == "main"
    assert git_stdout(target, "remote") == ""
    assert git_stdout(target, "rev-list", "--all", "--count") == "0"
    assert git_stdout(target, "config", "--local", "user.name") == "Machine User"
    assert git_stdout(target, "config", "--local", "user.email") == "machine-user@example.invalid"
    assert git_stdout(target, "config", "--local", "core.hooksPath") == ".githooks"
    assert (target / "config" / "identity.json").is_file()
    assert (target / "config" / "secrets.json").is_file()

    assert not (target / ".coverage").exists()
    assert not (target / ".mypy_cache").exists()
    assert not (target / ".pytest_cache").exists()
    assert not (target / ".ruff_cache").exists()
    assert not (target / "ai_dev_template.egg-info").exists()
    assert not (target / "docs-site" / "build").exists()
    assert "--global" not in (ROOT / "bootstrap.sh").read_text(encoding="utf-8")


def test_bootstrap_refuses_existing_target_dir(tmp_path: Path) -> None:
    target = tmp_path / "existing-project"
    target.mkdir()
    marker = target / "marker.txt"
    marker.write_text("do not overwrite\n", encoding="utf-8")

    result = run_bootstrap(tmp_path, "Existing Project")

    assert result.returncode != 0
    assert "target directory already exists" in result.stderr
    assert marker.read_text(encoding="utf-8") == "do not overwrite\n"
