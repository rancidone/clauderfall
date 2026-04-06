"""Shared v2 runtime substrate contracts."""

from clauderfall.runtime.artifacts import StageArtifactRuntime
from clauderfall.runtime.design import DesignRuntimeService
from clauderfall.runtime.discovery import DiscoveryRuntimeService
from clauderfall.runtime.session_lifecycle import SessionLifecycleService
from clauderfall.runtime.session_store import SessionStore
from clauderfall.runtime.services import RuntimeServices, build_runtime_services
from clauderfall.runtime.store import ArtifactStore
from clauderfall.runtime.types import (
    ArtifactKey,
    ArtifactRecord,
    ArtifactRuntimeResult,
    ArtifactStage,
    ArchivedSessionRecord,
    CurrentSessionMetadata,
    FlushReason,
    OperationResult,
    OperationStatus,
    RecentSessionIndexMetadata,
    StartupCurrentEntry,
)

__all__ = [
    "ArtifactKey",
    "ArtifactRecord",
    "ArtifactRuntimeResult",
    "ArchivedSessionRecord",
    "ArtifactStage",
    "ArtifactStore",
    "CurrentSessionMetadata",
    "DesignRuntimeService",
    "DiscoveryRuntimeService",
    "FlushReason",
    "OperationResult",
    "OperationStatus",
    "RecentSessionIndexMetadata",
    "RuntimeServices",
    "SessionLifecycleService",
    "SessionStore",
    "StartupCurrentEntry",
    "StageArtifactRuntime",
    "build_runtime_services",
]
