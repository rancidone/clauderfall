---
title: Session Recent State Artifact
doc_type: design
status: ready
updated: 2026-04-05
summary: Defines the recent-session-state artifact contract spanning a repo-level startup index, one current carry-forward record, and archived history.
---

# Session Recent State Artifact

## Purpose

This document defines the artifact contract for recent session state in Clauderfall.

The goal is to support reliable handoff and token-efficient session startup without turning recent continuity into a vague long-term memory blob.

## Design Position

Clauderfall should represent recent session state as three related layers:

- one repo-level recent-session index artifact
- zero or one current carry-forward state record
- one history layer for archived completed work

The repo-level index is the default startup entry point.

It should support quick orientation without forcing the operator to load the full current carry-forward note up front.

The current carry-forward state record is authoritative for the repo's active continuation state.

The history layer preserves completed work for later inspection while keeping it out of active startup context.

## Why Not Multiple Active Threads

A multi-thread active model raises coordination cost at exactly the layer that should stay cheap.

It asks startup to choose among parallel active workstreams, asks handoff to manage thread identity, and creates ambiguity around whether new work should attach to an existing thread or replace it.

That works against the main continuity goals:

- preserve decision-relevant recent state
- keep carry-forward context bounded
- favor token economy over workstream management

## Artifact Layers

## Repo-Level Recent-Session Index

The repo-level recent-session index is a persisted startup-oriented summary.

It should contain:

- a compact summary of the current carry-forward record when one exists
- a bounded `last N` view of recent completed records
- explicit references into the current record and archived history

It should not duplicate the full current readable note.

Its job is orientation first:

- show whether current carry-forward state exists
- show what it is about
- show what recently completed
- let the operator decide whether to continue current work or start something new

## Current Carry-Forward State Record

Clauderfall should maintain at most one current carry-forward state record.

This record is authoritative for the repo's active continuation state.

It should stay bounded and contain only the ordered next work items plus the readable context needed to execute them honestly.

The current record is active by virtue of existing in the current layer.

It does not need a separate persistent status field to restate that fact.

### Authoritative Current-State Fields

The minimum authoritative metadata for the current carry-forward state record should be:

- `title`
- `work_items`
- `updated_at`

These fields should be explicit structured metadata.

The readable note should live in the paired Markdown artifact.

`work_items` should not be recovered heuristically from prose.

## Archived History Record

When the current record completes, it should leave the current layer immediately.

Clauderfall should write an archived history record with this compact metadata:

- `history_id`
- `title`
- `closure_summary`
- `closed_at`
- `archived_artifact_ref`

The archived readable artifact remains inspectable on demand through the history layer.

Immediate archival removes completed work from current carry-forward state.

It does not make the work unreadable.

## Authority And Projection

The current carry-forward state record should be authoritative for active continuation state.

The repo-level recent-session index should be a persisted projection over current metadata, not a co-equal editable source of truth for the same facts.

This keeps startup cheap without creating a second current-state record that must be synchronized by hand.

For current continuity state:

- the current record owns canonical metadata
- the repo index owns startup-oriented aggregation
- any current fields shown in the repo index must come from explicit structured current metadata

The current session persistence format should keep these fields explicit and structured while storing readable carry-forward context in the paired Markdown artifact.

## Startup View

The repo-level recent-session index should expose a compact startup view for active work:

- `has_current`
- `title`
- `work_items`
- `last_updated_at`
- `current_artifact_ref`

For recent completed work retained in the bounded `last N` startup view, the index should expose:

- `history_id`
- `title`
- `closure_summary`
- `closed_at`
- `history_ref`

This keeps startup oriented around current work while preserving light visibility into recent closure.

## Lifecycle Boundary

The lifecycle boundary between current carry-forward state and history should be strict.

The current layer contains zero or one current state record.

Completed work should not remain as a lightweight inactive current artifact.

When work completes:

- the current record leaves the current layer
- the archived history record is written
- the repo-level index updates its bounded recent-completions view

This avoids muddy intermediate states like:

- current but nearly archived
- inactive but still current-shaped
- complete but still present in carry-forward state

## Constraints

This design should preserve the Discovery brief's constraints:

- token-efficient startup is primary
- active carry-forward state must stay bounded
- reading recent state must not force continuation of the same topic
- recent closed work should remain visible only through a bounded summary window plus history access
- continuity should not require active workstream management

## Related Lifecycle Units

This document defines the artifact contract only.

The concrete lifecycle behavior that applies to this contract is now defined in companion design units:

- `session_handoff_write_update_flow.md` - current-state handoff writes and derived repo-index refresh
- `session_start_drill_in_flow.md` - startup orientation and explicit current-state drill-in
- `session_archive_transition_mechanics.md` - immediate completion-to-archive transition and strict current/history boundary
- `session_lifecycle_runtime_interface.md` - deterministic backend enforcement and MCP-facing lifecycle operations

## Tradeoffs

## Benefits

- startup can begin from one compact repo-level index
- current detail is only loaded on demand
- continuity stays simple because there is only one authoritative active record
- current state and history remain clearly distinct

## Costs

- the system must maintain a reliable projection from current metadata into the repo index
- replacing current state requires explicit overwrite semantics
- the quality of startup orientation depends on current metadata staying concise and current

## Readiness

Readiness: high

Rationale:

The core artifact contract is concrete enough that downstream lifecycle design does not need to invent major structural decisions.

The artifact contract now has explicit companion units covering:

- handoff write/update flow
- archive transition mechanics
- start-session drill-in flow
- runtime enforcement and MCP-facing lifecycle operations

Those behaviors remain intentionally separated from this artifact contract rather than folded back into it.
