#!/usr/bin/env python3
"""Remove a repo-local Clauderfall install and Claude MCP registration."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from clauderfall.installer import remove_claude_mcp


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Remove Clauderfall install artifacts and Claude MCP registration from a target repo.",
    )
    parser.add_argument("target_repo", help="Path to the repo where Claude should stop using Clauderfall.")
    parser.add_argument(
        "server_name",
        nargs="?",
        default="clauderfall",
        help="Server name to remove from the Claude MCP config. Default: clauderfall",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    result = remove_claude_mcp(
        target_repo=Path(args.target_repo),
        server_name=args.server_name,
    )

    if not result["removed_server"] and not result["removed_install_root"]:
        print(f"No Clauderfall install found in {result['target_repo']}; nothing to remove.")
    else:
        print(f"Removed Claude MCP server '{result['server_name']}' from {result['target_repo']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
