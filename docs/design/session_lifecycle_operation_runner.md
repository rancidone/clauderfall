---
title: Session Lifecycle Operation Runner
doc_type: design
status: draft
updated: 2026-03-27
summary: Defines the shared bounded operation and recovery mechanism used by the session-lifecycle backend service.
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

It exists specifically to support the recent-session lifecycle invariants already established in this design cluster.

## Why A Shared Runner

Several lifecycle methods already need more than a single write:

- handoff write persists the thread artifact and then refreshes a derived startup projection
- startup validation may warn and rebuild projection state before returning orientation data
- archive transition must coordinate history write, active-layer removal, index update, and final consistency checks

If each method implements its own local sequence, Clauderfall risks divergence in:

- recovery behavior
- warning thresholds
- postcondition checks
- result-shape semantics

The shared runner is the boundary that keeps those concerns consistent.

## Scope

The operation runner should be used for multi-step lifecycle operations that need bounded recovery or postcondition checks.

That likely includes:

- `write_active_thread_handoff`
- `rebuild_recent_session_index`
- `archive_completed_thread`
- startup validation paths inside `read_recent_session_startup_view`

It does not need to wrap every simple read path.

For example, a straightforward `read_active_thread` call may not need the full runner unless it grows recovery behavior later.

## Execution Model

The runner should operate as a bounded state-transition helper with explicit phases.

The preferred phases are:

1. prepare
2. execute
3. verify
4. recover if needed
5. return structured result

This keeps the lifecycle methods readable while still making the transition model inspectable.

## 1. Prepare

The prepare phase should gather and validate the state needed before mutation begins.

Typical work may include:

- resolve current authoritative artifact references
- read required metadata sidecars
- validate that required inputs are present
- compute any deterministic derived values needed for the operation

Prepare should fail early if the operation cannot safely proceed.

## 2. Execute

The execute phase should perform the intended bounded sequence of writes or updates for the operation.

Examples:

- persist the new active-thread checkpoint
- rebuild and persist the startup index
- write an archived history record
- remove an active artifact from the active layer

The sequence must be explicit and operation-specific, but the runner should provide the surrounding structure for consistent handling.

## 3. Verify

After execution, the runner should verify operation-specific postconditions before declaring success.

Verification is mandatory for lifecycle operations that claim deterministic behavior.

Examples:

- the current active-thread checkpoint matches the intended persisted handoff state
- the startup index projection reflects the authoritative thread sidecars
- the completed thread no longer appears in the active layer and now appears in history

Without verification, the runner is only a step sequencer, not an invariant boundary.

## 4. Recover

If execution or verification fails, the runner should invoke deterministic recovery toward an allowed valid end state.

Recovery policy remains operation-specific, but the runner should centralize the structure for:

- deciding whether recovery is allowed
- applying recovery steps
- re-verifying the recovered state
- producing warning or failure results

Examples:

- handoff may succeed with warning if the thread checkpoint committed but startup projection refresh remained stale and recoverable
- archive transition should prefer revert-to-active unless full archival can still be completed as one bounded recovery action
- startup validation may rebuild malformed projection state and return warning rather than failure

## 5. Return Structured Result

The runner should always return a structured lifecycle result object.

That object should include:

- `result`
- warning codes
- affected artifact/checkpoint references
- operation metadata

This is the object the backend service can pass upward to MCP handlers with minimal translation.

## Operation Policy Objects

Each lifecycle method should supply the runner with a small operation-specific policy or plan rather than embedding everything in one giant switch statement.

That policy should define at least:

- the ordered execution steps
- verification rules
- allowed recovery directions
- warning-versus-failure thresholds

This keeps the shared runner general enough for the session-lifecycle domain without turning it into an unbounded framework.

## Determinism Rule

The runner should not use heuristics or LLM interpretation during execution, verification, or recovery.

It should operate only on:

- explicit method inputs
- persisted artifact state
- deterministic projection logic
- controlled recovery rules

This is especially important for:

- startup index rebuild
- archive transition recovery
- success-versus-warning-versus-failure classification

## Logging And Inspection

The runner should make its phase outcomes inspectable in backend logs or debug traces.

Clauderfall does not need a full audit engine here, but it should be possible to tell:

- which lifecycle operation ran
- which phase failed, if any
- whether recovery was attempted
- what final result classification was returned

This supports debugging without pushing policy back into MCP handlers.

## Relation To Transactions

The runner is not required to be a database transaction abstraction.

Some underlying writes may not be truly atomic at the storage layer.

Its job is higher-level:

- coordinate bounded multi-step lifecycle operations
- verify postconditions
- recover deterministically to an allowed valid state

If stronger storage-level transaction support exists later, the runner may use it internally, but lifecycle correctness should not depend on pretending the filesystem itself is transactional.

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

- Clauderfall adds an internal abstraction that must stay scoped
- a poorly designed runner could become an over-general workflow engine
- operation policies still need careful design to avoid hidden branching

## Open Question

The main remaining question is whether the runner should expose explicit named phases as part of its internal API, or whether those phases should remain a conceptual design with a simpler implementation interface.

The design intent is clear either way, but the code shape could differ.

## Readiness

Readiness: medium

Rationale:

The structural role of the runner is concrete:

- one shared bounded mechanism
- explicit execution, verification, and recovery responsibilities
- operation-specific policy layered on top

The remaining gap is code-shape detail:

- how explicit the runner phases should be in the implementation-facing API
