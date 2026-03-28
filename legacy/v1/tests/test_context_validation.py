from clauderfall_v1.artifacts.common import ConflictSeverity, ReadinessState
from clauderfall_v1.validation.context import validate_context_packet


def test_valid_context_packet_has_no_validation_issues(valid_context_packet) -> None:
    assert validate_context_packet(valid_context_packet) == []


def test_context_validation_rejects_missing_justification_for_included_item(valid_context_packet) -> None:
    packet = valid_context_packet
    packet.inclusion_justification = packet.inclusion_justification[:-1]

    issues = validate_context_packet(packet)

    assert "inclusion_justification missing required entries for item_ids: ctx-2" in issues


def test_context_validation_rejects_unknown_justification_item_id(valid_context_packet) -> None:
    packet = valid_context_packet
    packet.inclusion_justification[0].item_id = "unknown"

    issues = validate_context_packet(packet)

    assert "inclusion_justification references unknown item_ids: unknown" in issues


def test_context_validation_rejects_ready_packet_with_high_conflict(valid_context_packet) -> None:
    packet = valid_context_packet
    packet.conflict_signals[0].severity = ConflictSeverity.HIGH

    issues = validate_context_packet(packet)

    assert "ready packets must not contain unresolved high-severity conflict_signals" in issues


def test_context_validation_rejects_missing_traceability_targets(valid_context_packet) -> None:
    packet = valid_context_packet
    packet.traceability = packet.traceability[:-1]

    issues = validate_context_packet(packet)

    assert "traceability missing required targets: inclusion_justification" in issues


def test_context_validation_rejects_ready_packet_with_blocking_gaps(valid_context_packet) -> None:
    packet = valid_context_packet
    packet.completion_status.blocking_gaps = ["Need an interface definition excerpt."]

    issues = validate_context_packet(packet)

    assert "ready packets must not contain blocking_gaps" in issues


def test_context_validation_rejects_not_ready_packet_without_blocking_gaps(valid_context_packet) -> None:
    packet = valid_context_packet
    packet.completion_status.readiness_state = ReadinessState.NOT_READY
    packet.completion_status.blocking_gaps = []

    issues = validate_context_packet(packet)

    assert "not_ready packets must contain at least one blocking gap" in issues
