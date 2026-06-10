"""Per-model CLI dispatch adapters for the agent fleet."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROUTING_PATH = ROOT / "config" / "model-routing.example.json"
PROJECT_ROUTING_PATH = ROOT / "config" / "model-routing.json"

Runner = Callable[..., subprocess.CompletedProcess[str]]

ADAPTER_COMMANDS: dict[str, tuple[str, ...]] = {
    "claude": ("claude", "-p"),
    "gemini": ("gemini", "-p"),
    "codex": ("codex", "exec"),
}

PROFILE_ADAPTERS = {
    "anthropic_claude": "claude",
    "google_gemini": "gemini",
    "openai_codex_gpt": "codex",
}

INSTALL_AUTH_HINTS = {
    "claude": "Install Claude Code CLI and sign in with the operator's Claude account.",
    "gemini": (
        "Install Gemini CLI and configure a Google/GEMINI API key for the `gemini` CLI, "
        "for example GEMINI_API_KEY from the approved secret source."
    ),
    "codex": "Install Codex CLI and authenticate with OpenAI/ChatGPT.",
}


class ModelCliUnavailableError(RuntimeError):
    """Raised when no suitable model CLI is available on PATH."""


class ModelDispatchError(RuntimeError):
    """Raised when a model CLI is present but the dispatch fails."""


def spawn(model: str, task: str, *, timeout: int = 300, runner: Runner = subprocess.run) -> str:
    """Run a single task through the requested model CLI and return stdout."""
    normalized = model.strip().lower()
    if normalized not in ADAPTER_COMMANDS:
        valid = ", ".join(ADAPTER_COMMANDS)
        raise ValueError(f"unknown model {model!r}; expected one of: {valid}")

    argv = [*ADAPTER_COMMANDS[normalized], task]
    try:
        result = runner(
            argv,
            capture_output=True,
            check=False,
            shell=False,
            text=True,
            timeout=timeout,
        )
    except FileNotFoundError as exc:
        raise ModelCliUnavailableError(_missing_cli_message(normalized)) from exc

    if result.returncode != 0:
        raise ModelDispatchError(
            f"{normalized} CLI exited with status {result.returncode}; check CLI authentication and task permissions."
        )
    return result.stdout or ""


def spawn_role(role: str, task: str, *, runner: Runner = subprocess.run) -> str:
    """Dispatch a task to the first available CLI for a configured model role."""
    config = _load_routing_config()
    preferred_order = _preferred_order(config, role)
    profile_adapters = _profile_adapters(config)
    attempts: list[str] = []

    for profile in preferred_order:
        model = profile_adapters.get(profile)
        if model is None:
            attempts.append(f"{profile} (no CLI adapter)")
            continue
        try:
            return spawn(model, task, runner=runner)
        except ModelCliUnavailableError as exc:
            attempts.append(f"{profile}->{model} ({exc})")

    tried = ", ".join(attempts) if attempts else ", ".join(preferred_order)
    raise ModelCliUnavailableError(
        f"No available CLI for role {role!r}. Tried: {tried}. "
        "Install and authenticate at least one preferred model CLI."
    )


def _missing_cli_message(model: str) -> str:
    return f"{model} CLI is not installed or not on PATH. {INSTALL_AUTH_HINTS[model]}"


def _load_routing_config() -> dict[str, Any]:
    path = PROJECT_ROUTING_PATH if PROJECT_ROUTING_PATH.exists() else DEFAULT_ROUTING_PATH
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"model routing config must be a JSON object: {path}")
    return data


def _preferred_order(config: dict[str, Any], role: str) -> list[str]:
    roles = config.get("model_roles", {})
    if not isinstance(roles, dict):
        raise ValueError("model routing model_roles must be a JSON object")
    role_config = roles.get(role)
    if not isinstance(role_config, dict):
        raise ValueError(f"model routing role not found: {role!r}")
    order = role_config.get("preferred_order")
    if not isinstance(order, list) or not order:
        raise ValueError(f"model routing role {role!r} must define a non-empty preferred_order list")
    preferred: list[str] = []
    for profile in order:
        if not isinstance(profile, str) or not profile.strip():
            raise ValueError(f"model routing role {role!r} preferred_order entries must be non-empty strings")
        preferred.append(profile.strip())
    return preferred


def _profile_adapters(config: dict[str, Any]) -> dict[str, str]:
    adapters = {model: model for model in ADAPTER_COMMANDS}
    adapters.update(PROFILE_ADAPTERS)
    for tool in config.get("first_class_tools", []):
        if not isinstance(tool, dict):
            continue
        profile = tool.get("profile")
        if not isinstance(profile, str) or not profile.strip():
            continue
        adapter = _adapter_from_tool(tool)
        if adapter is not None:
            adapters[profile.strip()] = adapter
    return adapters


def _adapter_from_tool(tool: dict[str, Any]) -> str | None:
    profile = str(tool.get("profile", "")).lower()
    provider = str(tool.get("provider", "")).lower()
    family = str(tool.get("model_family", "")).lower()
    display_tool = str(tool.get("tool", "")).lower()
    haystack = " ".join((profile, provider, family, display_tool))
    if provider == "anthropic" and "claude" in haystack:
        return "claude"
    if provider == "google" or "gemini" in haystack:
        return "gemini"
    if provider == "openai" or "codex" in haystack or family.startswith("gpt"):
        return "codex"
    return None


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point for single-dispatch model execution."""
    parser = argparse.ArgumentParser(description=__doc__)
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--model", choices=tuple(ADAPTER_COMMANDS))
    target.add_argument("--role")
    parser.add_argument("--task", required=True)
    args = parser.parse_args(argv)

    try:
        output = spawn(args.model, args.task) if args.model else spawn_role(args.role, args.task)
    except (ModelCliUnavailableError, ModelDispatchError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
