---
title: Clauderfall Design Unit Readiness
doc_type: design
status: stable
updated: 2026-03-22
summary: Defines the meaning, use, and rating criteria for design-unit readiness in Clauderfall.
---

# Clauderfall Design Unit Readiness

## Purpose

This document defines how design-unit readiness should be interpreted and assigned.

The goal is to keep readiness brief, dependable, and directly useful for build decisions.

## Design Position

Readiness is a build-relevance signal, not a document-completeness score.

A design unit is ready when the design appears concrete enough that implementation should not need to invent major decisions inside that unit's boundary.

Readiness should therefore answer one question:

Is this unit solved clearly enough at the design level that building from it is a reasonable move?

It should not answer unrelated questions such as:

- whether the prose is polished
- whether every edge case imaginable has been enumerated
- whether the whole system is finished
- whether implementation work will be easy

## Rating Scale

The rating scale remains:

- `low`
- `medium`
- `high`

This is intentionally small. The product does not need a finer-grained score at this stage.

## Meaning Of Each Rating

### `low`

`low` readiness means the unit is not yet safe to treat as buildable.

Major design uncertainty remains in one or more of these areas:

- core solution shape
- design boundary or decomposition
- important interfaces or responsibilities
- critical constraints or tradeoffs
- strong-signal edge cases that materially affect correctness, safety, or viability

Implementation would likely be forced to guess at major decisions or re-open design.

### `medium`

`medium` readiness means the design direction is plausible and materially useful, but not yet dependable enough to treat as build-ready by default.

The main solution shape is visible, but important uncertainty remains around items that could still change implementation in meaningful ways.

Typical reasons for `medium` include:

- one or two unresolved decisions with real architectural weight
- interface details that are directionally clear but not yet stable
- known strong-signal edge cases that have been identified but not fully designed through
- dependencies on other units whose own readiness is still weak

`medium` is a design-progress signal, not a quiet approval.

### `high`

`high` readiness means the unit is ready to treat as buildable.

The design appears concrete enough that implementation should not need to invent major decisions within the unit's boundary.

This does not require exhaustive certainty. It requires confidence that:

- the unit's scope is clear
- the main solution shape is concrete
- important interfaces or interaction points are resolved enough for building
- relevant constraints and tradeoffs have been addressed
- strong-signal edge cases have been handled or intentionally bounded

Minor open questions may still exist, but they should not undermine buildability.

## Rating Criteria

Readiness should be judged against five criteria.

### 1. Boundary Clarity

The unit's design boundary should be clear enough that the reader knows what problem this unit owns and what it does not.

If the boundary is still fuzzy, the unit should not rate `high`.

### 2. Solution Concreteness

The main design should be concrete enough to guide implementation behavior.

If a competent engineer would still need to invent core responsibilities, structure, or interaction patterns, readiness is not `high`.

### 3. Interface Dependability

Where interfaces or interaction points matter, they should be clear enough to prevent major guesswork.

Not every unit needs a heavy interface section. But if the unit's success depends on interactions with other parts of the system, those interactions must be concretized enough for the rating claimed.

### 4. Constraint And Edge-Case Coverage

The design should account for the constraints and strong-signal edge cases that materially affect viability.

A unit should not receive `high` if known high-impact cases remain untreated.

### 5. Dependency Posture

The unit's reliance on other units should be explicit enough that the rating is honest.

A unit may still rate `high` while depending on other units only when those dependencies are already stable enough that they do not create major downstream guesswork for this unit.

## Readiness Rationale

Every readiness rating should include a short rationale.

The rationale should:

- name the main reason for the rating
- focus on build relevance
- stay brief

It should not become a long review narrative or duplicate the whole unresolved-issues section.

Examples of the intended style:

- `high`: main flow, failure handling, and upstream contract are concrete enough to implement without guessing
- `medium`: storage model is clear, but retry behavior and concurrency boundaries still need design decisions
- `low`: unit boundary is still unstable and likely needs decomposition before concrete design is possible

## Relationship To Artifact Status

Readiness and artifact status are different signals.

`status` answers where the artifact is in the review workflow.

`readiness` answers whether the design is strong enough to build from.

This separation matters because:

- a `draft` may already have `high` readiness if the design is strong but not yet operator-approved
- an `accepted` artifact may still have only `medium` readiness if it is the current best design but not yet buildable

The operator's explicit build-readiness approval remains separate from both fields.

## Parent And Child Units

Parent readiness should not be treated as independent from child readiness.

If a parent unit depends on unresolved child units for its correctness or viability, the parent should not rate `high` merely because the parent-level narrative sounds coherent.

The engine should use this rule:

- a parent may summarize and coordinate child work
- a parent's readiness must reflect the least-resolved child dependencies that materially affect whether the parent can really be built from

This should remain a judgment rule, not a hard numeric rollup.

## Sequencing Implication

Readiness should influence what Design does next.

Typical implications are:

- `low`: keep working this unit or decompose it before treating it as a build candidate
- `medium`: finish the unresolved design pressure or strengthen dependencies before build approval
- `high`: this unit is a reasonable candidate for explicit build-readiness approval

## Failure Modes To Avoid

The engine should avoid these rating mistakes:

- giving `high` because the prose sounds confident while the design remains vague
- giving `medium` as a default placeholder instead of making a judgment
- giving `low` because the whole system is incomplete even when this unit itself is buildable
- treating checklist fullness as equivalent to readiness

## Open Questions

The main remaining question is whether some future product version needs an explicit distinction between:

- design readiness
- operator-approved build readiness

For the current design, that distinction is handled operationally rather than by adding another required field.
