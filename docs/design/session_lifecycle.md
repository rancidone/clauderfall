---
title: Session Lifecycle Discovery Brief
doc_type: brief
status: ready
updated: 2026-03-27
summary: Discovery brief for a strict recent-session-state artifact and session lifecycle flow covering handoff and session start.
---

# Session Lifecycle Discovery Brief

## Overview

Clauderfall needs a persisted recent-session-state artifact that makes recent work legible without requiring broad re-exploration, while still allowing the operator to either continue prior work or deliberately start something new.

The problem is the lack of a strict, inspectable contract for what recent session state is preserved, what is intentionally omitted, and what a new session may assume.

A major goal is context management and token economy, not just continuity correctness.

## Problem Area: Recent Session Continuity

### Problem Statement

Recent session state is not captured in a strict enough form to support reliable handoff and startup.

Later sessions may need to rediscover recent work or may reconstruct context incorrectly from loose prose.

The artifact should cover broader recent state for the repo or working context, but it must stay bounded, must not carry transient or resolved material forward indefinitely, and must support parallel active work without forcing costly exploration.

### Intended Outcomes

- Recent work can be understood quickly from persisted session state.
- Handoff uses a strict format rather than heuristic recovery.
- Session start can continue prior work or intentionally begin a new direction after reviewing recent state.
- Session start may stop at orientation or proceed into a selected thread, but it must not force thread selection.
- The artifact captures broader recent context without becoming a huge memory file.
- Resolved or stale transient state is pruned from active carry-forward state.
- Historically useful resolved material can exist in a separate history layer without polluting active startup context.
- Parallel active work can be represented without forcing all handoffs into one linear archive.
- Session start should favor token-efficient orientation from a compact repo-level view before drilling into one thread.

### Constraints

- The primary artifact is persisted recent session state.
- The format must be strict enough that required state is explicit and machine-readable.
- Reading prior session state must not force continuation of the same topic.
- The artifact must remain bounded and reviewable rather than growing into general long-term memory.
- Transient state must be pruned or omitted once it is no longer decision-relevant.
- Resolved material should move to a separate history layer rather than remain active carry-forward state.
- The lifecycle must support parallel work without requiring heavy manual management of named workstreams.
- The lifecycle must cover both `handoff` and `start session`.
- Token economy is a primary constraint, not a nice-to-have.
- The default startup view should include only the last `N` closed threads or completed items rather than unbounded historical closure.

### Assumptions

- The main failure mode is ambiguity in state shape and semantics, not merely weak prompting.
- The artifact should preserve the most decision-relevant recent state, not exhaustive history.
- Bounded recency and pruning matter more than broad retention.
- A distinct boundary between active carry-forward state and history is necessary.
- A compact repo-level summary of active threads is a better startup default than forcing the operator to pick a thread up front.
- A capped `last N` view is an acceptable default for closed threads or completed work.
- `N` should be tunable, with a small default in the 4-5 range.

### Risks And Edge Cases

- The artifact may become a dumping ground unless there is a strict boundary on what qualifies as carry-forward state.
- A per-workstream model may preserve correctness but create operator overhead.
- A repo-level summary may reduce overhead but blur unrelated active efforts together.
- Resolved items may still be relevant if they encode decisions or constraints that should survive as compact background.
- Start-session may accidentally inherit stale assumptions if active versus historical state is not legible.
- A strict format may still fail if field meanings are vague.
- A `last N` cutoff may hide an older but still important completed thread unless history access is still easy.

## Accepted Startup-View Categories

- active threads
- closed threads or completed work
- current intent per thread in one sentence
- next suggested actions

## Discovery Readiness

This brief is considered ready for Design.

The problem framing is clear enough that Design can define:

- the persisted recent-session-state artifact contract
- the active-versus-history boundary
- the handoff flow
- the start-session flow

without inventing the problem statement or the key constraints.

That Design work is now represented by the current session-lifecycle cluster:

- `session_recent_state_artifact.md`
- `session_handoff_write_update_flow.md`
- `session_start_drill_in_flow.md`
- `session_archive_transition_mechanics.md`
- `session_lifecycle_runtime_interface.md`
