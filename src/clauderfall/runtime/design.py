"""Design runtime service on top of the shared artifact runtime."""

from __future__ import annotations

from dataclasses import dataclass

from clauderfall.runtime.artifacts import StageArtifactRuntime
from clauderfall.runtime.types import (
    ArtifactKey,
    ArtifactRuntimeResult,
    ArtifactStage,
    FlushReason,
    OperationResult,
    OperationStatus,
)


DESIGN_REQUIRED_FIELDS = (
    "design_unit_id",
    "title",
    "status",
    "scope_summary",
    "readiness",
    "readiness_rationale",
    "open_questions",
    "assumptions",
)

DESIGN_RELATIONSHIP_FIELDS = ("depends_on", "children", "parent")
DESIGN_ALLOWED_STATUSES = {"draft", "in_review", "accepted"}
DESIGN_MUTABLE_STATUSES = {"draft", "in_review"}
DESIGN_READINESS_VALUES = {"low", "medium", "high"}


@dataclass(frozen=True)
class DesignRuntimeService:
    """Stage-specific Design operations built on the shared artifact runtime."""

    artifacts: StageArtifactRuntime

    def read(
        self,
        *,
        unit_id: str,
        checkpoint_id: str | None = None,
        view: str = "short",
    ) -> ArtifactRuntimeResult:
        key = ArtifactKey(stage=ArtifactStage.DESIGN, artifact_id=unit_id)
        result = self.artifacts.read_artifact(key=key, checkpoint_id=checkpoint_id)
        if not result.result.ok:
            return result

        stage_metadata = dict(result.artifacts["stage_metadata"])
        shaped_artifacts = _render_design_payload(
            unit_id=unit_id,
            base_artifacts=result.artifacts,
            stage_metadata=stage_metadata,
        )
        if view == "full":
            shaped_artifacts["open_questions"] = stage_metadata.get("open_questions", [])
            shaped_artifacts["assumptions"] = stage_metadata.get("assumptions", [])
            shaped_artifacts["markdown"] = self.artifacts.read_artifact_markdown(key=key) or ""
        return ArtifactRuntimeResult(
            result=result.result,
            warnings=result.warnings,
            artifacts=shaped_artifacts,
            metadata=result.metadata,
        )

    def write_draft(
        self,
        *,
        unit_id: str,
        markdown: str,
        sidecar: dict[str, object],
    ) -> ArtifactRuntimeResult:
        errors = _validate_design_sidecar(sidecar)
        if errors:
            return ArtifactRuntimeResult(
                result=OperationResult(
                    status=OperationStatus.ERROR,
                    message="invalid design sidecar",
                ),
                metadata={"unit_id": unit_id, "errors": errors},
            )

        status = sidecar["status"]
        if status not in DESIGN_MUTABLE_STATUSES:
            return ArtifactRuntimeResult(
                result=OperationResult(
                    status=OperationStatus.ERROR,
                    message="write_draft may persist only draft or in_review status",
                ),
                metadata={"unit_id": unit_id, "status": status},
            )

        return self.artifacts.write_artifact_checkpoint(
            key=ArtifactKey(stage=ArtifactStage.DESIGN, artifact_id=unit_id),
            markdown=markdown,
            stage_metadata=sidecar,
            flush_reason=FlushReason.CHECKPOINT,
        )

    def to_review(
        self,
        *,
        unit_id: str,
    ) -> ArtifactRuntimeResult:
        key = ArtifactKey(stage=ArtifactStage.DESIGN, artifact_id=unit_id)
        read_result = self.artifacts.read_artifact(key=key)
        if not read_result.result.ok:
            return read_result

        stage_metadata = dict(read_result.artifacts["stage_metadata"])
        errors = _validate_design_sidecar(stage_metadata)
        if errors:
            return ArtifactRuntimeResult(
                result=OperationResult(
                    status=OperationStatus.ERROR,
                    message="design unit is missing required review fields",
                ),
                metadata={"unit_id": unit_id, "errors": errors},
            )

        status = stage_metadata["status"]
        if status == "accepted":
            return ArtifactRuntimeResult(
                result=OperationResult(
                    status=OperationStatus.ERROR,
                    message="accepted design unit cannot move back into review via to_review",
                ),
                metadata={"unit_id": unit_id, "status": status},
            )
        if status == "in_review":
            return ArtifactRuntimeResult(
                result=OperationResult(
                    status=OperationStatus.OK,
                    message="design unit already in review",
                ),
                artifacts={"version_id": read_result.artifacts["version_id"]},
                metadata={
                    "unit_id": unit_id,
                    "version_id": read_result.metadata["version_id"],
                    "checkpoint_id": read_result.metadata["checkpoint_id"],
                    "status": status,
                },
            )

        return self.artifacts.transition_artifact_status(
            key=key,
            status="in_review",
            flush_reason=FlushReason.REVIEW_TRANSITION,
        )

    def accept(
        self,
        *,
        unit_id: str,
        override: bool = False,
    ) -> ArtifactRuntimeResult:
        key = ArtifactKey(stage=ArtifactStage.DESIGN, artifact_id=unit_id)
        read_result = self.artifacts.read_artifact(key=key)
        if not read_result.result.ok:
            return read_result

        stage_metadata = dict(read_result.artifacts["stage_metadata"])
        errors = _validate_design_sidecar(stage_metadata)
        if errors:
            return ArtifactRuntimeResult(
                result=OperationResult(
                    status=OperationStatus.ERROR,
                    message="design unit is missing required acceptance fields",
                ),
                metadata={"unit_id": unit_id, "errors": errors},
            )

        status = stage_metadata["status"]
        if status == "accepted":
            return ArtifactRuntimeResult(
                result=OperationResult(
                    status=OperationStatus.OK,
                    message="design unit already accepted",
                ),
                artifacts={"version_id": read_result.artifacts["version_id"]},
                metadata={
                    "unit_id": unit_id,
                    "version_id": read_result.metadata["version_id"],
                    "checkpoint_id": read_result.metadata["checkpoint_id"],
                    "status": status,
                    "override": override,
                },
            )

        if status != "in_review" and not override:
            return ArtifactRuntimeResult(
                result=OperationResult(
                    status=OperationStatus.ERROR,
                    message="design unit must be in_review before acceptance unless override is explicit",
                ),
                metadata={"unit_id": unit_id, "status": status, "override": override},
            )

        transition = self.artifacts.transition_artifact_status(
            key=key,
            status="accepted",
            flush_reason=FlushReason.REVIEW_DECISION,
        )
        if not transition.result.ok:
            return transition

        warnings = transition.warnings
        if override and status == "draft":
            warnings = (*warnings, "Design acceptance proceeded from draft via explicit override.")

        metadata = dict(transition.metadata)
        metadata["override"] = override
        metadata["accepted_from_status"] = status
        return ArtifactRuntimeResult(
            result=transition.result,
            warnings=warnings,
            artifacts=transition.artifacts,
            metadata=metadata,
        )


def _validate_design_sidecar(sidecar: dict[str, object]) -> list[str]:
    errors: list[str] = []
    for field in DESIGN_REQUIRED_FIELDS:
        if field not in sidecar:
            errors.append(f"missing required field: {field}")

    if sidecar.get("status") not in DESIGN_ALLOWED_STATUSES:
        errors.append("status must be 'draft', 'in_review', or 'accepted'")
    if sidecar.get("design_unit_id") is not None and sidecar.get("design_unit_id") == "":
        errors.append("design_unit_id must be a non-empty string")
    if not isinstance(sidecar.get("title"), str) or not sidecar.get("title"):
        errors.append("title must be a non-empty string")
    if not isinstance(sidecar.get("scope_summary"), str) or not sidecar.get("scope_summary"):
        errors.append("scope_summary must be a non-empty string")
    if sidecar.get("readiness") not in DESIGN_READINESS_VALUES:
        errors.append("readiness must be 'low', 'medium', or 'high'")
    if not isinstance(sidecar.get("readiness_rationale"), str) or not sidecar.get("readiness_rationale"):
        errors.append("readiness_rationale must be a non-empty string")
    if not isinstance(sidecar.get("open_questions"), list):
        errors.append("open_questions must be a list")
    if not isinstance(sidecar.get("assumptions"), list):
        errors.append("assumptions must be a list")

    depends_on = sidecar.get("depends_on", [])
    children = sidecar.get("children", [])
    parent = sidecar.get("parent")
    if not isinstance(depends_on, list):
        errors.append("depends_on must be a list when present")
    if not isinstance(children, list):
        errors.append("children must be a list when present")
    if parent is not None and not isinstance(parent, str):
        errors.append("parent must be a string or null when present")

    return errors


def _render_design_payload(
    *,
    unit_id: str,
    base_artifacts: dict[str, object],
    stage_metadata: dict[str, object],
) -> dict[str, object]:
    return {
        "artifact_id": base_artifacts["artifact_id"],
        "design_unit_id": stage_metadata.get("design_unit_id", unit_id),
        "stage": base_artifacts["stage"],
        "version_id": base_artifacts["version_id"],
        "title": stage_metadata.get("title"),
        "workflow_status": stage_metadata.get("status"),
        "readiness": stage_metadata.get("readiness"),
        "readiness_rationale": stage_metadata.get("readiness_rationale"),
        "scope_summary": stage_metadata.get("scope_summary"),
        "linkage": {
            "depends_on": stage_metadata.get("depends_on", []),
            "children": stage_metadata.get("children", []),
            "parent": stage_metadata.get("parent"),
        },
    }
