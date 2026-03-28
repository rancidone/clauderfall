"""Task-to-Context handoff gate."""

from __future__ import annotations

from pydantic import Field

from clauderfall_v1.artifacts.common import ArtifactBase, ReadinessState
from clauderfall_v1.artifacts.task import TaskArtifact
from clauderfall_v1.validation.task import validate_task_artifact


class TaskContextGateResult(ArtifactBase):
    """Result of evaluating the Task-to-Context handoff preconditions."""

    accepted: bool
    reasons: list[str] = Field(default_factory=list)


def check_task_to_context_handoff(artifact: TaskArtifact) -> TaskContextGateResult:
    """Apply the contract preconditions defined in task_context_contract.md."""

    issues = validate_task_artifact(artifact)

    if artifact.completion_status.readiness_state is not ReadinessState.READY:
        issues.append("completion_status.readiness_state must be 'ready' before Context can begin")

    return TaskContextGateResult(accepted=not issues, reasons=issues)
