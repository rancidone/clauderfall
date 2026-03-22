---
title: Clauderfall V2 Product Brief
doc_type: brief
status: active
updated: 2026-03-22
summary: Product brief for Clauderfall v2 focused on Discovery and Design for a single senior engineer.
---

# Clauderfall V2 Product Brief

## Product Definition

Clauderfall is a product for a single senior engineer who wants to turn an initially rough software idea into high-quality upstream artifacts for coding work.

Its primary outputs are:

- discovery briefs
- design artifacts

Task artifacts and context artifacts are not part of the v2 product boundary. They are later-stage product directions, likely for v3.

The product's purpose is to improve problem framing and design quality before execution begins.

Clauderfall does this by helping the operator understand and frame the software problem clearly enough that later artifacts do not drift, invent missing requirements, or harden weak assumptions into bad design.

Traceability and rigor matter, but they are not the primary promise. They are part of how the system produces trustworthy downstream artifacts.

## Primary User

The primary user for v2 is a single senior engineer.

This user commonly starts with:

- a feature idea
- a system idea
- a work ticket
- partially formed thinking that is not yet written down clearly

Clauderfall must work even when there is no existing codebase or document set.

## Core Problem

The core failure mode is that ordinary LLM interaction tends to jump into solution structure before the problem is framed well enough.

That causes predictable downstream failures:

- the wrong problem gets solved
- scope drifts and requirements are invented
- architectural realities are missed
- business rules are misunderstood or omitted
- important non-functional constraints such as performance, reliability, and security are under-specified
- later design work becomes unsafe, vague, noisy, or incomplete

## Desired Product Outcome

Clauderfall v2 should help a senior engineer arrive at a clear problem brief and a strong design artifact without collapsing too early into implementation structure or execution planning.

Early stages should prevent:

- premature collapse from problem framing into solution design
- hidden assumptions becoming implicit truth
- missing constraints and edge cases

## Product Principles

- Problem framing must stay ahead of solution structure.
- Assumptions must be explicit and operator-visible.
- Human review of evolving artifacts is required.
- The system must support interaction, not replace it with opaque state transitions.
- Operator-readable drafts are necessary to make artifacts trustworthy.
- Existing repos, docs, or code are optional evidence sources, not foundational assumptions.

## Product Model

Clauderfall v2 is a two-stage system:

- Discovery: an interview-driven stage that turns rough intent into a visible problem-framing brief
- Design: an interview-driven stage that turns that brief into a stronger design artifact without skipping review or hiding assumptions

Both stages should be interactive, operator-visible, and reviewable rather than schema-first or silent artifact generators.

## Discovery Role In The Product

Discovery exists to produce a strong enough problem framing that Design does not need to invent the problem.

Discovery is not the design stage.

It should:

- help the operator articulate the real problem
- challenge premature solutioning
- surface assumptions and constraints
- expose risks and edge cases
- maintain a visible evolving brief organized by problem areas/themes

Discovery may include high-level system architecture only when it is necessary to clarify the problem, expose constraints, or test whether the framing is coherent.

Discovery should stop short of:

- concrete interfaces
- implementation detail
- task decomposition

## Discovery Output

The output of Discovery should be a visible, readable brief organized around problem areas or themes rather than a single flat narrative.

Each problem area should make the framing concrete enough for Design to work from without inventing the problem.

A Discovery brief should therefore capture, for each important problem/theme where relevant:

- the problem statement
- intended outcomes
- constraints
- assumptions
- risks and edge cases
- open questions where material
- confidence: `low` / `medium` / `high`

The brief should also support cross-cutting sections for items that span multiple problem areas, such as:

- global constraints
- shared assumptions
- systemic risks
- cross-cutting open questions

## Discovery-To-Design Readiness

Discovery should prefer to reach a strong, broadly complete problem framing before Design begins.

This is the intended workflow. Starting Design early and using later Discovery passes to repair major framing gaps is allowed, but it is a weaker path that increases churn and reduces confidence in downstream artifacts.

Discovery is ready for Design when the brief is clear enough that Design does not need to invent the problem and confidence is strong across the relevant problem areas.

Important assumptions do not all need to be resolved before Design begins, but they must be explicit and treated as weaker signal than an explicit human decision.

External uncertainties should be called out as risks.

Transition into Design should be consensus-based:

- the interviewer may recommend moving on
- the operator may suggest moving on
- the handoff should happen only when both agree the discovery brief is strong enough

Clauderfall v2 should not treat Discovery as an absolute hard gate. However, it should require an explicit operator override to begin Design when Discovery is still meaningfully incomplete. That override should make clear that proceeding now increases the risk of design revision and reframing.

## Design Role In The Product

Design is the stage where solution structure becomes concrete.

Design is responsible for turning the discovery brief into a design artifact that is specific enough to drive later decomposition into machine-readable tasks.

Design may include:

- system structure
- component responsibilities
- concrete interfaces
- implementation-relevant design detail
- important tradeoffs and constraints

The point is not to force one fixed template. The point is to make the solution concrete enough that later decomposition is grounded rather than invented.

## Design Output

The v2 Design output should be a hybrid artifact.

It should remain readable as an engineering design document, but it should also carry enough explicit structure that later decomposition is straightforward.

Design artifacts in v2 should be separate documents, not just sections inside one large shared design doc.

The primary unit of design is a design unit. A design unit represents a specific system, subsystem, or other concrete design boundary being worked through in Design.

Each design unit should have its own:

- readable design document
- structured fields needed for later decomposition
- readiness rating
- brief readiness justification

Clear inputs and outputs are useful guidance when they exist, but they are not a universal requirement.

## Design Readiness

A design readiness rating should mean confidence that the relevant problem has been solved at the design level.

It is not a claim that every possible edge case has been handled. It is a claim that the design is strong enough on the main problem and the strong-signal edge cases that materially affect correctness, safety, or viability.

A readiness rating should be actionable for build decisions.

High readiness means the design appears to solve the intended problem concretely enough that implementation should not need to guess at major decisions.

Lower readiness means important uncertainty remains about whether the design actually solves the problem, especially around constraints, tradeoffs, or strong-signal edge cases.

The readiness justification should stay short. It should explain the main reason the unit is or is not ready, without turning into a long review narrative.

## Design Workflow

Design is interview-led and iterative.

A design pass may reveal that the current solution boundary is still too large or unclear and should be broken into smaller design units before the design is strong enough.

Sometimes that decomposition should create explicit parent-child relationships between design units. Sometimes it should not.

If a design unit has children, its readiness is not independent of them. Parent readiness should depend in part on the readiness of the child units it relies on.

When Design begins, Clauderfall should try to lead work in a logical dependency order. In v2, that sequencing should stay heuristic and conversational rather than being driven by a formal dependency graph.

## Artifact Persistence

Discovery and Design do not need to persist every working revision immediately.

Within an active session, stage artifacts may be maintained in session context as working draft state.

However, the system should explicitly flush that working state to persisted artifacts before context compaction risks losing important stage progress.

The preferred model for v2 is:

- maintain the evolving artifact in session while the interview is active
- avoid unnecessary persistence churn on every small turn
- flush explicitly at meaningful checkpoints and before context pressure makes loss likely

A practical trigger is to flush before context compaction, for example around 60% context usage.

## Draft Advancement

Within Discovery and Design, drafts should advance by default during the interview.

The system does not need explicit user approval for every substantive revision before treating it as the current working artifact.

The operator remains the final review gate at stage transition.

## Open Product Questions

- What is the right persistent representation for readable stage artifacts plus the supporting structured metadata they need?
- What is the right artifact shape for Discovery and Design so they remain readable first without becoming vague?
- What review and approval flow should exist around stage transitions, overrides, and pre-compaction flushes?
