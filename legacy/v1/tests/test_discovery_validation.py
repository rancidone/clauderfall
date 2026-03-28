from clauderfall_v1.artifacts.common import ConfidenceLevel, Grounding, ReadinessState, SourceClassification
from clauderfall_v1.contracts.discovery_design import check_discovery_to_design_handoff
from clauderfall_v1.validation.discovery import validate_discovery_artifact


def test_valid_discovery_artifact_has_no_validation_issues(valid_discovery_artifact) -> None:
    assert validate_discovery_artifact(valid_discovery_artifact) == []


def test_handoff_accepts_ready_valid_discovery_artifact(valid_discovery_artifact) -> None:
    artifact = valid_discovery_artifact

    result = check_discovery_to_design_handoff(artifact)

    assert result.accepted is True
    assert result.reasons == []


def test_handoff_rejects_ready_artifact_with_semantic_issue(valid_discovery_artifact) -> None:
    artifact = valid_discovery_artifact
    artifact.success_criteria = []

    result = check_discovery_to_design_handoff(artifact)

    assert result.accepted is False
    assert "success_criteria must not be empty" in result.reasons


def test_validation_rejects_missing_provenance_targets(valid_discovery_artifact) -> None:
    artifact = valid_discovery_artifact
    artifact.provenance_records = artifact.provenance_records[:-1]

    issues = validate_discovery_artifact(artifact)

    assert "provenance_records missing required targets: open_questions" in issues


def test_validation_rejects_ready_artifact_with_blocking_gaps(valid_discovery_artifact) -> None:
    artifact = valid_discovery_artifact
    artifact.completion_status.blocking_gaps = ["Unresolved ambiguity"]

    issues = validate_discovery_artifact(artifact)

    assert "ready artifacts must not contain blocking_gaps" in issues


def test_validation_rejects_not_ready_artifact_without_blocking_gaps(valid_discovery_artifact) -> None:
    artifact = valid_discovery_artifact
    artifact.completion_status.readiness_state = ReadinessState.NOT_READY
    artifact.completion_status.blocking_gaps = []

    issues = validate_discovery_artifact(artifact)

    assert "not_ready artifacts must contain at least one blocking gap" in issues


def test_validation_rejects_assumed_problem_definition(valid_discovery_artifact) -> None:
    artifact = valid_discovery_artifact
    artifact.provenance_records[0].source_classification = SourceClassification.ASSUMED

    issues = validate_discovery_artifact(artifact)

    assert "assumed provenance is not allowed for problem_definition" in issues


def test_validation_rejects_floating_scope_boundaries(valid_discovery_artifact) -> None:
    artifact = valid_discovery_artifact

    for record in artifact.provenance_records:
        if record.target_ref == "scope_boundaries":
            record.grounding = Grounding.FLOATING

    issues = validate_discovery_artifact(artifact)

    assert "floating grounding is not allowed for scope_boundaries" in issues


def test_validation_rejects_low_confidence_success_criteria(valid_discovery_artifact) -> None:
    artifact = valid_discovery_artifact

    for record in artifact.provenance_records:
        if record.target_ref == "success_criteria":
            record.confidence = ConfidenceLevel.LOW

    issues = validate_discovery_artifact(artifact)

    assert "low-confidence content is blocking for success_criteria" in issues
