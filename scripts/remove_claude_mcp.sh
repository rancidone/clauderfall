#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "usage: $0 <target-repo> [server-name]" >&2
  exit 1
fi

TARGET_REPO="$(cd "$1" && pwd)"
SERVER_NAME="${2:-clauderfall}"
CONFIG_PATH="${TARGET_REPO}/.claude/agentkit/mcp-servers.json"

python - <<'PY' "${CONFIG_PATH}" "${SERVER_NAME}"
import json
import sys
from pathlib import Path

config_path = Path(sys.argv[1])
server_name = sys.argv[2]

if not config_path.exists():
    print(f"No config file at {config_path}; nothing to remove.")
    raise SystemExit(0)

data = json.loads(config_path.read_text())
servers = data.get("mcpServers", {})

if server_name not in servers:
    print(f"Server '{server_name}' is not present in {config_path}; nothing to remove.")
    raise SystemExit(0)

del servers[server_name]

if servers:
    data["mcpServers"] = servers
    config_path.write_text(json.dumps(data, indent=2) + "\n")
    print(f"Removed Claude MCP server '{server_name}' from {config_path}")
else:
    config_path.unlink()
    print(f"Removed Claude MCP server '{server_name}' and deleted empty config {config_path}")
PY
