#!/usr/bin/env python3
"""Register the source-tree Clauderfall MCP server globally for Claude development use."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from clauderfall.installer import register_claude_global


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Register the current source-tree Clauderfall MCP server in Claude's user-scoped config for development use.",
    )
    parser.add_argument(
        "server_name",
        nargs="?",
        default="clauderfall",
        help="Server name to register in Claude. Default: clauderfall",
    )
    parser.add_argument(
        "mode",
        nargs="?",
        default="venv",
        choices=("venv", "path"),
        help="How Claude should launch the source-tree server. Default: venv",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Register the MCP server with CLAUDERFALL_DEBUG=1 to enable debug logging to the SQLite DB.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    result = register_claude_global(
        repo_root=REPO_ROOT,
        server_name=args.server_name,
        mode=args.mode,
        debug=args.debug,
    )
    print(f"Registered Claude MCP server '{result['server_name']}' globally")
    print(f"Command: {result['command']}")
    print(f"Installed skills: {', '.join(result['installed_skills']) or '(none)'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
