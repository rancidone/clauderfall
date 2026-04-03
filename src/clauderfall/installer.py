"""Installer helpers for Clauderfall MCP registration and skill installation."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

import tomli_w

from clauderfall import __version__


CODEX_MCP_CONFIG_PATH = Path(".codex/config.toml")
PACKAGED_SKILLS_DIR = Path("src/clauderfall/skills")
CLAUDE_SKILLS_ROOT = Path(".claude/skills")
CODEX_SKILLS_ROOT = Path(".codex/skills")
GLOBAL_INSTALL_ROOT = Path.home() / ".clauderfall"
INSTALL_TARGETS = ("claude", "codex")
SKILL_ROOTS = {
    "claude": CLAUDE_SKILLS_ROOT,
    "codex": CODEX_SKILLS_ROOT,
}


def install_global(
    *,
    source_repo_root: Path,
    server_name: str,
    python_executable: str | None = None,
    debug: bool = False,
    targets: list[str] | tuple[str, ...] | None = None,
) -> dict[str, object]:
    """Install Clauderfall once and register it for one or more global clients."""

    selected_targets = normalize_install_targets(targets)
    install_result = install_global_clauderfall(
        source_repo_root=source_repo_root,
        python_executable=python_executable,
    )
    registrations = register_installed_server(
        server_name=server_name,
        launcher=install_result["launcher"],
        debug=debug,
        targets=selected_targets,
    )
    return {
        **install_result,
        "server_name": server_name,
        "targets": list(selected_targets),
        "debug": debug,
        "registrations": registrations,
    }


def register_global(
    *,
    repo_root: Path,
    server_name: str,
    mode: str,
    debug: bool = False,
    targets: list[str] | tuple[str, ...] | None = None,
) -> dict[str, object]:
    """Register the source-tree Clauderfall server for one or more global clients."""

    selected_targets = normalize_install_targets(targets)
    command = resolve_codex_command(repo_root=repo_root.resolve(), mode=mode)
    registrations = register_installed_server(
        server_name=server_name,
        launcher=command,
        debug=debug,
        targets=selected_targets,
        source_repo_root=repo_root.resolve(),
        skill_mode="symlink",
    )
    return {
        "server_name": server_name,
        "command": command,
        "targets": list(selected_targets),
        "debug": debug,
        "registrations": registrations,
    }


def remove_global(
    *,
    source_repo_root: Path,
    server_name: str,
    targets: list[str] | tuple[str, ...] | None = None,
) -> dict[str, object]:
    """Remove the global Clauderfall registration for one or more clients."""

    selected_targets = normalize_install_targets(targets)
    removals: dict[str, object] = {}
    for target in selected_targets:
        removals[target] = remove_target_registration(
            source_repo_root=source_repo_root,
            server_name=server_name,
            target=target,
        )
    return {
        "server_name": server_name,
        "targets": list(selected_targets),
        "removals": removals,
    }


def install_claude_global(
    *,
    source_repo_root: Path,
    server_name: str,
    python_executable: str | None = None,
    debug: bool = False,
) -> dict[str, object]:
    """Install Clauderfall globally and register it as a user-scoped Claude MCP server."""

    result = install_global(
        source_repo_root=source_repo_root,
        server_name=server_name,
        python_executable=python_executable,
        debug=debug,
        targets=["claude"],
    )
    register_result = result["registrations"]["claude"]
    return {
        "install_root": result["install_root"],
        "venv_python": result["venv_python"],
        "launcher": result["launcher"],
        "installed_codex_skills": result["installed_codex_skills"],
        "installed_claude_skills": result["installed_claude_skills"],
        **register_result,
        "server_name": server_name,
    }


def install_codex_global(
    *,
    source_repo_root: Path,
    server_name: str,
    python_executable: str | None = None,
    debug: bool = False,
) -> dict[str, object]:
    """Install Clauderfall globally and register it in user-scoped Codex config."""

    result = install_global(
        source_repo_root=source_repo_root,
        server_name=server_name,
        python_executable=python_executable,
        debug=debug,
        targets=["codex"],
    )
    register_result = result["registrations"]["codex"]
    return {
        "install_root": result["install_root"],
        "venv_python": result["venv_python"],
        "launcher": result["launcher"],
        "server_name": server_name,
        "config_path": register_result["config_path"],
        "debug": debug,
        "installed_codex_skills": result["installed_codex_skills"],
        "installed_claude_skills": result["installed_claude_skills"],
    }


def remove_claude_global(*, source_repo_root: Path, server_name: str) -> dict[str, object]:
    """Remove the user-scoped Claude registration and packaged Claude skills."""

    result = remove_global(
        source_repo_root=source_repo_root,
        server_name=server_name,
        targets=["claude"],
    )
    removal = result["removals"]["claude"]
    return {
        "server_name": server_name,
        "removed_skills": removal["removed_skills"],
    }


def remove_codex_global(*, source_repo_root: Path, server_name: str) -> dict[str, object]:
    """Remove the user-scoped Codex registration and packaged Codex skills."""

    result = remove_global(
        source_repo_root=source_repo_root,
        server_name=server_name,
        targets=["codex"],
    )
    removal = result["removals"]["codex"]
    return {
        "server_name": server_name,
        "removed_server": removal["removed_server"],
        "removed_skills": removal["removed_skills"],
        "config_path": removal["config_path"],
    }


def register_claude_global(*, repo_root: Path, server_name: str, mode: str, debug: bool = False) -> dict[str, object]:
    """Register the source-tree Clauderfall server globally for Claude development use."""

    result = register_global(
        repo_root=repo_root,
        server_name=server_name,
        mode=mode,
        debug=debug,
        targets=["claude"],
    )
    register_result = result["registrations"]["claude"]
    return {
        "server_name": server_name,
        "command": result["command"],
        "installed_skills": register_result["installed_skills"],
    }


def register_codex_global(*, repo_root: Path, server_name: str, mode: str, debug: bool = False) -> dict[str, object]:
    """Register the source-tree Clauderfall server globally for Codex development use."""

    result = register_global(
        repo_root=repo_root,
        server_name=server_name,
        mode=mode,
        debug=debug,
        targets=["codex"],
    )
    register_result = result["registrations"]["codex"]
    return {
        "server_name": server_name,
        "command": result["command"],
        "config_path": register_result["config_path"],
        "installed_skills": register_result["installed_skills"],
        "debug": debug,
    }


def normalize_install_targets(targets: list[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    """Normalize target selectors into a de-duplicated, ordered target tuple."""

    if not targets:
        return INSTALL_TARGETS
    normalized: list[str] = []
    for target in targets:
        if target not in INSTALL_TARGETS:
            raise ValueError(f"unsupported install target: {target}")
        if target not in normalized:
            normalized.append(target)
    return tuple(normalized)


def register_installed_server(
    *,
    server_name: str,
    launcher: str,
    debug: bool,
    targets: tuple[str, ...],
    source_repo_root: Path | None = None,
    skill_mode: str = "copy",
) -> dict[str, object]:
    """Register one launcher across selected clients and install target-specific skills."""

    registrations: dict[str, object] = {}
    for target in targets:
        if target == "claude":
            register_result = add_claude_user_mcp_server(
                server_name=server_name,
                command=launcher,
                args=[],
                debug=debug,
            )
        elif target == "codex":
            config_path = update_codex_mcp_config(
                target_repo=Path.home(),
                server_name=server_name,
                command=launcher,
                args=[],
                env={"CLAUDERFALL_DEBUG": "1"} if debug else None,
            )
            register_result = {
                "command": launcher,
                "args": [],
                "config_path": str(config_path),
                "debug": debug,
            }
        else:
            raise ValueError(f"unsupported install target: {target}")

        if source_repo_root is not None:
            register_result["installed_skills"] = install_packaged_skills(
                source_repo_root=source_repo_root,
                destination_root=Path.home() / SKILL_ROOTS[target],
                mode=skill_mode,
            )
        registrations[target] = register_result
    return registrations


def remove_target_registration(*, source_repo_root: Path, server_name: str, target: str) -> dict[str, object]:
    """Remove one target registration and its packaged skills."""

    if target == "claude":
        remove_claude_user_mcp_server(server_name=server_name)
        removed_server = True
        config_path: str | None = None
    elif target == "codex":
        config = Path.home() / CODEX_MCP_CONFIG_PATH
        removed_server = remove_server_from_toml_config(
            config_path=config,
            server_name=server_name,
        )
        config_path = str(config)
    else:
        raise ValueError(f"unsupported install target: {target}")

    removed_skills = remove_packaged_skills(
        source_repo_root=source_repo_root,
        destination_root=Path.home() / SKILL_ROOTS[target],
    )
    result = {
        "removed_server": removed_server,
        "removed_skills": removed_skills,
    }
    if config_path is not None:
        result["config_path"] = config_path
    return result


def resolve_codex_command(*, repo_root: Path, mode: str) -> str:
    if mode == "venv":
        return str(repo_root / ".venv" / "bin" / "clauderfall-mcp")
    if mode == "path":
        return "clauderfall-mcp"
    raise ValueError(f"unsupported mode: {mode}")


def create_repo_local_venv(*, install_root: Path, source_repo_root: Path, python_executable: str) -> Path:
    """Create or update the venv used for one Clauderfall installation root."""

    venv_root = install_root / ".venv"
    subprocess.run([python_executable, "-m", "venv", str(venv_root)], check=True)
    venv_python = virtualenv_bin_dir(install_root) / "python"
    subprocess.run([str(venv_python), "-m", "pip", "install", "--upgrade", "pip"], check=True)
    subprocess.run([str(venv_python), "-m", "pip", "install", str(source_repo_root)], check=True)
    return venv_python


def install_global_clauderfall(*, source_repo_root: Path, python_executable: str | None = None) -> dict[str, object]:
    """Install the Clauderfall package and packaged skills into user-global locations."""

    install_root = GLOBAL_INSTALL_ROOT
    install_root.mkdir(parents=True, exist_ok=True)
    venv_python = create_repo_local_venv(
        install_root=install_root,
        source_repo_root=source_repo_root.resolve(),
        python_executable=python_executable or sys.executable,
    )
    launcher = virtualenv_bin_dir(install_root) / "clauderfall-mcp"
    installed_codex_skills = install_packaged_skills(
        source_repo_root=source_repo_root.resolve(),
        destination_root=Path.home() / CODEX_SKILLS_ROOT,
        mode="copy",
    )
    installed_claude_skills = install_packaged_skills(
        source_repo_root=source_repo_root.resolve(),
        destination_root=Path.home() / CLAUDE_SKILLS_ROOT,
        mode="copy",
    )
    write_global_install_manifest(
        install_root=install_root,
        source_repo_root=source_repo_root.resolve(),
        launcher=launcher,
    )
    return {
        "install_root": str(install_root),
        "venv_python": str(venv_python),
        "launcher": str(launcher),
        "installed_codex_skills": installed_codex_skills,
        "installed_claude_skills": installed_claude_skills,
    }


def install_packaged_skills(*, source_repo_root: Path, destination_root: Path, mode: str) -> list[str]:
    """Install packaged Clauderfall skills into one skill root."""

    skill_dirs = list_packaged_skill_dirs(source_repo_root=source_repo_root)
    if not skill_dirs:
        return []
    destination_root.mkdir(parents=True, exist_ok=True)

    installed_names: list[str] = []
    for skill_dir in skill_dirs:
        skill_name = skill_dir.name
        destination = destination_root / skill_name
        replace_path(destination)
        if mode == "copy":
            shutil.copytree(skill_dir, destination)
        elif mode == "symlink":
            destination.symlink_to(skill_dir, target_is_directory=True)
        else:
            raise ValueError(f"unsupported skill install mode: {mode}")
        installed_names.append(skill_name)
    return installed_names


def remove_packaged_skills(*, source_repo_root: Path, destination_root: Path) -> list[str]:
    """Remove packaged Clauderfall skills from one skill root."""

    removed_names: list[str] = []
    for skill_dir in list_packaged_skill_dirs(source_repo_root=source_repo_root):
        destination = destination_root / skill_dir.name
        if destination.exists() or destination.is_symlink():
            replace_path(destination)
            removed_names.append(skill_dir.name)
    return removed_names


def list_packaged_skill_dirs(*, source_repo_root: Path) -> list[Path]:
    """Return packaged skill directories from the source repo."""

    skills_root = source_repo_root / PACKAGED_SKILLS_DIR
    if not skills_root.exists():
        return []
    return sorted(
        path
        for path in skills_root.iterdir()
        if path.is_dir() and (path / "SKILL.md").exists()
    )


def replace_path(path: Path) -> None:
    """Remove an existing file, directory, or symlink so it can be replaced."""

    if not path.exists() and not path.is_symlink():
        return
    if path.is_symlink() or path.is_file():
        path.unlink()
        return
    shutil.rmtree(path)


def write_global_install_manifest(*, install_root: Path, source_repo_root: Path, launcher: Path) -> Path:
    """Record metadata for the user-global Clauderfall installation."""

    manifest_path = install_root / "install-manifest.json"
    manifest = {
        "installed_from_repo": str(source_repo_root),
        "installed_version": __version__,
        "launcher": str(launcher),
        "scope": "user",
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest_path


def add_claude_user_mcp_server(
    *,
    server_name: str,
    command: str,
    args: list[str],
    debug: bool = False,
) -> dict[str, object]:
    """Register one user-scoped Claude MCP server through the Claude CLI."""

    subprocess.run(
        ["claude", "mcp", "remove", server_name, "--scope", "user"],
        check=False,
    )
    cmd = ["claude", "mcp", "add", server_name, "--scope", "user"]
    if debug:
        cmd += ["--env", "CLAUDERFALL_DEBUG=1"]
    cmd += ["--", command, *args]
    subprocess.run(cmd, check=True)
    return {
        "command": command,
        "args": args,
        "scope": "user",
        "debug": debug,
    }


def remove_claude_user_mcp_server(*, server_name: str) -> None:
    """Remove one user-scoped Claude MCP server through the Claude CLI."""

    subprocess.run(["claude", "mcp", "remove", server_name, "--scope", "user"], check=True)


def virtualenv_bin_dir(install_root: Path) -> Path:
    """Return the venv bin directory for the current platform."""

    if sys.platform == "win32":
        return install_root / ".venv" / "Scripts"
    return install_root / ".venv" / "bin"


def update_codex_mcp_config(
    *,
    target_repo: Path,
    server_name: str,
    command: str,
    args: list[str],
    env: dict[str, str] | None = None,
) -> Path:
    """Upsert the Codex MCP server entry for Clauderfall in one TOML config root."""

    config_path = target_repo / CODEX_MCP_CONFIG_PATH
    config_path.parent.mkdir(parents=True, exist_ok=True)
    existing = load_toml_file(config_path)
    updated = dict(existing)
    mcp_servers = dict(existing.get("mcp_servers", {}))
    server_config: dict[str, object] = {"command": command}
    if args:
        server_config["args"] = args
    if env:
        server_config["env"] = env
    mcp_servers[server_name] = server_config
    updated["mcp_servers"] = mcp_servers
    config_path.write_text(tomli_w.dumps(updated))
    return config_path


def remove_server_from_toml_config(*, config_path: Path, server_name: str) -> bool:
    """Remove one server entry from the Codex TOML config if it exists."""

    if not config_path.exists():
        return False

    existing = load_toml_file(config_path)
    updated = dict(existing)
    mcp_servers = dict(existing.get("mcp_servers", {}))
    if server_name not in mcp_servers:
        return False

    del mcp_servers[server_name]
    if mcp_servers:
        updated["mcp_servers"] = mcp_servers
    else:
        updated.pop("mcp_servers", None)

    if updated:
        config_path.write_text(tomli_w.dumps(updated))
    else:
        config_path.unlink()
    return True


def load_toml_file(path: Path) -> dict[str, object]:
    """Load a TOML object file or return an empty object when absent."""

    if not path.exists():
        return {}
    return tomllib.loads(path.read_text())
