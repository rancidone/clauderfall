from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from installer import install_packaged_skills, packaged_skill_names


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


def test_install_packaged_skills_replaces_broken_symlink_target(tmp_path: Path) -> None:
    target = tmp_path / "skills"
    target.mkdir(parents=True)
    existing = target / "design"
    existing.symlink_to(tmp_path / "missing-design")

    install_packaged_skills(target, skill_names=["design"])

    assert existing.is_dir()
    assert not existing.is_symlink()
    assert (existing / "SKILL.md").is_file()


def test_cli_list_outputs_packaged_skill_names() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "installer", "--list"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert result.stdout.splitlines() == ["continue", "design", "discovery", "handoff"]


def test_direct_execution_uses_uv_shebang() -> None:
    result = subprocess.run(
        [str(REPO_ROOT / "installer.py"), "--list"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert result.stdout.splitlines() == ["continue", "design", "discovery", "handoff"]


def test_cli_installs_all_packaged_skills_into_codex_and_claude(tmp_path: Path) -> None:
    codex_home = tmp_path / "codex-home"
    claude_home = tmp_path / "claude-home"
    env = os.environ.copy()
    env["CODEX_HOME"] = str(codex_home)
    env["CLAUDE_HOME"] = str(claude_home)

    result = subprocess.run(
        [sys.executable, "-m", "installer"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )

    assert result.returncode == 0
    installed_paths = result.stdout.splitlines()
    assert len(installed_paths) == 8
    for home in (codex_home, claude_home):
        for skill_name in packaged_skill_names():
            assert str(home / "skills" / skill_name) in installed_paths
            assert (home / "skills" / skill_name / "SKILL.md").is_file()


def test_cli_rejects_unknown_skill(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "installer",
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
