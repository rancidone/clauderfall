"""Context packet assembly service."""

from __future__ import annotations

from clauderfall.artifacts.common import ReadinessState
from clauderfall.artifacts.context import (
    BudgetSummary,
    ContextAssemblyItem,
    ContextPacket,
    ContextTraceabilityRecord,
    ExclusionRecord,
    IncludedContextItem,
    InclusionJustification,
)
from clauderfall.artifacts.task import TaskArtifact
from clauderfall.contracts.task_context import check_task_to_context_handoff
from clauderfall.validation.context import validate_context_packet


class ContextService:
    """Deterministic packet assembly from a task contract plus explicit supporting inputs."""

    def assemble_packet(
        self,
        task_artifact: TaskArtifact,
        supporting_items: list[ContextAssemblyItem],
        exclusions: list[ExclusionRecord] | None = None,
    ) -> ContextPacket:
        """Assemble and validate a context packet from explicit inputs."""

        gate = check_task_to_context_handoff(task_artifact)
        if not gate.accepted:
            raise ValueError(f"task artifact failed handoff preconditions: {'; '.join(gate.reasons)}")

        if not supporting_items:
            raise ValueError("supporting_items must not be empty")

        exclusions = exclusions or [
            ExclusionRecord(
                excluded_material="Adjacent repository context not explicitly required by the task contract",
                reason="Excluded by default to preserve minimality and prevent scope expansion.",
            )
        ]

        included_context = [
            IncludedContextItem(
                item_id=item.item_id,
                included_material=item.included_material,
                item_type=item.item_type,
                source_origin=item.source_origin,
            )
            for item in supporting_items
        ]

        inclusion_justification = [
            InclusionJustification(
                item_id=item.item_id,
                justification=item.justification,
                supports=item.supports,
            )
            for item in supporting_items
        ]

        traceability = [
            ContextTraceabilityRecord(
                target_ref="task_contract",
                supports=["task-contract origin"],
                trace_links=["task_artifact"],
            ),
            ContextTraceabilityRecord(
                target_ref="included_context",
                supports=["included-context origin"],
                trace_links=[item.source_origin for item in supporting_items],
            ),
            ContextTraceabilityRecord(
                target_ref="inclusion_justification",
                supports=["inclusion-justification target mapping"],
                trace_links=[link for item in supporting_items for link in item.trace_links] or ["supporting_items"],
            ),
        ]

        budget_summary = BudgetSummary(
            total_budget_measure=f"{len(supporting_items)} included items, {len(exclusions)} exclusions",
            shaping_decisions=[
                "Assembly used only explicit supporting inputs.",
                "Task contract was copied directly from the source task artifact.",
                "Default exclusions protect against adjacent but unnecessary context.",
            ],
        )

        packet = ContextPacket(
            task_contract=task_artifact,
            included_context=included_context,
            inclusion_justification=inclusion_justification,
            exclusions=exclusions,
            conflict_signals=[],
            budget_summary=budget_summary,
            traceability=traceability,
            completion_status={
                "readiness_state": ReadinessState.READY,
                "blocking_gaps": [],
                "non_blocking_gaps": [],
                "justification": "The packet was assembled from explicit task-scoped inputs and passed validation.",
            },
        )

        issues = validate_context_packet(packet)
        if issues:
            raise ValueError(f"context packet assembly failed validation: {'; '.join(issues)}")

        return packet
