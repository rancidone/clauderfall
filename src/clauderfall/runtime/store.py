"""SQLite-backed artifact persistence for the v2 runtime."""

from __future__ import annotations

import json
import shutil
import sqlite3
import uuid
from datetime import UTC, datetime
from pathlib import Path

from clauderfall.runtime.types import ArtifactKey, ArtifactRecord, ArtifactStage


MARKDOWN_STAGES = {ArtifactStage.DISCOVERY, ArtifactStage.DESIGN}

_CREATE_ARTIFACTS = """
CREATE TABLE IF NOT EXISTS artifacts (
    stage TEXT NOT NULL,
    artifact_id TEXT NOT NULL,
    version_id TEXT NOT NULL,
    stage_metadata TEXT NOT NULL,
    flush_reason TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (stage, artifact_id)
);
"""

_CREATE_ARTIFACT_CHECKPOINTS = """
CREATE TABLE IF NOT EXISTS artifact_checkpoints (
    stage TEXT NOT NULL,
    artifact_id TEXT NOT NULL,
    version_id TEXT NOT NULL,
    stage_metadata TEXT NOT NULL,
    flush_reason TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (stage, artifact_id, version_id)
);
"""

_CREATE_THREADS = """
CREATE TABLE IF NOT EXISTS threads (
    thread_id TEXT PRIMARY KEY,
    status TEXT NOT NULL DEFAULT 'active',
    title TEXT NOT NULL DEFAULT '',
    current_intent_summary TEXT NOT NULL DEFAULT '',
    next_suggested_action TEXT NOT NULL DEFAULT '',
    thread_markdown TEXT NOT NULL DEFAULT '',
    closure_summary TEXT,
    updated_at TEXT NOT NULL,
    closed_at TEXT
);
"""


class ArtifactStore:
    """Persist and load current artifact records via SQLite plus flat markdown files."""

    def __init__(self, *, db_path: Path, docs_root: Path) -> None:
        self.db_path = db_path
        self.docs_root = docs_root
        db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.execute(_CREATE_ARTIFACTS)
            conn.execute(_CREATE_ARTIFACT_CHECKPOINTS)
            conn.execute(_CREATE_THREADS)

    def read(self, key: ArtifactKey) -> ArtifactRecord | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT version_id, stage_metadata, flush_reason, updated_at FROM artifacts WHERE stage = ? AND artifact_id = ?",
                (key.stage.value, key.artifact_id),
            ).fetchone()
        if row is None:
            return None
        return ArtifactRecord(
            key=key,
            version_id=row["version_id"],
            stage_metadata=json.loads(row["stage_metadata"]),
            flush_reason=row["flush_reason"],
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    def list_by_stage(self, stage: ArtifactStage) -> list[ArtifactRecord]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT artifact_id, version_id, stage_metadata, flush_reason, updated_at
                FROM artifacts
                WHERE stage = ?
                ORDER BY updated_at DESC
                """,
                (stage.value,),
            ).fetchall()

        return [
            ArtifactRecord(
                key=ArtifactKey(stage=stage, artifact_id=row["artifact_id"]),
                version_id=row["version_id"],
                stage_metadata=json.loads(row["stage_metadata"]),
                flush_reason=row["flush_reason"],
                updated_at=datetime.fromisoformat(row["updated_at"]),
            )
            for row in rows
        ]

    def read_checkpoint(self, *, key: ArtifactKey, checkpoint_id: str) -> ArtifactRecord | None:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT version_id, stage_metadata, flush_reason, updated_at
                FROM artifact_checkpoints
                WHERE stage = ? AND artifact_id = ? AND version_id = ?
                """,
                (key.stage.value, key.artifact_id, checkpoint_id),
            ).fetchone()
        if row is None:
            return None
        return ArtifactRecord(
            key=key,
            version_id=row["version_id"],
            stage_metadata=json.loads(row["stage_metadata"]),
            flush_reason=row["flush_reason"],
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    def write(
        self,
        *,
        key: ArtifactKey,
        markdown: str | None,
        stage_metadata: dict[str, object],
        flush_reason: str,
    ) -> ArtifactRecord:
        version_id = uuid.uuid4().hex
        updated_at = datetime.now(UTC)
        updated_at_str = updated_at.isoformat()

        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO artifacts (stage, artifact_id, version_id, stage_metadata, flush_reason, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT (stage, artifact_id) DO UPDATE SET
                    version_id = excluded.version_id,
                    stage_metadata = excluded.stage_metadata,
                    flush_reason = excluded.flush_reason,
                    updated_at = excluded.updated_at
                """,
                (
                    key.stage.value,
                    key.artifact_id,
                    version_id,
                    json.dumps(stage_metadata),
                    flush_reason,
                    updated_at_str,
                ),
            )
            conn.execute(
                """
                INSERT INTO artifact_checkpoints (stage, artifact_id, version_id, stage_metadata, flush_reason, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    key.stage.value,
                    key.artifact_id,
                    version_id,
                    json.dumps(stage_metadata),
                    flush_reason,
                    updated_at_str,
                ),
            )

        if markdown is not None and key.stage in MARKDOWN_STAGES:
            current_path = self.markdown_path(key)
            current_path.parent.mkdir(parents=True, exist_ok=True)
            current_path.write_text(markdown)

            checkpoint_path = self.checkpoint_markdown_path(key=key, checkpoint_id=version_id)
            checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
            checkpoint_path.write_text(markdown)

        return ArtifactRecord(
            key=key,
            version_id=version_id,
            stage_metadata=stage_metadata,
            flush_reason=flush_reason,
            updated_at=updated_at,
        )

    def delete(self, key: ArtifactKey) -> dict[str, object]:
        with self._connect() as conn:
            artifact_cursor = conn.execute(
                "DELETE FROM artifacts WHERE stage = ? AND artifact_id = ?",
                (key.stage.value, key.artifact_id),
            )
            checkpoint_cursor = conn.execute(
                "DELETE FROM artifact_checkpoints WHERE stage = ? AND artifact_id = ?",
                (key.stage.value, key.artifact_id),
            )

        current_markdown_deleted = False
        current_path = self.markdown_path(key)
        if current_path.exists():
            current_path.unlink()
            current_markdown_deleted = True

        checkpoint_markdown_deleted = False
        checkpoint_dir = self.docs_root / key.stage.value / ".checkpoints" / key.artifact_id
        if checkpoint_dir.exists():
            shutil.rmtree(checkpoint_dir)
            checkpoint_markdown_deleted = True

        return {
            "artifact_rows_deleted": artifact_cursor.rowcount,
            "checkpoint_rows_deleted": checkpoint_cursor.rowcount,
            "current_markdown_deleted": current_markdown_deleted,
            "checkpoint_markdown_deleted": checkpoint_markdown_deleted,
        }

    def markdown_path(self, key: ArtifactKey) -> Path:
        return self.docs_root / key.stage.value / f"{key.artifact_id}.md"

    def checkpoint_markdown_path(self, *, key: ArtifactKey, checkpoint_id: str) -> Path:
        return self.docs_root / key.stage.value / ".checkpoints" / key.artifact_id / f"{checkpoint_id}.md"

    def read_markdown(self, key: ArtifactKey, checkpoint_id: str | None = None) -> str | None:
        path = self.markdown_path(key) if checkpoint_id is None else self.checkpoint_markdown_path(key=key, checkpoint_id=checkpoint_id)
        if not path.exists():
            return None
        return path.read_text()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
