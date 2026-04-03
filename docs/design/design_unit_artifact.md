---
title: Clauderfall Design Unit Artifact
doc_type: design
status: stable
updated: 2026-03-22
summary: Defines the shape of a Clauderfall design unit as a readable design document with a small structured sidecar.
---

# Clauderfall Design Unit Artifact

## Purpose

This document defines the artifact shape for a design unit.

The goal is to keep Design document-first while still carrying enough explicit structure to support:

- design review
- readiness decisions
- design-unit decomposition
- downstream build planning

This is intentionally not a schema-first design. The readable design document remains primary.

## Design Position

A design unit should be represented as two tightly coupled parts:

- a readable design document written for an engineer
- a small structured sidecar containing the fields that are hard to recover reliably from prose later

The design document is the artifact a human should primarily read and review.

The structured sidecar exists to make a few downstream operations dependable:

- identifying the unit and its current boundary
- understanding its dependency and decomposition relationships
- knowing whether it is ready to build from
- carrying forward the most important unresolved decisions and assumptions

If a field does not materially improve one of those operations, it does not belong in the structured side.

## Artifact Model

Each design unit should have:

- one canonical document
- one structured metadata block or sidecar

The product should treat these as one logical artifact, even if the storage format later changes.

The current design does not require the structure to live in a separate file. It may be:

- frontmatter
- an adjacent machine-readable sidecar
- another tightly linked representation

The product requirement is the logical shape, not the file format.

The current default physical persistence format is defined separately in `artifact_persistence_format.md`.

## Canonical Document

The readable design document should carry the design reasoning and concrete solution shape.

It should usually include, when relevant:

- the design unit's scope and problem being solved
- context from Discovery that materially constrains the design
- the proposed solution shape
- key responsibilities or boundaries
- interfaces or interaction points
- important tradeoffs
- risks and edge cases with strong signal
- unresolved questions or decisions

The document should be readable without consulting the structured side except for indexing, sequencing, or status-style questions.

## Structured Side

The structured side should be intentionally small.

These fields appear necessary now.

### Core Identity

- `design_unit_id`
- `title`
- `status`

`design_unit_id` gives the unit a stable handle.

`title` is the operator-facing name for the unit.

`status` is the workflow state of the artifact itself, not the design readiness judgment. It should answer whether the unit is still being drafted or is accepted as the current working design.

### Boundary

- `scope_summary`

This is a short description of the concrete design boundary.

It should stay brief and should not duplicate the full document introduction. Its purpose is quick orientation and later sequencing, especially when many units exist.

### Relationships

- `depends_on`
- `children`
- `parent`

These fields capture meaningful relationships between units when they exist.

All relationship fields should be optional because not every design pass naturally produces a tree.

`depends_on` identifies other units that this unit relies on for its own readiness or correctness.

`children` identifies units that were explicitly decomposed from this unit.

`parent` identifies the containing unit when the decomposition is hierarchical.

The distinction between dependency and parent-child matters. A unit may depend on another unit without being its child.

### Readiness

- `readiness`
- `readiness_rationale`

`readiness` should use the same simple scale already established in product language:

- `low`
- `medium`
- `high`

`readiness_rationale` should be short and should explain the main reason the unit is or is not build-ready.

This keeps build-readiness explicit without turning the structured side into a long review record.

These fields are local to the current design-unit artifact.

When a new design-unit document is created, its `readiness` and `readiness_rationale` should be initialized from that unit's own state rather than inherited from a parent, child, or previously active peer unit.

### Open Design Pressure

- `open_questions`
- `assumptions`

These fields should contain only unresolved items that still materially affect design confidence or buildability.

They should not become dumping grounds for every note mentioned in the document.

Keeping them explicit in structure is useful because they directly affect sequencing, review, and readiness.

## Fields Deliberately Excluded

The following do not belong in the required structured shape right now:

- a universal `inputs` field
- a universal `outputs` field
- a full interface schema
- implementation tasks
- exhaustive acceptance criteria
- a formal dependency graph model
- a long review history

These may be useful in some designs, but forcing them into every unit would push the artifact toward template-filling and task planning.

Inputs and outputs should stay optional content in the design document unless they are important enough to justify later structured support.

## Proposed Minimal Shape

The current minimum viable logical shape is:

```yaml
design_unit_id: string
title: string
status: draft | accepted
scope_summary: string
depends_on: [design_unit_id]
children: [design_unit_id]
parent: design_unit_id | null
readiness: low | medium | high
readiness_rationale: string
open_questions: [string]
assumptions: [string]
```

This is not a final storage schema. It is the minimum field set that currently seems justified by the product and engine briefs.

## Transition Rule

Status and readiness transitions should be artifact-local and deterministic.

At minimum:

- creating or opening a new design-unit artifact initializes `status: draft`
- creating or opening a new design-unit artifact requires a fresh `readiness` and `readiness_rationale`
- moving an existing artifact to `accepted` applies only to that artifact
- decomposition may create related units, but it does not transfer workflow state automatically across artifacts

## Readability Rule

If a reader can no longer understand the unit by reading the document alone, the artifact has become too structure-heavy.

If downstream planning cannot reliably answer what the unit is, what it depends on, whether it is ready, and what unresolved design pressure remains, the artifact has become too prose-heavy.

The intended balance is:

- document-first for understanding
- structure-assisted for coordination and downstream use

## Open Questions

Some details remain intentionally open:

- whether `status` should use exactly `draft | accepted` or a slightly different small set
- whether `open_questions` and `assumptions` should later distinguish operator-confirmed items from interviewer-inferred items
- whether parent readiness should eventually carry an explicit derived signal from child readiness or remain a judgment the engine computes conversationally

These questions do not block adopting the artifact shape above as the current design direction.
