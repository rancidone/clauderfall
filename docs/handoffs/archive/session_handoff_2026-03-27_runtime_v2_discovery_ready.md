---
title: Clauderfall Session Handoff 2026-03-27 Runtime V2 Discovery Ready
doc_type: handoff
status: active
updated: 2026-03-27
summary: Continuity note after moving v1 out of src, establishing the shared v2 runtime substrate and artifact runtime, and shipping the initial Discovery runtime with YAML-backed sidecars.
---

# Clauderfall Session Handoff 2026-03-27 Runtime V2 Discovery Ready

## Completed

- Moved the prior implementation out of active package space into:
  - [legacy/v1/README.md](/home/maddie/repos/clauderfall/legacy/v1/README.md)
  - [legacy/v1/src/clauderfall_v1/__init__.py](/home/maddie/repos/clauderfall/legacy/v1/src/clauderfall_v1/__init__.py)
  - [legacy/v1/tests/conftest.py](/home/maddie/repos/clauderfall/legacy/v1/tests/conftest.py)
- Kept active development space under:
  - [src/clauderfall/__init__.py](/home/maddie/repos/clauderfall/src/clauderfall/__init__.py)
  - [src/clauderfall/runtime/__init__.py](/home/maddie/repos/clauderfall/src/clauderfall/runtime/__init__.py)
- Completed the runtime skeleton feat:
  - [TODO_FEAT_RUNTIME_SKELETON.md](/home/maddie/repos/clauderfall/TODO_FEAT_RUNTIME_SKELETON.md)
- Completed the shared artifact runtime feat:
  - [TODO_FEAT_SHARED_ARTIFACT_RUNTIME.md](/home/maddie/repos/clauderfall/TODO_FEAT_SHARED_ARTIFACT_RUNTIME.md)
- Completed the Discovery runtime feat:
  - [TODO_FEAT_DISCOVERY_RUNTIME.md](/home/maddie/repos/clauderfall/TODO_FEAT_DISCOVERY_RUNTIME.md)
- Added the shared v2 runtime substrate and artifact-layer implementation:
  - [src/clauderfall/runtime/types.py](/home/maddie/repos/clauderfall/src/clauderfall/runtime/types.py)
  - [src/clauderfall/runtime/checkpoints.py](/home/maddie/repos/clauderfall/src/clauderfall/runtime/checkpoints.py)
  - [src/clauderfall/runtime/resolver.py](/home/maddie/repos/clauderfall/src/clauderfall/runtime/resolver.py)
  - [src/clauderfall/runtime/store.py](/home/maddie/repos/clauderfall/src/clauderfall/runtime/store.py)
  - [src/clauderfall/runtime/artifacts.py](/home/maddie/repos/clauderfall/src/clauderfall/runtime/artifacts.py)
  - [src/clauderfall/runtime/services.py](/home/maddie/repos/clauderfall/src/clauderfall/runtime/services.py)
  - [src/clauderfall/runtime/discovery.py](/home/maddie/repos/clauderfall/src/clauderfall/runtime/discovery.py)
- Replaced the temporary manual sidecar parsing path with real YAML serialization using `PyYAML` in:
  - [pyproject.toml](/home/maddie/repos/clauderfall/pyproject.toml)
  - [uv.lock](/home/maddie/repos/clauderfall/uv.lock)
- Added focused active-runtime coverage in:
  - [tests/test_runtime_skeleton.py](/home/maddie/repos/clauderfall/tests/test_runtime_skeleton.py)

## Current Truth

- The active implementation space is now cleanly separated from archived v1 code.
- The completed feat order is now:
  1. runtime skeleton
  2. shared artifact runtime
  3. Discovery runtime
- The next unfinished feat is:
  4. Design runtime
- The current v2 runtime already supports:
  - artifact refs and checkpoint envelopes
  - current and explicit checkpoint reads
  - immutable checkpoint writes plus current-pointer updates
  - shared artifact status transitions as later checkpoints
  - Discovery `read`, `write_draft`, and `to_design`
  - deterministic Design Start Context derivation from persisted Discovery state
- Sidecars are now persisted as actual YAML via `PyYAML`, not JSON text in a `.yaml` file.

## Important Constraints

- Keep treating `legacy/v1/` as archived reference, not as architectural truth for v2.
- Keep stage policy above the shared artifact runtime.
- Do not push Discovery-specific assumptions into the shared artifact layer.
- Keep `to_design` as a mechanical transition, not a second readiness judge.
- Keep reopening semantics as later checkpoints on the same artifact identity.
- Preserve the separation between Design artifact acceptance and later build approval.

## Suggested Next Step

- Implement [TODO_FEAT_DESIGN_RUNTIME.md](/home/maddie/repos/clauderfall/TODO_FEAT_DESIGN_RUNTIME.md).
- Read the Design runtime and review docs first, then add the smallest stage-specific service on top of the shared runtime:
  - `read`
  - `write_draft`
  - `to_review`
  - `accept`
- Keep the first slice focused on mechanical transition rules, short/full reads, and reopen-after-acceptance behavior.

## Verification

- `uv run pytest -q`
- Current result at handoff time: `10 passed`

## Key Docs

- [TODO.md](/home/maddie/repos/clauderfall/TODO.md)
- [TODO_FEAT_DESIGN_RUNTIME.md](/home/maddie/repos/clauderfall/TODO_FEAT_DESIGN_RUNTIME.md)
- [stage_runtime_mcp_pattern.md](/home/maddie/repos/clauderfall/docs/design/stage_runtime_mcp_pattern.md)
- [shared_stage_runtime_substrate.md](/home/maddie/repos/clauderfall/docs/design/shared_stage_runtime_substrate.md)
- [stage_artifact_runtime_interface.md](/home/maddie/repos/clauderfall/docs/design/stage_artifact_runtime_interface.md)
- [discovery_runtime_mcp_interface.md](/home/maddie/repos/clauderfall/docs/design/discovery_runtime_mcp_interface.md)
- [discovery_readiness_and_transition.md](/home/maddie/repos/clauderfall/docs/design/discovery_readiness_and_transition.md)
- [discovery_design_start_context.md](/home/maddie/repos/clauderfall/docs/design/discovery_design_start_context.md)
- [design_runtime_mcp_interface.md](/home/maddie/repos/clauderfall/docs/design/design_runtime_mcp_interface.md)
