"""Local operator CLI."""

from __future__ import annotations

import json
from pathlib import Path

import typer

from clauderfall.artifacts.discovery import DiscoveryArtifact
from clauderfall.persistence.db import create_session_factory
from clauderfall.persistence.models import Base
from clauderfall.persistence.repositories import SqlAlchemyDiscoveryArtifactRepository
from clauderfall.services.artifact_service import ArtifactService


app = typer.Typer(no_args_is_help=True)


def build_artifact_service(db_path: Path | None = None) -> ArtifactService:
    """Create the shared artifact service for CLI commands."""

    session_factory = create_session_factory(db_path=db_path)
    session = session_factory()
    Base.metadata.create_all(bind=session.get_bind())
    repository = SqlAlchemyDiscoveryArtifactRepository(session=session)
    return ArtifactService(discovery_repository=repository)


@app.command("validate-discovery")
def validate_discovery(input_path: Path) -> None:
    """Validate a Discovery Artifact JSON file."""

    artifact = DiscoveryArtifact.model_validate_json(input_path.read_text())
    issues = build_artifact_service().validate_discovery(artifact)

    if issues:
        typer.echo(json.dumps({"valid": False, "issues": issues}, indent=2))
        raise typer.Exit(code=1)

    typer.echo(json.dumps({"valid": True, "issues": []}, indent=2))


@app.command("save-discovery")
def save_discovery(artifact_id: str, input_path: Path, version: int = 1) -> None:
    """Persist a Discovery Artifact JSON file."""

    artifact = DiscoveryArtifact.model_validate_json(input_path.read_text())
    service = build_artifact_service()
    service.save_discovery(artifact_id=artifact_id, artifact=artifact, version=version)
    typer.echo(json.dumps({"saved": True, "artifact_id": artifact_id, "version": version}, indent=2))


@app.command("check-discovery-handoff")
def check_discovery_handoff(input_path: Path) -> None:
    """Evaluate Discovery-to-Design handoff preconditions."""

    artifact = DiscoveryArtifact.model_validate_json(input_path.read_text())
    result = build_artifact_service().check_discovery_handoff(artifact)
    typer.echo(result.model_dump_json(indent=2))


if __name__ == "__main__":
    app()

