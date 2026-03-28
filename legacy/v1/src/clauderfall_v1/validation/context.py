"""Semantic validation for Context Packets."""

from __future__ import annotations

from clauderfall_v1.artifacts.common import ConflictSeverity, ReadinessState
from clauderfall_v1.artifacts.context import ContextPacket
from clauderfall_v1.validation.task import validate_task_artifact


def validate_context_packet(packet: ContextPacket) -> list[str]:
    """Return semantic validation issues for a Context Packet."""

    issues: list[str] = []

    task_issues = validate_task_artifact(packet.task_contract)
    if task_issues:
        issues.extend([f"task_contract invalid: {issue}" for issue in task_issues])

    if not packet.included_context:
        issues.append("included_context must not be empty")

    if not packet.inclusion_justification:
        issues.append("inclusion_justification must not be empty")

    if not packet.exclusions:
        issues.append("exclusions must not be empty")

    if not packet.budget_summary.shaping_decisions:
        issues.append("budget_summary.shaping_decisions must not be empty")

    if not packet.traceability:
        issues.append("traceability must not be empty")

    included_item_ids = {item.item_id for item in packet.included_context}
    if len(included_item_ids) != len(packet.included_context):
        issues.append("included_context.item_id values must be unique")

    justification_item_ids = {entry.item_id for entry in packet.inclusion_justification}
    missing_justifications = sorted(included_item_ids - justification_item_ids)
    if missing_justifications:
        issues.append(
            f"inclusion_justification missing required entries for item_ids: {', '.join(missing_justifications)}"
        )

    extra_justifications = sorted(justification_item_ids - included_item_ids)
    if extra_justifications:
        issues.append(
            f"inclusion_justification references unknown item_ids: {', '.join(extra_justifications)}"
        )

    for entry in packet.inclusion_justification:
        if not entry.supports:
            issues.append(f"inclusion_justification for '{entry.item_id}' must contain supports")

    for signal in packet.conflict_signals:
        if not signal.conflicting_elements:
            issues.append("conflict_signals entries must contain conflicting_elements")
        if signal.severity is ConflictSeverity.HIGH and packet.completion_status.readiness_state is ReadinessState.READY:
            issues.append("ready packets must not contain unresolved high-severity conflict_signals")

    traceable_targets = {record.target_ref for record in packet.traceability}
    required_targets = {"task_contract", "included_context", "inclusion_justification"}
    missing_targets = sorted(target for target in required_targets if target not in traceable_targets)
    if missing_targets:
        issues.append(f"traceability missing required targets: {', '.join(missing_targets)}")

    for record in packet.traceability:
        if not record.supports:
            issues.append(f"traceability record '{record.target_ref}' must contain supports")
        if not record.trace_links:
            issues.append(f"traceability record '{record.target_ref}' must contain trace_links")

    if packet.completion_status.readiness_state is ReadinessState.READY and packet.completion_status.blocking_gaps:
        issues.append("ready packets must not contain blocking_gaps")

    if packet.completion_status.readiness_state is ReadinessState.NOT_READY and not packet.completion_status.blocking_gaps:
        issues.append("not_ready packets must contain at least one blocking gap")

    return issues
