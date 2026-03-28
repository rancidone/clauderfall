---
title: Session Lifecycle MCP Interface
doc_type: design
status: draft
updated: 2026-03-27
summary: Defines the high-level MCP operations, inputs, and result shapes for recent-session lifecycle work.
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

- `read_recent_session_startup_view`
- `read_active_thread`
- `write_active_thread_handoff`
- `rebuild_recent_session_index`
- `archive_completed_thread`

This is intentionally small.

It covers the session-lifecycle behaviors already designed without turning MCP into a generic artifact-editing API.

## Shared Response Shape

Every lifecycle MCP operation should return a structured response with the same top-level shape:

- `result`
- `warnings`
- `artifacts`
- `metadata`

### `result`

`result` should use a small controlled set:

- `success`
- `warning`
- `failure`

`success` means the requested lifecycle operation completed and its postconditions were met.

`warning` means the requested operation completed, but the runtime also had to perform deterministic recovery or observed degraded-but-usable state that the operator should know about.

`failure` means the requested operation did not commit the intended lifecycle transition.

### `warnings`

`warnings` should be a short list of machine-usable warning codes with optional short human-readable messages.

The LLM should not need to parse long prose to determine whether startup state was stale, whether a rebuild was performed, or whether completion reverted to active.

### `artifacts`

`artifacts` should contain references to the artifact identities or current checkpoints materially affected by the operation.

This lets the LLM and operator understand which persisted state is now authoritative.

Responses should stay minimal.

Lifecycle MCP operations should return references and concise structured metadata, not full readable artifact bodies.

### `metadata`

`metadata` should contain operation-specific structured fields such as:

- `thread_id`
- `checkpoint_id`
- `rebuilt`
- `recovered`
- `active_thread_count`

This field should stay operational and concise.

## 1. `read_recent_session_startup_view`

## Purpose

Return the startup-oriented recent-session view used to begin session orientation.

## Inputs

This operation should require no thread-specific input.

Optional inputs may include:

- `force_rebuild: boolean`

`force_rebuild` should default to `false`.

If `true`, the runtime may rebuild the repo-level recent-session index before returning the startup view.

## Behavior

By default, the runtime should:

1. read the persisted repo-level recent-session index
2. validate it against active-thread metadata
3. rebuild deterministically if the index is stale, malformed, or missing required projection data
4. return the startup view

## Result Metadata

The response metadata should include at least:

- `rebuilt: boolean`
- `active_thread_count: number`
- `recent_completed_count: number`
- `startup_index_checkpoint_id`

## Returned View

The startup payload should include:

- active thread summaries
- recent completed thread summaries
- any warnings about deterministic rebuild or malformed persisted startup state

The returned active thread list should already be deterministically ordered:

- `updated_at` descending
- stable secondary key such as `thread_id`

## 2. `read_active_thread`

## Purpose

Return the authoritative state for one active thread after the operator or workflow chooses to drill into it.

## Inputs

Required:

- `thread_id`

## Behavior

The runtime should resolve the authoritative current active-thread artifact and return:

- structured metadata from the thread sidecar
- the readable thread artifact content
- references to the current artifact checkpoint

If the requested thread is not active, the operation should fail explicitly rather than silently reading archived history instead.

## Result Metadata

The response metadata should include at least:

- `thread_id`
- `artifact_id`
- `checkpoint_id`
- `updated_at`

## 3. `write_active_thread_handoff`

## Purpose

Persist a handoff update for one active thread using the thread-first write path.

## Inputs

Required:

- `thread_id`
- `title`
- `current_intent_summary`
- `next_suggested_action`
- `thread_markdown`

Optional:

- `flush_reason`

`flush_reason` should default to a controlled operational value appropriate for handoff persistence.

## Behavior

The runtime should:

1. persist the active-thread Markdown artifact
2. persist the authoritative thread metadata sidecar
3. checkpoint the thread artifact pair together
4. refresh or derive the repo-level recent-session index projection for that thread

The operation should succeed once the authoritative thread checkpoint is durable.

If repo-index projection refresh fails after thread persistence succeeds, the operation may return `warning` rather than `failure`, provided the runtime marks the startup projection as stale and recoverable.

## Result Metadata

The response metadata should include at least:

- `thread_id`
- `artifact_id`
- `checkpoint_id`
- `startup_index_updated: boolean`
- `projection_stale: boolean`

The response should not include the full persisted thread Markdown body.

If the caller needs authoritative readable content after the write, it should use `read_active_thread`.

## 4. `rebuild_recent_session_index`

## Purpose

Deterministically regenerate the repo-level recent-session index from authoritative metadata.

## Inputs

This operation should require no thread-specific input.

Optional inputs may include:

- `reason`

`reason` should be a controlled value such as:

- `startup_validation`
- `handoff_recovery`
- `operator_requested`

## Behavior

The runtime should:

1. read authoritative active-thread sidecars
2. read the bounded recent-completions history metadata needed for startup projection
3. regenerate the repo-level recent-session index mechanically
4. persist the rebuilt startup index as the current projection

This operation must not ask the LLM to regenerate summaries from prose.

## Result Metadata

The response metadata should include at least:

- `rebuilt: true`
- `active_thread_count`
- `recent_completed_count`
- `startup_index_checkpoint_id`

## 5. `archive_completed_thread`

## Purpose

Perform the immediate completion-to-archive transition for one thread.

## Inputs

Required:

- `thread_id`
- `closure_summary`

Optional:

- `archived_thread_markdown`

If omitted, the runtime may archive the current thread artifact content as the final readable record plus the provided closure metadata.

## Behavior

The runtime should:

1. resolve the authoritative active-thread state
2. write the archived history record
3. remove the thread from the active layer
4. update the repo-level recent-session index
5. verify the resulting archived-state postconditions

The operation should return `failure` if the runtime cannot reach a consistent archived state.

If partial work occurred and deterministic recovery restored the thread to active, the operation should still return `failure` plus an explicit warning that completion did not commit.

## Result Metadata

The response metadata should include at least:

- `thread_id`
- `archived: boolean`
- `history_checkpoint_id`
- `restored_to_active: boolean`
- `startup_index_updated: boolean`

The response should not include the full archived readable artifact body.

## Error Semantics

The MCP surface should prefer explicit machine-usable failure codes over vague prose.

Likely failure or warning codes include:

- `startup_index_stale_rebuilt`
- `startup_index_malformed_rebuilt`
- `active_thread_not_found`
- `thread_handoff_persist_failed`
- `startup_index_refresh_failed`
- `archive_transition_failed`
- `archive_transition_reverted_to_active`

The exact code list can evolve, but the runtime should keep it controlled and operational.

## Checkpoint Expectations

Lifecycle operations that persist artifacts should return the current checkpoint information for any newly written authoritative state.

This should align with the existing checkpoint model:

- one stable `artifact_id`
- one new `checkpoint_id` per successful flush
- explicit current-checkpoint semantics

The MCP layer should not hide whether a lifecycle operation created a new checkpoint.

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
- implementation can evolve below MCP without changing the model-facing contract immediately

## Costs

- the runtime must define and maintain stable operation schemas
- some ad hoc flexibility is traded for stronger lifecycle guarantees
- debugging may still require lower-level tools outside the normal lifecycle path

## Readiness

Readiness: high

Rationale:

The operation set and behavioral contract are concrete:

- the lifecycle MCP surface is small and high-level
- inputs and result semantics are explicit
- warning and failure behavior is visible
- write responses stay minimal and return references plus structured metadata only

The remaining work is implementation and schema definition, not unresolved interface behavior.
