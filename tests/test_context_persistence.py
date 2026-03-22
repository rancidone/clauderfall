from pathlib import Path

from sqlalchemy.orm import Session

from clauderfall.artifacts.context import ContextPacket
from clauderfall.persistence.db import create_session_factory
from clauderfall.persistence.models import ArtifactRecord, Base
from clauderfall.persistence.repositories import SqlAlchemyContextPacketRepository


def build_repository(db_path: Path) -> tuple[Session, SqlAlchemyContextPacketRepository]:
    session_factory = create_session_factory(db_path=db_path)
    session = session_factory()
    Base.metadata.create_all(bind=session.get_bind())
    return session, SqlAlchemyContextPacketRepository(session=session)


def test_context_repository_round_trip_persists_packet_body_and_metadata(
    tmp_path: Path,
    valid_context_packet: ContextPacket,
) -> None:
    db_path = tmp_path / "clauderfall.db"
    session, repository = build_repository(db_path)

    persisted_version = repository.create(
        "context-1",
        valid_context_packet,
        upstream_artifact_refs=["task:task-1@1", "design:design-1@1"],
    )
    reloaded = repository.get_latest("context-1")
    exact = repository.get_version("context-1", 1)
    record = session.get(ArtifactRecord, {"artifact_id": "context-1", "version": 1})

    assert persisted_version == 1
    assert reloaded == valid_context_packet
    assert exact == valid_context_packet
    assert record is not None
    assert record.artifact_kind == "context_packet"
    assert record.version == 1
    assert record.readiness_state == "ready"
    assert record.upstream_artifact_refs == ["task:task-1@1", "design:design-1@1"]


def test_context_repository_appends_new_versions_without_overwriting(
    tmp_path: Path,
    valid_context_packet: ContextPacket,
) -> None:
    db_path = tmp_path / "clauderfall.db"
    _, repository = build_repository(db_path)

    first_version = repository.create("context-1", valid_context_packet)
    valid_context_packet.exclusions[0].reason = "Out of scope and not required for safe execution."
    second_version = repository.create("context-1", valid_context_packet)

    first = repository.get_version("context-1", 1)
    latest = repository.get_latest("context-1")

    assert first_version == 1
    assert second_version == 2
    assert first is not None
    assert latest is not None
    assert first.exclusions[0].reason == "Historically relevant but not execution-relevant for the task."
    assert latest.exclusions[0].reason == "Out of scope and not required for safe execution."
