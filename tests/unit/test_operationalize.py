import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _write_identity_secret_profiles(target_root: Path) -> None:
    config_dir = target_root / "config"
    config_dir.mkdir(parents=True)
    (config_dir / "identity.json").write_text(
        (
            '{\n'
            '  "schema_version": "0.1",\n'
            '  "selected_provider": "microsoft_entra_id",\n'
            '  "contains_credentials": false\n'
            '}\n'
        ),
        encoding="utf-8",
    )
    (config_dir / "secrets.json").write_text(
        (
            '{\n'
            '  "schema_version": "0.1",\n'
            '  "selected_manager": "azure_key_vault",\n'
            '  "contains_credentials": false\n'
            '}\n'
        ),
        encoding="utf-8",
    )


def _dry_run_env(tmp_path: Path, profile_root: Path) -> dict[str, str]:
    env = {
        key: value
        for key, value in os.environ.items()
        if key
        not in {
            "ANTHROPIC_API_KEY",
            "OPENAI_API_KEY",
            "GEMINI_API_KEY",
            "MYTHOS_API_KEY",
            "MACHINE_USER_TOKEN",
            "AI_DEV_MACHINE_USER_TOKEN",
            "GH_MACHINE_USER_TOKEN",
            "GITHUB_REPOSITORY",
        }
    }
    marker = tmp_path / "gh-invoked"
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    gh = fake_bin / "gh"
    gh.write_text(f"#!/usr/bin/env bash\ntouch {marker}\nexit 99\n", encoding="utf-8")
    gh.chmod(0o755)
    env["PATH"] = f"{fake_bin}{os.pathsep}{env.get('PATH', '')}"
    env["GH_INVOKED_MARKER"] = str(marker)
    env["AI_DEV_TEMPLATE_ROOT"] = str(profile_root)
    return env


def test_operationalize_dry_run_is_idempotent_and_makes_no_gh_calls(tmp_path: Path) -> None:
    profile_root = tmp_path / "profiled-repo"
    _write_identity_secret_profiles(profile_root)
    env = _dry_run_env(tmp_path, profile_root)
    command = ["bash", "scripts/operationalize.sh", "--dry-run", "--repo", "example/repo"]

    first = subprocess.run(command, cwd=ROOT, env=env, check=False, text=True, capture_output=True)
    second = subprocess.run(command, cwd=ROOT, env=env, check=False, text=True, capture_output=True)

    assert first.returncode == 0, first.stderr
    assert second.returncode == 0, second.stderr
    assert first.stdout == second.stdout
    assert "Dry-run complete. No gh commands were invoked." in first.stdout
    assert not Path(env["GH_INVOKED_MARKER"]).exists()


def test_operationalize_refuses_without_identity_secret_profiles(tmp_path: Path) -> None:
    profile_root = tmp_path / "unprofiled-repo"
    env = _dry_run_env(tmp_path, profile_root)

    result = subprocess.run(
        ["bash", "scripts/operationalize.sh", "--dry-run", "--repo", "example/repo"],
        cwd=ROOT,
        env=env,
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 2
    assert "run `make setup-identity` first" in result.stderr
    assert not Path(env["GH_INVOKED_MARKER"]).exists()


def test_operationalize_script_is_repo_scoped() -> None:
    text = (ROOT / "scripts" / "operationalize.sh").read_text(encoding="utf-8")

    assert 'gh secret set "$secret" --repo "$REPO"' in text
    assert "/repos/$REPO/" in text
    assert "--org" not in text
    assert "/orgs/" not in text
    assert "gh config set" not in text
