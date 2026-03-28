"""Repository layer for persisted artifacts."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any, Protocol, TypeVar

from pydantic import BaseModel
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from clauderfall_v1.artifacts.common import ArtifactKind, ArtifactVersionRef, TraceLinkMatch
from clauderfall_v1.artifacts.context import ContextPacket
from clauderfall_v1.artifacts.design import DesignArtifact
from clauderfall_v1.artifacts.discovery import DiscoveryArtifact
from clauderfall_v1.artifacts.task import TaskArtifact
from clauderfall_v1.persistence.models import ArtifactRecord, ArtifactTraceLinkRecord


ArtifactModelT = TypeVar("ArtifactModelT", bound=BaseModel)


class DiscoveryArtifactRepository(Protocol):
    """Repository protocol for Discovery Artifact persistence."""

    def create(
        self,
        artifact_id: str,
        artifact: DiscoveryArtifact,
        version: int | None = None,
        upstream_artifact_refs: list[str] | None = None,
    ) -> int:
        """Persist a new append-only artifact version."""

    def get_version(self, artifact_id: str, version: int) -> DiscoveryArtifact | None:
        """Load an artifact by exact version."""

    def get_latest(self, artifact_id: str) -> DiscoveryArtifact | None:
        """Load the latest artifact version."""


class DesignArtifactRepository(Protocol):
    """Repository protocol for Design Artifact persistence."""

    def create(
        self,
        artifact_id: str,
        artifact: DesignArtifact,
        version: int | None = None,
        upstream_artifact_refs: list[str] | None = None,
    ) -> int:
        """Persist a new append-only artifact version."""

    def get_version(self, artifact_id: str, version: int) -> DesignArtifact | None:
        """Load an artifact by exact version."""

    def get_latest(self, artifact_id: str) -> DesignArtifact | None:
        """Load the latest artifact version."""


class TaskArtifactRepository(Protocol):
    """Repository protocol for Task Artifact persistence."""

    def create(
        self,
        artifact_id: str,
        artifact: TaskArtifact,
        version: int | None = None,
        upstream_artifact_refs: list[str] | None = None,
    ) -> int:
        """Persist a new append-only artifact version."""

    def get_version(self, artifact_id: str, version: int) -> TaskArtifact | None:
        """Load an artifact by exact version."""

    def get_latest(self, artifact_id: str) -> TaskArtifact | None:
        """Load the latest artifact version."""


class ContextPacketRepository(Protocol):
    """Repository protocol for Context Packet persistence."""

    def create(
        self,
        artifact_id: str,
        packet: ContextPacket,
        version: int | None = None,
        upstream_artifact_refs: list[str] | None = None,
    ) -> int:
        """Persist a new append-only packet version."""

    def get_version(self, artifact_id: str, version: int) -> ContextPacket | None:
        """Load a packet by exact version."""

    def get_latest(self, artifact_id: str) -> ContextPacket | None:
        """Load the latest packet version."""


class ArtifactIndexRepository(Protocol):
    """Repository protocol for artifact-level lineage and trace lookups."""

    def get_record(self, artifact_ref: ArtifactVersionRef) -> ArtifactRecord | None:
        """Load an exact persisted artifact record."""

    def get_latest_record(self, artifact_kind: ArtifactKind, artifact_id: str) -> ArtifactRecord | None:
        """Load the latest persisted artifact record for a lineage."""

    def find_by_trace_link(self, trace_link: str) -> list[TraceLinkMatch]:
        """List persisted artifact versions indexed by a trace link."""


def extract_trace_link_entries(payload: Any, *, parent_target_ref: str | None = None) -> list[tuple[str, str | None]]:
    """Collect trace-link edges from nested artifact bodies."""

    entries: list[tuple[str, str | None]] = []
    if isinstance(payload, dict):
        local_target_ref = payload.get("target_ref")
        if isinstance(local_target_ref, str):
            parent_target_ref = local_target_ref
        trace_links = payload.get("trace_links")
        if isinstance(trace_links, list):
            for trace_link in trace_links:
                if isinstance(trace_link, str):
                    entries.append((trace_link, parent_target_ref))
        for value in payload.values():
            entries.extend(extract_trace_link_entries(value, parent_target_ref=parent_target_ref))
        return entries
    if isinstance(payload, list):
        for item in payload:
            entries.extend(extract_trace_link_entries(item, parent_target_ref=parent_target_ref))
    return entries


def dedupe_strings(values: Iterable[str]) -> list[str]:
    """Preserve order while removing duplicate string values."""

    deduped: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        deduped.append(value)
    return deduped


class SqlAlchemyArtifactIndexRepository:
    """SQLAlchemy-backed repository for generic artifact lookups and indexes."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_record(self, artifact_ref: ArtifactVersionRef) -> ArtifactRecord | None:
        record = self._session.get(
            ArtifactRecord,
            {"artifact_id": artifact_ref.artifact_id, "version": artifact_ref.version},
        )
        if record is None or record.artifact_kind != artifact_ref.artifact_kind.value:
            return None
        return record

    def get_latest_record(self, artifact_kind: ArtifactKind, artifact_id: str) -> ArtifactRecord | None:
        statement = (
            select(ArtifactRecord)
            .where(ArtifactRecord.artifact_id == artifact_id, ArtifactRecord.artifact_kind == artifact_kind.value)
            .order_by(ArtifactRecord.version.desc())
            .limit(1)
        )
        return self._session.execute(statement).scalar_one_or_none()

    def find_by_trace_link(self, trace_link: str) -> list[TraceLinkMatch]:
        statement = (
            select(ArtifactTraceLinkRecord)
            .where(ArtifactTraceLinkRecord.trace_link == trace_link)
            .order_by(
                ArtifactTraceLinkRecord.artifact_kind.asc(),
                ArtifactTraceLinkRecord.artifact_id.asc(),
                ArtifactTraceLinkRecord.version.asc(),
                ArtifactTraceLinkRecord.id.asc(),
            )
        )
        matches = self._session.execute(statement).scalars().all()
        return [
            TraceLinkMatch(
                artifact_kind=ArtifactKind(match.artifact_kind),
                artifact_id=match.artifact_id,
                version=match.version,
                trace_link=match.trace_link,
                target_ref=match.target_ref,
            )
            for match in matches
        ]

    def replace_trace_links(
        self,
        artifact_kind: ArtifactKind,
        artifact_id: str,
        version: int,
        payload: dict[str, Any],
    ) -> None:
        self._session.execute(
            delete(ArtifactTraceLinkRecord).where(
                ArtifactTraceLinkRecord.artifact_id == artifact_id,
                ArtifactTraceLinkRecord.version == version,
                ArtifactTraceLinkRecord.artifact_kind == artifact_kind.value,
            )
        )
        for trace_link, target_ref in extract_trace_link_entries(payload):
            self._session.add(
                ArtifactTraceLinkRecord(
                    artifact_id=artifact_id,
                    artifact_kind=artifact_kind.value,
                    version=version,
                    trace_link=trace_link,
                    target_ref=target_ref,
                )
            )


class SqlAlchemyArtifactRepositoryBase:
    """Shared append-only persistence behavior for concrete artifact repositories."""

    artifact_kind: ArtifactKind

    def __init__(self, session: Session) -> None:
        self._session = session
        self._index_repository = SqlAlchemyArtifactIndexRepository(session=session)

    def _create_record(
        self,
        artifact_id: str,
        body: BaseModel,
        readiness_state: str,
        version: int | None,
        upstream_artifact_refs: list[str] | None,
    ) -> int:
        next_version = self._next_version(artifact_id)
        if version is None:
            version = next_version
        elif version != next_version:
            raise ValueError(
                f"version {version} is invalid for artifact '{artifact_id}'; expected next version {next_version}"
            )

        existing_kind = self._get_artifact_kind(artifact_id)
        if existing_kind is not None and existing_kind != self.artifact_kind.value:
            raise ValueError(
                f"artifact '{artifact_id}' already exists as kind '{existing_kind}', not '{self.artifact_kind.value}'"
            )

        body_json = body.model_dump(mode="json")
        record = ArtifactRecord(
            artifact_id=artifact_id,
            artifact_kind=self.artifact_kind.value,
            version=version,
            readiness_state=readiness_state,
            body_json=body_json,
            upstream_artifact_refs=dedupe_strings(upstream_artifact_refs or []),
        )
        self._session.add(record)
        self._session.flush()
        self._index_repository.replace_trace_links(self.artifact_kind, artifact_id, version, body_json)
        self._session.commit()
        return version

    def _get_version(self, artifact_id: str, version: int, model_type: type[ArtifactModelT]) -> ArtifactModelT | None:
        record = self._session.get(ArtifactRecord, {"artifact_id": artifact_id, "version": version})
        if record is None or record.artifact_kind != self.artifact_kind.value:
            return None
        return model_type.model_validate(record.body_json)

    def _get_latest(self, artifact_id: str, model_type: type[ArtifactModelT]) -> ArtifactModelT | None:
        statement = (
            select(ArtifactRecord)
            .where(ArtifactRecord.artifact_id == artifact_id, ArtifactRecord.artifact_kind == self.artifact_kind.value)
            .order_by(ArtifactRecord.version.desc())
            .limit(1)
        )
        record = self._session.execute(statement).scalar_one_or_none()
        if record is None:
            return None
        return model_type.model_validate(record.body_json)

    def _next_version(self, artifact_id: str) -> int:
        statement = (
            select(ArtifactRecord.version)
            .where(ArtifactRecord.artifact_id == artifact_id, ArtifactRecord.artifact_kind == self.artifact_kind.value)
            .order_by(ArtifactRecord.version.desc())
            .limit(1)
        )
        latest_version = self._session.execute(statement).scalar_one_or_none()
        if latest_version is None:
            return 1
        return latest_version + 1

    def _get_artifact_kind(self, artifact_id: str) -> str | None:
        statement = select(ArtifactRecord.artifact_kind).where(ArtifactRecord.artifact_id == artifact_id).limit(1)
        return self._session.execute(statement).scalar_one_or_none()


class SqlAlchemyDiscoveryArtifactRepository(SqlAlchemyArtifactRepositoryBase):
    """SQLAlchemy-backed repository for discovery artifacts."""

    artifact_kind = ArtifactKind.DISCOVERY

    def create(
        self,
        artifact_id: str,
        artifact: DiscoveryArtifact,
        version: int | None = None,
        upstream_artifact_refs: list[str] | None = None,
    ) -> int:
        return self._create_record(
            artifact_id=artifact_id,
            body=artifact,
            readiness_state=artifact.completion_status.readiness_state.value,
            version=version,
            upstream_artifact_refs=upstream_artifact_refs,
        )

    def get_version(self, artifact_id: str, version: int) -> DiscoveryArtifact | None:
        return self._get_version(artifact_id, version, DiscoveryArtifact)

    def get_latest(self, artifact_id: str) -> DiscoveryArtifact | None:
        return self._get_latest(artifact_id, DiscoveryArtifact)


class SqlAlchemyDesignArtifactRepository(SqlAlchemyArtifactRepositoryBase):
    """SQLAlchemy-backed repository for design artifacts."""

    artifact_kind = ArtifactKind.DESIGN

    def create(
        self,
        artifact_id: str,
        artifact: DesignArtifact,
        version: int | None = None,
        upstream_artifact_refs: list[str] | None = None,
    ) -> int:
        return self._create_record(
            artifact_id=artifact_id,
            body=artifact,
            readiness_state=artifact.completion_status.readiness_state.value,
            version=version,
            upstream_artifact_refs=upstream_artifact_refs,
        )

    def get_version(self, artifact_id: str, version: int) -> DesignArtifact | None:
        return self._get_version(artifact_id, version, DesignArtifact)

    def get_latest(self, artifact_id: str) -> DesignArtifact | None:
        return self._get_latest(artifact_id, DesignArtifact)


class SqlAlchemyTaskArtifactRepository(SqlAlchemyArtifactRepositoryBase):
    """SQLAlchemy-backed repository for task artifacts."""

    artifact_kind = ArtifactKind.TASK

    def create(
        self,
        artifact_id: str,
        artifact: TaskArtifact,
        version: int | None = None,
        upstream_artifact_refs: list[str] | None = None,
    ) -> int:
        return self._create_record(
            artifact_id=artifact_id,
            body=artifact,
            readiness_state=artifact.completion_status.readiness_state.value,
            version=version,
            upstream_artifact_refs=upstream_artifact_refs,
        )

    def get_version(self, artifact_id: str, version: int) -> TaskArtifact | None:
        return self._get_version(artifact_id, version, TaskArtifact)

    def get_latest(self, artifact_id: str) -> TaskArtifact | None:
        return self._get_latest(artifact_id, TaskArtifact)


class SqlAlchemyContextPacketRepository(SqlAlchemyArtifactRepositoryBase):
    """SQLAlchemy-backed repository for context packets."""

    artifact_kind = ArtifactKind.CONTEXT_PACKET

    def create(
        self,
        artifact_id: str,
        packet: ContextPacket,
        version: int | None = None,
        upstream_artifact_refs: list[str] | None = None,
    ) -> int:
        return self._create_record(
            artifact_id=artifact_id,
            body=packet,
            readiness_state=packet.completion_status.readiness_state.value,
            version=version,
            upstream_artifact_refs=upstream_artifact_refs,
        )

    def get_version(self, artifact_id: str, version: int) -> ContextPacket | None:
        return self._get_version(artifact_id, version, ContextPacket)

    def get_latest(self, artifact_id: str) -> ContextPacket | None:
        return self._get_latest(artifact_id, ContextPacket)
