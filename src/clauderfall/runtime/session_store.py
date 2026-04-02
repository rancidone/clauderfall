"""Purpose-built SQLite session store for thread lifecycle state."""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from pathlib import Path


class SessionStore:
    """Read and write session thread records via SQLite."""

    def __init__(self, *, db_path: Path) -> None:
        self.db_path = db_path

    def read_thread(self, thread_id: str) -> dict | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM threads WHERE thread_id = ?",
                (thread_id,),
            ).fetchone()
        if row is None:
            return None
        return dict(row)

    def write_thread(
        self,
        *,
        thread_id: str,
        title: str,
        current_intent_summary: str,
        next_suggested_action: str,
        thread_markdown: str,
    ) -> dict:
        updated_at = datetime.now(UTC).isoformat()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO threads (thread_id, status, title, current_intent_summary, next_suggested_action, thread_markdown, updated_at)
                VALUES (?, 'active', ?, ?, ?, ?, ?)
                ON CONFLICT (thread_id) DO UPDATE SET
                    title = excluded.title,
                    current_intent_summary = excluded.current_intent_summary,
                    next_suggested_action = excluded.next_suggested_action,
                    thread_markdown = excluded.thread_markdown,
                    updated_at = excluded.updated_at
                """,
                (thread_id, title, current_intent_summary, next_suggested_action, thread_markdown, updated_at),
            )
            row = conn.execute("SELECT * FROM threads WHERE thread_id = ?", (thread_id,)).fetchone()
        return dict(row)

    def archive_thread(self, thread_id: str, *, closure_summary: str) -> dict | None:
        closed_at = datetime.now(UTC).isoformat()
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE threads
                SET status = 'archived', closure_summary = ?, closed_at = ?, updated_at = ?
                WHERE thread_id = ?
                """,
                (closure_summary, closed_at, closed_at, thread_id),
            )
            row = conn.execute("SELECT * FROM threads WHERE thread_id = ?", (thread_id,)).fetchone()
        if row is None:
            return None
        return dict(row)

    def list_active_threads(self) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM threads WHERE status = 'active' ORDER BY updated_at DESC"
            ).fetchall()
        return [dict(row) for row in rows]

    def list_recent_archived(self, *, limit: int = 5) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM threads WHERE status = 'archived' ORDER BY closed_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
