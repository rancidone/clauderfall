---
title: Session Lifecycle Backend Service
doc_type: design
status: draft
updated: 2026-04-02
summary: Defines the backend service shape that should own recent-session lifecycle operations and enforce lifecycle invariants.
---

# Session Lifecycle Backend Service

## Purpose

This document defines the backend service shape that should implement recent-session lifecycle behavior in Clauderfall.

The goal is to keep lifecycle invariants centralized in one deterministic runtime boundary rather than scattering them across MCP handlers or ad hoc persistence code.

## Design Position

Clauderfall should use a dedicated session-lifecycle backend service.

That service should own the high-level lifecycle operations already defined by the runtime and MCP interface docs:

- startup-view read and validation
- active-thread read
- active-thread handoff write
- recent-session index rebuild
- thread archive transition

The MCP layer should delegate to this service rather than reimplement lifecycle behavior itself.

## Why A Dedicated Service

The session-lifecycle cluster now includes several invariants that need to stay aligned:

- active threads are authoritative for carry-forward state
- the repo-level recent-session index is a deterministic projection
- startup may rebuild stale or malformed projection state
- completion transitions must not leave durable middle states
- write operations and archive operations have different failure semantics

If these rules live partly in MCP handlers, partly in artifact persistence helpers, and partly in prompt conventions, they will drift.

The backend needs one place that owns the lifecycle contract.

## Service Boundary

The session-lifecycle service should sit above lower-level artifact and storage primitives.

It should depend on internal services such as:

- artifact read/write services
- checkpoint persistence services
- projection builders
- history lookup services

But those lower-level services should not own recent-session lifecycle policy.

The lifecycle service is where Clauderfall decides:

- what operation is being attempted
- what invariants must hold before success is returned
- what deterministic recovery is allowed
- what warnings or failures should be surfaced upward

## Recommended Shape

The preferred shape is:

- one `SessionLifecycleService` or equivalent coordinator
- one shared bounded operation/recovery mechanism inside that service for multi-step lifecycle transitions
- a small set of lifecycle-shaped methods matching the MCP surface
- internal helper collaborators for artifact persistence and projection work

This keeps one clear mapping:

- MCP operation
- backend lifecycle method
- deterministic enforcement logic

without forcing the MCP layer to orchestrate multi-step transitions itself.

The lifecycle methods should not each hand-roll their own transition control flow.

The service should centralize the mechanics for:

- step execution
- postcondition verification
- warning emission
- deterministic recovery or rollback-to-valid-state behavior

## Internal Responsibilities

The lifecycle service should own:

- validating startup index freshness against active-thread metadata
- invoking deterministic recent-session index rebuild when needed
- persisting active-thread handoff updates through the thread-first path
- executing archive transitions with correct completion semantics
- deciding whether a partial failure produces `warning` or `failure`
- returning structured lifecycle results to MCP handlers

The lifecycle service should not own:

- Markdown drafting logic
- prompt strategy
- low-level file mutation details

Those belong respectively to the LLM layer and the lower-level artifact/storage services.

## Relation To MCP Handlers

MCP handlers should be thin adapters.

Their job should be:

- validate tool-call input shape
- call the appropriate lifecycle service method
- translate the service result into the published MCP response shape

They should not:

- manually coordinate multiple persistence operations
- encode lifecycle recovery rules
- interpret partial storage outcomes independently

If MCP handlers do those things, the real lifecycle contract will be split across layers.

## Relation To Artifact Services

Artifact services should remain narrower and more mechanical.

They should handle concerns like:

- reading current artifact pairs
- writing new checkpoints
- updating current materialized views
- resolving checkpoint references

They should not decide:

- whether startup should rebuild projection state
- whether a handoff succeeds when projection refresh lags
- whether archive failure should revert to active

Those are lifecycle-policy decisions and belong in the lifecycle service.

## Method Shape

The lifecycle service methods should align closely with the MCP operation set:

- `session_read_startup_view(...)`
- `session_read_thread(...)`
- `session_write_handoff(...)`
- `session_archive_thread(...)`

This reduces translation overhead and makes logs, tests, and operator behavior easier to reason about.

The service may internally call smaller primitives, but the public runtime boundary should stay lifecycle-shaped.

## Result Shape

The lifecycle service should return structured result objects, not free-form status prose.

Those result objects should carry:

- lifecycle result status
- warning codes
- affected artifact references and checkpoint ids
- operation-specific metadata

This lets the MCP layer remain a transport adapter rather than a second policy layer.

## Recovery Ownership

Deterministic recovery should also live in the lifecycle service.

Examples:

- startup index mismatch triggers rebuild
- malformed startup projection triggers warning plus rebuild
- archive transition failure prefers revert-to-active unless full archive completion can still finish as one bounded recovery action

The lower-level artifact services may supply the mechanics, but the lifecycle service should decide which recovery path is allowed.

To keep that consistent, the lifecycle service should use a shared bounded operation/recovery abstraction rather than duplicating recovery logic across methods.

## Testing Consequence

This design also improves testability.

Clauderfall should be able to test lifecycle invariants at the service layer without needing:

- an active LLM session
- MCP transport wiring
- prompt-level simulation of multi-step persistence behavior

That is a strong signal that the invariant boundary is in the right place.

## Constraints

This service shape should preserve the cluster's established constraints:

- deterministic lifecycle transitions
- minimal model-facing operation set
- strict active-versus-history boundary
- token-efficient startup
- no reliance on prompt-enforced synchronization

## Tradeoffs

## Benefits

- lifecycle policy stays centralized
- MCP handlers remain thin and predictable
- lower-level persistence code stays reusable and mechanical
- recovery and warning behavior become easier to test

## Costs

- Clauderfall adds another explicit service boundary
- some logic that could be inlined into handlers is intentionally centralized instead
- the service contract needs careful versioning as lifecycle behavior evolves

## Readiness

Readiness: high

Rationale:

The backend structural direction is concrete:

- a dedicated lifecycle service should own the policy
- that service should use a shared bounded operation/recovery mechanism for multi-step lifecycle transitions
- MCP handlers should stay thin
- artifact services should stay mechanical

The remaining work is implementation detail, not unresolved service structure.
