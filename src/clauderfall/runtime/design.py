"""Design runtime service on top of the shared artifact runtime."""

from __future__ import annotations

import re
from dataclasses import dataclass

from clauderfall.runtime.artifacts import StageArtifactRuntime
from clauderfall.runtime.types import (
    ArtifactKey,
    ArtifactRecord,
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
DESIGN_ALLOWED_STATUSES = {"draft", "accepted"}
DESIGN_MUTABLE_STATUSES = {"draft"}
DESIGN_READINESS_VALUES = {"low", "medium", "high"}
HEADING_PATTERN = re.compile(r"^(#{1,6})[ \t]+(.+?)\s*$", re.MULTILINE)


@dataclass(frozen=True)
class DesignRuntimeService:
    """Stage-specific Design operations built on the shared artifact runtime."""

    artifacts: StageArtifactRuntime

    def list(self) -> ArtifactRuntimeResult:
        records = self.artifacts.list_artifacts(stage=ArtifactStage.DESIGN)
        units: list[dict[str, object]] = []
        warnings: list[str] = []

        for record in records:
            unit, unit_warnings = _render_design_list_entry(record)
            units.append(unit)
            warnings.extend(unit_warnings)

        return ArtifactRuntimeResult(
            result=OperationResult(status=OperationStatus.OK, message="design units listed"),
            warnings=tuple(warnings),
            artifacts={"units": units, "count": len(units)},
        )

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
            shaped_artifacts["markdown"] = self.artifacts.read_artifact_markdown(key=key, checkpoint_id=checkpoint_id) or ""
        return ArtifactRuntimeResult(
            result=result.result,
            warnings=result.warnings,
            artifacts=shaped_artifacts,
            metadata=result.metadata,
        )

    def write(
        self,
        *,
        unit_id: str,
        markdown: str | None = None,
        sidecar: dict[str, object] | None = None,
        markdown_operations: list[dict[str, object]] | None = None,
        sidecar_patch: dict[str, object] | None = None,
        base_checkpoint_id: str | None = None,
    ) -> ArtifactRuntimeResult:
        if markdown is not None or sidecar is not None:
            return self._write_full_draft(
                unit_id=unit_id,
                markdown=markdown,
                sidecar=sidecar,
            )
        return self._write_delta_draft(
            unit_id=unit_id,
            markdown_operations=markdown_operations,
            sidecar_patch=sidecar_patch,
            base_checkpoint_id=base_checkpoint_id,
        )

    def _write_full_draft(
        self,
        *,
        unit_id: str,
        markdown: str | None,
        sidecar: dict[str, object] | None,
    ) -> ArtifactRuntimeResult:
        if markdown is None or sidecar is None:
            return ArtifactRuntimeResult(
                result=OperationResult(
                    status=OperationStatus.ERROR,
                    message="full design writes require both markdown and sidecar",
                ),
                metadata={"unit_id": unit_id},
            )

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
                    message="write may persist only draft status",
                ),
                metadata={"unit_id": unit_id, "status": status},
            )

        return self.artifacts.write_artifact_checkpoint(
            key=ArtifactKey(stage=ArtifactStage.DESIGN, artifact_id=unit_id),
            markdown=markdown,
            stage_metadata=sidecar,
            flush_reason=FlushReason.CHECKPOINT,
        )

    def _write_delta_draft(
        self,
        *,
        unit_id: str,
        markdown_operations: list[dict[str, object]] | None,
        sidecar_patch: dict[str, object] | None,
        base_checkpoint_id: str | None,
    ) -> ArtifactRuntimeResult:
        if not markdown_operations and not sidecar_patch:
            return ArtifactRuntimeResult(
                result=OperationResult(
                    status=OperationStatus.ERROR,
                    message="delta design writes require markdown_operations or sidecar_patch",
                ),
                metadata={"unit_id": unit_id},
            )

        key = ArtifactKey(stage=ArtifactStage.DESIGN, artifact_id=unit_id)
        read_result = self.artifacts.read_artifact(key=key)
        if not read_result.result.ok:
            return read_result

        current_checkpoint_id = str(read_result.metadata["checkpoint_id"])
        if base_checkpoint_id is not None and base_checkpoint_id != current_checkpoint_id:
            return ArtifactRuntimeResult(
                result=OperationResult(
                    status=OperationStatus.ERROR,
                    message="base checkpoint does not match current authoritative checkpoint",
                ),
                metadata={
                    "unit_id": unit_id,
                    "base_checkpoint_id": base_checkpoint_id,
                    "current_checkpoint_id": current_checkpoint_id,
                },
            )

        current_markdown = self.artifacts.read_artifact_markdown(key=key) or ""
        current_sidecar = dict(read_result.artifacts["stage_metadata"])
        merged_sidecar = dict(current_sidecar)
        if sidecar_patch:
            merged_sidecar.update(sidecar_patch)

        errors = _validate_design_sidecar(merged_sidecar)
        if errors:
            return ArtifactRuntimeResult(
                result=OperationResult(
                    status=OperationStatus.ERROR,
                    message="invalid design sidecar patch",
                ),
                metadata={"unit_id": unit_id, "errors": errors},
            )

        status = merged_sidecar["status"]
        if status not in DESIGN_MUTABLE_STATUSES:
            return ArtifactRuntimeResult(
                result=OperationResult(
                    status=OperationStatus.ERROR,
                    message="write may persist only draft status",
                ),
                metadata={"unit_id": unit_id, "status": status},
            )

        try:
            next_markdown = _apply_markdown_operations(current_markdown, markdown_operations or [])
        except ValueError as exc:
            return ArtifactRuntimeResult(
                result=OperationResult(
                    status=OperationStatus.ERROR,
                    message=f"invalid markdown operations: {exc}",
                ),
                metadata={"unit_id": unit_id},
            )

        result = self.artifacts.write_artifact_checkpoint(
            key=key,
            markdown=next_markdown,
            stage_metadata=merged_sidecar,
            flush_reason=FlushReason.CHECKPOINT,
        )
        metadata = dict(result.metadata)
        metadata["base_checkpoint_id"] = current_checkpoint_id
        return ArtifactRuntimeResult(
            result=result.result,
            warnings=result.warnings,
            artifacts=result.artifacts,
            metadata=metadata,
        )

    def accept(
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
                },
            )

        transition = self.artifacts.transition_artifact_status(
            key=key,
            status="accepted",
            flush_reason=FlushReason.REVIEW_DECISION,
        )
        if not transition.result.ok:
            return transition

        metadata = dict(transition.metadata)
        metadata["accepted_from_status"] = status
        return ArtifactRuntimeResult(
            result=transition.result,
            warnings=transition.warnings,
            artifacts=transition.artifacts,
            metadata=metadata,
        )

    def delete(self, *, unit_id: str) -> ArtifactRuntimeResult:
        return self.artifacts.delete_artifact(
            key=ArtifactKey(stage=ArtifactStage.DESIGN, artifact_id=unit_id),
        )


def _validate_design_sidecar(sidecar: dict[str, object]) -> list[str]:
    errors: list[str] = []
    for field in DESIGN_REQUIRED_FIELDS:
        if field not in sidecar:
            errors.append(f"missing required field: {field}")

    if sidecar.get("status") not in DESIGN_ALLOWED_STATUSES:
        errors.append("status must be 'draft' or 'accepted'")
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


def _render_design_list_entry(record: ArtifactRecord) -> tuple[dict[str, object], tuple[str, ...]]:
    unit = {
        "unit_id": record.key.artifact_id,
        "title": record.stage_metadata.get("title"),
        "status": record.stage_metadata.get("status"),
        "readiness": record.stage_metadata.get("readiness"),
        "updated_at": record.updated_at.isoformat(),
    }

    missing_fields = [
        field
        for field in ("title", "status", "readiness")
        if not isinstance(record.stage_metadata.get(field), str) or not record.stage_metadata.get(field)
    ]
    if not missing_fields:
        return unit, ()

    unit["malformed"] = True
    return unit, (f"design unit {record.key.artifact_id} is malformed: missing {', '.join(missing_fields)}",)


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


def _apply_markdown_operations(markdown: str, operations: list[dict[str, object]]) -> str:
    updated = markdown
    for operation in operations:
        op_name = operation.get("op")
        if not isinstance(op_name, str) or not op_name:
            raise ValueError("each markdown operation requires a non-empty op")

        if op_name == "replace_section":
            heading = _require_string_field(operation, "heading")
            content = _require_string_field(operation, "content")
            updated = _replace_section(updated, heading=heading, content=content)
            continue
        if op_name == "append_to_section":
            heading = _require_string_field(operation, "heading")
            content = _require_string_field(operation, "content")
            updated = _append_to_section(updated, heading=heading, content=content)
            continue
        if op_name == "insert_section_after":
            after_heading = _require_string_field(operation, "after_heading")
            heading_line = _require_string_field(operation, "heading_line")
            content = _require_string_field(operation, "content")
            updated = _insert_section_after(
                updated,
                after_heading=after_heading,
                heading_line=heading_line,
                content=content,
            )
            continue
        if op_name == "delete_section":
            heading = _require_string_field(operation, "heading")
            updated = _delete_section(updated, heading=heading)
            continue
        if op_name == "append_markdown":
            content = _require_string_field(operation, "content")
            updated = _append_markdown(updated, content=content)
            continue
        raise ValueError(f"unsupported markdown operation: {op_name}")
    return updated


def _require_string_field(payload: dict[str, object], field: str) -> str:
    value = payload.get(field)
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field} must be a non-empty string")
    return value


def _replace_section(markdown: str, *, heading: str, content: str) -> str:
    start, end, heading_line = _find_section(markdown, heading)
    section = _render_section(heading_line=heading_line, content=content)
    return markdown[:start] + section + markdown[end:]


def _append_to_section(markdown: str, *, heading: str, content: str) -> str:
    start, end, heading_line = _find_section(markdown, heading)
    existing_section = markdown[start:end]
    existing_body = existing_section[len(heading_line) :].strip()
    combined = existing_body
    addition = content.strip()
    if combined:
        combined = f"{combined}\n\n{addition}" if addition else combined
    else:
        combined = addition
    section = _render_section(heading_line=heading_line, content=combined)
    return markdown[:start] + section + markdown[end:]


def _insert_section_after(markdown: str, *, after_heading: str, heading_line: str, content: str) -> str:
    _, end, _ = _find_section(markdown, after_heading)
    inserted = _render_section(heading_line=heading_line, content=content)
    prefix = markdown[:end].rstrip()
    suffix = markdown[end:].lstrip("\n")
    if suffix:
        return f"{prefix}\n\n{inserted}\n\n{suffix}"
    return f"{prefix}\n\n{inserted}"


def _delete_section(markdown: str, *, heading: str) -> str:
    start, end, _ = _find_section(markdown, heading)
    prefix = markdown[:start].rstrip()
    suffix = markdown[end:].lstrip("\n")
    if prefix and suffix:
        return f"{prefix}\n\n{suffix}"
    return prefix or suffix


def _append_markdown(markdown: str, *, content: str) -> str:
    stripped = markdown.rstrip()
    addition = content.strip()
    if not stripped:
        return addition
    if not addition:
        return stripped
    return f"{stripped}\n\n{addition}"


def _render_section(*, heading_line: str, content: str) -> str:
    body = content.strip()
    if body:
        return f"{heading_line}\n\n{body}\n"
    return f"{heading_line}\n"


def _find_section(markdown: str, heading: str) -> tuple[int, int, str]:
    matches = list(HEADING_PATTERN.finditer(markdown))
    normalized_heading = heading.strip()
    for index, match in enumerate(matches):
        heading_text = match.group(2).strip()
        if heading_text != normalized_heading:
            continue
        level = len(match.group(1))
        start = match.start()
        end = len(markdown)
        for next_match in matches[index + 1 :]:
            if len(next_match.group(1)) <= level:
                end = next_match.start()
                break
        return start, end, match.group(0).rstrip()
    raise ValueError(f"section not found: {heading}")
