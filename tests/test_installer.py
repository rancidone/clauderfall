from __future__ import annotations

import json
from pathlib import Path

from clauderfall.installer import (
    CLAUDE_INSTALL_DIR,
    CLAUDE_GITIGNORE_ENTRIES,
    CLAUDE_MCP_CONFIG_PATH,
    CODEX_INSTALL_DIR,
    CODEX_GITIGNORE_ENTRIES,
    CODEX_MCP_CONFIG_PATH,
    build_server_args,
    ensure_clauderfall_gitignore,
    install_claude_mcp,
    install_codex_mcp,
    register_claude_mcp,
    remove_claude_mcp,
    remove_codex_mcp,
    resolve_codex_command,
    resolve_claude_registration_command,
    update_claude_mcp_config,
    update_codex_mcp_config,
)


def test_update_claude_mcp_config_writes_stdio_server_entry(tmp_path: Path) -> None:
    config_path = update_claude_mcp_config(
        target_repo=tmp_path,
        server_name="clauderfall",
        command="/tmp/clauderfall/.venv/bin/clauderfall-mcp",
        args=["--repo-root", str(tmp_path)],
    )

    data = json.loads(config_path.read_text())

    assert config_path == tmp_path / CLAUDE_MCP_CONFIG_PATH
    assert data["mcpServers"]["clauderfall"]["transport"] == "stdio"
    assert data["mcpServers"]["clauderfall"]["args"] == ["--repo-root", str(tmp_path)]


def test_gitignore_block_is_added_only_once(tmp_path: Path) -> None:
    gitignore_path = tmp_path / ".gitignore"
    gitignore_path.write_text("node_modules/\n")

    ensure_clauderfall_gitignore(tmp_path, CLAUDE_GITIGNORE_ENTRIES)
    ensure_clauderfall_gitignore(tmp_path, CLAUDE_GITIGNORE_ENTRIES)

    content = gitignore_path.read_text()
    assert content.count("# clauderfall-mcp: begin") == 1
    assert ".claude/clauderfall/" in content
    assert ".mcp.json" in content
    assert ".codex/clauderfall/" not in content
    assert ".codex/config.toml" not in content


def test_install_claude_mcp_creates_repo_local_artifacts_and_manifest(tmp_path: Path, monkeypatch) -> None:
    source_repo = tmp_path / "source"
    source_repo.mkdir()

    def fake_create_repo_local_venv(*, install_root: Path, source_repo_root: Path, python_executable: str) -> Path:
        del source_repo_root, python_executable
        bin_dir = install_root / ".venv" / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        launcher = bin_dir / "clauderfall-mcp"
        launcher.write_text("#!/bin/sh\n")
        return bin_dir / "python"

    monkeypatch.setattr("clauderfall.installer.create_repo_local_venv", fake_create_repo_local_venv)

    result = install_claude_mcp(
        source_repo_root=source_repo,
        target_repo=tmp_path,
        server_name="clauderfall",
        python_executable="python3",
    )

    manifest = json.loads((tmp_path / CLAUDE_INSTALL_DIR / "install-manifest.json").read_text())
    config = json.loads((tmp_path / CLAUDE_MCP_CONFIG_PATH).read_text())

    assert result["launcher"] == str(tmp_path / CLAUDE_INSTALL_DIR / ".venv" / "bin" / "clauderfall-mcp")
    assert manifest["installed_from_repo"] == str(source_repo.resolve())
    assert config["mcpServers"]["clauderfall"]["command"] == result["launcher"]
    assert (tmp_path / ".gitignore").exists()


def test_install_claude_mcp_writes_custom_docs_root_into_config(tmp_path: Path, monkeypatch) -> None:
    source_repo = tmp_path / "source"
    source_repo.mkdir()

    def fake_create_repo_local_venv(*, install_root: Path, source_repo_root: Path, python_executable: str) -> Path:
        del source_repo_root, python_executable
        bin_dir = install_root / ".venv" / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        (bin_dir / "clauderfall-mcp").write_text("#!/bin/sh\n")
        return bin_dir / "python"

    monkeypatch.setattr("clauderfall.installer.create_repo_local_venv", fake_create_repo_local_venv)

    result = install_claude_mcp(
        source_repo_root=source_repo,
        target_repo=tmp_path,
        server_name="clauderfall",
        docs_root="docs/clauderfall",
    )

    config = json.loads((tmp_path / CLAUDE_MCP_CONFIG_PATH).read_text())

    assert result["docs_root"] == str((tmp_path / "docs/clauderfall").resolve())
    assert config["mcpServers"]["clauderfall"]["args"] == [
        "--repo-root",
        str(tmp_path),
        "--docs-root",
        str((tmp_path / "docs/clauderfall").resolve()),
    ]


def test_remove_claude_mcp_cleans_install_root_config_and_gitignore(tmp_path: Path) -> None:
    install_root = tmp_path / CLAUDE_INSTALL_DIR
    install_root.mkdir(parents=True)
    (install_root / "install-manifest.json").write_text("{}\n")
    ensure_clauderfall_gitignore(tmp_path, CLAUDE_GITIGNORE_ENTRIES)
    update_claude_mcp_config(
        target_repo=tmp_path,
        server_name="clauderfall",
        command="/tmp/clauderfall/.venv/bin/clauderfall-mcp",
        args=["--repo-root", str(tmp_path)],
    )

    result = remove_claude_mcp(target_repo=tmp_path, server_name="clauderfall")

    assert result["removed_server"] is True
    assert result["removed_install_root"] is True
    assert not (tmp_path / CLAUDE_INSTALL_DIR).exists()
    assert not (tmp_path / CLAUDE_MCP_CONFIG_PATH).exists()
    gitignore_path = tmp_path / ".gitignore"
    if gitignore_path.exists():
        assert "# clauderfall-mcp: begin" not in gitignore_path.read_text()


def test_resolve_codex_command_supports_venv_and_path(tmp_path: Path) -> None:
    assert resolve_codex_command(repo_root=tmp_path, mode="venv") == str(tmp_path / ".venv" / "bin" / "clauderfall-mcp")
    assert resolve_codex_command(repo_root=tmp_path, mode="path") == "clauderfall-mcp"


def test_register_claude_mcp_writes_source_tree_command(tmp_path: Path) -> None:
    result = register_claude_mcp(
        repo_root=Path("/work/clauderfall"),
        target_repo=tmp_path,
        server_name="clauderfall-dev",
        mode="venv",
    )

    config = json.loads((tmp_path / CLAUDE_MCP_CONFIG_PATH).read_text())

    assert result["command"] == "/work/clauderfall/.venv/bin/clauderfall-mcp"
    assert config["mcpServers"]["clauderfall-dev"]["args"] == ["--repo-root", str(tmp_path)]


def test_register_claude_mcp_supports_custom_docs_root(tmp_path: Path) -> None:
    result = register_claude_mcp(
        repo_root=Path("/work/clauderfall"),
        target_repo=tmp_path,
        server_name="clauderfall-dev",
        mode="venv",
        docs_root="docs/clauderfall",
    )

    assert result["args"] == [
        "--repo-root",
        str(tmp_path),
        "--docs-root",
        str((tmp_path / "docs/clauderfall").resolve()),
    ]


def test_update_codex_mcp_config_writes_minimal_toml_entry(tmp_path: Path) -> None:
    config_path = update_codex_mcp_config(
        target_repo=tmp_path,
        server_name="clauderfall",
        command="/tmp/clauderfall/.codex/clauderfall/.venv/bin/clauderfall-mcp",
        args=["--repo-root", str(tmp_path)],
    )

    content = config_path.read_text()

    assert config_path == tmp_path / CODEX_MCP_CONFIG_PATH
    assert "[mcp_servers.clauderfall]" in content
    assert 'command = "/tmp/clauderfall/.codex/clauderfall/.venv/bin/clauderfall-mcp"' in content
    assert 'args = ["--repo-root", "' in content


def test_install_codex_mcp_creates_repo_local_artifacts_and_manifest(tmp_path: Path, monkeypatch) -> None:
    source_repo = tmp_path / "source"
    source_repo.mkdir()

    def fake_create_repo_local_venv(*, install_root: Path, source_repo_root: Path, python_executable: str) -> Path:
        del source_repo_root, python_executable
        bin_dir = install_root / ".venv" / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        launcher = bin_dir / "clauderfall-mcp"
        launcher.write_text("#!/bin/sh\n")
        return bin_dir / "python"

    monkeypatch.setattr("clauderfall.installer.create_repo_local_venv", fake_create_repo_local_venv)

    result = install_codex_mcp(
        source_repo_root=source_repo,
        target_repo=tmp_path,
        server_name="clauderfall",
        python_executable="python3",
    )

    manifest = json.loads((tmp_path / CODEX_INSTALL_DIR / "install-manifest.json").read_text())
    config = (tmp_path / CODEX_MCP_CONFIG_PATH).read_text()

    assert result["launcher"] == str(tmp_path / CODEX_INSTALL_DIR / ".venv" / "bin" / "clauderfall-mcp")
    assert manifest["installed_from_repo"] == str(source_repo.resolve())
    assert 'command = "' + result["launcher"] + '"' in config


def test_install_codex_mcp_writes_custom_docs_root_into_config(tmp_path: Path, monkeypatch) -> None:
    source_repo = tmp_path / "source"
    source_repo.mkdir()

    def fake_create_repo_local_venv(*, install_root: Path, source_repo_root: Path, python_executable: str) -> Path:
        del source_repo_root, python_executable
        bin_dir = install_root / ".venv" / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        (bin_dir / "clauderfall-mcp").write_text("#!/bin/sh\n")
        return bin_dir / "python"

    monkeypatch.setattr("clauderfall.installer.create_repo_local_venv", fake_create_repo_local_venv)

    result = install_codex_mcp(
        source_repo_root=source_repo,
        target_repo=tmp_path,
        server_name="clauderfall",
        docs_root="docs/clauderfall",
    )

    config = (tmp_path / CODEX_MCP_CONFIG_PATH).read_text()

    assert result["docs_root"] == str((tmp_path / "docs/clauderfall").resolve())
    assert '--docs-root' in config
    assert str((tmp_path / "docs/clauderfall").resolve()) in config


def test_remove_codex_mcp_cleans_install_root_config_and_gitignore(tmp_path: Path) -> None:
    install_root = tmp_path / CODEX_INSTALL_DIR
    install_root.mkdir(parents=True)
    (install_root / "install-manifest.json").write_text("{}\n")
    ensure_clauderfall_gitignore(tmp_path, CODEX_GITIGNORE_ENTRIES)
    update_codex_mcp_config(
        target_repo=tmp_path,
        server_name="clauderfall",
        command="/tmp/clauderfall/.venv/bin/clauderfall-mcp",
        args=["--repo-root", str(tmp_path)],
    )

    result = remove_codex_mcp(target_repo=tmp_path, server_name="clauderfall")

    assert result["removed_server"] is True
    assert result["removed_install_root"] is True
    assert not (tmp_path / CODEX_INSTALL_DIR).exists()
    assert not (tmp_path / CODEX_MCP_CONFIG_PATH).exists()


def test_gitignore_union_is_preserved_across_claude_and_codex_entries(tmp_path: Path) -> None:
    ensure_clauderfall_gitignore(tmp_path, CLAUDE_GITIGNORE_ENTRIES)
    ensure_clauderfall_gitignore(tmp_path, CODEX_GITIGNORE_ENTRIES)

    content = (tmp_path / ".gitignore").read_text()

    assert ".claude/clauderfall/" in content
    assert ".mcp.json" in content
    assert ".codex/clauderfall/" in content
    assert ".codex/config.toml" in content


def test_resolve_claude_registration_command_supports_venv_and_path(tmp_path: Path) -> None:
    command, args = resolve_claude_registration_command(
        repo_root=Path("/work/clauderfall"),
        target_repo=tmp_path,
        mode="venv",
    )
    assert command == "/work/clauderfall/.venv/bin/clauderfall-mcp"
    assert args == ["--repo-root", str(tmp_path)]
    path_command, path_args = resolve_claude_registration_command(
        repo_root=Path("/work/clauderfall"),
        target_repo=tmp_path,
        mode="path",
    )
    assert path_command == "clauderfall-mcp"
    assert path_args == ["--repo-root", str(tmp_path)]


def test_build_server_args_defaults_to_docs_and_supports_custom_docs_root(tmp_path: Path) -> None:
    assert build_server_args(target_repo=tmp_path, docs_root=None) == ["--repo-root", str(tmp_path)]
    assert build_server_args(target_repo=tmp_path, docs_root="docs/clauderfall") == [
        "--repo-root",
        str(tmp_path),
        "--docs-root",
        str((tmp_path / "docs/clauderfall").resolve()),
    ]
