import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_root_mcp_config_has_no_default_external_servers():
    data = json.loads((ROOT / ".mcp.json").read_text(encoding="utf-8"))
    assert data == {"mcpServers": {}}


def test_vscode_mcp_config_has_no_default_external_servers():
    data = json.loads((ROOT / ".vscode" / "mcp.json").read_text(encoding="utf-8"))
    assert data == {"servers": {}}
