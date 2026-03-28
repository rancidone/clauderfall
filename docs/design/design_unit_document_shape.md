---
title: Clauderfall Design Unit Document Shape
doc_type: design
status: stable
updated: 2026-03-22
summary: Defines the recommended human-readable structure for a Clauderfall design unit document.
---

# Clauderfall Design Unit Document Shape

## Purpose

This document defines the recommended shape of the readable design document for a design unit.

The goal is not to force a rigid template. The goal is to give the Design engine a consistent document structure that preserves clarity, reviewability, and design rigor.

## Design Position

A design unit document should read like an engineering design note, not like:

- a task plan
- a questionnaire transcript
- a schema dump
- a speculative essay

The document should help a senior engineer answer:

- what concrete boundary is being designed
- what problem this unit solves
- what design has been chosen
- what tradeoffs and risks matter
- what remains unresolved

## Recommended Section Set

The readable document should usually contain the following sections.

Section names can vary slightly, but the semantic content should remain stable.

### 1. Scope

This section defines the unit boundary and the concrete problem being solved.

It should answer:

- what this unit owns
- what it does not own
- why this unit exists as a separate design boundary

If the unit boundary cannot be explained cleanly, the design unit may still be too broad or ill-formed.

### 2. Design Context

This section carries only the discovery and system context that materially constrains the design.

It should not restate the whole discovery brief.

Useful content includes:

- requirements that shape the design
- non-functional constraints
- upstream assumptions that the design is currently relying on
- related units or system context that affect design choices

### 3. Proposed Design

This is the core of the document.

It should describe the actual solution shape in concrete terms.

Depending on the unit, this may include:

- responsibilities
- major components or internal parts
- state model
- interactions
- data flow
- control flow
- lifecycle behavior

This section should be concrete enough that the reader can understand how the unit works, not just what goals it aspires to meet.

### 4. Interfaces And Boundaries

This section is included when the unit materially interacts with other units, systems, or actors.

It should describe the contracts that matter for correctness or implementation.

This may cover:

- external interfaces
- upstream and downstream interactions
- invariants at the boundary
- failure or error behavior that affects callers or dependents

Not every design unit needs a heavyweight API specification, but interaction points should be made explicit when they matter.

### 5. Tradeoffs And Alternatives

This section records the important choices that shaped the design.

It should focus on decisions with real consequence, such as:

- rejected approaches
- cost or complexity tradeoffs
- constraints that forced a non-obvious design

This section is important because it keeps the artifact from looking more inevitable than it really was.

### 6. Risks And Edge Cases

This section covers the strong-signal risks and edge cases that materially affect viability.

It should not become an exhaustive brainstorming dump.

The bar is practical importance:

- what could break correctness
- what could break safety
- what could break operability
- what could force material redesign if ignored

### 7. Open Questions

This section lists unresolved design questions that still matter.

These should align with the structured `open_questions` field, but the document may give more context where useful.

If this section dominates the document, the unit is probably not yet mature enough to treat as strongly designed.

## Optional Sections

Some units will need extra sections. These are optional, not universal requirements:

- rollout or migration considerations
- observability or operational concerns
- performance model
- security considerations
- compatibility constraints
- examples or request flows

The engine should add these only when they materially improve the design.

## Section Order Rule

The default order should move from boundary to solution to pressure:

1. Scope
2. Design Context
3. Proposed Design
4. Interfaces And Boundaries
5. Tradeoffs And Alternatives
6. Risks And Edge Cases
7. Open Questions

This order keeps the document readable and prevents it from opening with unresolved noise before the actual design is visible.

## What The Document Should Avoid

The readable design document should avoid:

- implementation task lists
- full acceptance-test plans
- boilerplate sections with no content
- repeating structured metadata in prose without adding meaning
- vague aspirational language that avoids concrete design claims

If a section has nothing meaningful to say for a given unit, it should be omitted or folded into a nearby section rather than left as empty scaffolding.

## Relationship To Structured Side

The readable document remains primary.

The structured side should summarize a few operational facts, but it should not replace the document's responsibilities.

The intended split is:

- the document explains the design
- the structured side supports indexing, sequencing, and build-readiness handling

## Review Rule

A reviewer should be able to read the design document and answer, with minimal ambiguity:

- what this unit is
- how it works
- what it depends on
- what risks remain
- why it is or is not ready

If the reviewer cannot answer those questions, the problem is in the design, the document, or the unit boundary.

## Open Question

The main remaining open question is whether Clauderfall should later standardize a more explicit subsection for examples and flows when the design concerns behavior-heavy systems.

That question does not block using this document shape as the current default.
