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
    """Lifecycle-shaped recent-session runtime backed by filesystem artifacts."""

    session: SessionStore

    def session_read_startup_view(self) -> ArtifactRuntimeResult:
        current = self.session.current_startup_entry()
        recent_completed = self.session.archived_startup_entries(limit=5)
        rebuilt = False
        warnings: tuple[str, ...] = ()

        if not self.session.startup_projection_matches(
            current=current,
            recent_completed=recent_completed,
        ):
            self.session.write_startup_index(
                current=current,
                recent_completed=recent_completed,
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
                "current": current,
                "recent_completed": recent_completed,
            },
            metadata={
                "rebuilt": rebuilt,
                "has_current": current is not None,
                "recent_completed_count": len(recent_completed),
            },
        )

    def session_read_current(self) -> ArtifactRuntimeResult:
        row = self.session.read_current()
        if row is None or row.get("status") != "current":
            return ArtifactRuntimeResult(
                result=OperationResult(status=OperationStatus.ERROR, message="current carry-forward record not found"),
            )
        return ArtifactRuntimeResult(
            result=OperationResult(status=OperationStatus.OK, message="current carry-forward record read"),
            artifacts={
                "title": row["title"],
                "work_items": row["work_items"],
                "thread_markdown": row["thread_markdown"],
            },
            metadata={
                "artifact_id": "current",
                "checkpoint_id": row["checkpoint_id"],
                "updated_at": row["updated_at"],
            },
        )

    def session_write_handoff(
        self,
        *,
        title: str,
        work_items: list[str],
        thread_markdown: str,
        flush_reason: FlushReason = FlushReason.CHECKPOINT,
    ) -> ArtifactRuntimeResult:
        del flush_reason  # filesystem session artifacts are always authoritative
        projection_stale = not self.session.startup_projection_matches(
            current=self.session.current_startup_entry(),
            recent_completed=self.session.archived_startup_entries(limit=5),
        )
        written = self.session.write_current(
            title=title,
            work_items=work_items,
            thread_markdown=thread_markdown,
        )
        self.session.write_startup_index(
            current=self.session.current_startup_entry(),
            recent_completed=self.session.archived_startup_entries(limit=5),
        )
        return ArtifactRuntimeResult(
            result=OperationResult(status=OperationStatus.OK, message="current carry-forward handoff written"),
            metadata={
                "artifact_id": "current",
                "checkpoint_id": written["checkpoint_id"],
                "startup_index_updated": True,
                "projection_stale": projection_stale,
            },
        )

    def session_archive_current(self, *, closure_summary: str) -> ArtifactRuntimeResult:
        archived = self.session.archive_current(closure_summary=closure_summary)
        if archived is None:
            return ArtifactRuntimeResult(
                result=OperationResult(status=OperationStatus.ERROR, message="current carry-forward record not found"),
            )
        self.session.write_startup_index(
            current=self.session.current_startup_entry(),
            recent_completed=self.session.archived_startup_entries(limit=5),
        )
        return ArtifactRuntimeResult(
            result=OperationResult(status=OperationStatus.OK, message="current carry-forward record archived"),
            metadata={
                "history_id": archived["history_id"],
                "checkpoint_id": archived["checkpoint_id"],
            },
        )
