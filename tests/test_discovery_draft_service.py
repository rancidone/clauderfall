from pathlib import Path

from clauderfall.cli.main import build_artifact_service
from clauderfall.artifacts.common import ReadinessState
from clauderfall.services.discovery_draft_service import StaticDiscoveryProposalProvider


def test_prepare_discovery_turn_includes_skill_and_references(
    tmp_path: Path,
) -> None:
    service = build_artifact_service(db_path=tmp_path / "draft.db")

    payload = service.prepare_discovery_turn(
        artifact_id="disc-1",
        user_turn="We need to tighten the scope and make success measurable.",
    )

    assert payload.session.artifact_id == "disc-1"
    assert payload.session.skill_name == "discovery"
    assert "You are the Discovery driver for Clauderfall." in payload.skill_instructions
    assert any(ref.path == "references/artifact_contract.md" for ref in payload.skill_references)


def test_review_discovery_draft_flags_clarification_when_not_ready(
    tmp_path: Path,
    valid_discovery_artifact,
) -> None:
    service = build_artifact_service(db_path=tmp_path / "draft.db")
    valid_discovery_artifact.completion_status.readiness_state = ReadinessState.NOT_READY
    valid_discovery_artifact.completion_status.blocking_gaps = ["Need measurable success criteria."]

    review = service.review_discovery_draft(valid_discovery_artifact)

    assert review.persistable is True
    assert review.requires_clarification is True
    assert review.handoff.accepted is False
    assert "Ask a targeted clarification question" in review.recommended_next_action


def test_save_discovery_revision_rejects_invalid_candidate(
    tmp_path: Path,
    valid_discovery_artifact,
) -> None:
    service = build_artifact_service(db_path=tmp_path / "draft.db")
    valid_discovery_artifact.success_criteria = []

    try:
        service.save_discovery_revision("disc-1", valid_discovery_artifact)
    except ValueError as exc:
        assert "not persistable" in str(exc)
    else:
        raise AssertionError("expected ValueError for invalid discovery revision")


def test_propose_discovery_revision_returns_assistant_reply_and_review(
    tmp_path: Path,
    discovery_proposal,
) -> None:
    service = build_artifact_service(db_path=tmp_path / "draft.db")

    result = service.propose_discovery_revision(
        artifact_id="disc-1",
        user_turn="We need the scope boundaries made explicit.",
        provider=StaticDiscoveryProposalProvider(discovery_proposal),
    )

    assert result.turn_payload.session.artifact_id == "disc-1"
    assert result.proposal.assistant_reply.startswith("I tightened the discovery draft")
    assert result.review.persistable is True
    assert result.review.handoff.accepted is True
