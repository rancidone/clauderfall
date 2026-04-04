---
title: Design Runtime MCP Interface
doc_type: design
status: ready
updated: 2026-04-03
summary: Defines the Design runtime and MCP-facing operation set for reading the current unit, checkpointing draft progress through full or delta writes, accepting the current design record, and explicitly deleting obsolete units.
---

# Design Runtime MCP Interface

## Purpose

This document defines the concrete runtime and MCP-facing operation set for Design.

The goal is to make the shared stage-runtime pattern actionable for Design while preserving the Design-specific acceptance workflow and readiness signaling already established elsewhere in the docs.

## Design Position

Design should expose a small high-level operation set:

- `read`
- `write_draft`
- `accept`
- `delete`

## Why This Boundary

The Design engine should own:

- design interviewing
- design judgment
- visible drafting and revision
- readiness assessment
- recommendations about when to accept a unit

The runtime should own:

- authoritative artifact reads
- checkpoint creation and current-checkpoint updates
- persistence of the readable design unit and its structured sidecar
- deterministic status transitions for the current design unit
- structured acceptance results and artifact linkage

Without this boundary, Design would still rely on prompt discipline for artifact status transitions and acceptance correctness.

## Relationship To Existing Design Workflow

The Design workflow keeps readiness separate from artifact status.

This runtime interface should preserve that model rather than replacing it.

The MCP surface should therefore support:

- reading the current unit
- writing draft checkpoints
- explicitly accepting the current design record

## Operation Set

The initial Design runtime/MCP surface should expose exactly these operations:

- `read`
- `write_draft`
- `accept`
- `delete`

These names should follow the shared vocabulary in [stage_runtime_operation_vocabulary.md](/home/maddie/repos/clauderfall/docs/design/stage_runtime_operation_vocabulary.md) while still staying stage-shaped.

## 1. `read`

## Purpose

Return the authoritative current Design unit state for the active unit.

## What `read` Should Return

`read` should support a short form and a full form.

The short form should return the minimum structured metadata needed for the LLM to continue the Design interview safely without loading the full unit body.

The full form should return the readable design document plus the same structured metadata.

The short form should include at least:

- artifact identity
- title
- current checkpoint reference
- workflow status
- readiness signal
- readiness rationale
- scope summary
- parent/child/dependency references when present

`read` is the recovery and orientation operation for Design sessions.

## 2. `write_draft`

## Purpose

Persist a new Design unit checkpoint while keeping the artifact in its current non-terminal workflow state.

## Design Position

`write_draft` should be the normal persistence operation during Design interviewing and revision.

It should:

- accept either a full revised readable design unit body or a checkpoint-relative markdown delta
- accept either a full structured sidecar or a metadata-only sidecar patch
- create a new checkpoint for the same artifact identity
- update the current checkpoint pointer deterministically
- persist the current workflow status
- persist the current readiness signal
- persist the current readiness rationale
- return structured confirmation of the new authoritative checkpoint

`write_draft` should persist the normal mutable Design workflow state:

- `draft`

`write_draft` should not itself perform acceptance.

Acceptance is an explicit review decision, not a normal drafting checkpoint.

## Delta-Friendly Write Contract

To keep iterative drafting cheap, `write_draft` should support two equivalent write shapes:

- full replacement writes with complete `markdown` and complete `sidecar`
- delta writes with one or both of:
  - section-aware markdown operations against the current checkpoint
  - metadata-only sidecar patches for fields such as readiness, rationale, or open questions

Delta writes should still resolve to one complete new checkpoint internally.

The token cost at the MCP boundary should scale with what changed, not with the total current unit size.

### Checkpoint-Relative Guard

When the caller supplies a base checkpoint reference, the runtime should reject the delta write if that reference is stale relative to the current authoritative checkpoint.

This keeps incremental writes from silently applying against outdated state.

## Important Constraint

The runtime should preserve the separation between:

- saving revised design content
- rating design readiness
- accepting the design artifact

The LLM may recommend any of those moves, but `write_draft` should only persist the artifact and its current judgment.
## 3. `accept`

## Purpose

Accept the current Design artifact as the operator-approved design record for this unit.

## Design Position

`accept` should be explicit.

## 4. `delete`

## Purpose

Delete a Design unit and all of its persisted runtime state when the operator explicitly wants it removed.

## Design Position

`delete` should be reserved for cleanup of superseded or mistaken units.

It should not be used as a substitute for acceptance, reopening, or decomposition.

`delete` should remove:

- the current unit record
- all persisted checkpoints for that unit
- the current Markdown document
- all checkpoint Markdown files

After deletion, `read` and `list` should no longer surface that `unit_id`.

Design acceptance is a distinct workflow decision and should not be smuggled into `write_draft` or inferred from high readiness alone.

`accept` should record artifact acceptance, not automatic build approval.

That distinction is already established in [design_review_workflow.md](/home/maddie/repos/clauderfall/docs/design/design_review_workflow.md) and [design_unit_readiness.md](/home/maddie/repos/clauderfall/docs/design/design_unit_readiness.md).

## What `accept` Should Enforce

`accept` should not re-judge whether the design is globally correct.

That judgment should already have happened in the Design conversation.

The runtime should enforce only the mechanical conditions required to record a valid acceptance transition.

At minimum, that includes:

- a persisted current Design checkpoint exists
- the current unit is not already `accepted`
- required acceptance metadata is present if the product later decides to persist it

If the mechanical preconditions fail, `accept` should return a structured failure result.

## Result Shape

All three operations should return a shared structured top-level response shape:

- `result`
- `warnings`
- `artifacts`
- `metadata`

This should match the style already used in [session_lifecycle_mcp_interface.md](/home/maddie/repos/clauderfall/docs/design/session_lifecycle_mcp_interface.md) and [discovery_runtime_mcp_interface.md](/home/maddie/repos/clauderfall/docs/design/discovery_runtime_mcp_interface.md).

Responses should stay operational and concise.

Explicit `read` operations may return structured artifact state, including readable body content in full view.

`write_draft` and `accept` are write-like operations at the MCP boundary and should therefore return status-only success by default.

If the caller needs post-write or post-acceptance state, it should perform an explicit `read`.

Failure and warning results may still include concise structured detail when needed to explain why the operation did not complete cleanly.

## Operation Semantics

The intended semantics are:

- `read` reads authoritative current state in short or full form
- `write_draft` persists a new checkpoint plus current status and readiness judgment without performing workflow acceptance
- `accept` commits the explicit artifact-acceptance transition without automatically approving the unit for build execution

This gives Design one normal read path, one normal persistence path, and one explicit workflow transition that matches the current Design model.

## Tradeoffs

- A three-operation surface is only slightly broader than Discovery's while keeping Design acceptance explicit.
- Reusing the generic name `read` keeps the shared vocabulary clean, but it pushes short-versus-full shape choice into parameters rather than separate tools.
- Keeping `accept` separate from build approval preserves the workflow distinction already present in the Design docs, but it means downstream execution still needs a separate operator decision.

## Reopen Rule

Reopening should not be a separate runtime verb.

If an accepted unit needs revision, the normal path should be:

- `write_draft`
- with `status: draft`

This preserves the artifact's identity while recording the reopen as an ordinary later checkpoint, which matches the checkpoint semantics already defined in [artifact_checkpoint_semantics.md](/home/maddie/repos/clauderfall/docs/design/artifact_checkpoint_semantics.md).

## Unresolved

- Whether explicit build approval should eventually become a separate persisted operation outside this unit.
- Whether parent/child unit linkage changes ever justify a separate transition operation, or whether they should remain part of normal draft writes.

## Readiness

Readiness: high

Rationale: the runtime shape now matches the settled Design workflow rather than borrowing Discovery's simpler model. The remaining uncertainty is narrower and mostly about whether explicit build approval deserves its own persisted operation later.
