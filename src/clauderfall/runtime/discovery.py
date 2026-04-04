"""Discovery runtime service on top of the shared artifact runtime."""

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


DISCOVERY_REQUIRED_FIELDS = (
    "title",
    "status",
    "readiness",
    "readiness_rationale",
    "blocking_gaps",
    "problem_areas",
    "cross_cutting",
)


@dataclass(frozen=True)
class DiscoveryRuntimeService:
    """Stage-specific Discovery operations built on the shared artifact runtime."""

    artifacts: StageArtifactRuntime

    def read(
        self,
        *,
        brief_id: str,
        checkpoint_id: str | None = None,
        view: str = "short",
    ) -> ArtifactRuntimeResult:
        key = ArtifactKey(stage=ArtifactStage.DISCOVERY, artifact_id=brief_id)
        result = self.artifacts.read_artifact(key=key, checkpoint_id=checkpoint_id)
        if not result.result.ok:
            return result

        sidecar = dict(result.artifacts["stage_metadata"])
        artifacts = _render_discovery_short_payload(
            brief_id=brief_id,
            base_artifacts=result.artifacts,
            sidecar=sidecar,
        )
        if view == "full":
            artifacts["problem_areas"] = sidecar.get("problem_areas", [])
            artifacts["cross_cutting"] = sidecar.get("cross_cutting", {})
            artifacts["markdown"] = self.artifacts.read_artifact_markdown(key=key, checkpoint_id=checkpoint_id) or ""
        return ArtifactRuntimeResult(
            result=result.result,
            warnings=result.warnings,
            artifacts=artifacts,
            metadata=result.metadata,
        )

    def write_draft(
        self,
        *,
        brief_id: str,
        markdown: str,
        sidecar: dict[str, object],
    ) -> ArtifactRuntimeResult:
        errors = _validate_discovery_sidecar(sidecar)
        if errors:
            return ArtifactRuntimeResult(
                result=OperationResult(
                    status=OperationStatus.ERROR,
                    message="invalid discovery sidecar",
                ),
                metadata={"brief_id": brief_id, "errors": errors},
            )

        return self.artifacts.write_artifact_checkpoint(
            key=ArtifactKey(stage=ArtifactStage.DISCOVERY, artifact_id=brief_id),
            markdown=markdown,
            stage_metadata=sidecar,
            flush_reason=FlushReason.CHECKPOINT,
        )

    def to_design(
        self,
        *,
        brief_id: str,
        override: bool = False,
    ) -> ArtifactRuntimeResult:
        key = ArtifactKey(stage=ArtifactStage.DISCOVERY, artifact_id=brief_id)
        read_result = self.artifacts.read_artifact(key=key)
        if not read_result.result.ok:
            return read_result

        stage_metadata = dict(read_result.artifacts["stage_metadata"])
        errors = _validate_discovery_sidecar(stage_metadata)
        if errors:
            return ArtifactRuntimeResult(
                result=OperationResult(
                    status=OperationStatus.ERROR,
                    message="discovery brief is missing required handoff fields",
                ),
                metadata={"brief_id": brief_id, "errors": errors},
            )

        status = stage_metadata["status"]
        readiness = stage_metadata["readiness"]
        if status != "accepted" and not override:
            return ArtifactRuntimeResult(
                result=OperationResult(
                    status=OperationStatus.ERROR,
                    message="discovery brief must be accepted before Design handoff unless override is explicit",
                ),
                metadata={"brief_id": brief_id, "status": status, "override": override},
            )

        if override and readiness not in {"low", "medium", "high"}:
            return ArtifactRuntimeResult(
                result=OperationResult(status=OperationStatus.ERROR, message="invalid readiness value"),
                metadata={"brief_id": brief_id, "readiness": readiness},
            )

        discovery_markdown = self.artifacts.read_artifact_markdown(key=key) or ""
        start_context = _derive_design_start_context(
            discovery_markdown=discovery_markdown,
            discovery_sidecar=stage_metadata,
            override=override,
        )

        warnings: tuple[str, ...] = ()
        if override and status != "accepted":
            warnings = ("Design handoff proceeded from draft via explicit override.",)

        return ArtifactRuntimeResult(
            result=OperationResult(status=OperationStatus.OK, message="discovery transitioned to design"),
            warnings=warnings,
            artifacts={
                "design_handoff": _render_design_handoff_payload(start_context),
            },
            metadata={
                "brief_id": brief_id,
                "override": override,
                "source_version_id": read_result.metadata["version_id"],
                "readiness": readiness,
                "status": status,
            },
        )

    def delete(self, *, brief_id: str) -> ArtifactRuntimeResult:
        return self.artifacts.delete_artifact(
            key=ArtifactKey(stage=ArtifactStage.DISCOVERY, artifact_id=brief_id),
        )


def _render_design_handoff_payload(start_context: dict[str, object]) -> dict[str, object]:
    recommendation = dict(start_context["design_start_recommendation"])
    return {
        "recommended_focus": recommendation["focus"],
        "rationale": recommendation["rationale"],
        "caution": recommendation["caution"],
        "regenerated_after_reentry": dict(start_context["design_start_context_metadata"]).get(
            "regenerated_after_reentry",
            False,
        ),
    }


def _render_discovery_short_payload(
    *,
    brief_id: str,
    base_artifacts: dict[str, object],
    sidecar: dict[str, object],
) -> dict[str, object]:
    return {
        "brief_id": brief_id,
        "stage": base_artifacts["stage"],
        "version_id": base_artifacts["version_id"],
        "title": sidecar.get("title"),
        "status": sidecar.get("status"),
        "readiness": sidecar.get("readiness"),
        "readiness_rationale": sidecar.get("readiness_rationale"),
        "blocking_gaps": sidecar.get("blocking_gaps", []),
    }


def _validate_discovery_sidecar(sidecar: dict[str, object]) -> list[str]:
    errors: list[str] = []
    for field in DISCOVERY_REQUIRED_FIELDS:
        if field not in sidecar:
            errors.append(f"missing required field: {field}")

    if sidecar.get("status") not in {"draft", "accepted"}:
        errors.append("status must be 'draft' or 'accepted'")
    if sidecar.get("readiness") not in {"low", "medium", "high"}:
        errors.append("readiness must be 'low', 'medium', or 'high'")
    if not isinstance(sidecar.get("readiness_rationale"), str) or not sidecar.get("readiness_rationale"):
        errors.append("readiness_rationale must be a non-empty string")
    if not isinstance(sidecar.get("blocking_gaps"), list):
        errors.append("blocking_gaps must be a list")
    if not isinstance(sidecar.get("problem_areas"), list) or not sidecar.get("problem_areas"):
        errors.append("problem_areas must be a non-empty list")
    else:
        for i, area in enumerate(sidecar["problem_areas"]):  # type: ignore[union-attr]
            errors.extend(_validate_problem_area(i, area))  # type: ignore[arg-type]
    if not isinstance(sidecar.get("cross_cutting"), dict):
        errors.append("cross_cutting must be an object")
    return errors


def _validate_problem_area(index: int, area: dict[str, object]) -> list[str]:
    errors: list[str] = []
    prefix = f"problem_areas[{index}]"
    for field in ("problem_area_id", "title", "confidence", "source_section"):
        if not area.get(field):
            errors.append(f"{prefix}: missing required field: {field}")
    if "confidence" in area and area["confidence"] not in {"low", "medium", "high"}:
        errors.append(f"{prefix}: confidence must be 'low', 'medium', or 'high'")
    if not isinstance(area.get("assumptions"), list):
        errors.append(f"{prefix}: assumptions must be a list")
    else:
        for j, assumption in enumerate(area["assumptions"]):  # type: ignore[union-attr]
            errors.extend(_validate_assumption(f"{prefix}.assumptions[{j}]", assumption))  # type: ignore[arg-type]
    return errors


def _validate_assumption(prefix: str, assumption: dict[str, object]) -> list[str]:
    errors: list[str] = []
    for field in ("assumption_id", "statement", "status"):
        if not assumption.get(field):
            errors.append(f"{prefix}: missing required field: {field}")
    if "status" in assumption and assumption["status"] not in {"confirmed", "inferred", "unknown"}:
        errors.append(f"{prefix}: status must be 'confirmed', 'inferred', or 'unknown'")
    return errors


def _derive_design_start_context(
    *,
    discovery_markdown: str,
    discovery_sidecar: dict[str, object],
    override: bool,
) -> dict[str, object]:
    problem_areas = list(discovery_sidecar["problem_areas"])
    cross_cutting = dict(discovery_sidecar["cross_cutting"])
    assumptions: list[dict[str, object]] = []

    for problem_area in problem_areas:
        for assumption in problem_area.get("assumptions", []):
            assumptions.append(
                {
                    "assumption_id": assumption["assumption_id"],
                    "statement": assumption["statement"],
                    "status": assumption["status"],
                    "scope": problem_area["problem_area_id"],
                    "design_impact": f"Affects design work around {problem_area['title']}.",
                    "source_section": problem_area["source_section"],
                }
            )

    for assumption in cross_cutting.get("shared_assumptions", []):
        assumptions.append(
            {
                "assumption_id": assumption["assumption_id"],
                "statement": assumption["statement"],
                "status": assumption["status"],
                "scope": "cross_cutting",
                "design_impact": "Shapes multiple early design decisions.",
                "source_section": cross_cutting.get("source_sections", []),
            }
        )

    mapped_problem_areas = [
        {
            "problem_area_id": area["problem_area_id"],
            "title": area["title"],
            "summary": f"Design should preserve the framing for {area['title']}.",
            "confidence": area["confidence"],
            "design_relevance": f"{area['title']} is likely to shape early design sequencing.",
            "source_section": area["source_section"],
        }
        for area in problem_areas
    ]

    caution = None
    if override or discovery_sidecar["readiness"] != "high" or discovery_sidecar["blocking_gaps"]:
        caution = discovery_sidecar["blocking_gaps"][0] if discovery_sidecar["blocking_gaps"] else (
            "Proceeding with visible framing weakness from Discovery."
        )

    return {
        "design_start_context_metadata": {"regenerated_after_reentry": False},
        "context_summary": discovery_sidecar["readiness_rationale"],
        "problem_areas": mapped_problem_areas,
        "cross_cutting": {
            "global_constraints": cross_cutting.get("global_constraints", []),
            "systemic_risks": cross_cutting.get("systemic_risks", []),
            "open_questions": cross_cutting.get("open_questions", []),
            "source_sections": cross_cutting.get("source_sections", []),
        },
        "assumptions": assumptions,
        "design_start_recommendation": {
            "focus": mapped_problem_areas[0]["title"],
            "rationale": f"Start with {mapped_problem_areas[0]['title']} because it is a visible Discovery problem area.",
            "caution": caution,
        },
    }
