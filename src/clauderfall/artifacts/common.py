"""Shared artifact types and validation primitives."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class ReadinessState(StrEnum):
    READY = "ready"
    NOT_READY = "not_ready"


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


class ArtifactBase(BaseModel):
    """Base config shared by all normative artifact models."""

    model_config = ConfigDict(extra="forbid", use_attribute_docstrings=True)


class CompletionStatus(ArtifactBase):
    """Artifact readiness record shared by the normative specs."""

    readiness_state: ReadinessState
    blocking_gaps: list[str] = Field(default_factory=list)
    non_blocking_gaps: list[str] = Field(default_factory=list)
    justification: str = Field(min_length=1)
