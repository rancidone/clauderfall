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

    def read_recent_session_startup_view(self, *, force_rebuild: bool = False) -> ArtifactRuntimeResult:
        del force_rebuild  # DB always current; rebuild is a no-op
        active_rows = self.session.list_active_threads()
        archived_rows = self.session.list_recent_archived(limit=5)

        active_threads = [
            {
                "thread_id": row["thread_id"],
                "title": row["title"],
                "current_intent_summary": row["current_intent_summary"],
                "next_suggested_action": row["next_suggested_action"],
                "last_updated_at": row["updated_at"],
            }
            for row in active_rows
        ]
        recent_completed_threads = [
            {
                "thread_id": row["thread_id"],
                "title": row["title"],
                "closure_summary": row["closure_summary"] or "",
                "closed_at": row["closed_at"],
            }
            for row in archived_rows
        ]

        return ArtifactRuntimeResult(
            result=OperationResult(status=OperationStatus.OK, message="recent session startup view read"),
            artifacts={
                "active_threads": active_threads,
                "recent_completed_threads": recent_completed_threads,
            },
            metadata={
                "rebuilt": False,
                "active_thread_count": len(active_threads),
                "recent_completed_count": len(recent_completed_threads),
            },
        )

    def read_active_thread(self, *, thread_id: str) -> ArtifactRuntimeResult:
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
                "current_intent_summary": row["current_intent_summary"],
                "next_suggested_action": row["next_suggested_action"],
                "thread_markdown": row["thread_markdown"],
            },
            metadata={
                "thread_id": thread_id,
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
        del flush_reason  # ignored; DB is always authoritative
        self.session.write_thread(
            thread_id=thread_id,
            title=title,
            current_intent_summary=current_intent_summary,
            next_suggested_action=next_suggested_action,
            thread_markdown=thread_markdown,
        )
        return ArtifactRuntimeResult(
            result=OperationResult(status=OperationStatus.OK, message="active thread handoff written"),
            artifacts={"thread_id": thread_id},
            metadata={
                "thread_id": thread_id,
                "startup_index_updated": True,
                "projection_stale": False,
            },
        )

    def rebuild_recent_session_index(self, *, reason: str) -> ArtifactRuntimeResult:
        del reason
        return self.read_recent_session_startup_view()

    def archive_completed_thread(self, *, thread_id: str, closure_summary: str) -> ArtifactRuntimeResult:
        row = self.session.read_thread(thread_id)
        if row is None or row.get("status") != "active":
            return ArtifactRuntimeResult(
                result=OperationResult(status=OperationStatus.ERROR, message="active thread not found"),
                metadata={"thread_id": thread_id},
            )
        self.session.archive_thread(thread_id, closure_summary=closure_summary)
        return ArtifactRuntimeResult(
            result=OperationResult(status=OperationStatus.OK, message="thread archived"),
            artifacts={"thread_id": thread_id},
            metadata={
                "thread_id": thread_id,
                "active_removed": True,
            },
        )
