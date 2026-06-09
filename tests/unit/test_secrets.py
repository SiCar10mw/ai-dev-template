from pathlib import Path

from ai_dev_template.secrets import (
    ChainProvider,
    EnvProvider,
    KeyringProvider,
    KeyVaultProvider,
    get_secret,
)
from scripts.check_template_conformance import (
    check_env_example_shapes,
    check_secret_access_patterns,
    check_secrets_config,
)

ROOT = Path(__file__).resolve().parents[2]


class _MockKeyVaultSecret:
    def __init__(self, value: str | None) -> None:
        self.value = value


class _MockKeyVaultClient:
    def __init__(self, values: dict[str, str | None]) -> None:
        self.values = values
        self.names: list[str] = []

    def get_secret(self, name: str) -> _MockKeyVaultSecret:
        self.names.append(name)
        return _MockKeyVaultSecret(self.values.get(name))


def test_env_provider_returns_nonempty_runtime_value() -> None:
    provider = EnvProvider({"OPENAI_API_KEY": "runtime-value", "EMPTY_SECRET": ""})

    assert provider.get("OPENAI_API_KEY") == "runtime-value"
    assert provider.get("EMPTY_SECRET") is None
    assert provider.get("MISSING_SECRET") is None


def test_keyring_provider_uses_injected_getter_for_offline_local_resolution() -> None:
    calls: list[tuple[str, str]] = []

    def getter(service_name: str, name: str) -> str | None:
        calls.append((service_name, name))
        return "from-keyring" if name == "OPENAI_API_KEY" else None

    provider = KeyringProvider(service_name="ai-dev-template-test", getter=getter)

    assert provider.get("OPENAI_API_KEY") == "from-keyring"
    assert provider.get("MISSING_SECRET") is None
    assert calls == [
        ("ai-dev-template-test", "OPENAI_API_KEY"),
        ("ai-dev-template-test", "MISSING_SECRET"),
    ]


def test_chain_provider_falls_back_from_env_to_keyring() -> None:
    provider = ChainProvider(
        [
            EnvProvider({"OPENAI_API_KEY": ""}),
            KeyringProvider(getter=lambda _service_name, name: "fallback-value" if name == "OPENAI_API_KEY" else None),
        ]
    )

    assert provider.get("OPENAI_API_KEY") == "fallback-value"


def test_key_vault_provider_uses_mocked_client_and_name_map_without_network() -> None:
    client = _MockKeyVaultClient({"openai-api-key": "from-key-vault"})
    provider = KeyVaultProvider(client=client, secret_name_map={"OPENAI_API_KEY": "openai-api-key"})

    assert provider.get("OPENAI_API_KEY") == "from-key-vault"
    assert client.names == ["openai-api-key"]


def test_get_secret_uses_explicit_provider_without_hardcoded_value() -> None:
    provider = EnvProvider({"MACHINE_USER_TOKEN": "runtime-token"})

    assert get_secret("MACHINE_USER_TOKEN", provider=provider) == "runtime-token"


def test_current_secret_conformance_tripwires_pass() -> None:
    assert check_env_example_shapes(ROOT) == []
    assert check_secrets_config(ROOT) == []
    assert check_secret_access_patterns(ROOT) == []


def test_env_example_tripwire_rejects_real_secret_values(tmp_path: Path) -> None:
    (tmp_path / ".env.example").write_text(
        "OPENAI_API_KEY=" + "sk-" + ("A" * 32) + "\n",
        encoding="utf-8",
    )

    assert any("placeholder" in error for error in check_env_example_shapes(tmp_path))


def test_secret_access_tripwire_rejects_direct_secret_env_reads(tmp_path: Path) -> None:
    package = tmp_path / "ai_dev_template"
    package.mkdir()
    (package / "unsafe.py").write_text(
        'import os\nTOKEN = os.environ.get("MACHINE_USER_TOKEN")\n',
        encoding="utf-8",
    )

    assert any("SecretProvider" in error for error in check_secret_access_patterns(tmp_path))
