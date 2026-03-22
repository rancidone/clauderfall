from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from clauderfall.artifacts.common import (
    CompletionStatus,
    ConfidenceLevel,
    Grounding,
    ReadinessState,
    SourceClassification,
)
from clauderfall.artifacts.discovery import (
    DiscoveryArtifact,
    ProvenanceRecord,
    ScopeBoundaries,
    SourceRegisterEntry,
)


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def valid_discovery_artifact() -> DiscoveryArtifact:
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


@pytest.fixture
def discovery_json_path(tmp_path: Path, valid_discovery_artifact: DiscoveryArtifact) -> Path:
    path = tmp_path / "discovery.json"
    path.write_text(json.dumps(valid_discovery_artifact.model_dump(mode="json"), indent=2))
    return path

