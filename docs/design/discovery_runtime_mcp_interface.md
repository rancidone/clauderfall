---
title: Discovery Runtime MCP Interface
doc_type: design
status: ready
updated: 2026-04-03
summary: Defines the Discovery runtime and MCP-facing operation set for reading the working brief, checkpointing draft progress, transitioning accepted Discovery output into Design, and explicitly deleting obsolete briefs.
---

# Discovery Runtime MCP Interface

## Purpose

This document defines the concrete runtime and MCP-facing operation set for Discovery.

The goal is to make the shared stage-runtime pattern actionable for Discovery without expanding the interface into a generic artifact-editing surface.

## Design Position

Discovery should expose a minimal high-level operation set:

- `read`
- `write_draft`
- `to_design`
- `delete`

This is intentionally small.

Discovery should not expose low-level file mutation, ad hoc checkpoint management, or free-form stage-transition commands as the normal LLM contract.

## Why This Boundary

The Discovery engine should own interview logic, synthesis, and readable brief drafting.

The runtime should own:

- authoritative artifact reads
- checkpoint creation and current-checkpoint updates
- persistence of the readable brief and its structured sidecar
- mechanical transition integrity for Design handoff
- deterministic transition results

Without this boundary, Discovery would still depend on prompt discipline for persistence and handoff correctness.

## Operation Set

The initial Discovery runtime/MCP surface should expose exactly these operations:

- `read`
- `write_draft`
- `to_design`
- `delete`

These names should follow the shared vocabulary in [stage_runtime_operation_vocabulary.md](/home/maddie/repos/clauderfall/docs/design/stage_runtime_operation_vocabulary.md) while still staying stage-shaped.

## 1. `read`

## Purpose

Return the authoritative current Discovery artifact state for the active design unit or session context.

## What `read` Should Return

`read` should support a short form and a full form.

The short form should return the minimum structured metadata needed for the LLM to continue the interview safely without loading the full brief body.

The full form should return the readable brief body plus the same structured metadata.

The short form should include at least:

- artifact identity
- title
- current checkpoint reference
- workflow status
- readiness signal
- readiness rationale
- any structured transition metadata needed to reason about `to_design`

`read` is the operation the LLM uses to recover context, verify current truth, or resume after compaction.

## 2. `write_draft`

## Purpose

Persist a new Discovery draft checkpoint while keeping the artifact in Discovery-owned workflow state.

## Design Position

`write_draft` should be the normal persistence operation during Discovery interviewing.

It should:

- accept the revised readable brief body
- accept the associated structured sidecar content
- create a new checkpoint for the same artifact identity
- update the current checkpoint pointer deterministically
- persist the current workflow status
- persist the current readiness signal
- persist the current readiness rationale
- return structured confirmation of the new authoritative checkpoint

`write_draft` should be able to persist either of the normal Discovery workflow states:

- `draft`
- `accepted`

`accepted` means the Discovery brief has been accepted as the Design input artifact.

It does not mean the Design transition has already been executed.

`write_draft` is a drafting operation, not a transition operation.

## Important Constraint

The runtime should preserve the separation between:

- saving draft progress
- evaluating readiness
- performing a stage transition

The LLM may recommend readiness in the draft content, and `write_draft` should persist that readiness judgment explicitly.

## 4. `delete`

## Purpose

Delete a Discovery brief and all of its persisted runtime state when the operator explicitly wants it removed.

## Design Position

`delete` should be exceptional.

It should be used for cleanup of superseded or mistaken Discovery briefs, not for ordinary workflow transitions.

`delete` should remove:

- the current brief record
- all persisted checkpoints for that brief
- the current Markdown document
- all checkpoint Markdown files

After deletion, `read` should fail for that `brief_id`.

But `write_draft` should not treat that judgment as an automatic transition.

## 3. `to_design`

## Purpose

Perform the explicit Discovery-to-Design transition after the operator and LLM have already decided to move forward.

## Design Position

`to_design` should be the only normal operation that advances accepted Discovery output into Design-facing state.

It should be explicit because this is a workflow boundary and artifact-creation event, not just another checkpoint write.

## What `to_design` Should Enforce

`to_design` should not perform a second Discovery-readiness judgment.

The readiness decision should already have been made in the Discovery conversation and persisted by `write_draft`.

The runtime should enforce only the mechanical preconditions required to create valid downstream state.

At minimum, that includes:

- a persisted current Discovery checkpoint exists
- the current Discovery artifact is in `accepted` status, unless an explicit override is supplied
- required handoff fields are present
- any Design Start Context derivation required by the current docs succeeds

It should also support an explicit override path from `draft` when the operator chooses to move into Design despite medium readiness or incomplete framing.

If the mechanical preconditions fail, `to_design` should return a structured failure result rather than allowing the LLM to imply that the transition happened.

## Result Shape

All three operations should return a shared structured top-level response shape:

- `result`
- `warnings`
- `artifacts`
- `metadata`

This should match the style already used in [session_lifecycle_mcp_interface.md](/home/maddie/repos/clauderfall/docs/design/session_lifecycle_mcp_interface.md).

Responses should stay operational and concise.

Explicit `read` operations may return structured artifact state, including readable body content in full view.

`write_draft` and `to_design` are write-like operations at the MCP boundary and should therefore return status-only success by default.

If the caller needs post-write or post-transition state, it should perform an explicit `read`.

Failure and warning results may still include concise structured detail when needed to explain why the operation did not complete cleanly.

## Operation Semantics

The intended semantics are:

- `read` reads authoritative current state in short or full form
- `write_draft` persists a new checkpoint plus current status and readiness judgment without crossing the stage boundary
- `to_design` commits the explicit Design transition without re-judging Discovery quality

This gives Discovery one normal read path, one normal persistence path, and one explicit transition path.

That is enough to support the core Discovery workflow without making the MCP surface sprawling.

## Tradeoffs

- A three-operation surface is easy to reason about, but it may prove too narrow if Discovery needs a distinct operation for explicit review or reopen behavior.
- Reusing the generic name `read` keeps the shared vocabulary clean, but it pushes view-shape variation into parameters rather than separate tool names.
- Keeping `accepted` separate from readiness preserves a clean workflow field, but it means Discovery now records both status and readiness judgment explicitly.
- Keeping `write_draft` separate from `to_design` preserves workflow clarity, but it means the LLM must decide explicitly when to attempt the transition.

## Unresolved

- Whether `to_design` should derive the Design Start Context directly or delegate that derivation to a lower artifact service used inside the same operation.
- Whether Discovery needs a separate explicit `reopen` or `revise_after_handoff` operation later, or whether that belongs under a broader cross-stage repair workflow.
- Whether the explicit override path should persist any special marker beyond the normal readiness rationale.

## Readiness

Readiness: high

Rationale: the workflow semantics are now concrete enough to guide downstream Design interface work. The remaining uncertainty is narrower and mostly about Design Start Context derivation placement and override recording details.
