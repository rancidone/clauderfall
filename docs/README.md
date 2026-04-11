---
title: Clauderfall Docs Index
status: stable
last_updated: 2026-04-11
summary: Top-level index for the active Clauderfall v3 documentation set.
---

# Docs Index

This folder contains the active Clauderfall v3 documentation set.

## Structure

- `design/` - Active product and engine-level design docs.
- `discovery/` - Active Discovery briefs.

## Standard Frontmatter

Core docs use the same frontmatter fields:

- `title` - Canonical document title.
- `status` - Document maturity state. Prefer `draft`, `ready`, or `stable` for active docs, and reserve `archived`, `superseded`, or `deprecated` for inactive docs.
- `last_updated` - Date of the last substantive edit in `YYYY-MM-DD` format.
- `summary` - One-line description of the document's purpose.

Document role is inferred from folder structure and document content rather than a dedicated frontmatter field.

## Status Vocabulary

Use these values consistently:

- `draft` - Actively being shaped. The document is useful, but core structure or decisions may still change.
- `ready` - Ready for normal downstream use and review. The document is coherent enough that later work should not need to invent major decisions.
- `stable` - Mature and expected to change infrequently. Use this for settled reference docs and long-lived contracts.
- `archived` - Retained for historical reference, not current truth.
- `superseded` - Replaced by a newer canonical document.
- `deprecated` - Still present temporarily, but should not be used for new work.

## Primary Entry Points

- `design/README.md` - Canonical index for the active v3 design documentation set.
- `discovery/README.md` - Canonical index for the active v3 Discovery briefs.
- `discovery/clauderfall_product.md` - Top-level product discovery brief for Clauderfall v3.
- `design/discovery_skill.md` - Design for the Clauderfall Discovery skill.
- `design/design_skill.md` - Design for the Clauderfall Design skill.
- `discovery/clauderfall_system.md` - Top-level Discovery brief for the Clauderfall v3 system.
- `discovery/session_continuity.md` - Discovery brief for explicit handoff and continue workflows across long-running work.
- `discovery/document_maintenance.md` - Discovery brief for an operator-invoked document maintenance skill over the canonical docs set.

## Notes

- New design docs should be added back incrementally as the v3 workflow and skill contracts are designed.
