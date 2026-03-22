"""Semantic validation for Design Artifacts."""

from __future__ import annotations

from clauderfall.artifacts.common import DesignElementClassification, ReadinessState
from clauderfall.artifacts.design import DesignArtifact


def validate_design_artifact(artifact: DesignArtifact) -> list[str]:
    """Return semantic validation issues for a Design Artifact."""

    issues: list[str] = []

    if not artifact.objective:
        issues.append("objective must not be empty")

    if not artifact.scope.in_scope and not artifact.scope.out_of_scope:
        issues.append("scope must define in_scope or out_of_scope entries")

    if not artifact.system_structure:
        issues.append("system_structure must not be empty")

    if not artifact.constraints_encoding:
        issues.append("constraints_encoding must not be empty")

    if not artifact.invariants:
        issues.append("invariants must not be empty")

    if not artifact.decisions:
        issues.append("decisions must not be empty")

    if not artifact.task_decomposition_signals.natural_work_boundaries:
        issues.append("task_decomposition_signals.natural_work_boundaries must not be empty")

    if not artifact.task_decomposition_signals.dependency_relationships:
        issues.append("task_decomposition_signals.dependency_relationships must not be empty")

    if not artifact.task_decomposition_signals.acceptance_expectations_to_preserve:
        issues.append("task_decomposition_signals.acceptance_expectations_to_preserve must not be empty")

    if not artifact.traceability:
        issues.append("traceability must not be empty")

    traceable_targets = {record.target_ref for record in artifact.traceability}
    required_targets = {
        "objective",
        "system_structure",
        "constraints_encoding",
        "invariants",
        "decisions",
        "task_decomposition_signals",
    }
    missing_targets = sorted(target for target in required_targets if target not in traceable_targets)
    if missing_targets:
        issues.append(f"traceability missing required targets: {', '.join(missing_targets)}")

    for decision in artifact.decisions:
        if not decision.alternatives_considered:
            issues.append(f"decision '{decision.affected_design_area}' must list alternatives_considered")
        if not decision.consequences:
            issues.append(f"decision '{decision.affected_design_area}' must list consequences")
        if not decision.trace_links:
            issues.append(f"decision '{decision.affected_design_area}' must contain trace_links")

    for record in artifact.traceability:
        if not record.trace_links:
            issues.append(f"traceability record '{record.target_ref}' must contain trace_links")
        if not record.supports:
            issues.append(f"traceability record '{record.target_ref}' must contain supports")
        if record.classification is DesignElementClassification.UNRESOLVED and record.target_ref in {
            "system_structure",
            "invariants",
            "task_decomposition_signals",
        }:
            issues.append(f"unresolved classification is not allowed for {record.target_ref}")

    if artifact.completion_status.readiness_state is ReadinessState.READY and artifact.completion_status.blocking_gaps:
        issues.append("ready artifacts must not contain blocking_gaps")

    if artifact.completion_status.readiness_state is ReadinessState.NOT_READY and not artifact.completion_status.blocking_gaps:
        issues.append("not_ready artifacts must contain at least one blocking gap")

    return issues
