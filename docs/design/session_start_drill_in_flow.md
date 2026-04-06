---
title: Session Start Drill-In Flow
doc_type: design
status: ready
updated: 2026-04-05
summary: Defines how startup orients from the repo-level recent-session index and drills into the current carry-forward record only when needed.
---

# Session Start Drill-In Flow

## Purpose

This document defines the startup interaction flow for recent session state after the repo-level recent-session index and current carry-forward artifact already exist.

The goal is to preserve cheap orientation at session start without forcing immediate continuation.

## Design Position

Session start should begin from the repo-level recent-session index by default.

The system should not immediately load the full current carry-forward artifact unless:

- the operator chooses to continue current work
- the startup flow needs current detail to resolve ambiguity
- repo-level projection recovery requires validation against current metadata

This keeps startup token-efficient while preserving a deliberate boundary between orientation and continuation.

## Startup Entry Point

The repo-level recent-session index is the normal startup entry point.

Startup should present:

- the current carry-forward summary when one exists
- a bounded recent-completions view
- enough metadata to decide whether to continue prior work or begin something new

The startup entry should not assume that the presence of current state is an instruction to resume automatically.

## Default Startup Sequence

The default startup flow should be:

1. load the repo-level recent-session index
2. validate that the index projection is usable
3. warn and rebuild deterministically if the projection is stale, malformed, or missing required data
4. present the compact startup view
5. allow the operator to either:
   - drill into the current carry-forward record
   - remain at orientation and start a new direction
   - inspect a recent completed item through history

The key rule is that startup orientation happens before continuation.

## Operator Choices

After orientation, the operator should have three valid moves:

- continue the current carry-forward record
- inspect but not continue the current carry-forward record
- start something new without selecting current state

Clauderfall should preserve all three as first-class paths.

The startup flow should not treat the presence of current state as an instruction to resume it automatically.

## Current-State Drill-In

When the operator chooses the current record, Clauderfall should then load that record's authoritative artifact.

Drill-in should expose:

- the current title
- the ordered next work items
- the readable carry-forward artifact for fuller context when needed

The readable artifact is loaded because the operator selected that boundary, not because startup itself requires all current prose up front.

## New-Direction Path

If the operator chooses not to continue the current record, startup should still succeed.

That path should:

- keep recent state visible as orientation context
- avoid implicitly attaching new work to current carry-forward state
- allow the operator to begin a new direction cleanly

Reading recent session state must inform startup, not trap it.

## Completed-Record Access

Recent completed records should remain visible through the bounded recent-completions section of the repo-level index.

Selecting one of those items should be an inspection move through history, not a hidden reactivation of current state.

If the operator wants to reuse prior completed work as the new current state, that should be a deliberate action rather than a side effect of inspection.

## Constraints

This flow must preserve the session-lifecycle constraints:

- startup should be token-efficient
- startup should default to a compact repo-level view
- current detail should load on demand
- recent state should support continuation without forcing it
- history inspection should stay distinct from active carry-forward state

## Tradeoffs

## Benefits

- startup remains cheap because there is at most one current record to summarize
- the operator stays in control of whether orientation becomes continuation
- current detail is loaded only when its value is clear

## Costs

- startup still needs an explicit orientation step rather than assuming automatic resume
- some sessions will involve one extra selection step before full continuation context loads
- the flow depends on the repo-level index being a reliable enough startup projection

## Readiness

Readiness: high

Rationale:

The startup boundary is now concrete:

- repo-level orientation comes first
- current-state drill-in is explicit
- new-direction startup remains valid
- history inspection stays separate from reactivation
- the flow no longer depends on multi-thread selection behavior
