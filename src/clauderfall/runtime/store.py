"""Filesystem-backed artifact persistence for the v2 runtime."""

from __future__ import annotations

import yaml

from clauderfall.runtime.resolver import ArtifactResolver
from clauderfall.runtime.types import ArtifactPair, ArtifactRef, CheckpointEnvelope


class ArtifactStore:
    """Persist and load current or checkpointed artifact pairs."""

    def __init__(self, resolver: ArtifactResolver) -> None:
        self.resolver = resolver

    def write_checkpoint(self, ref: ArtifactRef, pair: ArtifactPair) -> ArtifactPair:
        if ref.checkpoint_id is None:
            raise ValueError("checkpoint writes require an ArtifactRef with checkpoint_id")
        if pair.metadata.checkpoint_id != ref.checkpoint_id:
            raise ValueError("pair metadata checkpoint_id must match the requested checkpoint ref")

        resolved = self.resolver.resolve(ref)
        assert resolved.checkpoint_dir is not None
        assert resolved.checkpoint_markdown_path is not None
        assert resolved.checkpoint_metadata_path is not None

        resolved.checkpoint_dir.mkdir(parents=True, exist_ok=False)
        resolved.current_dir.mkdir(parents=True, exist_ok=True)

        checkpoint_yaml = _dump_yaml(pair.metadata.model_dump(mode="json"))

        resolved.checkpoint_markdown_path.write_text(pair.markdown)
        resolved.checkpoint_metadata_path.write_text(checkpoint_yaml)
        resolved.current_markdown_path.write_text(pair.markdown)
        resolved.current_metadata_path.write_text(checkpoint_yaml)

        return pair

    def load_current(self, ref: ArtifactRef) -> ArtifactPair | None:
        resolved = self.resolver.resolve(ArtifactRef(key=ref.key))
        if not resolved.current_markdown_path.exists() or not resolved.current_metadata_path.exists():
            return None
        return ArtifactPair(
            markdown=resolved.current_markdown_path.read_text(),
            metadata=CheckpointEnvelope.model_validate(_load_yaml(resolved.current_metadata_path.read_text())),
        )

    def load_checkpoint(self, ref: ArtifactRef) -> ArtifactPair | None:
        if ref.checkpoint_id is None:
            raise ValueError("checkpoint loads require an ArtifactRef with checkpoint_id")

        resolved = self.resolver.resolve(ref)
        assert resolved.checkpoint_markdown_path is not None
        assert resolved.checkpoint_metadata_path is not None

        if not resolved.checkpoint_markdown_path.exists() or not resolved.checkpoint_metadata_path.exists():
            return None

        return ArtifactPair(
            markdown=resolved.checkpoint_markdown_path.read_text(),
            metadata=CheckpointEnvelope.model_validate(
                _load_yaml(resolved.checkpoint_metadata_path.read_text())
            ),
        )


def _dump_yaml(value: object, *, indent: int = 0) -> str:
    del indent
    return yaml.safe_dump(value, sort_keys=False)


def _dump_scalar(value: object) -> str:
    return yaml.safe_dump(value, sort_keys=False).strip()


def _load_yaml(text: str) -> object:
    return yaml.safe_load(text)
