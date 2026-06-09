#!/usr/bin/env bash
set -euo pipefail

python scripts/check_template_conformance.py
python scripts/check_principle_tripwires.py
python scripts/check_profile_boundary.py
python scripts/check_docs_impact.py
python scripts/check_docs_site.py
python scripts/check_generated_artifacts.py
python scripts/check_no_secrets.py
pre-commit run gitleaks --all-files --config .pre-commit-config.yaml
mypy ai_dev_template scripts skills
ruff check .
pytest --cov=ai_dev_template --cov=skills --cov=scripts --cov-report=term-missing
bandit -r ai_dev_template skills scripts -lll -ii
pip-audit --requirement requirements.txt --disable-pip --no-deps
