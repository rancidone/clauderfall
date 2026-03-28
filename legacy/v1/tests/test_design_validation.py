from clauderfall_v1.artifacts.common import DesignElementClassification, ReadinessState
from clauderfall_v1.contracts.design_task import check_design_to_task_handoff
from clauderfall_v1.validation.design import validate_design_artifact


def test_valid_design_artifact_has_no_validation_issues(valid_design_artifact) -> None:
    assert validate_design_artifact(valid_design_artifact) == []


def test_design_handoff_accepts_ready_valid_design_artifact(valid_design_artifact) -> None:
    result = check_design_to_task_handoff(valid_design_artifact)

    assert result.accepted is True
    assert result.reasons == []


def test_design_handoff_rejects_missing_task_decomposition_signals(valid_design_artifact) -> None:
    artifact = valid_design_artifact
    artifact.task_decomposition_signals.natural_work_boundaries = []

    result = check_design_to_task_handoff(artifact)

    assert result.accepted is False
    assert "task_decomposition_signals.natural_work_boundaries must not be empty" in result.reasons


def test_design_validation_rejects_missing_traceability_targets(valid_design_artifact) -> None:
    artifact = valid_design_artifact
    artifact.traceability = artifact.traceability[:-1]

    issues = validate_design_artifact(artifact)

    assert "traceability missing required targets: task_decomposition_signals" in issues


def test_design_validation_rejects_unresolved_system_structure(valid_design_artifact) -> None:
    artifact = valid_design_artifact
    artifact.traceability[1].classification = DesignElementClassification.UNRESOLVED

    issues = validate_design_artifact(artifact)

    assert "unresolved classification is not allowed for system_structure" in issues


def test_design_validation_rejects_ready_artifact_with_blocking_gaps(valid_design_artifact) -> None:
    artifact = valid_design_artifact
    artifact.completion_status.blocking_gaps = ["Missing invariant"]

    issues = validate_design_artifact(artifact)

    assert "ready artifacts must not contain blocking_gaps" in issues


def test_design_validation_rejects_not_ready_without_blocking_gaps(valid_design_artifact) -> None:
    artifact = valid_design_artifact
    artifact.completion_status.readiness_state = ReadinessState.NOT_READY
    artifact.completion_status.blocking_gaps = []

    issues = validate_design_artifact(artifact)

    assert "not_ready artifacts must contain at least one blocking gap" in issues
