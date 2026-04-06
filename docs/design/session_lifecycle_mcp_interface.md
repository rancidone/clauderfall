---
title: Session Lifecycle MCP Interface
doc_type: design
status: ready
updated: 2026-04-05
summary: Defines the high-level MCP operations, inputs, and result shapes for recent-session lifecycle work under a single current carry-forward model.
---

# Session Lifecycle MCP Interface

## Purpose

This document defines the MCP-facing interface for recent-session lifecycle behavior in Clauderfall.

The goal is to give the LLM a small, explicit set of lifecycle operations that preserve deterministic backend enforcement without exposing raw persistence as the normal path.

## Design Position

The MCP surface for recent-session lifecycle should expose a few high-level lifecycle operations.

Those operations should be:

- explicit about lifecycle intent
- narrow enough to preserve backend invariants
- structured enough that the LLM does not need to infer transition success from prose

The MCP layer should not expose low-level file mutation as the default lifecycle contract.

## Operation Set

The initial MCP surface should expose these operations:

- `session_read_startup_view`
- `session_read_current`
- `session_write_handoff`
- `session_archive_current`

This is intentionally small.

It covers the recent-session behaviors already designed without turning MCP into a generic artifact-editing API.

## Shared Response Shape

Every lifecycle MCP operation should return a structured response with the same top-level shape:

- `result`
- `warnings`
- `artifacts`
- `metadata`

## 1. `session_read_startup_view`

## Purpose

Return the startup-oriented recent-session view used to begin session orientation.

## Inputs

This operation should require no session-specific input.

## Behavior

The runtime should return the authoritative startup-oriented session view directly from persisted session state.

Any validation or repair needed to make that view safe should happen inside the runtime rather than as a separate MCP step.

## Result Metadata

The response metadata should include at least:

- `rebuilt: boolean`
- `has_current: boolean`
- `recent_completed_count: number`

## Returned View

The startup payload should include:

- current carry-forward summary when one exists
- recent completed record summaries
- any warnings about internal validation or repair

## 2. `session_read_current`

## Purpose

Return the authoritative state for the current carry-forward record after the operator or workflow chooses to drill into it.

## Inputs

This operation should require no identifier.

## Behavior

The runtime should resolve the authoritative current-state record and return:

- structured current metadata
- the authoritative Markdown handoff note
- references to the current artifact checkpoint

If no current record exists, the operation should fail explicitly rather than silently reading history instead.

## Result Metadata

The response metadata should include at least:

- `artifact_id`
- `checkpoint_id`
- `updated_at`

## 3. `session_write_handoff`

## Purpose

Persist a handoff update for the one current carry-forward record.

## Inputs

Required:

- `title`
- `work_items`
- `thread_markdown`

Optional:

- `flush_reason`

## Behavior

The runtime should:

1. persist the current state record
2. persist the authoritative current metadata
3. make the new current state durable
4. refresh the startup-oriented recent-session index

The operation should succeed once the authoritative current state is durable.

The response should not include the full persisted body.

If the caller needs authoritative state after the write, it should use `session_read_current`.

## Result Metadata

The response metadata should include at least:

- `artifact_id`
- `checkpoint_id`
- `startup_index_updated: boolean`
- `projection_stale: boolean`

## 4. `session_archive_current`

## Purpose

Perform the immediate completion-to-archive transition for the current carry-forward record.

## Inputs

Required:

- `closure_summary`

## Behavior

The runtime should:

1. resolve the authoritative current state
2. write the archived history record
3. remove the current record from the current layer
4. update the repo-level recent-session index
5. verify the resulting archived-state postconditions

The operation should return `failure` if the runtime cannot reach a consistent archived state.

If partial work occurred and deterministic recovery restored a valid current-state end state, the operation should still return `failure` plus an explicit warning that completion did not commit.

## Result Metadata

The response metadata should include at least:

- `archived: boolean`
- `history_checkpoint_id`
- `restored_to_current: boolean`

## Error Semantics

The MCP surface should prefer explicit machine-usable failure codes over vague prose.

Likely failure or warning codes include:

- `startup_index_stale_rebuilt`
- `startup_index_malformed_rebuilt`
- `current_state_not_found`
- `current_handoff_persist_failed`
- `startup_index_refresh_failed`
- `archive_transition_failed`
- `archive_transition_restored_current`

## Relationship To Runtime Interface

This document makes the MCP surface concrete.

The broader runtime boundary is defined in:

- `session_lifecycle_runtime_interface.md`

The lifecycle behaviors behind these operations are defined in:

- `session_recent_state_artifact.md`
- `session_handoff_write_update_flow.md`
- `session_start_drill_in_flow.md`
- `session_archive_transition_mechanics.md`

## Constraints

This MCP surface should preserve the cluster's main design constraints:

- deterministic lifecycle enforcement
- token-efficient startup
- no prompt-enforced multi-artifact synchronization
- explicit operator-visible warnings on degraded state
- small, inspectable model-facing operation set

## Tradeoffs

## Benefits

- the LLM gets a clear operational contract
- backend code keeps control of lifecycle invariants
- the single-current model removes thread-identity ambiguity from the MCP surface

## Costs

- the runtime must define and maintain stable operation schemas
- some ad hoc flexibility is traded for stronger lifecycle guarantees

## Readiness

Readiness: high

Rationale:

The operation set and behavioral contract are concrete:

- the lifecycle MCP surface is small and high-level
- inputs and result semantics are explicit
- warning and failure behavior is visible
- write responses stay minimal and return references plus structured metadata only

The remaining work is implementation and schema definition, not unresolved interface behavior.
