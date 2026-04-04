---
title: Artifact Deletion Control Surface
doc_type: design
status: ready
updated: 2026-04-03
summary: Defines the explicit operator-driven deletion surface for removing superseded or mistaken Discovery briefs and Design units from Clauderfall runtime state.
---

# Artifact Deletion Control Surface

## Purpose

This document defines the explicit control surface for deleting persisted stage artifacts from Clauderfall.

The goal is to keep runtime state aligned with explicit operator cleanup when a Discovery brief or Design unit should no longer exist as authoritative product state.

## Problem

Clauderfall currently supports:

- reading active artifacts
- writing new checkpoints
- transitioning workflow state

That is sufficient for ordinary drafting.

It is not sufficient for explicit cleanup of superseded or accidental artifacts.

Without a supported deletion surface, operators can remove Markdown files manually while leaving persisted sidecar state behind in runtime storage.

That creates divergence between:

- the filesystem view
- MCP-visible runtime state
- the underlying checkpoint store

## Design Position

Clauderfall should expose an explicit destructive deletion operation for stage artifacts.

This operation is exceptional.

It should exist only for operator-directed cleanup such as:

- removing superseded Discovery briefs
- removing mistaken Design units
- repairing runtime state after manual filesystem cleanup

Deletion is not part of normal Discovery or Design authoring flow.

## Scope

The first deletion surface should apply to:

- Discovery briefs
- Design units

Session lifecycle archival remains separate and should continue to use archive semantics rather than deletion semantics.

## MCP Surface

The first MCP slice should expose:

- `discovery_delete`
- `design_delete`

These names should stay stage-shaped and explicit.

## Runtime Shape

The shared stage-artifact runtime should expose one reusable backend operation:

- `delete_artifact`

Stage-specific services should wrap that shared operation in stage-shaped methods so the MCP layer does not need to construct raw artifact keys itself.

## Semantics

Deleting an artifact should remove all authoritative persisted state for that artifact:

- the current artifact record
- all persisted checkpoints for that artifact
- the current Markdown projection
- all checkpoint Markdown files for that artifact

After deletion:

- ordinary `read` should fail for that artifact id
- stage listing surfaces should no longer include that artifact
- no orphaned stage sidecar state should remain in runtime storage

## Explicitness Requirement

Deletion should be available only through an explicit operator-driven tool call.

Clauderfall skills should not treat deletion as a routine cleanup step during drafting.

## Idempotence

Deletion should be idempotent at the interface boundary.

If the target artifact no longer exists, the runtime should return a structured warning rather than failing with an internal error.

This keeps cleanup workflows safe to retry after partial manual edits.

## Why Deletion Instead Of Archive

Discovery and Design artifacts currently have checkpoint history, but they do not have a separate archived-state product surface comparable to session lifecycle.

Adding archive semantics here would not solve the immediate problem of orphaned authoritative sidecar state after manual removal.

The first implementation should therefore expose direct deletion for explicit cleanup.

If Clauderfall later needs recoverable archived artifact history, that should be introduced as a separate design decision rather than hidden behind a misleading delete-like surface.
