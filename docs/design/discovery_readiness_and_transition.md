---
title: Clauderfall Discovery Readiness And Transition
doc_type: design
status: ready
updated: 2026-03-27
summary: Defines how Discovery readiness is judged from the Discovery brief and how the stage transitions into Design through either accepted consensus or explicit override.
---

# Clauderfall Discovery Readiness And Transition

## Purpose

This document defines:

- how Discovery readiness is judged from the Discovery brief
- how the normal consensus transition into Design works
- how the explicit early-start override path differs
- what state changes occur in the Discovery brief and Design Start Context at transition time

The goal is to make the Discovery-to-Design boundary concrete enough that the full system works on paper without hidden stage changes or fuzzy approval semantics.

## Design Position

Discovery readiness is a visible judgment over the current Discovery brief.

It is not:

- a private engine threshold
- an automatic transition
- a claim that every assumption is resolved

The purpose of the readiness judgment is narrower:

- determine whether the Discovery brief is strong enough that Design does not need to invent the problem
- expose the main reasons the brief is or is not ready
- support either the normal consensus transition or the weaker explicit override path

## Readiness Inputs

The readiness judgment should come from the current Discovery brief artifact, not from hidden conversation state.

The main inputs are:

- clarity of the problem statement
- clarity of intended outcomes
- visibility of major constraints
- visibility of important risks and edge cases
- explicitness of important assumptions
- confidence across the problem areas relevant to likely early Design work
- remaining blocking framing gaps

These inputs should already be visible either in the readable brief or in its structured side.

## Readiness Standard

Discovery is ready for Design when all of the following are substantially true:

- the problem is framed clearly enough that Design will not need to invent it
- intended outcomes are clear enough to judge design adequacy
- major constraints are visible enough to bound early design work
- important assumptions are explicit and their statuses are legible
- important risks and edge cases are visible
- relevant problem areas have usable confidence
- any remaining uncertainty is weak enough that Design can carry it forward explicitly without collapsing into reframing

This is a sufficiency judgment, not a perfection standard.

Discovery does not need exhaustive completeness before Design begins.

It does need enough framing integrity that Design can proceed honestly.

## Readiness States

The current minimum Discovery readiness states should be:

- `low`
- `medium`
- `high`

These are stage-level judgments recorded on the Discovery brief artifact.

They should not be overloaded to also mean whether Design has already begun.

The brief artifact's workflow `status` remains separate and uses:

- `draft`
- `accepted`

## Normal Reasons For `low`

Discovery should remain `low` when one or more of these conditions is true:

- the real problem statement is still ambiguous
- intended outcomes are still subjective, conflicting, or weakly grounded
- a major constraint is missing or contradictory
- a critical assumption is still implicit rather than explicit
- a critical problem area has confidence too weak for the next design decision likely to arise
- major blocking framing gaps remain

In this state, the engine should say so directly and continue Discovery rather than offering a softened pseudo-transition.

## Normal Reasons For `high`

Discovery may move to `high` when:

- the main problem framing is stable
- major intended outcomes and constraints are visible
- important assumptions are explicit
- relevant problem-area confidence is good enough for early Design
- remaining uncertainty is bounded and legible rather than hidden

The engine should still explain the main reason the brief is considered ready.

This keeps the judgment inspectable rather than mystical.

## Readiness Artifact Updates

When the engine evaluates readiness, it should update the Discovery brief artifact directly.

At minimum it should update:

- `readiness`
- `readiness_rationale`
- `blocking_gaps`

If the brief is ready, `blocking_gaps` should usually be empty or limited to non-blocking residual uncertainty that is still worth naming in the readable brief.

If the brief is not ready, `blocking_gaps` should remain short and specific.

The engine should not dump every unresolved note into this field.

## Transition Outcomes

Once readiness is evaluated, Discovery should support three outcomes:

### Continue Discovery

Continue Discovery when the brief remains materially weak.

The engine should:

- say directly that Discovery is not yet ready
- name the most important blocking gap
- ask the next narrow Discovery question or propose the next brief revision

### Consensus Transition

Begin Design through the normal path when:

- the brief is `accepted`
- the engine recommends transition
- the operator agrees the brief is strong enough

This is the intended default transition model.

### Explicit Override

Begin Design through an explicit override when:

- Discovery is still meaningfully incomplete
- the operator wants to proceed anyway
- the system makes the weakness explicit rather than hiding it

This is a weaker path and should stay visibly distinct from the normal consensus path.

## Consensus Transition Rule

The normal transition into Design should be consensus-based.

That means:

- the engine may recommend moving on
- the operator may suggest moving on
- the actual transition occurs when both agree the brief is strong enough

The system should not start Design merely because the engine thinks the brief is ready.

It should also not require a ceremonial approval workflow beyond explicit agreement.

The practical interaction should stay lightweight:

- show the readiness judgment
- show the main rationale
- make the remaining important uncertainty explicit
- confirm whether to begin Design

## Override Rule

The override path exists because Clauderfall is not meant to be an absolute hard gate between Discovery and Design.

However, the system should not blur override into ordinary readiness.

The override path should require all of the following:

- the operator explicitly chooses to proceed now
- the brief remains visibly marked as having medium or low readiness in some relevant area
- the resulting Design Start Context preserves those weak-signal areas and assumptions

The engine should explain that proceeding now increases the chance of:

- design churn
- Discovery reentry
- revised framing after Design has already started

## Override Interaction Style

The override interaction should be direct and short.

It should name:

- what is still weak
- why that weakness matters to Design
- that Design may proceed anyway if the operator accepts the extra churn risk

The system should avoid melodrama here.

Override is not a failure state.

It is a weaker but legitimate workflow path.

## Artifact State Changes At Transition

When Discovery transitions into Design, the system should make a small set of explicit artifact changes.

### Discovery Brief

The Discovery brief should:

- preserve its current readable content as canonical
- preserve its latest readiness judgment
- receive a flush checkpoint for the transition state

The normal path should persist the brief as `accepted` before `to_design`.

The override path may still transition from `draft` when the operator explicitly chooses to proceed anyway.

The brief should not be replaced by the Design Start Context.

### Design Start Context

At Design start, the system should derive a Design Start Context from the current Discovery brief.

That artifact should:

- be created as a separate persisted artifact
- capture the design-relevant condensation of the brief
- preserve weak-signal assumptions and low-confidence areas when transition happened through override
- mark `regenerated_after_reentry` as `false` on first creation

## Normal Transition Sequence

The normal sequence should be:

1. evaluate the current Discovery brief readiness as high enough to move forward
2. show the rationale and any remaining meaningful uncertainty
3. persist the brief in `accepted` status with its current readiness judgment
4. confirm consensus to begin Design
5. create the initial Design Start Context
6. begin the Design session against that Design Start Context

This keeps the transition explicit without making it heavy.

## Override Transition Sequence

The override sequence should be:

1. evaluate the current Discovery brief as still materially incomplete
2. show the main blocking or weak framing area
3. explicitly ask whether the operator wants to proceed anyway
4. if yes, flush the Discovery brief with that weaker readiness visible
5. create a Design Start Context that preserves the weak signal
6. begin Design with lower tolerance for later reentry

The system should not promote the brief to looking fully ready just because the operator chose to move forward.

## Relationship To Reentry

The readiness and transition model should compose cleanly with Design-to-Discovery reentry.

If Design later discovers that Discovery framing was weaker than expected:

- the Discovery brief is repaired
- a new Discovery brief checkpoint is created
- the Design Start Context is regenerated from that repaired brief
- Design resumes against the regenerated context

If Design began through explicit override, the threshold for recommending reentry should be lower, because weak framing was already acknowledged at transition time.

## Failure Modes To Avoid

This boundary should avoid:

- treating readiness as a hidden score
- silently beginning Design once the engine thinks the brief is good enough
- using override as an unmarked shortcut that erases weakness
- forcing Discovery to reach perfection before any Design can begin
- starting Design from a weak brief without preserving the weakness explicitly

## Open Questions

The main remaining open questions are:

- whether the operator-facing override interaction should include a standardized short warning block
- whether the Discovery brief should persist a separate transition record beyond the standard checkpoint model

These questions do not block adopting the readiness and transition model above as the current v2 direction.
