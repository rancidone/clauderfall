"""Artifact application services."""

from __future__ import annotations

from clauderfall.artifacts.discovery import DiscoveryArtifact
from clauderfall.contracts.discovery_design import DiscoveryDesignGateResult, check_discovery_to_design_handoff
from clauderfall.persistence.repositories import DiscoveryArtifactRepository
from clauderfall.validation.discovery import validate_discovery_artifact


class ArtifactService:
    """High-level operations over artifacts for CLI and MCP adapters."""

    def __init__(self, discovery_repository: DiscoveryArtifactRepository) -> None:
        self._discovery_repository = discovery_repository

    def validate_discovery(self, artifact: DiscoveryArtifact) -> list[str]:
        return validate_discovery_artifact(artifact)

    def save_discovery(self, artifact_id: str, artifact: DiscoveryArtifact, version: int | None = None) -> int:
        return self._discovery_repository.create(artifact_id=artifact_id, artifact=artifact, version=version)

    def load_discovery(self, artifact_id: str, version: int | None = None) -> DiscoveryArtifact | None:
        if version is None:
            return self._discovery_repository.get_latest(artifact_id)
        return self._discovery_repository.get_version(artifact_id, version)

    def check_discovery_handoff(self, artifact: DiscoveryArtifact) -> DiscoveryDesignGateResult:
        return check_discovery_to_design_handoff(artifact)
