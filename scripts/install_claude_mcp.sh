#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDERFALL_REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

if [[ $# -lt 1 || $# -gt 3 ]]; then
  echo "usage: $0 <target-repo> [server-name] [venv|uv|path]" >&2
  exit 1
fi

TARGET_REPO="$(cd "$1" && pwd)"
SERVER_NAME="${2:-clauderfall}"
MODE="${3:-venv}"
CONFIG_PATH="${TARGET_REPO}/.claude/agentkit/mcp-servers.json"

mkdir -p "$(dirname "${CONFIG_PATH}")"

case "${MODE}" in
  venv)
    COMMAND="${CLAUDERFALL_REPO_ROOT}/.venv/bin/clauderfall-mcp"
    ARGS=(--repo-root "${TARGET_REPO}")
    ;;
  uv)
    COMMAND="uv"
    ARGS=(run --directory "${CLAUDERFALL_REPO_ROOT}" clauderfall-mcp --repo-root "${TARGET_REPO}")
    ;;
  path)
    COMMAND="clauderfall-mcp"
    ARGS=(--repo-root "${TARGET_REPO}")
    ;;
  *)
    echo "usage: $0 <target-repo> [server-name] [venv|uv|path]" >&2
    exit 1
    ;;
esac

python - <<'PY' "${CONFIG_PATH}" "${SERVER_NAME}" "${COMMAND}" "${MODE}" "${ARGS[@]}"
import json
import sys
from pathlib import Path

config_path = Path(sys.argv[1])
server_name = sys.argv[2]
command = sys.argv[3]
mode = sys.argv[4]
args = sys.argv[5:]

if config_path.exists():
    data = json.loads(config_path.read_text())
else:
    data = {}

servers = data.setdefault("mcpServers", {})
servers[server_name] = {
    "command": command,
    "args": args,
    "transport": "stdio",
}

config_path.write_text(json.dumps(data, indent=2) + "\n")
print(f"Installed Claude MCP server '{server_name}' into {config_path}")
print(f"Mode: {mode}")
print(f"Command: {command}")
print(f"Args: {args}")
PY
