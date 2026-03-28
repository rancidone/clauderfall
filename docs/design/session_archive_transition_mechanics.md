---
title: Session Archive Transition Mechanics
doc_type: design
status: ready
updated: 2026-03-27
summary: Defines how an active thread leaves the active layer and becomes archived when completion is declared.
---

# Session Archive Transition Mechanics

## Purpose

This document defines the completion-to-archive transition for recent session state in Clauderfall.

The goal is to keep the boundary between active carry-forward state and history strict, immediate, and operationally dependable.

## Design Position

Archival should happen immediately when a thread is completed.

Clauderfall should not support a soft intermediate state where a thread is complete in meaning but still present in the active layer waiting for later cleanup.

Completion should trigger the archive transition itself.

## Why Immediate Archival

The recent-session-state design depends on a strict separation between:

- active thread artifacts used for carry-forward work
- archived history records used for later inspection

If completion only marks a thread for later cleanup, the system reintroduces ambiguous states such as:

- complete but still active-shaped
- inactive but still present in carry-forward state
- archived in intent but not yet reflected in startup state

Those states make startup less trustworthy and weaken the main lifecycle boundary.

## Completion Transition

When the operator or system declares an active thread complete, Clauderfall should perform one archive transition flow:

1. finalize the active thread artifact as the last authoritative thread-state record
2. write the archived history record for that thread
3. remove the active thread artifact from the active layer
4. update the repo-level recent-session index to remove the thread from active work and include it in the bounded recent-completions view

The intended result is that, after a successful completion transition, the thread no longer exists in the active layer at all.

## LLM And Engine Boundary

The archive transition should not be enforced by prompt discipline alone.

The LLM's role should be limited to designating completion and supplying any required closure content, such as:

- a completion decision or completion intent
- the `closure_summary`
- any final human-readable thread wording that belongs in the archived record

The deterministic lifecycle transition itself should be owned by the engine.

That means the engine, not the LLM skill, is responsible for:

1. reading the authoritative active-thread state
2. creating the archived history record
3. removing the thread from the active layer
4. updating the repo-level recent-session index
5. verifying that the resulting persisted state is consistent

If this boundary is not explicit, Clauderfall is not really enforcing an archive transition contract.

## Atomicity Goal

This transition should be as atomic as the persistence model can practically make it.

The system should treat completion as successful only when the archive transition has reached a consistent state across:

- the archived history record
- the active-layer removal
- the repo-level recent-session index projection

The thread should not be presented as completed if it is still partially active in persisted state.

## Authority During Transition

Before completion, the active thread artifact remains authoritative for current thread state.

At the moment of successful completion transition:

- the archived history record becomes the durable history entry
- the active layer stops carrying that thread
- the repo-level recent-session index reflects the thread only through recent completion metadata

There should not be a persistent dual-presence state where the same thread is both active and archived for normal operation.

## Failure Model

Because completion changes lifecycle state rather than merely updating thread content, failure handling should be stricter than ordinary handoff projection lag.

The completion transition should be treated as failed if Clauderfall cannot reach a consistent archived state.

In practice:

- if archived history record creation fails, completion fails
- if active-layer removal fails, completion fails
- if repo-level recent-session index update fails, completion fails

This is intentionally stricter than the thread-first handoff write path.

The cost is higher coordination during completion.

The benefit is that lifecycle state remains trustworthy.

The enforcement mechanism is therefore runtime state transition logic, not an LLM-authored multi-document update.

## Recovery Rule

If a completion transition fails partway through, Clauderfall should recover toward one of two valid states only:

- still active
- fully archived

It should not leave the thread in a normal partially transitioned state.

Recovery should be deterministic and metadata-driven where possible.

The preferred recovery direction should be revert to active unless the full archive transition commits cleanly.

This is the safer default because it preserves the pre-existing authoritative state when completion cannot be durably established across the full lifecycle boundary.

The system should either:

- roll forward only if the engine can still deterministically complete the remaining archival steps as part of the same bounded recovery operation
- otherwise restore the thread to active status and surface a warning that completion did not commit

## Startup Consequence

Startup should never need to interpret a durable middle state for thread completion.

At startup, a thread should appear as either:

- active, through the active layer and active-thread projection
- archived, through the history layer and bounded recent-completions projection

This keeps session orientation simple and avoids lifecycle ambiguity.

## Constraints

This design preserves the recent-session-state constraints:

- active carry-forward state stays strict and bounded
- recent completed work stays visible without polluting active context
- startup does not need to reason about quasi-active completed threads
- lifecycle semantics remain inspectable and deterministic

## Tradeoffs

## Benefits

- active and archived state remain clearly separated
- startup and handoff behavior stay easier to reason about
- completion is a trustworthy lifecycle event rather than a hint for cleanup

## Costs

- completion flow is more coordination-heavy than ordinary handoff updates
- failure handling must support deterministic recovery to a valid state
- the system cannot rely on background cleanup to reconcile lifecycle state later

## Open Question

The main remaining implementation-facing question is whether the runtime should expose the archive transition as a single named transaction-like operation in artifact services, or as a smaller sequence wrapped by a higher-level lifecycle coordinator.

## Readiness

Readiness: high

Rationale:

The lifecycle boundary is now concrete:

- completion implies immediate archival
- partial completion is not a valid steady state
- completion success requires a consistent archived result
- the LLM only signals completion and provides closure content
- the engine owns deterministic archive-state enforcement
- failure recovery prefers revert-to-active unless full archival can still complete cleanly as one bounded recovery action

The remaining question is structural implementation detail rather than unresolved lifecycle behavior.
