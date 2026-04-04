"""Shared v2 runtime types."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field


class ArtifactStage(str, Enum):
    """Stable stage keys for the runtime filesystem layout."""

    DISCOVERY = "discovery"
    DESIGN = "design"
    SESSION = "session"
    TODO = "todo"


class FlushReason(str, Enum):
    """Controlled checkpoint flush reasons from the active design docs."""

    CHECKPOINT = "checkpoint"
    REVIEW_TRANSITION = "review_transition"
    REVIEW_DECISION = "review_decision"
    DECOMPOSITION = "decomposition"
    REENTRY_REPAIR = "reentry_repair"
    CONTEXT_SAFETY = "context_safety"


class OperationStatus(str, Enum):
    """Shared operation result vocabulary for the v2 runtime."""

    OK = "ok"
    WARNING = "warning"
    ERROR = "error"



@dataclass(frozen=True)
class ArtifactKey:
    """Stable logical identity for one persisted artifact."""

    stage: ArtifactStage
    artifact_id: str


@dataclass(frozen=True)
class ArtifactRecord:
    """Current persisted state of one artifact."""

    key: ArtifactKey
    version_id: str
    stage_metadata: dict[str, object]
    flush_reason: str
    updated_at: datetime


@dataclass(frozen=True)
class OperationResult:
    """Shared structured result object for deterministic runtime operations."""

    status: OperationStatus
    message: str
    warnings: tuple[str, ...] = field(default_factory=tuple)

    @property
    def ok(self) -> bool:
        return self.status != OperationStatus.ERROR


@dataclass(frozen=True)
class ArtifactRuntimeResult:
    """Standard shared result envelope for artifact runtime operations."""

    result: OperationResult
    warnings: tuple[str, ...] = field(default_factory=tuple)
    artifacts: dict[str, object] = field(default_factory=dict)
    metadata: dict[str, object] = field(default_factory=dict)


class ActiveThreadMetadata(BaseModel):
    """Authoritative structured metadata for one active thread handoff artifact."""

    model_config = ConfigDict(use_enum_values=True)

    thread_id: str
    title: str
    work_items: list[str] = Field(default_factory=list)
    updated_at: datetime


class StartupActiveThreadEntry(BaseModel):
    """Compact startup projection for one active thread."""

    model_config = ConfigDict(use_enum_values=True)

    thread_id: str
    title: str
    work_items: list[str] = Field(default_factory=list)
    last_updated_at: datetime


class ArchivedThreadRecord(BaseModel):
    """Compact archived-thread metadata retained for recent startup history."""

    model_config = ConfigDict(use_enum_values=True)

    thread_id: str
    title: str
    closure_summary: str
    closed_at: datetime


class RecentSessionIndexMetadata(BaseModel):
    """Repo-level derived startup projection over active and recent archived threads."""

    model_config = ConfigDict(use_enum_values=True)

    active_threads: list[StartupActiveThreadEntry] = Field(default_factory=list)
    recent_completed_threads: list[ArchivedThreadRecord] = Field(default_factory=list)
    projection_stale: bool = False
