---
title: Session Archive Transition Mechanics
doc_type: design
status: ready
updated: 2026-04-05
summary: Defines how the current carry-forward record leaves the current layer and becomes archived when completion is declared.
---

# Session Archive Transition Mechanics

## Purpose

This document defines the completion-to-archive transition for recent session state in Clauderfall.

The goal is to keep the boundary between current carry-forward state and history strict, immediate, and operationally dependable.

## Design Position

Archival should happen immediately when the current carry-forward record is completed.

Clauderfall should not support a soft intermediate state where work is complete in meaning but still present in the current layer waiting for later cleanup.

Completion should trigger the archive transition itself.

## Why Immediate Archival

The recent-session-state design depends on a strict separation between:

- the current carry-forward artifact used for continuation
- archived history records used for later inspection

If completion only marks the current record for later cleanup, the system reintroduces ambiguous states such as:

- complete but still current-shaped
- inactive but still present in carry-forward state
- archived in intent but not yet reflected in startup state

Those states make startup less trustworthy and weaken the main lifecycle boundary.

## Completion Transition

When the operator or system declares the current carry-forward record complete, Clauderfall should perform one archive transition flow:

1. finalize the current artifact as the last authoritative carry-forward record
2. write the archived history record
3. remove the current artifact from the current layer
4. update the repo-level recent-session index to remove current state and include the archived item in the bounded recent-completions view

The intended result is that, after a successful completion transition, no current carry-forward record exists.

## LLM And Engine Boundary

The archive transition should not be enforced by prompt discipline alone.

The LLM's role should be limited to designating completion and supplying any required closure content, such as:

- a completion decision or completion intent
- the `closure_summary`
- any final human-readable wording that belongs in the archived record

The deterministic lifecycle transition itself should be owned by the engine.

That means the engine, not the LLM skill, is responsible for:

1. reading the authoritative current state
2. creating the archived history record
3. removing the record from the current layer
4. updating the repo-level recent-session index
5. verifying that the resulting persisted state is consistent

## Failure Model

Archive should behave like one bounded lifecycle transition, not a best-effort background cleanup.

The runtime should prefer these outcomes:

- success only when archived state is consistent
- failure if the transition cannot reach a valid archived end state
- bounded deterministic recovery if partial work occurred

If partial work occurred and the runtime can restore a valid current-state end state, it should do so and return explicit failure plus warning detail.

## Postconditions

After a successful archive transition:

- the current layer contains no current record
- the archived history layer contains the new archived item
- the repo-level recent-session index reflects the absence of current state
- the bounded recent-completions view includes the archived item when within retention

Startup should never need to interpret a durable middle state for completion.

At startup, recent work should appear as either:

- current, through the current layer and current projection
- archived, through the history layer and recent-completions projection

## Constraints

This design should preserve the session-lifecycle constraints:

- strict current-versus-history boundary
- deterministic lifecycle transitions
- no durable middle state for completion
- token-efficient startup
- no prompt-enforced archive semantics

## Tradeoffs

## Benefits

- startup does not need to reason about quasi-current completed work
- history remains inspectable without polluting carry-forward state
- archive behavior stays easier to reason about

## Costs

- completion is a multi-step lifecycle transition that needs explicit verification
- recovery behavior must be designed rather than improvised in handlers

## Readiness

Readiness: high

Rationale:

The archive boundary is concrete:

- one current record may exist before completion
- none exists after successful archive
- history becomes the only durable location for completed continuity state
- startup never needs to interpret a half-archived current artifact
