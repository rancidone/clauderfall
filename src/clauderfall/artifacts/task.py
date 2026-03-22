"""Task Artifact model."""

from __future__ import annotations

from pydantic import Field

from clauderfall.artifacts.common import ArtifactBase, CompletionStatus, TaskElementClassification
from clauderfall.artifacts.discovery import ScopeBoundaries


class TaskTraceabilityRecord(ArtifactBase):
    """Traceability record for a major task element."""

    target_ref: str = Field(min_length=1)
    classification: TaskElementClassification
    supports: list[str] = Field(default_factory=list)
    trace_links: list[str] = Field(default_factory=list)


class TaskArtifact(ArtifactBase):
    """Normative Task Artifact aligned with task_artifact.md."""

    objective: list[str] = Field(default_factory=list)
    scope: ScopeBoundaries
    inputs: list[str] = Field(default_factory=list)
    outputs: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    invariants: list[str] = Field(default_factory=list)
    acceptance_criteria: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    traceability: list[TaskTraceabilityRecord] = Field(default_factory=list)
    completion_status: CompletionStatus
