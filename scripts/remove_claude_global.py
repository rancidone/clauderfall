#!/usr/bin/env python3
"""Remove the global Claude MCP registration and packaged Claude skills."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from clauderfall.installer import remove_claude_global


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Remove the user-scoped Claude MCP registration and packaged Claude skills.",
    )
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

    result = remove_claude_global(
        source_repo_root=REPO_ROOT,
        server_name=args.server_name,
    )

    print(f"Removed Claude MCP server '{result['server_name']}' globally")
    print(f"Removed skills: {', '.join(result['removed_skills']) or '(none)'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
