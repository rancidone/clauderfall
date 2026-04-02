"""Shared v2 runtime substrate contracts."""

from clauderfall.runtime.artifacts import StageArtifactRuntime
from clauderfall.runtime.design import DesignRuntimeService
from clauderfall.runtime.discovery import DiscoveryRuntimeService
from clauderfall.runtime.session_lifecycle import SessionLifecycleService
from clauderfall.runtime.session_store import SessionStore
from clauderfall.runtime.services import RuntimeServices, build_runtime_services
from clauderfall.runtime.store import ArtifactStore
from clauderfall.runtime.types import (
    ActiveThreadMetadata,
    ArtifactKey,
    ArtifactRecord,
    ArtifactRuntimeResult,
    ArtifactStage,
    ArchivedThreadRecord,
    FlushReason,
    OperationResult,
    OperationStatus,
    RecentSessionIndexMetadata,
    StartupActiveThreadEntry,
)

__all__ = [
    "ArtifactKey",
    "ArtifactRecord",
    "ArtifactRuntimeResult",
    "ActiveThreadMetadata",
    "ArchivedThreadRecord",
    "ArtifactStage",
    "ArtifactStore",
    "DesignRuntimeService",
    "DiscoveryRuntimeService",
    "FlushReason",
    "OperationResult",
    "OperationStatus",
    "RecentSessionIndexMetadata",
    "RuntimeServices",
    "SessionLifecycleService",
    "SessionStore",
    "StartupActiveThreadEntry",
    "StageArtifactRuntime",
    "build_runtime_services",
]
