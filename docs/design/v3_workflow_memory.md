---
title: V3 Workflow Memory Discovery Brief
doc_type: brief
status: ready
updated: 2026-04-11
summary: Discovery brief for a markdown-first v3 pivot centered on Discovery, Design, and explicit session continuity through handoff and continue skills.
---

# V3 Workflow Memory Discovery Brief

## Overview

Clauderfall v3 should shrink to the minimum product surface that materially improves professional-quality software development over multi-week work.

Discovery and Design remain first-class because they help the developer understand the problem domain and validate solutions before code generation.

What is missing is durable continuity during implementation work and during long design efforts with many design units, where context churn causes unfinished work and important open questions to get lost.

The current v2 direction is over-involved in runtime mediation. MCP-heavy surfaces and structured sidecars added friction, duplicated state, and interfered with the LLM's native strengths around reading markdown and writing files.

The v3 pivot is therefore toward a workflow memory system with strong collaborative artifacts, explicit skill invocation, and minimal framework interference.

## Problem Area: Runtime Interference

### Problem Statement

Clauderfall currently tries to mediate too much of the runtime's normal work.

Custom MCP surfaces and structured sidecars duplicate information that already exists in readable artifacts, create additional failure modes, and move the product away from the higher-value work of interviewing, design guidance, and continuity.

This over-structuring makes the system harder to trust and maintain without clearly improving artifact quality or continuity outcomes.

### Intended Outcomes

- Clauderfall should rely on markdown-first artifacts the operator and model can inspect directly.
- The product should stop requiring schema-first or sidecar-first state management for normal workflow.
- The framework should assist the runtime without gating ordinary file reads and writes.
- Discovery and Design should preserve the strong interviewing and solution-shaping behavior that made earlier skill-driven work valuable.

### Constraints

- Clauderfall should not require MCP-style mediation for routine artifact authoring.
- Helper scripts may assist with orientation, summarization, or validation, but they should not become mandatory control points.
- The product should remain compatible with the natural working model of current LLM runtimes.

### Assumptions

- The main product value is not custom protocol surface area.
- Readable markdown is a better primary durability layer than duplicated structured sidecars.
- Skill quality matters more than backend mediation for Discovery and Design outcomes.

### Risks And Edge Cases

- Removing too much structure may collapse the workflow into a loose folder of notes with weak operating discipline.
- Helper scripts may gradually recreate the same control-heavy surface if their contract is too rigid.
- A markdown-first approach may still fail if artifact boundaries and invocation patterns remain vague.

## Problem Area: Long-Running Continuity

### Problem Statement

Long-running implementation work and long multi-session design efforts lose continuity across context churn.

Important open questions, next steps, and unfinished work can disappear between sessions, while stale carry-forward context can also misdirect the next session if it is treated as authoritative.

The continuity problem is therefore two-sided: Clauderfall needs to preserve what still matters without polluting the runtime with outdated or speculative LLM-generated state.

### Intended Outcomes

- Clauderfall should provide long-running continuity over multi-week work.
- Continuity should help the next session recover the current objective, next steps, and open questions quickly.
- The system should avoid silently carrying stale LLM in-flight state into a new session.
- The continuity surface should stay compact and high-signal rather than turning into transcript replay or general long-term memory.

### Constraints

- Continuity must act through explicit skill invocation rather than automatic session startup behavior.
- `/handoff` and `/continue` should be explicit user-called workflows.
- Handoff artifacts should be brief and targeted, roughly 20 to 100 useful lines.
- `/continue` should use the latest handoff as its primary resume surface.
- `/continue` is read-only with respect to handoff artifacts.
- Handoff artifacts should be private local records stored under `docs/handoff/` and ignored by git.

### Assumptions

- Automatic startup injection of continuity context is more likely to pollute a session than help it.
- Operator truth and LLM working state need semantic separation even when both matter during handoff.
- A small explicit handoff contract is more reliable than broad state preservation.
- Open questions are important enough to preserve explicitly, but they also decay quickly enough to need status marking.

### Risks And Edge Cases

- Fire-and-forget handoff generation may still produce noisy or misleading carry-forward if the skill contract is weak.
- Current objectives and next steps may themselves go stale and misdirect the resumed session.
- Open questions may either be silently dropped or carried forward long after they stopped mattering.
- A compact handoff may omit important nuance unless related durable artifacts remain easy to inspect selectively.

## Durable Artifact Set

The initial explicit durable artifact set for v3 is:

- Discovery briefs
- Design units
- session handoff / carry-forward records

These are collaborative records, not purely operator-authored canon.

Discovery briefs and Design units involve higher collaboration and visible iteration between the operator and the skill.

Handoff records are lower-collaboration working artifacts that are mostly produced through the skill contract and intended to be fast to create and consume.

## Handoff Contract

The default handoff contract should stay minimal and targeted.

The core contents are:

- current objective
- next steps
- open questions

Open questions should carry explicit status markers:

- `active`
- `stale`

Resolved questions are not open questions and should be removed from the handoff artifact rather than retained there.

The handoff artifact is the primary resume surface for `/continue`, but it should not be treated as durable shared project truth.

## Anti-Goals

- Clauderfall should not auto-inject continuity context at session start.
- Clauderfall should not depend on broad MCP-facing runtime mediation for normal workflow.
- Clauderfall should not preserve large amounts of in-flight LLM context as if it were durable project memory.
- Handoff should not become a long transcript dump or a 300-line session summary.

## Discovery Readiness

This brief is considered ready for Design.

The framing is coherent enough for design work to define:

- the v3 skill surface around explicit `/discovery`, `/design`, `/handoff`, and `/continue` workflows
- the markdown-first artifact boundaries for Discovery, Design, and handoff
- the separation between durable collaborative artifacts and tentative session-scoped continuity context
- the handoff write and continue read contracts
- the minimal helper-script role that assists skills without recreating a heavy runtime mediation layer
