---
title: Clauderfall Session Handoff 2026-03-27 Implementation Plan Ready
doc_type: handoff
status: active
updated: 2026-03-27
summary: Continuity note after packaging the runtime-design work into a dependency-ordered implementation plan and explicitly framing the current codebase as v1 reference rather than v2 architectural truth.
---

# Clauderfall Session Handoff 2026-03-27 Implementation Plan Ready

## Completed

- Kept the runtime-design work as the active v2 product direction.
- Added a short top-level implementation orchestrator:
  - [TODO.md](/home/maddie/repos/clauderfall/TODO.md)
- Added dependency-ordered feat TODOs for single-threaded implementation:
  - [TODO_FEAT_RUNTIME_SKELETON.md](/home/maddie/repos/clauderfall/TODO_FEAT_RUNTIME_SKELETON.md)
  - [TODO_FEAT_SHARED_ARTIFACT_RUNTIME.md](/home/maddie/repos/clauderfall/TODO_FEAT_SHARED_ARTIFACT_RUNTIME.md)
  - [TODO_FEAT_DISCOVERY_RUNTIME.md](/home/maddie/repos/clauderfall/TODO_FEAT_DISCOVERY_RUNTIME.md)
  - [TODO_FEAT_DESIGN_RUNTIME.md](/home/maddie/repos/clauderfall/TODO_FEAT_DESIGN_RUNTIME.md)
  - [TODO_FEAT_SESSION_LIFECYCLE_RUNTIME.md](/home/maddie/repos/clauderfall/TODO_FEAT_SESSION_LIFECYCLE_RUNTIME.md)
- Updated the orchestrator prompt to:
  - process feats one at a time
  - stop around 60 percent remaining context
  - stop on real blocking design gaps
  - avoid inventing missing design

## Current Truth

- The active docs are ready enough to begin implementation of the v2 runtime.
- The current `src/` tree should be treated as v1 reference unless a feat explicitly chooses to reuse part of it.
- The intended implementation order is:
  1. runtime skeleton
  2. shared artifact runtime
  3. Discovery runtime
  4. Design runtime
  5. session lifecycle runtime
- The plan assumes a clean v2 runtime cut first, not an incremental reshaping of v1 abstractions into the new architecture.

## Important Constraints

- Do not let v1 module shape define the v2 runtime architecture.
- Do not invent missing design to keep implementation moving.
- Surface real blocking design gaps explicitly when encountered.
- Keep stage policy above the shared artifact-runtime layer.
- Keep reopening as ordinary checkpointed revision, not a special workflow verb.
- Keep Design artifact acceptance separate from build approval.

## Suggested Next Step

- Start implementation with [TODO_FEAT_RUNTIME_SKELETON.md](/home/maddie/repos/clauderfall/TODO_FEAT_RUNTIME_SKELETON.md).
- Use the feat TODOs as the execution order rather than re-deriving the implementation plan from the full doc set each session.

## Key Docs

- [TODO.md](/home/maddie/repos/clauderfall/TODO.md)
- [TODO_FEAT_RUNTIME_SKELETON.md](/home/maddie/repos/clauderfall/TODO_FEAT_RUNTIME_SKELETON.md)
- [stage_runtime_mcp_pattern.md](/home/maddie/repos/clauderfall/docs/design/stage_runtime_mcp_pattern.md)
- [shared_stage_runtime_substrate.md](/home/maddie/repos/clauderfall/docs/design/shared_stage_runtime_substrate.md)
- [stage_artifact_runtime_interface.md](/home/maddie/repos/clauderfall/docs/design/stage_artifact_runtime_interface.md)
- [discovery_runtime_mcp_interface.md](/home/maddie/repos/clauderfall/docs/design/discovery_runtime_mcp_interface.md)
- [design_runtime_mcp_interface.md](/home/maddie/repos/clauderfall/docs/design/design_runtime_mcp_interface.md)
- [session_lifecycle_runtime_interface.md](/home/maddie/repos/clauderfall/docs/design/session_lifecycle_runtime_interface.md)
