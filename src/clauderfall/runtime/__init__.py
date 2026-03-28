"""Shared v2 runtime substrate contracts."""

from clauderfall.runtime.artifacts import StageArtifactRuntime
from clauderfall.runtime.checkpoints import CheckpointManager
from clauderfall.runtime.design import DesignRuntimeService
from clauderfall.runtime.discovery import DiscoveryRuntimeService
from clauderfall.runtime.resolver import ArtifactResolver
from clauderfall.runtime.session_lifecycle import SessionLifecycleOperationRunner, SessionLifecycleService
from clauderfall.runtime.services import RuntimeServices, build_runtime_services
from clauderfall.runtime.store import ArtifactStore
from clauderfall.runtime.types import (
    ActiveThreadMetadata,
    ArtifactKey,
    ArtifactPair,
    ArtifactRef,
    ArtifactRuntimeResult,
    ArtifactStage,
    ArtifactView,
    ArchivedThreadRecord,
    CheckpointEnvelope,
    FlushReason,
    OperationResult,
    OperationStatus,
    RecentSessionIndexMetadata,
    StartupActiveThreadEntry,
)

__all__ = [
    "ArtifactKey",
    "ArtifactPair",
    "ArtifactRef",
    "ArtifactRuntimeResult",
    "ArtifactResolver",
    "ActiveThreadMetadata",
    "ArchivedThreadRecord",
    "ArtifactStage",
    "ArtifactStore",
    "ArtifactView",
    "CheckpointEnvelope",
    "CheckpointManager",
    "DesignRuntimeService",
    "DiscoveryRuntimeService",
    "FlushReason",
    "OperationResult",
    "OperationStatus",
    "RecentSessionIndexMetadata",
    "RuntimeServices",
    "SessionLifecycleOperationRunner",
    "SessionLifecycleService",
    "StartupActiveThreadEntry",
    "StageArtifactRuntime",
    "build_runtime_services",
]
