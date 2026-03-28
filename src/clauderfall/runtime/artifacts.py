"""Shared artifact-level runtime operations beneath stage-specific services."""

from __future__ import annotations

from dataclasses import replace

from clauderfall.runtime.checkpoints import CheckpointManager
from clauderfall.runtime.store import ArtifactStore
from clauderfall.runtime.types import (
    ArtifactKey,
    ArtifactPair,
    ArtifactRef,
    ArtifactRuntimeResult,
    ArtifactView,
    CheckpointEnvelope,
    FlushReason,
    OperationResult,
    OperationStatus,
)


class StageArtifactRuntime:
    """Execute shared artifact mechanics without deciding stage policy."""

    def __init__(self, *, store: ArtifactStore, checkpoints: CheckpointManager) -> None:
        self.store = store
        self.checkpoints = checkpoints

    def read_artifact(
        self,
        *,
        key: ArtifactKey,
        checkpoint_id: str | None = None,
        view: ArtifactView = ArtifactView.FULL,
    ) -> ArtifactRuntimeResult:
        ref = ArtifactRef(key=key, checkpoint_id=checkpoint_id)
        pair = self.store.load_checkpoint(ref) if checkpoint_id else self.store.load_current(ref)
        if pair is None:
            return ArtifactRuntimeResult(
                result=OperationResult(
                    status=OperationStatus.ERROR,
                    message=f"artifact not found: {key.stage.value}/{key.artifact_id}",
                ),
                metadata={"artifact_id": key.artifact_id, "stage": key.stage.value, "checkpoint_id": checkpoint_id},
            )

        return ArtifactRuntimeResult(
            result=OperationResult(status=OperationStatus.OK, message="artifact read"),
            artifacts=self._render_artifact_payload(key=key, pair=pair, view=view),
            metadata=self._metadata_for_pair(key=key, pair=pair, view=view),
        )

    def write_artifact_checkpoint(
        self,
        *,
        key: ArtifactKey,
        markdown: str,
        stage_metadata: dict[str, object],
        flush_reason: FlushReason,
    ) -> ArtifactRuntimeResult:
        envelope = self.checkpoints.build_envelope(
            artifact_id=key.artifact_id,
            flush_reason=flush_reason,
            stage_metadata=stage_metadata,
        )
        pair = ArtifactPair(markdown=markdown, metadata=envelope)
        ref = ArtifactRef(key=key, checkpoint_id=envelope.checkpoint_id)
        self.store.write_checkpoint(ref, pair)
        return ArtifactRuntimeResult(
            result=OperationResult(status=OperationStatus.OK, message="artifact checkpoint written"),
            artifacts=self._render_artifact_payload(key=key, pair=pair, view=ArtifactView.FULL),
            metadata=self._metadata_for_pair(key=key, pair=pair, view=ArtifactView.FULL),
        )

    def transition_artifact_status(
        self,
        *,
        key: ArtifactKey,
        status: str,
        flush_reason: FlushReason,
        stage_metadata_updates: dict[str, object] | None = None,
    ) -> ArtifactRuntimeResult:
        current = self.store.load_current(ArtifactRef(key=key))
        if current is None:
            return ArtifactRuntimeResult(
                result=OperationResult(
                    status=OperationStatus.ERROR,
                    message=f"artifact not found for transition: {key.stage.value}/{key.artifact_id}",
                ),
                metadata={"artifact_id": key.artifact_id, "stage": key.stage.value},
            )

        next_stage_metadata = dict(current.metadata.stage_metadata)
        next_stage_metadata["status"] = status
        if stage_metadata_updates:
            next_stage_metadata.update(stage_metadata_updates)

        next_envelope = self.checkpoints.build_envelope(
            artifact_id=key.artifact_id,
            flush_reason=flush_reason,
            stage_metadata=next_stage_metadata,
        )
        next_pair = ArtifactPair(markdown=current.markdown, metadata=next_envelope)
        ref = ArtifactRef(key=key, checkpoint_id=next_envelope.checkpoint_id)
        self.store.write_checkpoint(ref, next_pair)

        previous_ref = ArtifactRef(key=key, checkpoint_id=current.metadata.checkpoint_id)
        return ArtifactRuntimeResult(
            result=OperationResult(status=OperationStatus.OK, message="artifact status transitioned"),
            artifacts={
                **self._render_artifact_payload(key=key, pair=next_pair, view=ArtifactView.FULL),
                "previous_checkpoint_ref": previous_ref,
            },
            metadata={
                **self._metadata_for_pair(key=key, pair=next_pair, view=ArtifactView.FULL),
                "previous_checkpoint_id": current.metadata.checkpoint_id,
            },
        )

    def _render_artifact_payload(
        self,
        *,
        key: ArtifactKey,
        pair: ArtifactPair,
        view: ArtifactView,
    ) -> dict[str, object]:
        payload: dict[str, object] = {
            "artifact_ref": ArtifactRef(key=key, checkpoint_id=pair.metadata.checkpoint_id),
            "artifact_id": key.artifact_id,
            "stage": key.stage.value,
            "checkpoint_id": pair.metadata.checkpoint_id,
            "status": pair.metadata.stage_metadata.get("status"),
            "title": pair.metadata.stage_metadata.get("title"),
            "readiness": pair.metadata.stage_metadata.get("readiness"),
        }
        if view is ArtifactView.FULL:
            payload["markdown"] = pair.markdown
            payload["stage_metadata"] = pair.metadata.stage_metadata
        return payload

    def _metadata_for_pair(
        self,
        *,
        key: ArtifactKey,
        pair: ArtifactPair,
        view: ArtifactView,
    ) -> dict[str, object]:
        return {
            "artifact_id": key.artifact_id,
            "stage": key.stage.value,
            "checkpoint_id": pair.metadata.checkpoint_id,
            "flush_reason": pair.metadata.flush_reason,
            "is_current": pair.metadata.is_current,
            "created_at": pair.metadata.created_at,
            "view": view,
        }
