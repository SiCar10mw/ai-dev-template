# Skills Convention

Skills implement progressive discovery for agents.

Progressive discovery means an agent first reads small metadata for available capabilities, selects the relevant capability, and only then loads the full instructions for that skill.

This is distinct from progressive loading, which is a UI pattern where an interface paints cached summary content immediately and streams detail behind a spinner.

## Skill Layout

```text
skills/
└── example_skill/
    ├── SKILL.md
    └── example_skill.py
```

## Required Metadata

Each `SKILL.md` must start with metadata:

```yaml
---
name: example-skill
description: One-line description.
when_to_use: Use when ...
---
```

## Rules

- Keep metadata short and searchable.
- Keep full instructions in the selected skill only.
- Prefer small CLI tools that can be tested.
- Skills must not require secrets for default tests.

