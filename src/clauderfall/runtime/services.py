"""Runtime service wiring for the v2 substrate."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from clauderfall.debug_log import configure as _configure_debug_log
from clauderfall.runtime.artifacts import StageArtifactRuntime
from clauderfall.runtime.design import DesignRuntimeService
from clauderfall.runtime.discovery import DiscoveryRuntimeService
from clauderfall.runtime.session_lifecycle import SessionLifecycleService
from clauderfall.runtime.session_store import SessionStore
from clauderfall.runtime.store import ArtifactStore


@dataclass(frozen=True)
class RuntimeServices:
    """Shared substrate services for the v2 runtime spine."""

    store: ArtifactStore
    session: SessionStore
    artifacts: StageArtifactRuntime
    discovery: DiscoveryRuntimeService
    design: DesignRuntimeService
    session_lifecycle: SessionLifecycleService


def build_runtime_services(docs_root: Path, *, repo_root: Path | None = None) -> RuntimeServices:
    db_path = (repo_root if repo_root is not None else docs_root) / "clauderfall.db"
    _configure_debug_log(db_path)
    store = ArtifactStore(db_path=db_path, docs_root=docs_root)
    session = SessionStore(db_path=db_path)
    artifacts = StageArtifactRuntime(store=store)
    discovery = DiscoveryRuntimeService(artifacts=artifacts)
    design = DesignRuntimeService(artifacts=artifacts)
    session_lifecycle = SessionLifecycleService(session=session)
    return RuntimeServices(
        store=store,
        session=session,
        artifacts=artifacts,
        discovery=discovery,
        design=design,
        session_lifecycle=session_lifecycle,
    )
