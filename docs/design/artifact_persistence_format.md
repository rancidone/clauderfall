---
title: Clauderfall Artifact Persistence Format
doc_type: design
status: stable
updated: 2026-03-22
summary: Defines the physical persisted format for readable Discovery and Design artifacts plus their structured metadata.
---

# Clauderfall Artifact Persistence Format

## Purpose

This document defines the default physical persistence format for Clauderfall stage artifacts.

The goal is to keep artifacts readable-first while still making their structured metadata dependable for sequencing, review, and later machine use.

## Design Position

Clauderfall should persist each stage artifact as a paired document:

- one canonical readable Markdown document
- one adjacent machine-readable YAML metadata file

These two files are one logical artifact.

The Markdown document is primary for human review and understanding.

The YAML file is primary for structured fields that should not be recovered heuristically from prose.

This keeps the product document-first without forcing large nested structure into the readable artifact body.

## Why Not Frontmatter-Only

A frontmatter-only approach is attractive for small metadata, but it breaks down for the current artifact shapes.

Design Start Context artifacts and design units already need structured fields that can become nested enough to make frontmatter noisy, long, and unpleasant to review.

Large inline metadata blocks also weaken the lazy-load behavior the active docs rely on, because the reader must often scan through structure before reaching the document itself.

For the current product boundary, an adjacent sidecar is the cleaner default.

## Canonical Pairing Rule

The default persisted form should use a shared basename:

- `<artifact_name>.md`
- `<artifact_name>.meta.yaml`

Example:

- `design-unit-auth-session.md`
- `design-unit-auth-session.meta.yaml`

The exact directory layout can vary by stage or implementation, but the pairing must be obvious from filenames alone.

## Markdown Document

The Markdown document should remain the canonical readable artifact.

It should contain the human-facing content already defined by the relevant stage docs:

- Discovery brief narrative
- Design Start Context narrative
- design-unit design document

The document may use a short frontmatter header for fast document loading when useful, but that frontmatter should stay intentionally small.

If a field is mirrored in both frontmatter and the sidecar, the sidecar remains authoritative for structured machine use.

The body should not embed large YAML or JSON sections just to satisfy persistence needs.

## YAML Sidecar

The sidecar should contain the structured fields defined by the relevant artifact-shape doc.

This includes fields such as:

- stable artifact identity
- workflow status
- readiness signals
- dependency or decomposition links
- structured assumptions and open questions
- Design Start Context indexes and references

The sidecar should stay limited to fields that materially improve downstream reliability.

It should not become a second prose document.

## Applicability By Artifact Type

This paired-file format should be the default for the current artifact types in scope:

- Discovery brief
- Design Start Context
- design unit

The stage-specific docs still define each artifact's logical shape.

This document only settles the physical persisted form.

## Flush And Update Rule

During an active session, the working artifact may live in session state.

At a flush checkpoint, the system should write both members of the artifact pair together as one persistence action.

The product should avoid persisting every tiny turn, but once a flush happens, the readable document and sidecar should represent the same checkpoint.

If a write only partially succeeds, the checkpoint should be treated as incomplete rather than silently accepting drift between the two files.

The checkpoint and revision semantics for those flushes are defined separately in `artifact_checkpoint_semantics.md`.

The default on-disk layout for current artifacts and historical checkpoints is defined separately in `artifact_filesystem_layout.md`.

## Reviewability Rule

An engineer should be able to review the artifact's meaning by reading the Markdown document alone.

An engine should be able to answer identity, status, sequencing, and readiness questions by consulting the sidecar alone.

If either statement stops being true, the artifact has drifted out of balance.

## Rejected Alternatives

## Single Markdown File With Large Frontmatter

Rejected because it makes structured artifacts harder to read and maintain as metadata grows.

## Pure Sidecar Persistence Without A Canonical Readable Document

Rejected because it undermines the core product promise that the artifact itself should be directly reviewable by a senior engineer.

## Format-Specific Database Rows As The Canonical Artifact

Rejected for the current design phase because the product truth is the readable artifact plus its explicit structured side, not an internal storage projection.

## Open Questions

This decision does not yet settle:

- whether mirrored Markdown frontmatter should be mandatory or optional
- whether later stages need attachments beyond the document-plus-sidecar pair

Those questions can be addressed later without changing the document-first persistence direction established here.
