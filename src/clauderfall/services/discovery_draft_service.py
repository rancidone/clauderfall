"""Conversational drafting support for Discovery."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from clauderfall.artifacts.common import ArtifactBase, ReadinessState
from clauderfall.artifacts.discovery import DiscoveryArtifact
from clauderfall.contracts.discovery_design import DiscoveryDesignGateResult, check_discovery_to_design_handoff
from clauderfall.skills.loader import SkillDefinition, load_skill
from clauderfall.validation.discovery import validate_discovery_artifact


class DiscoveryConversationSession(ArtifactBase):
    """Current conversational Discovery session state."""

    artifact_id: str
    current_version: int | None = None
    current_artifact: DiscoveryArtifact | None = None
    skill_name: str
    skill_path: str


class SkillReferenceDocument(ArtifactBase):
    """Packaged reference loaded alongside a skill."""

    path: str
    content: str


class DiscoveryTurnPayload(ArtifactBase):
    """Prepared Discovery turn payload for an external conversational driver."""

    session: DiscoveryConversationSession
    user_turn: str
    skill_instructions: str
    skill_references: list[SkillReferenceDocument]
    recommended_cli_flow: list[str]


class DiscoveryDraftReview(ArtifactBase):
    """Deterministic review result for a candidate Discovery Artifact."""

    candidate_artifact: DiscoveryArtifact
    validation_issues: list[str]
    handoff: DiscoveryDesignGateResult
    persistable: bool
    requires_clarification: bool
    recommended_next_action: str


class DiscoveryProposal(ArtifactBase):
    """LLM proposal output for one Discovery turn."""

    assistant_reply: str
    candidate_artifact: DiscoveryArtifact


class DiscoveryProposalResult(ArtifactBase):
    """End-to-end result of generating and reviewing one Discovery proposal."""

    turn_payload: DiscoveryTurnPayload
    proposal: DiscoveryProposal
    review: DiscoveryDraftReview


class DiscoveryTurnResult(ArtifactBase):
    """Reviewed result for one skill-driven Discovery turn."""

    session: DiscoveryConversationSession
    user_turn: str
    assistant_reply: str
    candidate_artifact: DiscoveryArtifact
    review: DiscoveryDraftReview


class DiscoveryProposalProvider(Protocol):
    """Provider interface for model-backed Discovery proposals."""

    def propose(self, payload: DiscoveryTurnPayload) -> DiscoveryProposal:
        """Generate an assistant reply plus candidate artifact for one Discovery turn."""


class StaticDiscoveryProposalProvider:
    """Deterministic provider for tests and file-backed CLI workflows."""

    def __init__(self, proposal: DiscoveryProposal) -> None:
        self._proposal = proposal

    def propose(self, payload: DiscoveryTurnPayload) -> DiscoveryProposal:
        return self._proposal


class DiscoveryDraftService:
    """Session preparation, proposal generation, and candidate review for the Discovery skill."""

    def __init__(self, load_artifact, save_artifact, load_latest_version) -> None:
        self._load_artifact = load_artifact
        self._save_artifact = save_artifact
        self._load_latest_version = load_latest_version

    def start_session(self, artifact_id: str, version: int | None = None) -> DiscoveryConversationSession:
        skill = load_skill("discovery")
        current_artifact = self._load_artifact(artifact_id, version)
        current_version = None
        if current_artifact is not None:
            current_version = version if version is not None else self._load_latest_version(artifact_id)
        return DiscoveryConversationSession(
            artifact_id=artifact_id,
            current_version=current_version,
            current_artifact=current_artifact,
            skill_name=skill.name,
            skill_path=str(skill.path),
        )

    def prepare_turn(
        self,
        artifact_id: str,
        user_turn: str,
        version: int | None = None,
    ) -> DiscoveryTurnPayload:
        skill = load_skill("discovery")
        session = self.start_session(artifact_id=artifact_id, version=version)
        return DiscoveryTurnPayload(
            session=session,
            user_turn=user_turn,
            skill_instructions=skill.instructions,
            skill_references=self._load_skill_references(skill),
            recommended_cli_flow=[
                "validate-discovery <candidate.json>",
                "check-discovery-handoff <candidate.json>",
                f"save-discovery {artifact_id} <candidate.json>",
            ],
        )

    def propose_revision(
        self,
        artifact_id: str,
        user_turn: str,
        provider: DiscoveryProposalProvider,
        version: int | None = None,
    ) -> DiscoveryProposalResult:
        turn_payload = self.prepare_turn(
            artifact_id=artifact_id,
            user_turn=user_turn,
            version=version,
        )
        proposal = provider.propose(turn_payload)
        review = self.review_candidate(proposal.candidate_artifact)
        return DiscoveryProposalResult(
            turn_payload=turn_payload,
            proposal=proposal,
            review=review,
        )

    def next_turn(
        self,
        artifact_id: str,
        user_turn: str,
        assistant_reply: str,
        candidate_artifact: DiscoveryArtifact,
        version: int | None = None,
    ) -> DiscoveryTurnResult:
        session = self.start_session(artifact_id=artifact_id, version=version)
        review = self.review_candidate(candidate_artifact)
        return DiscoveryTurnResult(
            session=session,
            user_turn=user_turn,
            assistant_reply=assistant_reply,
            candidate_artifact=candidate_artifact,
            review=review,
        )

    def review_candidate(self, candidate_artifact: DiscoveryArtifact) -> DiscoveryDraftReview:
        validation_issues = validate_discovery_artifact(candidate_artifact)
        handoff = check_discovery_to_design_handoff(candidate_artifact)
        persistable = not validation_issues
        requires_clarification = (
            candidate_artifact.completion_status.readiness_state is ReadinessState.NOT_READY
            or bool(candidate_artifact.completion_status.blocking_gaps)
            or not handoff.accepted
        )
        if validation_issues:
            recommended_next_action = "Revise the candidate artifact to resolve deterministic validation issues."
        elif requires_clarification:
            recommended_next_action = "Ask a targeted clarification question and issue a new artifact revision."
        else:
            recommended_next_action = "Persist the candidate artifact as the next Discovery version."
        return DiscoveryDraftReview(
            candidate_artifact=candidate_artifact,
            validation_issues=validation_issues,
            handoff=handoff,
            persistable=persistable,
            requires_clarification=requires_clarification,
            recommended_next_action=recommended_next_action,
        )

    def save_candidate(
        self,
        artifact_id: str,
        candidate_artifact: DiscoveryArtifact,
        version: int | None = None,
    ) -> tuple[int, DiscoveryDraftReview]:
        review = self.review_candidate(candidate_artifact)
        if not review.persistable:
            issues = "; ".join(review.validation_issues)
            raise ValueError(f"candidate discovery artifact is not persistable: {issues}")
        persisted_version = self._save_artifact(
            artifact_id=artifact_id,
            artifact=candidate_artifact,
            version=version,
        )
        return persisted_version, review

    def _load_skill_references(self, skill: SkillDefinition) -> list[SkillReferenceDocument]:
        references_dir = Path(skill.path) / "references"
        if not references_dir.exists():
            return []
        references: list[SkillReferenceDocument] = []
        for path in sorted(references_dir.glob("*.md")):
            references.append(SkillReferenceDocument(path=str(path.relative_to(skill.path)), content=path.read_text()))
        return references
