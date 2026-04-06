"""Filesystem-backed session store for one current carry-forward record."""

from __future__ import annotations

import json
import shutil
import sqlite3
import uuid
from datetime import UTC, datetime
from pathlib import Path

import yaml


class SessionStore:
    """Read and write session lifecycle artifacts from the repo filesystem."""

    def __init__(self, *, docs_root: Path, legacy_db_path: Path | None = None) -> None:
        self.docs_root = docs_root
        self.root = docs_root / "session"
        self.legacy_db_path = legacy_db_path
        self.root.mkdir(parents=True, exist_ok=True)
        self._migrate_legacy_sqlite_threads_if_needed()

    def read_current(self) -> dict | None:
        return self._read_record(self._current_dir())

    def write_current(
        self,
        *,
        title: str,
        work_items: list[str],
        thread_markdown: str,
    ) -> dict:
        updated_at = datetime.now(UTC).isoformat()
        checkpoint_id = uuid.uuid4().hex
        metadata = {
            "title": title,
            "work_items": work_items,
            "updated_at": updated_at,
            "checkpoint_id": checkpoint_id,
        }
        self._write_artifact_pair(
            artifact_dir=self._current_dir(),
            markdown=thread_markdown,
            metadata=metadata,
            checkpoint_id=checkpoint_id,
        )
        return {
            **metadata,
            "thread_markdown": thread_markdown,
            "status": "current",
        }

    def archive_current(self, *, closure_summary: str) -> dict | None:
        current_dir = self._current_dir()
        current_record = self._read_record(current_dir)
        if current_record is None:
            return None

        history_id = uuid.uuid4().hex
        history_dir = self._history_dir(history_id)
        history_dir.parent.mkdir(parents=True, exist_ok=True)
        if history_dir.exists():
            shutil.rmtree(history_dir)
        shutil.copytree(current_dir, history_dir)

        closed_at = datetime.now(UTC).isoformat()
        checkpoint_id = uuid.uuid4().hex
        archive_metadata = {
            "history_id": history_id,
            "title": current_record["title"],
            "closure_summary": closure_summary,
            "closed_at": closed_at,
            "checkpoint_id": checkpoint_id,
        }
        self._write_artifact_pair(
            artifact_dir=history_dir,
            markdown=current_record["thread_markdown"],
            metadata=archive_metadata,
            checkpoint_id=checkpoint_id,
        )
        shutil.rmtree(current_dir)
        return {
            **archive_metadata,
            "thread_markdown": current_record["thread_markdown"],
            "status": "archived",
        }

    def list_recent_archived(self, *, limit: int = 5) -> list[dict]:
        records = self._read_records_from_parent(self.root / "history")
        records.sort(key=lambda row: (row["closed_at"], row["history_id"]), reverse=True)
        return records[:limit]

    def read_startup_index(self) -> dict | None:
        return self._read_index_record()

    def write_startup_index(
        self,
        *,
        current: dict[str, object] | None,
        recent_completed: list[dict[str, object]],
    ) -> dict:
        updated_at = datetime.now(UTC).isoformat()
        checkpoint_id = uuid.uuid4().hex
        metadata = {
            "has_current": current is not None,
            "current": current,
            "recent_completed": recent_completed,
            "updated_at": updated_at,
            "checkpoint_id": checkpoint_id,
        }
        self._write_artifact_pair(
            artifact_dir=self._startup_index_dir(),
            markdown=_render_startup_markdown(
                current=current,
                recent_completed=recent_completed,
            ),
            metadata=metadata,
            checkpoint_id=checkpoint_id,
        )
        return {"checkpoint_id": checkpoint_id, "updated_at": updated_at}

    def startup_projection_matches(
        self,
        *,
        current: dict[str, object] | None,
        recent_completed: list[dict[str, object]],
    ) -> bool:
        existing = self.read_startup_index()
        if existing is None:
            return False
        return (
            existing.get("has_current") == (current is not None)
            and existing.get("current") == current
            and existing.get("recent_completed", []) == recent_completed
        )

    def current_artifact_ref(self) -> str:
        return str(self._current_dir() / "current" / "artifact.md")

    def archived_artifact_ref(self, history_id: str) -> str:
        return str(self._history_dir(history_id) / "current" / "artifact.md")

    def _migrate_legacy_sqlite_threads_if_needed(self) -> None:
        if self.legacy_db_path is None or not self.legacy_db_path.exists():
            return
        if any((self.root / name).exists() for name in ("current", "history", "recent-session")):
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

        current_payload: dict[str, object] | None = None
        for row in rows:
            payload = dict(row)
            title = str(payload.get("title") or payload.get("thread_id") or "Current Session State")
            work_items = self._legacy_work_items(payload)
            thread_markdown = self._legacy_markdown(payload, work_items=work_items)
            status = payload.get("status") or "active"
            if status != "archived" and current_payload is None:
                current_payload = {
                    "title": title,
                    "work_items": work_items,
                    "thread_markdown": thread_markdown,
                    "updated_at": str(payload.get("updated_at") or datetime.now(UTC).isoformat()),
                }
                continue

            history_id = uuid.uuid4().hex
            self._write_artifact_pair(
                artifact_dir=self._history_dir(history_id),
                markdown=thread_markdown,
                metadata={
                    "history_id": history_id,
                    "title": title,
                    "closure_summary": str(payload.get("closure_summary") or ""),
                    "closed_at": str(payload.get("closed_at") or payload.get("updated_at") or datetime.now(UTC).isoformat()),
                    "checkpoint_id": uuid.uuid4().hex,
                },
                checkpoint_id=uuid.uuid4().hex,
            )

        if current_payload is not None:
            checkpoint_id = uuid.uuid4().hex
            self._write_artifact_pair(
                artifact_dir=self._current_dir(),
                markdown=str(current_payload["thread_markdown"]),
                metadata={
                    "title": str(current_payload["title"]),
                    "work_items": list(current_payload["work_items"]),
                    "updated_at": str(current_payload["updated_at"]),
                    "checkpoint_id": checkpoint_id,
                },
                checkpoint_id=checkpoint_id,
            )

        self.write_startup_index(
            current=self.current_startup_entry(),
            recent_completed=self.archived_startup_entries(limit=5),
        )

    def current_startup_entry(self) -> dict[str, object] | None:
        row = self.read_current()
        if row is None:
            return None
        return {
            "title": row["title"],
            "work_items": row["work_items"],
            "last_updated_at": row["updated_at"],
            "current_artifact_ref": self.current_artifact_ref(),
        }

    def archived_startup_entries(self, *, limit: int = 5) -> list[dict[str, object]]:
        return [
            {
                "history_id": row["history_id"],
                "title": row["title"],
                "closure_summary": row["closure_summary"] or "",
                "closed_at": row["closed_at"],
                "history_ref": self.archived_artifact_ref(str(row["history_id"])),
            }
            for row in self.list_recent_archived(limit=limit)
        ]

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

        lines = [f"# {payload.get('title') or payload.get('thread_id') or 'Current Session State'}", ""]
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
            record = self._read_record(artifact_dir)
            if record is not None:
                records.append(record)
        return records

    def _read_record(self, artifact_dir: Path) -> dict | None:
        metadata = self._read_metadata(artifact_dir / "current" / "artifact.meta.yaml")
        if metadata is None:
            return None
        markdown_path = artifact_dir / "current" / "artifact.md"
        thread_markdown = markdown_path.read_text() if markdown_path.exists() else ""
        record = dict(metadata)
        record["thread_markdown"] = thread_markdown
        if "updated_at" in record:
            record["status"] = "current"
        elif "closed_at" in record:
            record["status"] = "archived"
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

    def _current_dir(self) -> Path:
        return self.root / "current"

    def _history_dir(self, history_id: str) -> Path:
        return self.root / "history" / history_id

    def _startup_index_dir(self) -> Path:
        return self.root / "recent-session"


def _render_startup_markdown(
    *,
    current: dict[str, object] | None,
    recent_completed: list[dict[str, object]],
) -> str:
    lines = ["# Recent Session State", "", "## Current Carry Forward", ""]
    if current is None:
        lines.append("- None.")
    else:
        lines.append(f"- {current['title']}")
    lines.extend(["", "## Recent Completed", ""])
    if not recent_completed:
        lines.append("- None.")
    else:
        for item in recent_completed:
            lines.append(f"- {item['title']} (`{item['history_id']}`)")
    lines.append("")
    return "\n".join(lines)
