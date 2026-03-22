from pathlib import Path

from sqlalchemy.orm import Session

from clauderfall.artifacts.design import DesignArtifact
from clauderfall.persistence.db import create_session_factory
from clauderfall.persistence.models import ArtifactRecord, Base
from clauderfall.persistence.repositories import SqlAlchemyDesignArtifactRepository


def build_repository(db_path: Path) -> tuple[Session, SqlAlchemyDesignArtifactRepository]:
    session_factory = create_session_factory(db_path=db_path)
    session = session_factory()
    Base.metadata.create_all(bind=session.get_bind())
    return session, SqlAlchemyDesignArtifactRepository(session=session)


def test_design_repository_round_trip_persists_artifact_body_and_metadata(
    tmp_path: Path,
    valid_design_artifact: DesignArtifact,
) -> None:
    db_path = tmp_path / "clauderfall.db"
    session, repository = build_repository(db_path)

    persisted_version = repository.create("design-1", valid_design_artifact)
    reloaded = repository.get_latest("design-1")
    exact = repository.get_version("design-1", 1)
    record = session.get(ArtifactRecord, {"artifact_id": "design-1", "version": 1})

    assert persisted_version == 1
    assert reloaded == valid_design_artifact
    assert exact == valid_design_artifact
    assert record is not None
    assert record.artifact_kind == "design"
    assert record.version == 1
    assert record.readiness_state == "ready"


def test_design_repository_appends_new_versions_without_overwriting(
    tmp_path: Path,
    valid_design_artifact: DesignArtifact,
) -> None:
    db_path = tmp_path / "clauderfall.db"
    _, repository = build_repository(db_path)

    first_version = repository.create("design-1", valid_design_artifact)
    valid_design_artifact.open_design_questions[0].question = "Should workflow modeling become first-class?"
    second_version = repository.create("design-1", valid_design_artifact)

    first = repository.get_version("design-1", 1)
    latest = repository.get_latest("design-1")

    assert first_version == 1
    assert second_version == 2
    assert first is not None
    assert latest is not None
    assert first.open_design_questions[0].question == "Should future design artifacts encode richer workflow structure?"
    assert latest.open_design_questions[0].question == "Should workflow modeling become first-class?"
