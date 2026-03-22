from clauderfall.artifacts.common import ReadinessState, TaskElementClassification
from clauderfall.contracts.task_context import check_task_to_context_handoff
from clauderfall.validation.task import validate_task_artifact


def test_valid_task_artifact_has_no_validation_issues(valid_task_artifact) -> None:
    assert validate_task_artifact(valid_task_artifact) == []


def test_task_handoff_accepts_ready_valid_task_artifact(valid_task_artifact) -> None:
    result = check_task_to_context_handoff(valid_task_artifact)

    assert result.accepted is True
    assert result.reasons == []


def test_task_handoff_rejects_missing_acceptance_criteria(valid_task_artifact) -> None:
    artifact = valid_task_artifact
    artifact.acceptance_criteria = []

    result = check_task_to_context_handoff(artifact)

    assert result.accepted is False
    assert "acceptance_criteria must not be empty" in result.reasons


def test_task_validation_rejects_missing_traceability_targets(valid_task_artifact) -> None:
    artifact = valid_task_artifact
    artifact.traceability = artifact.traceability[:-1]

    issues = validate_task_artifact(artifact)

    assert "traceability missing required targets: acceptance_criteria" in issues


def test_task_validation_rejects_unresolved_inputs(valid_task_artifact) -> None:
    artifact = valid_task_artifact
    artifact.traceability[1].classification = TaskElementClassification.UNRESOLVED

    issues = validate_task_artifact(artifact)

    assert "unresolved classification is not allowed for inputs" in issues


def test_task_validation_rejects_ready_artifact_with_blocking_gaps(valid_task_artifact) -> None:
    artifact = valid_task_artifact
    artifact.completion_status.blocking_gaps = ["Missing dependency clarity"]

    issues = validate_task_artifact(artifact)

    assert "ready artifacts must not contain blocking_gaps" in issues


def test_task_validation_rejects_not_ready_without_blocking_gaps(valid_task_artifact) -> None:
    artifact = valid_task_artifact
    artifact.completion_status.readiness_state = ReadinessState.NOT_READY
    artifact.completion_status.blocking_gaps = []

    issues = validate_task_artifact(artifact)

    assert "not_ready artifacts must contain at least one blocking gap" in issues
