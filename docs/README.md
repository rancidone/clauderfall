---
title: Clauderfall Docs Index
doc_type: index
status: stable
updated: 2026-04-04
summary: Top-level index for the active Clauderfall documentation set.
---

# Docs Index

This folder contains the active Clauderfall documentation set.

## Structure

- `design/` - Active product and engine-level discovery/design docs.

## Standard Frontmatter

Core docs use the same frontmatter fields:

- `title` - Canonical document title.
- `doc_type` - Document role, such as `index`, `brief`, `engine-brief`, `design`, or `archive-index`.
- `status` - Document maturity state. Prefer `draft`, `ready`, or `stable` for active docs, and reserve `archived`, `superseded`, or `deprecated` for inactive docs.
- `updated` - Date of the last substantive edit in `YYYY-MM-DD` format.
- `summary` - One-line description of the document's purpose.

## Status Vocabulary

Use these values consistently:

- `draft` - Actively being shaped. The document is useful, but core structure or decisions may still change.
- `ready` - Ready for normal downstream use and review. The document is coherent enough that later work should not need to invent major decisions.
- `stable` - Mature and expected to change infrequently. Use this for settled reference docs and long-lived contracts.
- `archived` - Retained for historical reference, not current truth.
- `superseded` - Replaced by a newer canonical document.
- `deprecated` - Still present temporarily, but should not be used for new work.

## Primary Entry Points

- `design/README.md` - Canonical index for the active documentation set.
- `design/clauderfall_product_brief.md` - Product brief for Clauderfall.
- `design/discovery_engine.md` - Discovery engine brief derived from the product brief.
- `design/design_engine.md` - Design engine brief derived from the product brief.
- `design/mcp_adapter_surface.md` - Design doc for the first MCP-facing adapter layer over the v2 runtime services.
- `design/skill_mcp_interaction_contract.md` - Design doc for how Clauderfall stage skills should interact with MCP for authoritative reads, writes, and workflow transitions.
- `design/stage_artifact_runtime_interface.md` - Design doc for the shared artifact-level runtime interface beneath stage-specific Discovery and Design services.
- `design/artifact_deletion_control_surface.md` - Design doc for the explicit deletion surface used to remove superseded or mistaken Discovery and Design artifacts from runtime state.
- `design/discovery_runtime_mcp_interface.md` - Design doc for the Discovery runtime and MCP-facing operation set of `read`, `write`, `to_design`, and `delete`.
- `design/design_runtime_mcp_interface.md` - Design doc for the Design runtime and MCP-facing operation set of `read`, `write`, `accept`, and `delete`.
- `design/stage_runtime_mcp_pattern.md` - Design doc for the shared LLM-front-end plus deterministic-backend architecture pattern across stages.
- `design/shared_stage_runtime_substrate.md` - Design doc for the common runtime substrate beneath stage-specific services and MCP handlers.
- `design/stage_runtime_operation_vocabulary.md` - Design doc for the standardized cross-stage operation vocabulary used by runtime services and MCP interfaces.
- `design/artifact_persistence_format.md` - Design doc for the physical persisted format of readable artifacts and structured metadata.
- `design/artifact_checkpoint_semantics.md` - Design doc for artifact identity, checkpoints, and revision semantics.
- `design/artifact_checkpoint_metadata.md` - Design doc for the required metadata recorded for each checkpoint.
- `design/artifact_filesystem_layout.md` - Design doc for the on-disk layout of current artifacts and checkpoint history.
- `design/discovery_brief_artifact.md` - Design doc for the canonical Discovery brief artifact and its structured side.
- `design/discovery_session_flow.md` - Design doc for the end-to-end Discovery-stage interaction flow.
- `design/discovery_readiness_and_transition.md` - Design doc for Discovery readiness judgment and transition rules.
- `design/design_start_context_generation.md` - Design doc for the derivation rules that condense a Discovery brief into a Design Start Context artifact.
- `design/design_unit_artifact.md` - Design doc for the design-unit artifact shape.
- `design/design_unit_readiness.md` - Design doc for the meaning of design-unit readiness.
- `design/design_unit_document_shape.md` - Design doc for the canonical readable design-unit document shape.
- `design/design_unit_sequencing.md` - Design doc for sequencing and decomposition of design units.
- `design/design_review_workflow.md` - Design doc for design-unit drafting, review, and build-readiness approval.
- `design/design_session_flow.md` - Design doc for the end-to-end Design-stage interaction flow.
- `design/discovery_design_start_context.md` - Design doc for the condensed Design Start Context artifact between Discovery and Design.
- `design/design_discovery_reentry.md` - Design doc for the Design-to-Discovery repair boundary.
- `design/session_lifecycle.md` - Discovery brief for strict recent-session-state, handoff, and start-session lifecycle work under a single-current carry-forward model.
- `design/session_recent_state_artifact.md` - Design doc for the recent-session-state artifact contract across a startup index, one current carry-forward record, and archived history.
- `design/session_handoff_write_update_flow.md` - Design doc for the current-state-first handoff write path and recoverable repo-index projection.
- `design/session_start_drill_in_flow.md` - Design doc for startup orientation from the repo-level index into explicit current-state drill-in or a new direction.
- `design/session_continuity_skill_surface.md` - Design doc for the packaged session skill surface over lifecycle startup and handoff operations in the single-current model.
- `design/session_archive_transition_mechanics.md` - Design doc for the immediate current-to-history archive transition and consistent archived-state requirement.
- `design/session_lifecycle_runtime_interface.md` - Design doc for deterministic backend lifecycle operations and a single-current MCP-facing interface for recent-session state.
- `design/session_lifecycle_mcp_interface.md` - Design doc for concrete high-level MCP lifecycle operations, payloads, and error semantics under the single-current model.
- `design/session_lifecycle_backend_service.md` - Design doc for the backend service shape behind recent-session lifecycle operations and recovery rules under the single-current model.
- `design/session_lifecycle_operation_runner.md` - Design doc for the shared bounded operation and recovery mechanism behind lifecycle service methods in the single-current model.
