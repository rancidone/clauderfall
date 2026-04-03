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
pytest_args=(tests/test_skill_harness.py)

if [[ -n "${CLAUDERFALL_LLM_HARNESS_WORKERS:-}" ]]; then
  pytest_args+=(-n "$CLAUDERFALL_LLM_HARNESS_WORKERS")
fi

exec uv run pytest "${pytest_args[@]}" "$@"
