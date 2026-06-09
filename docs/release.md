# Release Discipline

Release status is determined by deterministic gates and human approval, not by an LLM.

## Required Before Release

- `make check` passes.
- Required branch protections pass.
- Gitleaks and mypy gates pass.
- Gitleaks full-history scan passes.
- Generated artifact drift tripwire passes.
- Documentation impact is complete.
- Security-sensitive changes have independent review.
- Human approval is recorded.
- Release notes or `CHANGELOG.md` are updated.

## Recommended Versioning

Use semantic versioning unless the project has a stronger existing convention.

## Release Notes

Release notes should distinguish:

- shipped behavior
- changed configuration
- migration steps
- known limitations
- future target state
