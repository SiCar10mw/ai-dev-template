"""Pluggable runtime secret providers for offline-first template checks."""

from __future__ import annotations

import json
import os
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol, cast

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG_PATH = ROOT / "config" / "secrets.example.json"
PROJECT_CONFIG_PATH = ROOT / "config" / "secrets.json"
DEFAULT_RESOLUTION_ORDER = ("env", "keyring")

KeyringGetter = Callable[[str, str], str | None]


class SecretProvider(Protocol):
    """Secret provider interface used by runtime code."""

    def get(self, name: str) -> str | None:
        """Return a secret value by logical name, or None when unavailable."""


class KeyVaultClient(Protocol):
    """Small Key Vault client protocol for tests and optional Azure SDK adapters."""

    def get_secret(self, name: str) -> object:
        """Return a secret object for name."""


def _require_name(name: str) -> str:
    normalized = name.strip()
    if not normalized:
        raise ValueError("secret name must not be empty")
    return normalized


def _nonempty(value: object) -> str | None:
    if isinstance(value, str) and value:
        return value
    return None


@dataclass(frozen=True)
class EnvProvider:
    """Resolve secrets from the process environment.

    This provider exists for platform-injected runtime environments and offline tests. Real values still must not be
    stored in tracked files or committed dotenv files.
    """

    environ: Mapping[str, str] | None = None

    def get(self, name: str) -> str | None:
        """Return a nonempty environment variable value."""
        source = self.environ if self.environ is not None else os.environ
        return _nonempty(source.get(_require_name(name)))


@dataclass(frozen=True)
class KeyringProvider:
    """Resolve local-development secrets from an OS keyring."""

    service_name: str = "ai-dev-template"
    getter: KeyringGetter | None = None

    def get(self, name: str) -> str | None:
        """Return a nonempty keyring value without requiring keyring in CI."""
        getter = self.getter or _default_keyring_getter
        try:
            return _nonempty(getter(self.service_name, _require_name(name)))
        except Exception:
            return None


@dataclass
class KeyVaultProvider:
    """Azure Key Vault adapter selected only by explicit configuration."""

    vault_url: str | None = None
    client: KeyVaultClient | None = None
    secret_name_map: Mapping[str, str] | None = None
    credential: object | None = None

    def get(self, name: str) -> str | None:
        """Return a nonempty Key Vault secret value."""
        secret = self._client().get_secret(self._secret_name(name))
        return _nonempty(getattr(secret, "value", secret))

    def _secret_name(self, name: str) -> str:
        logical_name = _require_name(name)
        if self.secret_name_map is None:
            return logical_name
        return _require_name(self.secret_name_map.get(logical_name, logical_name))

    def _client(self) -> KeyVaultClient:
        if self.client is not None:
            return self.client
        if not self.vault_url:
            raise RuntimeError("KeyVaultProvider requires vault_url or an injected client")
        try:
            from azure.identity import DefaultAzureCredential
            from azure.keyvault.secrets import SecretClient
        except ImportError as exc:
            raise RuntimeError(
                "KeyVaultProvider requires azure-identity and azure-keyvault-secrets when no client is injected"
            ) from exc
        credential = self.credential if self.credential is not None else DefaultAzureCredential()
        self.client = SecretClient(vault_url=self.vault_url, credential=credential)
        return cast(KeyVaultClient, self.client)


@dataclass(frozen=True)
class ChainProvider:
    """Resolve a secret from the first provider that has a value."""

    providers: Sequence[SecretProvider]

    def get(self, name: str) -> str | None:
        """Return the first nonempty provider result."""
        _require_name(name)
        for provider in self.providers:
            value = provider.get(name)
            if value:
                return value
        return None


def _default_keyring_getter(service_name: str, name: str) -> str | None:
    try:
        import keyring
    except ImportError:
        return None
    return cast(str | None, keyring.get_password(service_name, name))


def load_secret_config(path: Path | None = None) -> dict[str, Any]:
    """Load secret-provider config, defaulting to the project config or example config."""
    active_path = path or (PROJECT_CONFIG_PATH if PROJECT_CONFIG_PATH.exists() else DEFAULT_CONFIG_PATH)
    if not active_path.exists():
        return {}
    data = json.loads(active_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("secret provider config must be a JSON object")
    return data


def build_secret_provider(
    config: Mapping[str, Any] | None = None,
    *,
    environ: Mapping[str, str] | None = None,
    keyring_getter: KeyringGetter | None = None,
    keyvault_client: KeyVaultClient | None = None,
) -> SecretProvider:
    """Build the configured provider chain without making network calls."""
    active_config = config or {}
    providers_config = active_config.get("providers", {})
    if not isinstance(providers_config, Mapping):
        providers_config = {}
    raw_order = active_config.get("resolution_order", DEFAULT_RESOLUTION_ORDER)
    if not isinstance(raw_order, list | tuple):
        raise ValueError("secret provider resolution_order must be a list")

    providers: list[SecretProvider] = []
    for provider_name in raw_order:
        name = str(provider_name).strip().lower()
        settings = providers_config.get(name, {})
        if not isinstance(settings, Mapping):
            settings = {}
        if settings.get("enabled", True) is False:
            continue
        if name == "env":
            providers.append(EnvProvider(environ))
        elif name == "keyring":
            service_name = str(settings.get("service_name", "ai-dev-template"))
            providers.append(KeyringProvider(service_name=service_name, getter=keyring_getter))
        elif name == "azure_key_vault":
            raw_map = settings.get("secret_name_map", {})
            secret_name_map = raw_map if isinstance(raw_map, Mapping) else {}
            providers.append(
                KeyVaultProvider(
                    vault_url=_nonempty(settings.get("vault_url")),
                    client=keyvault_client,
                    secret_name_map={str(key): str(value) for key, value in secret_name_map.items()},
                )
            )
        else:
            raise ValueError(f"unsupported secret provider: {provider_name}")

    if not providers:
        providers = [EnvProvider(environ), KeyringProvider(getter=keyring_getter)]
    return ChainProvider(providers)


def get_secret(
    name: str,
    *,
    provider: SecretProvider | None = None,
    config_path: Path | None = None,
) -> str | None:
    """Resolve a secret by logical name through the configured provider interface."""
    active_provider = provider or build_secret_provider(load_secret_config(config_path))
    return active_provider.get(name)
