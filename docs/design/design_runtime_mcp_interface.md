---
title: Design Runtime MCP Interface
doc_type: design
status: ready
updated: 2026-03-27
summary: Defines the minimal Design runtime and MCP-facing operation set for reading the current unit, checkpointing draft progress, moving into review, and accepting the current design record.
---

# Design Runtime MCP Interface

## Purpose

This document defines the concrete runtime and MCP-facing operation set for Design.

The goal is to make the shared stage-runtime pattern actionable for Design while preserving the Design-specific review and acceptance workflow already established elsewhere in the docs.

## Design Position

Design should expose a small high-level operation set:

- `read`
- `write_draft`
- `to_review`
- `accept`

This is intentionally slightly broader than Discovery.

Discovery can move from drafting into the next stage with a single explicit transition.

Design already has a meaningful internal review workflow, so its runtime surface should reflect that rather than collapsing review and acceptance into one operation.

## Why This Boundary

The Design engine should own:

- design interviewing
- design judgment
- visible drafting and revision
- readiness assessment
- recommendations about when to review or accept a unit

The runtime should own:

- authoritative artifact reads
- checkpoint creation and current-checkpoint updates
- persistence of the readable design unit and its structured sidecar
- deterministic status transitions for the current design unit
- structured acceptance results and artifact linkage

Without this boundary, Design would still rely on prompt discipline for artifact status transitions and review-state correctness.

## Relationship To Existing Design Workflow

The Design review model already distinguishes:

- `draft`
- `in_review`
- `accepted`

And it already keeps readiness separate from workflow status.

This runtime interface should preserve that model rather than replacing it.

The MCP surface should therefore support:

- reading the current unit
- writing draft checkpoints
- explicitly moving a stable unit into review
- explicitly accepting the current design record

## Operation Set

The initial Design runtime/MCP surface should expose exactly these operations:

- `read`
- `write_draft`
- `to_review`
- `accept`

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

- accept the revised readable design unit body
- accept the associated structured sidecar content
- create a new checkpoint for the same artifact identity
- update the current checkpoint pointer deterministically
- persist the current workflow status
- persist the current readiness signal
- persist the current readiness rationale
- return structured confirmation of the new authoritative checkpoint

`write_draft` should be able to persist either of the normal mutable Design workflow states:

- `draft`
- `in_review`

`write_draft` should not itself perform acceptance.

Acceptance is an explicit review decision, not a normal drafting checkpoint.

## Important Constraint

The runtime should preserve the separation between:

- saving revised design content
- rating design readiness
- moving the unit into review
- accepting the design artifact

The LLM may recommend any of those moves, but `write_draft` should only persist the artifact and its current judgment.

## 3. `to_review`

## Purpose

Move the current Design unit from active drafting into explicit review state.

## Design Position

`to_review` should exist because Design has a real workflow distinction between “still shaping” and “stable enough to review.”

This should not be faked through prose alone.

`to_review` should be the operation that records that distinction.

## What `to_review` Should Enforce

`to_review` should not re-design the unit or produce an independent readiness judgment.

The Design conversation should already have produced the current draft, readiness signal, and rationale.

The runtime should enforce only the mechanical conditions required to move into review cleanly.

At minimum, that includes:

- a persisted current Design checkpoint exists
- the artifact is not already `accepted`
- the structured fields required for review are present

If those preconditions fail, `to_review` should return a structured failure rather than allowing the LLM to imply that review state changed.

## 4. `accept`

## Purpose

Accept the current Design artifact as the operator-approved design record for this unit.

## Design Position

`accept` should be explicit.

Design acceptance is a distinct workflow decision and should not be smuggled into `write_draft` or inferred from high readiness alone.

`accept` should record artifact acceptance, not automatic build approval.

That distinction is already established in [design_review_workflow.md](/home/maddie/repos/clauderfall/docs/design/design_review_workflow.md) and [design_unit_readiness.md](/home/maddie/repos/clauderfall/docs/design/design_unit_readiness.md).

## What `accept` Should Enforce

`accept` should not re-judge whether the design is globally correct.

That judgment should already have happened in the Design conversation and review moment.

The runtime should enforce only the mechanical conditions required to record a valid acceptance transition.

At minimum, that includes:

- a persisted current Design checkpoint exists
- the current unit is in `in_review`, unless an explicit override is supplied
- required acceptance metadata is present if the product later decides to persist it

It should also support an explicit override path from `draft` when the operator chooses to accept the current design without a prior formal review transition.

If the mechanical preconditions fail, `accept` should return a structured failure result.

## Result Shape

All four operations should return a shared structured top-level response shape:

- `result`
- `warnings`
- `artifacts`
- `metadata`

This should match the style already used in [session_lifecycle_mcp_interface.md](/home/maddie/repos/clauderfall/docs/design/session_lifecycle_mcp_interface.md) and [discovery_runtime_mcp_interface.md](/home/maddie/repos/clauderfall/docs/design/discovery_runtime_mcp_interface.md).

Responses should stay operational and concise.

The runtime should return references and structured state, not long explanatory prose, unless a short human-readable message is needed to explain a warning or failure.

## Operation Semantics

The intended semantics are:

- `read` reads authoritative current state in short or full form
- `write_draft` persists a new checkpoint plus current status and readiness judgment without performing workflow acceptance
- `to_review` commits the explicit transition into review state
- `accept` commits the explicit artifact-acceptance transition without automatically approving the unit for build execution

This gives Design one normal read path, one normal persistence path, and two explicit workflow transitions that match the current Design model.

## Tradeoffs

- A four-operation surface is larger than Discovery's, but Design has a genuinely richer workflow and should not flatten review away.
- Reusing the generic name `read` keeps the shared vocabulary clean, but it pushes short-versus-full shape choice into parameters rather than separate tools.
- Keeping `accept` separate from build approval preserves the workflow distinction already present in the Design docs, but it means downstream execution still needs a separate operator decision.
- Allowing override into `accept` from `draft` keeps the interface practical, but it weakens the normal expectation that stable units pass through `in_review`.

## Reopen Rule

Reopening should not be a separate runtime verb.

If an accepted or in-review unit needs revision, the normal path should be:

- `write_draft`
- with `status: draft`

This preserves the artifact's identity while recording the reopen as an ordinary later checkpoint, which matches the checkpoint semantics already defined in [artifact_checkpoint_semantics.md](/home/maddie/repos/clauderfall/docs/design/artifact_checkpoint_semantics.md).

## Unresolved

- Whether explicit build approval should eventually become a separate persisted operation outside this unit.
- Whether parent/child unit linkage changes ever justify a separate transition operation, or whether they should remain part of normal draft writes.

## Readiness

Readiness: high

Rationale: the runtime shape now matches the settled Design workflow rather than borrowing Discovery's simpler model. The remaining uncertainty is narrower and mostly about whether explicit build approval deserves its own persisted operation later.
