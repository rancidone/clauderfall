"""Runtime service wiring for the v2 substrate."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from clauderfall.runtime.artifacts import StageArtifactRuntime
from clauderfall.runtime.checkpoints import CheckpointManager
from clauderfall.runtime.discovery import DiscoveryRuntimeService
from clauderfall.runtime.resolver import ArtifactResolver
from clauderfall.runtime.store import ArtifactStore


@dataclass(frozen=True)
class RuntimeServices:
    """Shared substrate services for the v2 runtime spine."""

    root: Path
    resolver: ArtifactResolver
    checkpoints: CheckpointManager
    store: ArtifactStore
    artifacts: StageArtifactRuntime
    discovery: DiscoveryRuntimeService


def build_runtime_services(root: Path) -> RuntimeServices:
    resolver = ArtifactResolver(root=root)
    checkpoints = CheckpointManager()
    store = ArtifactStore(resolver=resolver)
    artifacts = StageArtifactRuntime(store=store, checkpoints=checkpoints)
    discovery = DiscoveryRuntimeService(artifacts=artifacts)
    return RuntimeServices(
        root=root,
        resolver=resolver,
        checkpoints=checkpoints,
        store=store,
        artifacts=artifacts,
        discovery=discovery,
    )
