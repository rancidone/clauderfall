# TODO FEAT: Runtime Skeleton

Goal: create a clean v2 runtime spine without letting the existing v1 implementation define the architecture.

Read first:
- `docs/design/stage_runtime_mcp_pattern.md`
- `docs/design/shared_stage_runtime_substrate.md`
- `docs/design/artifact_persistence_format.md`
- `docs/design/artifact_checkpoint_semantics.md`

TODONE:
- define the v2 module boundaries for substrate, artifact runtime, stage services, and MCP adapters
- treat the current `src/` implementation as v1 reference only unless a specific piece is intentionally reused
- introduce shared v2 runtime result types, artifact reference types, and status vocabulary
- create the first v2 skeleton for store, checkpoint manager, artifact resolver, and service wiring
- keep the new runtime isolated enough that we can migrate incrementally without forcing v1 compatibility into v2 APIs
- add focused tests for the new v2 foundation contracts
