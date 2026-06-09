#!/usr/bin/env bash
set -euo pipefail

printf "Project name: "
read -r project_name

printf "Machine-user git name: "
read -r machine_user_name

printf "Machine-user git email: "
read -r machine_user_email

if [[ -z "$project_name" || -z "$machine_user_name" || -z "$machine_user_email" ]]; then
  echo "All prompts are required." >&2
  exit 1
fi

python - "$project_name" <<'PY'
from pathlib import Path
import sys

project_name = sys.argv[1]
slug = project_name.lower().replace(" ", "-")
for path in [Path("README.md"), Path("docs-site/README.md"), Path("pyproject.toml")]:
    text = path.read_text(encoding="utf-8")
    text = text.replace("AI Development Template", project_name)
    text = text.replace("ai-dev-template", slug)
    path.write_text(text, encoding="utf-8")
PY

if [[ ! -d .git ]]; then
  git init -b main
fi

git config user.name "$machine_user_name"
git config user.email "$machine_user_email"
git config core.hooksPath .githooks

make check

echo "Bootstrap complete for $project_name."
