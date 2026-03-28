"""Shared v2 runtime substrate contracts."""

from clauderfall.runtime.artifacts import StageArtifactRuntime
from clauderfall.runtime.checkpoints import CheckpointManager
from clauderfall.runtime.discovery import DiscoveryRuntimeService
from clauderfall.runtime.resolver import ArtifactResolver
from clauderfall.runtime.services import RuntimeServices, build_runtime_services
from clauderfall.runtime.store import ArtifactStore
from clauderfall.runtime.types import (
    ArtifactKey,
    ArtifactPair,
    ArtifactRef,
    ArtifactRuntimeResult,
    ArtifactStage,
    ArtifactView,
    CheckpointEnvelope,
    FlushReason,
    OperationResult,
    OperationStatus,
)

__all__ = [
    "ArtifactKey",
    "ArtifactPair",
    "ArtifactRef",
    "ArtifactRuntimeResult",
    "ArtifactResolver",
    "ArtifactStage",
    "ArtifactStore",
    "ArtifactView",
    "CheckpointEnvelope",
    "CheckpointManager",
    "DiscoveryRuntimeService",
    "FlushReason",
    "OperationResult",
    "OperationStatus",
    "RuntimeServices",
    "StageArtifactRuntime",
    "build_runtime_services",
]
