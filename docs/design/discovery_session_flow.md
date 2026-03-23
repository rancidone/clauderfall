---
title: Clauderfall Discovery Session Flow
doc_type: design
status: active
updated: 2026-03-22
summary: Defines the end-to-end interaction flow for an active Discovery session from rough intent through Design Start Context creation.
---

# Clauderfall Discovery Session Flow

## Purpose

This document defines the default end-to-end interaction flow for an active Discovery session.

The goal is to make the Discovery stage work as one coherent paper system from rough user intent through a Design-ready Discovery brief and derived Design Start Context.

## Design Position

The Discovery session should feel like guided problem-framing work, not:

- a questionnaire wizard
- a hidden state machine
- a design session that has not admitted it is design

The engine's job is to keep the operator oriented around:

- the current framing gap
- the visible Discovery brief
- the strongest unresolved assumptions, constraints, and risks
- whether the conversation is still in Discovery or drifting into Design

## Default Session Flow

The default flow is:

1. initialize the Discovery brief from rough intent
2. identify the highest-risk framing gap
3. run a focused drafting loop
4. organize and strengthen problem areas
5. surface cross-cutting pressure
6. evaluate Discovery readiness
7. decide transition versus continued Discovery
8. create the Design Start Context when Design begins

The sections below define that flow in more detail.

## 1. Session Initialization

Discovery should begin from rough software intent, not from an assumed schema.

At session start, the engine should do two things immediately:

- restate the rough intent in concise engineer-readable terms
- open a visible Discovery brief in `draft`

The first Discovery brief does not need to be strong.

It needs to be legible enough that the operator can inspect and correct it.

The initialization should usually establish:

- a provisional brief title
- an initial overview paragraph or short opening summary
- one or more provisional problem areas when the initial intent already suggests them
- explicit uncertainty where the initial framing is weak

If the initial intent is too vague to justify multiple problem areas, the engine may begin with a single provisional area and decompose it later.

## 2. Highest-Risk Gap Identification

After initialization, the engine should identify the single highest-risk framing gap.

This is the next question that most improves the Discovery brief if answered.

Typical high-risk gaps include:

- the actual problem statement is still ambiguous
- intended outcomes are subjective or fuzzy
- a major constraint is missing
- the user is speaking in solution structure instead of problem framing
- a key assumption has been smuggled in without being named

The engine should prefer one sharp question over a broad prompt for more detail.

Discovery quality depends more on resolving the right blocker than on collecting more text.

## 3. Focused Drafting Loop

Once the highest-risk gap is identified, Discovery should run a tight drafting loop.

That loop should repeatedly do three things:

- ask the next narrow Discovery question
- update the visible brief
- restate the current unresolved framing pressure

The system should treat the brief as the active working artifact during this loop.

The engine should not hide important state in private memory if the operator cannot inspect it.

Each loop iteration should tend to add or clarify one of:

- problem statement
- intended outcomes
- constraints
- assumptions
- risks and edge cases
- open questions
- confidence

## 4. Problem-Area Formation And Refinement

As Discovery progresses, the engine should shape the brief around problem areas or themes.

The goal is not taxonomy for its own sake.

The goal is to separate distinct framing pressures cleanly enough that Design can later reason about them without rereading the whole conversation.

The engine should create or split problem areas when:

- one area is carrying multiple unrelated concerns
- different parts of the problem have meaningfully different confidence
- a newly surfaced constraint or risk clearly belongs to a distinct theme

The engine should merge or simplify areas when:

- two areas are really the same framing concern
- one area has no meaningful independence
- the structure is making the brief harder to read without adding real clarity

## 5. Cross-Cutting Pressure Capture

Discovery should not force everything into local problem areas.

The engine should explicitly surface cross-cutting items when they materially affect multiple areas.

These usually include:

- global constraints
- shared assumptions
- systemic risks
- cross-cutting open questions

This step matters because the later Design Start Context depends on those cross-cutting pressures being explicit rather than buried across multiple sections.

## 6. Design Drift Handling

Discovery should actively test whether the conversation is still problem-framing work.

When the user starts giving concrete solution structure, the engine should not simply accept that as ordinary Discovery content.

Instead it should:

- say that the conversation is moving toward Design
- extract any useful assumptions or constraints from what was said
- update the Discovery brief only with the parts that are genuinely problem-framing signal
- ask a narrower replacement question when Discovery is still incomplete

If the conversation is consistently operating at design level and the Discovery brief is already strong enough, the engine may suggest transition rather than repeatedly dragging the user backward.

## 7. Flush Checkpoint Moments

The Discovery brief does not need to persist every turn.

However, the engine should flush the current brief as a new checkpoint before meaningful progress is at risk.

Important flush moments include:

- before context compaction risk becomes material
- after a major problem area becomes coherent
- after cross-cutting assumptions or constraints materially change
- before a readiness discussion
- before creating the Design Start Context

Each flush should preserve one coherent readable brief plus its structured side.

The checkpoint should reflect the same Discovery state in both files.

## 8. Readiness Evaluation

When the brief appears strong enough to support Design, the engine should evaluate whether Discovery is actually ready.

This judgment should be based on:

- whether the problem is framed clearly enough that Design will not need to invent it
- whether relevant problem areas have usable confidence
- whether important assumptions are explicit
- whether major constraints and risks are visible
- whether blocking framing gaps remain

This evaluation should update the Discovery brief artifact itself.

It should not silently trigger a stage transition.

## 9. Transition Decision

Once readiness is visible, Discovery should support one of three outcomes:

- continue Discovery because the brief is still materially weak
- begin Design through the normal consensus path
- begin Design through an explicit operator override despite meaningful incompleteness

The normal path is consensus-based.

The engine may recommend transition, and the operator may suggest it, but the intended transition is when both agree the brief is strong enough.

The override path is weaker and should stay explicit.

The system should preserve the weak-signal assumptions and low-confidence areas rather than pretending the brief is fully ready.

## 10. Design Start Context Creation

When Design begins, the engine should derive the Design Start Context from the current Discovery brief.

The Design Start Context should be selective and condensed.

The Discovery brief remains canonical.

Creation of the Design Start Context should not replace or rewrite the Discovery brief.

It should produce a separate artifact under the same overall persistence model and should preserve:

- the problem-area index relevant to Design
- cross-cutting constraints and risks
- materially important assumptions and their statuses
- the recommended starting focus for Design

## Example Interaction Skeleton

The intended Discovery interaction shape is roughly:

1. rough user intent
2. engine opens the Discovery brief in `draft`
3. engine asks one targeted framing question
4. engine updates the visible brief
5. loop through framing gaps and brief refinement
6. surface cross-cutting pressure and confidence
7. evaluate readiness explicitly
8. continue Discovery or agree to start Design
9. create the Design Start Context if Design begins

This is a workflow skeleton, not a rigid script.

## Failure Modes To Avoid

The Discovery session should avoid:

- collecting broad background detail before resolving the main framing blocker
- allowing solution structure to silently replace problem framing
- hiding important assumptions in metadata only
- treating readiness as a private engine judgment
- creating the Design Start Context from a brief that is visibly too weak

## Open Questions

The main remaining open questions for this flow are:

- what exact operator-facing interaction should accompany the explicit override path
- whether the brief should visibly mark low-confidence areas inline as well as in the sidecar
- how much design-drift continuity should be shown by default in the active session view

Those questions do not block adopting the flow above as the current Discovery session direction.
