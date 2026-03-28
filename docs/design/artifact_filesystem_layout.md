---
title: Clauderfall Artifact Filesystem Layout
doc_type: design
status: stable
updated: 2026-03-22
summary: Defines the on-disk layout for current artifact pairs and immutable checkpoint history.
---

# Clauderfall Artifact Filesystem Layout

## Purpose

This document defines the default filesystem layout for persisted Clauderfall artifacts.

The goal is to make the latest artifact easy to load while preserving explicit access to immutable checkpoint history.

## Design Position

Each logical artifact should have:

- one stable current location
- one history location containing immutable checkpoints

This keeps the common case simple:

- load the current artifact by default
- load a specific checkpoint only when history matters

## Directory Model

The default layout should be organized by stage, then artifact identity.

At a logical level, each artifact directory should look like:

```text
<stage>/<artifact_id>/
  current/
    artifact.md
    artifact.meta.yaml
  checkpoints/
    <checkpoint_id>/
      artifact.md
      artifact.meta.yaml
```

The exact root path is implementation-specific.

The important rule is the stable separation between:

- the latest materialized artifact pair
- immutable historical checkpoint pairs

## Current Location

The `current/` directory should hold the latest successfully flushed artifact pair.

This is the default read target for normal product behavior.

If an operator or engine asks for the artifact without specifying a checkpoint, the system should resolve to this location.

## Checkpoint History

The `checkpoints/` directory should contain one subdirectory per `checkpoint_id`.

Each checkpoint directory should contain the exact artifact pair for that immutable checkpoint:

- `artifact.md`
- `artifact.meta.yaml`

Checkpoint contents should never be rewritten after a successful flush.

The checkpoint directory name is an address key, not a human-readable summary of the checkpoint.

## Flush Update Rule

When a flush succeeds, the system should:

1. write the new immutable checkpoint pair
2. update `current/` to reflect that same checkpoint state

The product should treat these as one logical persistence operation.

`current/` is therefore a materialized convenience view of the latest checkpoint, not a separate checkpointless artifact.

## Identity Rule

The artifact directory should be keyed by stable `artifact_id`, not by title.

Human-readable titles may change over time.

Artifact identity should not.

This avoids path churn when a document is renamed during normal design work.

## Filename Rule

Within `current/` and within each checkpoint directory, filenames should be stable:

- `artifact.md`
- `artifact.meta.yaml`

The meaningful identifiers should live in directory names and metadata, not in changing filenames.

This keeps filesystem handling simpler and reduces rename noise across revisions.

## Relationship To Artifact Names

Operator-facing names and titles should remain metadata and document content concerns.

They may influence UI labels or export names later, but they should not be the canonical filesystem key for persisted runtime artifacts.

## Retrieval Expectations

This layout should support the required retrieval modes cleanly:

- latest artifact: read `current/`
- specific checkpoint: read `checkpoints/<checkpoint_id>/`

No directory scanning heuristics should be required to answer those basic requests.

## Rejected Alternatives

## History-Only Layout Without A Current Convenience Path

Rejected because the common case would require history resolution logic for every ordinary artifact load.

## Current-Only Layout With No Addressable Checkpoint Directories

Rejected because it makes revision history implicit, brittle, or implementation-hidden.

## Title-Based Artifact Paths

Rejected because titles are user-facing and likely to evolve during design iteration.

## Open Questions

This decision does not yet settle:

- whether `current/` should be implemented as copied files, generated files, or another equivalent projection
- what root directory naming should be used for each stage
- whether later export workflows need more human-friendly duplicate filenames outside the canonical runtime layout

Those can be decided later without changing the current-versus-checkpoint layout rule.
