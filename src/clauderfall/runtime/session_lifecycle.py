"""Session lifecycle runtime service and bounded operation runner."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Callable, Generic, TypeVar

from clauderfall.runtime.artifacts import StageArtifactRuntime
from clauderfall.runtime.store import ArtifactStore
from clauderfall.runtime.types import (
    ActiveThreadMetadata,
    ArchivedThreadRecord,
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
    RecentSessionIndexMetadata,
    StartupActiveThreadEntry,
)


SESSION_INDEX_ARTIFACT_ID = "index/recent-session"
ACTIVE_THREADS_PREFIX = "active"
ARCHIVE_PREFIX = "history"
RECENT_COMPLETED_LIMIT = 5

TPrepare = TypeVar("TPrepare")
TExecute = TypeVar("TExecute")


@dataclass
class RunnerStepPlan(Generic[TPrepare, TExecute]):
    """Bounded lifecycle operation phases for one session-lifecycle action."""

    prepare: Callable[[], TPrepare]
    execute: Callable[[TPrepare], TExecute]
    verify: Callable[[TPrepare, TExecute], ArtifactRuntimeResult | None]
    recover: Callable[[TPrepare, TExecute | None, Exception | None], ArtifactRuntimeResult | None]


@dataclass
class SessionLifecycleOperationRunner:
    """Shared execute/verify/recover wrapper for lifecycle operations."""

    def run(
        self,
        *,
        operation_name: str,
        plan: RunnerStepPlan[TPrepare, TExecute],
    ) -> ArtifactRuntimeResult:
        del operation_name
        prepared = plan.prepare()
        executed: TExecute | None = None
        try:
            executed = plan.execute(prepared)
            verified = plan.verify(prepared, executed)
            if verified is not None:
                return verified
        except Exception as exc:  # pragma: no cover - exercised via recovery tests
            recovered = plan.recover(prepared, executed, exc)
            if recovered is not None:
                return recovered
            raise

        return ArtifactRuntimeResult(
            result=OperationResult(status=OperationStatus.OK, message="lifecycle operation completed"),
        )


@dataclass
class SessionLifecycleService:
    """Lifecycle-shaped recent-session runtime above the shared artifact substrate."""

    artifacts: StageArtifactRuntime
    store: ArtifactStore
    root: Path
    runner: SessionLifecycleOperationRunner
    recent_completed_limit: int = RECENT_COMPLETED_LIMIT

    def read_recent_session_startup_view(self, *, force_rebuild: bool = False) -> ArtifactRuntimeResult:
        active_metadata = self._load_active_thread_metadata()
        index_pair = self.store.load_current(ArtifactRef(key=self._session_key(SESSION_INDEX_ARTIFACT_ID)))
        recent_completed = self._load_recent_completed_records()

        if force_rebuild or self._startup_index_needs_rebuild(index_pair=index_pair, active_metadata=active_metadata):
            rebuilt = self.rebuild_recent_session_index(
                reason="operator_requested" if force_rebuild else "startup_validation"
            )
            if not rebuilt.result.ok:
                return rebuilt
            warning_codes = tuple(rebuilt.warnings)
            index_pair = self.store.load_current(ArtifactRef(key=self._session_key(SESSION_INDEX_ARTIFACT_ID)))
            assert index_pair is not None
            startup_index = RecentSessionIndexMetadata.model_validate(index_pair.metadata.stage_metadata)
            return ArtifactRuntimeResult(
                result=OperationResult(
                    status=OperationStatus.WARNING if warning_codes else OperationStatus.OK,
                    message="recent session startup view read",
                ),
                warnings=warning_codes,
                artifacts={
                    "startup_index_ref": ArtifactRef(
                        key=self._session_key(SESSION_INDEX_ARTIFACT_ID),
                        checkpoint_id=index_pair.metadata.checkpoint_id,
                    ),
                    "active_threads": [entry.model_dump(mode="json") for entry in startup_index.active_threads],
                    "recent_completed_threads": [
                        entry.model_dump(mode="json") for entry in startup_index.recent_completed_threads
                    ],
                },
                metadata={
                    "rebuilt": True,
                    "active_thread_count": len(startup_index.active_threads),
                    "recent_completed_count": len(startup_index.recent_completed_threads),
                    "startup_index_checkpoint_id": index_pair.metadata.checkpoint_id,
                },
            )

        assert index_pair is not None
        startup_index = RecentSessionIndexMetadata.model_validate(index_pair.metadata.stage_metadata)
        return ArtifactRuntimeResult(
            result=OperationResult(status=OperationStatus.OK, message="recent session startup view read"),
            artifacts={
                "startup_index_ref": ArtifactRef(
                    key=self._session_key(SESSION_INDEX_ARTIFACT_ID),
                    checkpoint_id=index_pair.metadata.checkpoint_id,
                ),
                "active_threads": [entry.model_dump(mode="json") for entry in startup_index.active_threads],
                "recent_completed_threads": [entry.model_dump(mode="json") for entry in startup_index.recent_completed_threads],
            },
            metadata={
                "rebuilt": False,
                "active_thread_count": len(startup_index.active_threads),
                "recent_completed_count": len(startup_index.recent_completed_threads),
                "startup_index_checkpoint_id": index_pair.metadata.checkpoint_id,
            },
        )

    def read_active_thread(self, *, thread_id: str) -> ArtifactRuntimeResult:
        result = self.artifacts.read_artifact(
            key=self._session_key(self._active_artifact_id(thread_id)),
            view=ArtifactView.FULL,
        )
        if not result.result.ok:
            return ArtifactRuntimeResult(
                result=OperationResult(status=OperationStatus.ERROR, message="active thread not found"),
                metadata={"thread_id": thread_id},
            )

        metadata = ActiveThreadMetadata.model_validate(result.artifacts["stage_metadata"])
        return ArtifactRuntimeResult(
            result=OperationResult(status=OperationStatus.OK, message="active thread read"),
            artifacts={
                "artifact_ref": result.artifacts["artifact_ref"],
                "thread_markdown": result.artifacts["markdown"],
                "thread_metadata": metadata.model_dump(mode="json"),
            },
            metadata={
                "thread_id": thread_id,
                "artifact_id": self._active_artifact_id(thread_id),
                "checkpoint_id": result.metadata["checkpoint_id"],
                "updated_at": metadata.updated_at,
            },
        )

    def write_active_thread_handoff(
        self,
        *,
        thread_id: str,
        title: str,
        current_intent_summary: str,
        next_suggested_action: str,
        thread_markdown: str,
        flush_reason: FlushReason = FlushReason.CHECKPOINT,
    ) -> ArtifactRuntimeResult:
        metadata = ActiveThreadMetadata(
            thread_id=thread_id,
            title=title,
            current_intent_summary=current_intent_summary,
            next_suggested_action=next_suggested_action,
            updated_at=datetime.now(UTC),
        )

        def prepare() -> ActiveThreadMetadata:
            return metadata

        def execute(prepared: ActiveThreadMetadata) -> ArtifactRuntimeResult:
            return self.artifacts.write_artifact_checkpoint(
                key=self._session_key(self._active_artifact_id(thread_id)),
                markdown=thread_markdown,
                stage_metadata=prepared.model_dump(mode="json"),
                flush_reason=flush_reason,
            )

        def verify(prepared: ActiveThreadMetadata, thread_write: ArtifactRuntimeResult) -> ArtifactRuntimeResult | None:
            if not thread_write.result.ok:
                return thread_write

            try:
                index_result = self._persist_recent_session_index(reason="handoff_recovery")
            except Exception:
                return ArtifactRuntimeResult(
                    result=OperationResult(
                        status=OperationStatus.WARNING,
                        message="active thread handoff written with stale startup projection",
                    ),
                    warnings=("startup_projection_stale",),
                    artifacts={"thread_artifact_ref": thread_write.artifacts["artifact_ref"]},
                    metadata={
                        "thread_id": thread_id,
                        "artifact_id": self._active_artifact_id(thread_id),
                        "checkpoint_id": thread_write.metadata["checkpoint_id"],
                        "startup_index_updated": False,
                        "projection_stale": True,
                    },
                )

            return ArtifactRuntimeResult(
                result=OperationResult(status=OperationStatus.OK, message="active thread handoff written"),
                artifacts={
                    "thread_artifact_ref": thread_write.artifacts["artifact_ref"],
                    "startup_index_ref": index_result.artifacts["startup_index_ref"],
                },
                metadata={
                    "thread_id": thread_id,
                    "artifact_id": self._active_artifact_id(thread_id),
                    "checkpoint_id": thread_write.metadata["checkpoint_id"],
                    "startup_index_updated": True,
                    "projection_stale": False,
                },
            )

        def recover(
            prepared: ActiveThreadMetadata,
            executed: ArtifactRuntimeResult | None,
            error: Exception | None,
        ) -> ArtifactRuntimeResult | None:
            del prepared, error
            if executed is None:
                return None
            return ArtifactRuntimeResult(
                result=OperationResult(
                    status=OperationStatus.WARNING,
                    message="active thread handoff written with stale startup projection",
                ),
                warnings=("startup_projection_stale",),
                artifacts={"thread_artifact_ref": executed.artifacts["artifact_ref"]},
                metadata={
                    "thread_id": thread_id,
                    "artifact_id": self._active_artifact_id(thread_id),
                    "checkpoint_id": executed.metadata["checkpoint_id"],
                    "startup_index_updated": False,
                    "projection_stale": True,
                },
            )

        return self.runner.run(
            operation_name="write_active_thread_handoff",
            plan=RunnerStepPlan(
                prepare=prepare,
                execute=execute,
                verify=verify,
                recover=recover,
            ),
        )

    def rebuild_recent_session_index(self, *, reason: str) -> ArtifactRuntimeResult:
        del reason
        return self._persist_recent_session_index(reason="startup_validation")

    def archive_completed_thread(self, *, thread_id: str, closure_summary: str) -> ArtifactRuntimeResult:
        def prepare() -> tuple[ArtifactRuntimeResult, ActiveThreadMetadata]:
            current = self.artifacts.read_artifact(
                key=self._session_key(self._active_artifact_id(thread_id)),
                view=ArtifactView.FULL,
            )
            if not current.result.ok:
                return (
                    ArtifactRuntimeResult(
                        result=OperationResult(status=OperationStatus.ERROR, message="active thread not found"),
                        metadata={"thread_id": thread_id},
                    ),
                    ActiveThreadMetadata(
                        thread_id=thread_id,
                        title="",
                        current_intent_summary="",
                        next_suggested_action="",
                        updated_at=datetime.now(UTC),
                    ),
                )
            metadata = ActiveThreadMetadata.model_validate(current.artifacts["stage_metadata"])
            return current, metadata

        def execute(prepared: tuple[ArtifactRuntimeResult, ActiveThreadMetadata]) -> dict[str, object]:
            active_result, metadata = prepared
            if not active_result.result.ok:
                return {"active_result": active_result}

            closed_at = datetime.now(UTC)
            archive_record = ArchivedThreadRecord(
                thread_id=thread_id,
                title=metadata.title,
                closure_summary=closure_summary,
                closed_at=closed_at,
                archived_artifact_ref=self._artifact_ref_string(self._archive_artifact_id(thread_id)),
            )
            history_write = self.artifacts.write_artifact_checkpoint(
                key=self._session_key(self._archive_artifact_id(thread_id)),
                markdown=active_result.artifacts["markdown"],
                stage_metadata=archive_record.model_dump(mode="json"),
                flush_reason=FlushReason.REVIEW_DECISION,
            )
            if not history_write.result.ok:
                return {"active_result": active_result, "history_write": history_write}

            self._remove_active_thread(thread_id)
            index_result = self._persist_recent_session_index(reason="archive_transition")
            return {
                "active_result": active_result,
                "history_write": history_write,
                "index_result": index_result,
            }

        def verify(
            prepared: tuple[ArtifactRuntimeResult, ActiveThreadMetadata],
            executed: dict[str, object],
        ) -> ArtifactRuntimeResult | None:
            active_result, _ = prepared
            if not active_result.result.ok:
                return active_result

            history_write = executed["history_write"]
            index_result = executed["index_result"]
            active_current = self.store.load_current(ArtifactRef(key=self._session_key(self._active_artifact_id(thread_id))))
            if active_current is not None:
                return None
            return ArtifactRuntimeResult(
                result=OperationResult(status=OperationStatus.OK, message="thread archived"),
                artifacts={
                    "archived_thread_ref": history_write.artifacts["artifact_ref"],
                    "startup_index_ref": index_result.artifacts["startup_index_ref"],
                },
                metadata={
                    "thread_id": thread_id,
                    "history_checkpoint_id": history_write.metadata["checkpoint_id"],
                    "active_removed": True,
                },
            )

        def recover(
            prepared: tuple[ArtifactRuntimeResult, ActiveThreadMetadata],
            executed: dict[str, object] | None,
            error: Exception | None,
        ) -> ArtifactRuntimeResult | None:
            del error
            active_result, metadata = prepared
            if not active_result.result.ok:
                return active_result

            if executed and executed.get("history_write") is not None:
                self._remove_archive_thread(thread_id)
            self.artifacts.write_artifact_checkpoint(
                key=self._session_key(self._active_artifact_id(thread_id)),
                markdown=active_result.artifacts["markdown"],
                stage_metadata=metadata.model_dump(mode="json"),
                flush_reason=FlushReason.REENTRY_REPAIR,
            )
            self._persist_recent_session_index(reason="archive_recovery")
            return ArtifactRuntimeResult(
                result=OperationResult(
                    status=OperationStatus.WARNING,
                    message="archive transition reverted to active state",
                ),
                warnings=("archive_reverted_to_active",),
                artifacts={"thread_artifact_ref": active_result.artifacts["artifact_ref"]},
                metadata={"thread_id": thread_id, "recovered": True},
            )

        return self.runner.run(
            operation_name="archive_completed_thread",
            plan=RunnerStepPlan(
                prepare=prepare,
                execute=execute,
                verify=verify,
                recover=recover,
            ),
        )

    def _persist_recent_session_index(self, *, reason: str) -> ArtifactRuntimeResult:
        active_entries = self._project_active_threads()
        recent_completed = self._load_recent_completed_records()
        index = RecentSessionIndexMetadata(
            active_threads=active_entries,
            recent_completed_threads=recent_completed[: self.recent_completed_limit],
            projection_stale=False,
        )
        markdown = self._render_startup_index_markdown(index)
        write = self.artifacts.write_artifact_checkpoint(
            key=self._session_key(SESSION_INDEX_ARTIFACT_ID),
            markdown=markdown,
            stage_metadata=index.model_dump(mode="json"),
            flush_reason=FlushReason.CONTEXT_SAFETY if reason == "startup_validation" else FlushReason.CHECKPOINT,
        )
        return ArtifactRuntimeResult(
            result=OperationResult(status=OperationStatus.OK, message="recent session index rebuilt"),
            warnings=("startup_index_rebuilt",),
            artifacts={"startup_index_ref": write.artifacts["artifact_ref"]},
            metadata={
                "rebuilt": True,
                "active_thread_count": len(index.active_threads),
                "recent_completed_count": len(index.recent_completed_threads),
                "startup_index_checkpoint_id": write.metadata["checkpoint_id"],
            },
        )

    def _project_active_threads(self) -> list[StartupActiveThreadEntry]:
        entries = [
            StartupActiveThreadEntry(
                thread_id=metadata.thread_id,
                title=metadata.title,
                current_intent_summary=metadata.current_intent_summary,
                last_updated_at=metadata.updated_at,
                thread_artifact_ref=self._artifact_ref_string(self._active_artifact_id(metadata.thread_id)),
                next_suggested_action=metadata.next_suggested_action,
            )
            for metadata in self._load_active_thread_metadata()
        ]
        return sorted(entries, key=lambda entry: (-int(entry.last_updated_at.timestamp()), entry.thread_id))

    def _load_active_thread_metadata(self) -> list[ActiveThreadMetadata]:
        base_dir = self.root / ArtifactStage.SESSION.value / ACTIVE_THREADS_PREFIX
        if not base_dir.exists():
            return []

        metadata: list[ActiveThreadMetadata] = []
        for child in sorted(path for path in base_dir.iterdir() if path.is_dir()):
            pair = self.store.load_current(ArtifactRef(key=self._session_key(self._active_artifact_id(child.name))))
            if pair is None:
                continue
            metadata.append(ActiveThreadMetadata.model_validate(pair.metadata.stage_metadata))
        return metadata

    def _load_recent_completed_records(self) -> list[ArchivedThreadRecord]:
        base_dir = self.root / ArtifactStage.SESSION.value / ARCHIVE_PREFIX
        if not base_dir.exists():
            return []

        records: list[ArchivedThreadRecord] = []
        for child in sorted(path for path in base_dir.iterdir() if path.is_dir()):
            pair = self.store.load_current(ArtifactRef(key=self._session_key(self._archive_artifact_id(child.name))))
            if pair is None:
                continue
            records.append(ArchivedThreadRecord.model_validate(pair.metadata.stage_metadata))
        return sorted(records, key=lambda entry: (-int(entry.closed_at.timestamp()), entry.thread_id))

    def _startup_index_needs_rebuild(
        self,
        *,
        index_pair: ArtifactPair | None,
        active_metadata: list[ActiveThreadMetadata],
    ) -> bool:
        if index_pair is None:
            return True
        try:
            index = RecentSessionIndexMetadata.model_validate(index_pair.metadata.stage_metadata)
        except Exception:
            return True

        projected = self._project_active_threads()
        if len(index.active_threads) != len(projected):
            return True
        for current, expected in zip(index.active_threads, projected, strict=False):
            if current.thread_id != expected.thread_id:
                return True
            if current.last_updated_at != expected.last_updated_at:
                return True
            if current.title != expected.title:
                return True
            if current.current_intent_summary != expected.current_intent_summary:
                return True
            if current.next_suggested_action != expected.next_suggested_action:
                return True
        return False

    def _remove_active_thread(self, thread_id: str) -> None:
        artifact_root = self.root / ArtifactStage.SESSION.value / ACTIVE_THREADS_PREFIX / thread_id
        if artifact_root.exists():
            shutil.rmtree(artifact_root)

    def _remove_archive_thread(self, thread_id: str) -> None:
        artifact_root = self.root / ArtifactStage.SESSION.value / ARCHIVE_PREFIX / thread_id
        if artifact_root.exists():
            shutil.rmtree(artifact_root)

    def _render_startup_index_markdown(self, index: RecentSessionIndexMetadata) -> str:
        lines = ["# Recent Session Startup View", "", "## Active Threads"]
        if not index.active_threads:
            lines.append("- None")
        else:
            for entry in index.active_threads:
                lines.append(f"- {entry.title} ({entry.thread_id}): {entry.current_intent_summary}")

        lines.extend(["", "## Recent Completed"])
        if not index.recent_completed_threads:
            lines.append("- None")
        else:
            for entry in index.recent_completed_threads:
                lines.append(f"- {entry.title} ({entry.thread_id}): {entry.closure_summary}")
        lines.append("")
        return "\n".join(lines)

    def _artifact_ref_string(self, artifact_id: str) -> str:
        return f"{ArtifactStage.SESSION.value}/{artifact_id}"

    def _session_key(self, artifact_id: str) -> ArtifactKey:
        return ArtifactKey(stage=ArtifactStage.SESSION, artifact_id=artifact_id)

    def _active_artifact_id(self, thread_id: str) -> str:
        return f"{ACTIVE_THREADS_PREFIX}/{thread_id}"

    def _archive_artifact_id(self, thread_id: str) -> str:
        return f"{ARCHIVE_PREFIX}/{thread_id}"
