"""Filesystem-backed session store for bounded thread handoff state."""

from __future__ import annotations

import json
import shutil
import sqlite3
import uuid
from datetime import UTC, datetime
from pathlib import Path

import yaml


class SessionStore:
    """Read and write session thread artifacts from the repo filesystem."""

    def __init__(self, *, docs_root: Path, legacy_db_path: Path | None = None) -> None:
        self.docs_root = docs_root
        self.root = docs_root / "session"
        self.legacy_db_path = legacy_db_path
        self.root.mkdir(parents=True, exist_ok=True)
        self._migrate_legacy_sqlite_threads_if_needed()

    def read_thread(self, thread_id: str) -> dict | None:
        return self._read_thread_record(self._active_thread_dir(thread_id))

    def write_thread(
        self,
        *,
        thread_id: str,
        title: str,
        work_items: list[str],
        thread_markdown: str,
    ) -> dict:
        updated_at = datetime.now(UTC).isoformat()
        checkpoint_id = uuid.uuid4().hex
        metadata = {
            "thread_id": thread_id,
            "title": title,
            "work_items": work_items,
            "updated_at": updated_at,
        }
        self._write_artifact_pair(
            artifact_dir=self._active_thread_dir(thread_id),
            markdown=thread_markdown,
            metadata=metadata,
            checkpoint_id=checkpoint_id,
        )
        return {
            **metadata,
            "thread_markdown": thread_markdown,
            "status": "active",
            "checkpoint_id": checkpoint_id,
        }

    def archive_thread(self, thread_id: str, *, closure_summary: str) -> dict | None:
        active_dir = self._active_thread_dir(thread_id)
        active_record = self._read_thread_record(active_dir)
        if active_record is None:
            return None

        archive_dir = self._archive_thread_dir(thread_id)
        if archive_dir.exists():
            shutil.rmtree(archive_dir)
        archive_dir.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(active_dir, archive_dir)

        closed_at = datetime.now(UTC).isoformat()
        checkpoint_id = uuid.uuid4().hex
        archive_metadata = {
            "thread_id": thread_id,
            "title": active_record["title"],
            "closure_summary": closure_summary,
            "closed_at": closed_at,
        }
        self._write_artifact_pair(
            artifact_dir=archive_dir,
            markdown=active_record["thread_markdown"],
            metadata=archive_metadata,
            checkpoint_id=checkpoint_id,
        )
        shutil.rmtree(active_dir)
        return {
            **archive_metadata,
            "thread_markdown": active_record["thread_markdown"],
            "status": "archived",
            "checkpoint_id": checkpoint_id,
        }

    def list_active_threads(self) -> list[dict]:
        records = self._read_records_from_parent(self.root / "active")
        return sorted(records, key=lambda row: (row["updated_at"], row["thread_id"]), reverse=True)

    def list_recent_archived(self, *, limit: int = 5) -> list[dict]:
        records = self._read_records_from_parent(self.root / "archive")
        records.sort(key=lambda row: (row["closed_at"], row["thread_id"]), reverse=True)
        return records[:limit]

    def read_startup_index(self) -> dict | None:
        return self._read_index_record()

    def write_startup_index(
        self,
        *,
        active_threads: list[dict[str, object]],
        recent_completed_threads: list[dict[str, object]],
    ) -> dict:
        updated_at = datetime.now(UTC).isoformat()
        checkpoint_id = uuid.uuid4().hex
        metadata = {
            "active_threads": active_threads,
            "recent_completed_threads": recent_completed_threads,
            "updated_at": updated_at,
        }
        self._write_artifact_pair(
            artifact_dir=self._startup_index_dir(),
            markdown=_render_startup_markdown(
                active_threads=active_threads,
                recent_completed_threads=recent_completed_threads,
            ),
            metadata=metadata,
            checkpoint_id=checkpoint_id,
        )
        return {"checkpoint_id": checkpoint_id, "updated_at": updated_at}

    def startup_projection_matches(
        self,
        *,
        active_threads: list[dict[str, object]],
        recent_completed_threads: list[dict[str, object]],
    ) -> bool:
        existing = self.read_startup_index()
        if existing is None:
            return False
        return (
            existing.get("active_threads", []) == active_threads
            and existing.get("recent_completed_threads", []) == recent_completed_threads
        )

    def active_thread_artifact_ref(self, thread_id: str) -> str:
        return str(self._active_thread_dir(thread_id) / "current" / "artifact.md")

    def archived_thread_artifact_ref(self, thread_id: str) -> str:
        return str(self._archive_thread_dir(thread_id) / "current" / "artifact.md")

    def _migrate_legacy_sqlite_threads_if_needed(self) -> None:
        if self.legacy_db_path is None or not self.legacy_db_path.exists():
            return
        if any((self.root / name).exists() for name in ("active", "archive", "recent-session")):
            return

        with sqlite3.connect(self.legacy_db_path) as conn:
            conn.row_factory = sqlite3.Row
            table = conn.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'threads'"
            ).fetchone()
            if table is None:
                return
            rows = conn.execute("SELECT * FROM threads ORDER BY updated_at DESC").fetchall()

        if not rows:
            return

        for row in rows:
            payload = dict(row)
            thread_id = str(payload["thread_id"])
            title = str(payload.get("title") or thread_id)
            work_items = self._legacy_work_items(payload)
            thread_markdown = self._legacy_markdown(payload, work_items=work_items)
            status = payload.get("status") or "active"
            if status == "archived":
                self._write_artifact_pair(
                    artifact_dir=self._archive_thread_dir(thread_id),
                    markdown=thread_markdown,
                    metadata={
                        "thread_id": thread_id,
                        "title": title,
                        "closure_summary": str(payload.get("closure_summary") or ""),
                        "closed_at": str(payload.get("closed_at") or payload.get("updated_at") or datetime.now(UTC).isoformat()),
                    },
                    checkpoint_id=uuid.uuid4().hex,
                )
            else:
                self._write_artifact_pair(
                    artifact_dir=self._active_thread_dir(thread_id),
                    markdown=thread_markdown,
                    metadata={
                        "thread_id": thread_id,
                        "title": title,
                        "work_items": work_items,
                        "updated_at": str(payload.get("updated_at") or datetime.now(UTC).isoformat()),
                    },
                    checkpoint_id=uuid.uuid4().hex,
                )

        active_threads = [
            {
                "thread_id": row["thread_id"],
                "title": row["title"],
                "work_items": row["work_items"],
                "last_updated_at": row["updated_at"],
                "thread_artifact_ref": self.active_thread_artifact_ref(str(row["thread_id"])),
            }
            for row in self.list_active_threads()
        ]
        recent_completed_threads = [
            {
                "thread_id": row["thread_id"],
                "title": row["title"],
                "closure_summary": row["closure_summary"],
                "closed_at": row["closed_at"],
                "history_ref": self.archived_thread_artifact_ref(str(row["thread_id"])),
            }
            for row in self.list_recent_archived(limit=5)
        ]
        self.write_startup_index(
            active_threads=active_threads,
            recent_completed_threads=recent_completed_threads,
        )

    def _legacy_work_items(self, payload: dict[str, object]) -> list[str]:
        raw_work_items = payload.get("work_items")
        if isinstance(raw_work_items, str) and raw_work_items:
            try:
                parsed = json.loads(raw_work_items)
            except json.JSONDecodeError:
                parsed = []
            if isinstance(parsed, list):
                items = [item for item in parsed if isinstance(item, str) and item]
                if items:
                    return items
        next_action = payload.get("next_suggested_action")
        if isinstance(next_action, str) and next_action:
            return [next_action]
        return []

    def _legacy_markdown(self, payload: dict[str, object], *, work_items: list[str]) -> str:
        existing_markdown = payload.get("thread_markdown")
        if isinstance(existing_markdown, str) and existing_markdown:
            return existing_markdown

        lines = [f"# {payload.get('title') or payload.get('thread_id')}", ""]
        current_intent = payload.get("current_intent_summary")
        if isinstance(current_intent, str) and current_intent:
            lines.extend(["## Current State", "", current_intent, ""])
        if work_items:
            lines.extend(["## Work Items", ""])
            lines.extend([f"- {item}" for item in work_items])
            lines.append("")
        return "\n".join(lines).strip() + "\n"

    def _read_records_from_parent(self, parent: Path) -> list[dict]:
        if not parent.exists():
            return []
        records: list[dict] = []
        for artifact_dir in parent.iterdir():
            if not artifact_dir.is_dir():
                continue
            record = self._read_thread_record(artifact_dir)
            if record is not None:
                records.append(record)
        return records

    def _read_thread_record(self, artifact_dir: Path) -> dict | None:
        metadata = self._read_metadata(artifact_dir / "current" / "artifact.meta.yaml")
        if metadata is None:
            return None
        markdown_path = artifact_dir / "current" / "artifact.md"
        thread_markdown = markdown_path.read_text() if markdown_path.exists() else ""
        record = dict(metadata)
        record["thread_markdown"] = thread_markdown
        record["status"] = "active" if "updated_at" in record else "archived"
        return record

    def _read_index_record(self) -> dict | None:
        metadata = self._read_metadata(self._startup_index_dir() / "current" / "artifact.meta.yaml")
        if metadata is None:
            return None
        markdown_path = self._startup_index_dir() / "current" / "artifact.md"
        markdown = markdown_path.read_text() if markdown_path.exists() else ""
        return {**metadata, "markdown": markdown}

    def _write_artifact_pair(
        self,
        *,
        artifact_dir: Path,
        markdown: str,
        metadata: dict[str, object],
        checkpoint_id: str,
    ) -> None:
        current_dir = artifact_dir / "current"
        checkpoints_dir = artifact_dir / "checkpoints" / checkpoint_id
        current_dir.mkdir(parents=True, exist_ok=True)
        checkpoints_dir.mkdir(parents=True, exist_ok=True)

        (current_dir / "artifact.md").write_text(markdown)
        (checkpoints_dir / "artifact.md").write_text(markdown)
        self._write_metadata(current_dir / "artifact.meta.yaml", metadata)
        self._write_metadata(checkpoints_dir / "artifact.meta.yaml", metadata)

    def _write_metadata(self, path: Path, metadata: dict[str, object]) -> None:
        path.write_text(yaml.safe_dump(metadata, sort_keys=False))

    def _read_metadata(self, path: Path) -> dict | None:
        if not path.exists():
            return None
        loaded = yaml.safe_load(path.read_text())
        return loaded if isinstance(loaded, dict) else None

    def _active_thread_dir(self, thread_id: str) -> Path:
        return self.root / "active" / thread_id

    def _archive_thread_dir(self, thread_id: str) -> Path:
        return self.root / "archive" / thread_id

    def _startup_index_dir(self) -> Path:
        return self.root / "recent-session"


def _render_startup_markdown(
    *,
    active_threads: list[dict[str, object]],
    recent_completed_threads: list[dict[str, object]],
) -> str:
    lines = ["# Recent Session State", ""]
    lines.extend(["## Active Threads", ""])
    if not active_threads:
        lines.append("- None.")
    else:
        for thread in active_threads:
            lines.append(f"- {thread['title']} (`{thread['thread_id']}`)")
    lines.extend(["", "## Recent Completed Threads", ""])
    if not recent_completed_threads:
        lines.append("- None.")
    else:
        for thread in recent_completed_threads:
            lines.append(f"- {thread['title']} (`{thread['thread_id']}`)")
    lines.append("")
    return "\n".join(lines)
