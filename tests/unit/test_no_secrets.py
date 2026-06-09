from scripts.check_no_secrets import scan_file


def test_secret_scan_flags_private_key(tmp_path):
    path = tmp_path / "key.txt"
    marker = "-----BEGIN " + "PRIVATE KEY-----"
    path.write_text(f"{marker}\nvalue\n", encoding="utf-8")
    assert scan_file(path)


def test_secret_scan_allows_placeholder_text(tmp_path):
    path = tmp_path / "safe.txt"
    path.write_text("Set OPENAI_API_KEY in the environment.", encoding="utf-8")
    assert scan_file(path) == []
