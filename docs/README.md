---
title: Clauderfall Docs Index
doc_type: index
status: active
updated: 2026-03-22
summary: Top-level index for the active Clauderfall documentation set and archived legacy material.
---

# Docs Index

This folder contains the active Clauderfall documentation set.

## Structure

- `design/` - Active product and engine-level discovery/design docs.
- `handoffs/` - Active short session handoffs for continuity across sessions.
- `legacy/` - Archived MVP-era docs retained as input material, not current truth.

## Standard Frontmatter

Core docs use the same frontmatter fields:

- `title` - Canonical document title.
- `doc_type` - Document role, such as `index`, `brief`, `engine-brief`, `design`, or `archive-index`.
- `status` - Lifecycle state. Use `active` unless explicitly archived, superseded, or deprecated.
- `updated` - Date of the last substantive edit in `YYYY-MM-DD` format.
- `summary` - One-line description of the document's purpose.

## Primary Entry Points

- `design/README.md` - Canonical index for the active documentation set.
- `design/clauderfall_product_brief.md` - Product brief for Clauderfall.
- `design/discovery_engine.md` - Discovery engine brief derived from the product brief.
- `design/design_engine.md` - Design engine brief derived from the product brief.
- `design/design_unit_artifact.md` - Design doc for the design-unit artifact shape.
- `design/design_unit_readiness.md` - Design doc for the meaning of design-unit readiness.
- `design/design_unit_document_shape.md` - Design doc for the canonical readable design-unit document shape.
- `design/design_unit_sequencing.md` - Design doc for sequencing and decomposition of design units.
- `design/design_review_workflow.md` - Design doc for design-unit drafting, review, and build-readiness approval.
- `design/design_session_flow.md` - Design doc for the end-to-end Design-stage interaction flow.
- `design/discovery_design_handoff.md` - Design doc for the condensed Discovery-to-Design handoff artifact.
- `design/design_discovery_reentry.md` - Design doc for the Design-to-Discovery repair boundary.
- `handoffs/` - Short active continuity notes for the current discovery/design effort.
- `handoffs/session_handoff_2026-03-22_design_ready.md` - Latest active handoff into the Design phase.
- `legacy/README.md` - Index for archived MVP-era docs.
