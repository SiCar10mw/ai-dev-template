# Safety Habits

## Blast-Radius Check Before Edits

Before editing, identify:

- Files that will change.
- Tests that should fail or pass.
- Generated artifacts affected.
- Documentation affected.
- External systems touched.
- Owners or reviewers required.

Write down assumptions in the spec, task, or pull request.

## Look-Before-You-Delete

Before deleting:

1. Inspect the file.
2. Check references with search.
3. Check git status.
4. Determine whether the file is generated or source.
5. Confirm tests and docs that depend on it.
6. Ask before deleting externally visible, production, or shared artifacts.

## External Writes

External writes are blocked by default. Prepare the change and stop for explicit human approval.

