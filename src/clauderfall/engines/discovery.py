"""Discovery engine orchestration entry points."""

from __future__ import annotations

from clauderfall.artifacts.discovery import DiscoveryArtifact
from clauderfall.contracts.discovery_design import DiscoveryDesignGateResult, check_discovery_to_design_handoff
from clauderfall.validation.discovery import validate_discovery_artifact


class DiscoveryEngine:
    """Thin orchestration wrapper for the first vertical slice."""

    def validate(self, artifact: DiscoveryArtifact) -> list[str]:
        return validate_discovery_artifact(artifact)

    def check_handoff(self, artifact: DiscoveryArtifact) -> DiscoveryDesignGateResult:
        return check_discovery_to_design_handoff(artifact)

