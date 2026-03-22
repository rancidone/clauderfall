"""Repository layer for persisted artifacts."""

from __future__ import annotations

from typing import Protocol

from sqlalchemy.orm import Session

from clauderfall.artifacts.discovery import DiscoveryArtifact
from clauderfall.persistence.models import ArtifactRecord


class DiscoveryArtifactRepository(Protocol):
    """Repository protocol for Discovery Artifact persistence."""

    def upsert(self, artifact_id: str, artifact: DiscoveryArtifact, version: int = 1) -> None:
        """Persist an artifact version."""

    def get(self, artifact_id: str) -> DiscoveryArtifact | None:
        """Load an artifact by id."""


class SqlAlchemyDiscoveryArtifactRepository:
    """SQLAlchemy-backed repository for discovery artifacts."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def upsert(self, artifact_id: str, artifact: DiscoveryArtifact, version: int = 1) -> None:
        record = ArtifactRecord(
            artifact_id=artifact_id,
            artifact_kind="discovery",
            version=version,
            readiness_state=artifact.completion_status.readiness_state.value,
            body_json=artifact.model_dump(mode="json"),
            source_artifact_ids=[],
        )
        self._session.merge(record)
        self._session.commit()

    def get(self, artifact_id: str) -> DiscoveryArtifact | None:
        record = self._session.get(ArtifactRecord, artifact_id)
        if record is None:
            return None
        return DiscoveryArtifact.model_validate(record.body_json)

