---
title: Clauderfall Docs Index
doc_type: index
status: active
updated: 2026-03-22
summary: Top-level index for the fresh Clauderfall v2 documentation set and archived legacy material.
---

# Docs Index

This folder contains the active Clauderfall v2 documentation set.

## Structure

- `design/` - Active v2 product and engine-level discovery/design docs.
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

- `design/README.md` - Canonical index for the active v2 documentation set.
- `design/clauderfall_v2_product_brief.md` - Product brief for Clauderfall v2.
- `design/discovery_engine_v2.md` - Discovery engine brief derived from the v2 product brief.
- `handoffs/` - Short active continuity notes for the current v2 discovery effort.
- `legacy/README.md` - Index for archived MVP-era docs.
