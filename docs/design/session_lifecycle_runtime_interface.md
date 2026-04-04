---
title: Session Lifecycle Runtime Interface
doc_type: design
status: ready
updated: 2026-04-04
summary: Defines the deterministic runtime operations and MCP-facing boundary for recent-session lifecycle work.
---

# Session Lifecycle Runtime Interface

## Purpose

This document defines the runtime boundary that should enforce recent-session lifecycle behavior in Clauderfall.

The goal is to keep lifecycle correctness in deterministic backend code while still giving the LLM a clean interface for inspecting and advancing recent-session state.

## Design Position

Recent-session lifecycle behavior should not be implemented as a loose collection of prompt-driven file edits.

It should be implemented as deterministic runtime operations owned by backend code and exposed to the LLM through a narrow interface.

MCP is a good fit for the LLM-facing side of that boundary.

The intended split is:

- backend runtime code owns artifact reads, writes, projection rebuilds, and lifecycle transitions
- MCP tools expose those operations to the LLM as explicit capabilities
- the LLM decides when to invoke the operations and supplies bounded human-authored content where needed

## Why This Boundary

The session-lifecycle cluster already established several behaviors that are not safely enforceable by prompt discipline alone:

- thread-first handoff writes with derived repo-index projection
- deterministic projection rebuild on mismatch or malformed startup state
- immediate archive transition on completion
- no valid steady state between active and archived

Those are runtime guarantees, not conversational preferences.

If Clauderfall leaves them to ordinary document editing skills, it will not actually have deterministic lifecycle behavior.

## Runtime Responsibilities

Backend code should own at least these responsibilities:

- read authoritative active-thread artifacts and sidecars
- persist handoff updates for active threads
- derive and rebuild the repo-level recent-session index from structured metadata
- perform archive transitions
- enforce postconditions for lifecycle operations
- surface warnings or errors when persisted state is stale, malformed, or inconsistent

These operations should not require the LLM to manually keep multiple persisted artifacts synchronized.

## MCP-Facing Responsibilities

The LLM-facing interface should expose a small set of explicit capabilities rather than raw filesystem mutation.

At a minimum, the MCP boundary likely needs operations for:

- reading startup-oriented recent-session state
- reading one active thread artifact
- updating one active thread handoff artifact
- rebuilding the repo-level recent-session index deterministically
- completing and archiving a thread

Those operations should return structured results that make lifecycle state explicit.

The LLM should not need to infer whether a transition succeeded from prose alone.

The preferred shape is high-level lifecycle operations rather than low-level artifact-service primitives exposed directly to the model.

## LLM Responsibilities

The LLM should remain responsible for the parts that are actually language-shaped:

- drafting or revising the readable thread artifact content
- producing ordered `work_items`, bounded thread Markdown, or `closure_summary` when appropriate
- deciding which lifecycle operation to invoke next based on operator intent and current state

The LLM should not be responsible for:

- enforcing atomicity
- synchronizing multi-artifact writes manually
- deciding whether projection rebuild was mechanically correct from raw file edits

## Operation Shape

The runtime interface should prefer named lifecycle operations over generic file-write tools.

That means operations should look more like:

- `session_read_startup_view`
- `session_read_thread`
- `session_write_handoff`
- `session_archive_thread`

and less like:

- write arbitrary file
- rewrite Markdown document
- patch YAML sidecar directly

Generic file access may still exist for inspection or debugging, but it should not be the normal correctness path for lifecycle transitions.

The MCP surface should stay intentionally small and lifecycle-shaped.

Artifact-service primitives may still exist inside the runtime, but they should sit behind the lifecycle layer rather than becoming the normal model-facing contract.

## Determinism Rule

Any operation that changes lifecycle state should be deterministic in backend behavior.

That means:

- explicit inputs
- explicit postconditions
- explicit success or failure result
- deterministic rebuild from structured metadata where rebuild is allowed

For example, repo-index rebuild should be a mechanical projection from authoritative thread sidecars, not an LLM-authored summary regeneration pass.

## Error Model

MCP responses for lifecycle operations should make failure visible and machine-usable.

They should distinguish at least:

- success
- warning with recovery performed
- failure with no state transition committed

This matters because the LLM needs to know whether it should continue normal session flow, inform the operator about degraded state, or stop and request intervention.

## Relationship To Artifact Docs

The existing artifact and flow docs remain the source of lifecycle behavior:

- `session_recent_state_artifact.md` defines the artifact contract
- `session_handoff_write_update_flow.md` defines handoff write semantics
- `session_start_drill_in_flow.md` defines startup drill-in behavior
- `session_archive_transition_mechanics.md` defines completion and archive-transition behavior

This document adds the missing enforcement boundary:

- which parts belong in deterministic runtime code
- which parts may be exposed through MCP
- which parts remain LLM-authored content work

## Constraints

This design should preserve the main recent-session-state constraints:

- token-efficient startup
- bounded carry-forward state
- deterministic lifecycle transitions
- strict separation between active state and history
- minimal need for multi-pass document synchronization

## Tradeoffs

## Benefits

- lifecycle correctness moves into code that can enforce invariants
- MCP gives the LLM a clean operational interface without exposing raw persistence as the main path
- failures become inspectable and actionable rather than conversationally ambiguous

## Costs

- Clauderfall needs backend lifecycle services, not just prompt skills
- the MCP layer needs careful operation design to avoid becoming a thin wrapper around arbitrary file edits
- some implementation speed is traded for stronger invariants and clearer runtime semantics

## Readiness

Readiness: high

Rationale:

The core direction is now explicit:

- lifecycle correctness belongs in backend runtime code
- MCP is the preferred LLM-facing interface
- the LLM remains responsible for language work, not enforcement
- the model-facing boundary should use a small set of high-level lifecycle operations rather than low-level persistence primitives

The remaining work is downstream interface definition and implementation, not unresolved design direction.
