---
title: Clauderfall Artifact Checkpoint Metadata
doc_type: design
status: stable
updated: 2026-03-22
summary: Defines the required metadata recorded for each persisted artifact checkpoint.
---

# Clauderfall Artifact Checkpoint Metadata

## Purpose

This document defines the minimum metadata every persisted artifact checkpoint should carry.

The goal is to make checkpoint history inspectable and dependable without forcing consumers to infer meaning from filesystem layout alone.

## Design Position

Each persisted checkpoint should carry a small standard metadata envelope.

That envelope should answer:

- what artifact this checkpoint belongs to
- which checkpoint this is
- when it was created
- why it was flushed
- whether it is the current checkpoint

The envelope should stay small and operational.

It should not become a second audit log.

## Required Checkpoint Metadata

Every checkpoint should record at least:

- `artifact_id`
- `checkpoint_id`
- `created_at`
- `flush_reason`
- `is_current`

These fields should live in the checkpoint sidecar metadata.

They may also be reflected elsewhere for indexing, but the sidecar is the canonical structured source.

## `artifact_id`

`artifact_id` identifies the logical artifact across its full revision history.

It must remain stable across ordinary edits, review transitions, acceptance, reopening, and Discovery repair that preserves artifact identity.

## `checkpoint_id`

`checkpoint_id` identifies one immutable persisted snapshot.

It should be an opaque identifier rather than a semantic timestamp or human-readable sequence label.

The product needs uniqueness and stable addressability, not human interpretation from the identifier itself.

Ordering should be determined by checkpoint metadata and persistence logic, not by parsing the identifier string.

## `created_at`

`created_at` records when the checkpoint was successfully persisted.

It should use a full timestamp rather than a date-only field.

This is the main human-readable ordering signal for checkpoint history inspection.

## `flush_reason`

`flush_reason` should record the product-level reason this checkpoint was created.

This should use a small controlled set rather than free-form prose.

The current default set should be:

- `checkpoint`
- `review_transition`
- `review_decision`
- `decomposition`
- `reentry_repair`
- `context_safety`

These values correspond to the flush triggers and lifecycle events already established elsewhere in the active docs.

They are operational labels, not long-form explanations.

## `is_current`

`is_current` indicates whether this checkpoint is the artifact's current materialized state.

For a healthy artifact history:

- exactly one checkpoint should be current
- all earlier checkpoints should be non-current

This field exists to make history inspection and indexing straightforward without requiring every consumer to compare timestamps or query external state.

## Why Opaque `checkpoint_id`

Human-readable or timestamp-shaped checkpoint identifiers create false coupling between:

- persistence internals
- ordering semantics
- UI presentation

An opaque id keeps those concerns separate.

Humans should use `created_at` and `flush_reason` to understand history.

Systems should use `checkpoint_id` only for stable reference.

## Relationship To Filesystem Layout

The filesystem layout may still use `checkpoint_id` as the checkpoint directory name.

That does not make the identifier itself a human-facing explanation.

The directory key is only an address.

The meaning of the checkpoint comes from the metadata envelope.

## Deliberately Excluded

The required envelope does not yet include:

- free-form flush notes
- actor identity
- parent checkpoint references
- branch names
- approval records separate from artifact state

Those may be useful later, but they are not required for the current single-operator product boundary.

## Rejected Alternatives

## Timestamp-As-Identifier

Rejected because it overloads one field with both identity and ordering semantics.

## Free-Form Flush Reasons

Rejected because they would drift in wording and reduce queryability.

## No Explicit Flush Reason

Rejected because not all checkpoints mean the same thing, and that distinction materially affects later inspection.

## Open Questions

This decision does not yet settle:

- whether checkpoint metadata should also be duplicated into a per-artifact history index
- whether later multi-actor workflows need actor identity in the checkpoint envelope
- whether some future UI needs optional human-authored revision notes alongside the controlled flush reason

Those can be decided later without changing the minimum checkpoint metadata defined here.
