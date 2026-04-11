---
status: ready
last_updated: 2026-04-11
---

# Document Maintenance Discovery Brief

## Overview

Clauderfall may need a document maintenance skill that keeps the active documentation set coherent as the product evolves.

The problem is not only writing or editing docs. It is maintaining the structure and truth of the docs set over time so active documents do not drift, overlap, accumulate stale framing, or retain transitional naming after their role has changed.

This brief is limited to the canonical docs set under `docs/`.

## Problem Area: Docs Drift

### Problem Statement

Active docs can drift structurally as the project evolves.

Multiple docs may start covering the same ground, transitional document names may linger after the role hardens, indexes may become inaccurate, backward-looking narrative may remain in active artifacts even when it no longer helps current work, and speculative future-state placeholders may linger without affecting any current decision.

The result is a docs set that becomes harder to trust, harder to navigate, and harder to maintain as current truth.

### Intended Outcomes

- The docs set should stay minimal, current, and internally consistent.
- Each active document should have a clear role that is distinct from nearby docs.
- Transitional names, duplicated framing, and stale narrative should be cleaned up instead of lingering.
- Speculative future placeholders that do not affect current work should be removed from active docs rather than carried forward.
- Indexes should stay accurate as docs are renamed, split, merged, narrowed, or deleted.
- The skill should maintain both document structure and document content.

### Constraints

- The skill should stay focused on markdown docs under `docs/`.
- The skill should optimize for active truth rather than historical narration.
- The skill should work from readable markdown artifacts and visible indexes.
- The skill should preserve concise, reviewable docs rather than expanding them into low-signal explanation.
- The skill should be operator-invoked rather than always-on.
- The skill should remove vague future-thinking language from active docs unless it is a real current open question.

### Assumptions

- Document maintenance is a recurring workflow, not one-off cleanup.
- Structural maintenance and content maintenance are tightly coupled enough to belong in one skill.
- The skill may need to inspect several neighboring docs before deciding whether the problem is prose-level or structure-level.
- Other skills may detect meaningful overlap or drift and recommend invoking this skill.

### Risks And Edge Cases

- If the skill tries to do both structure and content work without a clear contract, it may become an unfocused "fix the docs" assistant.
- If it edits content without respecting document role boundaries, it may blur the docs set instead of improving it.
- If it only flags issues and does not reshape the docs set, sprawl will continue.
- If it becomes too aggressive about merge or delete actions, it may collapse distinctions that still matter.

## Scope Boundary

In scope:

- active markdown docs under `docs/`
- docs indexes
- document role clarity
- content cleanup for consistency and current-truth alignment

Out of scope:

- instruction files such as `AGENTS.md`, `CLAUDE.md`, and `SKILL.md`
- markdown artifacts outside `docs/`
- general repository maintenance

## Trigger Model

The skill should be operator-invoked.

Other skills may recommend invoking it when they detect significant overlap, drift, stale framing, or unclear document boundaries.

It should not operate as an automatic background process.

## Output Contract

The skill should edit directly when the needed changes are obvious and low-risk.

When the maintenance action is broader, structurally meaningful, or ambiguous, it should first produce a compact proposal.

That proposal should focus on the specific role or structure changes being considered rather than narrating every obvious edit.

## Anti-Goals

- The skill should not become a general-purpose repo cleanup tool.
- The skill should not maintain instruction artifacts outside the docs set.
- The skill should not preserve stale or backward-looking narrative in active docs when it no longer serves current truth.
- The skill should not preserve `maybe later`, `deferred`, or similar speculative future notes inside canonical docs when they are not part of the current problem.
- The skill should not spend tokens on unnecessary planning for straightforward cleanup.

## Discovery Readiness

This brief is considered ready for Design.

The framing is coherent enough for design work to define:

- the document maintenance skill contract
- the trigger and recommendation model
- the proposal-versus-direct-edit rule
- the maintenance operations over docs structure and content
