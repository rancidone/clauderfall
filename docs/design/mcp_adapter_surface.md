---
title: MCP Adapter Surface
doc_type: design
status: ready
updated: 2026-04-03
summary: Defines the first MCP-facing adapter layer over the v2 runtime services, including tool naming, response mapping, and thin-handler boundaries.
---

# MCP Adapter Surface

## Purpose

This document defines the first implementation-facing MCP adapter surface for Clauderfall.

The goal is to make the current runtime services directly usable through MCP without reopening the already-settled runtime architecture.

This unit focuses on:

- tool naming
- adapter responsibilities
- response mapping
- returned-content boundaries

It does not redefine stage behavior that is already covered by the Discovery, Design, and session-lifecycle runtime interface docs.

## Design Position

Clauderfall should expose one MCP server with a flat tool namespace for the first implementation slice.

The tool names should be explicit and stage-shaped:

- `discovery_read`
- `discovery_write_draft`
- `discovery_to_design`
- `discovery_delete`
- `design_read`
- `design_write_draft`
- `design_accept`
- `design_delete`
- `session_read_startup_view`
- `session_read_thread`
- `session_write_handoff`
- `session_archive_thread`

The adapter layer should remain thin.

The runtime services already own:

- artifact reads
- checkpoint writes
- workflow transitions
- lifecycle verification and recovery

The MCP adapter should not become a second policy layer.

## Why Flat Tool Names

The first MCP slice does not need a more elaborate namespace model.

Flat names are acceptable here because:

- the operation set is still small
- stage intent is visible in the tool name
- the runtime already supplies the stronger organizational boundary
- flat names reduce framework and transport assumptions in the first slice

If Clauderfall later needs namespaced grouping for discoverability, that can be added after the initial adapter surface has real usage pressure.

## Adapter Boundary

Each MCP handler should do only four things:

1. validate input shape
2. call exactly one runtime service method
3. map the runtime result into the published MCP response shape
4. return structured output

Handlers should not:

- perform direct filesystem edits
- orchestrate multi-step lifecycle transitions on their own
- reinterpret stage-policy rules
- synthesize replacement metadata from prose

That work already belongs in the runtime layer.

## Runtime-To-MCP Result Mapping

The runtime layer currently returns:

- `ok`
- `warning`
- `error`

The MCP layer should map these deterministically to:

- `success`
- `warning`
- `failure`

The mapping rule should be:

- runtime `ok` -> MCP `success`
- runtime `warning` -> MCP `warning`
- runtime `error` -> MCP `failure`

This mapping should happen centrally in shared adapter code rather than inside each individual tool.

## Shared MCP Response Shape

Every Clauderfall MCP tool in this first slice should return the same top-level shape:

- `result`
- `warnings`
- `artifacts`
- `metadata`

### `result`

`result` should be one of:

- `success`
- `warning`
- `failure`

### `warnings`

`warnings` should remain short and machine-usable.

Where the runtime already returns warning codes or short warning strings, the MCP layer should preserve them rather than rewrite them into longer prose.

### `artifacts`

`artifacts` should contain:

- artifact references
- checkpoint references
- compact structured payloads that are explicitly part of the tool contract

This field should not turn into a generic document dump surface.

Write-like MCP operations should usually omit `artifacts` entirely.

### `metadata`

`metadata` should contain concise operational fields such as:

- ids
- checkpoint ids
- booleans like `override`, `rebuilt`, or `projection_stale`
- counts used for startup or lifecycle orientation

Write-like MCP operations should usually omit `metadata` entirely.

## Returned Content Rule

The MCP adapter should preserve the content boundary already implied by the runtime interface docs.

For Discovery and Design:

- `*_read` tools may return readable artifact bodies in full view
- short view should remain compact and structured
- write and transition tools should return status only by default
- if a write or transition needs follow-up state inspection, the caller should perform an explicit read

For session lifecycle:

- `session_read_thread` may return the readable thread artifact because drill-in explicitly asks for thread detail
- `session_read_startup_view` should remain compact
- lifecycle write and archive tools should return status only by default

This keeps MCP aligned with the token-economy goal instead of turning every operation into a large read response.

## Initial Tool Mapping

The first adapter layer should map tools to runtime services like this.

### Discovery

- `discovery_read` -> `RuntimeServices.discovery.read(...)`
- `discovery_write_draft` -> `RuntimeServices.discovery.write_draft(...)`
- `discovery_to_design` -> `RuntimeServices.discovery.to_design(...)`

### Design

- `design_read` -> `RuntimeServices.design.read(...)`
- `design_write_draft` -> `RuntimeServices.design.write_draft(...)`
- `design_accept` -> `RuntimeServices.design.accept(...)`

### Session Lifecycle

- `session_read_startup_view` -> `RuntimeServices.session_lifecycle.session_read_startup_view(...)`
- `session_read_thread` -> `RuntimeServices.session_lifecycle.session_read_thread(...)`
- `session_write_handoff` -> `RuntimeServices.session_lifecycle.session_write_handoff(...)`
- `session_archive_thread` -> `RuntimeServices.session_lifecycle.session_archive_thread(...)`

## Shared Adapter Helpers

The first MCP implementation should include a small shared adapter helper layer for:

- runtime result mapping
- common response serialization
- shared error wrapping for input validation failures
- runtime service bootstrapping from repo root

This helper layer should remain narrow.

It should not grow into a second runtime or a second domain model.

## Validation Rule

Input validation should happen at the MCP boundary for:

- required parameter presence
- enum-like option normalization where the runtime expects controlled values
- simple shape errors that should fail before runtime invocation

But validation should not duplicate runtime invariants that the runtime already owns.

Examples:

- the adapter may reject a missing `thread_id`
- the adapter should not independently decide whether acceptance from `draft` is allowed

## Input Schema Completeness Rule

Every MCP tool that accepts a structured body parameter — particularly `sidecar` arguments — must expose the full internal schema of that parameter in its `input_schema` definition, not just `{"type": "object"}`.

The LLM client uses the tool's input schema as the sole authoritative contract for what to write.

A bare `{"type": "object"}` gives the client no field contract. The result is schema drift: the client invents fields, uses the wrong names, or omits required fields, and the error surfaces at runtime rather than at the tool boundary.

The input schema for structured body parameters should:

- enumerate required fields
- specify enum constraints for controlled values
- define nested object and array shapes
- match the shape the runtime validator actually enforces

This is not redundant with runtime validation. The runtime validator is the invariant layer. The tool input schema is the machine-readable contract that tells the LLM what to produce. Both must exist and stay in sync.

## Versioning Position

The first MCP slice should not introduce explicit version suffixes in tool names.

The active runtime is already the v2 runtime, and the repo does not currently have a competing live MCP surface that requires parallel naming.

If a future incompatible MCP contract appears, that is the right time to introduce explicit versioning.

## Constraints

This design must preserve the current architecture constraints:

- runtime remains the only policy and invariant layer
- MCP is a narrow operational contract
- no raw file-mutation tools as the primary path
- stage and lifecycle interfaces remain small and explicit
- token-heavy content should be returned only where the underlying stage contract expects it

## Readiness

Readiness: high

Rationale:

The remaining MCP-facing ambiguity was narrow and is now resolved concretely:

- flat tool names are chosen
- handlers stay thin
- response mapping is explicit
- content-return boundaries are aligned with the existing runtime-interface docs

This is sufficient to start implementation without inventing a second architecture pass.
