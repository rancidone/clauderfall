---
title: Session Start Drill-In Flow
doc_type: design
status: ready
updated: 2026-03-27
summary: Defines how startup orients from the repo-level recent-session index and drills into an active thread only when needed.
---

# Session Start Drill-In Flow

## Purpose

This document defines the startup interaction flow for recent session state after the repo-level recent-session index and active thread artifacts already exist.

The goal is to preserve cheap orientation at session start without forcing immediate continuation of any one active thread.

## Design Position

Session start should begin from the repo-level recent-session index by default.

The system should not immediately load full active-thread artifacts unless:

- the operator chooses a thread to continue
- the startup flow needs thread detail to resolve ambiguity
- repo-level projection recovery requires validation against thread metadata

This keeps startup token-efficient while preserving a deliberate boundary between orientation and continuation.

## Startup Entry Point

The repo-level recent-session index is the normal startup entry point.

Startup should present:

- active threads from the derived startup view
- a bounded recent-completions view
- enough thread metadata to decide whether to continue prior work or begin something new

The startup entry should not assume that the most recently updated thread is the thread the operator wants.

If multiple active threads are present, startup should sort and list them deterministically rather than computing a recommended thread.

## Default Startup Sequence

The default startup flow should be:

1. load the repo-level recent-session index
2. validate that the index projection is usable
3. warn and rebuild deterministically if the projection is stale, malformed, or missing required data
4. present the compact startup view
5. allow the operator to either:
   - drill into one active thread
   - remain at orientation and start a new direction
   - inspect a recent completed thread through history

The key rule is that startup orientation happens before thread commitment.

## Operator Choices

After orientation, the operator should have three valid moves:

- continue an active thread
- inspect but not continue an active thread
- start something new without selecting any active thread

Clauderfall should preserve all three as first-class paths.

The startup flow should not treat the presence of active threads as an instruction to resume one automatically.

Ordering should be simple and inspectable:

- sort active threads by `updated_at` descending
- break ties with a stable secondary key such as `thread_id`
- present the ordered list without a recommendation badge or implicit default selection

## Active-Thread Drill-In

When the operator chooses an active thread, Clauderfall should then load that thread's authoritative artifact.

Drill-in should expose:

- the thread title
- the current intent summary
- the next suggested action
- the readable thread artifact for fuller context when needed

The thread artifact is loaded because the operator selected that boundary, not because startup itself requires all thread prose up front.

## New-Direction Path

If the operator chooses not to continue any active thread, startup should still succeed.

That path should:

- keep recent state visible as orientation context
- avoid implicitly attaching the new session to an existing thread
- allow the operator to begin a new direction cleanly

Reading recent session state must inform startup, not trap it.

## Completed-Thread Access

Recent completed threads should remain visible through the bounded recent-completions section of the repo-level index.

Selecting one of those items should be an inspection move through history, not a hidden reactivation of the thread.

If the operator wants to reopen prior completed work, that should be a deliberate action rather than a side effect of inspection.

## Constraints

This flow must preserve the session-lifecycle constraints:

- startup should be token-efficient
- startup should default to a compact repo-level view
- active thread detail should load on demand
- recent state should support continuation without forcing it
- history inspection should stay distinct from active carry-forward state

## Tradeoffs

## Benefits

- startup remains cheap even when multiple active threads exist
- the operator stays in control of whether orientation becomes continuation
- thread detail is loaded only when its value is clear

## Costs

- startup needs an explicit orientation step rather than assuming automatic resume
- some sessions will involve one extra selection step before full continuation context loads
- the flow depends on the repo-level index being a reliable enough startup projection

## Readiness

Readiness: high

Rationale:

The startup boundary is now concrete:

- repo-level orientation comes first
- thread drill-in is explicit
- new-direction startup remains valid
- history inspection stays separate from reactivation
- multiple active threads are handled by deterministic list ordering rather than inferred recommendation
