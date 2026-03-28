"""Filesystem path resolution for v2 runtime artifacts."""

from __future__ import annotations

from pathlib import Path

from clauderfall.runtime.types import ArtifactKey, ArtifactRef, ResolvedArtifactPaths


class ArtifactResolver:
    """Translate logical artifact references into stable filesystem paths."""

    def __init__(self, root: Path) -> None:
        self.root = root

    def resolve(self, ref: ArtifactRef) -> ResolvedArtifactPaths:
        artifact_root = self.root / ref.key.stage.value / ref.key.artifact_id
        current_dir = artifact_root / "current"
        checkpoints_dir = artifact_root / "checkpoints"
        checkpoint_dir = checkpoints_dir / ref.checkpoint_id if ref.checkpoint_id else None
        return ResolvedArtifactPaths(
            key=ref.key,
            artifact_root=artifact_root,
            current_dir=current_dir,
            current_markdown_path=current_dir / "artifact.md",
            current_metadata_path=current_dir / "artifact.meta.yaml",
            checkpoints_dir=checkpoints_dir,
            checkpoint_id=ref.checkpoint_id,
            checkpoint_dir=checkpoint_dir,
            checkpoint_markdown_path=checkpoint_dir / "artifact.md" if checkpoint_dir else None,
            checkpoint_metadata_path=checkpoint_dir / "artifact.meta.yaml" if checkpoint_dir else None,
        )

