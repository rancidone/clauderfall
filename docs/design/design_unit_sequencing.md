---
title: Clauderfall Design Unit Sequencing
doc_type: design
status: active
updated: 2026-03-22
summary: Defines how the Design engine should choose, decompose, and sequence design units during an active design session.
---

# Clauderfall Design Unit Sequencing

## Purpose

This document defines how the Design engine should decide what unit to work on next when multiple design paths are available.

The goal is to keep sequencing logical and operator-comprehensible without turning Design into a formal project planner.

## Design Position

Design should proceed in a logical dependency order, but that order should remain heuristic and conversational.

The engine should not pretend it has a complete dependency graph or a mathematically optimal plan.

It should instead make explicit, reviewable sequencing judgments based on the current design pressure in front of it.

## Core Sequencing Question

At any point in Design, the engine should be trying to answer:

What is the next design unit that will most reduce downstream guesswork or unblock meaningful design progress?

This framing matters because the right next unit is not always:

- the largest remaining unit
- the first unit discovered
- the most interesting unit
- the first unit that seems implementation-adjacent

## Primary Sequencing Heuristics

When recommending the next unit, the engine should weigh these heuristics.

### 1. Dependency Criticality

Prefer units that other units materially depend on for their own design clarity or readiness.

If several downstream units are blocked on one unresolved boundary or contract, that upstream unit should usually come first.

### 2. Architectural Leverage

Prefer units whose design will settle important system shape questions.

Some units define major boundaries, contracts, or state/control patterns that influence many later decisions. Those units have higher sequencing value than isolated leaves.

### 3. Unresolved Risk Concentration

Prefer units where unresolved risk is both strong-signal and central to solution viability.

If a unit carries the main uncertainty around correctness, safety, operability, or feasibility, delaying it creates false confidence elsewhere.

### 4. Boundary Clarity

Prefer units that can actually be designed as coherent units now.

If a candidate unit is still too broad or muddy to support concrete design, the engine should decompose it or choose a more stable unit instead.

### 5. Near-Term Build Value

Prefer units that could plausibly reach `high` readiness soon once their remaining design pressure is addressed.

This does not mean Design should optimize for easy wins. It means the engine should notice when a unit is close to becoming a legitimate build candidate.

## Heuristics The Engine Should Avoid

The engine should not sequence work primarily by:

- document order
- arbitrary breadth-first or depth-first traversal
- whichever unit the interviewer can write about fastest
- whichever unit sounds most implementation-detailed

Those patterns create motion without necessarily improving design quality.

## Candidate Recommendation Model

When more than one plausible next unit exists, the engine should present a small set of candidate recommendations rather than silently picking one.

The default recommendation model should be:

- recommend one primary next unit
- optionally mention one or two secondary candidates
- give a short reason for the primary recommendation
- explain why the alternatives are not first

This keeps sequencing explicit without forcing the operator through a heavyweight choice workflow.

## Recommendation Style

The engine's recommendation should be brief and concrete.

The intended style is:

- primary unit
- reason it reduces the most uncertainty or unblocks the most design
- notable alternative if the operator wants a different path

The recommendation should sound like design guidance, not backlog grooming.

## Decomposition Rule

If the current unit is too broad, the engine should prefer decomposition over vague continuation.

Signals that decomposition is needed include:

- the unit cannot be explained with a stable boundary
- the design document keeps mixing multiple separate problems
- readiness cannot be judged honestly because the unit bundles unrelated uncertainty
- proposed solution details keep splitting into independently reviewable subproblems

When decomposition happens, the engine should identify whether the resulting units are:

- parent-child design units
- peer units with dependency relationships
- a mix of both

It should not force every split into a tree if the design shape does not justify that structure.

## Parent-Child Sequencing Rule

When a parent unit is decomposed into children, the engine should usually sequence work toward the child units that most determine whether the parent can be considered buildable.

This means:

- not every child needs to be explored immediately
- not every child needs equal depth before the parent becomes useful
- the parent's readiness should reflect the unresolved children that materially affect it

## Peer Dependency Rule

When units are peers rather than parent and child, sequencing should usually favor the peer that provides the strongest design constraint on the others.

Examples include:

- a contract-defining unit before an implementation-shaped dependent unit
- a state-model unit before units whose behavior depends on that model
- a failure-handling boundary before components whose correctness depends on that boundary

## Operator Override

The operator should always be able to push the session toward a different unit.

If the operator chooses a non-recommended path, the engine should not resist mechanically. It should:

- make the tradeoff explicit
- continue productively on the chosen path
- preserve visibility into the risks created by that sequencing choice

This keeps the workflow collaborative rather than paternalistic.

## Sequencing Output

The engine does not need a formal global plan artifact.

However, it should be able to express, at any checkpoint:

- the current unit
- the likely next unit
- why that next unit is recommended
- what dependency or risk is driving that recommendation

This is enough sequencing structure for the current product boundary.

## Failure Modes To Avoid

The engine should avoid:

- decomposing too early just because a unit is complex
- keeping units too large because decomposition feels like planning
- recommending a next unit without naming the reasoning
- treating every unresolved question as deserving its own design unit
- pretending the sequencing heuristic is more certain than it is

## Open Question

The main remaining open question is whether the structured side later needs a lightweight field for `recommended_next_units`.

For the current design, that recommendation should remain conversational and session-local rather than persisted as required artifact structure.
