from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from clauderfall.artifacts.common import (
    ConflictSeverity,
    CompletionStatus,
    ConfidenceLevel,
    DesignElementClassification,
    Grounding,
    IncludedItemType,
    ReadinessState,
    SourceClassification,
    TaskElementClassification,
)
from clauderfall.artifacts.context import (
    BudgetSummary,
    ContextAssemblyItem,
    ConflictSignal,
    ContextPacket,
    ContextTraceabilityRecord,
    ExclusionRecord,
    IncludedContextItem,
    InclusionJustification,
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
from clauderfall.artifacts.task import TaskArtifact, TaskTraceabilityRecord
from clauderfall.services.discovery_draft_service import DiscoveryProposal


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


@pytest.fixture
def valid_task_artifact() -> TaskArtifact:
    return TaskArtifact(
        objective=["Implement the append-only task repository and handoff checks."],
        scope=ScopeBoundaries(
            in_scope=["Task artifact modeling", "Context handoff gate"],
            out_of_scope=["Execution runtime"],
        ),
        inputs=[
            "Design repository API for append-only artifact versions.",
            "Design contract requirements for bounded task execution inputs.",
        ],
        outputs=[
            "A persisted task artifact version.",
            "A deterministic Task-to-Context handoff result.",
        ],
        constraints=[
            "Task artifacts must not introduce new design requirements.",
            "Persistence must remain append-only and auditable.",
        ],
        invariants=[
            "Task acceptance criteria remain explicit and testable.",
            "Context handoff does not proceed from not_ready tasks.",
        ],
        acceptance_criteria=[
            "A valid task artifact passes deterministic validation.",
            "The task handoff gate rejects not_ready artifacts.",
        ],
        dependencies=[
            "Design artifact validation must already be implemented.",
            "Artifact repositories must support exact and latest version reads.",
        ],
        traceability=[
            TaskTraceabilityRecord(
                target_ref=target_ref,
                classification=TaskElementClassification.GROUNDED,
                supports=["bounded execution contract", "context-safe handoff"],
                trace_links=["design.system_structure[0]"],
            )
            for target_ref in [
                "objective",
                "inputs",
                "constraints",
                "invariants",
                "acceptance_criteria",
            ]
        ],
        completion_status=CompletionStatus(
            readiness_state=ReadinessState.READY,
            blocking_gaps=[],
            non_blocking_gaps=["Task dependency modeling may become richer later."],
            justification="The task is bounded and explicit enough for context assembly.",
        ),
    )


@pytest.fixture
def task_json_path(tmp_path: Path, valid_task_artifact: TaskArtifact) -> Path:
    path = tmp_path / "task.json"
    path.write_text(json.dumps(valid_task_artifact.model_dump(mode="json"), indent=2))
    return path


@pytest.fixture
def valid_context_packet(valid_task_artifact: TaskArtifact) -> ContextPacket:
    return ContextPacket(
        task_contract=valid_task_artifact,
        included_context=[
            IncludedContextItem(
                item_id="ctx-1",
                included_material="Task repository implementation surface",
                item_type=IncludedItemType.SOURCE_SURFACE,
                source_origin="src/clauderfall/persistence/repositories.py",
            ),
            IncludedContextItem(
                item_id="ctx-2",
                included_material="Task validation rules for readiness and traceability",
                item_type=IncludedItemType.ARTIFACT,
                source_origin="docs/design/task_artifact.md",
            ),
        ],
        inclusion_justification=[
            InclusionJustification(
                item_id="ctx-1",
                justification="Needed to implement append-only task persistence correctly.",
                supports=["correctness", "dependency handling"],
            ),
            InclusionJustification(
                item_id="ctx-2",
                justification="Needed to preserve task constraints and acceptance semantics during execution.",
                supports=["constraint preservation", "acceptance evaluation"],
            ),
        ],
        exclusions=[
            ExclusionRecord(
                excluded_material="Unrelated discovery history",
                reason="Historically relevant but not execution-relevant for the task.",
            )
        ],
        conflict_signals=[
            ConflictSignal(
                conflicting_elements=["ctx-1", "ctx-2"],
                nature_of_conflict="Minor wording mismatch between code and docs.",
                impact_on_safe_execution="Low; traceability remains intact.",
                severity=ConflictSeverity.LOW,
            )
        ],
        budget_summary=BudgetSummary(
            total_budget_measure="2 included items, 1 exclusion",
            shaping_decisions=[
                "Included direct implementation surfaces instead of broader repository context.",
                "Excluded unrelated historical material to protect task scope.",
            ],
        ),
        traceability=[
            ContextTraceabilityRecord(
                target_ref=target_ref,
                supports=["safe execution packet assembly"],
                trace_links=["task.objective[0]"],
            )
            for target_ref in ["task_contract", "included_context", "inclusion_justification"]
        ],
        completion_status=CompletionStatus(
            readiness_state=ReadinessState.READY,
            blocking_gaps=[],
            non_blocking_gaps=["Budget measurement may become more formal later."],
            justification="The packet is minimal, justified, and sufficient for bounded execution.",
        ),
    )


@pytest.fixture
def context_json_path(tmp_path: Path, valid_context_packet: ContextPacket) -> Path:
    path = tmp_path / "context.json"
    path.write_text(json.dumps(valid_context_packet.model_dump(mode="json"), indent=2))
    return path


@pytest.fixture
def context_assembly_items() -> list[ContextAssemblyItem]:
    return [
        ContextAssemblyItem(
            item_id="ctx-1",
            included_material="Task repository implementation surface",
            item_type=IncludedItemType.SOURCE_SURFACE,
            source_origin="src/clauderfall/persistence/repositories.py",
            justification="Needed to implement append-only task persistence correctly.",
            supports=["correctness", "dependency handling"],
            trace_links=["src/clauderfall/persistence/repositories.py"],
        ),
        ContextAssemblyItem(
            item_id="ctx-2",
            included_material="Task validation rules for readiness and traceability",
            item_type=IncludedItemType.ARTIFACT,
            source_origin="docs/design/task_artifact.md",
            justification="Needed to preserve task constraints and acceptance semantics during execution.",
            supports=["constraint preservation", "acceptance evaluation"],
            trace_links=["docs/design/task_artifact.md"],
        ),
    ]


@pytest.fixture
def context_assembly_items_path(tmp_path: Path, context_assembly_items: list[ContextAssemblyItem]) -> Path:
    path = tmp_path / "supporting-items.json"
    path.write_text(json.dumps([item.model_dump(mode="json") for item in context_assembly_items], indent=2))
    return path


@pytest.fixture
def discovery_proposal(valid_discovery_artifact: DiscoveryArtifact) -> DiscoveryProposal:
    return DiscoveryProposal(
        assistant_reply="I tightened the discovery draft and left readiness at ready because the success criteria are explicit.",
        candidate_artifact=valid_discovery_artifact,
    )


@pytest.fixture
def discovery_proposal_path(tmp_path: Path, discovery_proposal: DiscoveryProposal) -> Path:
    path = tmp_path / "discovery-proposal.json"
    path.write_text(discovery_proposal.model_dump_json(indent=2))
    return path
