"""Contract-focused application services."""

from __future__ import annotations

from clauderfall.artifacts.design import DesignArtifact
from clauderfall.artifacts.discovery import DiscoveryArtifact
from clauderfall.contracts.design_task import DesignTaskGateResult, check_design_to_task_handoff
from clauderfall.contracts.discovery_design import DiscoveryDesignGateResult, check_discovery_to_design_handoff


class ContractService:
    """Deterministic contract checks exposed to operator surfaces."""

    def check_discovery_to_design(self, artifact: DiscoveryArtifact) -> DiscoveryDesignGateResult:
        return check_discovery_to_design_handoff(artifact)

    def check_design_to_task(self, artifact: DesignArtifact) -> DesignTaskGateResult:
        return check_design_to_task_handoff(artifact)
