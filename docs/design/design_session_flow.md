---
title: Clauderfall Design Session Flow
doc_type: design
status: active
updated: 2026-03-22
summary: Defines the end-to-end interaction flow from the Design Start Context into the first concrete Design unit and its review cycle.
---

# Clauderfall Design Session Flow

## Purpose

This document defines the default end-to-end interaction flow for an active Design session.

The goal is to test the existing Design decisions as one coherent operator experience:

- Design Start Context intake
- first-unit selection
- design-unit drafting
- decomposition when needed
- review
- build-readiness recommendation

## Design Position

The Design session should feel like guided engineering design work, not:

- a stage transition wizard
- a hidden artifact generator
- a task breakdown tool

The engine's job is to keep the operator oriented around the current design boundary, the main unresolved design pressure, and the next best move.

## Default Session Flow

The default flow is:

1. confirm Design Start Context
1. confirm Design Start Context
2. propose the first design unit
3. draft the first design unit in-session
4. decompose if the unit proves too broad
5. move the unit into review when it stabilizes
6. recommend build-readiness judgment
7. sequence to the next unit

The sections below define that flow in more detail.

## 1. Design Start Context Intake

When Design starts, the engine should first restate the discovery context that matters for design.

This should be brief and selective.

The normal source for this intake should be the condensed Design Start Context artifact, not a full reread of the Discovery brief.

The engine should surface:

- the relevant problem areas or themes
- the constraints that materially shape the solution
- important assumptions that are still unresolved
- risks or open questions that are likely to drive early design choices

It should not restate the entire Discovery brief.

## 2. First-Unit Recommendation

After grounding on the Design Start Context, the engine should recommend the first design unit.

The recommendation should include:

- the proposed unit title or boundary
- why this is the right place to start
- one or two plausible alternatives when relevant

The reason should usually point to one of:

- architectural leverage
- dependency criticality
- unresolved risk concentration
- near-term build value

If the Design Start Context is too weak to support a first unit cleanly, the engine should say so explicitly and either:

- ask a narrowing design question
- recommend a brief return to Discovery

That choice should follow the Design-to-Discovery reentry rule: stay in Design for ordinary solution clarification, and return to Discovery when the problem framing itself is unstable.

## 3. Unit Initialization

Once a first unit is chosen, the engine should initialize the unit in `draft`.

That initialization should produce two things immediately:

- a visible unit boundary
- an initial working document shape

The first draft does not need to be complete, but it should already make the unit legible as a coherent design boundary rather than a blank scaffold.

The initial structured side should usually be populated with:

- `design_unit_id`
- `title`
- `status: draft`
- `scope_summary`
- an initial `readiness` judgment
- a brief `readiness_rationale`
- any obvious `assumptions` or `open_questions`

The initial readiness may be `low` or `medium`. It exists to orient the session, not to gate progress.

## 4. Drafting Loop

While the unit is in `draft`, the engine should run a focused drafting loop.

That loop should repeatedly do three things:

- ask the next question that most reduces design uncertainty
- update the visible unit artifact
- restate the current unresolved design pressure

The loop should remain centered on the current unit boundary.

If the conversation drifts into another unit, the engine should either:

- explicitly defer that topic
- create a related unit candidate if the drift reveals a real decomposition boundary

## 5. Decomposition Decision

During drafting, the engine should actively test whether the current unit is still the right unit.

If the unit proves too broad or internally mixed, the engine should say that the boundary is unstable and recommend decomposition.

That recommendation should include:

- the reason the current unit is no longer coherent
- the proposed child or peer units
- which resulting unit should be worked next

Decomposition should be framed as a design clarification move, not as project planning.

## 6. Review Readiness Check

When the unit becomes coherent and concrete enough, the engine should suggest moving it to `in_review`.

The trigger is not document length. The trigger is that the engine can now state, with reasonable confidence:

- what the unit owns
- how it works
- what it depends on
- what the main remaining uncertainty is
- what readiness judgment it currently deserves

If the engine cannot do that honestly, the unit is not ready for review.

## 7. Review Moment

At review time, the engine should present a short review summary covering:

- scope
- proposed design
- dependencies
- strong-signal risks or edge cases
- open questions or assumptions
- readiness rating and rationale

The operator should then be able to respond in one of four ways:

- accept the artifact as the current design
- request revision to the same unit
- redirect to a blocking dependency or alternative unit
- defer build-readiness approval

This keeps review explicit without making it ceremonially heavy.

## 8. Build-Readiness Recommendation

If the unit reaches `high` readiness, the engine should explicitly recommend whether the operator should treat it as buildable.

That recommendation should be short and evidence-based.

It should name:

- the main reason the unit appears buildable
- any remaining caveat that does not invalidate that judgment

If the unit remains `medium` or `low`, the engine should instead name what still blocks build-readiness.

The recommendation is not the approval. The operator remains the decision-maker.

## 9. Post-Review Sequencing

After review, the engine should name the next likely unit.

That recommendation should connect back to the current unit's outcome:

- a dependency that still blocks the current design
- a child unit revealed by decomposition
- a peer unit now made clearer by the reviewed design

The engine does not need to produce a full plan. It only needs to keep the next step legible.

## Example Interaction Skeleton

The intended interaction shape is roughly:

1. Design Start Context summary
2. first-unit recommendation
3. operator confirms or redirects
4. engine opens the unit in `draft`
5. drafting questions and artifact updates
6. decomposition if needed
7. engine proposes `in_review`
8. review summary with readiness judgment
9. operator accepts, revises, or defers build approval
10. engine recommends the next unit

This is a workflow skeleton, not a rigid script.

## What The Session Should Keep Visible

At all times during Design, the operator should be able to tell:

- what unit is active
- why that unit is active now
- what the design currently says
- what unresolved pressure remains
- whether the unit is approaching review or still being worked

If those answers are not obvious, the session has become too opaque.

## Failure Modes To Avoid

The session flow should avoid:

- starting Design with a unit recommendation that is not grounded in the Design Start Context
- letting drafting continue without clarifying the current unit boundary
- treating decomposition as a sign of failure rather than normal design work
- jumping from active drafting straight to implicit build approval
- ending review without making the next likely unit explicit

## Current Design Wall

The main remaining pressure point is whether Design Start Context metadata should eventually carry richer history than a simple regenerated-after-reentry marker.

The current direction is clear that Discovery repair should update the brief, regenerate the Design Start Context, and mark that regeneration in its metadata rather than creating a separate repair artifact.
