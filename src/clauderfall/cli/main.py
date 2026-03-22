"""Local operator CLI."""

from __future__ import annotations

import json
from pathlib import Path

import typer

from clauderfall.artifacts.common import ArtifactKind, ArtifactVersionRef
from clauderfall.artifacts.context import ContextAssemblyItem, ContextPacket, ExclusionRecord
from clauderfall.artifacts.design import DesignArtifact
from clauderfall.artifacts.discovery import DiscoveryArtifact
from clauderfall.artifacts.task import TaskArtifact
from clauderfall.persistence.db import create_session_factory
from clauderfall.persistence.models import Base
from clauderfall.persistence.repositories import (
    SqlAlchemyArtifactIndexRepository,
    SqlAlchemyContextPacketRepository,
    SqlAlchemyDesignArtifactRepository,
    SqlAlchemyDiscoveryArtifactRepository,
    SqlAlchemyTaskArtifactRepository,
)
from clauderfall.services.artifact_service import ArtifactService
from clauderfall.services.discovery_draft_service import DiscoveryProposal, StaticDiscoveryProposalProvider
from clauderfall.skills.loader import list_skills, load_skill


app = typer.Typer(no_args_is_help=True)


def build_artifact_service(db_path: Path | None = None) -> ArtifactService:
    """Create the shared artifact service for CLI commands."""

    session_factory = create_session_factory(db_path=db_path)
    session = session_factory()
    Base.metadata.create_all(bind=session.get_bind())
    discovery_repository = SqlAlchemyDiscoveryArtifactRepository(session=session)
    design_repository = SqlAlchemyDesignArtifactRepository(session=session)
    task_repository = SqlAlchemyTaskArtifactRepository(session=session)
    context_repository = SqlAlchemyContextPacketRepository(session=session)
    artifact_index_repository = SqlAlchemyArtifactIndexRepository(session=session)
    return ArtifactService(
        discovery_repository=discovery_repository,
        design_repository=design_repository,
        task_repository=task_repository,
        context_repository=context_repository,
        artifact_index_repository=artifact_index_repository,
    )


@app.command("list-skills")
def list_skills_command() -> None:
    """List repository-local skills."""

    payload = [
        {
            "name": definition.name,
            "description": definition.description,
            "path": str(definition.path),
        }
        for definition in list_skills()
    ]
    typer.echo(json.dumps({"skills": payload}, indent=2))


@app.command("show-skill")
def show_skill(name: str) -> None:
    """Show one repository-local skill."""

    try:
        definition = load_skill(name)
    except (FileNotFoundError, ValueError) as exc:
        typer.echo(json.dumps({"found": False, "error": str(exc)}, indent=2))
        raise typer.Exit(code=1) from exc

    typer.echo(
        json.dumps(
            {
                "found": True,
                "name": definition.name,
                "description": definition.description,
                "path": str(definition.path),
                "instructions": definition.instructions,
            },
            indent=2,
        )
    )


def parse_artifact_ref(value: str) -> ArtifactVersionRef:
    """Parse a version-qualified artifact ref like kind:artifact-id@3."""

    kind_and_id, separator, version_text = value.rpartition("@")
    if separator == "":
        raise ValueError(f"artifact ref must include '@<version>': {value}")
    kind_text, kind_separator, artifact_id = kind_and_id.partition(":")
    if kind_separator == "" or not artifact_id:
        raise ValueError(f"artifact ref must be formatted as <kind>:<artifact_id>@<version>: {value}")
    try:
        artifact_kind = ArtifactKind(kind_text)
    except ValueError as exc:
        raise ValueError(f"unknown artifact kind '{kind_text}' in ref '{value}'") from exc
    try:
        version = int(version_text)
    except ValueError as exc:
        raise ValueError(f"artifact ref version must be an integer in ref '{value}'") from exc
    return ArtifactVersionRef(artifact_kind=artifact_kind, artifact_id=artifact_id, version=version)


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
    upstream_ref: list[str] = typer.Option(None, "--upstream-ref"),
    db_path: Path | None = typer.Option(None, "--db-path"),
) -> None:
    """Persist a Discovery Artifact JSON file."""

    artifact = DiscoveryArtifact.model_validate_json(input_path.read_text())
    service = build_artifact_service(db_path=db_path)
    try:
        persisted_version = service.save_discovery(
            artifact_id=artifact_id,
            artifact=artifact,
            version=version,
            upstream_artifact_refs=upstream_ref,
        )
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


@app.command("start-discovery-session")
def start_discovery_session(
    artifact_id: str,
    version: int | None = typer.Option(None, "--version"),
    db_path: Path | None = typer.Option(None, "--db-path"),
) -> None:
    """Load the current Discovery session state for an artifact lineage."""

    session = build_artifact_service(db_path=db_path).start_discovery_session(
        artifact_id=artifact_id,
        version=version,
    )
    typer.echo(session.model_dump_json(indent=2))


@app.command("prepare-discovery-turn")
def prepare_discovery_turn(
    artifact_id: str,
    user_turn: str,
    version: int | None = typer.Option(None, "--version"),
    db_path: Path | None = typer.Option(None, "--db-path"),
) -> None:
    """Prepare a Discovery turn payload for a conversational driver."""

    payload = build_artifact_service(db_path=db_path).prepare_discovery_turn(
        artifact_id=artifact_id,
        user_turn=user_turn,
        version=version,
    )
    typer.echo(payload.model_dump_json(indent=2))


@app.command("review-discovery-draft")
def review_discovery_draft(
    input_path: Path,
    db_path: Path | None = typer.Option(None, "--db-path"),
) -> None:
    """Review a candidate Discovery Artifact revision deterministically."""

    artifact = DiscoveryArtifact.model_validate_json(input_path.read_text())
    review = build_artifact_service(db_path=db_path).review_discovery_draft(artifact)
    typer.echo(review.model_dump_json(indent=2))


@app.command("propose-discovery-revision")
def propose_discovery_revision(
    artifact_id: str,
    user_turn: str,
    proposal_path: Path = typer.Option(..., "--proposal-path"),
    version: int | None = typer.Option(None, "--version"),
    db_path: Path | None = typer.Option(None, "--db-path"),
) -> None:
    """Run the proposal/review loop using a file-backed proposal provider."""

    proposal = DiscoveryProposal.model_validate_json(proposal_path.read_text())
    provider = StaticDiscoveryProposalProvider(proposal=proposal)
    result = build_artifact_service(db_path=db_path).propose_discovery_revision(
        artifact_id=artifact_id,
        user_turn=user_turn,
        provider=provider,
        version=version,
    )
    typer.echo(result.model_dump_json(indent=2))


@app.command("save-discovery-revision")
def save_discovery_revision(
    artifact_id: str,
    input_path: Path,
    version: int | None = typer.Option(None, "--version"),
    db_path: Path | None = typer.Option(None, "--db-path"),
) -> None:
    """Persist a Discovery revision only if it passes deterministic validation."""

    artifact = DiscoveryArtifact.model_validate_json(input_path.read_text())
    service = build_artifact_service(db_path=db_path)
    try:
        persisted_version, review = service.save_discovery_revision(
            artifact_id=artifact_id,
            artifact=artifact,
            version=version,
        )
    except ValueError as exc:
        typer.echo(json.dumps({"saved": False, "error": str(exc)}, indent=2))
        raise typer.Exit(code=1) from exc

    typer.echo(
        json.dumps(
            {
                "saved": True,
                "artifact_id": artifact_id,
                "version": persisted_version,
                "review": review.model_dump(mode="json"),
            },
            indent=2,
        )
    )


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
    upstream_ref: list[str] = typer.Option(None, "--upstream-ref"),
    db_path: Path | None = typer.Option(None, "--db-path"),
) -> None:
    """Persist a Design Artifact JSON file."""

    artifact = DesignArtifact.model_validate_json(input_path.read_text())
    service = build_artifact_service(db_path=db_path)
    try:
        persisted_version = service.save_design(
            artifact_id=artifact_id,
            artifact=artifact,
            version=version,
            upstream_artifact_refs=upstream_ref,
        )
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
    upstream_ref: list[str] = typer.Option(None, "--upstream-ref"),
    db_path: Path | None = typer.Option(None, "--db-path"),
) -> None:
    """Persist a Task Artifact JSON file."""

    artifact = TaskArtifact.model_validate_json(input_path.read_text())
    service = build_artifact_service(db_path=db_path)
    try:
        persisted_version = service.save_task(
            artifact_id=artifact_id,
            artifact=artifact,
            version=version,
            upstream_artifact_refs=upstream_ref,
        )
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


@app.command("validate-context")
def validate_context(
    input_path: Path,
    db_path: Path | None = typer.Option(None, "--db-path"),
) -> None:
    """Validate a Context Packet JSON file."""

    packet = ContextPacket.model_validate_json(input_path.read_text())
    issues = build_artifact_service(db_path=db_path).validate_context(packet)

    if issues:
        typer.echo(json.dumps({"valid": False, "issues": issues}, indent=2))
        raise typer.Exit(code=1)

    typer.echo(json.dumps({"valid": True, "issues": []}, indent=2))


@app.command("save-context")
def save_context(
    artifact_id: str,
    input_path: Path,
    version: int | None = None,
    upstream_ref: list[str] = typer.Option(None, "--upstream-ref"),
    db_path: Path | None = typer.Option(None, "--db-path"),
) -> None:
    """Persist a Context Packet JSON file."""

    packet = ContextPacket.model_validate_json(input_path.read_text())
    service = build_artifact_service(db_path=db_path)
    try:
        persisted_version = service.save_context(
            artifact_id=artifact_id,
            packet=packet,
            version=version,
            upstream_artifact_refs=upstream_ref,
        )
    except ValueError as exc:
        typer.echo(json.dumps({"saved": False, "error": str(exc)}, indent=2))
        raise typer.Exit(code=1) from exc
    typer.echo(json.dumps({"saved": True, "artifact_id": artifact_id, "version": persisted_version}, indent=2))


@app.command("assemble-context")
def assemble_context(
    task_path: Path,
    supporting_items_path: Path,
    exclusions_path: Path | None = typer.Option(None, "--exclusions-path"),
    artifact_id: str | None = typer.Option(None, "--artifact-id"),
    db_path: Path | None = typer.Option(None, "--db-path"),
) -> None:
    """Assemble a Context Packet from a Task Artifact and explicit supporting inputs."""

    task_artifact = TaskArtifact.model_validate_json(task_path.read_text())
    supporting_items = [ContextAssemblyItem.model_validate(item) for item in json.loads(supporting_items_path.read_text())]
    exclusions = None
    if exclusions_path is not None:
        exclusions = [ExclusionRecord.model_validate(item) for item in json.loads(exclusions_path.read_text())]

    service = build_artifact_service(db_path=db_path)
    try:
        packet = service.assemble_context(
            task_artifact=task_artifact,
            supporting_items=supporting_items,
            exclusions=exclusions,
        )
    except ValueError as exc:
        typer.echo(json.dumps({"assembled": False, "error": str(exc)}, indent=2))
        raise typer.Exit(code=1) from exc

    payload = packet.model_dump(mode="json")
    if artifact_id is not None:
        version = service.save_context(artifact_id=artifact_id, packet=packet)
        typer.echo(json.dumps({"assembled": True, "saved": True, "artifact_id": artifact_id, "version": version, "packet": payload}, indent=2))
        return

    typer.echo(json.dumps({"assembled": True, "saved": False, "packet": payload}, indent=2))


@app.command("assemble-context-from-refs")
def assemble_context_from_refs(
    task_ref: str,
    supporting_ref: list[str] = typer.Argument(...),
    exclusions_path: Path | None = typer.Option(None, "--exclusions-path"),
    artifact_id: str | None = typer.Option(None, "--artifact-id"),
    db_path: Path | None = typer.Option(None, "--db-path"),
) -> None:
    """Assemble a Context Packet from persisted artifact refs."""

    exclusions = None
    if exclusions_path is not None:
        exclusions = [ExclusionRecord.model_validate(item) for item in json.loads(exclusions_path.read_text())]

    service = build_artifact_service(db_path=db_path)
    try:
        parsed_task_ref = parse_artifact_ref(task_ref)
        parsed_supporting_refs = [parse_artifact_ref(value) for value in supporting_ref]
        packet, upstream_artifact_refs = service.assemble_context_from_refs(
            task_ref=parsed_task_ref,
            supporting_refs=parsed_supporting_refs,
            exclusions=exclusions,
        )
    except ValueError as exc:
        typer.echo(json.dumps({"assembled": False, "error": str(exc)}, indent=2))
        raise typer.Exit(code=1) from exc

    payload = packet.model_dump(mode="json")
    if artifact_id is not None:
        version = service.save_context(
            artifact_id=artifact_id,
            packet=packet,
            upstream_artifact_refs=upstream_artifact_refs,
        )
        typer.echo(
            json.dumps(
                {
                    "assembled": True,
                    "saved": True,
                    "artifact_id": artifact_id,
                    "version": version,
                    "upstream_artifact_refs": upstream_artifact_refs,
                    "packet": payload,
                },
                indent=2,
            )
        )
        return

    typer.echo(
        json.dumps(
            {
                "assembled": True,
                "saved": False,
                "upstream_artifact_refs": upstream_artifact_refs,
                "packet": payload,
            },
            indent=2,
        )
    )


@app.command("query-trace-link")
def query_trace_link(
    trace_link: str,
    db_path: Path | None = typer.Option(None, "--db-path"),
) -> None:
    """Query persisted artifact versions by indexed trace link."""

    matches = build_artifact_service(db_path=db_path).query_trace_link(trace_link)
    typer.echo(
        json.dumps(
            {
                "trace_link": trace_link,
                "matches": [match.model_dump(mode="json") for match in matches],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    app()
