---
title: Clauderfall - Persistence Semantics
doc_type: design
status: active
updated: 2026-03-22
summary: Canonical MVP persistence semantics for artifact identity, versioning, mutability, and retrieval.
---

# Clauderfall - Persistence Semantics

## 1. Purpose

This document defines how Clauderfall persists artifacts during the MVP.

It answers the implementation question left open by the handoff:

* what persistence semantics apply to durable artifacts

This document is authoritative for:

* artifact identity
* versioning
* mutability rules
* retrieval rules
* minimal relational metadata required for auditability

It stays inside the MVP boundary and does not define persistence for deferred execution, validation, or harvest systems.

---

## 2. Core Decision

Artifacts are persisted as **append-only, versioned records**.

The system MUST NOT silently mutate the canonical body of an already persisted artifact version.

Rationale:

* the system is artifact-driven and auditable
* the boundary contracts require explicit updated artifacts after backflow resolution
* downstream consumers must be able to trace exactly what upstream artifact version they used
* append-only persistence preserves historical reasoning state without relying on session memory

---

## 3. Artifact Identity Model

Each persisted artifact has two identities:

### 3.1 Logical Artifact Identity

`artifact_id` identifies the durable artifact lineage.

Examples:

* one Discovery Artifact lineage for a problem framing
* one Design Artifact lineage for a solution definition
* one Task Artifact lineage for a bounded work contract

`artifact_id` stays stable across revisions of the same logical artifact.

### 3.2 Artifact Version Identity

`version` identifies a specific persisted revision within an `artifact_id` lineage.

The tuple:

* `artifact_id`
* `version`

is the canonical identity of a persisted artifact record.

No two persisted records may share the same tuple.

---

## 4. Version Semantics

## 4.1 Monotonic Versioning

Versions MUST start at `1` and increase by `1` within a lineage.

The MVP does not support sparse or out-of-order version insertion.

Examples:

* valid: `1`, `2`, `3`
* invalid: `1`, `3`
* invalid: `2` as the first version

## 4.2 Append-Only Writes

Persisting a new revision creates a new row.

Persisting version `N + 1` MUST NOT overwrite version `N`.

## 4.3 Latest Version

The latest version of an artifact is the highest persisted version number for that `artifact_id`.

The MVP should derive latest-ness from version ordering, not from a mutable pointer column.

This avoids introducing a second source of truth for what counts as current.

---

## 5. Mutability Rules

## 5.1 Immutable Artifact Bodies

Once persisted, an artifact record's canonical `body_json` is immutable.

If the artifact content changes, the system MUST write a new version.

## 5.2 No Silent Replacement

Operations named `save`, `persist`, or `create_version` MUST create a new version or reject the request.

They MUST NOT behave as implicit upserts on canonical artifact bodies.

## 5.3 Deletion

The MVP should not support hard deletion of persisted artifact versions through normal application flows.

If deletion is ever needed for operational reasons, it should remain an explicit maintenance action outside normal engine behavior.

---

## 6. Read Semantics

## 6.1 Exact-Version Reads

The persistence layer MUST support loading a specific `(artifact_id, version)`.

This is the authoritative read mode for:

* traceability
* audit
* handoff reconstruction
* debugging

## 6.2 Latest-Version Reads

The persistence layer SHOULD support loading the latest version for an `artifact_id`.

This is a convenience read mode for operator workflows and local development.

It MUST resolve to the highest existing version, not to a mutable status flag.

## 6.3 Missing Reads

If the requested artifact lineage or version does not exist, the repository should return `None` or an equivalent absence result.

It should not synthesize a placeholder artifact.

---

## 7. Write Semantics

## 7.1 Initial Write

The first persisted record for an `artifact_id` MUST be version `1`.

## 7.2 Subsequent Writes

A new write for an existing lineage MUST be version `current_latest + 1`.

The repository MAY assign this version automatically.

If the caller provides an explicit version, it MUST match the next valid version number or the write must be rejected.

## 7.3 Kind Stability

`artifact_kind` is immutable within an artifact lineage.

An `artifact_id` used for a Discovery Artifact MUST NOT later be reused for a Design Artifact or any other kind.

## 7.4 Metadata Snapshot

Each persisted version stores a metadata snapshot alongside `body_json`, including:

* `artifact_kind`
* `version`
* `readiness_state`
* creation timestamp
* upstream artifact references when applicable

This metadata is an index over the canonical body, not a replacement for it.

---

## 8. Upstream Reference Semantics

When an artifact is derived from upstream artifacts, persistence should record explicit upstream version references.

The MVP should store these references as version-qualified lineage references, not only bare artifact ids.

Examples:

* `discovery:disc-1@2`
* `design:des-4@1`

This is necessary because:

* Design must be traceable to the exact Discovery Artifact version it consumed
* Task must be traceable to the exact Design Artifact version it consumed
* Context Packet assembly must be traceable to exact Task and support artifact versions

Bare `artifact_id` references are insufficient for auditability.

---

## 9. Recommended MVP Table Semantics

## 9.1 `artifacts`

The canonical `artifacts` table should represent one row per persisted artifact version.

Recommended key properties:

* composite primary key on `artifact_id` and `version`
* no mutable latest pointer required
* `body_json` stores the full canonical artifact body
* upstream references are stored as version-qualified strings or structured JSON

## 9.2 `trace_links`

`trace_links` may index edges for queryability, but it does not replace version-qualified upstream references on the artifact record itself.

## 9.3 `engine_runs`

`engine_runs` should reference exact artifact versions where possible.

Run history is operational metadata and must not be treated as the canonical artifact store.

---

## 10. Repository API Implications

The MVP repository API should reflect append-only semantics directly.

Prefer operations such as:

* `create`
* `create_next_version`
* `get_version`
* `get_latest`
* `list_versions`

Avoid ambiguous operations such as:

* `upsert`

`upsert` is a poor fit because it implies silent replacement semantics that conflict with auditability.

---

## 11. Contract Implications

The contract docs already require updated artifacts after backflow resolution.

Persistence semantics make that operationally concrete:

* resolving a blocker produces a new artifact version
* downstream engines should consume the updated version explicitly
* historical blocked versions remain available for audit and debugging

This behavior is consistent with:

* `discovery_design_contract.md`
* `design_task_contract.md`
* `task_context_contract.md`

---

## 12. MVP Non-Goals

The MVP does not need:

* branching artifact histories
* merge semantics between competing versions
* soft-delete lifecycle workflows
* cross-project multi-tenant storage semantics
* distributed database coordination

Those can be introduced later if real usage requires them.
