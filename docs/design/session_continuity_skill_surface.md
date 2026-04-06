---
title: Session Continuity Skill Surface
doc_type: design
status: ready
updated: 2026-04-05
summary: Defines the packaged skill surface for startup orientation and handoff persistence over the single-current session lifecycle MCP interface.
---

# Session Continuity Skill Surface

## Purpose

This document defines the skill-facing surface for recent session continuity in Clauderfall.

The goal is to make session startup and session handoff easy to invoke conversationally without pushing operators toward raw MCP tool calls or overloading one skill with conflicting responsibilities.

## Design Position

Clauderfall should expose two packaged session continuity skills:

- `session_continue`
- `session_handoff`

These should sit above the session lifecycle MCP surface:

- `session_read_startup_view`
- `session_read_current`
- `session_write_handoff`
- `session_archive_current`

The skill layer should make the lifecycle flow easier to invoke and easier to reason about, but it should not create a second persistence or lifecycle policy layer outside the runtime.

## Why Two Skills

Startup orientation and handoff persistence are adjacent behaviors, but they are not the same job.

`session_continue` is about:

- orienting from recent state
- inspecting current carry-forward context
- deliberately choosing whether to continue prior work

`session_handoff` is about:

- capturing carry-forward state
- writing the current continuity checkpoint
- optionally archiving completed work

Two small skills are clearer than one overloaded one.

## Shared Skill Contract

Both session continuity skills should follow the shared skill/MCP contract already used elsewhere in Clauderfall:

- skills own conversation control, summarization, and judgment
- MCP owns authoritative reads, writes, and archive transitions
- skills must treat MCP results as authoritative
- skills must not imply persistence or lifecycle change unless the corresponding MCP call succeeded

## `session_continue`

## Purpose

`session_continue` should be the startup and continuity-orientation skill.

Its job is to help the operator answer:

- whether current carry-forward state exists
- whether it should be resumed
- whether they should instead start something new

## Responsibilities

`session_continue` should:

- call `session_read_startup_view` when authoritative recent state is needed
- present current state compactly
- keep startup orientation separate from continuation
- call `session_read_current` only after the operator chooses to drill in or continuation intent is otherwise unambiguous
- preserve the valid "start something new" path even when current state exists

`session_continue` should not:

- write handoff state as part of ordinary startup orientation
- archive state as part of ordinary startup orientation
- auto-resume current work without making that choice visible
- silently attach new work to existing continuity state

## Interaction Shape

The default `session_continue` flow should be:

1. read the compact startup view
2. show current state plus recent completed items
3. let the operator choose to inspect current state, continue it, or start something new
4. load full current detail only after drill-in

If current state exists and the operator explicitly asks to continue prior work, the skill may read it directly, but it should still state that choice.

## `session_handoff`

## Purpose

`session_handoff` should be the persistence-focused continuity skill.

Its job is to help the operator turn the current working state into a durable current carry-forward record that another session can resume safely.

## Responsibilities

`session_handoff` should:

- produce the payload needed by `session_write_handoff`
- make replacement or overwrite implications visible before or when writing
- keep the persisted handoff compact and continuation-focused
- use `session_archive_current` only when the operator explicitly wants the current work completed

`session_handoff` should not:

- assume archive on every handoff
- treat visible prose alone as saved continuity state
- overwrite existing current state blindly when the workstream changed materially

## Required Persisted Content

The skill should produce and persist:

- `title`
- `work_items`
- `thread_markdown`

The handoff should optimize for continuation safety rather than completeness.

That means:

- title should identify the current workstream
- work items should be the ordered next actions the next session should pick up
- thread markdown should carry only the readable context needed to execute those items safely

## Current-State Replacement Policy

The current MCP/runtime surface does not model multiple active threads.

That means the skill layer needs an explicit replacement policy.

For the first skill slice, `session_handoff` should follow this rule set:

1. if the current work is a continuation of the existing current record, update it in place
2. if the current work is materially different and the old record should be preserved, archive the old record first
3. if the operator intends to replace the old current state without preserving it as completed work, make that overwrite explicit before writing

## Skill-To-MCP Mapping

The expected mapping should be:

### `session_continue`

- startup orientation -> `session_read_startup_view`
- drill into current state -> `session_read_current`

### `session_handoff`

- inspect current state before replacing when needed -> `session_read_current`
- persist carry-forward state -> `session_write_handoff`
- complete and close current state -> `session_archive_current`

## Constraints

This design should preserve the existing session-lifecycle constraints:

- startup remains compact by default
- continuation stays operator-directed rather than automatic
- handoff remains a single authoritative current-state write
- skill prompts do not become a second persistence layer
- archive remains explicit

## Tradeoffs

## Benefits

- session continuity becomes easier to invoke than raw tool names
- startup orientation and handoff persistence get clearer boundaries
- the model no longer needs thread-identity policy
- the first skill slice matches the simplified lifecycle surface

## Costs

- replacing current state needs explicit operator-visible handling
- history reuse still needs a deliberate reopen or replacement workflow later if product wants it

## Readiness

Readiness: high

Rationale:

The skill split remains sound and the simplified lifecycle model removes the previous highest-friction ambiguity:

- no active-thread selection logic
- no thread-id derivation policy
- no hidden question about whether new work should create or reuse a parallel active thread
