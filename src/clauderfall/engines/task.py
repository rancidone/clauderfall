"""Task engine orchestration entry points."""

from __future__ import annotations

from clauderfall.artifacts.task import TaskArtifact
from clauderfall.contracts.task_context import TaskContextGateResult, check_task_to_context_handoff
from clauderfall.validation.task import validate_task_artifact


class TaskEngine:
    """Thin orchestration wrapper for the Task vertical slice."""

    def validate(self, artifact: TaskArtifact) -> list[str]:
        return validate_task_artifact(artifact)

    def check_handoff(self, artifact: TaskArtifact) -> TaskContextGateResult:
        return check_task_to_context_handoff(artifact)
