---
title: Clauderfall - Design Docs Index
doc_type: index
status: active
updated: 2026-03-22
summary: Canonical index for Clauderfall design-level architecture, artifact, contract, and implementation documents.
---

# Design Docs Index

This folder contains the design-level documents that define the Clauderfall MVP.

## Purpose

These documents define:

- the system brief and MVP boundary
- the responsibilities of each engine
- the required artifact schemas
- the boundary contracts between engines
- the deferred future-state components that remain outside the MVP

## Read Order

1. `clauderfall.md`
2. `discovery_engine.md`
3. `design_engine.md`
4. `task_engine.md`
5. `context_engine.md`
6. `future_state.md`
7. `implementation_strategy.md`
8. `persistence_semantics.md`

Use the artifact specs and contracts while refining or implementing a specific layer.

## Files

- `clauderfall.md` - Project brief, architecture, workflow, and MVP boundary.
- `discovery_engine.md` - Discovery engine purpose, capabilities, operating model, and exit condition.
- `design_engine.md` - Design engine purpose, capabilities, operating model, and exit condition.
- `task_engine.md` - Task engine purpose, capabilities, operating model, and exit condition.
- `context_engine.md` - Context engine purpose, capabilities, operating model, and exit condition.
- `discovery_artifact.md` - Normative structure and validity rules for Discovery Artifacts.
- `design_artifact.md` - Normative structure and validity rules for Design Artifacts.
- `task_artifact.md` - Normative structure and validity rules for Task Artifacts.
- `context_packet.md` - Normative structure and validity rules for Context Packets.
- `discovery_design_contract.md` - Boundary contract between Discovery and Design.
- `design_task_contract.md` - Boundary contract between Design and Task.
- `task_context_contract.md` - Boundary contract between Task and Context.
- `future_state.md` - Deferred post-MVP architecture for execution, validation, and harvest.
- `implementation_strategy.md` - Concrete MVP implementation decisions for package shape, storage, access, and MCP layering.
- `persistence_semantics.md` - Canonical MVP rules for artifact identity, versioning, mutability, and retrieval.
