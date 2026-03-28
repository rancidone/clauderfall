"""Design-to-Task handoff gate."""

from __future__ import annotations

from pydantic import Field

from clauderfall_v1.artifacts.common import ArtifactBase, ReadinessState
from clauderfall_v1.artifacts.design import DesignArtifact
from clauderfall_v1.validation.design import validate_design_artifact


class DesignTaskGateResult(ArtifactBase):
    """Result of evaluating the Design-to-Task handoff preconditions."""

    accepted: bool
    reasons: list[str] = Field(default_factory=list)


def check_design_to_task_handoff(artifact: DesignArtifact) -> DesignTaskGateResult:
    """Apply the contract preconditions defined in design_task_contract.md."""

    issues = validate_design_artifact(artifact)

    if artifact.completion_status.readiness_state is not ReadinessState.READY:
        issues.append("completion_status.readiness_state must be 'ready' before Task can begin")

    return DesignTaskGateResult(accepted=not issues, reasons=issues)
