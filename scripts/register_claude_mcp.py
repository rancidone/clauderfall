#!/usr/bin/env python3
"""Register the source-tree Clauderfall MCP server for Claude development use."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from clauderfall.installer import register_claude_mcp


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Register the current source-tree Clauderfall MCP server in a target repo's Claude config for development use.",
    )
    parser.add_argument("target_repo", help="Path to the repo where Claude should use the source-tree server.")
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
        "--docs-root",
        default=None,
        help="Optional Clauderfall docs root inside the target repo. Default: docs",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    result = register_claude_mcp(
        repo_root=REPO_ROOT,
        target_repo=Path(args.target_repo),
        server_name=args.server_name,
        mode=args.mode,
        docs_root=args.docs_root,
    )
    print(f"Registered Claude MCP server '{result['server_name']}' in {result['target_repo']}")
    print(f"Command: {result['command']}")
    print(f"Args: {result['args']}")
    print(f"Docs root: {result['docs_root']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
