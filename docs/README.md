---
status: stable
last_updated: 2026-04-11
---

# Docs Index

This folder contains the active Clauderfall v3 documentation set.

## Structure

- `design/` - Active product and engine-level design docs.
- `discovery/` - Active Discovery briefs.

## Standard Frontmatter

Active docs use a minimal shared frontmatter shape:

- `status` - Document maturity state. Prefer `draft`, `ready`, or `stable` for active docs, and reserve `archived`, `superseded`, or `deprecated` for inactive docs.
- `last_updated` - Date of the last substantive edit in `YYYY-MM-DD` format.
- `parents` - Optional ordered list of related document paths for docs that explicitly participate in a parent-child design or discovery relationship.

Document role, title, and summary are inferred from folder structure and document content rather than duplicated in frontmatter.

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
- `design/handoff.md` - Design for the Clauderfall Handoff skill.
- `design/continue.md` - Design for the Clauderfall Continue skill.
- `discovery/clauderfall_system.md` - Top-level Discovery brief for the Clauderfall v3 system.
- `discovery/session_continuity.md` - Discovery brief for explicit handoff and continue workflows across long-running work.
- `discovery/document_maintenance.md` - Discovery brief for an operator-invoked document maintenance skill over the canonical docs set.

## Notes

- New design docs should be added back incrementally as the v3 workflow and skill contracts are designed.
