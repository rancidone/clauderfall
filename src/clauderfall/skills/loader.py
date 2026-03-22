"""Skill asset loading."""

from __future__ import annotations

from pathlib import Path


def resolve_skill_path(name: str, base_dir: Path) -> Path:
    """Resolve a skill asset directory by name."""

    return base_dir / name

