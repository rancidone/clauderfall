---
title: Session Continuity Skill Surface
doc_type: design
status: ready
updated: 2026-04-02
summary: Defines the packaged skill surface for startup orientation and handoff persistence over the session lifecycle MCP interface.
---

# Session Continuity Skill Surface

## Purpose

This document defines the skill-facing surface for recent session continuity in Clauderfall.

The goal is to make session startup and session handoff easy to invoke conversationally without pushing operators toward raw MCP tool calls or overloading one skill with conflicting responsibilities.

This document focuses on:

- packaged skill boundaries
- skill-to-MCP mapping
- operator-facing interaction shape
- thread-identity handling for handoff

It does not redefine the underlying lifecycle runtime or MCP behavior already covered elsewhere.

## Design Position

Clauderfall should expose two packaged session continuity skills:

- `session_continue`
- `session_handoff`

These should sit above the existing session lifecycle MCP surface:

- `session_read_startup_view`
- `session_read_thread`
- `session_write_handoff`
- `session_archive_thread`

The skill layer should make the lifecycle flow easier to invoke and easier to reason about, but it should not create a second persistence or lifecycle policy layer outside the runtime.

## Why Two Skills

Startup orientation and handoff persistence are adjacent behaviors, but they are not the same job.

`session_continue` is about:

- orienting from recent state
- inspecting active threads
- deliberately choosing whether to continue prior work

`session_handoff` is about:

- capturing carry-forward state
- writing an active-thread checkpoint
- optionally archiving completed work

Collapsing those into one skill would create avoidable confusion:

- startup orientation would carry write-focused prompt baggage
- handoff would inherit thread-selection and startup presentation behavior it does not need
- operators would have to infer whether "session" means read, write, or archive

Two small skills are clearer than one overloaded one.

## Naming Position

The primary packaged startup skill should be named `session_continue`.

That name is shorter and easier to type than a more descriptive phrase such as `session_startup_orientation` while still matching the actual operator intent in most cases.

The write-focused skill should be named `session_handoff` because the underlying job is to persist continuation state for later work.

These names should remain skill-level names.

The MCP layer should keep the explicit lifecycle operation names:

- `session_read_startup_view`
- `session_read_thread`
- `session_write_handoff`
- `session_archive_thread`

The skill surface should be convenient.
The MCP surface should stay explicit.

## Shared Skill Contract

Both session continuity skills should follow the shared skill/MCP contract already used elsewhere in Clauderfall:

- skills own conversation control, summarization, and judgment
- MCP owns authoritative reads, writes, and archive transitions
- skills must treat MCP results as authoritative
- skills must not imply persistence or lifecycle change unless the corresponding MCP call succeeded

These skills should not revert to raw file editing or prompt-only continuity state.

## `session_continue`

## Purpose

`session_continue` should be the startup and continuity-orientation skill.

Its job is to help the operator answer:

- what active work exists
- whether any of it should be resumed
- which thread should be drilled into for full context

## Responsibilities

`session_continue` should:

- call `session_read_startup_view` when authoritative recent state is needed
- present active threads compactly
- keep startup orientation separate from thread commitment
- call `session_read_thread` only after the operator chooses a thread or continuation intent is otherwise unambiguous
- preserve the valid "start something new" path even when active threads exist

`session_continue` should not:

- write handoff state as part of ordinary startup orientation
- archive threads as part of ordinary startup orientation
- auto-resume the newest thread without making that choice visible
- silently attach new work to an existing active thread

## Interaction Shape

The default `session_continue` flow should be:

1. read the compact startup view
2. show active threads ordered by `updated_at` descending
3. let the operator choose one thread, inspect one thread without committing, or start something new
4. load full thread detail only after drill-in

If exactly one active thread exists and the operator explicitly asks to continue prior work, the skill may read that thread directly, but it should still state which thread it selected and why.

## `session_handoff`

## Purpose

`session_handoff` should be the persistence-focused continuity skill.

Its job is to help the operator turn the current working state into a durable active-thread handoff that another session can resume safely.

## Responsibilities

`session_handoff` should:

- decide whether the target is an existing active thread or a new one
- produce the handoff payload needed by `session_write_handoff`
- make the chosen thread identity visible before or when writing
- keep the persisted handoff compact and continuation-focused
- use `session_archive_thread` only when the operator explicitly wants the thread completed

`session_handoff` should not:

- assume archive on every handoff
- treat visible prose alone as saved continuity state
- overwrite an existing thread blindly when thread identity is unclear

## Required Persisted Content

The skill should produce and persist:

- `thread_id`
- `title`
- `current_intent_summary`
- `next_suggested_action`
- `thread_markdown`

The handoff should optimize for continuation safety rather than completeness.

That means:

- title should identify the workstream
- current intent summary should explain what is in motion now
- next suggested action should say what the next session should do first
- thread markdown should carry only the readable context needed to resume safely

## Thread Identity Policy

The current MCP/runtime surface requires `thread_id` on `session_write_handoff` and does not expose a separate `session_create_thread` operation.

That means the skill layer needs an explicit thread-identity policy.

For the first skill slice, `session_handoff` should follow this rule set:

1. if the operator has already selected an active thread, reuse that exact `thread_id`
2. if startup view shows a clearly matching active thread, reuse that `thread_id`
3. if the handoff is clearly for new work, derive a kebab-case `thread_id` from the chosen title
4. if the derived id conflicts with a different active thread title, append a numeric suffix

This is acceptable for the first continuity skill slice because:

- the underlying runtime already treats thread writes as upserts by `thread_id`
- active thread count is expected to stay small
- the skill can make the chosen identity visible before persistence

This is not the ideal long-term identity model.

A later lifecycle extension may still add:

- `session_create_thread`
- richer list/query operations
- stronger duplicate-resolution behavior

But those are not required to make the first packaged continuity skills coherent.

## Skill-To-MCP Mapping

The expected mapping should be:

### `session_continue`

- startup orientation -> `session_read_startup_view`
- drill into active thread -> `session_read_thread`

### `session_handoff`

- resolve current active thread context when needed -> `session_read_startup_view`
- inspect one active thread before overwriting -> `session_read_thread`
- persist carry-forward state -> `session_write_handoff`
- complete and close a thread -> `session_archive_thread`

The skill names should not become aliases for MCP operations one-to-one.

They are interaction surfaces, not transport surfaces.

## Out Of Scope For This Slice

This skill design does not try to solve the entire thread-management problem.

It does not add:

- filtering or search over active threads
- bulk cleanup operations
- archived-thread reopen behavior
- explicit recent-history inspection beyond what startup already returns
- a separate create-thread API

Those may deserve later design work, but they should not block the first usable continuity skill surface.

## Constraints

This design should preserve the existing session-lifecycle constraints:

- startup remains compact by default
- continuation stays operator-directed rather than automatic
- handoff remains a single authoritative thread write
- skill prompts do not become a second persistence layer
- archive remains explicit

## Tradeoffs

## Benefits

- session continuity becomes easier to invoke than raw tool names
- startup orientation and handoff persistence get clearer boundaries
- `session_continue` matches the operator's likely language at startup
- the first skill slice works with the current MCP surface without reopening runtime work immediately

## Costs

- the skill layer has to carry a temporary thread-id derivation policy
- thread management remains intentionally minimal beyond startup and handoff
- some future cleanup or search workflows still need more lifecycle design work

## Readiness

Readiness: high

Rationale:

The first packaged session continuity surface is now concrete:

- two skills rather than one overloaded session skill
- explicit mapping to the current lifecycle MCP interface
- startup orientation and handoff have separate responsibilities
- thread-identity handling is defined well enough for implementation
- richer lifecycle management remains explicitly out of scope rather than implicit

## Relationship To Other Docs

This document depends on:

- `skill_mcp_interaction_contract.md`
- `session_lifecycle_mcp_interface.md`
- `session_start_drill_in_flow.md`
- `session_handoff_write_update_flow.md`

It provides the skill-layer design that was previously missing from the session lifecycle work.
