---
name: example-skill
description: Emits a deterministic canonical verdict JSON object from a status string.
when_to_use: Use when an agent needs a tiny, testable example of metadata-selected CLI capability.
---

# Example Skill

This skill demonstrates progressive discovery.

An agent should read the metadata first. If the task needs deterministic verdict JSON, the agent may then load this full file and call the CLI.

## Command

```bash
python -m skills.example_skill.example_skill --status pass
```

## Behavior

- Accepts `pass`, `fail`, or `partial`.
- Emits canonical JSON with sorted keys.
- Does not call the network.
- Does not read secrets.

