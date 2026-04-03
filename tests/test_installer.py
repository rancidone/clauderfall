from __future__ import annotations

import json
from pathlib import Path

from clauderfall.installer import (
    CODEX_MCP_CONFIG_PATH,
    install_claude_global,
    install_codex_global,
    install_global_clauderfall,
    install_packaged_skills,
    list_packaged_skill_dirs,
    register_claude_global,
    register_codex_global,
    remove_claude_global,
    remove_codex_global,
    resolve_codex_command,
    update_codex_mcp_config,
)


def test_resolve_codex_command_supports_venv_and_path(tmp_path: Path) -> None:
    assert resolve_codex_command(repo_root=tmp_path, mode="venv") == str(tmp_path / ".venv" / "bin" / "clauderfall-mcp")
    assert resolve_codex_command(repo_root=tmp_path, mode="path") == "clauderfall-mcp"


def test_update_codex_mcp_config_writes_minimal_toml_entry(tmp_path: Path) -> None:
    config_path = update_codex_mcp_config(
        target_repo=tmp_path,
        server_name="clauderfall",
        command="/tmp/clauderfall/.clauderfall/.venv/bin/clauderfall-mcp",
        args=[],
    )

    content = config_path.read_text()

    assert config_path == tmp_path / CODEX_MCP_CONFIG_PATH
    assert "[mcp_servers.clauderfall]" in content
    assert 'command = "/tmp/clauderfall/.clauderfall/.venv/bin/clauderfall-mcp"' in content
    assert "args =" not in content


def test_update_codex_mcp_config_writes_env_when_present(tmp_path: Path) -> None:
    config_path = update_codex_mcp_config(
        target_repo=tmp_path,
        server_name="clauderfall",
        command="/tmp/clauderfall/.clauderfall/.venv/bin/clauderfall-mcp",
        args=[],
        env={"CLAUDERFALL_DEBUG": "1"},
    )

    content = config_path.read_text()

    assert 'env = { CLAUDERFALL_DEBUG = "1" }' in content


def test_list_packaged_skill_dirs_discovers_skill_directories(tmp_path: Path) -> None:
    skills_root = tmp_path / "src" / "clauderfall" / "skills"
    (skills_root / "design").mkdir(parents=True)
    (skills_root / "design" / "SKILL.md").write_text("# design\n")
    (skills_root / "discovery").mkdir(parents=True)
    (skills_root / "discovery" / "SKILL.md").write_text("# discovery\n")
    (skills_root / "not-a-skill").mkdir(parents=True)

    result = list_packaged_skill_dirs(source_repo_root=tmp_path)

    assert [path.name for path in result] == ["design", "discovery"]


def test_install_packaged_skills_copies_skill_directories(tmp_path: Path) -> None:
    skills_root = tmp_path / "src" / "clauderfall" / "skills"
    (skills_root / "design" / "references").mkdir(parents=True)
    (skills_root / "design" / "SKILL.md").write_text("design\n")
    (skills_root / "design" / "references" / "ref.md").write_text("ref\n")

    installed = install_packaged_skills(
        source_repo_root=tmp_path,
        destination_root=tmp_path / "home" / ".codex" / "skills",
        mode="copy",
    )

    destination = tmp_path / "home" / ".codex" / "skills" / "design"
    assert installed == ["design"]
    assert destination.is_dir()
    assert not destination.is_symlink()
    assert (destination / "SKILL.md").read_text() == "design\n"
    assert (destination / "references" / "ref.md").read_text() == "ref\n"


def test_install_packaged_skills_symlinks_skill_directories(tmp_path: Path) -> None:
    skills_root = tmp_path / "src" / "clauderfall" / "skills"
    (skills_root / "design").mkdir(parents=True)
    (skills_root / "design" / "SKILL.md").write_text("design\n")

    installed = install_packaged_skills(
        source_repo_root=tmp_path,
        destination_root=tmp_path / "home" / ".codex" / "skills",
        mode="symlink",
    )

    destination = tmp_path / "home" / ".codex" / "skills" / "design"
    assert installed == ["design"]
    assert destination.is_symlink()
    assert destination.resolve() == skills_root / "design"


def test_install_global_clauderfall_installs_shared_runtime_and_skills(tmp_path: Path, monkeypatch) -> None:
    source_repo = tmp_path / "source"
    source_repo.mkdir()
    global_root = tmp_path / ".clauderfall"

    def fake_create_repo_local_venv(*, install_root: Path, source_repo_root: Path, python_executable: str) -> Path:
        assert install_root == global_root
        del source_repo_root, python_executable
        bin_dir = install_root / ".venv" / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        (bin_dir / "clauderfall-mcp").write_text("#!/bin/sh\n")
        return bin_dir / "python"

    monkeypatch.setattr("clauderfall.installer.GLOBAL_INSTALL_ROOT", global_root)
    monkeypatch.setattr("clauderfall.installer.create_repo_local_venv", fake_create_repo_local_venv)
    monkeypatch.setattr("clauderfall.installer.install_packaged_skills", lambda **_: ["design", "discovery"])

    result = install_global_clauderfall(source_repo_root=source_repo, python_executable="python3")

    assert result["install_root"] == str(global_root)
    assert result["launcher"] == str(global_root / ".venv" / "bin" / "clauderfall-mcp")
    assert result["installed_codex_skills"] == ["design", "discovery"]
    assert result["installed_claude_skills"] == ["design", "discovery"]
    manifest = json.loads((global_root / "install-manifest.json").read_text())
    assert manifest["scope"] == "user"
    assert manifest["installed_from_repo"] == str(source_repo.resolve())


def test_install_claude_global_registers_user_scoped_server(monkeypatch) -> None:
    monkeypatch.setattr(
        "clauderfall.installer.install_global_clauderfall",
        lambda **_: {
            "install_root": "/home/test/.clauderfall",
            "venv_python": "/home/test/.clauderfall/.venv/bin/python",
            "launcher": "/home/test/.clauderfall/.venv/bin/clauderfall-mcp",
            "installed_codex_skills": ["design", "discovery"],
            "installed_claude_skills": ["design", "discovery"],
        },
    )
    calls: list[tuple[str, str, list[str]]] = []

    def fake_add(
        *,
        server_name: str,
        command: str,
        args: list[str],
        debug: bool = False,
    ) -> dict[str, object]:
        calls.append((server_name, command, args))
        return {"command": command, "args": args, "scope": "user", "debug": debug}

    monkeypatch.setattr("clauderfall.installer.add_claude_user_mcp_server", fake_add)

    result = install_claude_global(source_repo_root=Path("/work/clauderfall"), server_name="clauderfall")

    assert calls == [("clauderfall", "/home/test/.clauderfall/.venv/bin/clauderfall-mcp", [])]
    assert result["server_name"] == "clauderfall"
    assert result["scope"] == "user"


def test_install_codex_global_writes_user_config(monkeypatch) -> None:
    monkeypatch.setattr(
        "clauderfall.installer.install_global_clauderfall",
        lambda **_: {
            "install_root": "/home/test/.clauderfall",
            "venv_python": "/home/test/.clauderfall/.venv/bin/python",
            "launcher": "/home/test/.clauderfall/.venv/bin/clauderfall-mcp",
            "installed_codex_skills": ["design", "discovery"],
            "installed_claude_skills": ["design", "discovery"],
        },
    )

    def fake_update(
        *,
        target_repo: Path,
        server_name: str,
        command: str,
        args: list[str],
        env: dict[str, str] | None = None,
    ) -> Path:
        assert target_repo == Path.home()
        assert server_name == "clauderfall"
        assert command == "/home/test/.clauderfall/.venv/bin/clauderfall-mcp"
        assert args == []
        assert env is None
        return Path("/home/test/.codex/config.toml")

    monkeypatch.setattr("clauderfall.installer.update_codex_mcp_config", fake_update)

    result = install_codex_global(source_repo_root=Path("/work/clauderfall"), server_name="clauderfall")

    assert result["server_name"] == "clauderfall"
    assert result["config_path"] == "/home/test/.codex/config.toml"


def test_install_codex_global_can_enable_debug(monkeypatch) -> None:
    monkeypatch.setattr(
        "clauderfall.installer.install_global_clauderfall",
        lambda **_: {
            "install_root": "/home/test/.clauderfall",
            "venv_python": "/home/test/.clauderfall/.venv/bin/python",
            "launcher": "/home/test/.clauderfall/.venv/bin/clauderfall-mcp",
            "installed_codex_skills": ["design", "discovery"],
            "installed_claude_skills": ["design", "discovery"],
        },
    )

    def fake_update(
        *,
        target_repo: Path,
        server_name: str,
        command: str,
        args: list[str],
        env: dict[str, str] | None = None,
    ) -> Path:
        assert target_repo == Path.home()
        assert server_name == "clauderfall"
        assert command == "/home/test/.clauderfall/.venv/bin/clauderfall-mcp"
        assert args == []
        assert env == {"CLAUDERFALL_DEBUG": "1"}
        return Path("/home/test/.codex/config.toml")

    monkeypatch.setattr("clauderfall.installer.update_codex_mcp_config", fake_update)

    result = install_codex_global(
        source_repo_root=Path("/work/clauderfall"),
        server_name="clauderfall",
        debug=True,
    )

    assert result["debug"] is True
    assert result["config_path"] == "/home/test/.codex/config.toml"


def test_register_claude_global_uses_user_scope(monkeypatch) -> None:
    calls: list[tuple[str, str, list[str]]] = []

    def fake_add(
        *,
        server_name: str,
        command: str,
        args: list[str],
        debug: bool = False,
    ) -> dict[str, object]:
        calls.append((server_name, command, args))
        return {"command": command, "args": args, "scope": "user", "debug": debug}

    monkeypatch.setattr("clauderfall.installer.add_claude_user_mcp_server", fake_add)
    monkeypatch.setattr("clauderfall.installer.install_packaged_skills", lambda **_: ["design", "discovery"])

    result = register_claude_global(repo_root=Path("/work/clauderfall"), server_name="clauderfall-dev", mode="venv")

    assert calls == [("clauderfall-dev", "/work/clauderfall/.venv/bin/clauderfall-mcp", [])]
    assert result["installed_skills"] == ["design", "discovery"]


def test_register_codex_global_writes_user_config(monkeypatch) -> None:
    calls: list[tuple[Path, str, str, list[str], dict[str, str] | None]] = []

    def fake_update(
        *,
        target_repo: Path,
        server_name: str,
        command: str,
        args: list[str],
        env: dict[str, str] | None = None,
    ) -> Path:
        calls.append((target_repo, server_name, command, args, env))
        return Path("/home/test/.codex/config.toml")

    monkeypatch.setattr("clauderfall.installer.update_codex_mcp_config", fake_update)
    monkeypatch.setattr("clauderfall.installer.install_packaged_skills", lambda **_: ["design", "discovery"])

    result = register_codex_global(repo_root=Path("/work/clauderfall"), server_name="clauderfall-dev", mode="venv")

    assert calls == [(Path.home(), "clauderfall-dev", "/work/clauderfall/.venv/bin/clauderfall-mcp", [], None)]
    assert result["installed_skills"] == ["design", "discovery"]
    assert result["config_path"] == "/home/test/.codex/config.toml"


def test_register_codex_global_can_enable_debug(monkeypatch) -> None:
    calls: list[tuple[Path, str, str, list[str], dict[str, str] | None]] = []

    def fake_update(
        *,
        target_repo: Path,
        server_name: str,
        command: str,
        args: list[str],
        env: dict[str, str] | None = None,
    ) -> Path:
        calls.append((target_repo, server_name, command, args, env))
        return Path("/home/test/.codex/config.toml")

    monkeypatch.setattr("clauderfall.installer.update_codex_mcp_config", fake_update)
    monkeypatch.setattr("clauderfall.installer.install_packaged_skills", lambda **_: ["design", "discovery"])

    result = register_codex_global(
        repo_root=Path("/work/clauderfall"),
        server_name="clauderfall-dev",
        mode="venv",
        debug=True,
    )

    assert calls == [
        (
            Path.home(),
            "clauderfall-dev",
            "/work/clauderfall/.venv/bin/clauderfall-mcp",
            [],
            {"CLAUDERFALL_DEBUG": "1"},
        )
    ]
    assert result["debug"] is True
    assert result["installed_skills"] == ["design", "discovery"]


def test_remove_global_helpers_remove_skills_and_registration(monkeypatch) -> None:
    removed_claude: list[str] = []

    def fake_remove_claude_user_mcp_server(*, server_name: str) -> None:
        removed_claude.append(server_name)

    monkeypatch.setattr("clauderfall.installer.remove_claude_user_mcp_server", fake_remove_claude_user_mcp_server)
    monkeypatch.setattr("clauderfall.installer.remove_packaged_skills", lambda **_: ["design", "discovery"])
    monkeypatch.setattr("clauderfall.installer.remove_server_from_toml_config", lambda **_: True)

    claude_result = remove_claude_global(source_repo_root=Path("/work/clauderfall"), server_name="clauderfall")
    codex_result = remove_codex_global(source_repo_root=Path("/work/clauderfall"), server_name="clauderfall")

    assert removed_claude == ["clauderfall"]
    assert claude_result["removed_skills"] == ["design", "discovery"]
    assert codex_result["removed_server"] is True
    assert codex_result["removed_skills"] == ["design", "discovery"]
