---
title: Clauderfall Session Handoff 2026-03-22 Persistence Checkpoint
doc_type: handoff
status: active
updated: 2026-03-22
summary: Continuity note after settling the persistence format, checkpoint semantics, filesystem layout, and checkpoint metadata for active artifacts.
---

# Clauderfall Session Handoff 2026-03-22 Persistence Checkpoint

## Completed

- Continued from the active design docs and handoff/reentry checkpoint without reopening archived MVP material as current truth.
- Settled the default physical persistence format for active artifacts.
- Chose a document-first paired-file model:
  - one canonical readable Markdown document
  - one adjacent YAML metadata sidecar
- Settled checkpoint semantics for persisted artifacts.
- Chose immutable checkpoints under a stable `artifact_id` rather than overwrite-in-place persistence.
- Settled the default filesystem layout for persisted artifacts.
- Chose a stable `current/` location plus immutable `checkpoints/<checkpoint_id>/` history.
- Settled the minimum metadata envelope required for each checkpoint.
- Chose opaque `checkpoint_id` values and a controlled `flush_reason` set.

## Current Truth

- The active source of truth is the doc set under `docs/design/`.
- Artifact persistence design is now split into four active decisions:
  - physical format
  - checkpoint semantics
  - checkpoint metadata
  - filesystem layout
- The current persisted artifact model is:
  - one readable Markdown artifact
  - one adjacent YAML sidecar
  - one stable `artifact_id`
  - immutable checkpoints for each flush
  - one `current/` materialization plus explicit checkpoint history
- Artifact titles are operator-facing and may change.
- Filesystem identity should be keyed by stable `artifact_id`, not title.
- Reopening an accepted design unit should create a new checkpoint for the same artifact, not a new artifact identity.
- Discovery repair after Design reentry should create new checkpoints under existing artifact identities.

## Key Docs

- `docs/design/clauderfall_product_brief.md`
- `docs/design/discovery_engine.md`
- `docs/design/design_engine.md`
- `docs/design/artifact_persistence_format.md`
- `docs/design/artifact_checkpoint_semantics.md`
- `docs/design/artifact_checkpoint_metadata.md`
- `docs/design/artifact_filesystem_layout.md`
- `docs/design/design_unit_artifact.md`
- `docs/design/discovery_design_handoff.md`
- `docs/design/design_discovery_reentry.md`

## Remaining Open Questions

- Whether persisted artifact history needs a per-artifact index file or whether checkpoint sidecars alone are sufficient.
- Whether `current/` should be implemented as copied files, generated files, or another equivalent projection.
- What stage root directory naming should be used in the canonical runtime layout.
- Whether checkpoint metadata eventually needs explicit parent-checkpoint linkage.
- Whether later workflows need optional human-authored revision notes in addition to the controlled `flush_reason`.
- Whether explicit build-readiness approval should remain a workflow action or later become persisted structure.

## Next Session

- Start from the active persistence docs, not the archived MVP persistence material.
- Treat the persistence model as designed enough through checkpoint metadata and filesystem layout.
- The next highest-value design problem is whether artifact history also needs a per-artifact history index.
- Keep the product document-first and avoid reintroducing schema-first stage artifacts.
