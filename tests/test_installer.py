from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from clauderfall.installer import install_packaged_skills, packaged_skill_names


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_packaged_skill_names_include_all_installed_skills() -> None:
    assert packaged_skill_names() == ["continue", "design", "discovery", "handoff"]


def test_install_packaged_skills_copies_requested_skills(tmp_path: Path) -> None:
    target = tmp_path / "skills"

    installed = install_packaged_skills(target, skill_names=["continue", "handoff"])

    assert [path.name for path in installed] == ["continue", "handoff"]
    assert (target / "continue" / "SKILL.md").is_file()
    assert (target / "handoff" / "SKILL.md").is_file()
    assert not (target / "design").exists()


def test_install_packaged_skills_replaces_existing_target(tmp_path: Path) -> None:
    target = tmp_path / "skills"
    existing = target / "continue"
    existing.mkdir(parents=True)
    (existing / "old.txt").write_text("stale\n", encoding="utf-8")

    install_packaged_skills(target, skill_names=["continue"])

    assert (existing / "SKILL.md").is_file()
    assert not (existing / "old.txt").exists()


def test_cli_list_outputs_packaged_skill_names() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "clauderfall.installer", "--list"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert result.stdout.splitlines() == ["continue", "design", "discovery", "handoff"]


def test_cli_rejects_unknown_skill(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "clauderfall.installer",
            "--target-dir",
            str(tmp_path / "skills"),
            "unknown",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "unknown packaged skills" in result.stderr
