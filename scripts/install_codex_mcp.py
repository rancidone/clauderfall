#!/usr/bin/env python3
"""Install Clauderfall into another repo for Codex to use locally."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from clauderfall.installer import install_codex_mcp


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Install Clauderfall into a target repo and register it in repo-local Codex config.",
    )
    parser.add_argument("target_repo", help="Path to the repo where Codex should use Clauderfall.")
    parser.add_argument(
        "server_name",
        nargs="?",
        default="clauderfall",
        help="Server name to register in the Codex MCP config. Default: clauderfall",
    )
    parser.add_argument(
        "--python",
        dest="python_executable",
        default=None,
        help="Python executable to use when creating the repo-local virtualenv. Default: current Python",
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

    result = install_codex_mcp(
        source_repo_root=REPO_ROOT,
        target_repo=Path(args.target_repo),
        server_name=args.server_name,
        docs_root=args.docs_root,
        python_executable=args.python_executable,
    )

    print(f"Installed Codex MCP server '{result['server_name']}' into {result['target_repo']}")
    print(f"Install root: {result['install_root']}")
    print(f"Launcher: {result['launcher']}")
    print(f"Config: {result['config_path']}")
    print(f"Docs root: {result['docs_root']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
