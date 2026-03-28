from __future__ import annotations

from pathlib import Path

from clauderfall.runtime import (
    ArtifactKey,
    ArtifactPair,
    ArtifactRef,
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
