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


def test_session_continue_skill_forbids_redundant_in_turn_rereads() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    skill_text = (
        repo_root / "src" / "clauderfall" / "skills" / "session_continue" / "SKILL.md"
    ).read_text()

    assert "Reuse authoritative in-turn session state when nothing suggests it changed." in skill_text
    assert "Stay in continuation until the operator explicitly asks to save, hand off, checkpoint, archive, or otherwise persist state." in skill_text


def test_session_handoff_skill_requires_explicit_persistence_intent() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    skill_text = (
        repo_root / "src" / "clauderfall" / "skills" / "session_handoff" / "SKILL.md"
    ).read_text()

    assert "Reuse authoritative in-turn session state when nothing suggests it changed." in skill_text
    assert "Do not call `session_write_handoff` unless the operator explicitly wants persistence now." in skill_text
    assert "If the operator has not asked to persist yet, stop after proposing the update and wait." in skill_text
