"""Semantic validation for Task Artifacts."""

from __future__ import annotations

from clauderfall.artifacts.common import ReadinessState, TaskElementClassification
from clauderfall.artifacts.task import TaskArtifact


def validate_task_artifact(artifact: TaskArtifact) -> list[str]:
    """Return semantic validation issues for a Task Artifact."""

    issues: list[str] = []

    if not artifact.objective:
        issues.append("objective must not be empty")

    if not artifact.scope.in_scope and not artifact.scope.out_of_scope:
        issues.append("scope must define in_scope or out_of_scope entries")

    if not artifact.inputs:
        issues.append("inputs must not be empty")

    if not artifact.outputs:
        issues.append("outputs must not be empty")

    if not artifact.constraints:
        issues.append("constraints must not be empty")

    if not artifact.invariants:
        issues.append("invariants must not be empty")

    if not artifact.acceptance_criteria:
        issues.append("acceptance_criteria must not be empty")

    if not artifact.dependencies:
        issues.append("dependencies must not be empty")

    if not artifact.traceability:
        issues.append("traceability must not be empty")

    traceable_targets = {record.target_ref for record in artifact.traceability}
    required_targets = {
        "objective",
        "inputs",
        "constraints",
        "invariants",
        "acceptance_criteria",
    }
    missing_targets = sorted(target for target in required_targets if target not in traceable_targets)
    if missing_targets:
        issues.append(f"traceability missing required targets: {', '.join(missing_targets)}")

    for record in artifact.traceability:
        if not record.trace_links:
            issues.append(f"traceability record '{record.target_ref}' must contain trace_links")
        if not record.supports:
            issues.append(f"traceability record '{record.target_ref}' must contain supports")
        if record.classification is TaskElementClassification.UNRESOLVED and record.target_ref in {
            "scope",
            "inputs",
            "outputs",
            "constraints",
            "invariants",
            "acceptance_criteria",
        }:
            issues.append(f"unresolved classification is not allowed for {record.target_ref}")

    if artifact.completion_status.readiness_state is ReadinessState.READY and artifact.completion_status.blocking_gaps:
        issues.append("ready artifacts must not contain blocking_gaps")

    if artifact.completion_status.readiness_state is ReadinessState.NOT_READY and not artifact.completion_status.blocking_gaps:
        issues.append("not_ready artifacts must contain at least one blocking gap")

    return issues
