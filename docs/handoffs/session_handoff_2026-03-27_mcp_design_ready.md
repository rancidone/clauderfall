---
title: Clauderfall Session Handoff 2026-03-27 MCP Design Ready
doc_type: handoff
status: active
updated: 2026-03-27
summary: Continuity note after completing the v2 runtime feat sequence, adding the MCP adapter surface design, simplifying the TODO set to the MCP adapter feat, and preparing the repo for MCP implementation.
---

# Clauderfall Session Handoff 2026-03-27 MCP Design Ready

## Completed

- Completed the remaining v2 runtime feat work after the older runtime handoffs:
  - Design runtime with `read`, `write_draft`, `to_review`, and `accept`
  - session lifecycle runtime with startup view, active-thread read, handoff write, index rebuild, archive transition, and bounded recovery
- Added the new runtime implementation files:
  - [src/clauderfall/runtime/design.py](/home/maddie/repos/clauderfall/src/clauderfall/runtime/design.py)
  - [src/clauderfall/runtime/session_lifecycle.py](/home/maddie/repos/clauderfall/src/clauderfall/runtime/session_lifecycle.py)
- Extended the shared runtime surface and models in:
  - [src/clauderfall/runtime/types.py](/home/maddie/repos/clauderfall/src/clauderfall/runtime/types.py)
  - [src/clauderfall/runtime/services.py](/home/maddie/repos/clauderfall/src/clauderfall/runtime/services.py)
  - [src/clauderfall/runtime/__init__.py](/home/maddie/repos/clauderfall/src/clauderfall/runtime/__init__.py)
- Expanded runtime coverage in:
  - [tests/test_runtime_skeleton.py](/home/maddie/repos/clauderfall/tests/test_runtime_skeleton.py)
- Added a focused MCP adapter design unit:
  - [docs/design/mcp_adapter_surface.md](/home/maddie/repos/clauderfall/docs/design/mcp_adapter_surface.md)
- Updated the active docs indexes to include the MCP adapter design unit:
  - [docs/README.md](/home/maddie/repos/clauderfall/docs/README.md)
  - [docs/design/README.md](/home/maddie/repos/clauderfall/docs/design/README.md)
- Simplified the execution plan to the next real feat:
  - [TODO.md](/home/maddie/repos/clauderfall/TODO.md)
  - [TODO_FEAT_MCP_ADAPTER.md](/home/maddie/repos/clauderfall/TODO_FEAT_MCP_ADAPTER.md)
- Removed stale completed feat TODO docs so the root TODO set reflects current work instead of historical steps.

## Current Truth

- The planned v2 runtime feat sequence is complete:
  1. runtime skeleton
  2. shared artifact runtime
  3. Discovery runtime
  4. Design runtime
  5. session lifecycle runtime
- The next implementation target is the MCP adapter layer.
- The MCP-facing design ambiguity about naming and handler boundary is now resolved:
  - one MCP server
  - flat tool names such as `design_read`
  - thin handlers that validate input, call one runtime method, and map result shape
- The repo’s active TODO surface is now intentionally narrowed to the MCP adapter feat rather than keeping already-completed runtime feat files around.

## Important Constraints

- Keep runtime services as the only policy and invariant layer.
- Do not reintroduce raw file mutation as the primary MCP path.
- Keep MCP handlers thin:
  - validate input shape
  - call one runtime service method
  - map runtime result to MCP response shape
- Preserve the shared MCP top-level response shape:
  - `result`
  - `warnings`
  - `artifacts`
  - `metadata`
- Use flat tool names for the first MCP slice:
  - `discovery_read`
  - `design_read`
  - `read_recent_session_startup_view`
  - and the other tool names defined in the MCP adapter design doc

## Suggested Next Step

- Implement [TODO_FEAT_MCP_ADAPTER.md](/home/maddie/repos/clauderfall/TODO_FEAT_MCP_ADAPTER.md).
- Start with shared MCP adapter helpers for:
  - runtime-to-MCP result mapping
  - common response serialization
  - runtime service bootstrapping
- Then add the first thin tool handlers over the existing runtime services.

## Verification

- `uv run pytest -q`
- Current result at handoff time: `19 passed`

## Key Docs

- [TODO.md](/home/maddie/repos/clauderfall/TODO.md)
- [TODO_FEAT_MCP_ADAPTER.md](/home/maddie/repos/clauderfall/TODO_FEAT_MCP_ADAPTER.md)
- [docs/design/mcp_adapter_surface.md](/home/maddie/repos/clauderfall/docs/design/mcp_adapter_surface.md)
- [docs/design/stage_runtime_mcp_pattern.md](/home/maddie/repos/clauderfall/docs/design/stage_runtime_mcp_pattern.md)
- [docs/design/discovery_runtime_mcp_interface.md](/home/maddie/repos/clauderfall/docs/design/discovery_runtime_mcp_interface.md)
- [docs/design/design_runtime_mcp_interface.md](/home/maddie/repos/clauderfall/docs/design/design_runtime_mcp_interface.md)
- [docs/design/session_lifecycle_mcp_interface.md](/home/maddie/repos/clauderfall/docs/design/session_lifecycle_mcp_interface.md)
