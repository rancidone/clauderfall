---
title: Clauderfall Artifact Checkpoint Semantics
doc_type: design
status: active
updated: 2026-03-22
summary: Defines artifact identity, checkpoint creation, and revision semantics for persisted readable artifacts and metadata sidecars.
---

# Clauderfall Artifact Checkpoint Semantics

## Purpose

This document defines what a persisted artifact flush means in Clauderfall.

The goal is to preserve useful revision history and recovery semantics without forcing the product to persist every conversational turn.

## Design Position

Clauderfall should treat each flush as the creation of a new immutable artifact checkpoint.

An artifact therefore has:

- one stable artifact identity across time
- a sequence of persisted checkpoints for that artifact
- one current checkpoint that represents the latest persisted state

This preserves continuity when drafts evolve, reviews happen, units are reopened, or Discovery framing is repaired.

## Core Model

The core persistence model should distinguish:

- `artifact_id`
- `checkpoint_id`
- current working session state

`artifact_id` identifies the logical artifact across revisions.

`checkpoint_id` identifies one persisted snapshot of that artifact.

Working session state may advance between checkpoints, but it is not itself a durable checkpoint until an explicit flush happens.

## What A Checkpoint Contains

Each checkpoint should capture one complete artifact state at one moment.

For the current product boundary, that means:

- the readable Markdown document
- the structured YAML sidecar

Those two files must correspond to the same checkpoint.

The required checkpoint metadata envelope for that sidecar is defined separately in `artifact_checkpoint_metadata.md`.

Partial mixed-state checkpoints are invalid.

## Immutability Rule

Once a checkpoint is written successfully, it should be treated as immutable.

Later artifact changes should create a new checkpoint rather than rewriting the contents of an older one.

This rule matters because Clauderfall needs to preserve:

- review context
- recovery after context loss
- the fact that accepted artifacts can later be reopened and revised
- continuity across Discovery repair and Design reentry

## Current Checkpoint Rule

At any time, an artifact may have many historical checkpoints but only one current checkpoint.

The current checkpoint is simply the latest successfully flushed checkpoint for that artifact.

Product behavior that asks for the persisted artifact by default should resolve to this current checkpoint unless a specific historical checkpoint is requested.

## Flush Triggers

A flush should happen only at meaningful checkpoints, not on every turn.

The current default triggers remain:

- when a draft becomes coherent enough that losing it would be costly
- when review state changes materially
- when an operator review decision is made
- when decomposition creates or materially restructures units
- when context pressure makes continued session-only state risky

These are product-level triggers, not a guarantee that every sentence edit becomes durable history.

## Status And Readiness Across Checkpoints

Workflow status and readiness are checkpointed artifact state, not separate audit events.

If a design unit moves from `draft` to `in_review`, or from `accepted` back to `draft`, that change should appear in a later checkpoint for the same `artifact_id`.

The model should not create a new artifact identity just because workflow state changed.

## Reopen Semantics

Reopening an accepted design unit should create a new checkpoint sequence entry for the same artifact.

The reopened unit is not a new logical design unit unless its boundary changes so much that the original identity is no longer coherent.

Ordinary revision after acceptance should therefore preserve:

- the same `artifact_id`
- a new `checkpoint_id`

This keeps revision history honest without fragmenting the design record.

## Discovery Repair Semantics

When Discovery is repaired after Design reentry, the repaired Discovery brief and regenerated handoff should each create new checkpoints under their existing artifact identities.

The purpose is to show that the framing evolved, not to imply that entirely new artifact types appeared.

## Retrieval Expectations

The persistence model should support at least these retrieval modes:

- latest checkpoint for an artifact
- specific checkpoint for an artifact

Anything more advanced can remain implementation-specific for now.

The design does not currently require branch-style histories, parallel drafts, or merge semantics.

## Relationship To Physical Files

The paired-file persistence format remains:

- one Markdown document
- one adjacent YAML metadata sidecar

This document adds the rule that those files belong to a specific immutable checkpoint once flushed.

How checkpoint history is laid out on disk may vary, but the implementation must preserve:

- stable artifact identity
- addressable checkpoints
- a dependable notion of the current checkpoint

## Rejected Alternatives

## Overwrite-Only Persistence

Rejected because it loses reviewable revision history and makes reopened design work look indistinguishable from uninterrupted drafting.

## Persist Every Conversational Turn

Rejected because it creates too much churn relative to the product's explicit-checkpoint workflow.

## New Artifact Identity For Every Meaningful Revision

Rejected because normal design iteration would fragment the artifact graph and make continuity harder to reason about.

## Open Questions

This decision does not yet settle:

- whether checkpoint metadata should also carry parent-checkpoint linkage explicitly
- whether some future workflow needs branch-style revision metadata

Those can be decided later without changing the checkpoint model established here.
