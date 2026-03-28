from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from clauderfall.mcp import create_server, map_runtime_result
from clauderfall.runtime import (
    ArtifactKey,
    ArtifactPair,
    ArtifactRef,
    ArtifactRuntimeResult,
    ArtifactResolver,
    ArtifactStage,
    ArtifactView,
    CheckpointEnvelope,
    CheckpointManager,
    FlushReason,
    OperationResult,
    OperationStatus,
    build_runtime_services,
)


def test_artifact_resolver_matches_current_and_checkpoint_layout(tmp_path: Path) -> None:
    resolver = ArtifactResolver(root=tmp_path)
    ref = ArtifactRef(
        key=ArtifactKey(stage=ArtifactStage.DISCOVERY, artifact_id="brief-1"),
        checkpoint_id="chk-123",
    )

    resolved = resolver.resolve(ref)

    assert resolved.artifact_root == tmp_path / "discovery" / "brief-1"
    assert resolved.current_markdown_path == tmp_path / "discovery" / "brief-1" / "current" / "artifact.md"
    assert (
        resolved.checkpoint_metadata_path
        == tmp_path / "discovery" / "brief-1" / "checkpoints" / "chk-123" / "artifact.meta.yaml"
    )


def test_checkpoint_manager_builds_envelope_with_controlled_reason() -> None:
    manager = CheckpointManager()

    envelope = manager.build_envelope(
        artifact_id="unit-7",
        flush_reason=FlushReason.REVIEW_TRANSITION,
        stage_metadata={"status": "in_review"},
    )

    assert envelope.artifact_id == "unit-7"
    assert envelope.flush_reason == FlushReason.REVIEW_TRANSITION
    assert envelope.is_current is True
    assert envelope.stage_metadata == {"status": "in_review"}
    assert envelope.checkpoint_id


def test_artifact_store_round_trips_checkpoint_and_current_pair(tmp_path: Path) -> None:
    services = build_runtime_services(tmp_path)
    key = ArtifactKey(stage=ArtifactStage.DESIGN, artifact_id="auth-session")
    checkpoint_id = "chk-auth-001"
    envelope = CheckpointEnvelope.create(
        artifact_id=key.artifact_id,
        checkpoint_id=checkpoint_id,
        flush_reason=FlushReason.CHECKPOINT,
        stage_metadata={
            "status": "draft",
            "readiness": {"state": "not_ready", "blocking_gaps": ["Need invariant coverage"]},
        },
    )
    pair = ArtifactPair(markdown="# Auth Session\n\nDraft design unit.", metadata=envelope)
    ref = ArtifactRef(key=key, checkpoint_id=checkpoint_id)

    services.store.write_checkpoint(ref, pair)

    current = services.store.load_current(ArtifactRef(key=key))
    checkpoint = services.store.load_checkpoint(ref)

    assert current == pair
    assert checkpoint == pair


def test_runtime_services_wiring_exposes_shared_substrate_components(tmp_path: Path) -> None:
    services = build_runtime_services(tmp_path)

    assert services.root == tmp_path
    assert services.store.resolver is services.resolver
    assert services.artifacts.store is services.store
    assert services.discovery.artifacts is services.artifacts
    assert services.design.artifacts is services.artifacts
    assert services.session_lifecycle.artifacts is services.artifacts


def test_operation_result_ok_tracks_non_error_status() -> None:
    warning = OperationResult(
        status=OperationStatus.WARNING,
        message="completed with warnings",
        warnings=("current projection refreshed",),
    )
    error = OperationResult(status=OperationStatus.ERROR, message="checkpoint write failed")

    assert warning.ok is True
    assert error.ok is False


def test_shared_artifact_runtime_reads_short_and_full_views(tmp_path: Path) -> None:
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

    short_result = services.artifacts.read_artifact(key=key, view=ArtifactView.SHORT)
    full_result = services.artifacts.read_artifact(
        key=key,
        checkpoint_id=write_result.metadata["checkpoint_id"],
        view=ArtifactView.FULL,
    )

    assert short_result.result.ok is True
    assert short_result.artifacts["artifact_id"] == "brief-1"
    assert "markdown" not in short_result.artifacts
    assert full_result.artifacts["markdown"] == "# Discovery Brief\n\nBody text."
    assert full_result.artifacts["title"] == "Discovery Brief"


def test_shared_artifact_runtime_transition_writes_later_checkpoint_for_reopen(tmp_path: Path) -> None:
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

    current = services.artifacts.read_artifact(key=key, view=ArtifactView.FULL)
    original_checkpoint = services.store.load_checkpoint(
        ArtifactRef(key=key, checkpoint_id=initial.metadata["checkpoint_id"])
    )

    assert reopened.result.ok is True
    assert reopened.metadata["previous_checkpoint_id"] == initial.metadata["checkpoint_id"]
    assert reopened.metadata["checkpoint_id"] != initial.metadata["checkpoint_id"]
    assert current.artifacts["status"] == "draft"
    assert current.artifacts["stage_metadata"]["reopen_reason"] == "new constraint found"
    assert original_checkpoint is not None
    assert original_checkpoint.metadata.stage_metadata["status"] == "accepted"


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

    services.discovery.write_draft(
        brief_id="disc-1",
        markdown="# Auth Discovery\n\nDraft brief body.",
        sidecar=sidecar,
    )

    short_view = services.discovery.read(brief_id="disc-1", view=ArtifactView.SHORT)
    full_view = services.discovery.read(brief_id="disc-1", view=ArtifactView.FULL)

    assert short_view.result.ok is True
    assert short_view.artifacts["status"] == "draft"
    assert short_view.artifacts["readiness"] == "medium"
    assert "markdown" not in short_view.artifacts
    assert full_view.artifacts["markdown"] == "# Auth Discovery\n\nDraft brief body."


def test_discovery_to_design_blocks_without_acceptance_or_override(tmp_path: Path) -> None:
    services = build_runtime_services(tmp_path)
    services.discovery.write_draft(
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
    services.discovery.write_draft(
        brief_id="disc-normal",
        markdown="# Accepted Discovery\n\nReady body.",
        sidecar=accepted_sidecar,
    )

    normal = services.discovery.to_design(brief_id="disc-normal")

    assert normal.result.ok is True
    assert normal.metadata["override"] is False
    assert normal.artifacts["design_start_context"]["design_start_recommendation"]["caution"] is None

    override_sidecar = dict(accepted_sidecar)
    override_sidecar["status"] = "draft"
    override_sidecar["readiness"] = "medium"
    override_sidecar["blocking_gaps"] = ["Revocation guarantees remain weak."]
    services.discovery.write_draft(
        brief_id="disc-override",
        markdown="# Override Discovery\n\nProceed anyway.",
        sidecar=override_sidecar,
    )

    override = services.discovery.to_design(brief_id="disc-override", override=True)

    assert override.result.ok is True
    assert override.warnings
    assert override.metadata["override"] is True
    assert override.artifacts["design_start_context"]["design_start_recommendation"]["caution"] == (
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

    services.design.write_draft(
        unit_id="unit-auth-session",
        markdown="# Auth Session Design\n\nDraft design body.",
        sidecar=sidecar,
    )

    short_view = services.design.read(unit_id="unit-auth-session", view=ArtifactView.SHORT)
    full_view = services.design.read(unit_id="unit-auth-session", view=ArtifactView.FULL)

    assert short_view.result.ok is True
    assert short_view.artifacts["workflow_status"] == "draft"
    assert short_view.artifacts["scope_summary"] == sidecar["scope_summary"]
    assert short_view.artifacts["linkage"]["depends_on"] == ["unit-auth-contract"]
    assert "markdown" not in short_view.artifacts
    assert full_view.artifacts["markdown"] == "# Auth Session Design\n\nDraft design body."
    assert full_view.artifacts["stage_metadata"]["design_unit_id"] == "unit-auth-session"


def test_design_to_review_requires_persisted_valid_draft_and_writes_review_checkpoint(tmp_path: Path) -> None:
    services = build_runtime_services(tmp_path)
    services.design.write_draft(
        unit_id="unit-auth-session",
        markdown="# Auth Session Design\n\nReady for review.",
        sidecar={
            "design_unit_id": "unit-auth-session",
            "title": "Auth Session Design",
            "status": "draft",
            "scope_summary": "Defines session issuance and revocation behavior.",
            "depends_on": [],
            "children": [],
            "parent": None,
            "readiness": "high",
            "readiness_rationale": "Main flow and failure handling are concrete enough to review.",
            "open_questions": [],
            "assumptions": [],
        },
    )

    result = services.design.to_review(unit_id="unit-auth-session")
    current = services.design.read(unit_id="unit-auth-session", view=ArtifactView.FULL)

    assert result.result.ok is True
    assert result.metadata["previous_checkpoint_id"] != result.metadata["checkpoint_id"]
    assert current.artifacts["workflow_status"] == "in_review"
    assert current.artifacts["stage_metadata"]["status"] == "in_review"


def test_design_accept_requires_review_without_override(tmp_path: Path) -> None:
    services = build_runtime_services(tmp_path)
    services.design.write_draft(
        unit_id="unit-auth-session",
        markdown="# Auth Session Design\n\nStill draft.",
        sidecar={
            "design_unit_id": "unit-auth-session",
            "title": "Auth Session Design",
            "status": "draft",
            "scope_summary": "Defines session issuance and revocation behavior.",
            "depends_on": [],
            "children": [],
            "parent": None,
            "readiness": "high",
            "readiness_rationale": "Concrete enough to build, but not yet formally reviewed.",
            "open_questions": [],
            "assumptions": [],
        },
    )

    result = services.design.accept(unit_id="unit-auth-session")

    assert result.result.ok is False
    assert "in_review" in result.result.message


def test_design_accept_supports_review_and_explicit_draft_override(tmp_path: Path) -> None:
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

    services.design.write_draft(
        unit_id="unit-review-path",
        markdown="# Auth Session Design\n\nReview path.",
        sidecar={**base_sidecar, "design_unit_id": "unit-review-path"},
    )
    services.design.to_review(unit_id="unit-review-path")
    normal = services.design.accept(unit_id="unit-review-path")

    assert normal.result.ok is True
    assert normal.metadata["override"] is False
    assert normal.metadata["accepted_from_status"] == "in_review"

    services.design.write_draft(
        unit_id="unit-override-path",
        markdown="# Auth Session Design\n\nOverride path.",
        sidecar={**base_sidecar, "design_unit_id": "unit-override-path"},
    )
    override = services.design.accept(unit_id="unit-override-path", override=True)

    assert override.result.ok is True
    assert override.metadata["override"] is True
    assert override.metadata["accepted_from_status"] == "draft"
    assert override.warnings == ("Design acceptance proceeded from draft via explicit override.",)


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

    services.design.write_draft(
        unit_id="unit-auth-session",
        markdown="# Auth Session Design\n\nAccepted body.",
        sidecar=accepted_sidecar,
    )
    services.design.to_review(unit_id="unit-auth-session")
    accepted = services.design.accept(unit_id="unit-auth-session")

    reopened = services.design.write_draft(
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
    current = services.design.read(unit_id="unit-auth-session", view=ArtifactView.FULL)
    original_checkpoint = services.store.load_checkpoint(
        ArtifactRef(
            key=ArtifactKey(stage=ArtifactStage.DESIGN, artifact_id="unit-auth-session"),
            checkpoint_id=accepted.metadata["checkpoint_id"],
        )
    )

    assert reopened.result.ok is True
    assert reopened.metadata["checkpoint_id"] != accepted.metadata["checkpoint_id"]
    assert current.artifacts["workflow_status"] == "draft"
    assert current.artifacts["readiness"] == "medium"
    assert original_checkpoint is not None
    assert original_checkpoint.metadata.stage_metadata["status"] == "accepted"


def test_session_startup_view_rebuilds_missing_or_stale_index(tmp_path: Path) -> None:
    services = build_runtime_services(tmp_path)
    services.session_lifecycle.write_active_thread_handoff(
        thread_id="thread-b",
        title="Second Thread",
        current_intent_summary="Still shaping the design runtime.",
        next_suggested_action="Decide whether to split review logic.",
        thread_markdown="# Thread B\n\nWorking notes.",
    )
    services.session_lifecycle.write_active_thread_handoff(
        thread_id="thread-a",
        title="First Thread",
        current_intent_summary="Finishing session lifecycle implementation.",
        next_suggested_action="Verify archive semantics.",
        thread_markdown="# Thread A\n\nWorking notes.",
    )
    index_root = tmp_path / "session" / "index" / "recent-session"
    if index_root.exists():
        import shutil

        shutil.rmtree(index_root)

    startup = services.session_lifecycle.read_recent_session_startup_view()

    assert startup.result.ok is True
    assert startup.metadata["rebuilt"] is True
    assert startup.metadata["active_thread_count"] == 2
    assert startup.warnings == ("startup_index_rebuilt",)
    assert [entry["thread_id"] for entry in startup.artifacts["active_threads"]] == ["thread-a", "thread-b"]


def test_session_handoff_refreshes_startup_projection(tmp_path: Path) -> None:
    services = build_runtime_services(tmp_path)

    write = services.session_lifecycle.write_active_thread_handoff(
        thread_id="thread-1",
        title="Implement Session Lifecycle",
        current_intent_summary="Add bounded recovery and archive enforcement.",
        next_suggested_action="Test startup rebuild and archive recovery paths.",
        thread_markdown="# Thread 1\n\nSession lifecycle work.",
    )
    startup = services.session_lifecycle.read_recent_session_startup_view()

    assert write.result.ok is True
    assert write.metadata["startup_index_updated"] is True
    assert write.metadata["projection_stale"] is False
    assert startup.metadata["rebuilt"] is False
    assert startup.artifacts["active_threads"][0]["thread_id"] == "thread-1"


def test_session_archive_moves_thread_to_history_and_removes_active_state(tmp_path: Path) -> None:
    services = build_runtime_services(tmp_path)
    services.session_lifecycle.write_active_thread_handoff(
        thread_id="thread-1",
        title="Implement Session Lifecycle",
        current_intent_summary="Add bounded recovery and archive enforcement.",
        next_suggested_action="Summarize completion and archive it.",
        thread_markdown="# Thread 1\n\nSession lifecycle work.",
    )

    archived = services.session_lifecycle.archive_completed_thread(
        thread_id="thread-1",
        closure_summary="Session lifecycle runtime shipped with tests.",
    )
    startup = services.session_lifecycle.read_recent_session_startup_view()
    active = services.session_lifecycle.read_active_thread(thread_id="thread-1")

    assert archived.result.ok is True
    assert archived.metadata["active_removed"] is True
    assert startup.artifacts["active_threads"] == []
    assert startup.artifacts["recent_completed_threads"][0]["thread_id"] == "thread-1"
    assert active.result.ok is False


def test_session_handoff_warns_when_projection_refresh_fails_but_thread_write_persists(
    tmp_path: Path,
    monkeypatch,
) -> None:
    services = build_runtime_services(tmp_path)

    def fail_index_refresh(*, reason: str):
        del reason
        raise RuntimeError("simulated index write failure")

    monkeypatch.setattr(services.session_lifecycle, "_persist_recent_session_index", fail_index_refresh)

    write = services.session_lifecycle.write_active_thread_handoff(
        thread_id="thread-1",
        title="Implement Session Lifecycle",
        current_intent_summary="Thread-first handoff should still persist.",
        next_suggested_action="Repair the startup projection later.",
        thread_markdown="# Thread 1\n\nSession lifecycle work.",
    )
    active = services.session_lifecycle.read_active_thread(thread_id="thread-1")

    assert write.result.status == OperationStatus.WARNING
    assert write.metadata["startup_index_updated"] is False
    assert write.metadata["projection_stale"] is True
    assert write.warnings == ("startup_projection_stale",)
    assert active.result.ok is True


def test_mcp_server_registers_flat_tool_surface(tmp_path: Path) -> None:
    server = create_server(tmp_path)

    tool_names = [tool.name for tool in server.list_tools()]

    assert tool_names == [
        "discovery_read",
        "discovery_write_draft",
        "discovery_to_design",
        "design_read",
        "design_write_draft",
        "design_to_review",
        "design_accept",
        "read_recent_session_startup_view",
        "read_active_thread",
        "write_active_thread_handoff",
        "rebuild_recent_session_index",
        "archive_completed_thread",
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
    assert success["warnings"] == []
    assert success["artifacts"]["value"] == "x"
    assert success["metadata"]["count"] == 1
    assert warning["result"] == "warning"
    assert warning["warnings"] == ["projection_stale"]
    assert failure["result"] == "failure"


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
        "discovery_write_draft",
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
            "view": "short",
        },
    )

    assert write["result"] == "success"
    assert write["warnings"] == []
    assert "checkpoint_id" in write["metadata"]
    assert write["artifacts"]["artifact_ref"]["stage"] == "discovery"
    assert read["result"] == "success"
    assert read["artifacts"]["status"] == "draft"
    assert read["artifacts"]["readiness"] == "medium"
    assert "markdown" not in read["artifacts"]


def test_mcp_session_lifecycle_path_reads_compact_startup_and_full_thread(tmp_path: Path) -> None:
    server = create_server(tmp_path)

    handoff = server.call_tool(
        "write_active_thread_handoff",
        {
            "thread_id": "thread-1",
            "title": "Implement MCP Adapter",
            "current_intent_summary": "Wire thin handlers over runtime services.",
            "next_suggested_action": "Add lifecycle coverage after the read path works.",
            "thread_markdown": "# Thread 1\n\nMCP adapter work.",
        },
    )
    startup = server.call_tool("read_recent_session_startup_view")
    active = server.call_tool("read_active_thread", {"thread_id": "thread-1"})

    assert handoff["result"] == "success"
    assert handoff["metadata"]["startup_index_updated"] is True
    assert startup["result"] == "success"
    assert startup["artifacts"]["active_threads"][0]["thread_id"] == "thread-1"
    assert "thread_markdown" not in startup["artifacts"]
    assert active["result"] == "success"
    assert active["artifacts"]["thread_markdown"] == "# Thread 1\n\nMCP adapter work."
    assert active["metadata"]["thread_id"] == "thread-1"


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
        cwd="/home/maddie/repos/clauderfall",
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
        assert "discovery_write_draft" in tool_names
        assert "write_active_thread_handoff" in tool_names

        discovery_write = _stdio_request(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "discovery_write_draft",
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
        assert discovery_write["result"]["structuredContent"]["result"] == "success"

        startup_write = _stdio_request(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "write_active_thread_handoff",
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
        assert startup_write["result"]["structuredContent"]["metadata"]["startup_index_updated"] is True

        startup_read = _stdio_request(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 5,
                "method": "tools/call",
                "params": {
                    "name": "read_recent_session_startup_view",
                    "arguments": {},
                },
            },
        )
        active_threads = startup_read["result"]["structuredContent"]["artifacts"]["active_threads"]
        assert active_threads[0]["thread_id"] == "thread-1"

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


def test_stdio_mcp_server_supports_custom_artifacts_root(tmp_path: Path) -> None:
    artifacts_root = tmp_path / "docs" / "clauderfall"
    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "clauderfall.mcp.stdio",
            "--repo-root",
            str(tmp_path),
            "--artifacts-root",
            str(artifacts_root),
        ],
        cwd="/home/maddie/repos/clauderfall",
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
                    "name": "write_active_thread_handoff",
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

    assert (artifacts_root / "session" / "active" / "thread-custom-root" / "current" / "artifact.md").exists()
    assert not (tmp_path / "session").exists()


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
