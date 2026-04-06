---
title: Session Handoff Write/Update Flow
doc_type: design
status: ready
updated: 2026-04-05
summary: Defines the handoff write path for the single current carry-forward record and the derived repo-level recent-session index projection.
---

# Session Handoff Write/Update Flow

## Purpose

This document defines how Clauderfall should persist handoff updates for recent session state.

The goal is to keep handoff cheap and reliable by making the current carry-forward state record the only LLM-authored state update, while still preserving a startup-oriented repo-level recent-session index.

## Design Position

The handoff path should be current-state first.

On handoff, Clauderfall should:

1. write the current carry-forward state record and its structured metadata
2. treat that record metadata as the only authoritative current-state source
3. update the repo-level recent-session index as a derived projection from structured current metadata

The repo-level index should not be a co-authored peer document that the handoff step asks the model to keep in sync manually.

That would turn a cheap handoff into a second authoring pass and reintroduce drift risk at exactly the point where the system needs strictness.

## Why Current-State First

The main constraint is operational, not philosophical.

Asking the LLM to update both:

- the current carry-forward state record
- the repo-level recent-session index

would require an additional synchronization pass during handoff and again during startup-oriented maintenance.

That is too expensive for the intended lightweight lifecycle behavior.

The system should therefore optimize for:

- one authoritative current-state write per handoff
- cheap projection for startup orientation
- explicit recovery when the projection lags or fails

## Handoff Write Path

For a handoff write, the default path should be:

1. persist the current carry-forward state record
2. persist the structured metadata for that record
3. mark that write as the new authoritative current state
4. derive or refresh the repo-level recent-session index from explicit structured metadata

The required structured metadata for this path comes from the recent-session artifact contract:

- `title`
- `work_items`
- `updated_at`

The handoff write is successful once the authoritative Markdown artifact and metadata sidecar are durable.

Repo-index refresh is required system behavior, but it is logically downstream of the authoritative current-state write rather than part of the authored handoff payload.

## Authority Boundary

Authority should remain strict:

- the current record owns carry-forward state
- the current metadata owns explicit structured fields for projection
- the repo-level recent-session index owns startup-oriented aggregation only

The repo-level index must not become a second editable source of truth for current continuity metadata.

If a field appears in both places, the current sidecar is authoritative and the repo-level index is replaceable.

## Failure Model

Clauderfall should not require atomic dual-document authoring to consider handoff valid.

Instead, the failure model should be:

- if current-state persistence fails, handoff fails
- if current-state persistence succeeds and repo-index refresh fails, handoff still succeeds for current state
- if repo-index refresh lags or fails, the system should treat the index as stale and recoverable

This keeps the expensive part of the write path small and preserves the most important guarantee:

- the next-work state was captured correctly

## Overwrite Rule

Because the system allows only one current carry-forward record, every successful handoff write replaces the prior current record.

That replacement should be explicit at the workflow level.

If the operator intends to preserve the previous current record as completed work, Clauderfall should archive it before or as part of the workflow that moves to the next current state.

Handoff should not silently create parallel active records.

## Recovery And Refresh

Because the repo-level index is derived, it should be recoverable without re-authoring current state.

Recovery should be projection-based:

- read authoritative current metadata from the current layer
- rebuild the relevant repo-index entry
- rewrite the repo-level recent-session index

Rebuild must be deterministic.

Clauderfall should regenerate the repo-level recent-session index directly from explicit structured metadata, not by asking the model to re-summarize the readable note.

This recovery path should be available both:

- after a failed index refresh during handoff
- during session startup if the system detects stale or missing repo-level projection data

The recovery mechanism should not require rereading broader narrative when structured metadata is sufficient.

## Freshness Detection

Freshness detection should be mismatch based rather than unconditional.

The expected current-state count is zero or one.

Because of that, startup does not need a more elaborate projection-maintenance system.

The repo-level recent-session index should be treated as stale when its projected current state does not match the authoritative current sidecar on the structured fields used for projection.

At minimum, startup should compare:

- whether a current record exists
- current `updated_at`
- presence of the required startup projection fields

If those checks match, startup may trust the persisted repo-level index for orientation.

If they do not match, Clauderfall should rebuild the repo-level index from current metadata before continuing with normal startup presentation.

If the persisted repo-level index is malformed or only partially projected, startup should surface a warning before rebuilding it deterministically from authoritative metadata.

## Startup Consequence

Startup should prefer the repo-level recent-session index for cheap orientation.

But the startup path must tolerate the possibility that the repo index is briefly stale relative to the current layer.

That means startup should treat the repo-level index as:

- the default orientation entry point
- a cached persisted projection
- invalidatable when freshness checks fail

The current layer remains the stronger source when startup needs to resolve ambiguity.

When startup rebuilds because of mismatch or malformed projection state, the rebuild should be mechanical and inspectable:

- derive startup fields from current metadata only
- avoid prose rereads unless structured metadata is missing or invalid
- record that the persisted startup view was refreshed from authoritative metadata

## Constraints

This design preserves the session-lifecycle constraints:

- handoff remains cheap enough to run routinely
- authoritative recent state is captured in one place
- startup can begin from a compact repo-level view
- projection drift is recoverable without asking the model to rewrite multiple documents
- token-heavy rereads are avoided when structured metadata is available

## Tradeoffs

## Benefits

- handoff remains a single authored current-state update rather than a dual-write authoring task
- authority stays clear and local to the current carry-forward record
- repo-level startup state can be repaired mechanically
- the system avoids synchronization-by-prompting as a core correctness mechanism

## Costs

- the repo-level index may briefly lag behind authoritative current state
- the system needs explicit stale-index detection and projection refresh behavior
- overwrite semantics need to stay explicit because there is no second active slot

## Readiness

Readiness: high

Rationale:

The core write/update contract is concrete:

- handoff writes current state first
- the repo index is a derived projection
- index lag is acceptable if it is detectable and recoverable
- startup refresh is triggered by structured metadata mismatch rather than unconditional rebuild
- malformed or partial projection state triggers an operator-visible warning plus deterministic rebuild from metadata

The remaining work is downstream implementation detail rather than unresolved design structure.
