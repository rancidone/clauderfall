"""Repository layer for persisted artifacts."""

from __future__ import annotations

from typing import Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session

from clauderfall.artifacts.design import DesignArtifact
from clauderfall.artifacts.discovery import DiscoveryArtifact
from clauderfall.artifacts.task import TaskArtifact
from clauderfall.persistence.models import ArtifactRecord


class DiscoveryArtifactRepository(Protocol):
    """Repository protocol for Discovery Artifact persistence."""

    def create(self, artifact_id: str, artifact: DiscoveryArtifact, version: int | None = None) -> int:
        """Persist a new append-only artifact version."""

    def get_version(self, artifact_id: str, version: int) -> DiscoveryArtifact | None:
        """Load an artifact by exact version."""

    def get_latest(self, artifact_id: str) -> DiscoveryArtifact | None:
        """Load the latest artifact version."""


class DesignArtifactRepository(Protocol):
    """Repository protocol for Design Artifact persistence."""

    def create(self, artifact_id: str, artifact: DesignArtifact, version: int | None = None) -> int:
        """Persist a new append-only artifact version."""

    def get_version(self, artifact_id: str, version: int) -> DesignArtifact | None:
        """Load an artifact by exact version."""

    def get_latest(self, artifact_id: str) -> DesignArtifact | None:
        """Load the latest artifact version."""


class TaskArtifactRepository(Protocol):
    """Repository protocol for Task Artifact persistence."""

    def create(self, artifact_id: str, artifact: TaskArtifact, version: int | None = None) -> int:
        """Persist a new append-only artifact version."""

    def get_version(self, artifact_id: str, version: int) -> TaskArtifact | None:
        """Load an artifact by exact version."""

    def get_latest(self, artifact_id: str) -> TaskArtifact | None:
        """Load the latest artifact version."""


class SqlAlchemyDiscoveryArtifactRepository:
    """SQLAlchemy-backed repository for discovery artifacts."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, artifact_id: str, artifact: DiscoveryArtifact, version: int | None = None) -> int:
        next_version = self._next_version(artifact_id)
        if version is None:
            version = next_version
        elif version != next_version:
            raise ValueError(
                f"version {version} is invalid for artifact '{artifact_id}'; expected next version {next_version}"
            )

        existing_kind = self._get_artifact_kind(artifact_id)
        if existing_kind is not None and existing_kind != "discovery":
            raise ValueError(
                f"artifact '{artifact_id}' already exists as kind '{existing_kind}', not 'discovery'"
            )

        record = ArtifactRecord(
            artifact_id=artifact_id,
            artifact_kind="discovery",
            version=version,
            readiness_state=artifact.completion_status.readiness_state.value,
            body_json=artifact.model_dump(mode="json"),
            upstream_artifact_refs=[],
        )
        self._session.add(record)
        self._session.commit()
        return version

    def get_version(self, artifact_id: str, version: int) -> DiscoveryArtifact | None:
        record = self._session.get(ArtifactRecord, {"artifact_id": artifact_id, "version": version})
        if record is None:
            return None
        return DiscoveryArtifact.model_validate(record.body_json)

    def get_latest(self, artifact_id: str) -> DiscoveryArtifact | None:
        statement = (
            select(ArtifactRecord)
            .where(ArtifactRecord.artifact_id == artifact_id)
            .order_by(ArtifactRecord.version.desc())
            .limit(1)
        )
        record = self._session.execute(statement).scalar_one_or_none()
        if record is None:
            return None
        return DiscoveryArtifact.model_validate(record.body_json)

    def _next_version(self, artifact_id: str) -> int:
        statement = (
            select(ArtifactRecord.version)
            .where(ArtifactRecord.artifact_id == artifact_id)
            .order_by(ArtifactRecord.version.desc())
            .limit(1)
        )
        latest_version = self._session.execute(statement).scalar_one_or_none()
        if latest_version is None:
            return 1
        return latest_version + 1

    def _get_artifact_kind(self, artifact_id: str) -> str | None:
        statement = (
            select(ArtifactRecord.artifact_kind)
            .where(ArtifactRecord.artifact_id == artifact_id)
            .limit(1)
        )
        return self._session.execute(statement).scalar_one_or_none()


class SqlAlchemyDesignArtifactRepository:
    """SQLAlchemy-backed repository for design artifacts."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, artifact_id: str, artifact: DesignArtifact, version: int | None = None) -> int:
        next_version = self._next_version(artifact_id)
        if version is None:
            version = next_version
        elif version != next_version:
            raise ValueError(
                f"version {version} is invalid for artifact '{artifact_id}'; expected next version {next_version}"
            )

        existing_kind = self._get_artifact_kind(artifact_id)
        if existing_kind is not None and existing_kind != "design":
            raise ValueError(f"artifact '{artifact_id}' already exists as kind '{existing_kind}', not 'design'")

        record = ArtifactRecord(
            artifact_id=artifact_id,
            artifact_kind="design",
            version=version,
            readiness_state=artifact.completion_status.readiness_state.value,
            body_json=artifact.model_dump(mode="json"),
            upstream_artifact_refs=[],
        )
        self._session.add(record)
        self._session.commit()
        return version

    def get_version(self, artifact_id: str, version: int) -> DesignArtifact | None:
        record = self._session.get(ArtifactRecord, {"artifact_id": artifact_id, "version": version})
        if record is None:
            return None
        return DesignArtifact.model_validate(record.body_json)

    def get_latest(self, artifact_id: str) -> DesignArtifact | None:
        statement = (
            select(ArtifactRecord)
            .where(ArtifactRecord.artifact_id == artifact_id)
            .order_by(ArtifactRecord.version.desc())
            .limit(1)
        )
        record = self._session.execute(statement).scalar_one_or_none()
        if record is None:
            return None
        return DesignArtifact.model_validate(record.body_json)

    def _next_version(self, artifact_id: str) -> int:
        statement = (
            select(ArtifactRecord.version)
            .where(ArtifactRecord.artifact_id == artifact_id)
            .order_by(ArtifactRecord.version.desc())
            .limit(1)
        )
        latest_version = self._session.execute(statement).scalar_one_or_none()
        if latest_version is None:
            return 1
        return latest_version + 1

    def _get_artifact_kind(self, artifact_id: str) -> str | None:
        statement = (
            select(ArtifactRecord.artifact_kind)
            .where(ArtifactRecord.artifact_id == artifact_id)
            .limit(1)
        )
        return self._session.execute(statement).scalar_one_or_none()


class SqlAlchemyTaskArtifactRepository:
    """SQLAlchemy-backed repository for task artifacts."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, artifact_id: str, artifact: TaskArtifact, version: int | None = None) -> int:
        next_version = self._next_version(artifact_id)
        if version is None:
            version = next_version
        elif version != next_version:
            raise ValueError(
                f"version {version} is invalid for artifact '{artifact_id}'; expected next version {next_version}"
            )

        existing_kind = self._get_artifact_kind(artifact_id)
        if existing_kind is not None and existing_kind != "task":
            raise ValueError(f"artifact '{artifact_id}' already exists as kind '{existing_kind}', not 'task'")

        record = ArtifactRecord(
            artifact_id=artifact_id,
            artifact_kind="task",
            version=version,
            readiness_state=artifact.completion_status.readiness_state.value,
            body_json=artifact.model_dump(mode="json"),
            upstream_artifact_refs=[],
        )
        self._session.add(record)
        self._session.commit()
        return version

    def get_version(self, artifact_id: str, version: int) -> TaskArtifact | None:
        record = self._session.get(ArtifactRecord, {"artifact_id": artifact_id, "version": version})
        if record is None:
            return None
        return TaskArtifact.model_validate(record.body_json)

    def get_latest(self, artifact_id: str) -> TaskArtifact | None:
        statement = (
            select(ArtifactRecord)
            .where(ArtifactRecord.artifact_id == artifact_id)
            .order_by(ArtifactRecord.version.desc())
            .limit(1)
        )
        record = self._session.execute(statement).scalar_one_or_none()
        if record is None:
            return None
        return TaskArtifact.model_validate(record.body_json)

    def _next_version(self, artifact_id: str) -> int:
        statement = (
            select(ArtifactRecord.version)
            .where(ArtifactRecord.artifact_id == artifact_id)
            .order_by(ArtifactRecord.version.desc())
            .limit(1)
        )
        latest_version = self._session.execute(statement).scalar_one_or_none()
        if latest_version is None:
            return 1
        return latest_version + 1

    def _get_artifact_kind(self, artifact_id: str) -> str | None:
        statement = (
            select(ArtifactRecord.artifact_kind)
            .where(ArtifactRecord.artifact_id == artifact_id)
            .limit(1)
        )
        return self._session.execute(statement).scalar_one_or_none()
