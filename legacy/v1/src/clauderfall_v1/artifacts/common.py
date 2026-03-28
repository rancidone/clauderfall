"""Shared artifact types and validation primitives."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class ReadinessState(StrEnum):
    READY = "ready"
    NOT_READY = "not_ready"


class ArtifactKind(StrEnum):
    DISCOVERY = "discovery"
    DESIGN = "design"
    TASK = "task"
    CONTEXT_PACKET = "context_packet"


class SourceClassification(StrEnum):
    EXPLICIT = "explicit"
    DERIVED = "derived"
    ASSUMED = "assumed"
    IMPORTED = "imported"
    REFINED = "refined"


class ConfidenceLevel(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Grounding(StrEnum):
    ANCHORED = "anchored"
    FLOATING = "floating"


class DesignElementClassification(StrEnum):
    GROUNDED = "grounded"
    INFERRED = "inferred"
    IMPORTED = "imported"
    UNRESOLVED = "unresolved"


class TaskElementClassification(StrEnum):
    GROUNDED = "grounded"
    INFERRED = "inferred"
    UNRESOLVED = "unresolved"


class IncludedItemType(StrEnum):
    ARTIFACT = "artifact"
    EXCERPT = "excerpt"
    REFERENCE = "reference"
    SOURCE_SURFACE = "source_surface"
    INTERFACE_DEFINITION = "interface_definition"
    ACCEPTANCE_REFERENCE = "acceptance_reference"
    OTHER_EXPLICIT_TYPE = "other_explicit_type"


class ConflictSeverity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ArtifactBase(BaseModel):
    """Base config shared by all normative artifact models."""

    model_config = ConfigDict(extra="forbid", use_attribute_docstrings=True)


class CompletionStatus(ArtifactBase):
    """Artifact readiness record shared by the normative specs."""

    readiness_state: ReadinessState
    blocking_gaps: list[str] = Field(default_factory=list)
    non_blocking_gaps: list[str] = Field(default_factory=list)
    justification: str = Field(min_length=1)


class ArtifactVersionRef(ArtifactBase):
    """Version-qualified persisted artifact reference."""

    artifact_kind: ArtifactKind
    artifact_id: str = Field(min_length=1)
    version: int = Field(ge=1)

    def to_ref_string(self) -> str:
        return f"{self.artifact_kind}:{self.artifact_id}@{self.version}"


class TraceLinkMatch(ArtifactBase):
    """Indexed trace-link match against a persisted artifact version."""

    artifact_kind: ArtifactKind
    artifact_id: str = Field(min_length=1)
    version: int = Field(ge=1)
    trace_link: str = Field(min_length=1)
    target_ref: str | None = None
