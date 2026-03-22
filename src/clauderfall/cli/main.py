"""Local operator CLI."""

from __future__ import annotations

import json
from pathlib import Path

import typer

from clauderfall.artifacts.design import DesignArtifact
from clauderfall.artifacts.discovery import DiscoveryArtifact
from clauderfall.artifacts.task import TaskArtifact
from clauderfall.persistence.db import create_session_factory
from clauderfall.persistence.models import Base
from clauderfall.persistence.repositories import (
    SqlAlchemyDesignArtifactRepository,
    SqlAlchemyDiscoveryArtifactRepository,
    SqlAlchemyTaskArtifactRepository,
)
from clauderfall.services.artifact_service import ArtifactService


app = typer.Typer(no_args_is_help=True)


def build_artifact_service(db_path: Path | None = None) -> ArtifactService:
    """Create the shared artifact service for CLI commands."""

    session_factory = create_session_factory(db_path=db_path)
    session = session_factory()
    Base.metadata.create_all(bind=session.get_bind())
    discovery_repository = SqlAlchemyDiscoveryArtifactRepository(session=session)
    design_repository = SqlAlchemyDesignArtifactRepository(session=session)
    task_repository = SqlAlchemyTaskArtifactRepository(session=session)
    return ArtifactService(
        discovery_repository=discovery_repository,
        design_repository=design_repository,
        task_repository=task_repository,
    )


@app.command("validate-discovery")
def validate_discovery(
    input_path: Path,
    db_path: Path | None = typer.Option(None, "--db-path"),
) -> None:
    """Validate a Discovery Artifact JSON file."""

    artifact = DiscoveryArtifact.model_validate_json(input_path.read_text())
    issues = build_artifact_service(db_path=db_path).validate_discovery(artifact)

    if issues:
        typer.echo(json.dumps({"valid": False, "issues": issues}, indent=2))
        raise typer.Exit(code=1)

    typer.echo(json.dumps({"valid": True, "issues": []}, indent=2))


@app.command("save-discovery")
def save_discovery(
    artifact_id: str,
    input_path: Path,
    version: int | None = None,
    db_path: Path | None = typer.Option(None, "--db-path"),
) -> None:
    """Persist a Discovery Artifact JSON file."""

    artifact = DiscoveryArtifact.model_validate_json(input_path.read_text())
    service = build_artifact_service(db_path=db_path)
    try:
        persisted_version = service.save_discovery(artifact_id=artifact_id, artifact=artifact, version=version)
    except ValueError as exc:
        typer.echo(json.dumps({"saved": False, "error": str(exc)}, indent=2))
        raise typer.Exit(code=1) from exc
    typer.echo(json.dumps({"saved": True, "artifact_id": artifact_id, "version": persisted_version}, indent=2))


@app.command("check-discovery-handoff")
def check_discovery_handoff(
    input_path: Path,
    db_path: Path | None = typer.Option(None, "--db-path"),
) -> None:
    """Evaluate Discovery-to-Design handoff preconditions."""

    artifact = DiscoveryArtifact.model_validate_json(input_path.read_text())
    result = build_artifact_service(db_path=db_path).check_discovery_handoff(artifact)
    typer.echo(result.model_dump_json(indent=2))


@app.command("validate-design")
def validate_design(
    input_path: Path,
    db_path: Path | None = typer.Option(None, "--db-path"),
) -> None:
    """Validate a Design Artifact JSON file."""

    artifact = DesignArtifact.model_validate_json(input_path.read_text())
    issues = build_artifact_service(db_path=db_path).validate_design(artifact)

    if issues:
        typer.echo(json.dumps({"valid": False, "issues": issues}, indent=2))
        raise typer.Exit(code=1)

    typer.echo(json.dumps({"valid": True, "issues": []}, indent=2))


@app.command("save-design")
def save_design(
    artifact_id: str,
    input_path: Path,
    version: int | None = None,
    db_path: Path | None = typer.Option(None, "--db-path"),
) -> None:
    """Persist a Design Artifact JSON file."""

    artifact = DesignArtifact.model_validate_json(input_path.read_text())
    service = build_artifact_service(db_path=db_path)
    try:
        persisted_version = service.save_design(artifact_id=artifact_id, artifact=artifact, version=version)
    except ValueError as exc:
        typer.echo(json.dumps({"saved": False, "error": str(exc)}, indent=2))
        raise typer.Exit(code=1) from exc
    typer.echo(json.dumps({"saved": True, "artifact_id": artifact_id, "version": persisted_version}, indent=2))


@app.command("check-design-handoff")
def check_design_handoff(
    input_path: Path,
    db_path: Path | None = typer.Option(None, "--db-path"),
) -> None:
    """Evaluate Design-to-Task handoff preconditions."""

    artifact = DesignArtifact.model_validate_json(input_path.read_text())
    result = build_artifact_service(db_path=db_path).check_design_handoff(artifact)
    typer.echo(result.model_dump_json(indent=2))


@app.command("validate-task")
def validate_task(
    input_path: Path,
    db_path: Path | None = typer.Option(None, "--db-path"),
) -> None:
    """Validate a Task Artifact JSON file."""

    artifact = TaskArtifact.model_validate_json(input_path.read_text())
    issues = build_artifact_service(db_path=db_path).validate_task(artifact)

    if issues:
        typer.echo(json.dumps({"valid": False, "issues": issues}, indent=2))
        raise typer.Exit(code=1)

    typer.echo(json.dumps({"valid": True, "issues": []}, indent=2))


@app.command("save-task")
def save_task(
    artifact_id: str,
    input_path: Path,
    version: int | None = None,
    db_path: Path | None = typer.Option(None, "--db-path"),
) -> None:
    """Persist a Task Artifact JSON file."""

    artifact = TaskArtifact.model_validate_json(input_path.read_text())
    service = build_artifact_service(db_path=db_path)
    try:
        persisted_version = service.save_task(artifact_id=artifact_id, artifact=artifact, version=version)
    except ValueError as exc:
        typer.echo(json.dumps({"saved": False, "error": str(exc)}, indent=2))
        raise typer.Exit(code=1) from exc
    typer.echo(json.dumps({"saved": True, "artifact_id": artifact_id, "version": persisted_version}, indent=2))


@app.command("check-task-handoff")
def check_task_handoff(
    input_path: Path,
    db_path: Path | None = typer.Option(None, "--db-path"),
) -> None:
    """Evaluate Task-to-Context handoff preconditions."""

    artifact = TaskArtifact.model_validate_json(input_path.read_text())
    result = build_artifact_service(db_path=db_path).check_task_handoff(artifact)
    typer.echo(result.model_dump_json(indent=2))


if __name__ == "__main__":
    app()
