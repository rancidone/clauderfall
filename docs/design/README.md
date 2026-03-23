---
title: Clauderfall Design Docs Index
doc_type: index
status: active
updated: 2026-03-22
summary: Canonical index for the active Clauderfall product and engine-level documentation set.
---

# Clauderfall Design Docs Index

This folder contains the active documentation set.

## Purpose

These docs define:

- the Clauderfall product brief
- the behavior expected from the Discovery engine
- the behavior expected from the Design engine
- the starting point for the active doc set, independent of the archived MVP docs

## Read Order

1. `clauderfall_product_brief.md`
2. `discovery_engine.md`
3. `design_engine.md`

## Files

- `clauderfall_product_brief.md` - Product brief for Clauderfall.
- `discovery_engine.md` - Discovery engine brief derived from the product brief.
- `design_engine.md` - Design engine brief derived from the product brief.
- `artifact_persistence_format.md` - Defines the physical persistence format for readable stage artifacts and their structured metadata.
- `artifact_checkpoint_semantics.md` - Defines artifact identity, flush checkpoints, and revision semantics for persisted artifacts.
- `artifact_checkpoint_metadata.md` - Defines the required metadata envelope recorded for each artifact checkpoint.
- `artifact_filesystem_layout.md` - Defines the on-disk layout for latest artifacts and immutable checkpoint history.
- `design_unit_artifact.md` - Defines the design-unit artifact shape for the Design stage.
- `design_unit_readiness.md` - Defines the semantics and rating criteria for design-unit readiness.
- `design_unit_document_shape.md` - Defines the recommended readable structure for a design unit document.
- `design_unit_sequencing.md` - Defines how the Design engine should choose and decompose design units.
- `design_review_workflow.md` - Defines the workflow from drafting through review and build-readiness approval.
- `design_session_flow.md` - Defines the end-to-end interaction flow for an active Design session.
- `discovery_design_handoff.md` - Defines the condensed handoff artifact between Discovery and Design.
- `design_discovery_reentry.md` - Defines when Design should resolve ambiguity locally versus return to Discovery.
