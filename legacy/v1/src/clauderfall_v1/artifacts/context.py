"""Context Packet model."""

from __future__ import annotations

from pydantic import Field

from clauderfall_v1.artifacts.common import ArtifactBase, CompletionStatus, ConflictSeverity, IncludedItemType
from clauderfall_v1.artifacts.task import TaskArtifact


class IncludedContextItem(ArtifactBase):
    """Supporting material included in a context packet."""

    item_id: str = Field(min_length=1)
    included_material: str = Field(min_length=1)
    item_type: IncludedItemType
    source_origin: str = Field(min_length=1)


class ContextAssemblyItem(ArtifactBase):
    """Explicit supporting input used to assemble a context packet."""

    item_id: str = Field(min_length=1)
    included_material: str = Field(min_length=1)
    item_type: IncludedItemType
    source_origin: str = Field(min_length=1)
    justification: str = Field(min_length=1)
    supports: list[str] = Field(default_factory=list)
    trace_links: list[str] = Field(default_factory=list)


class InclusionJustification(ArtifactBase):
    """Justification for including a context item."""

    item_id: str = Field(min_length=1)
    justification: str = Field(min_length=1)
    supports: list[str] = Field(default_factory=list)


class ExclusionRecord(ArtifactBase):
    """Related material intentionally omitted from the packet."""

    excluded_material: str = Field(min_length=1)
    reason: str = Field(min_length=1)


class ConflictSignal(ArtifactBase):
    """Contradiction or ambiguity detected in the packet."""

    conflicting_elements: list[str] = Field(default_factory=list)
    nature_of_conflict: str = Field(min_length=1)
    impact_on_safe_execution: str = Field(min_length=1)
    severity: ConflictSeverity


class BudgetSummary(ArtifactBase):
    """Summary of packet sizing and reduction decisions."""

    total_budget_measure: str = Field(min_length=1)
    shaping_decisions: list[str] = Field(default_factory=list)


class ContextTraceabilityRecord(ArtifactBase):
    """Traceability record for a packet element."""

    target_ref: str = Field(min_length=1)
    supports: list[str] = Field(default_factory=list)
    trace_links: list[str] = Field(default_factory=list)


class ContextPacket(ArtifactBase):
    """Normative Context Packet aligned with context_packet.md."""

    task_contract: TaskArtifact
    included_context: list[IncludedContextItem] = Field(default_factory=list)
    inclusion_justification: list[InclusionJustification] = Field(default_factory=list)
    exclusions: list[ExclusionRecord] = Field(default_factory=list)
    conflict_signals: list[ConflictSignal] = Field(default_factory=list)
    budget_summary: BudgetSummary
    traceability: list[ContextTraceabilityRecord] = Field(default_factory=list)
    completion_status: CompletionStatus
