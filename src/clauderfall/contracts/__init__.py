"""Contract gate helpers."""

from clauderfall.contracts.task_context import TaskContextGateResult, check_task_to_context_handoff
from clauderfall.contracts.design_task import DesignTaskGateResult, check_design_to_task_handoff
from clauderfall.contracts.discovery_design import DiscoveryDesignGateResult, check_discovery_to_design_handoff

__all__ = [
    "DiscoveryDesignGateResult",
    "DesignTaskGateResult",
    "TaskContextGateResult",
    "check_discovery_to_design_handoff",
    "check_design_to_task_handoff",
    "check_task_to_context_handoff",
]
