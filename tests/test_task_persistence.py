from pathlib import Path

from sqlalchemy.orm import Session

from clauderfall.artifacts.task import TaskArtifact
from clauderfall.persistence.db import create_session_factory
from clauderfall.persistence.models import ArtifactRecord, Base
from clauderfall.persistence.repositories import SqlAlchemyTaskArtifactRepository


def build_repository(db_path: Path) -> tuple[Session, SqlAlchemyTaskArtifactRepository]:
    session_factory = create_session_factory(db_path=db_path)
    session = session_factory()
    Base.metadata.create_all(bind=session.get_bind())
    return session, SqlAlchemyTaskArtifactRepository(session=session)


def test_task_repository_round_trip_persists_artifact_body_and_metadata(
    tmp_path: Path,
    valid_task_artifact: TaskArtifact,
) -> None:
    db_path = tmp_path / "clauderfall.db"
    session, repository = build_repository(db_path)

    persisted_version = repository.create("task-1", valid_task_artifact)
    reloaded = repository.get_latest("task-1")
    exact = repository.get_version("task-1", 1)
    record = session.get(ArtifactRecord, {"artifact_id": "task-1", "version": 1})

    assert persisted_version == 1
    assert reloaded == valid_task_artifact
    assert exact == valid_task_artifact
    assert record is not None
    assert record.artifact_kind == "task"
    assert record.version == 1
    assert record.readiness_state == "ready"


def test_task_repository_appends_new_versions_without_overwriting(
    tmp_path: Path,
    valid_task_artifact: TaskArtifact,
) -> None:
    db_path = tmp_path / "clauderfall.db"
    _, repository = build_repository(db_path)

    first_version = repository.create("task-1", valid_task_artifact)
    valid_task_artifact.dependencies[0] = "Design artifact validation and persistence must already be implemented."
    second_version = repository.create("task-1", valid_task_artifact)

    first = repository.get_version("task-1", 1)
    latest = repository.get_latest("task-1")

    assert first_version == 1
    assert second_version == 2
    assert first is not None
    assert latest is not None
    assert first.dependencies[0] == "Design artifact validation must already be implemented."
    assert latest.dependencies[0] == "Design artifact validation and persistence must already be implemented."
