---
title: Session Handoff Write/Update Flow
doc_type: design
status: ready
updated: 2026-03-27
summary: Defines the handoff write path for active thread artifacts and the derived repo-level recent-session index projection.
---

# Session Handoff Write/Update Flow

## Purpose

This document defines how Clauderfall should persist handoff updates for recent session state.

The goal is to keep handoff cheap and reliable by making the active thread artifact the only LLM-authored state update, while still preserving a startup-oriented repo-level recent-session index.

## Design Position

The handoff path should be thread first.

On handoff, Clauderfall should:

1. write the active thread artifact and its structured metadata
2. treat that artifact metadata as the only authoritative thread-state source
3. update the repo-level recent-session index as a derived projection from structured thread metadata

The repo-level index should not be a co-authored peer document that the handoff step asks the model to keep in sync manually.

That would turn a cheap handoff into a second authoring pass and reintroduce drift risk at exactly the point where the system needs strictness.

## Why Thread First

The main constraint is operational, not philosophical.

Asking the LLM to update both:

- the active thread artifact
- the repo-level recent-session index

would require an additional synchronization pass during handoff and again during startup-oriented maintenance.

That is too expensive for the intended lightweight lifecycle behavior.

The system should therefore optimize for:

- one authoritative thread write per handoff
- cheap projection for startup orientation
- explicit recovery when the projection lags or fails

## Handoff Write Path

For an active thread handoff, the default write path should be:

1. persist the readable active thread artifact
2. persist the structured sidecar for that thread artifact
3. mark that write as the new authoritative thread state
4. derive or refresh the repo-level recent-session index entry for that thread from explicit structured metadata

The required structured metadata for this path comes from the recent-session artifact contract:

- `thread_id`
- `title`
- `current_intent_summary`
- `next_suggested_action`
- `updated_at`

The handoff write is successful once the authoritative thread artifact and sidecar are durable.

Repo-index refresh is required system behavior, but it is logically downstream of the authoritative thread write rather than part of the authored handoff payload.

## Authority Boundary

Authority should remain strict:

- the active thread artifact owns thread-specific carry-forward state
- the thread sidecar owns explicit structured metadata for projection
- the repo-level recent-session index owns startup-oriented aggregation only

The repo-level index must not become a second editable source of truth for thread metadata.

If a field appears in both places, the thread sidecar is authoritative and the repo-level index is replaceable.

## Failure Model

Clauderfall should not require atomic dual-document authoring to consider handoff valid.

Instead, the failure model should be:

- if thread artifact persistence fails, handoff fails
- if thread artifact persistence succeeds and repo-index refresh fails, handoff still succeeds for the thread
- if repo-index refresh lags or fails, the system should treat the index as stale and recoverable

This keeps the expensive part of the write path small and preserves the most important guarantee:

- the thread's carry-forward state was captured correctly

## Recovery And Refresh

Because the repo-level index is derived, it should be recoverable without re-authoring thread state.

Recovery should be projection-based:

- read authoritative thread sidecars from the active layer
- rebuild the relevant repo-index entries
- rewrite the repo-level recent-session index

Rebuild must be deterministic.

Clauderfall should regenerate the repo-level recent-session index directly from explicit structured metadata, not by asking the model to re-summarize active threads from prose.

This recovery path should be available both:

- after a failed index refresh during handoff
- during session startup if the system detects stale or missing repo-level projection data

The recovery mechanism should not require rereading full prose artifacts when structured metadata is sufficient.

## Freshness Detection

Freshness detection should be mismatch based rather than unconditional.

The expected active-thread count is small, usually one or two active threads rather than a large fleet of parallel work.

Because of that, startup does not need a more elaborate projection-maintenance system.

The repo-level recent-session index should be treated as stale when its active-thread projection does not match the authoritative active-thread sidecars on the structured fields used for projection.

At minimum, startup should compare:

- active-thread membership by `thread_id`
- per-thread `updated_at`
- presence of the required startup projection fields

If those checks match, startup may trust the persisted repo-level index for orientation.

If they do not match, Clauderfall should rebuild the repo-level index from active-thread metadata before continuing with normal startup presentation.

If the persisted repo-level index is malformed or only partially projected, startup should surface a warning before rebuilding it deterministically from authoritative metadata.

## Startup Consequence

Startup should prefer the repo-level recent-session index for cheap orientation.

But the startup path must tolerate the possibility that the repo index is briefly stale relative to the active thread layer.

That means startup should treat the repo-level index as:

- the default orientation entry point
- a cached persisted projection
- invalidatable when freshness checks fail

The active thread layer remains the stronger source when startup needs to resolve ambiguity.

When startup rebuilds because of mismatch or malformed projection state, the rebuild should be mechanical and inspectable:

- derive startup fields from thread sidecars only
- avoid prose rereads unless structured metadata is missing or invalid
- record that the persisted startup view was refreshed from authoritative metadata

## Constraints

This design preserves the session-lifecycle constraints:

- handoff remains cheap enough to run routinely
- authoritative recent state is captured in one place per active thread
- startup can begin from a compact repo-level view
- projection drift is recoverable without asking the model to rewrite multiple documents
- token-heavy rereads of thread prose are avoided when structured metadata is available

## Tradeoffs

## Benefits

- handoff remains a single authored thread update rather than a dual-write authoring task
- authority stays clear and local to the active thread artifact
- repo-level startup state can be repaired mechanically
- the system avoids synchronization-by-prompting as a core correctness mechanism

## Costs

- the repo-level index may briefly lag behind authoritative thread state
- the system needs explicit stale-index detection and projection refresh behavior
- startup semantics depend on a clear freshness rule rather than assuming every persisted view is current

## Readiness

Readiness: high

Rationale:

The core write/update contract is concrete:

- handoff writes thread state first
- the repo index is a derived projection
- index lag is acceptable if it is detectable and recoverable
- startup refresh is triggered by structured metadata mismatch rather than unconditional rebuild
- malformed or partial projection state triggers an operator-visible warning plus deterministic rebuild from metadata

The remaining work is downstream implementation detail rather than unresolved design structure.
