---
title: Clauderfall System Discovery Brief
status: ready
last_updated: 2026-04-11
summary: Top-level Discovery brief for Clauderfall v3 covering the system problem, intended outcomes, and scoped follow-on discovery areas.
---

# Clauderfall System Discovery Brief

## Overview

Clauderfall is a tool for a single senior engineer doing LLM-assisted software development over multi-week work.

Its job is to improve software development quality by strengthening upstream thinking and by preserving continuity across long-running work.

Discovery and Design are already valuable first-class working modes.

What the system still needs is a coherent continuity layer and disciplined maintenance of the active docs set so the product can stay usable as work and artifacts accumulate.

## Problem Area: Upstream Quality

### Problem Statement

Ordinary LLM interaction tends to jump into solution structure before the problem is framed well enough.

That causes the wrong problem to be solved, weak assumptions to harden into design, and downstream work to drift.

### Intended Outcomes

- Clauderfall should help the developer understand the problem domain before solutioning.
- Clauderfall should help the developer validate solutions before code generation.
- Discovery and Design should remain strong, explicit working modes rather than collapsing into generic prompting.

### Constraints

- Problem framing must stay ahead of solution structure.
- Assumptions must be explicit and operator-visible.
- Active artifacts should remain readable and reviewable.

### Assumptions

- Strong Discovery and Design work materially improve software development quality.
- Artifact quality matters more than workflow ceremony for its own sake.

### Risks And Edge Cases

- If Discovery and Design lose their sharp boundaries, the system will drift back toward vague assistant behavior.
- If active artifacts become bloated or stale, their value as working surfaces will degrade.

## Problem Area: Long-Running Continuity

### Problem Statement

Long-running implementation work and long multi-session design efforts lose continuity across context churn.

Important open questions, next steps, and unfinished work can disappear between sessions, while stale carry-forward context can misdirect later work.

### Intended Outcomes

- Clauderfall should preserve continuity over multi-week work.
- Continuity should help a new session recover what matters now without replaying broad historical context.

### Constraints

- Continuity should use explicit workflows rather than automatic startup injection.
- Continuity artifacts should stay compact and current-truth-oriented.

### Assumptions

- The continuity problem is important enough to justify dedicated workflow support.

### Risks And Edge Cases

- Continuity can fail by losing important state.
- Continuity can also fail by preserving stale state too aggressively.

## Problem Area: Documentation Integrity

### Problem Statement

As the product evolves, the docs set can drift structurally and semantically.

Overlapping docs, transitional naming, stale narrative, and speculative future placeholders can make the active docs harder to trust as current truth.

### Intended Outcomes

- The active docs set should stay coherent, minimal, and role-clean.
- Active docs should describe current truth rather than backward-looking or speculative narrative.

### Constraints

- Canonical docs should stay under `docs/`.
- Indexes should remain accurate as docs are added, renamed, narrowed, split, merged, or deleted.

### Assumptions

- Documentation maintenance is a recurring workflow, not one-off cleanup.

### Risks And Edge Cases

- If maintenance is too passive, docs sprawl will continue.
- If maintenance is too aggressive, useful distinctions may be lost.

## Product Principles

- Discovery and Design remain first-class working modes.
- Continuity should be explicit, compact, and selective.
- Active artifacts should describe current truth.
- Active artifacts should not accumulate backward-looking narrative or vague future placeholders when they do not affect current work.
- Readable markdown artifacts are the primary durability layer.
- The framework should assist the LLM runtime without over-mediating it.

## Scoped Follow-On Discovery

This top-level brief frames the overall system.

More specific discovery work currently exists for:

- `session_continuity.md`
- `document_maintenance.md`

Those briefs should stay narrower than this document and should not restate the full Clauderfall system framing.

## Discovery Readiness

This brief is considered ready.

The overall product problem is framed clearly enough for:

- engine-level behavior to remain grounded
- subsystem discovery briefs to stay scoped
- design work to proceed on continuity and document maintenance without inventing the top-level system problem
