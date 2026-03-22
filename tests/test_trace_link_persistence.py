from pathlib import Path

from sqlalchemy.orm import Session

from clauderfall.artifacts.design import DesignArtifact
from clauderfall.persistence.db import create_session_factory
from clauderfall.persistence.models import ArtifactTraceLinkRecord, Base
from clauderfall.persistence.repositories import SqlAlchemyArtifactIndexRepository, SqlAlchemyDesignArtifactRepository


def build_repositories(db_path: Path) -> tuple[Session, SqlAlchemyDesignArtifactRepository, SqlAlchemyArtifactIndexRepository]:
    session_factory = create_session_factory(db_path=db_path)
    session = session_factory()
    Base.metadata.create_all(bind=session.get_bind())
    return (
        session,
        SqlAlchemyDesignArtifactRepository(session=session),
        SqlAlchemyArtifactIndexRepository(session=session),
    )


def test_persisted_artifact_versions_index_trace_links(
    tmp_path: Path,
    valid_design_artifact: DesignArtifact,
) -> None:
    db_path = tmp_path / "clauderfall.db"
    session, repository, index_repository = build_repositories(db_path)

    repository.create("design-1", valid_design_artifact, upstream_artifact_refs=["discovery:disc-1@2"])
    matches = index_repository.find_by_trace_link("discovery.problem_definition[0]")
    rows = session.query(ArtifactTraceLinkRecord).all()

    assert rows
    assert matches
    assert matches[0].artifact_id == "design-1"
    assert matches[0].artifact_kind.value == "design"
    assert matches[0].version == 1
    assert matches[0].target_ref == "objective"
