from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from clauderfall.artifacts.common import (
    CompletionStatus,
    ConfidenceLevel,
    DesignElementClassification,
    Grounding,
    ReadinessState,
    SourceClassification,
)
from clauderfall.artifacts.design import (
    ConstraintEncoding,
    DecisionRecord,
    DesignArtifact,
    OpenDesignQuestion,
    RiskAndEdgeCase,
    TaskDecompositionSignals,
    TraceabilityRecord,
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


@pytest.fixture
def valid_design_artifact() -> DesignArtifact:
    return DesignArtifact(
        objective=[
            "Define a bounded artifact pipeline that converts grounded discovery into explicit design structure."
        ],
        scope=ScopeBoundaries(
            in_scope=["Design artifact modeling", "Task handoff framing"],
            out_of_scope=["Execution system"],
        ),
        system_structure=[
            "A design service validates candidate artifacts before persistence.",
            "A contract gate checks design readiness before task generation.",
        ],
        constraints_encoding=[
            ConstraintEncoding(
                source_constraint_ref="discovery.constraints[0]",
                enforcing_design_element="artifact_service.validate_design",
                violation_consequence="Reject invalid design artifacts before handoff.",
            )
        ],
        invariants=[
            "Design artifacts remain traceable to discovery inputs.",
            "Task handoff never proceeds from not_ready design artifacts.",
        ],
        decisions=[
            DecisionRecord(
                decision_statement="Persist design artifacts as append-only versions.",
                affected_design_area="persistence",
                alternatives_considered=["Mutable latest-only record", "Filesystem-only snapshots"],
                rationale="Append-only versions preserve auditability across backflow and revision.",
                consequences=["Repository APIs must expose latest and exact-version reads."],
                trace_links=["discovery.success_criteria[0]"],
            )
        ],
        risks_and_edge_cases=[
            RiskAndEdgeCase(
                condition="A design omits task decomposition signals.",
                affected_design_area="task handoff",
                expected_impact="Task formation becomes ambiguous or unsafe.",
                encoded_mitigation="Fail validation before handoff.",
            )
        ],
        open_design_questions=[
            OpenDesignQuestion(
                question="Should future design artifacts encode richer workflow structure?",
                affected_design_areas=["system_structure"],
            )
        ],
        task_decomposition_signals=TaskDecompositionSignals(
            natural_work_boundaries=["Artifact validation", "Contract gates", "Persistence"],
            dependency_relationships=["Validation must precede persistence."],
            acceptance_expectations_to_preserve=["Task handoff checks must be deterministic."],
            sequencing_requirements=["Persist only validated design artifacts."],
        ),
        traceability=[
            TraceabilityRecord(
                target_ref=target_ref,
                classification=DesignElementClassification.GROUNDED,
                supports=["discovery problem grounding", "task-safe design handoff"],
                trace_links=["discovery.problem_definition[0]"],
            )
            for target_ref in [
                "objective",
                "system_structure",
                "constraints_encoding",
                "invariants",
                "decisions",
                "task_decomposition_signals",
            ]
        ],
        completion_status=CompletionStatus(
            readiness_state=ReadinessState.READY,
            blocking_gaps=[],
            non_blocking_gaps=["Workflow modeling may evolve later."],
            justification="The design is specific enough for bounded task formation.",
        ),
    )


@pytest.fixture
def design_json_path(tmp_path: Path, valid_design_artifact: DesignArtifact) -> Path:
    path = tmp_path / "design.json"
    path.write_text(json.dumps(valid_design_artifact.model_dump(mode="json"), indent=2))
    return path
