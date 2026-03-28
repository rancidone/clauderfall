"""Semantic validation for Discovery Artifacts."""

from __future__ import annotations

from clauderfall_v1.artifacts.common import ConfidenceLevel, Grounding, ReadinessState, SourceClassification
from clauderfall_v1.artifacts.discovery import DiscoveryArtifact


def validate_discovery_artifact(artifact: DiscoveryArtifact) -> list[str]:
    """Return semantic validation issues for a Discovery Artifact."""

    issues: list[str] = []

    if not artifact.problem_definition:
        issues.append("problem_definition must not be empty")

    if not artifact.success_criteria:
        issues.append("success_criteria must not be empty")

    if not artifact.scope_boundaries.in_scope and not artifact.scope_boundaries.out_of_scope:
        issues.append("scope_boundaries must define in_scope or out_of_scope entries")

    if not artifact.source_register:
        issues.append("source_register must not be empty")

    if not artifact.provenance_records:
        issues.append("provenance_records must not be empty")

    traceable_targets = {record.target_ref for record in artifact.provenance_records}
    required_targets = {
        "problem_definition",
        "constraints",
        "success_criteria",
        "scope_boundaries",
        "risks",
        "unknowns",
        "open_questions",
    }
    missing_targets = sorted(target for target in required_targets if target not in traceable_targets)
    if missing_targets:
        issues.append(f"provenance_records missing required targets: {', '.join(missing_targets)}")

    for record in artifact.provenance_records:
        if not record.trace_links:
            issues.append(f"provenance record '{record.target_ref}' must contain trace_links")

        if record.source_classification is SourceClassification.ASSUMED and record.target_ref in {
            "problem_definition",
            "constraints",
            "success_criteria",
            "scope_boundaries",
        }:
            issues.append(f"assumed provenance is not allowed for {record.target_ref}")

        if record.grounding is Grounding.FLOATING and record.target_ref in {
            "problem_definition",
            "constraints",
            "success_criteria",
            "scope_boundaries",
        }:
            issues.append(f"floating grounding is not allowed for {record.target_ref}")

        if record.confidence is ConfidenceLevel.LOW and record.target_ref in {
            "problem_definition",
            "constraints",
            "success_criteria",
            "scope_boundaries",
        }:
            issues.append(f"low-confidence content is blocking for {record.target_ref}")

    if artifact.completion_status.readiness_state is ReadinessState.READY and artifact.completion_status.blocking_gaps:
        issues.append("ready artifacts must not contain blocking_gaps")

    if artifact.completion_status.readiness_state is ReadinessState.NOT_READY and not artifact.completion_status.blocking_gaps:
        issues.append("not_ready artifacts must contain at least one blocking gap")

    return issues

