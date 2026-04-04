---
title: Stage Artifact Runtime Interface
doc_type: design
status: ready
updated: 2026-04-03
summary: Defines the shared artifact-level runtime interface beneath stage-specific Discovery and Design services for authoritative reads, checkpoint writes, status-aware transitions, and explicit artifact deletion.
---

# Stage Artifact Runtime Interface

## Purpose

This document defines the shared artifact-level runtime interface that should sit beneath stage-specific services such as Discovery and Design.

The goal is to make the common runtime layer explicit so Discovery and Design do not each grow their own hidden artifact service contract with slightly different semantics.

## Design Position

Clauderfall should have a shared stage-artifact runtime interface below stage-specific services and above raw persistence primitives.

This layer should own the cross-stage artifact operations that are genuinely the same for readable stage artifacts:

- authoritative reads
- checkpoint writes
- current-checkpoint resolution
- status-aware checkpoint transitions
- explicit destructive artifact deletion
- structured operation results

It should not own stage policy.

It should provide reusable artifact mechanics that stage-specific services compose into Discovery, Design, and later stage workflows.

## Why This Layer Should Exist

The shared runtime substrate already defines common capabilities such as persistence primitives, checkpoint resolution, and operation runners.

The Discovery and Design runtime docs now define stage-specific MCP surfaces on top.

Without an explicit artifact-level layer between those two, the repo still has an important unnamed design gap:

- Discovery and Design both need `read` semantics
- Discovery and Design both need checkpoint-write semantics
- Discovery and Design both need status persisted as checkpointed artifact state
- Discovery and Design both need deterministic transitions that create later checkpoints for the same artifact identity

Those are not raw persistence details anymore, but they are also not unique stage-policy decisions.

They belong in a shared artifact runtime interface.

## Intended Layering

The recommended layering is:

1. persistence primitives and checkpoint storage
2. shared stage-artifact runtime interface
3. stage-specific services such as Discovery and Design
4. MCP handlers
5. LLM interview logic

This keeps the boundaries clean:

- persistence stays generic
- artifact mechanics stay shared
- stage policy stays stage-specific

## Shared Responsibilities

The shared stage-artifact runtime interface should own:

- resolving an artifact identity to its current checkpoint
- reading an artifact in short or full view
- writing a new checkpoint for an existing artifact identity
- persisting workflow status and readiness fields as checkpointed artifact state
- applying deterministic status transitions that produce a new current checkpoint
- deleting an artifact's persisted runtime state when explicitly requested
- returning structured operation results with references and metadata

These are common artifact-runtime concerns.

They should not be re-specified independently in every stage service.

## What Stays Out Of This Layer

This layer should not decide:

- whether a Discovery brief is good enough to move to Design
- when a Design unit should be reviewed or accepted
- whether session lifecycle should rebuild an index or archive a thread

Those are stage-policy questions.

The stage-artifact runtime interface should make those decisions executable once a stage service has already decided what should happen.

## Shared Operations

The shared artifact runtime layer should provide reusable operations shaped roughly like:

- `read_artifact`
- `write_artifact_checkpoint`
- `transition_artifact_status`
- `delete_artifact`

These are backend interface concepts, not necessarily final MCP tool names.

Stage-specific services should wrap them in stage-shaped operations such as:

- Discovery `read`
- Discovery `write_draft`
- Discovery `to_design`
- Design `read`
- Design `write_draft`
- Design `accept`
- Discovery `delete`
- Design `delete`

## 1. `read_artifact`

## Purpose

Return authoritative persisted state for one artifact identity.

## Design Position

`read_artifact` should support:

- current checkpoint lookup by default
- optional specific checkpoint lookup
- short view
- full view

The short view should return a compact header-level representation suitable for fast orientation.

The full view should return the readable artifact body plus the same structured metadata.

The exact fields may vary by artifact type, but the shared expectation should be consistent:

- artifact identity
- title when present
- current or requested checkpoint reference
- workflow status
- readiness fields when the artifact type uses them

## 2. `write_artifact_checkpoint`

## Purpose

Persist a new immutable checkpoint for an existing artifact identity.

## Design Position

`write_artifact_checkpoint` should:

- accept the full readable artifact body
- accept the full structured sidecar state for that checkpoint
- create a new immutable checkpoint
- update the current checkpoint pointer on success
- return the new checkpoint reference and any warnings

This operation should not interpret stage-policy meaning beyond enforcing basic structural validity.

For example, it may verify that required fields for that artifact type are present, but it should not decide whether a Discovery brief should move to Design or whether a Design unit deserves acceptance.

## 3. `transition_artifact_status`

## Purpose

Persist a workflow status transition for an artifact by writing a new checkpoint with updated status-bearing sidecar state.

## Design Position

`transition_artifact_status` should exist because status changes are not merely in-memory flags.

They are checkpointed artifact state and should therefore produce a new current checkpoint for the same artifact identity.

This operation should:

- resolve the current artifact checkpoint
- apply the requested status change
- optionally apply other explicitly supplied sidecar-field changes such as readiness rationale updates
- create a new immutable checkpoint
- return structured confirmation of the transition

This operation still should not decide whether the requested transition is desirable.

## 4. `delete_artifact`

## Purpose

Remove one artifact's authoritative persisted state when the operator explicitly wants that artifact deleted.

## Design Position

`delete_artifact` should:

- remove the current artifact record
- remove all persisted checkpoints for that artifact
- remove current and checkpoint Markdown files for that artifact
- return a structured result describing whether any state was deleted

This operation is intentionally destructive and should not be part of ordinary drafting flow.

The stage-specific service should decide that.

The shared runtime should only make the transition deterministic and durable.

## Relationship To Reopening

Reopening an artifact should not require a special shared runtime verb.

Reopening is just another checkpoint write or status transition on the same artifact identity.

That matches the checkpoint model in [artifact_checkpoint_semantics.md](/home/maddie/repos/clauderfall/docs/design/artifact_checkpoint_semantics.md), where reopening accepted work produces a later checkpoint rather than a new artifact identity.

## Structured Result Shape

The shared artifact runtime interface should standardize a result shape that stage-specific services can reuse:

- `result`
- `warnings`
- `artifacts`
- `metadata`

This keeps backend and MCP behavior consistent even when stage-level operations differ.

## Relationship To Existing Docs

This document sits between:

- [shared_stage_runtime_substrate.md](/home/maddie/repos/clauderfall/docs/design/shared_stage_runtime_substrate.md)
- [discovery_runtime_mcp_interface.md](/home/maddie/repos/clauderfall/docs/design/discovery_runtime_mcp_interface.md)
- [design_runtime_mcp_interface.md](/home/maddie/repos/clauderfall/docs/design/design_runtime_mcp_interface.md)

It also depends on:

- [artifact_persistence_format.md](/home/maddie/repos/clauderfall/docs/design/artifact_persistence_format.md)
- [artifact_checkpoint_semantics.md](/home/maddie/repos/clauderfall/docs/design/artifact_checkpoint_semantics.md)
- [artifact_checkpoint_metadata.md](/home/maddie/repos/clauderfall/docs/design/artifact_checkpoint_metadata.md)

## Tradeoffs

- Adding this layer introduces another named abstraction, but it removes a more dangerous problem: duplicated artifact-runtime semantics hidden inside multiple stage services.
- Keeping the layer artifact-focused rather than stage-focused makes it reusable, but it also means some operations stay abstract until wrapped by a stage service.
- A shared status-transition helper improves consistency, but it requires care to avoid letting shared code silently absorb stage-policy decisions.

## Readiness

Readiness: high

Rationale: Discovery and Design now both rely on the same underlying artifact runtime concepts, and this document makes that dependency explicit without collapsing stage-specific workflow semantics into one generic service.
