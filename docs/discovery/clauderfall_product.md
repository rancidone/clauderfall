---
title: Clauderfall Product Discovery Brief
status: stable
last_updated: 2026-04-11
summary: Top-level product discovery brief for Clauderfall v3 focused on professional-quality Discovery, Design, and workflow continuity over multi-week work.
---

# Clauderfall Product Discovery Brief

## Product Definition

Clauderfall is a product for a single senior engineer who wants stronger software development outcomes from LLM-assisted work.

Its core value is twofold:

- improve artifact quality through strong Discovery and Design work
- preserve long-running continuity over multi-week work

Clauderfall is therefore not just a document folder and not primarily a runtime protocol layer.

It is a workflow memory system with strong collaborative artifacts and explicit skill-driven working modes.

## Primary User

The primary user is a single senior engineer.

This user may be working from:

- a rough feature idea
- a system or architecture direction
- a partially implemented codebase
- a long-running design effort
- a multi-week implementation thread that risks losing continuity

Clauderfall should help even when the current project state is incomplete, drifting, or spread across many sessions.

## Core Problem

Ordinary LLM interaction tends to fail in two predictable ways:

- it jumps into solution structure before the problem is framed well enough
- it loses continuity across long-running work or carries stale context forward in misleading ways

These failures produce downstream problems such as:

- the wrong problem gets solved
- scope or requirements drift
- weak assumptions harden into design decisions
- unfinished work and important open questions disappear across context churn
- stale session context misdirects later implementation or design sessions

## Desired Product Outcome

Clauderfall should help a senior engineer:

- understand the problem domain before solutioning
- validate solutions before code generation
- resume long-running work without re-deriving everything from scratch

The product should improve software development quality without over-mediating the runtime.

## Product Principles

- problem framing must stay ahead of solution structure
- Discovery and Design remain first-class working modes
- assumptions must be explicit and operator-visible
- human review of evolving artifacts is required
- readable markdown artifacts are the primary durability layer
- continuity context must be compact, selective, and explicit
- explicit skill invocation is preferred over automatic startup behavior
- the framework should assist normal LLM work, not gate it

## Product Model

Clauderfall v3 currently centers on four explicit skills:

- `/discovery`
- `/design`
- `/handoff`
- `/continue`

Discovery and Design produce strong collaborative artifacts.

Handoff and continue provide workflow continuity through brief, targeted carry-forward records rather than transcript replay or broad automatic memory injection.

## Durable Artifact Set

The initial durable artifact set is:

- Discovery briefs
- Design units
- session handoff / carry-forward records

Discovery briefs and Design units are reviewable collaborative project artifacts.

Handoff records are compact personal continuity artifacts used primarily to resume work safely.

## Anti-Goals

- Clauderfall should not auto-inject continuity context at session start.
- Clauderfall should not depend on MCP-heavy runtime mediation for normal workflow.
- Clauderfall should not rely on duplicated sidecar state as the primary source of truth.
- Clauderfall should not treat large amounts of in-flight LLM state as durable project memory.
