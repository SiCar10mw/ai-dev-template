import json
import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _copy_config_examples(target_root: Path) -> None:
    config_dir = target_root / "config"
    config_dir.mkdir(parents=True)
    for name in ("identity.example.json", "secrets.example.json"):
        shutil.copy2(ROOT / "config" / name, config_dir / name)


def _setup_env(target_root: Path, tmp_path: Path) -> tuple[dict[str, str], Path]:
    env = os.environ.copy()
    marker = tmp_path / "cloud-invoked"
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    for command in ("az", "aws", "gcloud", "vault", "op", "doppler"):
        tool = fake_bin / command
        tool.write_text(f"#!/usr/bin/env bash\ntouch {marker}\nexit 99\n", encoding="utf-8")
        tool.chmod(0o755)
    env["PATH"] = f"{fake_bin}{os.pathsep}{env.get('PATH', '')}"
    env["AI_DEV_TEMPLATE_ROOT"] = str(target_root)
    return env, marker


def _run_setup(target_root: Path, tmp_path: Path, *args: str) -> tuple[subprocess.CompletedProcess[str], Path]:
    _copy_config_examples(target_root)
    env, marker = _setup_env(target_root, tmp_path)
    result = subprocess.run(
        ["bash", "scripts/setup_identity.sh", *args],
        cwd=ROOT,
        env=env,
        check=False,
        text=True,
        capture_output=True,
    )
    return result, marker


def test_setup_identity_non_interactive_dry_run_writes_profiles_and_prints_next_steps(tmp_path: Path) -> None:
    target_root = tmp_path / "repo"
    result, marker = _run_setup(
        target_root,
        tmp_path,
        "--non-interactive",
        "--dry-run",
        "--idp",
        "entra",
        "--secrets",
        "azure-key-vault",
    )

    assert result.returncode == 0, result.stderr
    identity = json.loads((target_root / "config" / "identity.json").read_text(encoding="utf-8"))
    secrets = json.loads((target_root / "config" / "secrets.json").read_text(encoding="utf-8"))
    assert identity["selected_provider"] == "microsoft_entra_id"
    assert secrets["selected_manager"] == "azure_key_vault"
    assert "az ad app create" in result.stdout
    assert "az keyvault create" in result.stdout
    assert "No cloud calls were made" in result.stdout
    assert not marker.exists()


def test_setup_identity_non_interactive_requires_both_choices(tmp_path: Path) -> None:
    target_root = tmp_path / "repo"
    result, marker = _run_setup(
        target_root,
        tmp_path,
        "--non-interactive",
        "--dry-run",
        "--idp",
        "entra",
    )

    assert result.returncode == 2
    assert "requires --idp and --secrets" in result.stderr
    assert not (target_root / "config" / "identity.json").exists()
    assert not marker.exists()


def test_setup_identity_rejects_invalid_choice_without_writing_profiles(tmp_path: Path) -> None:
    target_root = tmp_path / "repo"
    result, marker = _run_setup(
        target_root,
        tmp_path,
        "--non-interactive",
        "--dry-run",
        "--idp",
        "not-a-provider",
        "--secrets",
        "azure-key-vault",
    )

    assert result.returncode == 2
    assert "invalid identity provider" in result.stderr
    assert not (target_root / "config" / "identity.json").exists()
    assert not marker.exists()
