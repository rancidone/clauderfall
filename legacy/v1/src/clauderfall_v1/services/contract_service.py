"""Contract-focused application services."""

from __future__ import annotations

from clauderfall_v1.artifacts.design import DesignArtifact
from clauderfall_v1.artifacts.discovery import DiscoveryArtifact
from clauderfall_v1.artifacts.task import TaskArtifact
from clauderfall_v1.contracts.design_task import DesignTaskGateResult, check_design_to_task_handoff
from clauderfall_v1.contracts.discovery_design import DiscoveryDesignGateResult, check_discovery_to_design_handoff
from clauderfall_v1.contracts.task_context import TaskContextGateResult, check_task_to_context_handoff


class ContractService:
    """Deterministic contract checks exposed to operator surfaces."""

    def check_discovery_to_design(self, artifact: DiscoveryArtifact) -> DiscoveryDesignGateResult:
        return check_discovery_to_design_handoff(artifact)

    def check_design_to_task(self, artifact: DesignArtifact) -> DesignTaskGateResult:
        return check_design_to_task_handoff(artifact)

    def check_task_to_context(self, artifact: TaskArtifact) -> TaskContextGateResult:
        return check_task_to_context_handoff(artifact)
