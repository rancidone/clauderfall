"""Session lifecycle runtime service."""

from __future__ import annotations

from dataclasses import dataclass

from clauderfall.runtime.session_store import SessionStore
from clauderfall.runtime.types import (
    ArtifactRuntimeResult,
    FlushReason,
    OperationResult,
    OperationStatus,
)


@dataclass
class SessionLifecycleService:
    """Lifecycle-shaped recent-session runtime backed by SQLite."""

    session: SessionStore

    def session_read_startup_view(self) -> ArtifactRuntimeResult:
        active_threads = self._active_startup_entries()
        recent_completed_threads = self._archived_startup_entries(limit=5)
        rebuilt = False
        warnings: tuple[str, ...] = ()

        if not self.session.startup_projection_matches(
            active_threads=active_threads,
            recent_completed_threads=recent_completed_threads,
        ):
            self.session.write_startup_index(
                active_threads=active_threads,
                recent_completed_threads=recent_completed_threads,
            )
            rebuilt = True
            warnings = ("startup_index_rebuilt",)

        return ArtifactRuntimeResult(
            result=OperationResult(
                status=OperationStatus.WARNING if rebuilt else OperationStatus.OK,
                message="recent session startup view read",
                warnings=warnings if rebuilt else (),
            ),
            artifacts={
                "active_threads": active_threads,
                "recent_completed_threads": recent_completed_threads,
            },
            metadata={
                "rebuilt": rebuilt,
                "active_thread_count": len(active_threads),
                "recent_completed_count": len(recent_completed_threads),
            },
        )

    def session_read_thread(self, *, thread_id: str) -> ArtifactRuntimeResult:
        row = self.session.read_thread(thread_id)
        if row is None or row.get("status") != "active":
            return ArtifactRuntimeResult(
                result=OperationResult(status=OperationStatus.ERROR, message="active thread not found"),
                metadata={"thread_id": thread_id},
            )
        return ArtifactRuntimeResult(
            result=OperationResult(status=OperationStatus.OK, message="active thread read"),
            artifacts={
                "thread_id": row["thread_id"],
                "title": row["title"],
                "work_items": row["work_items"],
                "thread_markdown": row["thread_markdown"],
            },
            metadata={
                "thread_id": thread_id,
                "updated_at": row["updated_at"],
            },
        )

    def session_write_handoff(
        self,
        *,
        thread_id: str,
        title: str,
        work_items: list[str],
        thread_markdown: str,
        flush_reason: FlushReason = FlushReason.CHECKPOINT,
    ) -> ArtifactRuntimeResult:
        del flush_reason  # ignored; filesystem session artifacts are always authoritative
        written = self.session.write_thread(
            thread_id=thread_id,
            title=title,
            work_items=work_items,
            thread_markdown=thread_markdown,
        )
        self.session.write_startup_index(
            active_threads=self._active_startup_entries(),
            recent_completed_threads=self._archived_startup_entries(limit=5),
        )
        return ArtifactRuntimeResult(
            result=OperationResult(status=OperationStatus.OK, message="active thread handoff written"),
            metadata={"thread_id": thread_id, "checkpoint_id": written["checkpoint_id"]},
        )

    def session_archive_thread(self, *, thread_id: str, closure_summary: str) -> ArtifactRuntimeResult:
        row = self.session.read_thread(thread_id)
        if row is None or row.get("status") != "active":
            return ArtifactRuntimeResult(
                result=OperationResult(status=OperationStatus.ERROR, message="active thread not found"),
                metadata={"thread_id": thread_id},
            )
        self.session.archive_thread(thread_id, closure_summary=closure_summary)
        self.session.write_startup_index(
            active_threads=self._active_startup_entries(),
            recent_completed_threads=self._archived_startup_entries(limit=5),
        )
        return ArtifactRuntimeResult(
            result=OperationResult(status=OperationStatus.OK, message="thread archived"),
        )

    def _active_startup_entries(self) -> list[dict[str, object]]:
        return [
            {
                "thread_id": row["thread_id"],
                "title": row["title"],
                "work_items": row["work_items"],
                "last_updated_at": row["updated_at"],
                "thread_artifact_ref": self.session.active_thread_artifact_ref(str(row["thread_id"])),
            }
            for row in self.session.list_active_threads()
        ]

    def _archived_startup_entries(self, *, limit: int) -> list[dict[str, object]]:
        return [
            {
                "thread_id": row["thread_id"],
                "title": row["title"],
                "closure_summary": row["closure_summary"] or "",
                "closed_at": row["closed_at"],
                "history_ref": self.session.archived_thread_artifact_ref(str(row["thread_id"])),
            }
            for row in self.session.list_recent_archived(limit=limit)
        ]
