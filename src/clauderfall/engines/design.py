"""Design engine orchestration entry points."""

from __future__ import annotations

from clauderfall.artifacts.design import DesignArtifact
from clauderfall.contracts.design_task import DesignTaskGateResult, check_design_to_task_handoff
from clauderfall.validation.design import validate_design_artifact


class DesignEngine:
    """Thin orchestration wrapper for the Design vertical slice."""

    def validate(self, artifact: DesignArtifact) -> list[str]:
        return validate_design_artifact(artifact)

    def check_handoff(self, artifact: DesignArtifact) -> DesignTaskGateResult:
        return check_design_to_task_handoff(artifact)
