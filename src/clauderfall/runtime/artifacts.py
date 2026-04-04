"""Shared artifact-level runtime operations beneath stage-specific services."""

from __future__ import annotations

from clauderfall.runtime.store import ArtifactStore
from clauderfall.runtime.types import (
    ArtifactKey,
    ArtifactRecord,
    ArtifactRuntimeResult,
    ArtifactStage,
    FlushReason,
    OperationResult,
    OperationStatus,
)


class StageArtifactRuntime:
    """Execute shared artifact mechanics without deciding stage policy."""

    def __init__(self, *, store: ArtifactStore) -> None:
        self.store = store

    def read_artifact(
        self,
        *,
        key: ArtifactKey,
        checkpoint_id: str | None = None,
    ) -> ArtifactRuntimeResult:
        record = self.store.read(key) if checkpoint_id is None else self.store.read_checkpoint(key=key, checkpoint_id=checkpoint_id)
        if record is None:
            message = f"artifact not found: {key.stage.value}/{key.artifact_id}"
            if checkpoint_id is not None:
                message = f"checkpoint not found: {key.stage.value}/{key.artifact_id}@{checkpoint_id}"
            return ArtifactRuntimeResult(
                result=OperationResult(
                    status=OperationStatus.ERROR,
                    message=message,
                ),
                metadata={
                    "artifact_id": key.artifact_id,
                    "stage": key.stage.value,
                    **({"checkpoint_id": checkpoint_id} if checkpoint_id is not None else {}),
                },
            )

        return ArtifactRuntimeResult(
            result=OperationResult(status=OperationStatus.OK, message="artifact read"),
            artifacts=_render_payload(key=key, record=record, include_stage_metadata=True),
            metadata=_render_metadata(key=key, record=record),
        )

    def read_artifact_markdown(self, *, key: ArtifactKey, checkpoint_id: str | None = None) -> str | None:
        """Return the raw markdown body for a key, or None if not found. For internal runtime use only."""
        return self.store.read_markdown(key, checkpoint_id=checkpoint_id)

    def list_artifacts(self, *, stage: ArtifactStage) -> list[ArtifactRecord]:
        return self.store.list_by_stage(stage)

    def write_artifact_checkpoint(
        self,
        *,
        key: ArtifactKey,
        markdown: str,
        stage_metadata: dict[str, object],
        flush_reason: FlushReason,
    ) -> ArtifactRuntimeResult:
        record = self.store.write(
            key=key,
            markdown=markdown,
            stage_metadata=stage_metadata,
            flush_reason=flush_reason.value,
        )
        return ArtifactRuntimeResult(
            result=OperationResult(status=OperationStatus.OK, message="artifact checkpoint written"),
            artifacts=_render_payload(key=key, record=record),
            metadata=_render_metadata(key=key, record=record),
        )

    def transition_artifact_status(
        self,
        *,
        key: ArtifactKey,
        status: str,
        flush_reason: FlushReason,
        stage_metadata_updates: dict[str, object] | None = None,
    ) -> ArtifactRuntimeResult:
        current = self.store.read(key)
        if current is None:
            return ArtifactRuntimeResult(
                result=OperationResult(
                    status=OperationStatus.ERROR,
                    message=f"artifact not found for transition: {key.stage.value}/{key.artifact_id}",
                ),
                metadata={"artifact_id": key.artifact_id, "stage": key.stage.value},
            )

        previous_version_id = current.version_id
        next_stage_metadata = dict(current.stage_metadata)
        next_stage_metadata["status"] = status
        if stage_metadata_updates:
            next_stage_metadata.update(stage_metadata_updates)

        record = self.store.write(
            key=key,
            markdown=None,
            stage_metadata=next_stage_metadata,
            flush_reason=flush_reason.value,
        )

        return ArtifactRuntimeResult(
            result=OperationResult(status=OperationStatus.OK, message="artifact status transitioned"),
            artifacts=_render_payload(key=key, record=record),
            metadata={
                **_render_metadata(key=key, record=record),
                "previous_version_id": previous_version_id,
                # Keep previous_checkpoint_id as alias for test compatibility
                "previous_checkpoint_id": previous_version_id,
            },
        )

    def delete_artifact(self, *, key: ArtifactKey) -> ArtifactRuntimeResult:
        deletion = self.store.delete(key)
        if not any(
            (
                deletion["artifact_deleted"],
                deletion["checkpoint_count_deleted"],
                deletion["current_markdown_deleted"],
                deletion["checkpoint_markdown_deleted"],
            )
        ):
            return ArtifactRuntimeResult(
                result=OperationResult(
                    status=OperationStatus.WARNING,
                    message="artifact already absent",
                ),
                warnings=("artifact_not_found",),
                metadata={"artifact_id": key.artifact_id, "stage": key.stage.value, "deleted": False},
            )

        return ArtifactRuntimeResult(
            result=OperationResult(status=OperationStatus.OK, message="artifact deleted"),
            metadata={
                "artifact_id": key.artifact_id,
                "stage": key.stage.value,
                "deleted": True,
                **deletion,
            },
        )


def _render_payload(*, key: ArtifactKey, record: ArtifactRecord, include_stage_metadata: bool = False) -> dict[str, object]:
    payload: dict[str, object] = {
        "artifact_id": key.artifact_id,
        "stage": key.stage.value,
        "version_id": record.version_id,
        "status": record.stage_metadata.get("status"),
        "title": record.stage_metadata.get("title"),
        "readiness": record.stage_metadata.get("readiness"),
    }
    if include_stage_metadata:
        payload["stage_metadata"] = record.stage_metadata
    return payload


def _render_metadata(*, key: ArtifactKey, record: ArtifactRecord) -> dict[str, object]:
    return {
        "artifact_id": key.artifact_id,
        "stage": key.stage.value,
        "version_id": record.version_id,
        # checkpoint_id alias for backward compat with tests and design.py
        "checkpoint_id": record.version_id,
        "flush_reason": record.flush_reason,
        "updated_at": record.updated_at,
    }
