"""Contract-focused application services."""

from __future__ import annotations

from clauderfall.artifacts.discovery import DiscoveryArtifact
from clauderfall.contracts.discovery_design import DiscoveryDesignGateResult, check_discovery_to_design_handoff


class ContractService:
    """Deterministic contract checks exposed to operator surfaces."""

    def check_discovery_to_design(self, artifact: DiscoveryArtifact) -> DiscoveryDesignGateResult:
        return check_discovery_to_design_handoff(artifact)

