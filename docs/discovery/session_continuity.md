---
title: Session Continuity Discovery Brief
status: ready
last_updated: 2026-04-11
summary: Discovery brief for explicit handoff and continue workflows that preserve continuity across long-running work without polluting new sessions.
---

# Session Continuity Discovery Brief

## Overview

Clauderfall already has strong Discovery and Design working modes.

What is missing is durable continuity during implementation work and during long design efforts with many design units, where context churn causes unfinished work and important open questions to get lost.

This brief frames the continuity problem specifically.

It does not restate the full product mission or the Discovery and Design engine contracts.

## Problem Area: Long-Running Continuity

### Problem Statement

Long-running implementation work and long multi-session design efforts lose continuity across context churn.

Important open questions, next steps, and unfinished work can disappear between sessions, while stale carry-forward context can also misdirect the next session if it is treated as authoritative.

The continuity problem is therefore two-sided: Clauderfall needs to preserve what still matters without polluting the runtime with outdated or speculative session state.

### Intended Outcomes

- Clauderfall should provide long-running continuity over multi-week work.
- Continuity should help the next session recover the current objective, next steps, and open questions quickly.
- The system should avoid silently carrying stale in-flight context into a new session.
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
- Operator truth and session working state need semantic separation even when both matter during handoff.
- A small explicit handoff contract is more reliable than broad state preservation.
- Open questions are important enough to preserve explicitly, but they also decay quickly enough to need status marking.
- Active artifacts should describe current truth rather than carrying backward-looking historical narrative.
- Active artifacts should not carry speculative future-state placeholders that do not affect current work.

### Risks And Edge Cases

- Fire-and-forget handoff generation may still produce noisy or misleading carry-forward if the skill contract is weak.
- Current objectives and next steps may themselves go stale and misdirect the resumed session.
- Open questions may either be silently dropped or carried forward long after they stopped mattering.
- A compact handoff may omit important nuance unless related durable artifacts remain easy to inspect selectively.

## Durable Artifact Relationship

This brief assumes the current durable artifact set includes:

- Discovery briefs
- Design units
- session handoff / carry-forward records

Discovery briefs and Design units remain higher-collaboration artifacts.

Handoff records are lower-collaboration working artifacts used to resume work safely.

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
- Clauderfall should not preserve large amounts of in-flight session context as if it were durable project memory.
- Handoff should not become a long transcript dump or a 300-line session summary.
- Active artifacts should not accumulate backward-looking statements that are only relevant as historical explanation.
- Active artifacts should not retain vague future-thinking notes such as `maybe later`, `deferred`, or similar placeholders.

## Discovery Readiness

This brief is considered ready for Design.

The framing is coherent enough for design work to define:

- the explicit `/handoff` and `/continue` workflows
- the handoff write and continue read contracts
- the separation between durable collaborative artifacts and session-scoped continuity context
- the minimal helper-script role that assists continuity without becoming a heavy control surface
