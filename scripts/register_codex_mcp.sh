#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

SERVER_NAME="${1:-clauderfall}"
MODE="${2:-venv}"

case "${MODE}" in
  venv)
    COMMAND="${REPO_ROOT}/.venv/bin/clauderfall-mcp"
    ;;
  path)
    COMMAND="clauderfall-mcp"
    ;;
  *)
    echo "usage: $0 [server-name] [venv|path]" >&2
    exit 1
    ;;
esac

codex mcp add "${SERVER_NAME}" -- "${COMMAND}"
echo "Registered Codex MCP server '${SERVER_NAME}' with command: ${COMMAND}"
