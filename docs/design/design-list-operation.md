# Design: design_list Operation

## Problem

`DesignRuntimeService` has no enumeration operation. The only way to read a design unit is by known `unit_id`. There is no way to retrieve all units for a project in a single call, which blocks any skill that needs to orient across the full design surface.

## Solution

Add a list path at three layers, each minimal.

### 1. `ArtifactStore.list_by_stage(stage: ArtifactStage) -> list[ArtifactRecord]`

New method on `ArtifactStore`. Single SQL query:

```sql
SELECT artifact_id, version_id, stage_metadata, updated_at
FROM artifacts
WHERE stage = ?
ORDER BY updated_at DESC
```

Returns a list of `ArtifactRecord`. No new types needed.

### 2. `StageArtifactRuntime.list_artifacts(stage: ArtifactStage) -> list[ArtifactRecord]`

Thin pass-through to `store.list_by_stage(stage)`. Consistent with the existing delegation pattern.

### 3. `DesignRuntimeService.list() -> ArtifactRuntimeResult`

Calls `self.artifacts.list_artifacts(ArtifactStage.DESIGN)`.

For each record, produces a compact unit summary:

```python
{
    "unit_id": artifact_id,
    "title": stage_metadata.get("title"),
    "status": stage_metadata.get("status"),
    "readiness": stage_metadata.get("readiness"),
    "updated_at": updated_at.isoformat(),
}
```

- Malformed sidecars (missing title, status, or readiness) are included with `"malformed": true` and a `warnings` entry — not silently dropped.
- Returns `ArtifactRuntimeResult` with `artifacts: {"units": [...], "count": N}`.
- Empty result (`count: 0, units: []`) is valid and not an error.

### 4. MCP tool `design_list`

New tool in `server.py`, no required parameters. Calls `design.list()` and returns the result directly. Sits alongside `design_read`, `design_write_draft`, and `design_accept`.

## Constraints

- List view is compact: `unit_id`, `title`, `status`, `readiness`, `updated_at` only.
- No linkage, no readiness_rationale, no markdown body.
- Ordering: `updated_at DESC` from the store. Grouping by status is the skill's responsibility, not the operation's.

## Tradeoffs

- Grouping is intentionally excluded from this operation. The skill owns presentation logic; the operation owns enumeration. This keeps `design_list` reusable for non-skill callers.
- `updated_at DESC` ordering from the store is a convenience default, not a contract. The skill re-sorts by status group anyway.
