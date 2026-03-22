"""Design Artifact model."""

from __future__ import annotations

from pydantic import Field

from clauderfall.artifacts.common import ArtifactBase, CompletionStatus, DesignElementClassification
from clauderfall.artifacts.discovery import ScopeBoundaries


class ConstraintEncoding(ArtifactBase):
    """How a discovery constraint is enforced in design."""

    source_constraint_ref: str = Field(min_length=1)
    enforcing_design_element: str = Field(min_length=1)
    violation_consequence: str | None = None


class DecisionRecord(ArtifactBase):
    """Material design decision and its justification."""

    decision_statement: str = Field(min_length=1)
    affected_design_area: str = Field(min_length=1)
    alternatives_considered: list[str] = Field(default_factory=list)
    rationale: str = Field(min_length=1)
    consequences: list[str] = Field(default_factory=list)
    trace_links: list[str] = Field(default_factory=list)


class RiskAndEdgeCase(ArtifactBase):
    """Failure mode or edge condition relevant to downstream work."""

    condition: str = Field(min_length=1)
    affected_design_area: str = Field(min_length=1)
    expected_impact: str = Field(min_length=1)
    encoded_mitigation: str | None = None


class OpenDesignQuestion(ArtifactBase):
    """Unresolved question remaining after design."""

    question: str = Field(min_length=1)
    affected_design_areas: list[str] = Field(default_factory=list)


class TaskDecompositionSignals(ArtifactBase):
    """Cues required to partition design into bounded tasks."""

    natural_work_boundaries: list[str] = Field(default_factory=list)
    dependency_relationships: list[str] = Field(default_factory=list)
    acceptance_expectations_to_preserve: list[str] = Field(default_factory=list)
    sequencing_requirements: list[str] = Field(default_factory=list)


class TraceabilityRecord(ArtifactBase):
    """Traceability record for a major design element."""

    target_ref: str = Field(min_length=1)
    classification: DesignElementClassification
    supports: list[str] = Field(default_factory=list)
    trace_links: list[str] = Field(default_factory=list)


class DesignArtifact(ArtifactBase):
    """Normative Design Artifact aligned with design_artifact.md."""

    objective: list[str] = Field(default_factory=list)
    scope: ScopeBoundaries
    system_structure: list[str] = Field(default_factory=list)
    constraints_encoding: list[ConstraintEncoding] = Field(default_factory=list)
    invariants: list[str] = Field(default_factory=list)
    decisions: list[DecisionRecord] = Field(default_factory=list)
    risks_and_edge_cases: list[RiskAndEdgeCase] = Field(default_factory=list)
    open_design_questions: list[OpenDesignQuestion] = Field(default_factory=list)
    task_decomposition_signals: TaskDecompositionSignals
    traceability: list[TraceabilityRecord] = Field(default_factory=list)
    completion_status: CompletionStatus
