"""Filesystem-backed artifact persistence for the v2 runtime."""

from __future__ import annotations

import json
import shutil
import sqlite3
import uuid
from datetime import UTC, datetime
from pathlib import Path

import yaml

from clauderfall.runtime.types import ArtifactKey, ArtifactRecord, ArtifactStage


MARKDOWN_STAGES = {ArtifactStage.DISCOVERY, ArtifactStage.DESIGN}

class ArtifactStore:
    """Persist and load current artifact records via filesystem artifact pairs."""

    def __init__(self, *, db_path: Path, docs_root: Path) -> None:
        self.db_path = db_path
        self.docs_root = docs_root
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.docs_root.mkdir(parents=True, exist_ok=True)
        self._migrate_legacy_sqlite_artifacts_if_needed()

    def read(self, key: ArtifactKey) -> ArtifactRecord | None:
        metadata = self._read_metadata(self.current_metadata_path(key))
        if metadata is None:
            return None
        return self._record_from_metadata(key=key, metadata=metadata)

    def list_by_stage(self, stage: ArtifactStage) -> list[ArtifactRecord]:
        stage_dir = self.docs_root / stage.value
        if not stage_dir.exists():
            return []

        records: list[ArtifactRecord] = []
        for artifact_dir in stage_dir.iterdir():
            if not artifact_dir.is_dir():
                continue
            current_metadata = self._read_metadata(artifact_dir / "current" / "artifact.meta.yaml")
            if current_metadata is None:
                continue
            records.append(
                self._record_from_metadata(
                    key=ArtifactKey(stage=stage, artifact_id=artifact_dir.name),
                    metadata=current_metadata,
                )
            )
        return sorted(records, key=lambda record: record.updated_at, reverse=True)

    def read_checkpoint(self, *, key: ArtifactKey, checkpoint_id: str) -> ArtifactRecord | None:
        metadata = self._read_metadata(self.checkpoint_metadata_path(key=key, checkpoint_id=checkpoint_id))
        if metadata is None:
            return None
        return self._record_from_metadata(key=key, metadata=metadata)

    def write(
        self,
        *,
        key: ArtifactKey,
        markdown: str | None,
        stage_metadata: dict[str, object],
        flush_reason: str,
    ) -> ArtifactRecord:
        current = self.read(key)
        if current is not None:
            self._set_checkpoint_is_current(
                key=key,
                checkpoint_id=current.version_id,
                is_current=False,
            )

        version_id = uuid.uuid4().hex
        created_at = datetime.now(UTC)
        markdown_to_write = markdown
        if markdown_to_write is None and key.stage in MARKDOWN_STAGES:
            markdown_to_write = self.read_markdown(key) or ""

        checkpoint_metadata = self._checkpoint_metadata(
            artifact_id=key.artifact_id,
            checkpoint_id=version_id,
            created_at=created_at,
            flush_reason=flush_reason,
            is_current=True,
            stage_metadata=stage_metadata,
        )
        self._write_artifact_pair(
            key=key,
            checkpoint_id=version_id,
            markdown=markdown_to_write,
            metadata=checkpoint_metadata,
        )

        return ArtifactRecord(
            key=key,
            version_id=version_id,
            stage_metadata=stage_metadata,
            flush_reason=flush_reason,
            updated_at=created_at,
        )

    def delete(self, key: ArtifactKey) -> dict[str, object]:
        artifact_dir = self.artifact_dir(key)
        current_markdown_deleted = self.markdown_path(key).exists()
        checkpoint_dir = artifact_dir / "checkpoints"
        checkpoint_markdown_deleted = checkpoint_dir.exists()
        checkpoint_count_deleted = len(list(checkpoint_dir.iterdir())) if checkpoint_dir.exists() else 0
        artifact_deleted = artifact_dir.exists()

        if artifact_dir.exists():
            shutil.rmtree(artifact_dir)

        return {
            "artifact_deleted": artifact_deleted,
            "checkpoint_count_deleted": checkpoint_count_deleted,
            "current_markdown_deleted": current_markdown_deleted,
            "checkpoint_markdown_deleted": checkpoint_markdown_deleted,
            # Keep DB-shaped aliases temporarily for compatibility with existing callers/tests.
            "artifact_rows_deleted": 1 if artifact_deleted else 0,
            "checkpoint_rows_deleted": checkpoint_count_deleted,
        }

    def artifact_dir(self, key: ArtifactKey) -> Path:
        return self.docs_root / key.stage.value / key.artifact_id

    def markdown_path(self, key: ArtifactKey) -> Path:
        return self.artifact_dir(key) / "current" / "artifact.md"

    def current_metadata_path(self, key: ArtifactKey) -> Path:
        return self.artifact_dir(key) / "current" / "artifact.meta.yaml"

    def checkpoint_markdown_path(self, *, key: ArtifactKey, checkpoint_id: str) -> Path:
        return self.artifact_dir(key) / "checkpoints" / checkpoint_id / "artifact.md"

    def checkpoint_metadata_path(self, *, key: ArtifactKey, checkpoint_id: str) -> Path:
        return self.artifact_dir(key) / "checkpoints" / checkpoint_id / "artifact.meta.yaml"

    def read_markdown(self, key: ArtifactKey, checkpoint_id: str | None = None) -> str | None:
        path = self.markdown_path(key) if checkpoint_id is None else self.checkpoint_markdown_path(key=key, checkpoint_id=checkpoint_id)
        if not path.exists():
            return None
        return path.read_text()

    def _write_artifact_pair(
        self,
        *,
        key: ArtifactKey,
        checkpoint_id: str,
        markdown: str | None,
        metadata: dict[str, object],
    ) -> None:
        current_dir = self.artifact_dir(key) / "current"
        checkpoint_dir = self.artifact_dir(key) / "checkpoints" / checkpoint_id
        current_dir.mkdir(parents=True, exist_ok=True)
        checkpoint_dir.mkdir(parents=True, exist_ok=True)

        self._write_metadata(self.current_metadata_path(key), metadata)
        self._write_metadata(self.checkpoint_metadata_path(key=key, checkpoint_id=checkpoint_id), metadata)
        if markdown is not None and key.stage in MARKDOWN_STAGES:
            self.markdown_path(key).write_text(markdown)
            self.checkpoint_markdown_path(key=key, checkpoint_id=checkpoint_id).write_text(markdown)

    def _checkpoint_metadata(
        self,
        *,
        artifact_id: str,
        checkpoint_id: str,
        created_at: datetime,
        flush_reason: str,
        is_current: bool,
        stage_metadata: dict[str, object],
    ) -> dict[str, object]:
        return {
            "artifact_id": artifact_id,
            "checkpoint_id": checkpoint_id,
            "created_at": created_at.isoformat(),
            "flush_reason": flush_reason,
            "is_current": is_current,
            "stage_metadata": stage_metadata,
        }

    def _record_from_metadata(self, *, key: ArtifactKey, metadata: dict[str, object]) -> ArtifactRecord:
        return ArtifactRecord(
            key=key,
            version_id=str(metadata["checkpoint_id"]),
            stage_metadata=dict(metadata.get("stage_metadata", {})),
            flush_reason=str(metadata["flush_reason"]),
            updated_at=datetime.fromisoformat(str(metadata["created_at"])),
        )

    def _set_checkpoint_is_current(self, *, key: ArtifactKey, checkpoint_id: str, is_current: bool) -> None:
        metadata_path = self.checkpoint_metadata_path(key=key, checkpoint_id=checkpoint_id)
        metadata = self._read_metadata(metadata_path)
        if metadata is None:
            return
        metadata["is_current"] = is_current
        self._write_metadata(metadata_path, metadata)

    def _write_metadata(self, path: Path, metadata: dict[str, object]) -> None:
        path.write_text(yaml.safe_dump(metadata, sort_keys=False))

    def _read_metadata(self, path: Path) -> dict | None:
        if not path.exists():
            return None
        loaded = yaml.safe_load(path.read_text())
        return loaded if isinstance(loaded, dict) else None

    def _migrate_legacy_sqlite_artifacts_if_needed(self) -> None:
        if not self.db_path.exists():
            return
        if self._has_filesystem_artifact_authority():
            return

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            tables = {
                row["name"] for row in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                ).fetchall()
            }
            if "artifacts" not in tables or "artifact_checkpoints" not in tables:
                return
            current_rows = conn.execute(
                "SELECT stage, artifact_id, version_id, stage_metadata, flush_reason, updated_at FROM artifacts"
            ).fetchall()
            checkpoint_rows = conn.execute(
                "SELECT stage, artifact_id, version_id, stage_metadata, flush_reason, updated_at FROM artifact_checkpoints"
            ).fetchall()

        current_by_key = {
            (str(row["stage"]), str(row["artifact_id"])): dict(row)
            for row in current_rows
        }
        checkpoint_groups: dict[tuple[str, str], list[dict[str, object]]] = {}
        for row in checkpoint_rows:
            payload = dict(row)
            checkpoint_groups.setdefault((str(payload["stage"]), str(payload["artifact_id"])), []).append(payload)

        artifact_keys = set(current_by_key) | set(checkpoint_groups)
        for stage_value, artifact_id in artifact_keys:
            stage = ArtifactStage(stage_value)
            key = ArtifactKey(stage=stage, artifact_id=artifact_id)
            current_row = current_by_key.get((stage_value, artifact_id))
            current_version = str(current_row["version_id"]) if current_row is not None else None
            checkpoints = checkpoint_groups.get((stage_value, artifact_id), [])
            if not checkpoints and current_row is not None:
                checkpoints = [current_row]
            for checkpoint in checkpoints:
                checkpoint_id = str(checkpoint["version_id"])
                stage_metadata = json.loads(str(checkpoint["stage_metadata"]))
                created_at = datetime.fromisoformat(str(checkpoint["updated_at"]))
                metadata = self._checkpoint_metadata(
                    artifact_id=artifact_id,
                    checkpoint_id=checkpoint_id,
                    created_at=created_at,
                    flush_reason=str(checkpoint["flush_reason"]),
                    is_current=checkpoint_id == current_version,
                    stage_metadata=stage_metadata,
                )
                markdown = self._read_legacy_markdown(
                    key=key,
                    checkpoint_id=checkpoint_id,
                    is_current=checkpoint_id == current_version,
                )
                checkpoint_dir = self.artifact_dir(key) / "checkpoints" / checkpoint_id
                checkpoint_dir.mkdir(parents=True, exist_ok=True)
                self._write_metadata(self.checkpoint_metadata_path(key=key, checkpoint_id=checkpoint_id), metadata)
                if markdown is not None and key.stage in MARKDOWN_STAGES:
                    self.checkpoint_markdown_path(key=key, checkpoint_id=checkpoint_id).write_text(markdown)

            if current_row is not None:
                current_metadata = self._checkpoint_metadata(
                    artifact_id=artifact_id,
                    checkpoint_id=str(current_row["version_id"]),
                    created_at=datetime.fromisoformat(str(current_row["updated_at"])),
                    flush_reason=str(current_row["flush_reason"]),
                    is_current=True,
                    stage_metadata=json.loads(str(current_row["stage_metadata"])),
                )
                current_dir = self.artifact_dir(key) / "current"
                current_dir.mkdir(parents=True, exist_ok=True)
                self._write_metadata(self.current_metadata_path(key), current_metadata)
                current_markdown = self._read_legacy_markdown(
                    key=key,
                    checkpoint_id=str(current_row["version_id"]),
                    is_current=True,
                )
                if current_markdown is not None and key.stage in MARKDOWN_STAGES:
                    self.markdown_path(key).write_text(current_markdown)

    def _has_filesystem_artifact_authority(self) -> bool:
        for stage in MARKDOWN_STAGES:
            stage_dir = self.docs_root / stage.value
            if not stage_dir.exists():
                continue
            for artifact_dir in stage_dir.iterdir():
                if not artifact_dir.is_dir():
                    continue
                if (artifact_dir / "current" / "artifact.meta.yaml").exists():
                    return True
        return False

    def _read_legacy_markdown(self, *, key: ArtifactKey, checkpoint_id: str, is_current: bool) -> str | None:
        if key.stage not in MARKDOWN_STAGES:
            return None
        if is_current:
            current_path = self.docs_root / key.stage.value / f"{key.artifact_id}.md"
            if current_path.exists():
                return current_path.read_text()
        checkpoint_path = self.docs_root / key.stage.value / ".checkpoints" / key.artifact_id / f"{checkpoint_id}.md"
        if checkpoint_path.exists():
            return checkpoint_path.read_text()
        return None
