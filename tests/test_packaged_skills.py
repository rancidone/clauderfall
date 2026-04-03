from __future__ import annotations

from pathlib import Path

from clauderfall.installer import list_packaged_skill_dirs


def test_repo_packaged_skills_include_session_continuity_skills() -> None:
    repo_root = Path(__file__).resolve().parents[1]

    skills = list_packaged_skill_dirs(source_repo_root=repo_root)
    skill_names = [path.name for path in skills]

    assert skill_names == [
        "design",
        "discovery",
        "session_continue",
        "session_handoff",
    ]


def test_session_skill_frontmatter_matches_directory_name() -> None:
    repo_root = Path(__file__).resolve().parents[1]

    for skill_name in ("session_continue", "session_handoff"):
        skill_text = (
            repo_root / "src" / "clauderfall" / "skills" / skill_name / "SKILL.md"
        ).read_text()
        assert f"name: {skill_name}" in skill_text
        assert "description:" in skill_text
