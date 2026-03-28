"""Checkpoint identity and metadata helpers."""

from __future__ import annotations

from uuid import uuid4

from clauderfall.runtime.types import CheckpointEnvelope, FlushReason


class CheckpointManager:
    """Own checkpoint id creation and envelope construction."""

    def new_checkpoint_id(self) -> str:
        return uuid4().hex

    def build_envelope(
        self,
        *,
        artifact_id: str,
        flush_reason: FlushReason,
        checkpoint_id: str | None = None,
        stage_metadata: dict[str, object] | None = None,
        is_current: bool = True,
    ) -> CheckpointEnvelope:
        return CheckpointEnvelope.create(
            artifact_id=artifact_id,
            checkpoint_id=checkpoint_id or self.new_checkpoint_id(),
            flush_reason=flush_reason,
            stage_metadata=stage_metadata,
            is_current=is_current,
        )

