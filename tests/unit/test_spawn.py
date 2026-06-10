import json
import subprocess
from pathlib import Path
from typing import Any

import pytest

import ai_dev_template.spawn as spawn_module
from ai_dev_template.spawn import ModelCliUnavailableError, spawn, spawn_role


def _routing_config(path: Path, preferred_order: list[str]) -> None:
    path.write_text(
        json.dumps(
            {
                "first_class_tools": [
                    {"profile": "anthropic_claude", "provider": "anthropic", "model_family": "claude"},
                    {"profile": "google_gemini", "provider": "google", "model_family": "gemini"},
                    {"profile": "openai_codex_gpt", "provider": "openai", "model_family": "gpt-codex"},
                ],
                "model_roles": {
                    "primary_coding": {
                        "preferred_order": preferred_order,
                    }
                },
            }
        ),
        encoding="utf-8",
    )


@pytest.mark.parametrize(
    ("model", "expected"),
    [
        ("claude", ["claude", "-p", "do the thing"]),
        ("gemini", ["gemini", "-p", "do the thing"]),
        ("codex", ["codex", "exec", "do the thing"]),
    ],
)
def test_spawn_routes_each_model_to_cli_argv(model: str, expected: list[str]) -> None:
    calls: list[dict[str, Any]] = []

    def runner(argv: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        calls.append({"argv": argv, **kwargs})
        return subprocess.CompletedProcess(argv, 0, stdout=f"{model} stdout", stderr="")

    assert spawn(model, "do the thing", runner=runner) == f"{model} stdout"

    assert calls == [
        {
            "argv": expected,
            "capture_output": True,
            "check": False,
            "shell": False,
            "text": True,
            "timeout": 300,
        }
    ]
    assert isinstance(calls[0]["argv"], list)


def test_spawn_rejects_unknown_model() -> None:
    with pytest.raises(ValueError, match="unknown model 'llama'.*claude.*gemini.*codex"):
        spawn("llama", "do the thing", runner=lambda *_args, **_kwargs: None)


def test_spawn_missing_cli_error_names_model_and_operator_action() -> None:
    def runner(_argv: list[str], **_kwargs: Any) -> subprocess.CompletedProcess[str]:
        raise FileNotFoundError("gemini")

    with pytest.raises(ModelCliUnavailableError, match="gemini.*Install.*GEMINI_API_KEY"):
        spawn("gemini", "do the thing", runner=runner)


def test_spawn_role_uses_first_available_model(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    routing = tmp_path / "model-routing.example.json"
    _routing_config(routing, ["anthropic_claude", "google_gemini", "openai_codex_gpt"])
    monkeypatch.setattr(spawn_module, "DEFAULT_ROUTING_PATH", routing)
    monkeypatch.setattr(spawn_module, "PROJECT_ROUTING_PATH", tmp_path / "missing-model-routing.json")
    calls: list[list[str]] = []

    def runner(argv: list[str], **_kwargs: Any) -> subprocess.CompletedProcess[str]:
        calls.append(argv)
        return subprocess.CompletedProcess(argv, 0, stdout="claude stdout", stderr="")

    assert spawn_role("primary_coding", "do the thing", runner=runner) == "claude stdout"
    assert calls == [["claude", "-p", "do the thing"]]


def test_spawn_role_falls_through_when_cli_is_absent(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    routing = tmp_path / "model-routing.example.json"
    _routing_config(routing, ["anthropic_claude", "google_gemini", "openai_codex_gpt"])
    monkeypatch.setattr(spawn_module, "DEFAULT_ROUTING_PATH", routing)
    monkeypatch.setattr(spawn_module, "PROJECT_ROUTING_PATH", tmp_path / "missing-model-routing.json")
    calls: list[list[str]] = []

    def runner(argv: list[str], **_kwargs: Any) -> subprocess.CompletedProcess[str]:
        calls.append(argv)
        if argv[0] == "claude":
            raise FileNotFoundError("claude")
        return subprocess.CompletedProcess(argv, 0, stdout="gemini stdout", stderr="")

    assert spawn_role("primary_coding", "do the thing", runner=runner) == "gemini stdout"
    assert calls == [["claude", "-p", "do the thing"], ["gemini", "-p", "do the thing"]]


def test_spawn_role_raises_when_no_preferred_cli_is_available(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    routing = tmp_path / "model-routing.example.json"
    _routing_config(routing, ["anthropic_claude", "google_gemini"])
    monkeypatch.setattr(spawn_module, "DEFAULT_ROUTING_PATH", routing)
    monkeypatch.setattr(spawn_module, "PROJECT_ROUTING_PATH", tmp_path / "missing-model-routing.json")

    def runner(argv: list[str], **_kwargs: Any) -> subprocess.CompletedProcess[str]:
        raise FileNotFoundError(argv[0])

    with pytest.raises(ModelCliUnavailableError, match="No available CLI for role 'primary_coding'.*claude.*gemini"):
        spawn_role("primary_coding", "do the thing", runner=runner)
