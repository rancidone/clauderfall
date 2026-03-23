---
title: Clauderfall Design Review Workflow
doc_type: design
status: active
updated: 2026-03-22
summary: Defines how a design unit moves through drafting, review, and build-readiness approval during the Design stage.
---

# Clauderfall Design Review Workflow

## Purpose

This document defines the operator-facing workflow for advancing a design unit through Design.

The goal is to keep iteration fluid while preserving the two important signals already established:

- the artifact's workflow status
- the unit's design readiness

## Design Position

Design should advance draft artifacts by default during the interview.

The engine should not ask for approval on every small revision.

However, the workflow must still preserve an explicit review moment before a unit is treated as buildable.

## Core Signals

Each design unit carries at least these workflow-relevant signals:

- `status`
- `readiness`
- `readiness_rationale`

The operator also makes a separate explicit judgment about whether the unit is ready enough to treat as buildable.

## Status Model

The current recommended `status` set is:

- `draft`
- `in_review`
- `accepted`

This is intentionally small.

### `draft`

`draft` means the design is still being actively developed.

The document may already be substantial. The label only means the session is still shaping the design rather than asking for a review decision.

### `in_review`

`in_review` means the unit is stable enough to review as the current proposed design.

This is the point where the engine should be willing to summarize the unit's scope, main design choices, unresolved pressure, and readiness judgment for operator review.

### `accepted`

`accepted` means the operator accepts this artifact as the current working design for the unit.

This does not automatically mean the unit has `high` readiness or is approved for build execution. It means the artifact itself is the accepted design record at this point in time.

## Default Flow

The default flow should be:

1. work the unit in `draft`
2. move to `in_review` when the design has stabilized enough for evaluation
3. ask for explicit operator review of the unit's readiness
4. mark the artifact `accepted` if the operator accepts it as the current design
5. separately note whether the unit is approved to treat as buildable

The key separation is:

- accepting the design artifact
- approving the unit for build use

These often happen together, but they are not the same thing.

## When To Enter Review

The engine should suggest moving a unit to `in_review` when:

- the unit boundary is coherent
- the main design is visible and concrete
- the readiness rating can be argued honestly
- the main remaining uncertainty is explicit rather than hidden

The engine should not push review just because the document is long enough.

## Review Moment

At review time, the engine should make the current judgment explicit.

The minimum review summary should cover:

- unit scope
- proposed design shape
- key dependencies
- key unresolved questions or assumptions
- readiness rating and rationale

This is the point where the operator can:

- accept the unit as-is
- ask for revision
- redirect sequencing to a blocking dependency
- defer build-readiness approval even if the artifact is accepted

## Build-Readiness Approval

Build-readiness approval should remain an explicit operator gate.

The engine may recommend approval when a unit has `high` readiness, but it should not silently convert that recommendation into approval.

This matters because the operator may choose to:

- accept the design artifact while still deferring build work
- request stronger treatment of a particular edge case before approval
- wait for another related unit to stabilize first

## Relationship Between Status And Readiness

The expected combinations are:

- `draft` + `low` or `medium` is normal
- `in_review` + any readiness is possible, though `low` should usually trigger more work
- `accepted` + `medium` is valid when the artifact is accepted but not yet buildable
- `accepted` + `high` is the common case for a unit that is both accepted and approved as a build candidate

The workflow should not assume one field determines the other.

## Revision After Acceptance

Acceptance is not permanent closure.

If later design work reveals a material issue, the engine should be able to reopen the unit by moving it back to `draft` or `in_review` and revising readiness accordingly.

This avoids the false idea that design review is irreversible.

## Session Checkpoints

The engine should explicitly flush the current artifact at meaningful checkpoints, especially when:

- a draft becomes coherent enough for review
- a review decision is made
- context pressure threatens loss of meaningful progress
- decomposition creates new units that change the sequencing picture

The flush should preserve the current unit state without forcing persistence on every turn.

## Failure Modes To Avoid

The workflow should avoid:

- treating `accepted` as equivalent to approved-to-build in every case
- forcing explicit approval on every draft revision
- leaving units in `draft` indefinitely because review feels heavyweight
- assigning `high` readiness without triggering an explicit review moment
- pretending a reopened unit is a workflow failure rather than normal design iteration

## Open Question

The main remaining open question is whether explicit build approval eventually needs its own persisted field or whether it should remain a workflow action outside the required design-unit structure.

For the current design, it should remain a separate operator decision rather than a required artifact field.
