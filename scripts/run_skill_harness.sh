#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ -f "$repo_root/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$repo_root/.env"
  set +a
fi

cd "$repo_root"
exec uv run pytest tests/test_skill_harness.py "$@"
