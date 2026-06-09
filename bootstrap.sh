#!/usr/bin/env bash
set -euo pipefail

template_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
default_parent="$HOME/projects"

printf "Project name: "
IFS= read -r project_name

printf "Target parent directory [%s]: " "$default_parent"
IFS= read -r parent_input
parent_input="${parent_input:-$default_parent}"

printf "Machine-user git name: "
IFS= read -r machine_user_name

printf "Machine-user git email: "
IFS= read -r machine_user_email

if [[ -z "$project_name" || -z "$parent_input" || -z "$machine_user_name" || -z "$machine_user_email" ]]; then
  echo "All prompts are required." >&2
  exit 1
fi

if ! slug="$(python3 - "$project_name" <<'PY'
import re
import sys

project_name = sys.argv[1].strip().lower()
slug = re.sub(r"[^a-z0-9]+", "-", project_name).strip("-")
if not slug:
    print("project name must contain at least one letter or digit", file=sys.stderr)
    raise SystemExit(1)
print(slug)
PY
)"; then
  echo "Project name could not be converted to a slug." >&2
  exit 1
fi

parent_dir="$(python3 - "$parent_input" <<'PY'
from pathlib import Path
import sys

parent = Path(sys.argv[1]).expanduser().resolve()
print(parent)
PY
)"
target_dir="$parent_dir/$slug"

if [[ -e "$target_dir" || -L "$target_dir" ]]; then
  echo "ERROR: target directory already exists: $target_dir" >&2
  exit 1
fi

python3 - "$template_root" "$target_dir" "$project_name" "$slug" <<'PY'
from pathlib import Path
import shutil
import sys

template_root = Path(sys.argv[1]).resolve()
target_dir = Path(sys.argv[2]).resolve()
project_name = sys.argv[3]
slug = sys.argv[4]

try:
    target_dir.relative_to(template_root)
except ValueError:
    pass
else:
    print("ERROR: target directory must be outside this template checkout", file=sys.stderr)
    raise SystemExit(1)


def ignore_template_artifacts(_: str, names: list[str]) -> set[str]:
    ignored = set()
    for name in names:
        lower = name.lower()
        if name in {".git", "node_modules", "build", ".coverage"}:
            ignored.add(name)
        elif "cache" in lower:
            ignored.add(name)
        elif lower.endswith(".egg-info"):
            ignored.add(name)
    return ignored


target_dir.parent.mkdir(parents=True, exist_ok=True)
shutil.copytree(template_root, target_dir, ignore=ignore_template_artifacts)

for relative in ("README.md", "docs-site/README.md", "pyproject.toml"):
    path = target_dir / relative
    if not path.exists():
        continue
    text = path.read_text(encoding="utf-8")
    text = text.replace("AI Development Template", project_name)
    text = text.replace("ai-dev-template", slug)
    path.write_text(text, encoding="utf-8")
PY

(
  cd "$target_dir"

  git init -b main
  git config --local user.name "$machine_user_name"
  git config --local user.email "$machine_user_email"
  git config --local core.hooksPath .githooks

  python3 -m venv .venv
  # shellcheck disable=SC1091
  source .venv/bin/activate

  if [[ "${BOOTSTRAP_TEST_SKIP_INSTALL:-0}" != "1" ]]; then
    python -m pip install --upgrade pip
    python -m pip install -e ".[dev]"
  fi

  if [[ "${BOOTSTRAP_TEST_SKIP_CHECK:-0}" != "1" ]]; then
    make check
  fi
)

echo "Bootstrap complete for $project_name at $target_dir."
