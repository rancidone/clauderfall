from clauderfall.artifacts.context import ExclusionRecord
from clauderfall.artifacts.common import ReadinessState
from clauderfall.services.context_service import ContextService


def test_context_service_assembles_valid_packet(valid_task_artifact, context_assembly_items) -> None:
    service = ContextService()

    packet = service.assemble_packet(
        task_artifact=valid_task_artifact,
        supporting_items=context_assembly_items,
    )

    assert packet.task_contract == valid_task_artifact
    assert len(packet.included_context) == 2
    assert len(packet.inclusion_justification) == 2
    assert packet.completion_status.readiness_state is ReadinessState.READY


def test_context_service_uses_explicit_exclusions(valid_task_artifact, context_assembly_items) -> None:
    service = ContextService()
    exclusions = [
        ExclusionRecord(
            excluded_material="Large unrelated design history",
            reason="Not required for safe execution of this task.",
        )
    ]

    packet = service.assemble_packet(
        task_artifact=valid_task_artifact,
        supporting_items=context_assembly_items,
        exclusions=exclusions,
    )

    assert packet.exclusions == exclusions


def test_context_service_rejects_not_ready_task(valid_task_artifact, context_assembly_items) -> None:
    service = ContextService()
    valid_task_artifact.completion_status.readiness_state = ReadinessState.NOT_READY
    valid_task_artifact.completion_status.blocking_gaps = ["Need a stable output definition."]

    try:
        service.assemble_packet(
            task_artifact=valid_task_artifact,
            supporting_items=context_assembly_items,
        )
    except ValueError as exc:
        assert "task artifact failed handoff preconditions" in str(exc)
    else:
        raise AssertionError("expected ValueError for not_ready task artifact")
