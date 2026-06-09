.PHONY: check conformance docs-impact docs-site-check generated-check profile-boundary corporate-profile-check owasp-llm no-secrets type-check lint test sast ai-sast ai-sast-verify-fix dependency-audit setup-identity operationalize documents reference-docx project-brief-deck docs-site-build

check:
	./scripts/ci_check.sh

conformance:
	python scripts/check_template_conformance.py
	python scripts/check_principle_tripwires.py
	python scripts/check_profile_boundary.py

docs-impact:
	python scripts/check_docs_impact.py

docs-site-check:
	python scripts/check_docs_site.py

generated-check:
	python scripts/check_generated_artifacts.py

profile-boundary:
	python scripts/check_profile_boundary.py

corporate-profile-check:
	AI_DEV_PROFILE=corporate python scripts/check_profile_boundary.py

owasp-llm:
	python scripts/check_owasp_llm.py

no-secrets:
	python scripts/check_no_secrets.py
	pre-commit run gitleaks --all-files --config .pre-commit-config.yaml

type-check:
	mypy ai_dev_template scripts skills

lint:
	ruff check .

test:
	pytest --cov=ai_dev_template --cov=skills --cov=scripts --cov-report=term-missing

sast:
	bandit -r ai_dev_template skills scripts -lll -ii

ai-sast:
	python scripts/check_ai_sast.py --scanner mock

ai-sast-verify-fix:
	python scripts/verify_fix.py --self-test

dependency-audit:
	pip-audit --requirement requirements.txt --disable-pip --no-deps

setup-identity:
	bash scripts/setup_identity.sh

operationalize:
	bash scripts/operationalize.sh

documents: reference-docx project-brief-deck

reference-docx:
	python scripts/gen_reference_docx.py

project-brief-deck:
	python scripts/gen_sample_deck.py

docs-site-build:
	cd docs-site && npm ci && npm run build
