from skills.example_skill.example_skill import main


def test_example_skill_cli_emits_canonical_json(capsys) -> None:
    exit_code = main(["--status", "pass"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out.strip() == '{"passed":true,"reason":"positive evidence","status":"pass"}'

