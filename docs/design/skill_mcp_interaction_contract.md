---
title: Skill MCP Interaction Contract
doc_type: design
status: ready
updated: 2026-03-27
summary: Defines how Clauderfall stage skills should interact with MCP as the reasoning layer over deterministic runtime operations.
---

# Skill MCP Interaction Contract

## Purpose

This document defines how Clauderfall skills should interact with MCP.

The goal is to make the skill-side contract explicit so Discovery and Design prompts do not drift back toward file-edit behavior, implicit state transitions, or prompt-only persistence discipline.

This document focuses on:

- what the skill owns
- what MCP owns
- when the skill should call MCP
- how stage-specific skill surfaces map onto stage-specific MCP operations

It does not redefine the underlying runtime semantics already covered by the runtime and MCP interface docs.

## Design Position

Clauderfall skills should behave as the language and judgment layer over deterministic backend operations exposed through MCP.

Skills should:

- run the interview
- decide what question or revision is needed next
- draft and revise readable artifacts
- assess readiness and explain tradeoffs
- decide when persistence, review, acceptance, or transition should be attempted

Skills should not:

- directly mutate authoritative artifact files as the normal workflow path
- infer that a state transition happened without calling the corresponding MCP operation
- treat conversational intent as equivalent to persisted workflow state
- recreate backend invariants in prompt instructions

The normal architecture is:

1. skill reasons about the current stage state
2. skill calls a small explicit MCP operation
3. runtime performs the deterministic write or transition
4. skill continues from the returned authoritative result

## Core Responsibility Split

## Skill Responsibilities

The skill owns:

- conversational control
- interviewing strategy
- synthesis and artifact prose
- readiness judgment
- tradeoff surfacing
- deciding when persistence or transition should be attempted

## MCP And Runtime Responsibilities

The MCP-facing runtime owns:

- authoritative reads
- checkpoint creation
- current-checkpoint updates
- persisted workflow status changes
- transition integrity
- structured success, warning, and failure results

The skill should supply the language-shaped content and judgment inputs.
The runtime should supply the authoritative persisted state change.

## General Interaction Rules

Skills should follow these rules across stages.

### 1. Read Before Assuming

When a skill needs authoritative current state, it should call the appropriate `*_read` tool rather than relying on conversational memory alone.

This is especially important:

- at session start
- after compaction or context loss
- before attempting a transition
- after any warning or failure result
- when current status or checkpoint is unclear

### 2. Persist Through Explicit Write Operations

When the skill has produced a material artifact revision that should become authoritative, it should call the stage's `*_write_draft` tool.

The write operation is the normal persistence path for evolving stage content.

The skill should not represent draft progress as safely persisted until that operation succeeds.

### 3. Use Transition Operations Explicitly

Workflow transitions should be attempted only through their named MCP operations.

That means:

- Discovery uses `discovery_to_design`
- Design uses `design_accept`

The skill should not describe those transitions as completed unless the MCP result confirms the persisted effect.

### 4. Separate Judgment From Enforcement

The skill may decide that a draft appears ready for review, acceptance, or handoff.

That does not itself change artifact state.

The skill should:

- make the judgment explicit in the conversation and artifact
- call the appropriate MCP operation when the operator wants the persisted state change
- treat the runtime as the authority on whether the mechanical transition actually succeeded

### 5. Treat MCP Results As Authoritative

Skills should treat MCP responses as the source of truth for:

- current checkpoint references
- persisted status
- artifact references
- whether a transition actually occurred
- whether warnings or failures need follow-up

If an MCP call returns `failure`, the skill should not continue as though the state change succeeded.

If an MCP call returns `warning`, the skill should surface the warning clearly and continue from the returned authoritative state.

## Shared Response Handling

The first MCP slice uses one shared top-level response shape:

- `result`
- `warnings`
- `artifacts`
- `metadata`

Skills should interpret those fields consistently.

### `result`

`result` tells the skill whether the operation ended in:

- `success`
- `warning`
- `failure`

### `warnings`

`warnings` should be surfaced to the operator when they affect confidence, continuity, or next-step safety.

Skills should not silently swallow warnings that indicate degraded state, override use, or partial recovery conditions.

### `artifacts`

`artifacts` contains the returned artifact references and any compact payloads explicitly included in the tool contract.

Skills should not assume that non-read operations return full document bodies.

### `metadata`

`metadata` contains operational fields such as:

- ids
- checkpoint ids
- status flags
- override indicators
- compact transition facts

Skills should use this data to keep visible state and narrative claims aligned with the actual persisted result.

## Content Boundary

Skills should respect the returned-content boundary of the MCP surface.

- `*_read` tools may be used when the skill needs full readable artifact content
- short reads should be preferred when the skill only needs compact orientation metadata
- write and transition tools should not be used as a substitute for full artifact reads

This keeps the skill prompt disciplined about token use and avoids turning every write or transition into an implicit reread.

## Discovery Skill Surface

The Discovery skill should treat the Discovery MCP surface as:

- `discovery_read`
- `discovery_write_draft`
- `discovery_to_design`

### `discovery_read`

Use when the skill needs authoritative Discovery state.

Typical cases:

- recovering current brief state
- checking current checkpoint and status
- resuming after compaction
- verifying whether the brief is still `draft` or already `accepted`
- loading the full brief before revising it

### `discovery_write_draft`

Use when the skill has a revised Discovery brief and wants to persist it as the current authoritative checkpoint.

The skill should supply:

- revised readable brief content
- structured sidecar content
- the current intended workflow status
- readiness signal and rationale

The skill may use `discovery_write_draft` to persist either:

- `draft`
- `accepted`

But writing `accepted` does not itself move the session into Design.

### `discovery_to_design`

Use only when the operator wants the explicit Discovery-to-Design transition.

The Discovery skill should call this after Discovery has already:

- produced the current accepted brief state
- made readiness visible
- decided to move forward

The skill should not expect `discovery_to_design` to redo Discovery judgment.
It should expect that operation to enforce mechanical preconditions and either succeed, warn, or fail explicitly.

## Discovery Interaction Pattern

The normal Discovery pattern should be:

1. `discovery_read` when authoritative state is needed
2. interview and revise the visible brief
3. `discovery_write_draft` to persist the updated brief checkpoint
4. repeat until the brief is accepted
5. `discovery_to_design` when the operator chooses to hand off

## Design Skill Surface

The Design skill should treat the Design MCP surface as:

- `design_read`
- `design_write_draft`
- `design_accept`

### `design_read`

Use when the skill needs authoritative Design state.

Typical cases:

- recovering the current design unit
- checking checkpoint, status, and readiness state
- resuming after compaction
- loading the full design unit before revising it
- confirming whether the unit is `draft` or `accepted`

### `design_write_draft`

Use when the skill has a revised design unit draft to persist.

The skill should supply:

- either full revised readable design-unit content or a small markdown delta against the current checkpoint
- either full structured sidecar content or a metadata-only sidecar patch
- the current intended workflow status
- readiness signal and rationale

This is the normal persistence operation for Design drafting and revision.

For small iterative edits, prefer delta writes so token cost tracks the changed section or metadata field instead of the full unit length.
For small localized revisions, the skill should default to:

- `markdown_operations` for section-level document edits
- `sidecar_patch` for partial metadata updates

The skill should avoid resending the full markdown body or the full sidecar when only one section or a few metadata fields changed.

It may persist:

- `draft`

It should not be treated as artifact acceptance.

It is also the normal reopen path when a previously reviewed or accepted unit needs revision by writing a new checkpoint with `status: draft`.

### `design_accept`

Use when the operator wants to accept the current design artifact as the accepted record for the unit.

The skill should treat acceptance as an explicit workflow operation, not as something implied by high readiness or polished prose.

Acceptance records artifact status.
It does not automatically imply downstream build execution approval.

## Design Interaction Pattern

The normal Design pattern should be:

1. `design_read` when authoritative state is needed
2. interview and revise the visible design unit
3. `design_write_draft` to persist revised checkpoints during drafting
4. additional `design_write_draft` with `status: draft` if acceptance reveals needed revision
5. `design_accept` when the operator wants the accepted design record

## Skill Prompt Implications

Skill instructions should explicitly reinforce this boundary.

A stage skill prompt should say, in substance:

- keep the visible artifact in the conversation
- use MCP for authoritative reads, writes, and transitions
- for Clauderfall-managed artifacts, use MCP as the only write path
- do not directly edit the corresponding on-disk artifact files
- do not write session continuity state as an implicit side effect of stage drafting
- do not imply that status changed unless the corresponding MCP operation succeeded
- treat readiness as a judgment that may inform transitions, not as a transition by itself

## Recommended Skill-Surface Documentation Split

This contract is the shared rule set for all stage skills.

If Clauderfall wants more detailed skill-facing docs, the clean split is:

- one shared contract doc for all skills
- one Discovery skill-surface doc mapping Discovery interview behavior to `discovery_*` tools
- one Design skill-surface doc mapping Design interview behavior to `design_*` tools

That avoids repeating the shared architecture rules while still giving each stage a concrete skill-facing operational guide.

## References

- [stage_runtime_mcp_pattern.md](/home/maddie/repos/clauderfall/docs/design/stage_runtime_mcp_pattern.md)
- [shared_stage_runtime_substrate.md](/home/maddie/repos/clauderfall/docs/design/shared_stage_runtime_substrate.md)
- [mcp_adapter_surface.md](/home/maddie/repos/clauderfall/docs/design/mcp_adapter_surface.md)
- [discovery_runtime_mcp_interface.md](/home/maddie/repos/clauderfall/docs/design/discovery_runtime_mcp_interface.md)
- [design_runtime_mcp_interface.md](/home/maddie/repos/clauderfall/docs/design/design_runtime_mcp_interface.md)
