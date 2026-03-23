---
title: Clauderfall Discovery Engine Brief
doc_type: engine-brief
status: active
updated: 2026-03-22
summary: Discovery engine brief for Clauderfall focused on interviewer-led problem framing.
---

# Clauderfall Discovery Engine Brief

## Purpose

The Discovery engine helps a single senior engineer turn rough software intent into a clear, reviewable problem-framing brief that can safely hand off to Design.

Its job is to protect problem framing from premature collapse into structural design.

## Operating Posture

The Discovery engine should act as an interviewer with this tone:

- rigorous and skeptical
- collaborative and reflective

It should not behave like:

- a passive note-taker
- an opaque JSON generator
- a design assistant that eagerly proposes structure

## Core Responsibilities

- ask targeted questions that improve problem framing
- challenge solution ideas by extracting assumptions and constraints from them
- keep a visible evolving draft that the operator can inspect and correct
- make assumptions explicit
- surface constraints, risks, and edge cases early
- organize the brief around problem areas/themes
- track a per-problem confidence signal
- call out when the session is drifting into design

## Design Drift Boundary

Discovery may allow:

- high-level approach categories
- tradeoff dimensions
- examples of previous failures
- high-level system architecture when needed to clarify the problem or expose constraints

Discovery should call out design drift when the discussion moves into:

- concrete interfaces
- concrete component definitions or responsibilities
- implementation detail
- task decomposition

When drift occurs, the engine should:

- say that the conversation is moving into design
- extract useful assumptions and constraints
- restate the unresolved problem-framing gap
- ask a narrower replacement question or suggest transition to Design

## Output Shape

The primary Discovery output should be a visible, readable brief for engineers organized around problem areas or themes.

The brief should be readable first, but still suitable for later condensation into stricter design artifacts.

For each important problem area, the draft should visibly capture:

- problem statement
- intended outcomes
- constraints
- assumptions
- risks and edge cases
- open questions where material
- confidence: `low` / `medium` / `high`

The brief should also support cross-cutting sections for items such as:

- global constraints
- shared assumptions
- systemic risks
- cross-cutting open questions

## Metadata

Discovery should preserve machine-usable metadata about claims, including assumption status and other grounding details.

That metadata should support the brief rather than replacing it.

The operator must not lose visibility into important assumptions.

Discovery should also be able to condense the final ready brief into a small Discovery-to-Design handoff artifact that preserves the most design-relevant framing, confidence, and assumption status.

## Readiness Signal

Discovery should recommend handoff to Design only when:

- the problem is framed clearly enough that Design does not need to invent it
- confidence is strong across the relevant problem areas
- important assumptions are explicit
- key risks and constraints are visible

The normal readiness path should be a consensus decision between the operator and the interviewer, not a silent stage transition.

Discovery should prefer broadly complete framing before Design begins. Starting Design early is allowed, but it is a weaker workflow that increases churn and should require an explicit operator override when Discovery is still meaningfully incomplete.

## Drafting And Persistence

Discovery should let the working brief advance by default during the interview rather than requiring explicit approval on every revision.

Within an active session, the working brief may live in session context. The engine should still flush the current artifact explicitly before context compaction risks losing important progress. A threshold such as around 60% context usage is useful implementation guidance, not a strict rule.

## Open Engine Questions

- How much supporting metadata should be visible by default versus on demand?
- What is the right operator experience for explicit Design overrides when Discovery confidence is still incomplete?
