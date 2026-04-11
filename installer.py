#!/usr/bin/env -S uv run python

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path


def packaged_skills_dir() -> Path:
    return Path(__file__).resolve().parent / "skills"


def packaged_skill_names() -> list[str]:
    skills_root = packaged_skills_dir()
    names = [
        entry.name
        for entry in skills_root.iterdir()
        if entry.is_dir() and (entry / "SKILL.md").is_file()
    ]
    return sorted(names)


def default_codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()


def default_claude_home() -> Path:
    return Path(os.environ.get("CLAUDE_HOME", Path.home() / ".claude")).expanduser()


def install_packaged_skills(
    target_skills_dir: Path,
    *,
    skill_names: list[str] | None = None,
) -> list[Path]:
    source_root = packaged_skills_dir()
    available = set(packaged_skill_names())
    requested = sorted(skill_names) if skill_names else sorted(available)

    unknown = [name for name in requested if name not in available]
    if unknown:
        unknown_text = ", ".join(unknown)
        raise ValueError(f"unknown packaged skills: {unknown_text}")

    target_skills_dir.mkdir(parents=True, exist_ok=True)

    installed_paths: list[Path] = []
    for name in requested:
        source = source_root / name
        target = target_skills_dir / name
        if target.is_symlink() or target.exists():
            if target.is_symlink() or target.is_file():
                target.unlink()
            else:
                shutil.rmtree(target)
        shutil.copytree(source, target)
        installed_paths.append(target)

    return installed_paths


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Install Clauderfall packaged skills into Codex and Claude skills directories.",
    )
    parser.add_argument(
        "skills",
        nargs="*",
        help="Optional packaged skill names to install. Installs all packaged skills when omitted.",
    )
    parser.add_argument(
        "--target-dir",
        type=Path,
        help="Explicit single target skills directory. Overrides the default Codex and Claude targets.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List packaged skill names and exit.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.list:
        for name in packaged_skill_names():
            print(name)
        return 0

    target_dirs = (
        [args.target_dir]
        if args.target_dir
        else [
            default_codex_home() / "skills",
            default_claude_home() / "skills",
        ]
    )

    try:
        installed: list[Path] = []
        for target_dir in target_dirs:
            installed.extend(install_packaged_skills(target_dir, skill_names=args.skills))
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    for path in installed:
        print(path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
