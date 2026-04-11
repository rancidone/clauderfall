---
title: Clauderfall Docs Index
doc_type: index
status: stable
updated: 2026-04-11
summary: Top-level index for the active Clauderfall v3 documentation set.
---

# Docs Index

This folder contains the active Clauderfall v3 documentation set.

## Structure

- `design/` - Active product and engine-level discovery/design docs.

## Standard Frontmatter

Core docs use the same frontmatter fields:

- `title` - Canonical document title.
- `doc_type` - Document role, such as `index`, `brief`, `engine-brief`, `design`, or `archive-index`.
- `status` - Document maturity state. Prefer `draft`, `ready`, or `stable` for active docs, and reserve `archived`, `superseded`, or `deprecated` for inactive docs.
- `updated` - Date of the last substantive edit in `YYYY-MM-DD` format.
- `summary` - One-line description of the document's purpose.

## Status Vocabulary

Use these values consistently:

- `draft` - Actively being shaped. The document is useful, but core structure or decisions may still change.
- `ready` - Ready for normal downstream use and review. The document is coherent enough that later work should not need to invent major decisions.
- `stable` - Mature and expected to change infrequently. Use this for settled reference docs and long-lived contracts.
- `archived` - Retained for historical reference, not current truth.
- `superseded` - Replaced by a newer canonical document.
- `deprecated` - Still present temporarily, but should not be used for new work.

## Primary Entry Points

- `design/README.md` - Canonical index for the active v3 documentation set.
- `design/clauderfall_product_brief.md` - Product brief for Clauderfall v3.
- `design/discovery_engine.md` - Discovery engine brief for Clauderfall v3.
- `design/design_engine.md` - Design engine brief for Clauderfall v3.
- `design/v3_workflow_memory.md` - Discovery brief for the v3 pivot toward markdown-first workflow memory, explicit skills, and compact session continuity.

## Notes

- The earlier v2 MCP- and sidecar-oriented design set has been removed so it does not conflict with the active v3 direction.
- The earlier v2 executable code surface was removed from the active tree in commit `9ac157f` and is retained only in git history.
- New design docs should be added back incrementally as the v3 workflow and skill contracts are designed.
