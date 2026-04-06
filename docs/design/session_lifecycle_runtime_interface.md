---
title: Session Lifecycle Runtime Interface
doc_type: design
status: ready
updated: 2026-04-05
summary: Defines the deterministic runtime operations and MCP-facing boundary for recent-session lifecycle work under a single current carry-forward model.
---

# Session Lifecycle Runtime Interface

## Purpose

This document defines the runtime boundary that should enforce recent-session lifecycle behavior in Clauderfall.

The goal is to keep recent continuity deterministic, inspectable, and separate from prompt-driven file mutation.

## Design Position

Recent-session lifecycle behavior should be implemented through one dedicated runtime surface over the filesystem-backed session artifacts.

That runtime should own:

- startup-view read and validation
- current carry-forward read
- current handoff write
- current-to-history archive transition
- deterministic startup-index rebuild when projection state drifts

The runtime should not expose low-level file mutation as the primary lifecycle contract.

## Required Operations

The runtime boundary should expose these lifecycle-shaped operations:

- `session_read_startup_view()`
- `session_read_current()`
- `session_write_handoff(...)`
- `session_archive_current(...)`

These operations are sufficient for the single-current continuity model.

## Operation Semantics

### `session_read_startup_view()`

Returns the startup-oriented recent-session view.

The runtime should:

- read the persisted startup projection
- compare it against authoritative current and archived metadata
- rebuild deterministically when projection state is stale or malformed
- return compact startup artifacts plus operational metadata

### `session_read_current()`

Returns the authoritative current carry-forward record when one exists.

The runtime should fail explicitly when no current record exists rather than synthesizing one from history or startup summaries.

### `session_write_handoff(...)`

Persists the authoritative current carry-forward record.

Inputs should include:

- `title`
- `work_items`
- `thread_markdown`
- optional `flush_reason`

The runtime should:

- persist the current Markdown artifact and metadata
- mark the resulting checkpoint as authoritative current state
- refresh the startup projection
- return status-only success by default plus operational metadata

This operation replaces the previous current state if one exists.

### `session_archive_current(...)`

Archives the current carry-forward record into history and removes it from the current layer.

Inputs should include:

- `closure_summary`

The runtime should:

- read the authoritative current record
- write the archived history record
- remove the current record
- refresh the startup projection
- verify that the resulting state is consistent

## Result Shape

The runtime should return structured result objects carrying:

- operation status
- warning codes
- affected artifact or checkpoint references
- operation-specific metadata

This keeps policy visible and allows the MCP layer to stay thin.

## Invariants

The runtime must preserve these invariants:

- at most one current carry-forward record exists
- current state is authoritative for continuation
- startup projection is derived and replaceable
- history is authoritative for completed continuity state
- archive transitions do not leave durable middle states

## Recovery Rules

Deterministic recovery belongs at the runtime boundary.

Examples:

- startup index mismatch triggers rebuild
- malformed startup projection triggers warning plus rebuild
- archive transition failure prefers restoration to a valid current-state end state unless full archival can still complete as one bounded recovery action

## Constraints

This runtime shape should preserve the cluster's established constraints:

- deterministic lifecycle transitions
- minimal model-facing operation set
- strict current-versus-history boundary
- token-efficient startup
- no reliance on prompt-enforced synchronization

## Tradeoffs

## Benefits

- lifecycle policy stays centralized
- MCP handlers can remain thin adapters
- current and archived state stay clearly separated

## Costs

- the runtime must implement explicit projection rebuild and archive recovery behavior
- startup summaries remain dependent on structured metadata correctness

## Readiness

Readiness: high

Rationale:

The runtime boundary is now concrete:

- the lifecycle surface is small
- the current-state model is explicit
- projection rebuild and archive verification are first-class runtime concerns
- the remaining work is implementation, not unresolved surface design
