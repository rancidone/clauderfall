"""Skill asset loading."""

from __future__ import annotations

from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path


@dataclass(frozen=True)
class SkillDefinition:
    """Loaded skill metadata and instructions."""

    name: str
    description: str
    path: Path
    instructions: str


def default_skill_base_dir() -> Path:
    """Return the repository-local skill asset directory."""

    return Path(files("clauderfall.skills"))


def resolve_skill_path(name: str, base_dir: Path | None = None) -> Path:
    """Resolve a skill asset directory by name."""

    return (base_dir or default_skill_base_dir()) / name


def list_skills(base_dir: Path | None = None) -> list[SkillDefinition]:
    """List available skills from the skill asset directory."""

    resolved_base_dir = base_dir or default_skill_base_dir()
    if not resolved_base_dir.exists():
        return []

    definitions: list[SkillDefinition] = []
    for child in sorted(resolved_base_dir.iterdir()):
        if not child.is_dir():
            continue
        skill_path = child / "SKILL.md"
        if not skill_path.exists():
            continue
        definitions.append(load_skill(child.name, base_dir=resolved_base_dir))
    return definitions


def load_skill(name: str, base_dir: Path | None = None) -> SkillDefinition:
    """Load a skill definition from disk."""

    skill_dir = resolve_skill_path(name, base_dir=base_dir)
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.exists():
        raise FileNotFoundError(f"skill '{name}' not found at {skill_file}")

    frontmatter, instructions = parse_skill_markdown(skill_file.read_text())
    skill_name = frontmatter.get("name")
    description = frontmatter.get("description")
    if not skill_name:
        raise ValueError(f"skill '{name}' is missing required frontmatter field 'name'")
    if not description:
        raise ValueError(f"skill '{name}' is missing required frontmatter field 'description'")

    return SkillDefinition(
        name=skill_name,
        description=description,
        path=skill_dir,
        instructions=instructions.strip(),
    )


def parse_skill_markdown(text: str) -> tuple[dict[str, str], str]:
    """Parse a skill markdown file with required YAML-style frontmatter."""

    if not text.startswith("---\n"):
        raise ValueError("skill markdown must begin with frontmatter")

    lines = text.splitlines()
    frontmatter: dict[str, str] = {}
    closing_index = None
    for index, line in enumerate(lines[1:], start=1):
        if line == "---":
            closing_index = index
            break
        if not line.strip():
            continue
        key, separator, value = line.partition(":")
        if separator == "":
            raise ValueError(f"invalid frontmatter line: {line}")
        frontmatter[key.strip()] = value.strip()

    if closing_index is None:
        raise ValueError("skill markdown frontmatter must be closed with '---'")

    instructions = "\n".join(lines[closing_index + 1 :]).strip()
    return frontmatter, instructions
