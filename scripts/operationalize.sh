#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${AI_DEV_TEMPLATE_ROOT:-$(cd "$SCRIPT_DIR/.." && pwd)}"
CONFIG_DIR="$REPO_ROOT/config"

DRY_RUN=0
REPO="${GITHUB_REPOSITORY:-}"
BRANCH="${AI_DEV_DEFAULT_BRANCH:-main}"
RULESET_NAME="${AI_DEV_RULESET_NAME:-ai-dev-template merge queue}"
REQUIRED_STATUS_CHECKS="${AI_DEV_REQUIRED_STATUS_CHECKS:-make check,OWASP LLM coverage gate,gitleaks secret scan,AI-SAST diff gate,conformance audit}"

WORKFLOWS=(
  "ci.yml"
  "codeql.yml"
  "sbom.yml"
  "dependency-review.yml"
  "secret-scan.yml"
  "owasp-llm.yml"
  "ai-sast-pr.yml"
  "ai-sast-scheduled.yml"
  "conformance-audit.yml"
)

SECRET_NAMES=(
  "ANTHROPIC_API_KEY"
  "OPENAI_API_KEY"
  "GEMINI_API_KEY"
  "MYTHOS_API_KEY"
  "MACHINE_USER_TOKEN"
)

usage() {
  cat <<'EOF'
Usage: scripts/operationalize.sh [--dry-run] [--repo OWNER/REPO] [--branch BRANCH]

Repo-scoped GitHub operationalization for this template. The script prints a plan first and prompts for confirmation
before outward writes. It assumes `gh auth login` has already been run for the target repository.

Before operationalization, run `make setup-identity` to choose the repo-local identity and secrets profile.

Options:
  --dry-run          Print the plan without invoking gh or making API calls.
  --repo OWNER/REPO  Target repository. Defaults to GITHUB_REPOSITORY or origin remote.
  --branch BRANCH    Protected branch. Defaults to main.
  -h, --help         Show this help.
EOF
}

detect_repo_from_origin() {
  local remote
  remote="$(git config --get remote.origin.url 2>/dev/null || true)"
  if [[ "$remote" =~ ^git@github.com:([^/]+)/([^/]+)(\.git)?$ ]]; then
    printf '%s/%s\n' "${BASH_REMATCH[1]}" "${BASH_REMATCH[2]%.git}"
    return 0
  fi
  if [[ "$remote" =~ ^https://github.com/([^/]+)/([^/]+)(\.git)?$ ]]; then
    printf '%s/%s\n' "${BASH_REMATCH[1]}" "${BASH_REMATCH[2]%.git}"
    return 0
  fi
  return 1
}

require_identity_secrets_profile() {
  local identity_config="$CONFIG_DIR/identity.json"
  local secrets_config="$CONFIG_DIR/secrets.json"
  if [[ ! -s "$identity_config" || ! -s "$secrets_config" ]]; then
    cat >&2 <<EOF
FAIL: identity/secrets profile has not been chosen.
Expected:
- $identity_config
- $secrets_config

run \`make setup-identity\` first.
EOF
    exit 2
  fi

  AI_DEV_IDENTITY_CONFIG="$identity_config" AI_DEV_SECRETS_CONFIG="$secrets_config" python3 - <<'PY'
import json
import os
import sys
from pathlib import Path

checks = (
    ("AI_DEV_IDENTITY_CONFIG", "selected_provider", "identity"),
    ("AI_DEV_SECRETS_CONFIG", "selected_manager", "secrets"),
)
for env_name, selected_key, label in checks:
    path = Path(os.environ[env_name])
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAIL: invalid {label} profile {path}: {exc}", file=sys.stderr)
        raise SystemExit(2)
    if not isinstance(data, dict) or not str(data.get(selected_key, "")).strip():
        print(f"FAIL: {label} profile {path} must contain {selected_key}; run `make setup-identity` first.", file=sys.stderr)
        raise SystemExit(2)
    if data.get("contains_credentials") is True:
        print(f"FAIL: {label} profile {path} must not contain credentials.", file=sys.stderr)
        raise SystemExit(2)
PY
}

env_has_value() {
  local name="$1"
  [[ -n "${!name:-}" ]]
}

machine_token_env_has_value() {
  env_has_value "MACHINE_USER_TOKEN" || env_has_value "AI_DEV_MACHINE_USER_TOKEN" || env_has_value "GH_MACHINE_USER_TOKEN"
}

plan_secret_source() {
  local name="$1"
  if [[ "$name" == "MACHINE_USER_TOKEN" ]]; then
    if machine_token_env_has_value; then
      printf 'env'
    else
      printf 'env absent; keyring checked only after confirmation'
    fi
    return 0
  fi

  if env_has_value "$name"; then
    printf 'env'
  else
    printf 'env absent; keyring checked only after confirmation'
  fi
}

lookup_secret_value() {
  local name="$1"
  local value=""

  if [[ "$name" == "MACHINE_USER_TOKEN" ]]; then
    for candidate in "MACHINE_USER_TOKEN" "AI_DEV_MACHINE_USER_TOKEN" "GH_MACHINE_USER_TOKEN"; do
      if env_has_value "$candidate"; then
        printf '%s' "${!candidate}"
        return 0
      fi
    done
  elif env_has_value "$name"; then
    printf '%s' "${!name}"
    return 0
  fi

  if command -v keyring >/dev/null 2>&1; then
    value="$(keyring get ai-dev-template "$name" 2>/dev/null || true)"
    if [[ -n "$value" ]]; then
      printf '%s' "$value"
      return 0
    fi
  fi

  if command -v security >/dev/null 2>&1; then
    value="$(security find-generic-password -s "ai-dev-template/$name" -w 2>/dev/null || true)"
    if [[ -n "$value" ]]; then
      printf '%s' "$value"
      return 0
    fi
    value="$(security find-generic-password -s "$name" -w 2>/dev/null || true)"
    if [[ -n "$value" ]]; then
      printf '%s' "$value"
      return 0
    fi
  fi

  return 1
}

print_plan() {
  cat <<EOF
Plan: repo-scoped GitHub operationalization

Target repository: $REPO
Protected branch:  $BRANCH
Dry run:           $DRY_RUN

Repo-scoped writes after confirmation:
- Set GitHub Actions repository secrets when local env/keyring values are present.
- Apply branch protection on refs/heads/$BRANCH with required status checks.
- Create or update a repository ruleset named "$RULESET_NAME" to enable the merge queue.
- Enable and confirm repository workflows.

Required status checks:
EOF
  local check
  IFS=',' read -r -a checks <<<"$REQUIRED_STATUS_CHECKS"
  for check in "${checks[@]}"; do
    check="${check#"${check%%[![:space:]]*}"}"
    check="${check%"${check##*[![:space:]]}"}"
    [[ -n "$check" ]] && printf -- '- %s\n' "$check"
  done

  printf '\nSecrets:\n'
  local secret
  for secret in "${SECRET_NAMES[@]}"; do
    printf -- '- %s: %s\n' "$secret" "$(plan_secret_source "$secret")"
  done

  printf '\nWorkflows:\n'
  local workflow
  for workflow in "${WORKFLOWS[@]}"; do
    printf -- '- %s\n' "$workflow"
  done

  cat <<'EOF'

Scope guardrails:
- No organization, enterprise, or global gh configuration is changed.
- Every gh write uses --repo OWNER/REPO or /repos/OWNER/REPO API paths.
- Dry-run mode does not invoke gh and makes no API calls.
EOF
}

require_repo() {
  if [[ -z "$REPO" ]]; then
    REPO="$(detect_repo_from_origin || true)"
  fi
  if [[ ! "$REPO" =~ ^[^/]+/[^/]+$ ]]; then
    echo "FAIL: target repository must be OWNER/REPO. Pass --repo OWNER/REPO." >&2
    exit 2
  fi
}

require_gh() {
  if ! command -v gh >/dev/null 2>&1; then
    echo "FAIL: gh is required. Run gh auth login before applying this plan." >&2
    exit 2
  fi
  gh auth status >/dev/null
}

branch_protection_payload() {
  AI_DEV_REQUIRED_STATUS_CHECKS="$REQUIRED_STATUS_CHECKS" python3 - <<'PY'
import json
import os

checks = [item.strip() for item in os.environ["AI_DEV_REQUIRED_STATUS_CHECKS"].split(",") if item.strip()]
payload = {
    "required_status_checks": {
        "strict": True,
        "contexts": checks,
    },
    "enforce_admins": True,
    "required_pull_request_reviews": {
        "dismiss_stale_reviews": True,
        "require_code_owner_reviews": False,
        "required_approving_review_count": 1,
        "require_last_push_approval": True,
    },
    "restrictions": None,
    "required_linear_history": True,
    "allow_force_pushes": False,
    "allow_deletions": False,
    "required_conversation_resolution": True,
}
print(json.dumps(payload, sort_keys=True))
PY
}

merge_queue_ruleset_payload() {
  AI_DEV_RULESET_NAME="$RULESET_NAME" AI_DEV_DEFAULT_BRANCH="$BRANCH" python3 - <<'PY'
import json
import os

branch = os.environ["AI_DEV_DEFAULT_BRANCH"]
payload = {
    "name": os.environ["AI_DEV_RULESET_NAME"],
    "target": "branch",
    "enforcement": "active",
    "conditions": {
        "ref_name": {
            "include": [f"refs/heads/{branch}"],
            "exclude": [],
        },
    },
    "rules": [
        {
            "type": "merge_queue",
            "parameters": {
                "check_response_timeout_minutes": 60,
                "grouping_strategy": "ALLGREEN",
                "max_entries_to_build": 5,
                "max_entries_to_merge": 5,
                "merge_method": "SQUASH",
                "min_entries_to_merge": 1,
                "min_entries_to_merge_wait_minutes": 5,
            },
        },
    ],
}
print(json.dumps(payload, sort_keys=True))
PY
}

gh_api_json() {
  local method="$1"
  local endpoint="$2"
  local payload="$3"
  printf '%s' "$payload" | gh api \
    --method "$method" \
    -H "Accept: application/vnd.github+json" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    "$endpoint" \
    --input -
}

apply_secrets() {
  local secret
  local value
  for secret in "${SECRET_NAMES[@]}"; do
    if value="$(lookup_secret_value "$secret")"; then
      printf '%s' "$value" | gh secret set "$secret" --repo "$REPO" --body-file -
      printf 'Set repository secret: %s\n' "$secret"
    else
      printf 'Skipped missing local secret: %s\n' "$secret"
    fi
  done
}

apply_branch_protection() {
  local endpoint="/repos/$REPO/branches/$BRANCH/protection"
  gh_api_json "PUT" "$endpoint" "$(branch_protection_payload)" >/dev/null
  printf 'Applied branch protection: %s refs/heads/%s\n' "$REPO" "$BRANCH"
}

apply_merge_queue_ruleset() {
  local existing_id
  local endpoint
  existing_id="$(
    gh api \
      -H "Accept: application/vnd.github+json" \
      -H "X-GitHub-Api-Version: 2022-11-28" \
      "/repos/$REPO/rulesets?includes_parents=false" \
      --jq ".[] | select(.name == \"$RULESET_NAME\") | .id" 2>/dev/null || true
  )"
  if [[ -n "$existing_id" ]]; then
    endpoint="/repos/$REPO/rulesets/$existing_id"
    gh_api_json "PUT" "$endpoint" "$(merge_queue_ruleset_payload)" >/dev/null
    printf 'Updated merge queue ruleset: %s\n' "$RULESET_NAME"
  else
    endpoint="/repos/$REPO/rulesets"
    gh_api_json "POST" "$endpoint" "$(merge_queue_ruleset_payload)" >/dev/null
    printf 'Created merge queue ruleset: %s\n' "$RULESET_NAME"
  fi
}

enable_workflows() {
  local workflow
  local state
  for workflow in "${WORKFLOWS[@]}"; do
    gh workflow enable "$workflow" --repo "$REPO" >/dev/null
    state="$(gh workflow view "$workflow" --repo "$REPO" --json state --jq '.state')"
    if [[ "$state" != "active" ]]; then
      echo "FAIL: workflow is not active after enable: $workflow ($state)" >&2
      exit 1
    fi
    printf 'Workflow active: %s\n' "$workflow"
  done
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --repo)
      REPO="${2:-}"
      shift 2
      ;;
    --branch)
      BRANCH="${2:-}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "FAIL: unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

require_identity_secrets_profile
require_repo
print_plan

if [[ "$DRY_RUN" -eq 1 ]]; then
  echo
  echo "Dry-run complete. No gh commands were invoked."
  exit 0
fi

echo
read -r -p "Type 'apply repo operationalization' to confirm repo-scoped GitHub writes for $REPO: " confirmation
if [[ "$confirmation" != "apply repo operationalization" ]]; then
  echo "Aborted before outward writes."
  exit 1
fi

require_gh
apply_secrets
apply_branch_protection
apply_merge_queue_ruleset
enable_workflows
echo "Operationalization complete for $REPO."
