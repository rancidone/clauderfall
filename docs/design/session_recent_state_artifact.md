---
title: Session Recent State Artifact
doc_type: design
status: ready
updated: 2026-03-27
summary: Defines the recent-session-state artifact contract spanning the repo-level startup index, active thread artifacts, and archived thread history.
---

# Session Recent State Artifact

## Purpose

This document defines the artifact contract for recent session state in Clauderfall.

The goal is to support reliable handoff and token-efficient session startup without turning recent continuity into a vague long-term memory blob.

## Design Position

Clauderfall should represent recent session state as three related layers:

- one repo-level recent-session index artifact
- one active artifact per active thread
- one history layer for archived completed threads

The repo-level index is the default startup entry point.

It should support quick orientation across the current working context without forcing the operator to load every active thread artifact up front.

The active thread artifact is authoritative for that thread's current carry-forward state.

The history layer preserves completed threads for later inspection while keeping them out of active startup context.

## Why Not One Shared Session-State Blob

A single repo-level blob would make startup simple in the short term, but it would blur parallel active work together and encourage unbounded accumulation of stale detail.

That would work against the brief's main constraint:

- preserve decision-relevant recent state
- keep carry-forward context bounded
- favor token economy over broad retention

## Artifact Layers

## Repo-Level Recent-Session Index

The repo-level recent-session index is a persisted startup-oriented summary.

It should contain:

- compact projections of active threads
- a bounded `last N` view of recent completed threads
- explicit references into active thread artifacts and archived history

It should not duplicate the full state of every active thread.

Its job is orientation first:

- show what is currently active
- show what recently completed
- let the operator decide whether to drill into a thread

## Active Thread Artifact

Each active thread should have its own persisted active artifact.

This artifact is authoritative for the thread's current carry-forward state.

It should stay bounded and contain only the information needed to continue or hand off the thread honestly.

An active thread artifact is active by virtue of existing in the active layer.

It does not need a persistent `status` field to restate that fact.

### Authoritative Active-Thread Fields

The minimum authoritative metadata for an active thread artifact should be:

- `thread_id`
- `title`
- `current_intent_summary`
- `next_suggested_action`
- `updated_at`

These fields should be explicit structured metadata.

They should not be recovered heuristically from prose.

## Archived History Record

When a thread completes, its active artifact should leave the active layer immediately.

Clauderfall should write an archived history record with this compact metadata:

- `thread_id`
- `title`
- `closure_summary`
- `closed_at`
- `archived_artifact_ref`

The archived readable artifact remains inspectable on demand through the history layer.

Immediate archival removes completed work from active carry-forward state.

It does not make the thread unreadable.

## Authority And Projection

The active thread artifact should be authoritative for thread-specific state.

The repo-level recent-session index should be a persisted projection over thread metadata, not a co-equal editable source of truth for the same facts.

This keeps startup cheap without creating a second thread-state record that must be synchronized by hand.

For active threads:

- the thread artifact owns canonical thread metadata
- the repo index owns startup-oriented aggregation
- any thread fields shown in the repo index must come from explicit structured thread metadata

The current artifact persistence format already prefers Markdown plus an adjacent YAML sidecar.

That sidecar is the right source for reliable projection.

## Startup View

The repo-level recent-session index should expose a compact per-thread startup view for active work:

- `thread_id`
- `title`
- `current_intent_summary`
- `last_updated_at`
- `thread_artifact_ref`
- `next_suggested_action`

For recent completed work retained in the bounded `last N` startup view, the index should expose:

- `thread_id`
- `title`
- `closure_summary`
- `closed_at`
- `history_ref`

This keeps startup oriented around current work while preserving light visibility into recent closure.

## Lifecycle Boundary

The lifecycle boundary between active carry-forward state and history should be strict.

The active layer contains only active thread artifacts.

Completed threads should not remain as lightweight inactive active artifacts.

When a thread completes:

- the active artifact leaves the active layer
- the archived history record is written
- the repo-level index updates its bounded recent-completions view

This avoids muddy intermediate states like:

- active but nearly archived
- inactive but still active-shaped
- complete but still present in carry-forward state

## Constraints

This design should preserve the Discovery brief's constraints:

- token-efficient startup is primary
- active carry-forward state must stay bounded
- reading recent state must not force continuation of the same topic
- recent closed work should remain visible only through a bounded summary window plus history access
- parallel active work should be legible without heavy manual workstream management

## Related Lifecycle Units

This document defines the artifact contract only.

The concrete lifecycle behavior that applies to this contract is now defined in companion design units:

- `session_handoff_write_update_flow.md` - thread-first handoff writes and derived repo-index refresh
- `session_start_drill_in_flow.md` - startup orientation, deterministic ordering, and explicit drill-in
- `session_archive_transition_mechanics.md` - immediate completion-to-archive transition and strict active/history boundary
- `session_lifecycle_runtime_interface.md` - deterministic backend enforcement and MCP-facing lifecycle operations

## Tradeoffs

## Benefits

- startup can begin from one compact repo-level index
- active thread detail is only loaded on demand
- parallel active work stays separated without requiring separate startup flows
- active state and history remain clearly distinct

## Costs

- the system must maintain a reliable projection from thread metadata into the repo index
- archival transition behavior must be explicit to avoid partial updates
- the quality of startup orientation depends on thread metadata staying concise and current

## Readiness

Readiness: high

Rationale:

The core artifact contract is concrete enough that downstream lifecycle design did not need to invent major structural decisions.

The artifact contract now has explicit companion units covering:

- handoff write/update flow
- archive transition mechanics
- start-session drill-in flow
- runtime enforcement and MCP-facing lifecycle operations

Those behaviors remain intentionally separated from this artifact contract rather than folded back into it.
