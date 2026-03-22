"""Contract gate helpers."""

from clauderfall.contracts.design_task import DesignTaskGateResult, check_design_to_task_handoff
from clauderfall.contracts.discovery_design import DiscoveryDesignGateResult, check_discovery_to_design_handoff

__all__ = [
    "DiscoveryDesignGateResult",
    "DesignTaskGateResult",
    "check_discovery_to_design_handoff",
    "check_design_to_task_handoff",
]
