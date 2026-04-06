---
title: Session Lifecycle Backend Service
doc_type: design
status: ready
updated: 2026-04-05
summary: Defines the backend service shape that should own recent-session lifecycle operations and enforce the single-current continuity model.
---

# Session Lifecycle Backend Service

## Purpose

This document defines the backend service shape that should implement recent-session lifecycle behavior in Clauderfall.

The goal is to keep lifecycle invariants centralized in one deterministic runtime boundary rather than scattering them across MCP handlers or ad hoc persistence code.

## Design Position

Clauderfall should use a dedicated session-lifecycle backend service.

That service should own the high-level lifecycle operations already defined by the runtime and MCP interface docs:

- startup-view read and validation
- current-state read
- current-state handoff write
- recent-session index rebuild
- current-to-history archive transition

The MCP layer should delegate to this service rather than reimplement lifecycle behavior itself.

## Why A Dedicated Service

The session-lifecycle cluster now includes several invariants that need to stay aligned:

- the current carry-forward record is authoritative for continuation
- the repo-level recent-session index is a deterministic projection
- startup may rebuild stale or malformed projection state
- completion transitions must not leave durable middle states
- write operations and archive operations have different failure semantics

If these rules live partly in MCP handlers, partly in artifact persistence helpers, and partly in prompt conventions, they will drift.

The backend needs one place that owns the lifecycle contract.

## Recommended Shape

The preferred shape is:

- one `SessionLifecycleService` or equivalent coordinator
- one shared bounded operation and recovery mechanism inside that service for multi-step lifecycle transitions
- a small set of lifecycle-shaped methods matching the MCP surface
- internal helper collaborators for artifact persistence and projection work

## Internal Responsibilities

The lifecycle service should own:

- validating startup index freshness against current-state metadata
- invoking deterministic recent-session index rebuild when needed
- persisting current-state handoff updates through the current-first path
- executing archive transitions with correct completion semantics
- deciding whether a partial failure produces `warning` or `failure`
- returning structured lifecycle results to MCP handlers

## Method Shape

The lifecycle service methods should align closely with the MCP operation set:

- `session_read_startup_view(...)`
- `session_read_current(...)`
- `session_write_handoff(...)`
- `session_archive_current(...)`

## Recovery Ownership

Deterministic recovery should also live in the lifecycle service.

Examples:

- startup index mismatch triggers rebuild
- malformed startup projection triggers warning plus rebuild
- archive transition failure prefers restore-to-current unless full archive completion can still finish as one bounded recovery action

## Constraints

This service shape should preserve the cluster's established constraints:

- deterministic lifecycle transitions
- minimal model-facing operation set
- strict current-versus-history boundary
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
- projection rebuild and archive recovery remain real implementation work

## Readiness

Readiness: high

Rationale:

The service boundary is concrete and directly aligned with the simplified lifecycle surface.

The remaining work is implementation, not architecture discovery.
