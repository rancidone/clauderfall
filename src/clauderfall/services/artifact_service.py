"""Artifact application services."""

from __future__ import annotations

from clauderfall.artifacts.context import ContextPacket
from clauderfall.artifacts.design import DesignArtifact
from clauderfall.artifacts.discovery import DiscoveryArtifact
from clauderfall.artifacts.task import TaskArtifact
from clauderfall.contracts.design_task import DesignTaskGateResult, check_design_to_task_handoff
from clauderfall.contracts.discovery_design import DiscoveryDesignGateResult, check_discovery_to_design_handoff
from clauderfall.contracts.task_context import TaskContextGateResult, check_task_to_context_handoff
from clauderfall.persistence.repositories import (
    ContextPacketRepository,
    DesignArtifactRepository,
    DiscoveryArtifactRepository,
    TaskArtifactRepository,
)
from clauderfall.validation.context import validate_context_packet
from clauderfall.validation.design import validate_design_artifact
from clauderfall.validation.discovery import validate_discovery_artifact
from clauderfall.validation.task import validate_task_artifact
from clauderfall.services.context_service import ContextService


class ArtifactService:
    """High-level operations over artifacts for CLI and MCP adapters."""

    def __init__(
        self,
        discovery_repository: DiscoveryArtifactRepository,
        design_repository: DesignArtifactRepository,
        task_repository: TaskArtifactRepository,
        context_repository: ContextPacketRepository,
    ) -> None:
        self._discovery_repository = discovery_repository
        self._design_repository = design_repository
        self._task_repository = task_repository
        self._context_repository = context_repository
        self._context_service = ContextService()

    def validate_discovery(self, artifact: DiscoveryArtifact) -> list[str]:
        return validate_discovery_artifact(artifact)

    def validate_design(self, artifact: DesignArtifact) -> list[str]:
        return validate_design_artifact(artifact)

    def validate_task(self, artifact: TaskArtifact) -> list[str]:
        return validate_task_artifact(artifact)

    def validate_context(self, packet: ContextPacket) -> list[str]:
        return validate_context_packet(packet)

    def save_discovery(self, artifact_id: str, artifact: DiscoveryArtifact, version: int | None = None) -> int:
        return self._discovery_repository.create(artifact_id=artifact_id, artifact=artifact, version=version)

    def load_discovery(self, artifact_id: str, version: int | None = None) -> DiscoveryArtifact | None:
        if version is None:
            return self._discovery_repository.get_latest(artifact_id)
        return self._discovery_repository.get_version(artifact_id, version)

    def save_design(self, artifact_id: str, artifact: DesignArtifact, version: int | None = None) -> int:
        return self._design_repository.create(artifact_id=artifact_id, artifact=artifact, version=version)

    def load_design(self, artifact_id: str, version: int | None = None) -> DesignArtifact | None:
        if version is None:
            return self._design_repository.get_latest(artifact_id)
        return self._design_repository.get_version(artifact_id, version)

    def save_task(self, artifact_id: str, artifact: TaskArtifact, version: int | None = None) -> int:
        return self._task_repository.create(artifact_id=artifact_id, artifact=artifact, version=version)

    def load_task(self, artifact_id: str, version: int | None = None) -> TaskArtifact | None:
        if version is None:
            return self._task_repository.get_latest(artifact_id)
        return self._task_repository.get_version(artifact_id, version)

    def save_context(self, artifact_id: str, packet: ContextPacket, version: int | None = None) -> int:
        return self._context_repository.create(artifact_id=artifact_id, packet=packet, version=version)

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

    def check_discovery_handoff(self, artifact: DiscoveryArtifact) -> DiscoveryDesignGateResult:
        return check_discovery_to_design_handoff(artifact)

    def check_design_handoff(self, artifact: DesignArtifact) -> DesignTaskGateResult:
        return check_design_to_task_handoff(artifact)

    def check_task_handoff(self, artifact: TaskArtifact) -> TaskContextGateResult:
        return check_task_to_context_handoff(artifact)
