#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${AI_DEV_TEMPLATE_ROOT:-$(cd "$SCRIPT_DIR/.." && pwd)}"
CONFIG_DIR="$REPO_ROOT/config"

IDP_CHOICE=""
SECRETS_CHOICE=""
NON_INTERACTIVE=0
DRY_RUN=0

usage() {
  cat <<'EOF'
Usage: scripts/setup_identity.sh [--non-interactive --idp IDP --secrets MANAGER] [--dry-run]

Required onboarding wizard for choosing the central identity provider and secrets manager. The script records the
choice in repo-local config/identity.json and config/secrets.json, then prints provider-specific next steps.

Options:
  --non-interactive       Require --idp and --secrets; do not prompt.
  --idp IDP               Identity provider: entra, okta, google, aws, local-dev-only.
  --secrets MANAGER       Secrets manager: azure-key-vault, hashicorp-vault, aws-secrets-manager,
                          gcp-secret-manager, onepassword-doppler, os-keyring.
  --dry-run               CI-safe mode. Writes the local profile and makes no cloud calls.
  -h, --help              Show this help.
EOF
}

normalize_token() {
  printf '%s' "$1" | tr '[:upper:]_' '[:lower:]-' | sed 's/[[:space:]]\{1,\}/-/g'
}

normalize_idp() {
  local value
  value="$(normalize_token "$1")"
  case "$value" in
    1|entra|microsoft-entra|microsoft-entra-id|azure-ad|azure-active-directory)
      printf 'microsoft_entra_id'
      ;;
    2|okta)
      printf 'okta'
      ;;
    3|google|gcp|google-cloud|google-cloud-iam|google-workspace|google-cloud-iam/workspace)
      printf 'google_cloud_iam_workspace'
      ;;
    4|aws|aws-iam|aws-iam-identity-center|iam-identity-center)
      printf 'aws_iam_identity_center'
      ;;
    5|local|local-dev|local-dev-only)
      printf 'local_dev_only'
      ;;
    *)
      return 1
      ;;
  esac
}

normalize_secrets() {
  local value
  value="$(normalize_token "$1")"
  case "$value" in
    1|azure-key-vault|akv|key-vault)
      printf 'azure_key_vault'
      ;;
    2|hashicorp|hashicorp-vault|vault)
      printf 'hashicorp_vault'
      ;;
    3|aws|aws-secrets|aws-secrets-manager|secrets-manager)
      printf 'aws_secrets_manager'
      ;;
    4|gcp|gcp-secret-manager|google-secret-manager|google-cloud-secret-manager)
      printf 'gcp_secret_manager'
      ;;
    5|1password|onepassword|doppler|1password-doppler|onepassword-doppler)
      printf 'onepassword_doppler'
      ;;
    6|os-keyring|keyring|local-keyring)
      printf 'os_keyring'
      ;;
    *)
      return 1
      ;;
  esac
}

idp_display_name() {
  case "$1" in
    microsoft_entra_id) printf 'Microsoft Entra ID' ;;
    okta) printf 'Okta' ;;
    google_cloud_iam_workspace) printf 'Google Cloud IAM / Workspace' ;;
    aws_iam_identity_center) printf 'AWS IAM Identity Center' ;;
    local_dev_only) printf 'local-dev-only' ;;
    *) printf '%s' "$1" ;;
  esac
}

secrets_display_name() {
  case "$1" in
    azure_key_vault) printf 'Azure Key Vault' ;;
    hashicorp_vault) printf 'HashiCorp Vault' ;;
    aws_secrets_manager) printf 'AWS Secrets Manager' ;;
    gcp_secret_manager) printf 'GCP Secret Manager' ;;
    onepassword_doppler) printf '1Password / Doppler' ;;
    os_keyring) printf 'OS keyring' ;;
    *) printf '%s' "$1" ;;
  esac
}

print_identity_options() {
  cat <<'EOF'
Choose your IDENTITY PROVIDER:
  [1] Microsoft Entra ID (recommended for Azure/M365)
      Managed identities/service principals with conditional access and audit logs.
  [2] Okta
      Central SSO and lifecycle management for Okta-standardized organizations.
  [3] Google Cloud IAM / Workspace
      Google Workspace or GCP-backed users, service accounts, and workload identity.
  [4] AWS IAM Identity Center
      AWS organization identities with permission sets, roles, and short-lived sessions.
  [5] local-dev-only
      Local development only; not for shared, production, or externally writable systems.
EOF
}

print_secrets_options() {
  cat <<'EOF'
Choose your SECRETS MANAGER:
  [1] Azure Key Vault (recommended for Azure)
      Central Azure-managed vault with RBAC, audit logs, and managed/workload identity access.
  [2] HashiCorp Vault
      Central broker for dynamic or leased secrets across clouds and datacenters.
  [3] AWS Secrets Manager
      AWS-native managed secrets with IAM scoping, rotation, and CloudTrail audit.
  [4] GCP Secret Manager
      Google Cloud managed secrets with IAM scoping and Cloud Audit Logs.
  [5] 1Password / Doppler
      Team-managed developer and runtime secrets synced into approved environments.
  [6] OS keyring (local dev only)
      Local developer fallback only; not a production or shared environment manager.
EOF
}

prompt_idp() {
  local answer
  local normalized
  print_identity_options
  while true; do
    printf 'Choose your IDENTITY PROVIDER: '
    IFS= read -r answer
    if normalized="$(normalize_idp "$answer")"; then
      IDP_CHOICE="$normalized"
      return 0
    fi
    echo "Invalid choice. Enter 1, 2, 3, 4, or 5."
  done
}

prompt_secrets() {
  local answer
  local normalized
  print_secrets_options
  while true; do
    printf 'Choose your SECRETS MANAGER: '
    IFS= read -r answer
    if normalized="$(normalize_secrets "$answer")"; then
      SECRETS_CHOICE="$normalized"
      return 0
    fi
    echo "Invalid choice. Enter 1, 2, 3, 4, 5, or 6."
  done
}

set_idp_choice() {
  local normalized
  if ! normalized="$(normalize_idp "$1")"; then
    echo "FAIL: invalid identity provider: $1" >&2
    exit 2
  fi
  IDP_CHOICE="$normalized"
}

set_secrets_choice() {
  local normalized
  if ! normalized="$(normalize_secrets "$1")"; then
    echo "FAIL: invalid secrets manager: $1" >&2
    exit 2
  fi
  SECRETS_CHOICE="$normalized"
}

write_profiles() {
  mkdir -p "$CONFIG_DIR"
  AI_DEV_CONFIG_DIR="$CONFIG_DIR" \
  AI_DEV_IDP_CHOICE="$IDP_CHOICE" \
  AI_DEV_IDP_DISPLAY="$(idp_display_name "$IDP_CHOICE")" \
  AI_DEV_SECRETS_CHOICE="$SECRETS_CHOICE" \
  AI_DEV_SECRETS_DISPLAY="$(secrets_display_name "$SECRETS_CHOICE")" \
  AI_DEV_SETUP_DRY_RUN="$DRY_RUN" \
  python3 - <<'PY'
import json
import os
import sys
from pathlib import Path

config_dir = Path(os.environ["AI_DEV_CONFIG_DIR"])
identity_example_path = config_dir / "identity.example.json"
secrets_example_path = config_dir / "secrets.example.json"

missing = [path for path in (identity_example_path, secrets_example_path) if not path.exists()]
if missing:
    for path in missing:
        print(f"FAIL: missing setup example file: {path}", file=sys.stderr)
    raise SystemExit(2)

identity = json.loads(identity_example_path.read_text(encoding="utf-8"))
secrets = json.loads(secrets_example_path.read_text(encoding="utf-8"))
if not isinstance(identity, dict) or not isinstance(secrets, dict):
    print("FAIL: setup example files must contain JSON objects", file=sys.stderr)
    raise SystemExit(2)

idp_choice = os.environ["AI_DEV_IDP_CHOICE"]
secrets_choice = os.environ["AI_DEV_SECRETS_CHOICE"]

identity["selected_provider"] = idp_choice
identity["selected_display_name"] = os.environ["AI_DEV_IDP_DISPLAY"]
identity["contains_credentials"] = False
identity["setup"] = {
    "script": "scripts/setup_identity.sh",
    "cloud_calls": False,
    "dry_run": os.environ["AI_DEV_SETUP_DRY_RUN"] == "1",
    "next_steps_only": True,
}
providers = identity.setdefault("providers", {})
if not isinstance(providers, dict) or idp_choice not in providers:
    print(f"FAIL: identity example is missing provider: {idp_choice}", file=sys.stderr)
    raise SystemExit(2)
for key, settings in providers.items():
    if isinstance(settings, dict):
        settings["selected"] = key == idp_choice

secrets["selected_manager"] = secrets_choice
secrets["selected_display_name"] = os.environ["AI_DEV_SECRETS_DISPLAY"]
secrets["contains_credentials"] = False
secrets["setup"] = {
    "script": "scripts/setup_identity.sh",
    "cloud_calls": False,
    "dry_run": os.environ["AI_DEV_SETUP_DRY_RUN"] == "1",
    "next_steps_only": True,
}
secrets["resolution_order"] = ["env", "keyring"]
providers = secrets.setdefault("providers", {})
if not isinstance(providers, dict) or secrets_choice not in providers:
    print(f"FAIL: secrets example is missing manager: {secrets_choice}", file=sys.stderr)
    raise SystemExit(2)
for key, settings in providers.items():
    if isinstance(settings, dict):
        settings["selected"] = key == secrets_choice

for path, data in (
    (config_dir / "identity.json", identity),
    (config_dir / "secrets.json", secrets),
):
    temp_path = path.with_suffix(path.suffix + ".tmp")
    temp_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temp_path.replace(path)
PY
}

print_identity_next_steps() {
  case "$IDP_CHOICE" in
    microsoft_entra_id)
      cat <<'EOF'

IDENTITY NEXT STEPS - Microsoft Entra ID
1. Register the machine-user application:
   az ad app create --display-name "<project>-machine-user"
2. Create or select the service principal:
   az ad sp create --id "<appId>"
3. Grant least-privilege roles only for the repository, workflow, and cloud scopes required.
4. Prefer workload identity federation, managed identity, or short-lived OAuth tokens over client secrets.
5. Record the owner, audit-log location, revocation path, and human approval gate.
EOF
      ;;
    okta)
      cat <<'EOF'

IDENTITY NEXT STEPS - Okta
1. Create an Okta OIDC application or service integration for "<project>-machine-user".
2. Assign only the groups and API scopes required for repository automation.
3. Enforce MFA and conditional access policies for human users.
4. Prefer OAuth/OIDC token exchange over static client secrets.
5. Record the owner, audit-log location, revocation path, and human approval gate.
EOF
      ;;
    google_cloud_iam_workspace)
      cat <<'EOF'

IDENTITY NEXT STEPS - Google Cloud IAM / Workspace
1. Create or select a dedicated service account:
   gcloud iam service-accounts create "<project>-machine-user"
2. Bind least-privilege IAM roles only at the required project/resource scope.
3. Prefer workload identity federation over exported service account keys.
4. Confirm Cloud Audit Logs cover the machine identity actions.
5. Record the owner, revocation path, and human approval gate.
EOF
      ;;
    aws_iam_identity_center)
      cat <<'EOF'

IDENTITY NEXT STEPS - AWS IAM Identity Center
1. Create or select the Identity Center permission set for repository automation.
2. Assign the permission set only to the target account and automation principal.
3. Prefer short-lived role sessions and OIDC federation over long-lived access keys.
4. Confirm CloudTrail records the machine identity actions.
5. Record the owner, revocation path, and human approval gate.
EOF
      ;;
    local_dev_only)
      cat <<'EOF'

IDENTITY NEXT STEPS - local-dev-only
1. Use only local, non-production testing resources.
2. Do not grant external write access, production access, shared tenant access, or deployment permissions.
3. Before any shared or production work, rerun this wizard and choose a central identity provider.
4. Record that this profile is restricted to local development.
EOF
      ;;
  esac
}

print_secrets_next_steps() {
  case "$SECRETS_CHOICE" in
    azure_key_vault)
      cat <<'EOF'

SECRETS NEXT STEPS - Azure Key Vault
1. Create the vault:
   az keyvault create --name "<vault-name>" --resource-group "<resource-group>" --location "<region>" --enable-rbac-authorization true
2. Grant the machine identity read-only secret access:
   az role assignment create --assignee "<service-principal-object-id>" --role "Key Vault Secrets User" --scope "<vault-resource-id>"
3. Add required secrets from a secure source:
   az keyvault secret set --vault-name "<vault-name>" --name "<logical-secret-name>" --value "<securely-entered-value>"
4. Update config/secrets.json with the real vault URL only; never store secret values there.
5. Confirm get/list access, rotation ownership, and revocation steps.
EOF
      ;;
    hashicorp_vault)
      cat <<'EOF'

SECRETS NEXT STEPS - HashiCorp Vault
1. Enable or select the secrets engine for this project path:
   vault secrets enable -path="<project>" kv-v2
2. Create a least-privilege read policy for runtime secret paths.
3. Bind the policy to the approved OIDC, AppRole, Kubernetes, or cloud auth method.
4. Store values with vault kv put from a secure terminal session.
5. Record lease/rotation settings, audit device coverage, and revocation steps.
EOF
      ;;
    aws_secrets_manager)
      cat <<'EOF'

SECRETS NEXT STEPS - AWS Secrets Manager
1. Create each runtime secret:
   aws secretsmanager create-secret --name "<project>/<logical-secret-name>" --secret-string "<securely-entered-value>"
2. Attach an IAM policy granting read access only to the required secret ARNs.
3. Prefer OIDC or role assumption for runtime access.
4. Enable rotation where supported and confirm CloudTrail audit coverage.
5. Record owner, rotation cadence, and revocation steps.
EOF
      ;;
    gcp_secret_manager)
      cat <<'EOF'

SECRETS NEXT STEPS - GCP Secret Manager
1. Create each runtime secret:
   gcloud secrets create "<logical-secret-name>" --replication-policy="automatic"
2. Add values from a secure source:
   gcloud secrets versions add "<logical-secret-name>" --data-file="<secure-local-file>"
3. Grant roles/secretmanager.secretAccessor only to the approved runtime identity.
4. Prefer workload identity federation over exported keys.
5. Record owner, rotation cadence, audit logs, and revocation steps.
EOF
      ;;
    onepassword_doppler)
      cat <<'EOF'

SECRETS NEXT STEPS - 1Password / Doppler
1. Create a project vault/config for this repository.
2. Add only the runtime secrets required by this project.
3. Grant access to named users, service accounts, or environments using least privilege.
4. Configure CI/runtime injection without writing .env files into the repository.
5. Record owner, rotation cadence, audit logs, and revocation steps.
EOF
      ;;
    os_keyring)
      cat <<'EOF'

SECRETS NEXT STEPS - OS keyring
1. Store local-only development secrets in the operating-system keyring.
2. Do not use this profile for shared, CI, production, deployment, or external-write workflows.
3. Before any shared or production work, rerun this wizard and choose a central secrets manager.
4. Record that this profile is restricted to local development.
EOF
      ;;
  esac
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --non-interactive)
      NON_INTERACTIVE=1
      shift
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --idp)
      if [[ -z "${2:-}" ]]; then
        echo "FAIL: --idp requires a value" >&2
        exit 2
      fi
      set_idp_choice "$2"
      shift 2
      ;;
    --secrets)
      if [[ -z "${2:-}" ]]; then
        echo "FAIL: --secrets requires a value" >&2
        exit 2
      fi
      set_secrets_choice "$2"
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

if [[ "$NON_INTERACTIVE" -eq 1 ]]; then
  if [[ -z "$IDP_CHOICE" || -z "$SECRETS_CHOICE" ]]; then
    echo "FAIL: --non-interactive requires --idp and --secrets." >&2
    exit 2
  fi
else
  [[ -n "$IDP_CHOICE" ]] || prompt_idp
  [[ -n "$SECRETS_CHOICE" ]] || prompt_secrets
fi

write_profiles

cat <<EOF
Identity and secrets setup recorded.

Profile files written:
- $CONFIG_DIR/identity.json
- $CONFIG_DIR/secrets.json

Selected identity provider: $(idp_display_name "$IDP_CHOICE")
Selected secrets manager:   $(secrets_display_name "$SECRETS_CHOICE")

No cloud calls were made. The commands below are next steps for a human/operator to run in the chosen provider.
EOF

if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "Dry-run mode: local profile files were written, and no external/cloud commands were invoked."
fi

print_identity_next_steps
print_secrets_next_steps
