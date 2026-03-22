---
title: Clauderfall - Session Handoff 2026-03-22 Codex MCP Ready
doc_type: handoff
status: active
updated: 2026-03-22
summary: Handoff after adding portable skills, discovery drafting services, and a stdio JSON-RPC MCP server ready to register in Codex.
---

# Clauderfall - Session Handoff 2026-03-22 Codex MCP Ready

## Completed This Session

Implemented the first portable skill and the first real conversational runtime slice:

* packaged `discovery` skill with self-contained prompt instructions
* packaged skill reference docs local to the skill
* skill loader that resolves packaged resources rather than repo-only docs
* `DiscoveryDraftService` for:
  * session load/start
  * turn preparation
  * proposal review
  * revision save
  * provider-backed proposal interface

Implemented the next toolchain gaps:

* persisted version-qualified upstream artifact refs on Design, Task, and Context writes
* trace-link indexing table and query surface
* context assembly from persisted artifact ids and versions

Implemented MCP layers:

* thin in-process MCP tool adapter
* newline-delimited stdio JSON-RPC transport
* `clauderfall-mcp` entrypoint

## Current MCP Surface

The MCP tool adapter currently exposes:

* `artifact.validate`
* `artifact.get`
* `contract.check_handoff`
* `context.assemble_from_refs`
* `traceability.get_links`
* `discovery.start_session`
* `discovery.next_turn`
* `discovery.save_revision`

Transport methods currently supported by the stdio server:

* `initialize`
* `ping`
* `tools/list`
* `tools/call`
* `shutdown`
* `exit`

## Codex Registration

The intended first integration target is Codex.

Verified local Codex CLI registration command:

```bash
codex mcp add clauderfall -- clauderfall-mcp
```

For repo-local development from this checkout:

```bash
codex mcp add clauderfall -- /home/maddie/repos/clauderfall/.venv/bin/clauderfall-mcp
```

Helper script added:

```bash
./scripts/register_codex_mcp.sh clauderfall venv
```

Verification commands:

```bash
codex mcp list
codex mcp get clauderfall --json
```

Codex setup doc:

* `docs/codex_mcp.md`

## Test Status

Most recent verified command:

* `uv run pytest`

Most recent result:

* `81 passed`

Coverage added this session includes:

* skill loading
* discovery drafting service
* MCP tool adapter
* JSON-RPC stdio transport
* persisted trace-link querying
* context assembly from persisted refs

## Important Notes

The portable skill model is now established:

* skill prompt drives personality and conversation
* concrete contract references needed by the skill live under the skill package
* toolkit validation and persistence remain authoritative

The MCP payloads are still intentionally thin and tool-shaped.

If payload tightening happens next, it should be universal at the tool contract layer rather than Codex-specific.

## Main Remaining Gaps

The biggest remaining gaps from this point are:

* a real LLM-backed proposal provider instead of only the static/file-backed proposal contract
* a more universal result envelope across all MCP tools
* possible `artifact.list` support to match the earlier implementation strategy recommendation
* Design skill and Design drafting loop
* external client docs/examples beyond Codex registration

## Recommended Next Step

The next best step is to normalize MCP tool result envelopes before adding more tools.

Specifically:

1. define one result envelope shape for success, warnings, artifact refs, and review state
2. apply it across existing MCP tools
3. then add the first real model-backed proposal provider behind the existing `DiscoveryProposalProvider` interface

That keeps the external integration surface coherent before more capabilities get layered on top.

## Workspace Notes

* `docs/handoffs/` remains gitignored by design; this handoff is local continuity only.
* `.codex-home/` was created locally to inspect Codex MCP config behavior and should remain uncommitted.
