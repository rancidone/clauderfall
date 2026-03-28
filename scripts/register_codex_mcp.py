#!/usr/bin/env python3
"""Register the source-tree Clauderfall MCP server with Codex."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from clauderfall.installer import register_codex_mcp


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Register the current source-tree Clauderfall MCP server with Codex for development use.",
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
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    command = register_codex_mcp(
        repo_root=REPO_ROOT,
        server_name=args.server_name,
        mode=args.mode,
    )
    print(f"Registered Codex MCP server '{args.server_name}' with command: {command}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
