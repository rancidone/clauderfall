---
title: Shared Stage Runtime Substrate
doc_type: design
status: ready
updated: 2026-03-27
summary: Defines the common runtime substrate that should support the shared artifact-runtime layer, stage-specific services, session lifecycle, and future TODO work.
---

# Shared Stage Runtime Substrate

## Purpose

This document defines the shared runtime substrate that should sit underneath Clauderfall's stage-specific services.

The goal is to make "one runtime" concrete without collapsing Discovery, Design, session lifecycle, and future TODO work into one giant undifferentiated service.

## Design Position

Clauderfall should have one shared runtime substrate with common primitives and coordination utilities used by multiple stage-specific services.

That substrate should sit below stage-specific service surfaces such as:

- Discovery runtime services
- Design runtime services
- session-lifecycle services
- future TODO or implementation-preparation services

The runtime should be shared at the infrastructure and invariant-support level, not by forcing every stage to share the exact same high-level service API.

For readable stage artifacts such as Discovery briefs and Design units, the substrate should support a shared artifact-runtime layer above raw persistence and below stage-specific services.

## Why A Shared Substrate

The shared architecture pattern already settled that Clauderfall should not build separate runtimes per stage.

The remaining design problem is how to make one runtime real without creating:

- duplicated checkpoint logic
- duplicated artifact read/write handling
- duplicated recovery machinery
- one monolithic mega-service that knows every stage detail

The shared substrate is the answer:

- common runtime capabilities stay centralized
- stage-specific policy still lives in stage-specific services

## Substrate Responsibilities

The shared runtime substrate should own reusable capabilities such as:

- artifact persistence primitives
- checkpoint creation and current-checkpoint updates
- artifact identity and checkpoint resolution
- paired Markdown-plus-sidecar handling
- status-transition write support for checkpointed artifact state
- bounded operation/recovery runner support
- structured operation result helpers
- common warning/failure result conventions

These are cross-stage runtime concerns.

They should not be reimplemented separately for Discovery, Design, lifecycle, or TODO work.

## What Stays Above The Substrate

Stage-specific services should still own:

- Discovery readiness and Design transition logic
- Design review and acceptance semantics
- session-lifecycle projection and archive policy
- future TODO sequencing and implementation-state semantics

The substrate should not decide product-stage policy.

It should provide the deterministic machinery those policies use.

## Suggested Layers

The recommended runtime layering is:

1. shared runtime substrate
2. shared artifact-runtime interface for readable stage artifacts
3. stage-specific backend services
4. MCP handlers
5. LLM skills and interview logic

This makes the dependency direction clean:

- LLM skills call MCP operations
- MCP handlers delegate to stage services
- stage services compose shared artifact-runtime operations and shared runtime substrate primitives

## Likely Shared Components

The shared substrate likely needs components equivalent to:

- `ArtifactStore`
- `CheckpointManager`
- `ArtifactResolver`
- `OperationRunner`
- `ResultFactory` or equivalent structured-result helpers

The names are not the decision.

The decision is that these concerns belong to the shared runtime, not repeated inside each stage.

## Artifact Store Role

The artifact store layer should handle mechanical persisted artifact behavior:

- read current artifact pair
- read specific checkpoint pair
- write new checkpoint pair
- update current materialized artifact pair

It should not decide workflow or lifecycle policy.

## Checkpoint Manager Role

The checkpoint manager should own:

- checkpoint id creation
- current-versus-history updates
- validation that flushed artifact pairs are complete

This is a cross-stage runtime concern because Discovery, Design, lifecycle indexes, and future TODO artifacts all need the same checkpoint semantics.

For readable stage artifacts, those checkpoint semantics should normally be consumed through the shared artifact-runtime layer rather than rebuilt independently inside each stage service.

## Artifact Resolver Role

The resolver should translate between:

- logical artifact identity
- current checkpoint
- specific checkpoint references
- stage/path layout

This keeps path and identity handling out of stage-policy services.

The resolver should be reusable both by the shared artifact-runtime layer and by lifecycle-oriented services that need checkpoint lookup without sharing the same higher-level policy surface.

## Artifact Runtime Layer Role

Above raw persistence primitives, Clauderfall should expose a shared artifact-runtime layer for readable stage artifacts.

That layer should standardize backend operations such as:

- `read_artifact`
- `write_artifact_checkpoint`
- `transition_artifact_status`

This layer should remain policy-neutral.

It should make artifact reads, checkpoint writes, and status-bearing transitions deterministic and durable, while leaving stage-specific decisions to Discovery, Design, or lifecycle services.

## Operation Runner Role

The bounded operation/recovery runner should live in the shared substrate because the need for:

- execute
- verify
- recover

is not unique to session lifecycle.

Discovery and Design transitions can also use the same mechanism once they gain deterministic runtime operations for review, acceptance, or stage transition behavior.

## Structured Result Helpers

Clauderfall should also standardize how backend operations return:

- success or failure classification
- warning codes
- affected artifact references
- operation-specific metadata

This should be shared so MCP response patterns stay consistent across stages.

## Stage Service Shape

Stage services should sit directly on top of the shared substrate and remain policy-oriented.

For readable stage artifacts, a stage service may depend on the shared artifact-runtime layer as its immediate artifact mechanism while still counting as a service built on top of the substrate.

For example:

- Discovery service decides when a brief transition to Design is allowed
- Design service decides when a unit should move to review or acceptance
- session-lifecycle service decides when stale projection is warning versus failure

They use the substrate to enforce those decisions, but they remain the owners of stage semantics.

## Avoiding A Mega-Service

One runtime does not mean one giant service with methods for every product concern.

The shared substrate should remain infrastructural.

The stage services should remain separate enough that:

- Discovery logic does not depend on lifecycle policy details
- lifecycle code does not need to know Design review semantics
- future TODO logic can be added without bloating unrelated services

This is the main reason to separate:

- one runtime substrate
- multiple stage-specific services on top

## Relationship To Existing Docs

This document refines the runtime side of:

- `stage_runtime_mcp_pattern.md`

It also depends on the existing persistence decisions in:

- `artifact_persistence_format.md`
- `artifact_checkpoint_semantics.md`
- `artifact_checkpoint_metadata.md`
- `artifact_filesystem_layout.md`

The lifecycle-specific backend and runner docs are concrete examples of how one stage area should sit on top of the shared substrate:

- `session_lifecycle_backend_service.md`
- `session_lifecycle_operation_runner.md`

The shared artifact-runtime layer that should sit between this substrate and the Discovery/Design services is defined in:

- `stage_artifact_runtime_interface.md`

## Constraints

The shared substrate should preserve:

- one runtime across stages
- clear stage-policy boundaries
- reusable deterministic persistence mechanics
- consistent checkpoint semantics
- consistent operation result semantics

## Tradeoffs

## Benefits

- runtime duplication stays low
- stage services stay smaller and more focused
- MCP interfaces can stay consistent across stages
- future TODO or implementation-prep work has an obvious place to fit

## Costs

- the substrate needs careful scope control
- some abstractions may feel premature if only one or two stages use them at first
- cross-stage changes to runtime primitives may affect several services at once

## Readiness

Readiness: high

Rationale:

The one-runtime structure is now concrete:

- shared substrate below
- stage-specific services above
- MCP above those services
- Clauderfall should prefer a standardized cross-stage artifact-operation vocabulary where the concepts genuinely align

That keeps the one-runtime direction legible at the interface level instead of only in backend structure.

## Vocabulary Direction

Clauderfall should standardize a common artifact-operation vocabulary across stages where the underlying runtime action is genuinely the same.

That likely includes concepts such as:

- read current artifact state
- read specific checkpoint
- write or flush current artifact state
- transition workflow state
- list or resolve artifact references

Stage-specific services may still define domain-specific operations where needed:

- generate Design Start Context
- archive completed thread
- accept design unit

But the common runtime should avoid needless naming drift for shared concepts.

This matters because standardized vocabulary improves:

- MCP consistency across stages
- backend service readability
- test utility reuse
- future extension into TODO or implementation-prep work
