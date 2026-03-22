"""Discovery-to-Design handoff gate."""

from __future__ import annotations

from pydantic import Field

from clauderfall.artifacts.discovery import DiscoveryArtifact
from clauderfall.artifacts.common import ArtifactBase, ReadinessState
from clauderfall.validation.discovery import validate_discovery_artifact


class DiscoveryDesignGateResult(ArtifactBase):
    """Result of evaluating the Discovery-to-Design handoff preconditions."""

    accepted: bool
    reasons: list[str] = Field(default_factory=list)


def check_discovery_to_design_handoff(artifact: DiscoveryArtifact) -> DiscoveryDesignGateResult:
    """Apply the contract preconditions defined in discovery_design_contract.md."""

    issues = validate_discovery_artifact(artifact)

    if artifact.completion_status.readiness_state is not ReadinessState.READY:
        issues.append("completion_status.readiness_state must be 'ready' before Design can begin")

    return DiscoveryDesignGateResult(accepted=not issues, reasons=issues)

