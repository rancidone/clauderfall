# TODO FEAT: MCP Adapter

Goal: expose the current v2 runtime services through a thin MCP adapter surface with flat tool names and shared result mapping.

Read first:
- `docs/design/mcp_adapter_surface.md`
- `docs/design/discovery_runtime_mcp_interface.md`
- `docs/design/design_runtime_mcp_interface.md`
- `docs/design/session_lifecycle_mcp_interface.md`

TODO:
- implement one MCP server for the active `clauderfall` package
- add flat tool handlers for Discovery, Design, and session lifecycle operations
- keep handlers thin: validate inputs, call one runtime service method, map runtime result, return structured output
- centralize runtime-to-MCP result mapping from `ok` / `warning` / `error` to `success` / `warning` / `failure`
- preserve the shared top-level MCP response shape:
  - `result`
  - `warnings`
  - `artifacts`
  - `metadata`
- return readable artifact bodies only for the operations whose docs already expect full reads
- add tests for tool registration, result mapping, one stage read/write path, and one lifecycle path
