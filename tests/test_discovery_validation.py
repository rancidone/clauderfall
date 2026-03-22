from clauderfall.artifacts.common import CompletionStatus, ConfidenceLevel, Grounding, ReadinessState, SourceClassification
from clauderfall.artifacts.discovery import DiscoveryArtifact, ProvenanceRecord, ScopeBoundaries, SourceRegisterEntry
from clauderfall.contracts.discovery_design import check_discovery_to_design_handoff
from clauderfall.validation.discovery import validate_discovery_artifact


def build_valid_artifact() -> DiscoveryArtifact:
    return DiscoveryArtifact(
        problem_definition=["Agents need bounded, auditable context."],
        constraints=["Context must be explicit and traceable."],
        success_criteria=["A valid discovery artifact can be handed to design."],
        scope_boundaries=ScopeBoundaries(
            in_scope=["Artifact modeling"],
            out_of_scope=["Execution system"],
        ),
        risks=["Terminology drift between docs and code."],
        unknowns=["Precise persistence schema for later artifacts."],
        open_questions=["Should readiness be stored or derived in code?"],
        source_register=[
            SourceRegisterEntry(
                source_id="src-1",
                source_type="doc",
                origin_ref="docs/design/discovery_artifact.md",
                authority_level="primary",
            )
        ],
        provenance_records=[
            ProvenanceRecord(
                target_ref=target_ref,
                source_classification=SourceClassification.EXPLICIT,
                confidence=ConfidenceLevel.HIGH,
                grounding=Grounding.ANCHORED,
                trace_links=["src-1"],
            )
            for target_ref in [
                "problem_definition",
                "constraints",
                "success_criteria",
                "scope_boundaries",
                "risks",
                "unknowns",
                "open_questions",
            ]
        ],
        completion_status=CompletionStatus(
            readiness_state=ReadinessState.READY,
            blocking_gaps=[],
            non_blocking_gaps=["Persistence model may evolve."],
            justification="Core discovery inputs are grounded enough for design.",
        ),
    )


def test_valid_discovery_artifact_has_no_validation_issues() -> None:
    artifact = build_valid_artifact()

    assert validate_discovery_artifact(artifact) == []


def test_handoff_accepts_ready_valid_discovery_artifact() -> None:
    artifact = build_valid_artifact()

    result = check_discovery_to_design_handoff(artifact)

    assert result.accepted is True
    assert result.reasons == []


def test_handoff_rejects_ready_artifact_with_semantic_issue() -> None:
    artifact = build_valid_artifact()
    artifact.success_criteria = []

    result = check_discovery_to_design_handoff(artifact)

    assert result.accepted is False
    assert "success_criteria must not be empty" in result.reasons
