from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from clauderfall.mcp import create_server, map_runtime_result
from clauderfall.runtime import (
    ArtifactKey,
    ArtifactRecord,
    ArtifactRuntimeResult,
    ArtifactStage,
    FlushReason,
    OperationResult,
    OperationStatus,
    build_runtime_services,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
LARGE_BODY = "# Heading\n\n" + ("payload line\n" * 2000)
COMPACT_MCP_BUDGET_BYTES = 300


def _payload_size_bytes(payload: dict[str, object]) -> int:
    return len(json.dumps(payload, sort_keys=True))


def test_artifact_store_round_trips_current_record(tmp_path: Path) -> None:
    services = build_runtime_services(tmp_path)
    key = ArtifactKey(stage=ArtifactStage.DESIGN, artifact_id="auth-session")

    record = services.store.write(
        key=key,
        markdown="# Auth Session\n\nDraft design unit.",
        stage_metadata={
            "status": "draft",
            "readiness": {"state": "not_ready", "blocking_gaps": ["Need invariant coverage"]},
        },
        flush_reason="checkpoint",
    )

    current = services.store.read(key)

    assert current is not None
    assert current.version_id == record.version_id
    assert current.stage_metadata["status"] == "draft"
    assert isinstance(current, ArtifactRecord)


def test_artifact_store_lists_stage_records_by_updated_at_desc(tmp_path: Path) -> None:
    services = build_runtime_services(tmp_path)
    services.store.write(
        key=ArtifactKey(stage=ArtifactStage.DESIGN, artifact_id="older-design-unit"),
        markdown="# Older Design Unit\n\nBody.",
        stage_metadata={"title": "Older Design Unit", "status": "draft", "readiness": "low"},
        flush_reason="checkpoint",
    )
    services.store.write(
        key=ArtifactKey(stage=ArtifactStage.DISCOVERY, artifact_id="discovery-brief"),
        markdown="# Discovery Brief\n\nBody.",
        stage_metadata={"title": "Discovery Brief", "status": "draft", "readiness": "medium"},
        flush_reason="checkpoint",
    )
    newer_design = services.store.write(
        key=ArtifactKey(stage=ArtifactStage.DESIGN, artifact_id="newer-design-unit"),
        markdown="# Newer Design Unit\n\nBody.",
        stage_metadata={"title": "Newer Design Unit", "status": "accepted", "readiness": "high"},
        flush_reason="checkpoint",
    )

    records = services.store.list_by_stage(ArtifactStage.DESIGN)

    assert [record.key.artifact_id for record in records] == ["newer-design-unit", "older-design-unit"]
    assert records[0].version_id == newer_design.version_id


def test_artifact_store_delete_removes_rows_and_markdown_history(tmp_path: Path) -> None:
    services = build_runtime_services(tmp_path)
    key = ArtifactKey(stage=ArtifactStage.DISCOVERY, artifact_id="disc-delete")
    first = services.store.write(
        key=key,
        markdown="# Discovery\n\nFirst.",
        stage_metadata={"title": "Discovery", "status": "draft", "readiness": "low"},
        flush_reason="checkpoint",
    )
    services.store.write(
        key=key,
        markdown="# Discovery\n\nSecond.",
        stage_metadata={"title": "Discovery", "status": "accepted", "readiness": "high"},
        flush_reason="checkpoint",
    )

    deletion = services.store.delete(key)

    assert deletion["artifact_rows_deleted"] == 1
    assert deletion["checkpoint_rows_deleted"] == 2
    assert deletion["current_markdown_deleted"] is True
    assert deletion["checkpoint_markdown_deleted"] is True
    assert services.store.read(key) is None
    assert services.store.read_checkpoint(key=key, checkpoint_id=first.version_id) is None
    assert not services.store.markdown_path(key).exists()
    assert not services.store.checkpoint_markdown_path(key=key, checkpoint_id=first.version_id).exists()


def test_runtime_services_wiring_exposes_shared_substrate_components(tmp_path: Path) -> None:
    services = build_runtime_services(tmp_path)

    assert services.store is not None
    assert services.artifacts.store is services.store
    assert services.discovery.artifacts is services.artifacts
    assert services.design.artifacts is services.artifacts
    assert services.session_lifecycle.session is services.session


def test_operation_result_ok_tracks_non_error_status() -> None:
    warning = OperationResult(
        status=OperationStatus.WARNING,
        message="completed with warnings",
        warnings=("current projection refreshed",),
    )
    error = OperationResult(status=OperationStatus.ERROR, message="checkpoint write failed")

    assert warning.ok is True
    assert error.ok is False


def test_shared_artifact_runtime_reads_current_returns_version_id(tmp_path: Path) -> None:
    services = build_runtime_services(tmp_path)
    key = ArtifactKey(stage=ArtifactStage.DISCOVERY, artifact_id="brief-1")
    write_result = services.artifacts.write_artifact_checkpoint(
        key=key,
        markdown="# Discovery Brief\n\nBody text.",
        stage_metadata={
            "title": "Discovery Brief",
            "status": "draft",
            "readiness": {"state": "not_ready"},
        },
        flush_reason=FlushReason.CHECKPOINT,
    )

    read_result = services.artifacts.read_artifact(key=key)

    assert read_result.result.ok is True
    assert read_result.artifacts["artifact_id"] == "brief-1"
    assert "markdown" not in read_result.artifacts
    assert read_result.artifacts["title"] == "Discovery Brief"
    assert "version_id" in read_result.metadata
    assert read_result.metadata["version_id"] == write_result.metadata["version_id"]


def test_shared_artifact_runtime_transition_writes_later_version_for_reopen(tmp_path: Path) -> None:
    services = build_runtime_services(tmp_path)
    key = ArtifactKey(stage=ArtifactStage.DESIGN, artifact_id="unit-1")
    initial = services.artifacts.write_artifact_checkpoint(
        key=key,
        markdown="# Unit\n\nAccepted draft.",
        stage_metadata={"status": "accepted", "title": "Unit"},
        flush_reason=FlushReason.REVIEW_DECISION,
    )

    reopened = services.artifacts.transition_artifact_status(
        key=key,
        status="draft",
        flush_reason=FlushReason.REENTRY_REPAIR,
        stage_metadata_updates={"reopen_reason": "new constraint found"},
    )

    current = services.artifacts.read_artifact(key=key)

    assert reopened.result.ok is True
    assert reopened.metadata["previous_version_id"] == initial.metadata["version_id"]
    assert reopened.metadata["version_id"] != initial.metadata["version_id"]
    assert current.artifacts["status"] == "draft"
    assert current.artifacts["stage_metadata"]["reopen_reason"] == "new constraint found"


def test_discovery_write_and_read_support_short_and_full_views(tmp_path: Path) -> None:
    services = build_runtime_services(tmp_path)
    sidecar = {
        "title": "Auth Discovery",
        "status": "draft",
        "readiness": "medium",
        "readiness_rationale": "Main framing is visible but one major assumption remains weak.",
        "blocking_gaps": ["Session invalidation behavior is unclear."],
        "problem_areas": [
            {
                "problem_area_id": "auth-session",
                "title": "Auth Session Boundaries",
                "confidence": "medium",
                "source_section": "## Auth Session Boundaries",
                "assumptions": [
                    {
                        "assumption_id": "assume-1",
                        "statement": "Session invalidation can be centralized.",
                        "status": "inferred",
                    }
                ],
            }
        ],
        "cross_cutting": {
            "global_constraints": ["Must preserve operator trust."],
            "shared_assumptions": [
                {
                    "assumption_id": "shared-1",
                    "statement": "Auditability matters across all flows.",
                    "status": "confirmed",
                }
            ],
            "systemic_risks": ["Rework if session boundaries are wrong."],
            "open_questions": ["How strict should revocation guarantees be?"],
            "source_sections": ["## Cross-Cutting Constraints"],
        },
    }

    services.discovery.write(
        brief_id="disc-1",
        markdown="# Auth Discovery\n\nDraft brief body.",
        sidecar=sidecar,
    )

    result = services.discovery.read(brief_id="disc-1")

    assert result.result.ok is True
    assert result.artifacts["status"] == "draft"
    assert result.artifacts["readiness"] == "medium"
    assert result.artifacts["title"] == "Auth Discovery"
    assert "markdown" not in result.artifacts
    assert "stage_metadata" not in result.artifacts
    assert "problem_areas" not in result.artifacts


def test_discovery_delete_removes_artifact_and_is_retry_safe(tmp_path: Path) -> None:
    services = build_runtime_services(tmp_path)
    services.discovery.write(
        brief_id="disc-1",
        markdown="# Discovery\n\nBody.",
        sidecar={
            "title": "Auth Discovery",
            "status": "draft",
            "readiness": "medium",
            "readiness_rationale": "Enough to persist.",
            "blocking_gaps": [],
            "problem_areas": [
                {
                    "problem_area_id": "auth-session",
                    "title": "Auth Session Boundaries",
                    "confidence": "medium",
                    "source_section": "## Auth Session Boundaries",
                    "assumptions": [],
                }
            ],
            "cross_cutting": {
                "global_constraints": [],
                "shared_assumptions": [],
                "systemic_risks": [],
                "open_questions": [],
                "source_sections": [],
            },
        },
    )

    deleted = services.discovery.delete(brief_id="disc-1")
    missing = services.discovery.read(brief_id="disc-1")
    repeat = services.discovery.delete(brief_id="disc-1")

    assert deleted.result.ok is True
    assert deleted.metadata["deleted"] is True
    assert missing.result.ok is False
    assert repeat.result.status == OperationStatus.WARNING
    assert repeat.warnings == ("artifact_not_found",)


def test_discovery_to_design_blocks_without_acceptance_or_override(tmp_path: Path) -> None:
    services = build_runtime_services(tmp_path)
    services.discovery.write(
        brief_id="disc-1",
        markdown="# Auth Discovery\n\nDraft brief body.",
        sidecar={
            "title": "Auth Discovery",
            "status": "draft",
            "readiness": "medium",
            "readiness_rationale": "Still one visible gap.",
            "blocking_gaps": ["Missing revocation semantics."],
            "problem_areas": [
                {
                    "problem_area_id": "auth-session",
                    "title": "Auth Session Boundaries",
                    "confidence": "medium",
                    "source_section": "## Auth Session Boundaries",
                    "assumptions": [],
                }
            ],
            "cross_cutting": {
                "global_constraints": [],
                "shared_assumptions": [],
                "systemic_risks": [],
                "open_questions": [],
                "source_sections": ["## Cross-Cutting Constraints"],
            },
        },
    )

    result = services.discovery.to_design(brief_id="disc-1")

    assert result.result.ok is False
    assert "accepted" in result.result.message


def test_discovery_to_design_supports_normal_and_override_handoff(tmp_path: Path) -> None:
    services = build_runtime_services(tmp_path)
    accepted_sidecar = {
        "title": "Auth Discovery",
        "status": "accepted",
        "readiness": "high",
        "readiness_rationale": "Framing is strong enough for Design.",
        "blocking_gaps": [],
        "problem_areas": [
            {
                "problem_area_id": "auth-session",
                "title": "Auth Session Boundaries",
                "confidence": "high",
                "source_section": "## Auth Session Boundaries",
                "assumptions": [],
            }
        ],
        "cross_cutting": {
            "global_constraints": ["Must preserve operator trust."],
            "shared_assumptions": [],
            "systemic_risks": ["Token leaks are costly."],
            "open_questions": [],
            "source_sections": ["## Cross-Cutting Constraints"],
        },
    }
    services.discovery.write(
        brief_id="disc-normal",
        markdown="# Accepted Discovery\n\nReady body.",
        sidecar=accepted_sidecar,
    )

    normal = services.discovery.to_design(brief_id="disc-normal")

    assert normal.result.ok is True
    assert normal.metadata["override"] is False
    assert normal.artifacts["design_handoff"]["recommended_focus"] == "Auth Session Boundaries"
    assert normal.artifacts["design_handoff"]["caution"] is None
    assert "design_start_context" not in normal.artifacts

    override_sidecar = dict(accepted_sidecar)
    override_sidecar["status"] = "draft"
    override_sidecar["readiness"] = "medium"
    override_sidecar["blocking_gaps"] = ["Revocation guarantees remain weak."]
    services.discovery.write(
        brief_id="disc-override",
        markdown="# Override Discovery\n\nProceed anyway.",
        sidecar=override_sidecar,
    )

    override = services.discovery.to_design(brief_id="disc-override", override=True)

    assert override.result.ok is True
    assert override.warnings
    assert override.metadata["override"] is True
    assert override.artifacts["design_handoff"]["caution"] == (
        "Revocation guarantees remain weak."
    )


def test_design_write_and_read_support_short_and_full_views(tmp_path: Path) -> None:
    services = build_runtime_services(tmp_path)
    sidecar = {
        "design_unit_id": "unit-auth-session",
        "title": "Auth Session Design",
        "status": "draft",
        "scope_summary": "Defines session issuance, invalidation, and consistency boundaries.",
        "depends_on": ["unit-auth-contract"],
        "children": ["unit-session-store"],
        "parent": None,
        "readiness": "medium",
        "readiness_rationale": "Main shape is clear but revocation guarantees still need tightening.",
        "open_questions": ["Should revocation be synchronous across all replicas?"],
        "assumptions": ["Audit events can be written asynchronously."],
    }

    services.design.write(
        unit_id="unit-auth-session",
        markdown="# Auth Session Design\n\nDraft design body.",
        sidecar=sidecar,
    )

    result = services.design.read(unit_id="unit-auth-session")

    assert result.result.ok is True
    assert result.artifacts["workflow_status"] == "draft"
    assert result.artifacts["scope_summary"] == sidecar["scope_summary"]
    assert result.artifacts["linkage"]["depends_on"] == ["unit-auth-contract"]
    assert result.artifacts["design_unit_id"] == "unit-auth-session"
    assert "markdown" not in result.artifacts
    assert "stage_metadata" not in result.artifacts


def test_design_read_can_load_specific_checkpoint(tmp_path: Path) -> None:
    services = build_runtime_services(tmp_path)
    first = services.design.write(
        unit_id="unit-auth-session",
        markdown="# Auth Session Design\n\nDraft body.",
        sidecar={
            "design_unit_id": "unit-auth-session",
            "title": "Auth Session Design",
            "status": "draft",
            "scope_summary": "Defines session issuance, invalidation, and consistency boundaries.",
            "depends_on": [],
            "children": [],
            "parent": None,
            "readiness": "medium",
            "readiness_rationale": "Main shape is clear but still evolving.",
            "open_questions": ["Should revocation be synchronous across all replicas?"],
            "assumptions": [],
        },
    )
    second = services.design.write(
        unit_id="unit-auth-session",
        markdown="# Auth Session Design\n\nRevised body.",
        sidecar={
            "design_unit_id": "unit-auth-session",
            "title": "Auth Session Design",
            "status": "draft",
            "scope_summary": "Defines session issuance, invalidation, and consistency boundaries.",
            "depends_on": [],
            "children": [],
            "parent": None,
            "readiness": "high",
            "readiness_rationale": "Main shape is now concrete enough to review.",
            "open_questions": [],
            "assumptions": [],
        },
    )

    historical = services.design.read(
        unit_id="unit-auth-session",
        checkpoint_id=first.metadata["checkpoint_id"],
        view="full",
    )
    current = services.design.read(unit_id="unit-auth-session", view="full")

    assert second.metadata["checkpoint_id"] != first.metadata["checkpoint_id"]
    assert historical.result.ok is True
    assert historical.artifacts["markdown"] == "# Auth Session Design\n\nDraft body."
    assert historical.artifacts["readiness"] == "medium"
    assert current.artifacts["markdown"] == "# Auth Session Design\n\nRevised body."
    assert current.artifacts["readiness"] == "high"


def test_design_accept_transitions_draft_to_accepted(tmp_path: Path) -> None:
    services = build_runtime_services(tmp_path)
    services.design.write(
        unit_id="unit-auth-session",
        markdown="# Auth Session Design\n\nAccepted from draft.",
        sidecar={
            "design_unit_id": "unit-auth-session",
            "title": "Auth Session Design",
            "status": "draft",
            "scope_summary": "Defines session issuance and revocation behavior.",
            "depends_on": [],
            "children": [],
            "parent": None,
            "readiness": "high",
            "readiness_rationale": "Concrete enough to accept directly.",
            "open_questions": [],
            "assumptions": [],
        },
    )

    result = services.design.accept(unit_id="unit-auth-session")
    current = services.design.read(unit_id="unit-auth-session")

    assert result.result.ok is True
    assert result.metadata["accepted_from_status"] == "draft"
    assert current.artifacts["workflow_status"] == "accepted"


def test_design_accept_is_idempotent_for_accepted_units(tmp_path: Path) -> None:
    services = build_runtime_services(tmp_path)
    base_sidecar = {
        "design_unit_id": "unit-auth-session",
        "title": "Auth Session Design",
        "status": "draft",
        "scope_summary": "Defines session issuance and revocation behavior.",
        "depends_on": [],
        "children": [],
        "parent": None,
        "readiness": "high",
        "readiness_rationale": "Main flow and failure handling are concrete enough to accept.",
        "open_questions": [],
        "assumptions": [],
    }

    services.design.write(
        unit_id="unit-accepted-path",
        markdown="# Auth Session Design\n\nAccepted path.",
        sidecar={**base_sidecar, "design_unit_id": "unit-accepted-path"},
    )
    first = services.design.accept(unit_id="unit-accepted-path")
    second = services.design.accept(unit_id="unit-accepted-path")

    assert first.result.ok is True
    assert first.metadata["accepted_from_status"] == "draft"
    assert second.result.ok is True
    assert second.metadata["status"] == "accepted"


def test_design_delete_removes_unit_from_read_and_list(tmp_path: Path) -> None:
    services = build_runtime_services(tmp_path)
    services.design.write(
        unit_id="unit-1",
        markdown="# Unit\n\nBody.",
        sidecar={
            "design_unit_id": "unit-1",
            "title": "Unit 1",
            "status": "draft",
            "scope_summary": "Test scope.",
            "readiness": "medium",
            "readiness_rationale": "Enough to persist.",
            "open_questions": [],
            "assumptions": [],
        },
    )

    deleted = services.design.delete(unit_id="unit-1")
    read = services.design.read(unit_id="unit-1")
    listed = services.design.list()

    assert deleted.result.ok is True
    assert deleted.metadata["deleted"] is True
    assert read.result.ok is False
    assert listed.artifacts["units"] == []


def test_design_list_returns_compact_unit_summaries_and_surfaces_malformed_units(tmp_path: Path) -> None:
    services = build_runtime_services(tmp_path)
    services.design.write(
        unit_id="healthy-unit",
        markdown="# Healthy Unit\n\nBody.",
        sidecar={
            "design_unit_id": "healthy-unit",
            "title": "Healthy Unit",
            "status": "draft",
            "scope_summary": "Well-formed unit.",
            "readiness": "high",
            "readiness_rationale": "The design is ready to accept.",
            "open_questions": [],
            "assumptions": [],
        },
    )
    services.store.write(
        key=ArtifactKey(stage=ArtifactStage.DESIGN, artifact_id="broken-unit"),
        markdown="# Broken Unit\n\nBody.",
        stage_metadata={
            "design_unit_id": "broken-unit",
            "status": "draft",
            "scope_summary": "Missing title and readiness.",
            "readiness_rationale": "Incomplete sidecar for coverage.",
            "open_questions": [],
            "assumptions": [],
        },
        flush_reason="checkpoint",
    )

    result = services.design.list()

    assert result.result.ok is True
    assert result.artifacts["count"] == 2
    assert [unit["unit_id"] for unit in result.artifacts["units"]] == ["broken-unit", "healthy-unit"]
    assert result.artifacts["units"][0]["malformed"] is True
    assert result.artifacts["units"][0]["title"] is None
    assert result.artifacts["units"][1]["status"] == "draft"
    assert result.warnings == ("design unit broken-unit is malformed: missing title, readiness",)


def test_design_reopen_after_acceptance_is_later_draft_checkpoint(tmp_path: Path) -> None:
    services = build_runtime_services(tmp_path)
    accepted_sidecar = {
        "design_unit_id": "unit-auth-session",
        "title": "Auth Session Design",
        "status": "draft",
        "scope_summary": "Defines session issuance and revocation behavior.",
        "depends_on": [],
        "children": [],
        "parent": None,
        "readiness": "high",
        "readiness_rationale": "Concrete enough to accept.",
        "open_questions": [],
        "assumptions": [],
    }

    services.design.write(
        unit_id="unit-auth-session",
        markdown="# Auth Session Design\n\nAccepted body.",
        sidecar=accepted_sidecar,
    )
    accepted = services.design.accept(unit_id="unit-auth-session")

    reopened = services.design.write(
        unit_id="unit-auth-session",
        markdown="# Auth Session Design\n\nReopened body.",
        sidecar={
            **accepted_sidecar,
            "status": "draft",
            "readiness": "medium",
            "readiness_rationale": "A new constraint requires revision before this is buildable again.",
            "open_questions": ["How should revocation lag be bounded?"],
        },
    )
    current = services.design.read(unit_id="unit-auth-session")

    assert reopened.result.ok is True
    assert reopened.metadata["version_id"] != accepted.metadata["version_id"]
    assert current.artifacts["workflow_status"] == "draft"
    assert current.artifacts["readiness"] == "medium"


def test_design_write_supports_metadata_only_delta_updates(tmp_path: Path) -> None:
    services = build_runtime_services(tmp_path)
    services.design.write(
        unit_id="unit-auth-session",
        markdown="# Auth Session Design\n\n## Tradeoffs\n\nInitial tradeoff text.",
        sidecar={
            "design_unit_id": "unit-auth-session",
            "title": "Auth Session Design",
            "status": "draft",
            "scope_summary": "Defines session issuance and revocation behavior.",
            "depends_on": [],
            "children": [],
            "parent": None,
            "readiness": "medium",
            "readiness_rationale": "Tradeoffs are visible but one open question remains.",
            "open_questions": ["Should revocation be synchronous?"],
            "assumptions": [],
        },
    )

    updated = services.design.write(
        unit_id="unit-auth-session",
        sidecar_patch={
            "readiness": "high",
            "readiness_rationale": "The remaining open question was resolved in review.",
            "open_questions": [],
        },
    )
    current = services.design.read(unit_id="unit-auth-session", view="full")

    assert updated.result.ok is True
    assert updated.metadata["base_checkpoint_id"]
    assert current.artifacts["readiness"] == "high"
    assert current.artifacts["open_questions"] == []
    assert current.artifacts["markdown"] == "# Auth Session Design\n\n## Tradeoffs\n\nInitial tradeoff text."


def test_design_write_supports_section_level_markdown_deltas(tmp_path: Path) -> None:
    services = build_runtime_services(tmp_path)
    initial = services.design.write(
        unit_id="unit-auth-session",
        markdown="# Auth Session Design\n\n## Main App\n\nOld text.\n\n## Tradeoffs\n\nInitial tradeoff text.",
        sidecar={
            "design_unit_id": "unit-auth-session",
            "title": "Auth Session Design",
            "status": "draft",
            "scope_summary": "Defines session issuance and revocation behavior.",
            "depends_on": [],
            "children": [],
            "parent": None,
            "readiness": "medium",
            "readiness_rationale": "Main shape is visible but tradeoffs need more detail.",
            "open_questions": ["Should revocation be synchronous?"],
            "assumptions": [],
        },
    )

    updated = services.design.write(
        unit_id="unit-auth-session",
        base_checkpoint_id=initial.metadata["checkpoint_id"],
        markdown_operations=[
            {"op": "replace_section", "heading": "Main App", "content": "New text."},
            {"op": "append_to_section", "heading": "Tradeoffs", "content": "Added detail."},
            {
                "op": "insert_section_after",
                "after_heading": "Tradeoffs",
                "heading_line": "## Open Questions",
                "content": "- None right now.",
            },
        ],
        sidecar_patch={
            "readiness": "high",
            "readiness_rationale": "The main sections are now concrete enough to review.",
            "open_questions": [],
        },
    )
    current = services.design.read(unit_id="unit-auth-session", view="full")

    assert updated.result.ok is True
    assert current.artifacts["readiness"] == "high"
    assert "## Main App\n\nNew text." in current.artifacts["markdown"]
    assert "## Tradeoffs\n\nInitial tradeoff text.\n\nAdded detail." in current.artifacts["markdown"]
    assert "## Open Questions\n\n- None right now." in current.artifacts["markdown"]


def test_design_write_rejects_stale_base_checkpoint_on_delta_update(tmp_path: Path) -> None:
    services = build_runtime_services(tmp_path)
    initial = services.design.write(
        unit_id="unit-auth-session",
        markdown="# Auth Session Design\n\nBody.",
        sidecar={
            "design_unit_id": "unit-auth-session",
            "title": "Auth Session Design",
            "status": "draft",
            "scope_summary": "Defines session issuance and revocation behavior.",
            "depends_on": [],
            "children": [],
            "parent": None,
            "readiness": "medium",
            "readiness_rationale": "Still drafting.",
            "open_questions": [],
            "assumptions": [],
        },
    )
    services.design.write(
        unit_id="unit-auth-session",
        sidecar_patch={"readiness_rationale": "New authoritative checkpoint."},
    )

    stale = services.design.write(
        unit_id="unit-auth-session",
        base_checkpoint_id=initial.metadata["checkpoint_id"],
        sidecar_patch={"readiness": "high"},
    )

    assert stale.result.ok is False
    assert "base checkpoint" in stale.result.message


def test_session_startup_view_returns_active_threads(tmp_path: Path) -> None:
    services = build_runtime_services(tmp_path)
    services.session_lifecycle.session_write_handoff(
        thread_id="thread-b",
        title="Second Thread",
        current_intent_summary="Still shaping the design runtime.",
        next_suggested_action="Decide whether to split review logic.",
        thread_markdown="# Thread B\n\nWorking notes.",
    )
    services.session_lifecycle.session_write_handoff(
        thread_id="thread-a",
        title="First Thread",
        current_intent_summary="Finishing session lifecycle implementation.",
        next_suggested_action="Verify archive semantics.",
        thread_markdown="# Thread A\n\nWorking notes.",
    )

    startup = services.session_lifecycle.session_read_startup_view()

    assert startup.result.ok is True
    assert startup.metadata["active_thread_count"] == 2
    thread_ids = {entry["thread_id"] for entry in startup.artifacts["active_threads"]}
    assert thread_ids == {"thread-a", "thread-b"}


def test_session_handoff_refreshes_startup_projection(tmp_path: Path) -> None:
    services = build_runtime_services(tmp_path)

    write = services.session_lifecycle.session_write_handoff(
        thread_id="thread-1",
        title="Implement Session Lifecycle",
        current_intent_summary="Add bounded recovery and archive enforcement.",
        next_suggested_action="Test startup rebuild and archive recovery paths.",
        thread_markdown="# Thread 1\n\nSession lifecycle work.",
    )
    startup = services.session_lifecycle.session_read_startup_view()

    assert write.result.ok is True
    assert write.metadata == {}
    assert startup.metadata["rebuilt"] is False
    assert startup.artifacts["active_threads"][0]["thread_id"] == "thread-1"


def test_session_archive_moves_thread_to_history_and_removes_active_state(tmp_path: Path) -> None:
    services = build_runtime_services(tmp_path)
    services.session_lifecycle.session_write_handoff(
        thread_id="thread-1",
        title="Implement Session Lifecycle",
        current_intent_summary="Add bounded recovery and archive enforcement.",
        next_suggested_action="Summarize completion and archive it.",
        thread_markdown="# Thread 1\n\nSession lifecycle work.",
    )

    archived = services.session_lifecycle.session_archive_thread(
        thread_id="thread-1",
        closure_summary="Session lifecycle runtime shipped with tests.",
    )
    startup = services.session_lifecycle.session_read_startup_view()
    active = services.session_lifecycle.session_read_thread(thread_id="thread-1")

    assert archived.result.ok is True
    assert archived.metadata == {}
    assert startup.artifacts["active_threads"] == []
    assert startup.artifacts["recent_completed_threads"][0]["thread_id"] == "thread-1"
    assert active.result.ok is False


def test_mcp_server_registers_flat_tool_surface(tmp_path: Path) -> None:
    server = create_server(tmp_path)

    tool_names = [tool.name for tool in server.list_tools()]

    assert tool_names == [
        "discovery_read",
        "discovery_write",
        "discovery_to_design",
        "discovery_delete",
        "design_read",
        "design_list",
        "design_write",
        "design_accept",
        "design_delete",
        "session_read_startup_view",
        "session_read_thread",
        "session_write_handoff",
        "session_archive_thread",
    ]
    assert server.list_tools()[0].input_schema["required"] == ["brief_id"]


def test_mcp_result_mapping_uses_shared_success_warning_failure_statuses() -> None:
    success = map_runtime_result(
        ArtifactRuntimeResult(
            result=OperationResult(status=OperationStatus.OK, message="ok"),
            artifacts={"value": "x"},
            metadata={"count": 1},
        )
    )
    warning = map_runtime_result(
        ArtifactRuntimeResult(
            result=OperationResult(status=OperationStatus.WARNING, message="warning"),
            warnings=("projection_stale",),
        )
    )
    failure = map_runtime_result(
        ArtifactRuntimeResult(
            result=OperationResult(status=OperationStatus.ERROR, message="error"),
        )
    )

    assert success["result"] == "success"
    assert success["artifacts"]["value"] == "x"
    assert success["metadata"]["count"] == 1
    assert warning["result"] == "warning"
    assert warning["warnings"] == ["projection_stale"]
    assert failure["result"] == "failure"
    assert "warnings" not in success
    assert "artifacts" not in warning
    assert "metadata" not in failure


def test_mcp_discovery_write_and_read_flow_returns_shared_shape(tmp_path: Path) -> None:
    server = create_server(tmp_path)
    sidecar = {
        "title": "Auth Discovery",
        "status": "draft",
        "readiness": "medium",
        "readiness_rationale": "Main framing is visible but one assumption still needs validation.",
        "blocking_gaps": ["Revocation semantics are still open."],
        "problem_areas": [
            {
                "problem_area_id": "auth-session",
                "title": "Auth Session Boundaries",
                "confidence": "medium",
                "source_section": "## Auth Session Boundaries",
                "assumptions": [],
            }
        ],
        "cross_cutting": {
            "global_constraints": [],
            "shared_assumptions": [],
            "systemic_risks": [],
            "open_questions": [],
            "source_sections": ["## Cross-Cutting Constraints"],
        },
    }

    write = server.call_tool(
        "discovery_write",
        {
            "brief_id": "disc-1",
            "markdown": "# Auth Discovery\n\nDraft body.",
            "sidecar": sidecar,
        },
    )
    read = server.call_tool(
        "discovery_read",
        {
            "brief_id": "disc-1",
        },
    )

    assert write["result"] == "success"
    assert write == {"result": "success"}
    assert read["result"] == "success"
    assert read["artifacts"]["status"] == "draft"
    assert read["artifacts"]["readiness"] == "medium"
    assert "markdown" not in read["artifacts"]


def test_mcp_discovery_to_design_returns_compact_handoff_shape(tmp_path: Path) -> None:
    server = create_server(tmp_path)
    sidecar = {
        "title": "Auth Discovery",
        "status": "accepted",
        "readiness": "high",
        "readiness_rationale": "Framing is strong enough for Design.",
        "blocking_gaps": [],
        "problem_areas": [
            {
                "problem_area_id": "auth-session",
                "title": "Auth Session Boundaries",
                "confidence": "high",
                "source_section": "## Auth Session Boundaries",
                "assumptions": [],
            }
        ],
        "cross_cutting": {
            "global_constraints": ["Must preserve operator trust."],
            "shared_assumptions": [],
            "systemic_risks": ["Token leaks are costly."],
            "open_questions": [],
            "source_sections": ["## Cross-Cutting Constraints"],
        },
    }

    server.call_tool(
        "discovery_write",
        {
            "brief_id": "disc-1",
            "markdown": "# Accepted Discovery\n\nReady body.",
            "sidecar": sidecar,
        },
    )
    handoff = server.call_tool("discovery_to_design", {"brief_id": "disc-1"})

    assert handoff == {"result": "success"}


def test_mcp_discovery_delete_removes_runtime_state(tmp_path: Path) -> None:
    server = create_server(tmp_path)
    server.call_tool(
        "discovery_write",
        {
            "brief_id": "disc-1",
            "markdown": "# Discovery\n\nBody.",
            "sidecar": {
                "title": "Auth Discovery",
                "status": "draft",
                "readiness": "medium",
                "readiness_rationale": "Enough to persist.",
                "blocking_gaps": [],
                "problem_areas": [
                    {
                        "problem_area_id": "auth-session",
                        "title": "Auth Session Boundaries",
                        "confidence": "medium",
                        "source_section": "## Auth Session Boundaries",
                        "assumptions": [],
                    }
                ],
                "cross_cutting": {
                    "global_constraints": [],
                    "shared_assumptions": [],
                    "systemic_risks": [],
                    "open_questions": [],
                    "source_sections": [],
                },
            },
        },
    )

    deleted = server.call_tool("discovery_delete", {"brief_id": "disc-1"})
    missing = server.call_tool("discovery_read", {"brief_id": "disc-1"})

    assert deleted == {"result": "success"}
    assert missing["result"] == "failure"


def test_mcp_design_read_can_load_specific_checkpoint(tmp_path: Path) -> None:
    server = create_server(tmp_path)
    server.call_tool(
        "design_write",
        {
            "unit_id": "unit-1",
            "markdown": "# Design\n\nDraft body.",
            "sidecar": {
                "design_unit_id": "unit-1",
                "title": "Design",
                "status": "draft",
                "scope_summary": "Scope summary.",
                "readiness": "medium",
                "readiness_rationale": "Still evolving.",
                "open_questions": ["One question"],
                "assumptions": [],
            },
        },
    )
    first = server.call_tool("design_read", {"unit_id": "unit-1"})
    server.call_tool(
        "design_write",
        {
            "unit_id": "unit-1",
            "markdown": "# Design\n\nRevised body.",
            "sidecar": {
                "design_unit_id": "unit-1",
                "title": "Design",
                "status": "draft",
                "scope_summary": "Scope summary.",
                "readiness": "high",
                "readiness_rationale": "Concrete enough to review.",
                "open_questions": [],
                "assumptions": [],
            },
        },
    )

    historical = server.call_tool(
        "design_read",
        {
            "unit_id": "unit-1",
            "checkpoint_id": first["metadata"]["checkpoint_id"],
            "view": "full",
        },
    )

    assert historical["result"] == "success"
    assert historical["artifacts"]["markdown"] == "# Design\n\nDraft body."
    assert historical["artifacts"]["readiness"] == "medium"


def test_mcp_design_list_returns_units_and_warnings(tmp_path: Path) -> None:
    server = create_server(tmp_path)
    server.call_tool(
        "design_write",
        {
            "unit_id": "healthy-unit",
            "markdown": "# Healthy Unit\n\nBody.",
            "sidecar": {
                "design_unit_id": "healthy-unit",
                "title": "Healthy Unit",
                "status": "draft",
                "scope_summary": "Well-formed unit.",
                "readiness": "medium",
                "readiness_rationale": "Still one review pass away.",
                "open_questions": [],
                "assumptions": [],
            },
        },
    )
    server.services.store.write(
        key=ArtifactKey(stage=ArtifactStage.DESIGN, artifact_id="broken-unit"),
        markdown="# Broken Unit\n\nBody.",
        stage_metadata={
            "design_unit_id": "broken-unit",
            "status": "draft",
            "scope_summary": "Missing title and readiness.",
            "readiness_rationale": "Incomplete sidecar for coverage.",
            "open_questions": [],
            "assumptions": [],
        },
        flush_reason="checkpoint",
    )

    result = server.call_tool("design_list")

    assert result["result"] == "success"
    assert result["artifacts"]["count"] == 2
    assert result["artifacts"]["units"][0]["unit_id"] == "broken-unit"
    assert result["artifacts"]["units"][0]["malformed"] is True
    assert result["warnings"] == ["design unit broken-unit is malformed: missing title, readiness"]


def test_mcp_design_delete_removes_unit_and_returns_warning_when_missing(tmp_path: Path) -> None:
    server = create_server(tmp_path)
    server.call_tool(
        "design_write",
        {
            "unit_id": "unit-1",
            "markdown": "# Unit\n\nBody.",
            "sidecar": {
                "design_unit_id": "unit-1",
                "title": "Unit 1",
                "status": "draft",
                "scope_summary": "Test scope.",
                "readiness": "medium",
                "readiness_rationale": "Enough to persist.",
                "open_questions": [],
                "assumptions": [],
            },
        },
    )

    deleted = server.call_tool("design_delete", {"unit_id": "unit-1"})
    listed = server.call_tool("design_list")
    repeat = server.call_tool("design_delete", {"unit_id": "unit-1"})

    assert deleted == {"result": "success"}
    assert listed["artifacts"]["units"] == []
    assert repeat["result"] == "warning"
    assert repeat["warnings"] == ["artifact_not_found"]


def test_mcp_design_write_supports_delta_updates(tmp_path: Path) -> None:
    server = create_server(tmp_path)
    server.call_tool(
        "design_write",
        {
            "unit_id": "unit-auth-session",
            "markdown": "# Auth Session Design\n\n## Tradeoffs\n\nInitial tradeoff text.",
            "sidecar": {
                "design_unit_id": "unit-auth-session",
                "title": "Auth Session Design",
                "status": "draft",
                "scope_summary": "Defines session issuance and revocation behavior.",
                "readiness": "medium",
                "readiness_rationale": "One open question remains.",
                "open_questions": ["Should revocation be synchronous?"],
                "assumptions": [],
            },
        },
    )
    initial = server.call_tool("design_read", {"unit_id": "unit-auth-session"})

    updated = server.call_tool(
        "design_write",
        {
            "unit_id": "unit-auth-session",
            "base_checkpoint_id": initial["metadata"]["checkpoint_id"],
            "markdown_operations": [
                {"op": "append_to_section", "heading": "Tradeoffs", "content": "Added detail."}
            ],
            "sidecar_patch": {
                "readiness": "high",
                "readiness_rationale": "The tradeoff is now settled.",
                "open_questions": [],
            },
        },
    )
    read = server.call_tool(
        "design_read",
        {"unit_id": "unit-auth-session", "view": "full"},
    )

    assert updated == {"result": "success"}
    assert read["artifacts"]["readiness"] == "high"
    assert "Added detail." in read["artifacts"]["markdown"]


def test_design_write_tool_schema_guides_delta_updates(tmp_path: Path) -> None:
    server = create_server(tmp_path)
    tool = next(tool for tool in server.list_tools() if tool.name == "design_write")
    schema = tool.input_schema
    sidecar_patch = schema["properties"]["sidecar_patch"]
    markdown_operations = schema["properties"]["markdown_operations"]

    assert "Partial sidecar update" in sidecar_patch["description"]
    assert sidecar_patch["additionalProperties"] is False
    assert "readiness" in sidecar_patch["properties"]
    assert "open_questions" in sidecar_patch["properties"]
    assert "Checkpoint-relative markdown deltas" in markdown_operations["description"]
    assert markdown_operations["items"]["properties"]["op"]["enum"] == [
        "replace_section",
        "append_to_section",
        "insert_section_after",
    ]


def test_mcp_session_lifecycle_path_reads_compact_startup_and_full_thread(tmp_path: Path) -> None:
    server = create_server(tmp_path)

    handoff = server.call_tool(
        "session_write_handoff",
        {
            "thread_id": "thread-1",
            "title": "Implement MCP Adapter",
            "current_intent_summary": "Wire thin handlers over runtime services.",
            "next_suggested_action": "Add lifecycle coverage after the read path works.",
            "thread_markdown": "# Thread 1\n\nMCP adapter work.",
        },
    )
    startup = server.call_tool("session_read_startup_view")
    active = server.call_tool("session_read_thread", {"thread_id": "thread-1"})

    assert handoff["result"] == "success"
    assert handoff == {"result": "success"}
    assert startup["result"] == "success"
    assert startup["artifacts"]["active_threads"][0] == {
        "thread_id": "thread-1",
        "title": "Implement MCP Adapter",
    }
    assert "thread_markdown" not in startup["artifacts"]
    assert active["result"] == "success"
    assert active["artifacts"]["thread_markdown"] == "# Thread 1\n\nMCP adapter work."
    assert active["metadata"]["thread_id"] == "thread-1"


def test_mcp_non_read_tools_stay_compact_even_with_large_artifact_bodies(tmp_path: Path) -> None:
    server = create_server(tmp_path)
    discovery_sidecar = {
        "title": "Auth Discovery",
        "status": "accepted",
        "readiness": "high",
        "readiness_rationale": "Framing is strong enough for Design.",
        "blocking_gaps": [],
        "problem_areas": [
            {
                "problem_area_id": "auth-session",
                "title": "Auth Session Boundaries",
                "confidence": "high",
                "source_section": "## Auth Session Boundaries",
                "assumptions": [],
            }
        ],
        "cross_cutting": {
            "global_constraints": ["Must preserve operator trust."],
            "shared_assumptions": [],
            "systemic_risks": ["Token leaks are costly."],
            "open_questions": [],
            "source_sections": ["## Cross-Cutting Constraints"],
        },
    }
    design_sidecar = {
        "design_unit_id": "unit-1",
        "title": "Design",
        "status": "draft",
        "scope_summary": "Scope summary.",
        "readiness": "medium",
        "readiness_rationale": "Still evolving.",
        "open_questions": ["One question"],
        "assumptions": [],
    }

    discovery_write = server.call_tool(
        "discovery_write",
        {"brief_id": "disc-1", "markdown": LARGE_BODY, "sidecar": discovery_sidecar},
    )
    discovery_handoff = server.call_tool("discovery_to_design", {"brief_id": "disc-1"})
    design_write = server.call_tool(
        "design_write",
        {"unit_id": "unit-1", "markdown": LARGE_BODY, "sidecar": design_sidecar},
    )
    design_list = server.call_tool("design_list")
    design_accept = server.call_tool("design_accept", {"unit_id": "unit-1"})
    session_write = server.call_tool(
        "session_write_handoff",
        {
            "thread_id": "thread-1",
            "title": "Large Thread",
            "current_intent_summary": "Keep the response compact.",
            "next_suggested_action": "Read the thread only when explicitly requested.",
            "thread_markdown": LARGE_BODY,
        },
    )
    startup_view = server.call_tool("session_read_startup_view")
    session_archive = server.call_tool(
        "session_archive_thread",
        {"thread_id": "thread-1", "closure_summary": "Archived."},
    )

    compact_results = {
        "discovery_write": discovery_write,
        "discovery_to_design": discovery_handoff,
        "discovery_delete": server.call_tool("discovery_delete", {"brief_id": "disc-1"}),
        "design_write": design_write,
        "design_list": design_list,
        "design_accept": design_accept,
        "design_delete": server.call_tool("design_delete", {"unit_id": "unit-1"}),
        "session_read_startup_view": startup_view,
        "session_write_handoff": session_write,
        "session_archive_thread": session_archive,
    }

    for tool_name, result in compact_results.items():
        assert _payload_size_bytes(result) < COMPACT_MCP_BUDGET_BYTES, f"{tool_name} response is too large"
        encoded = json.dumps(result)
        assert LARGE_BODY not in encoded, f"{tool_name} leaked full artifact body into the response"
        assert "\"markdown\"" not in encoded, f"{tool_name} should not expose markdown bodies"
        assert "\"thread_markdown\"" not in encoded, f"{tool_name} should not expose thread markdown bodies"


def test_mcp_explicit_read_tools_are_the_only_large_payload_path(tmp_path: Path) -> None:
    server = create_server(tmp_path)
    server.call_tool(
        "discovery_write",
        {
            "brief_id": "disc-1",
            "markdown": LARGE_BODY,
            "sidecar": {
                "title": "Auth Discovery",
                "status": "accepted",
                "readiness": "high",
                "readiness_rationale": "Framing is strong enough for Design.",
                "blocking_gaps": [],
                "problem_areas": [
                    {
                        "problem_area_id": "auth-session",
                        "title": "Auth Session Boundaries",
                        "confidence": "high",
                        "source_section": "## Auth Session Boundaries",
                        "assumptions": [],
                    }
                ],
                "cross_cutting": {
                    "global_constraints": [],
                    "shared_assumptions": [],
                    "systemic_risks": [],
                    "open_questions": [],
                    "source_sections": ["## Cross-Cutting Constraints"],
                },
            },
        },
    )
    server.call_tool(
        "design_write",
        {
            "unit_id": "unit-1",
            "markdown": LARGE_BODY,
            "sidecar": {
                "design_unit_id": "unit-1",
                "title": "Design",
                "status": "draft",
                "scope_summary": "Scope summary.",
                "readiness": "medium",
                "readiness_rationale": "Still evolving.",
                "open_questions": [],
                "assumptions": [],
            },
        },
    )
    server.call_tool(
        "session_write_handoff",
        {
            "thread_id": "thread-1",
            "title": "Large Thread",
            "current_intent_summary": "Keep the response compact.",
            "next_suggested_action": "Read the thread only when explicitly requested.",
            "thread_markdown": LARGE_BODY,
        },
    )

    discovery_short = server.call_tool("discovery_read", {"brief_id": "disc-1"})
    discovery_full = server.call_tool("discovery_read", {"brief_id": "disc-1", "view": "full"})
    design_short = server.call_tool("design_read", {"unit_id": "unit-1"})
    design_full = server.call_tool("design_read", {"unit_id": "unit-1", "view": "full"})
    thread_full = server.call_tool("session_read_thread", {"thread_id": "thread-1"})

    assert _payload_size_bytes(discovery_short) < COMPACT_MCP_BUDGET_BYTES
    assert "markdown" not in discovery_short["artifacts"]
    assert _payload_size_bytes(design_short) < COMPACT_MCP_BUDGET_BYTES
    assert "markdown" not in design_short["artifacts"]

    assert _payload_size_bytes(discovery_full) > 5000
    assert discovery_full["artifacts"]["markdown"] == LARGE_BODY
    assert _payload_size_bytes(design_full) > 5000
    assert design_full["artifacts"]["markdown"] == LARGE_BODY
    assert _payload_size_bytes(thread_full) > 5000
    assert thread_full["artifacts"]["thread_markdown"] == LARGE_BODY


def test_mcp_validation_failure_stays_at_adapter_boundary(tmp_path: Path) -> None:
    server = create_server(tmp_path)

    result = server.call_tool("design_read", {"unit_id": "unit-1", "view": "wide"})

    assert result["result"] == "failure"
    assert result["warnings"] == ["invalid_input"]
    assert "view must be 'short' or 'full'" in result["metadata"]["message"]


def test_stdio_mcp_server_supports_initialize_list_and_tool_calls(tmp_path: Path) -> None:
    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "clauderfall.mcp.stdio",
            "--repo-root",
            str(tmp_path),
        ],
        cwd=str(REPO_ROOT),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    try:
        init = _stdio_request(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-06-18",
                    "capabilities": {},
                    "clientInfo": {"name": "pytest", "version": "0"},
                },
            },
        )
        assert init["result"]["protocolVersion"] == "2025-06-18"
        assert init["result"]["capabilities"]["tools"]["listChanged"] is False

        _stdio_notify(proc, {"jsonrpc": "2.0", "method": "notifications/initialized"})

        tools = _stdio_request(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {},
            },
        )
        tool_names = [tool["name"] for tool in tools["result"]["tools"]]
        assert "discovery_write" in tool_names
        assert "session_write_handoff" in tool_names

        discovery_write = _stdio_request(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "discovery_write",
                    "arguments": {
                        "brief_id": "disc-1",
                        "markdown": "# Auth Discovery\n\nDraft body.",
                        "sidecar": {
                            "title": "Auth Discovery",
                            "status": "draft",
                            "readiness": "medium",
                            "readiness_rationale": "Main framing is visible but one assumption remains open.",
                            "blocking_gaps": ["Revocation semantics are still open."],
                            "problem_areas": [
                                {
                                    "problem_area_id": "auth-session",
                                    "title": "Auth Session Boundaries",
                                    "confidence": "medium",
                                    "source_section": "## Auth Session Boundaries",
                                    "assumptions": [],
                                }
                            ],
                            "cross_cutting": {
                                "global_constraints": [],
                                "shared_assumptions": [],
                                "systemic_risks": [],
                                "open_questions": [],
                                "source_sections": ["## Cross-Cutting Constraints"],
                            },
                        },
                    },
                },
            },
        )
        assert discovery_write["result"]["isError"] is False
        assert discovery_write["result"]["structuredContent"] == {"result": "success"}

        startup_write = _stdio_request(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "session_write_handoff",
                    "arguments": {
                        "thread_id": "thread-1",
                        "title": "Implement MCP Adapter",
                        "current_intent_summary": "Wire thin handlers over runtime services.",
                        "next_suggested_action": "Verify stdio round trips.",
                        "thread_markdown": "# Thread 1\n\nMCP adapter work.",
                    },
                },
            },
        )
        assert startup_write["result"]["structuredContent"] == {"result": "success"}

        startup_read = _stdio_request(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 5,
                "method": "tools/call",
                "params": {
                    "name": "session_read_startup_view",
                    "arguments": {},
                },
            },
        )
        active_threads = startup_read["result"]["structuredContent"]["artifacts"]["active_threads"]
        assert active_threads[0] == {"thread_id": "thread-1", "title": "Implement MCP Adapter"}

        invalid_read = _stdio_request(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 6,
                "method": "tools/call",
                "params": {
                    "name": "design_read",
                    "arguments": {"unit_id": "unit-1", "view": "wide"},
                },
            },
        )
        assert invalid_read["result"]["isError"] is True
        assert invalid_read["result"]["structuredContent"]["warnings"] == ["invalid_input"]
    finally:
        if proc.stdin is not None:
            proc.stdin.close()
        proc.terminate()
        proc.wait(timeout=5)


def test_stdio_mcp_server_defaults_to_docs_root_and_supports_custom_docs_root(tmp_path: Path) -> None:
    default_proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "clauderfall.mcp.stdio",
            "--repo-root",
            str(tmp_path),
        ],
        cwd=str(REPO_ROOT),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    try:
        _stdio_request(
            default_proc,
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-06-18",
                    "capabilities": {},
                    "clientInfo": {"name": "pytest", "version": "0"},
                },
            },
        )
        _stdio_notify(default_proc, {"jsonrpc": "2.0", "method": "notifications/initialized"})
        _stdio_request(
            default_proc,
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "session_write_handoff",
                    "arguments": {
                        "thread_id": "thread-default-docs",
                        "title": "Default Docs Root",
                        "current_intent_summary": "Write into docs by default.",
                        "next_suggested_action": "Verify default path.",
                        "thread_markdown": "# Default Docs Root\n\nStored under docs.",
                    },
                },
            },
        )
    finally:
        if default_proc.stdin is not None:
            default_proc.stdin.close()
        default_proc.terminate()
        default_proc.wait(timeout=5)

    # Session threads are now in SQLite only — no markdown files
    assert (tmp_path / "clauderfall.db").exists()
    assert not (tmp_path / "session").exists()

    docs_root = tmp_path / "docs" / "clauderfall"
    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "clauderfall.mcp.stdio",
            "--repo-root",
            str(tmp_path),
            "--docs-root",
            str(docs_root),
        ],
        cwd=str(REPO_ROOT),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    try:
        _stdio_request(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-06-18",
                    "capabilities": {},
                    "clientInfo": {"name": "pytest", "version": "0"},
                },
            },
        )
        _stdio_notify(proc, {"jsonrpc": "2.0", "method": "notifications/initialized"})
        _stdio_request(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "session_write_handoff",
                    "arguments": {
                        "thread_id": "thread-custom-root",
                        "title": "Custom Root",
                        "current_intent_summary": "Write into docs/clauderfall instead of repo root.",
                        "next_suggested_action": "Verify artifact paths.",
                        "thread_markdown": "# Custom Root\n\nStored under docs.",
                    },
                },
            },
        )
    finally:
        if proc.stdin is not None:
            proc.stdin.close()
        proc.terminate()
        proc.wait(timeout=5)

    # Session threads are in SQLite — verify DB exists at repo root
    assert (tmp_path / "clauderfall.db").exists()


def _stdio_request(proc: subprocess.Popen[str], message: dict[str, object]) -> dict[str, object]:
    assert proc.stdin is not None
    assert proc.stdout is not None
    proc.stdin.write(json.dumps(message) + "\n")
    proc.stdin.flush()
    line = proc.stdout.readline()
    assert line, proc.stderr.read() if proc.stderr is not None else "missing stdio response"
    return json.loads(line)


def _stdio_notify(proc: subprocess.Popen[str], message: dict[str, object]) -> None:
    assert proc.stdin is not None
    proc.stdin.write(json.dumps(message) + "\n")
    proc.stdin.flush()
