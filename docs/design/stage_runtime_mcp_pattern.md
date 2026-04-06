---
title: Stage Runtime MCP Pattern
doc_type: design
status: ready
updated: 2026-03-27
summary: Defines the shared architecture pattern of LLM-driven stage work over deterministic backend services exposed through MCP.
---

# Stage Runtime MCP Pattern

## Purpose

This document defines the shared runtime pattern Clauderfall should use across Discovery, Design, session lifecycle, and later stage work such as TODO or implementation preparation.

The goal is to make the architecture shift explicit:

- the LLM should own interview logic, synthesis, and readable artifact content
- deterministic backend services should own persisted state transitions and invariants
- MCP should be the narrow operational contract between them

## Design Position

Clauderfall should not treat stage behavior as "skills that edit files" as the primary product architecture.

That is the exact failure mode this design work is trying to solve.

The preferred architecture is:

- LLM front end for conversation, judgment, and artifact drafting
- one shared stateful runtime substrate, including a reusable artifact-runtime layer for readable stage artifacts
- MCP tools exposing a small set of explicit stage-shaped operations

This pattern should be shared across stages rather than invented separately for each subsystem.

Clauderfall should prefer one runtime substrate across Discovery, Design, session lifecycle, and future TODO or implementation-preparation work.

## Why This Pattern

Prompt-only workflows break down when the product needs more than good prose.

Clauderfall already needs deterministic handling for things like:

- checkpoint creation
- status and readiness transitions
- stage handoff and continuity
- projection rebuild and validation
- archive and recovery behavior

Those are product-state problems, not just prompting problems.

If Clauderfall leaves them inside open-ended document editing skills, the system will drift into:

- inconsistent state transitions
- duplicated lifecycle logic
- weak recovery behavior
- prompt-dependent correctness

## Core Split

The shared stage-runtime split should be:

## LLM Front End

The LLM front end should own:

- interview strategy
- question selection
- synthesis and summary writing
- readable artifact drafting and revision
- recommendations about readiness or next moves

The LLM should not own:

- multi-artifact synchronization
- checkpoint enforcement
- authoritative workflow-state transitions
- invariant enforcement or recovery logic

## Shared Runtime Substrate

The shared runtime substrate should own:

- reading and writing authoritative artifact state
- checkpoint creation
- deterministic transitions for workflow or lifecycle state
- verification and recovery
- structured result objects for stage operations

For readable stage artifacts such as Discovery briefs and Design units, those shared artifact mechanics should normally be exposed to stage-specific services through a shared artifact-runtime layer rather than duplicated per stage.

Each stage may still have its own higher-level service surface, but those services should sit on top of one shared runtime substrate rather than separate per-stage runtimes.

## MCP Boundary

MCP should expose a small set of explicit operations that match the stage's real product actions.

Examples:

- Discovery operations to read, write, checkpoint, and transition a Discovery brief
- Design operations to read, update, review, and accept design units
- Session lifecycle operations to hand off, orient startup, rebuild projections, and archive threads
- future TODO operations to create, update, and transition implementation work artifacts

MCP should not default to raw file mutation when the product really needs deterministic state transitions.

## Shared Product Consequences

This pattern implies several product-level consequences:

- skills remain important, but they become the language and reasoning layer, not the persistence layer
- stage state should be enforced by backend services rather than conversational habit
- stage transitions should be explicit operations
- readable artifacts remain primary for humans, but not as the only source of truth for operational state

This is the main architecture shift that the recent session-lifecycle work made visible.

## Applicability By Stage

## Discovery

Discovery should use this pattern for:

- working-brief persistence
- checkpoint creation
- readiness and transition handling
- Design Start Context generation

## Design

Design should use this pattern for:

- design-unit persistence
- deterministic status and readiness transitions
- review and acceptance workflow
- decomposition-related artifact updates

## Session Lifecycle

Session lifecycle should use this pattern for:

- current-state handoff
- startup orientation and projection rebuild
- archive transition behavior

## Future TODO Or Implementation-Prep Stage

A future TODO or implementation-preparation stage should use this same pattern rather than reverting to LLM-maintained task documents.

That stage would likely need:

- readable implementation-work artifacts
- backend state transitions
- MCP operations for updating and transitioning those artifacts

## Relationship To Existing Docs

This document is the shared architecture pattern above the more specific runtime work.

More concrete lifecycle-specific docs include:

- `session_lifecycle_runtime_interface.md`
- `session_lifecycle_mcp_interface.md`
- `session_lifecycle_backend_service.md`
- `session_lifecycle_operation_runner.md`

The same pattern is now made concrete for Discovery and Design runtime operations in:

- `stage_artifact_runtime_interface.md`
- `discovery_runtime_mcp_interface.md`
- `design_runtime_mcp_interface.md`

## Constraints

This pattern should preserve Clauderfall's core product promises:

- interactive, operator-visible work
- readable artifacts
- deterministic state handling where correctness matters
- minimal prompt dependence for product invariants
- ability to extend into later stages without changing architectural direction

## Tradeoffs

## Benefits

- one consistent architecture across stages
- clearer separation between reasoning and state management
- stronger invariants and easier testing
- future stage expansion becomes easier to reason about

## Costs

- Clauderfall needs more backend structure than a pure prompting tool
- stage interfaces need explicit schema design
- some flexibility is traded for consistency and recoverability

## Readiness

Readiness: high

Rationale:

The architecture shift is now explicit and coherent:

- LLM front end
- one shared deterministic runtime substrate
- MCP operational boundary

Stage-specific behavior may still differ, but the underlying runtime direction is now settled.
