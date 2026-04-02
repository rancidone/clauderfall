#!/usr/bin/env python3
"""Install Clauderfall globally for Codex to use."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from clauderfall.installer import install_codex_global


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Install Clauderfall globally and register it in user-scoped Codex config.",
    )
    parser.add_argument(
        "server_name",
        nargs="?",
        default="clauderfall",
        help="Server name to register in Codex. Default: clauderfall",
    )
    parser.add_argument(
        "--python",
        dest="python_executable",
        default=None,
        help="Python executable to use when creating the global Clauderfall virtualenv. Default: current Python",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    result = install_codex_global(
        source_repo_root=REPO_ROOT,
        server_name=args.server_name,
        python_executable=args.python_executable,
    )

    print(f"Installed Codex MCP server '{result['server_name']}' globally")
    print(f"Install root: {result['install_root']}")
    print(f"Launcher: {result['launcher']}")
    print(f"Config: {result['config_path']}")
    print(f"Installed Codex skills: {', '.join(result['installed_codex_skills']) or '(none)'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
