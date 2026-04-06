---
title: Clauderfall Design Docs Index
doc_type: index
status: stable
updated: 2026-04-04
summary: Canonical index for the active Clauderfall product and engine-level documentation set.
---

# Clauderfall Design Docs Index

This folder contains the active documentation set.

## Purpose

These docs define:

- the Clauderfall product brief
- the behavior expected from the Discovery engine
- the behavior expected from the Design engine
- the starting point for the active doc set

## Read Order

1. `clauderfall_product_brief.md`
2. `discovery_engine.md`
3. `design_engine.md`

## Files

- `clauderfall_product_brief.md` - Product brief for Clauderfall.
- `discovery_engine.md` - Discovery engine brief derived from the product brief.
- `design_engine.md` - Design engine brief derived from the product brief.
- `stage_runtime_mcp_pattern.md` - Defines the shared Clauderfall architecture pattern of LLM-driven stage work over deterministic backend services exposed through MCP.
- `skill_mcp_interaction_contract.md` - Defines the shared contract for how Discovery and Design skills should use MCP for authoritative reads, writes, and workflow transitions.
- `mcp_adapter_surface.md` - Defines the first MCP-facing adapter layer over the v2 runtime services, including flat tool naming, response mapping, and thin-handler boundaries.
- `shared_stage_runtime_substrate.md` - Defines the common runtime substrate shared by Discovery, Design, session lifecycle, and future TODO work.
- `stage_runtime_operation_vocabulary.md` - Defines the standardized cross-stage operation vocabulary for shared runtime services and MCP interfaces.
- `stage_artifact_runtime_interface.md` - Defines the shared artifact-level runtime interface beneath stage-specific services for authoritative reads, checkpoint writes, status-aware transitions, and explicit deletion.
- `artifact_deletion_control_surface.md` - Defines the explicit destructive cleanup surface for removing superseded or mistaken Discovery briefs and Design units from runtime state.
- `discovery_runtime_mcp_interface.md` - Defines the Discovery runtime and MCP-facing operation set for reading the working brief, checkpointing draft progress, handing off into Design, and deleting obsolete briefs.
- `design_runtime_mcp_interface.md` - Defines the Design runtime and MCP-facing operation set for reading the current unit, checkpointing draft progress, accepting the design record, and deleting obsolete units.
- `artifact_persistence_format.md` - Defines the physical persistence format for readable stage artifacts and their structured metadata.
- `artifact_checkpoint_semantics.md` - Defines artifact identity, flush checkpoints, and revision semantics for persisted artifacts.
- `artifact_checkpoint_metadata.md` - Defines the required metadata envelope recorded for each artifact checkpoint.
- `artifact_filesystem_layout.md` - Defines the on-disk layout for latest artifacts and immutable checkpoint history.
- `discovery_brief_artifact.md` - Defines the canonical Discovery brief artifact as a readable problem-framing document with a small structured sidecar.
- `discovery_session_flow.md` - Defines the end-to-end interaction flow for an active Discovery session from rough intent through Design Start Context creation.
- `discovery_readiness_and_transition.md` - Defines the Discovery-stage readiness judgment and transition rules into Design.
- `design_start_context_generation.md` - Defines the derivation rules that condense a Discovery brief into a Design Start Context artifact.
- `design_unit_artifact.md` - Defines the design-unit artifact shape for the Design stage.
- `design_unit_readiness.md` - Defines the semantics and rating criteria for design-unit readiness.
- `design_unit_document_shape.md` - Defines the recommended readable structure for a design unit document.
- `design_unit_sequencing.md` - Defines how the Design engine should choose and decompose design units.
- `design_review_workflow.md` - Defines the workflow from drafting through review and build-readiness approval.
- `design_session_flow.md` - Defines the end-to-end interaction flow for an active Design session.
- `discovery_design_start_context.md` - Defines the condensed Design Start Context artifact between Discovery and Design.
- `design_discovery_reentry.md` - Defines when Design should resolve ambiguity locally versus return to Discovery.
- `session_lifecycle.md` - Discovery brief for strict recent-session-state, handoff, and start-session lifecycle work under a single-current carry-forward model.
- `session_recent_state_artifact.md` - Defines the recent-session-state artifact contract spanning the repo index, one current carry-forward artifact, and archived history.
- `session_handoff_write_update_flow.md` - Defines the current-state-first handoff write path and derived repo-index projection behavior for recent session state.
- `session_start_drill_in_flow.md` - Defines the startup orientation flow from the repo-level recent-session index into optional current-state drill-in or a new direction.
- `session_continuity_skill_surface.md` - Defines the packaged skill surface for startup orientation and handoff persistence over the single-current session lifecycle MCP interface.
- `session_archive_transition_mechanics.md` - Defines the immediate completion-to-archive transition and failure semantics for leaving the current layer.
- `session_lifecycle_runtime_interface.md` - Defines the deterministic backend runtime and MCP-facing interface boundary for recent-session lifecycle work under the single-current model.
- `session_lifecycle_mcp_interface.md` - Defines the high-level MCP operations, inputs, outputs, and error semantics for recent-session lifecycle work under the single-current model.
- `session_lifecycle_backend_service.md` - Defines the backend lifecycle service that should own recent-session policy, recovery, and structured lifecycle results under the single-current model.
- `session_lifecycle_operation_runner.md` - Defines the shared bounded operation and recovery mechanism used by the session-lifecycle backend service under the single-current model.
