#!/usr/bin/env python3
"""Register the source-tree Clauderfall MCP server globally with Codex."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from clauderfall.installer import register_codex_global


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Register the current source-tree Clauderfall MCP server in user-scoped Codex config for development use.",
    )
    parser.add_argument(
        "server_name",
        nargs="?",
        default="clauderfall",
        help="Server name to register in Codex. Default: clauderfall",
    )
    parser.add_argument(
        "mode",
        nargs="?",
        default="venv",
        choices=("venv", "path"),
        help="How Codex should launch the server. Default: venv",
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

    result = register_codex_global(
        repo_root=REPO_ROOT,
        server_name=args.server_name,
        mode=args.mode,
        debug=args.debug,
    )
    print(f"Registered Codex MCP server '{args.server_name}' with command: {result['command']}")
    print(f"Installed skills: {', '.join(result['installed_skills']) or '(none)'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
