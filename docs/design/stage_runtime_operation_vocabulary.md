---
title: Stage Runtime Operation Vocabulary
doc_type: design
status: draft
updated: 2026-04-03
summary: Defines the standardized cross-stage operation vocabulary for the shared Clauderfall runtime and MCP interfaces.
---

# Stage Runtime Operation Vocabulary

## Purpose

This document defines the standardized operation vocabulary Clauderfall should use across the shared runtime substrate, stage services, and MCP interfaces.

The goal is to make the one-runtime architecture legible at the naming level rather than only in backend structure.

## Design Position

Clauderfall should standardize a common operation vocabulary across stages wherever the underlying runtime action is genuinely the same.

This vocabulary should apply consistently across:

- shared runtime primitives
- stage-specific backend services
- MCP operation naming
- documentation about stage operations

Stage-specific domains may still introduce domain-specific verbs where the underlying action is truly different.

But shared runtime concepts should not be renamed arbitrarily per stage.

## Why Standardized Vocabulary

Without a shared vocabulary, a one-runtime architecture will still feel like separate products.

Naming drift would create avoidable confusion such as:

- Discovery "publishes" where Design "flushes"
- Lifecycle "loads" where Design "reads"
- TODO "finalizes" where Design "accepts"

Even if the underlying mechanics were shared, the system would be harder to reason about, test, and extend.

Standardized vocabulary keeps the cross-stage mental model stable.

## Vocabulary Layers

The vocabulary should distinguish three layers:

1. shared runtime verbs
2. stage-specific operation names built from those verbs
3. domain-specific actions that do not map cleanly to a shared verb

## 1. Shared Runtime Verbs

These should be preferred wherever the underlying action matches.

### `read`

Use `read` for retrieving authoritative persisted state.

Examples:

- `read_discovery_brief`
- `read_design_unit`
- `session_read_thread`

Do not introduce synonyms like `load`, `fetch`, or `get` unless there is a real distinction.

### `list`

Use `list` for retrieving multiple references or summaries without claiming full artifact detail.

Examples:

- `list_design_units`
- `list_recent_threads`

### `write`

Use `write` for persisting current authoritative state for an artifact or artifact-like unit.

Examples:

- `write_discovery_brief`
- `write_design_unit`
- `session_write_handoff`

`write` should be the default verb for persisted artifact updates.

### `transition`

Use `transition` when the main purpose is changing workflow or stage state according to explicit rules.

Examples:

- `transition_design_unit_status`
- `transition_discovery_readiness`

This verb is useful when the action is not primarily about content revision.

### `derive`

Use `derive` for deterministic generation of one artifact or projection from another authoritative source.

Examples:

- `derive_design_start_context`
- `derive_recent_session_index`

This is better than vague verbs like `build` or `make` when the result is a deterministic product of existing state.

### `archive`

Use `archive` when moving authoritative state from active usage into a historical layer.

Example:

- `session_archive_thread`

This is domain-specific enough to remain a named verb, but broad enough to standardize where archival exists.

### `delete`

Use `delete` only for explicit destructive removal of authoritative persisted state.

Examples:

- `discovery_delete`
- `design_delete`

Do not rename this to softer verbs when the operation actually removes runtime state and checkpoint history.

Deletion should remain exceptional and operator-directed.

### `resolve`

Use `resolve` for mapping references to authoritative artifact ids, checkpoints, or paths.

Examples:

- `resolve_artifact_ref`
- `resolve_current_checkpoint`

### `checkpoint`

Use `checkpoint` only when the operation is explicitly about persisting a checkpoint as a product-level act.

Examples:

- `checkpoint_discovery_brief`
- `checkpoint_design_unit`

This should not be used as a synonym for every write.

Ordinary `write` may create a checkpoint under the hood, but `checkpoint` should be reserved for flows where checkpoint creation itself is the primary operator-visible action.

### `rebuild`

Use `rebuild` for deterministic regeneration of a derived artifact or projection after staleness, corruption, or explicit repair.

Examples:

- `rebuild_search_index`

This should imply:

- authoritative source already exists
- result is regenerated mechanically

## 2. Naming Rules For Stage Operations

Stage-facing operation names should generally follow:

- `<verb>_<artifact_or_domain_object>`
- `<verb>_<artifact_or_domain_object>_<qualifier>` when needed

Examples:

- `read_design_unit`
- `write_design_unit`
- `checkpoint_discovery_brief`
- `derive_design_start_context`
- `session_archive_thread`

Qualifiers should only be added when they disambiguate a real distinction:

- `session_read_startup_view`
- `session_write_handoff`

## 3. Domain-Specific Actions

Some actions are genuinely domain-specific and should remain so.

Examples:

- `accept_design_unit`
- `generate_design_start_context` if the product wants stronger user-facing wording than `derive`
- future TODO-specific actions around implementation sequencing or work approval

These should still align with the shared vocabulary when possible, but they do not need to be artificially flattened if doing so hides product meaning.

## Preferred Naming Constraints

Clauderfall should prefer:

- one canonical verb per shared runtime concept
- snake_case operation names
- explicit nouns over generic placeholders
- minimal synonyms

Clauderfall should avoid:

- `get`, `fetch`, and `load` all meaning the same thing
- `save`, `flush`, and `write` being used interchangeably without reason
- mixing user-facing metaphors with backend verbs arbitrarily

## Discovery Implications

Discovery operations should likely prefer names such as:

- `read_discovery_brief`
- `write_discovery_brief`
- `checkpoint_discovery_brief`
- `derive_design_start_context`
- `transition_discovery_state` or a narrower equivalent

## Design Implications

Design operations should likely prefer names such as:

- `read_design_unit`
- `write_design_unit`
- `checkpoint_design_unit`
- `transition_design_unit_status`
- `accept_design_unit`

## Workflow Noun Direction

Clauderfall should standardize on `status` as the default noun for workflow-oriented structured fields and transition operations.

That means Clauderfall should prefer names such as:

- `status`
- `transition_design_unit_status`
- `transition_discovery_status`
- `transition_todo_status`

and avoid mixing `state` and `status` when the concept is the ordinary workflow position of an artifact.

`state` may still be used for broader runtime or lifecycle descriptions when it genuinely means something wider than workflow status, but it should not be the default noun for stage artifact workflow fields.

## Session Lifecycle Implications

The current lifecycle operation set is already close to the preferred vocabulary:

- `session_read_startup_view`
- `session_read_thread`
- `session_write_handoff`
- `session_archive_thread`

That makes the lifecycle cluster a good concrete starting example.

## Future TODO Implications

A TODO or implementation-prep stage should follow the same vocabulary where possible.

Likely examples:

- `read_todo_artifact`
- `write_todo_artifact`
- `checkpoint_todo_artifact`
- `transition_todo_state`

## Relationship To Shared Runtime

This vocabulary is part of making the shared runtime substrate feel like one system.

It sits on top of:

- `stage_runtime_mcp_pattern.md`
- `shared_stage_runtime_substrate.md`

and should guide later Discovery, Design, lifecycle, and TODO interface work.

## Constraints

This vocabulary should preserve:

- one-runtime coherence
- readable and predictable operation names
- clear distinction between shared concepts and domain-specific actions
- low naming drift across stages

## Tradeoffs

## Benefits

- interface consistency improves across stages
- shared runtime and MCP docs become easier to scan
- backend service naming becomes easier to standardize

## Costs

- some stage-specific names may need to change later for consistency
- the vocabulary needs discipline to stay small and meaningful

## Readiness

Readiness: high

Rationale:

The cross-stage verb vocabulary is now concrete:

- shared verbs are named
- naming rules are explicit
- lifecycle already fits the pattern well
- `status` is the standardized workflow noun across stages

The remaining work is downstream adoption in stage-specific runtime interfaces, not unresolved vocabulary design.
