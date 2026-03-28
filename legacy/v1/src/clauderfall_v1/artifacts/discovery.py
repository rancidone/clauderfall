"""Discovery Artifact model."""

from __future__ import annotations

from pydantic import Field, model_validator

from clauderfall_v1.artifacts.common import (
    ArtifactBase,
    CompletionStatus,
    ConfidenceLevel,
    Grounding,
    SourceClassification,
)


class ScopeBoundaries(ArtifactBase):
    """Specific boundaries that constrain interpretation during design."""

    in_scope: list[str] = Field(default_factory=list)
    out_of_scope: list[str] = Field(default_factory=list)
    boundary_notes: list[str] = Field(default_factory=list)


class SourceRegisterEntry(ArtifactBase):
    """Source used to build a discovery artifact."""

    source_id: str = Field(min_length=1)
    source_type: str = Field(min_length=1)
    origin_ref: str = Field(min_length=1)
    authority_level: str | None = None


class ProvenanceRecord(ArtifactBase):
    """Provenance metadata for a substantive artifact element."""

    target_ref: str = Field(min_length=1)
    source_classification: SourceClassification
    confidence: ConfidenceLevel
    grounding: Grounding
    trace_links: list[str] = Field(default_factory=list)


class DiscoveryArtifact(ArtifactBase):
    """Normative Discovery Artifact aligned with discovery_artifact.md."""

    problem_definition: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    success_criteria: list[str] = Field(default_factory=list)
    scope_boundaries: ScopeBoundaries
    risks: list[str] = Field(default_factory=list)
    unknowns: list[str] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)
    source_register: list[SourceRegisterEntry] = Field(default_factory=list)
    provenance_records: list[ProvenanceRecord] = Field(default_factory=list)
    completion_status: CompletionStatus

    @model_validator(mode="after")
    def validate_source_ids_unique(self) -> "DiscoveryArtifact":
        source_ids = [entry.source_id for entry in self.source_register]
        if len(source_ids) != len(set(source_ids)):
            raise ValueError("source_register.source_id values must be unique")
        return self

