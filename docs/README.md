---
title: Clauderfall - Docs Index
doc_type: index
status: active
updated: 2026-03-22
summary: Top-level index for Clauderfall documentation domains, implementation planning, and documentation conventions.
---

# Docs Index

This folder is the top-level index for Clauderfall documentation.

## Structure

- `design/` - Core product-design and architecture documents for the MVP.
- `handoffs/` - Session handoffs and short continuity notes.

## Standard Frontmatter

Core docs use the same frontmatter fields:

- `title` - Canonical document title.
- `doc_type` - Document role, such as `index`, `brief`, `engine`, `artifact-spec`, `contract`, `design`, or `future-state`.
- `status` - Lifecycle state. Use `active` unless explicitly superseded or deprecated.
- `updated` - Date of the last substantive edit in `YYYY-MM-DD` format.
- `summary` - One-line description of the document's purpose.

## Primary Entry Points

- `design/README.md` - Canonical index for the architecture and specification set.
- `design/implementation_strategy.md` - Implementation-facing decisions for the MVP codebase.
- `handoffs/` - Recent continuity notes.
