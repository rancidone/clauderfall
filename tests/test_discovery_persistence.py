from pathlib import Path

from sqlalchemy.orm import Session

from clauderfall.artifacts.discovery import DiscoveryArtifact
from clauderfall.persistence.db import create_session_factory
from clauderfall.persistence.models import ArtifactRecord, Base
from clauderfall.persistence.repositories import SqlAlchemyDiscoveryArtifactRepository


def build_repository(db_path: Path) -> tuple[Session, SqlAlchemyDiscoveryArtifactRepository]:
    session_factory = create_session_factory(db_path=db_path)
    session = session_factory()
    Base.metadata.create_all(bind=session.get_bind())
    return session, SqlAlchemyDiscoveryArtifactRepository(session=session)


def test_repository_round_trip_persists_artifact_body_and_metadata(
    tmp_path: Path,
    valid_discovery_artifact: DiscoveryArtifact,
) -> None:
    db_path = tmp_path / "clauderfall.db"
    session, repository = build_repository(db_path)

    persisted_version = repository.create("disc-1", valid_discovery_artifact)
    reloaded = repository.get_latest("disc-1")
    exact = repository.get_version("disc-1", 1)
    record = session.get(ArtifactRecord, {"artifact_id": "disc-1", "version": 1})

    assert persisted_version == 1
    assert reloaded == valid_discovery_artifact
    assert exact == valid_discovery_artifact
    assert record is not None
    assert record.artifact_kind == "discovery"
    assert record.version == 1
    assert record.readiness_state == "ready"


def test_repository_returns_none_for_missing_artifact(tmp_path: Path) -> None:
    db_path = tmp_path / "clauderfall.db"
    _, repository = build_repository(db_path)

    assert repository.get_latest("missing") is None
    assert repository.get_version("missing", 1) is None


def test_repository_appends_new_versions_without_overwriting(
    tmp_path: Path,
    valid_discovery_artifact: DiscoveryArtifact,
) -> None:
    db_path = tmp_path / "clauderfall.db"
    _, repository = build_repository(db_path)

    first_version = repository.create("disc-1", valid_discovery_artifact)
    valid_discovery_artifact.open_questions = ["What persistence schema should later artifacts use?"]
    second_version = repository.create("disc-1", valid_discovery_artifact)

    first = repository.get_version("disc-1", 1)
    latest = repository.get_latest("disc-1")

    assert first_version == 1
    assert second_version == 2
    assert first is not None
    assert latest is not None
    assert first.open_questions == ["Should readiness be stored or derived in code?"]
    assert latest.open_questions == ["What persistence schema should later artifacts use?"]


def test_repository_rejects_out_of_order_version(
    tmp_path: Path,
    valid_discovery_artifact: DiscoveryArtifact,
) -> None:
    db_path = tmp_path / "clauderfall.db"
    _, repository = build_repository(db_path)

    try:
        repository.create("disc-1", valid_discovery_artifact, version=2)
    except ValueError as exc:
        assert "expected next version 1" in str(exc)
    else:
        raise AssertionError("expected ValueError for out-of-order version")
