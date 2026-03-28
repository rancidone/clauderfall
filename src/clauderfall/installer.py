"""Repo-local installer helpers for Claude and Codex MCP registration."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

from clauderfall import __version__


CLAUDE_INSTALL_DIR = Path(".claude/clauderfall")
CLAUDE_MCP_CONFIG_PATH = Path(".mcp.json")
CODEX_INSTALL_DIR = Path(".codex/clauderfall")
CODEX_MCP_CONFIG_PATH = Path(".codex/config.toml")
CLAUDERFALL_GITIGNORE_HEADER = "# clauderfall-mcp"
CLAUDE_GITIGNORE_ENTRIES = (".claude/clauderfall/", ".mcp.json")
CODEX_GITIGNORE_ENTRIES = (".codex/clauderfall/", ".codex/config.toml")


def install_claude_mcp(
    *,
    source_repo_root: Path,
    target_repo: Path,
    server_name: str,
    docs_root: str | Path | None = None,
    python_executable: str | None = None,
) -> dict[str, object]:
    """Install Clauderfall into a target repo and register it for Claude."""

    target_repo = target_repo.resolve()
    install_root = target_repo / CLAUDE_INSTALL_DIR
    install_root.mkdir(parents=True, exist_ok=True)

    venv_python = create_repo_local_venv(
        install_root=install_root,
        source_repo_root=source_repo_root.resolve(),
        python_executable=python_executable or sys.executable,
    )
    launcher = virtualenv_bin_dir(install_root) / "clauderfall-mcp"

    update_claude_mcp_config(
        target_repo=target_repo,
        server_name=server_name,
        command=str(launcher),
        args=build_server_args(target_repo=target_repo, docs_root=docs_root),
    )
    write_install_manifest(
        install_root=install_root,
        source_repo_root=source_repo_root.resolve(),
        server_name=server_name,
        launcher=launcher,
        target_repo=target_repo,
    )
    ensure_clauderfall_gitignore(target_repo, CLAUDE_GITIGNORE_ENTRIES)
    return {
        "target_repo": str(target_repo),
        "install_root": str(install_root),
        "venv_python": str(venv_python),
        "launcher": str(launcher),
        "server_name": server_name,
        "docs_root": str(resolve_target_docs_root(target_repo=target_repo, docs_root=docs_root)),
    }


def remove_claude_mcp(*, target_repo: Path, server_name: str) -> dict[str, object]:
    """Remove Clauderfall installation artifacts and Claude MCP registration."""

    target_repo = target_repo.resolve()
    install_root = target_repo / CLAUDE_INSTALL_DIR
    config_path = target_repo / CLAUDE_MCP_CONFIG_PATH
    removed_server = remove_server_from_config(config_path=config_path, server_name=server_name)
    remove_clauderfall_gitignore(target_repo, CLAUDE_GITIGNORE_ENTRIES)
    removed_install_root = False
    if install_root.exists():
        shutil.rmtree(install_root)
        removed_install_root = True
    return {
        "target_repo": str(target_repo),
        "install_root": str(install_root),
        "server_name": server_name,
        "removed_server": removed_server,
        "removed_install_root": removed_install_root,
    }


def register_claude_mcp(
    *,
    repo_root: Path,
    target_repo: Path,
    server_name: str,
    mode: str,
    docs_root: str | Path | None = None,
) -> dict[str, object]:
    """Register the source-tree Clauderfall MCP server in a target repo's Claude config."""

    target_repo = target_repo.resolve()
    command, args = resolve_claude_registration_command(
        repo_root=repo_root.resolve(),
        target_repo=target_repo,
        mode=mode,
        docs_root=docs_root,
    )
    config_path = update_claude_mcp_config(
        target_repo=target_repo,
        server_name=server_name,
        command=command,
        args=args,
    )
    return {
        "target_repo": str(target_repo),
        "server_name": server_name,
        "command": command,
        "args": args,
        "config_path": str(config_path),
        "docs_root": str(resolve_target_docs_root(target_repo=target_repo, docs_root=docs_root)),
    }


def install_codex_mcp(
    *,
    source_repo_root: Path,
    target_repo: Path,
    server_name: str,
    docs_root: str | Path | None = None,
    python_executable: str | None = None,
) -> dict[str, object]:
    """Install Clauderfall into a target repo and register it for Codex."""

    target_repo = target_repo.resolve()
    install_root = target_repo / CODEX_INSTALL_DIR
    install_root.mkdir(parents=True, exist_ok=True)

    venv_python = create_repo_local_venv(
        install_root=install_root,
        source_repo_root=source_repo_root.resolve(),
        python_executable=python_executable or sys.executable,
    )
    launcher = virtualenv_bin_dir(install_root) / "clauderfall-mcp"

    config_path = update_codex_mcp_config(
        target_repo=target_repo,
        server_name=server_name,
        command=str(launcher),
        args=build_server_args(target_repo=target_repo, docs_root=docs_root),
    )
    write_install_manifest(
        install_root=install_root,
        source_repo_root=source_repo_root.resolve(),
        server_name=server_name,
        launcher=launcher,
        target_repo=target_repo,
    )
    ensure_clauderfall_gitignore(target_repo, CODEX_GITIGNORE_ENTRIES)
    return {
        "target_repo": str(target_repo),
        "install_root": str(install_root),
        "venv_python": str(venv_python),
        "launcher": str(launcher),
        "server_name": server_name,
        "config_path": str(config_path),
        "docs_root": str(resolve_target_docs_root(target_repo=target_repo, docs_root=docs_root)),
    }


def remove_codex_mcp(*, target_repo: Path, server_name: str) -> dict[str, object]:
    """Remove Clauderfall installation artifacts and Codex MCP registration."""

    target_repo = target_repo.resolve()
    install_root = target_repo / CODEX_INSTALL_DIR
    config_path = target_repo / CODEX_MCP_CONFIG_PATH
    removed_server = remove_server_from_toml_config(config_path=config_path, server_name=server_name)
    remove_clauderfall_gitignore(target_repo, CODEX_GITIGNORE_ENTRIES)
    removed_install_root = False
    if install_root.exists():
        shutil.rmtree(install_root)
        removed_install_root = True
    return {
        "target_repo": str(target_repo),
        "install_root": str(install_root),
        "server_name": server_name,
        "removed_server": removed_server,
        "removed_install_root": removed_install_root,
    }


def register_codex_mcp(*, repo_root: Path, server_name: str, mode: str) -> str:
    """Register Clauderfall with Codex from the current source tree."""

    command = resolve_codex_command(repo_root=repo_root.resolve(), mode=mode)
    subprocess.run(["codex", "mcp", "add", server_name, "--", command], check=True)
    return command


def resolve_codex_command(*, repo_root: Path, mode: str) -> str:
    if mode == "venv":
        return str(repo_root / ".venv" / "bin" / "clauderfall-mcp")
    if mode == "path":
        return "clauderfall-mcp"
    raise ValueError(f"unsupported mode: {mode}")


def resolve_claude_registration_command(
    *,
    repo_root: Path,
    target_repo: Path,
    mode: str,
    docs_root: str | Path | None = None,
) -> tuple[str, list[str]]:
    """Resolve a source-tree launch command for Claude registration."""

    repo_root_arg = build_server_args(target_repo=target_repo, docs_root=docs_root)
    if mode == "venv":
        return str(repo_root / ".venv" / "bin" / "clauderfall-mcp"), repo_root_arg
    if mode == "path":
        return "clauderfall-mcp", repo_root_arg
    raise ValueError(f"unsupported mode: {mode}")


def create_repo_local_venv(*, install_root: Path, source_repo_root: Path, python_executable: str) -> Path:
    """Create or update the repo-local venv for a target repo install."""

    venv_root = install_root / ".venv"
    subprocess.run([python_executable, "-m", "venv", str(venv_root)], check=True)
    venv_python = virtualenv_bin_dir(install_root) / "python"
    subprocess.run([str(venv_python), "-m", "pip", "install", "--upgrade", "pip"], check=True)
    subprocess.run([str(venv_python), "-m", "pip", "install", str(source_repo_root)], check=True)
    return venv_python


def virtualenv_bin_dir(install_root: Path) -> Path:
    """Return the venv bin directory for the current platform."""

    if sys.platform == "win32":
        return install_root / ".venv" / "Scripts"
    return install_root / ".venv" / "bin"


def update_claude_mcp_config(*, target_repo: Path, server_name: str, command: str, args: list[str]) -> Path:
    """Upsert the Claude MCP server entry for Clauderfall."""

    config_path = target_repo / CLAUDE_MCP_CONFIG_PATH
    config_path.parent.mkdir(parents=True, exist_ok=True)
    data = load_json_file(config_path)
    servers = data.setdefault("mcpServers", {})
    servers[server_name] = {
        "command": command,
        "args": args,
        "transport": "stdio",
    }
    config_path.write_text(json.dumps(data, indent=2) + "\n")
    return config_path


def remove_server_from_config(*, config_path: Path, server_name: str) -> bool:
    """Remove one server entry from the Claude MCP config if it exists."""

    if not config_path.exists():
        return False

    data = load_json_file(config_path)
    servers = data.get("mcpServers", {})
    if server_name not in servers:
        return False

    del servers[server_name]
    if servers:
        data["mcpServers"] = servers
        config_path.write_text(json.dumps(data, indent=2) + "\n")
    else:
        config_path.unlink()
    return True


def update_codex_mcp_config(*, target_repo: Path, server_name: str, command: str, args: list[str]) -> Path:
    """Upsert the Codex MCP server entry for Clauderfall in repo-local config."""

    config_path = target_repo / CODEX_MCP_CONFIG_PATH
    config_path.parent.mkdir(parents=True, exist_ok=True)
    existing = load_toml_file(config_path)
    mcp_servers = existing.get("mcp_servers", {})
    mcp_servers[server_name] = {"command": command, "args": args}
    config_path.write_text(render_codex_config(mcp_servers))
    return config_path


def remove_server_from_toml_config(*, config_path: Path, server_name: str) -> bool:
    """Remove one server entry from the Codex TOML config if it exists."""

    if not config_path.exists():
        return False

    existing = load_toml_file(config_path)
    mcp_servers = dict(existing.get("mcp_servers", {}))
    if server_name not in mcp_servers:
        return False

    del mcp_servers[server_name]
    if mcp_servers:
        config_path.write_text(render_codex_config(mcp_servers))
    else:
        config_path.unlink()
    return True


def write_install_manifest(
    *,
    install_root: Path,
    source_repo_root: Path,
    server_name: str,
    launcher: Path,
    target_repo: Path,
) -> Path:
    """Record the installed Clauderfall snapshot metadata for later inspection."""

    manifest_path = install_root / "install-manifest.json"
    manifest = {
        "installed_from_repo": str(source_repo_root),
        "installed_version": __version__,
        "server_name": server_name,
        "launcher": str(launcher),
        "target_repo": str(target_repo),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest_path


def ensure_clauderfall_gitignore(target_repo: Path, entries: tuple[str, ...]) -> Path:
    """Ensure the installed Clauderfall artifacts remain ignored by git."""

    gitignore_path = target_repo / ".gitignore"
    existing_lines = gitignore_path.read_text().splitlines() if gitignore_path.exists() else []
    updated_lines = list(existing_lines)

    if CLAUDERFALL_GITIGNORE_HEADER not in updated_lines:
        if updated_lines and updated_lines[-1] != "":
            updated_lines.append("")
        updated_lines.append(CLAUDERFALL_GITIGNORE_HEADER)

    for entry in entries:
        if entry not in updated_lines:
            updated_lines.append(entry)

    gitignore_path.write_text("\n".join(updated_lines).rstrip("\n") + "\n")
    return gitignore_path


def remove_clauderfall_gitignore(target_repo: Path, entries: tuple[str, ...]) -> Path:
    """Remove Clauderfall installer ignore entries when uninstalling."""

    gitignore_path = target_repo / ".gitignore"
    if not gitignore_path.exists():
        return gitignore_path

    updated_lines = gitignore_path.read_text().splitlines()
    original_lines = list(updated_lines)

    for entry in entries:
        updated_lines = [line for line in updated_lines if line != entry]

    managed_lines = [line for line in updated_lines if line in (*CLAUDE_GITIGNORE_ENTRIES, *CODEX_GITIGNORE_ENTRIES)]
    if not managed_lines:
        updated_lines = [line for line in updated_lines if line != CLAUDERFALL_GITIGNORE_HEADER]

    while updated_lines and updated_lines[-1] == "":
        updated_lines.pop()

    if not updated_lines:
        gitignore_path.unlink()
        return gitignore_path

    if updated_lines != original_lines:
        gitignore_path.write_text("\n".join(updated_lines) + "\n")
    return gitignore_path


def load_json_file(path: Path) -> dict[str, object]:
    """Load a JSON object file or return an empty object when absent."""

    if not path.exists():
        return {}
    return json.loads(path.read_text())


def load_toml_file(path: Path) -> dict[str, object]:
    """Load a TOML object file or return an empty object when absent."""

    if not path.exists():
        return {}
    return tomllib.loads(path.read_text())


def render_codex_config(mcp_servers: dict[str, object]) -> str:
    """Render the minimal Codex MCP config for Clauderfall installs."""

    lines: list[str] = []
    for name, server in sorted(mcp_servers.items()):
        lines.append(f"[mcp_servers.{name}]")
        lines.append(f'command = "{server["command"]}"')
        if server.get("args"):
            rendered_args = ", ".join(f'"{arg}"' for arg in server["args"])
            lines.append(f"args = [{rendered_args}]")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def build_server_args(*, target_repo: Path, docs_root: str | Path | None) -> list[str]:
    """Build common stdio server launch args for the target repo."""

    args = ["--repo-root", str(target_repo)]
    resolved_docs_root = resolve_target_docs_root(
        target_repo=target_repo,
        docs_root=docs_root,
    )
    default_docs_root = (target_repo.resolve() / "docs").resolve()
    if resolved_docs_root != default_docs_root:
        args.extend(["--docs-root", str(resolved_docs_root)])
    return args


def resolve_target_docs_root(*, target_repo: Path, docs_root: str | Path | None) -> Path:
    """Resolve the effective docs root for one target repo installation."""

    target_repo = target_repo.resolve()
    candidate = Path("docs") if docs_root is None else Path(docs_root)
    if not candidate.is_absolute():
        candidate = target_repo / candidate
    return candidate.resolve()

