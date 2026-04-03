#!/usr/bin/env python3
"""Unified global installer for Clauderfall MCP registration."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Install, register, or remove Clauderfall globally for Claude and Codex.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    install_parser = subparsers.add_parser(
        "install",
        help="Install Clauderfall into a shared global venv and register selected clients.",
    )
    _add_common_target_args(install_parser)
    install_parser.add_argument(
        "server_name",
        nargs="?",
        default="clauderfall",
        help="Server name to register. Default: clauderfall",
    )
    install_parser.add_argument(
        "--python",
        dest="python_executable",
        default=None,
        help="Python executable to use when creating the global Clauderfall virtualenv. Default: current Python",
    )
    install_parser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Register the MCP server with CLAUDERFALL_DEBUG=1.",
    )

    register_parser = subparsers.add_parser(
        "register",
        help="Register the source-tree server for selected clients.",
    )
    _add_common_target_args(register_parser)
    register_parser.add_argument(
        "server_name",
        nargs="?",
        default="clauderfall",
        help="Server name to register. Default: clauderfall",
    )
    register_parser.add_argument(
        "mode",
        nargs="?",
        default="venv",
        choices=("venv", "path"),
        help="How clients should launch the source-tree server. Default: venv",
    )
    register_parser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Register the MCP server with CLAUDERFALL_DEBUG=1.",
    )

    remove_parser = subparsers.add_parser(
        "remove",
        help="Remove global registration and packaged skills for selected clients.",
    )
    _add_common_target_args(remove_parser)
    remove_parser.add_argument(
        "server_name",
        nargs="?",
        default="clauderfall",
        help="Server name to remove. Default: clauderfall",
    )

    return parser


def _add_common_target_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--target",
        dest="targets",
        action="append",
        choices=("claude", "codex"),
        help="Client target to operate on. Repeat to select multiple targets. Default: both",
    )


def main() -> int:
    if sys.version_info < (3, 12):
        env = dict(os.environ)
        env.setdefault("UV_CACHE_DIR", str(REPO_ROOT / ".uv-cache"))
        os.execvpe(
            "uv",
            ["uv", "run", "python", str(Path(__file__).resolve()), *sys.argv[1:]],
            env,
        )

    from clauderfall.installer import install_global, register_global, remove_global

    parser = build_parser()
    args = parser.parse_args()

    if args.command == "install":
        result = install_global(
            source_repo_root=REPO_ROOT,
            server_name=args.server_name,
            python_executable=args.python_executable,
            debug=args.debug,
            targets=args.targets,
        )
        print(f"Installed global MCP server '{result['server_name']}' for {', '.join(result['targets'])}")
        print(f"Install root: {result['install_root']}")
        print(f"Launcher: {result['launcher']}")
        for target in result["targets"]:
            _print_target_result(target, result["registrations"][target])
        return 0

    if args.command == "register":
        result = register_global(
            repo_root=REPO_ROOT,
            server_name=args.server_name,
            mode=args.mode,
            debug=args.debug,
            targets=args.targets,
        )
        print(f"Registered source-tree MCP server '{result['server_name']}' for {', '.join(result['targets'])}")
        print(f"Command: {result['command']}")
        for target in result["targets"]:
            _print_target_result(target, result["registrations"][target])
        return 0

    if args.command == "remove":
        result = remove_global(
            source_repo_root=REPO_ROOT,
            server_name=args.server_name,
            targets=args.targets,
        )
        print(f"Removed global MCP server '{result['server_name']}' for {', '.join(result['targets'])}")
        for target in result["targets"]:
            _print_target_result(target, result["removals"][target])
        return 0

    parser.error(f"unsupported command: {args.command}")
    return 2


def _print_target_result(target: str, result: dict[str, object]) -> None:
    label = target.capitalize()
    if "config_path" in result:
        print(f"{label} config: {result['config_path']}")
    if "installed_skills" in result:
        print(f"{label} skills: {', '.join(result['installed_skills']) or '(none)'}")
    if "removed_skills" in result:
        print(f"{label} removed skills: {', '.join(result['removed_skills']) or '(none)'}")


if __name__ == "__main__":
    raise SystemExit(main())
