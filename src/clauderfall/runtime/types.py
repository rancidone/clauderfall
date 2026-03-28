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


class ArtifactView(str, Enum):
    """Read shape for shared artifact runtime operations."""

    SHORT = "short"
    FULL = "full"


@dataclass(frozen=True)
class ArtifactKey:
    """Stable logical identity for one persisted artifact."""

    stage: ArtifactStage
    artifact_id: str


@dataclass(frozen=True)
class ArtifactRef:
    """Address either the current artifact or a specific checkpoint."""

    key: ArtifactKey
    checkpoint_id: str | None = None


@dataclass(frozen=True)
class ArtifactPair:
    """Readable artifact content plus structured metadata."""

    markdown: str
    metadata: "CheckpointEnvelope"


@dataclass(frozen=True)
class ResolvedArtifactPaths:
    """Filesystem paths for one logical artifact and optional checkpoint."""

    key: ArtifactKey
    artifact_root: Path
    current_dir: Path
    current_markdown_path: Path
    current_metadata_path: Path
    checkpoints_dir: Path
    checkpoint_id: str | None = None
    checkpoint_dir: Path | None = None
    checkpoint_markdown_path: Path | None = None
    checkpoint_metadata_path: Path | None = None


class CheckpointEnvelope(BaseModel):
    """Standard checkpoint metadata envelope plus stage-specific fields."""

    model_config = ConfigDict(use_enum_values=True)

    artifact_id: str
    checkpoint_id: str
    created_at: datetime
    flush_reason: FlushReason
    is_current: bool
    stage_metadata: dict[str, object] = Field(default_factory=dict)

    @classmethod
    def create(
        cls,
        *,
        artifact_id: str,
        checkpoint_id: str,
        flush_reason: FlushReason,
        stage_metadata: dict[str, object] | None = None,
        created_at: datetime | None = None,
        is_current: bool = True,
    ) -> "CheckpointEnvelope":
        return cls(
            artifact_id=artifact_id,
            checkpoint_id=checkpoint_id,
            created_at=created_at or datetime.now(UTC),
            flush_reason=flush_reason,
            is_current=is_current,
            stage_metadata=stage_metadata or {},
        )


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
