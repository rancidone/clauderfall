"""Design engine orchestration entry points."""

from __future__ import annotations

from clauderfall_v1.artifacts.design import DesignArtifact
from clauderfall_v1.contracts.design_task import DesignTaskGateResult, check_design_to_task_handoff
from clauderfall_v1.validation.design import validate_design_artifact


class DesignEngine:
    """Thin orchestration wrapper for the Design vertical slice."""

    def validate(self, artifact: DesignArtifact) -> list[str]:
        return validate_design_artifact(artifact)

    def check_handoff(self, artifact: DesignArtifact) -> DesignTaskGateResult:
        return check_design_to_task_handoff(artifact)
