---
title: Clauderfall Design To Discovery Reentry
doc_type: design
status: stable
updated: 2026-03-22
summary: Defines when Design should resolve ambiguity locally versus explicitly return to Discovery for problem-framing repair.
---

# Clauderfall Design To Discovery Reentry

## Purpose

This document defines how the Design stage should respond when ambiguity, contradiction, or weak framing appears after the Discovery-to-Design transition.

The goal is to distinguish:

- ordinary design clarification
- genuine problem-framing failure

Without this distinction, Design either reopens Discovery too often or quietly invents missing problem truth.

## Design Position

Design should absorb ordinary design ambiguity locally whenever the problem framing remains stable.

Design should explicitly return to Discovery when the ambiguity means the problem itself is no longer trustworthy enough to design against.

The key question is:

Is the current uncertainty about how to solve the problem, or about what problem should actually be considered true?

If it is the latter, Design should not silently continue.

## Local Clarification

Design should prefer local clarification when the problem framing remains intact and the open issue is design-shaped rather than discovery-shaped.

Typical local clarification cases include:

- choosing between plausible solution structures
- clarifying an interface or boundary inside an already stable problem area
- resolving an implementation-relevant tradeoff that does not alter the problem statement
- making assumptions explicit that were already latent in the Discovery material
- asking for one missing detail whose answer is unlikely to change scope, intended outcomes, or major constraints

In these cases, Design should:

- ask the narrowest useful question
- update the design artifact directly
- preserve visibility into the assumption or uncertainty being resolved

## Discovery Reentry

Design should explicitly return to Discovery when the current issue indicates that the problem framing itself is incomplete, contradictory, or unstable.

Typical reentry cases include:

- the intended outcome is no longer clear
- two Discovery sections materially conflict
- a missing constraint changes what counts as a valid solution
- a newly surfaced edge case changes the real problem boundary
- a supposedly stable assumption turns out to be unknown in a way that alters system scope or viability
- the first-unit recommendation cannot be defended without inventing missing requirements

In these cases, Design should not simply ask a narrow design question and continue as if the framing were still sound.

## Decision Rule

When ambiguity appears, the Design engine should make this judgment:

### Stay In Design

Stay in Design if all of the following are true:

- the problem statement still appears stable
- intended outcomes still appear stable
- major constraints still appear usable
- the ambiguity can be resolved without changing the meaning of the Design Start Context

### Return To Discovery

Return to Discovery if any of the following are true:

- the problem statement itself may need revision
- intended outcomes are materially unclear or conflicting
- a major constraint is missing, contradictory, or newly discovered
- the ambiguity would force Design to invent requirements rather than refine a solution
- confidence in a critical Discovery problem area is too weak for the design choice now required

This should stay a judgment rule, not a rigid checklist.

## Reentry Interaction Style

When Design recommends reentry, it should be explicit and concise.

It should name:

- what appears unstable
- why this is a Discovery issue rather than a Design issue
- what problem-framing question now needs repair

The recommendation should not sound like a failure state. Reentry is a normal correction path when the Design Start Context proves weaker than it first appeared.

## Reentry Scope

A return to Discovery should be as narrow as possible.

The point is to repair the specific problem-framing gap, not to restart Discovery from scratch.

The engine should identify:

- the affected problem area or cross-cutting section
- the unstable assumption, constraint, or intended outcome
- the minimum Discovery question needed to restore trustworthy framing

This keeps the workflow tight and prevents stage thrash.

## Relationship To Context References

When Design detects the need for reentry, it should first use the Design Start Context's section-header references to reopen the relevant Discovery brief sections.

That quick source check should help answer two questions:

- is the ambiguity due to an incomplete Design Start Context condensation
- or is the underlying Discovery brief itself actually weak or contradictory

This is why the Design Start Context carries brief references instead of acting as a standalone truth source.

## Effect On Active Design Work

When reentry is triggered, the current design unit should not continue advancing as if the issue were settled.

The engine should instead:

- mark the affected design pressure explicitly
- avoid increasing readiness based on unstable framing
- resume design progression only after the framing repair is made explicit

This prevents Design from hardening weak assumptions into false concreteness.

## Persistence Rule

Discovery repair during reentry should not create a separate required repair artifact.

The default persistence model should be:

- update the canonical Discovery brief
- regenerate the Design Start Context
- mark the regenerated Design Start Context via its metadata
- resume Design against the repaired Design Start Context

This keeps the stage model clean and avoids introducing a new artifact type for what is fundamentally a correction to problem framing.

A separate repair artifact should only be introduced later if there is a demonstrated continuity problem that the updated brief, regenerated Design Start Context, and its metadata cannot solve cleanly.

## Override Case

If Design was started through an explicit early-start override from incomplete Discovery, the threshold for reentry should be lower.

That is intentional.

The override path already acknowledges that framing weakness is being carried forward. The engine should therefore surface reentry sooner rather than pretending the weaker path behaves like a normal ready Design Start Context.

## Failure Modes To Avoid

The engine should avoid:

- bouncing back to Discovery for ordinary design tradeoffs
- continuing in Design when the problem itself has become unclear
- framing every missing detail as a stage-boundary failure
- treating reentry as a restart of the whole project
- silently revising the problem inside Design without saying so

## Open Question

The main remaining open question is whether regenerated Design Start Context metadata eventually needs more detail than a simple boolean marker.

That question does not block adopting the reentry model above.
