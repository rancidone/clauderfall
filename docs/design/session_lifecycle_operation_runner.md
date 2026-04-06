---
title: Session Lifecycle Operation Runner
doc_type: design
status: ready
updated: 2026-04-05
summary: Defines the shared bounded operation and recovery mechanism used by the session-lifecycle backend service under the single-current model.
---

# Session Lifecycle Operation Runner

## Purpose

This document defines the shared bounded operation and recovery mechanism inside the session-lifecycle backend service.

The goal is to keep multi-step lifecycle behavior consistent across handoff writes, startup recovery, and archive transitions without duplicating transition logic in each service method.

## Design Position

The session-lifecycle backend should use one shared operation runner for bounded multi-step lifecycle work.

That runner should coordinate:

- ordered step execution
- postcondition verification
- warning generation
- deterministic recovery toward a valid end state

It should not be a generic workflow engine.

## Why A Shared Runner

Several lifecycle methods already need more than a single write:

- handoff write persists the current record and then refreshes a derived startup projection
- startup validation may warn and rebuild projection state before returning orientation data
- archive transition must coordinate history write, current-layer removal, index update, and final consistency checks

If each method implements its own local sequence, Clauderfall risks divergence in:

- recovery behavior
- warning thresholds
- postcondition checks
- result-shape semantics

## Scope

The operation runner should be used for multi-step lifecycle operations that need bounded recovery or postcondition checks.

That likely includes:

- `session_write_handoff`
- `session_archive_current`
- startup validation paths inside `session_read_startup_view`

## Execution Model

The runner should operate as a bounded state-transition helper with explicit phases:

1. prepare
2. execute
3. verify
4. recover if needed
5. return structured result

## Determinism Rule

The runner should not use heuristics or LLM interpretation during execution, verification, or recovery.

It should operate only on:

- explicit method inputs
- persisted artifact state
- deterministic projection logic
- controlled recovery rules

## Example Postconditions

Examples of the postconditions the runner should help enforce:

- the current checkpoint matches the intended persisted handoff state
- the startup index projection reflects the authoritative current metadata
- no current record remains after successful archive and the new history record exists

## Constraints

This mechanism should preserve the cluster's main runtime constraints:

- deterministic lifecycle behavior
- consistent warning and failure semantics
- no durable middle states for archive transitions
- recoverable startup projection drift
- minimal policy leakage into MCP handlers

## Tradeoffs

## Benefits

- lifecycle methods stay simpler and more consistent
- recovery behavior is easier to test centrally
- result semantics stay aligned across operations

## Costs

- Clauderfall needs an explicit lifecycle helper instead of ad hoc method-local sequencing

## Readiness

Readiness: high

Rationale:

The runner's job is now well-bounded:

- coordinate the few multi-step lifecycle transitions that remain
- verify current-state and archive invariants
- keep recovery behavior centralized
