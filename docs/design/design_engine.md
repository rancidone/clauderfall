---
title: Clauderfall Design Engine Brief
doc_type: engine-brief
status: active
updated: 2026-03-22
summary: Design engine brief for Clauderfall focused on interview-led solution concretization.
---

# Clauderfall Design Engine Brief

## Purpose

The Design engine helps a single senior engineer turn a strong discovery brief into a concrete, reviewable design artifact.

Its job is to make the solution concrete without collapsing immediately into execution planning or hiding unresolved uncertainty.

## Operating Posture

The Design engine should act as an interviewer with this tone:

- rigorous and skeptical
- collaborative and reflective
- concrete about tradeoffs and unresolved design choices

It should not behave like:

- a passive note-taker
- a one-shot design generator
- a task planner pretending to be a design reviewer

## Core Responsibilities

- turn a discovery brief into a concrete solution design
- lead the operator through design work in a logical dependency order
- keep the evolving design visible and reviewable
- make unresolved decisions, assumptions, and tradeoffs explicit
- identify when the current design unit is still too broad and should be decomposed
- assign a readiness rating with a brief rationale to each design unit

## Scope

Design is the stage where solution structure becomes concrete.

Design may include:

- system structure
- component or subsystem responsibilities
- interfaces
- implementation-relevant design detail
- important tradeoffs and constraints

Design should stop short of:

- pretending every design must be globally complete before useful work can begin
- forcing one fixed template regardless of problem shape
- turning design output into execution-oriented task management

## Design Unit Model

The primary unit of design is a design unit.

A design unit represents a specific system, subsystem, or other concrete design boundary being worked through in Design.

Each design unit should have its own:

- readable design document
- supporting structured fields where they materially improve later planning
- readiness rating
- brief readiness justification

Clear inputs and outputs are useful guidance when they exist, but they are not a universal requirement.

## Decomposition

Design is iterative.

A design pass may reveal that the current solution boundary is still too large or unclear and should be broken into smaller design units before the design is strong enough.

Sometimes that decomposition should create explicit parent-child relationships between design units. Sometimes it should not.

If a design unit has children, its readiness is not independent of them. Parent readiness should depend in part on the readiness of the child units it relies on.

## Readiness Signal

A design readiness rating should mean confidence that the relevant problem has been solved at the design level.

It is not a claim that every possible edge case has been handled. It is a claim that the design is strong enough on the main problem and the strong-signal edge cases that materially affect correctness, safety, or viability.

The rating should be actionable for build decisions.

High readiness means the design appears to solve the intended problem concretely enough that implementation should not need to guess at major decisions.

Lower readiness means important uncertainty remains about whether the design actually solves the problem, especially around constraints, tradeoffs, or strong-signal edge cases.

Each readiness rating should include a brief justification that explains the main reason the unit is or is not ready.

## Workflow

Design should advance the working draft by default during the interview rather than requiring explicit approval on every revision.

Within an active session, the working design may live in session context. The engine should still flush the current artifact explicitly before context compaction risks losing important progress.

The operator remains the final review gate for deciding whether a design unit is ready enough to treat as buildable.

## Open Engine Questions

- What is the right structured shape for a design unit without making the artifact feel schema-first?
- How should design-unit readiness be represented so it is brief but still dependable?
- When decomposition reveals multiple candidate next units, what is the best operator experience for sequencing recommendations?
