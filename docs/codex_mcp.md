---
title: Clauderfall Codex MCP Setup
doc_type: guide
status: active
updated: 2026-03-22
summary: How to register the Clauderfall stdio MCP server with Codex for repo-local or user-level installs.
---

# Clauderfall Codex MCP Setup

Clauderfall exposes a stdio MCP server through the `clauderfall-mcp` command.

Codex can register that server directly with:

```bash
codex mcp add clauderfall -- clauderfall-mcp
```

For a repo-local virtualenv install, use the concrete path instead:

```bash
codex mcp add clauderfall -- /absolute/path/to/repo/.venv/bin/clauderfall-mcp
```

## Stored Config Shape

I verified the stored Codex config shape locally with `codex mcp add` and `codex mcp get --json`.

The resulting `~/.codex/config.toml` entry is:

```toml
[mcp_servers.clauderfall]
command = "clauderfall-mcp"
```

For a repo-local virtualenv:

```toml
[mcp_servers.clauderfall]
command = "/absolute/path/to/repo/.venv/bin/clauderfall-mcp"
```

## Recommended Registration Paths

User-level install:

* install Clauderfall so `clauderfall-mcp` is on `PATH`
* run `codex mcp add clauderfall -- clauderfall-mcp`

Repo-local development:

* create the local `.venv`
* install Clauderfall into that environment
* run `codex mcp add clauderfall -- /absolute/path/to/repo/.venv/bin/clauderfall-mcp`

## Verification

Check the server registration:

```bash
codex mcp list
codex mcp get clauderfall --json
```

The transport should be `stdio` and the command should point to the intended `clauderfall-mcp` binary.

## Notes

The Clauderfall MCP surface is intentionally thin and tool-oriented.

It currently exposes deterministic artifact operations plus the Discovery conversational loop helpers:

* `artifact.validate`
* `artifact.get`
* `contract.check_handoff`
* `context.assemble_from_refs`
* `traceability.get_links`
* `discovery.start_session`
* `discovery.prepare_turn`
* `discovery.propose_revision`
* `discovery.save_revision`
