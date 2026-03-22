---
title: Clauderfall - Docs Index
doc_type: index
status: active
updated: 2026-03-22
summary: Index of core Clauderfall documentation and shared documentation metadata conventions.
---

# Docs Index

This folder contains the core project docs for Clauderfall.

## Standard Frontmatter

All core docs in this folder use the same frontmatter header:

- `title` — Canonical document title.
- `doc_type` — Document role within the set, such as `index`, `brief`, `engine`, or `future-state`.
- `status` — Lifecycle state. Use `active` unless a document is explicitly superseded or deprecated.
- `updated` — Date of the last substantive edit in `YYYY-MM-DD` format.
- `summary` — One-line description of the document's purpose.

## Files

- `clauderfall.md` — High-level project brief, core thesis, system architecture, and workflow.
- `context_packet.md` — Required context packet structure, inclusion rules, and readiness criteria at the MVP boundary.
- `context_engine.md` — Context engine for turning task artifacts into minimal, auditable execution packets.
- `design_artifact.md` — Required design artifact structure, traceability rules, and readiness criteria for task handoff.
- `design_task_contract.md` — Boundary contract for Design-to-Task handoff and Task-to-Design backflow.
- `discovery_artifact.md` — Required discovery artifact structure, provenance rules, and readiness criteria for design handoff.
- `discovery_design_contract.md` — Boundary contract for Discovery-to-Design handoff and Design-to-Discovery backflow.
- `discovery_engine.md` — Discovery layer for turning unstructured input into grounded, traceable understanding.
- `design_engine.md` — Design layer for converting discovery into structured, implementation-ready system design.
- `future_state.md` — Deferred post-MVP architecture for execution, validation, and harvest.
- `task_artifact.md` — Required task artifact structure, traceability rules, and readiness criteria for context handoff.
- `task_context_contract.md` — Boundary contract for Task-to-Context handoff and Context-to-Task backflow.
- `task_engine.md` — Task engine for turning design artifacts into bounded, executable task contracts.
