"""Artifact application services."""

from __future__ import annotations

from clauderfall_v1.artifacts.common import ArtifactKind, ArtifactVersionRef, TraceLinkMatch
from clauderfall_v1.artifacts.context import ContextPacket
from clauderfall_v1.artifacts.design import DesignArtifact
from clauderfall_v1.artifacts.discovery import DiscoveryArtifact
from clauderfall_v1.artifacts.task import TaskArtifact
from clauderfall_v1.contracts.design_task import DesignTaskGateResult, check_design_to_task_handoff
from clauderfall_v1.contracts.discovery_design import DiscoveryDesignGateResult, check_discovery_to_design_handoff
from clauderfall_v1.contracts.task_context import TaskContextGateResult, check_task_to_context_handoff
from clauderfall_v1.persistence.repositories import (
    ArtifactIndexRepository,
    ContextPacketRepository,
    DesignArtifactRepository,
    DiscoveryArtifactRepository,
    TaskArtifactRepository,
)
from clauderfall_v1.validation.context import validate_context_packet
from clauderfall_v1.validation.design import validate_design_artifact
from clauderfall_v1.validation.discovery import validate_discovery_artifact
from clauderfall_v1.validation.task import validate_task_artifact
from clauderfall_v1.services.context_service import ContextService
class ArtifactService:
    """High-level operations over artifacts for CLI workflows."""

    def __init__(
        self,
        discovery_repository: DiscoveryArtifactRepository,
        design_repository: DesignArtifactRepository,
        task_repository: TaskArtifactRepository,
        context_repository: ContextPacketRepository,
        artifact_index_repository: ArtifactIndexRepository,
    ) -> None:
        self._discovery_repository = discovery_repository
        self._design_repository = design_repository
        self._task_repository = task_repository
        self._context_repository = context_repository
        self._artifact_index_repository = artifact_index_repository
        self._context_service = ContextService()

    def validate_discovery(self, artifact: DiscoveryArtifact) -> list[str]:
        return validate_discovery_artifact(artifact)

    def validate_design(self, artifact: DesignArtifact) -> list[str]:
        return validate_design_artifact(artifact)

    def validate_task(self, artifact: TaskArtifact) -> list[str]:
        return validate_task_artifact(artifact)

    def validate_context(self, packet: ContextPacket) -> list[str]:
        return validate_context_packet(packet)

    def save_discovery(
        self,
        artifact_id: str,
        artifact: DiscoveryArtifact,
        version: int | None = None,
        upstream_artifact_refs: list[str] | None = None,
    ) -> int:
        return self._discovery_repository.create(
            artifact_id=artifact_id,
            artifact=artifact,
            version=version,
            upstream_artifact_refs=upstream_artifact_refs,
        )

    def load_discovery(self, artifact_id: str, version: int | None = None) -> DiscoveryArtifact | None:
        if version is None:
            return self._discovery_repository.get_latest(artifact_id)
        return self._discovery_repository.get_version(artifact_id, version)

    def save_design(
        self,
        artifact_id: str,
        artifact: DesignArtifact,
        version: int | None = None,
        upstream_artifact_refs: list[str] | None = None,
    ) -> int:
        return self._design_repository.create(
            artifact_id=artifact_id,
            artifact=artifact,
            version=version,
            upstream_artifact_refs=upstream_artifact_refs,
        )

    def load_design(self, artifact_id: str, version: int | None = None) -> DesignArtifact | None:
        if version is None:
            return self._design_repository.get_latest(artifact_id)
        return self._design_repository.get_version(artifact_id, version)

    def save_task(
        self,
        artifact_id: str,
        artifact: TaskArtifact,
        version: int | None = None,
        upstream_artifact_refs: list[str] | None = None,
    ) -> int:
        return self._task_repository.create(
            artifact_id=artifact_id,
            artifact=artifact,
            version=version,
            upstream_artifact_refs=upstream_artifact_refs,
        )

    def load_task(self, artifact_id: str, version: int | None = None) -> TaskArtifact | None:
        if version is None:
            return self._task_repository.get_latest(artifact_id)
        return self._task_repository.get_version(artifact_id, version)

    def save_context(
        self,
        artifact_id: str,
        packet: ContextPacket,
        version: int | None = None,
        upstream_artifact_refs: list[str] | None = None,
    ) -> int:
        return self._context_repository.create(
            artifact_id=artifact_id,
            packet=packet,
            version=version,
            upstream_artifact_refs=upstream_artifact_refs,
        )

    def load_context(self, artifact_id: str, version: int | None = None) -> ContextPacket | None:
        if version is None:
            return self._context_repository.get_latest(artifact_id)
        return self._context_repository.get_version(artifact_id, version)

    def assemble_context(
        self,
        task_artifact: TaskArtifact,
        supporting_items,
        exclusions=None,
    ) -> ContextPacket:
        return self._context_service.assemble_packet(
            task_artifact=task_artifact,
            supporting_items=supporting_items,
            exclusions=exclusions,
        )

    def assemble_context_from_refs(
        self,
        task_ref: ArtifactVersionRef,
        supporting_refs: list[ArtifactVersionRef],
        exclusions=None,
    ) -> tuple[ContextPacket, list[str]]:
        if task_ref.artifact_kind is not ArtifactKind.TASK:
            raise ValueError("task_ref must reference a task artifact version")
        if not supporting_refs:
            raise ValueError("supporting_refs must not be empty")

        task_record = self._artifact_index_repository.get_record(task_ref)
        if task_record is None:
            raise ValueError(f"task artifact ref not found: {task_ref.to_ref_string()}")

        supporting_records = []
        for supporting_ref in supporting_refs:
            record = self._artifact_index_repository.get_record(supporting_ref)
            if record is None:
                raise ValueError(f"supporting artifact ref not found: {supporting_ref.to_ref_string()}")
            supporting_records.append(record)

        task_artifact = TaskArtifact.model_validate(task_record.body_json)
        supporting_items = self._context_service.build_supporting_items_from_artifact_refs(
            artifact_refs=supporting_refs,
            artifact_payloads=[record.body_json for record in supporting_records],
        )
        packet = self._context_service.assemble_packet(
            task_artifact=task_artifact,
            supporting_items=supporting_items,
            exclusions=exclusions,
        )
        upstream_artifact_refs = [task_ref.to_ref_string(), *[ref.to_ref_string() for ref in supporting_refs]]
        return packet, upstream_artifact_refs

    def query_trace_link(self, trace_link: str) -> list[TraceLinkMatch]:
        return self._artifact_index_repository.find_by_trace_link(trace_link)

    def check_discovery_handoff(self, artifact: DiscoveryArtifact) -> DiscoveryDesignGateResult:
        return check_discovery_to_design_handoff(artifact)

    def _load_latest_discovery_version(self, artifact_id: str) -> int | None:
        record = self._artifact_index_repository.get_latest_record(ArtifactKind.DISCOVERY, artifact_id)
        if record is None:
            return None
        return record.version

    def check_design_handoff(self, artifact: DesignArtifact) -> DesignTaskGateResult:
        return check_design_to_task_handoff(artifact)

    def check_task_handoff(self, artifact: TaskArtifact) -> TaskContextGateResult:
        return check_task_to_context_handoff(artifact)
