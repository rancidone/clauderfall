---
title: Session Lifecycle Discovery Brief
doc_type: brief
status: ready
updated: 2026-04-05
summary: Discovery brief for a strict recent-session-state artifact and session lifecycle flow covering one current carry-forward record, startup, and archive.
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

The artifact should stay bounded, should not carry transient or resolved material forward indefinitely, and should avoid the overhead and ambiguity of multiple simultaneously active carry-forward threads.

### Intended Outcomes

- Recent work can be understood quickly from persisted session state.
- Handoff uses a strict format rather than heuristic recovery.
- Session start can continue the one current carry-forward record or intentionally begin a new direction.
- Session start may stop at orientation or proceed into the selected current record, but it must not force continuation.
- The artifact captures broader recent context without becoming a huge memory file.
- Resolved or stale transient state is pruned from current carry-forward state.
- Historically useful resolved material can exist in a separate history layer without polluting active startup context.
- The lifecycle stays simple by allowing at most one current carry-forward record at a time.
- Session start should favor token-efficient orientation from a compact repo-level view before loading the full current note.

### Constraints

- The primary artifact is persisted recent session state.
- The format must be strict enough that required state is explicit and machine-readable.
- Reading prior session state must not force continuation of the same topic.
- The artifact must remain bounded and reviewable rather than growing into general long-term memory.
- Transient state must be pruned or omitted once it is no longer decision-relevant.
- Resolved material should move to a separate history layer rather than remain in current carry-forward state.
- The lifecycle must not require manual management of multiple named active workstreams.
- The lifecycle must cover both `handoff` and `start session`.
- Token economy is a primary constraint, not a nice-to-have.
- The default startup view should include only the last `N` completed items rather than unbounded historical closure.

### Assumptions

- The main failure mode is ambiguity in state shape and semantics, not merely weak prompting.
- The artifact should preserve the most decision-relevant recent state, not exhaustive history.
- Bounded recency and pruning matter more than broad retention.
- A distinct boundary between current carry-forward state and history is necessary.
- One current carry-forward record is a better default than a small set of parallel active threads.
- A compact repo-level summary of the current record is a better startup default than forcing the operator to load the full note up front.
- A capped `last N` view is an acceptable default for completed work.
- `N` should be tunable, with a small default in the 4-5 range.

### Risks And Edge Cases

- The artifact may become a dumping ground unless there is a strict boundary on what qualifies as carry-forward state.
- Replacing the current record with unrelated work may accidentally discard useful context unless overwrite behavior is explicit.
- A repo-level summary may still blur important nuance if the current readable note is too compressed.
- Resolved items may still be relevant if they encode decisions or constraints that should survive as compact background.
- Start-session may accidentally inherit stale assumptions if current versus historical state is not legible.
- A strict format may still fail if field meanings are vague.
- A `last N` cutoff may hide an older but still important completed item unless history access is still easy.

## Accepted Startup-View Categories

- current carry-forward state
- closed threads or completed work
- current intent in one sentence
- next suggested actions

## Discovery Readiness

This brief is considered ready for Design.

The problem framing is clear enough that Design can define:

- the persisted recent-session-state artifact contract
- the current-versus-history boundary
- the handoff flow
- the start-session flow

without inventing the problem statement or the key constraints.

That Design work is now represented by the current session-lifecycle cluster:

- `session_recent_state_artifact.md`
- `session_handoff_write_update_flow.md`
- `session_start_drill_in_flow.md`
- `session_archive_transition_mechanics.md`
- `session_lifecycle_runtime_interface.md`
