# Discovery Stub: Handoff Thread Management

## Problem

The handoff system has no skill surface and a minimal MCP surface. Currently there is no way for a user or LLM to:

- Query open threads interactively
- Archive or close threads from a skill
- Orient at session startup via a skill
- Manage thread lifecycle (create, update, archive) without direct MCP tool calls

The MCP tools that exist (`read_active_thread`, `read_recent_session_startup_view`, `write_active_thread_handoff`, `archive_completed_thread`) are functional but incomplete as a surface for both LLM-driven and user-driven thread management.

## Known Problem Areas

- No skill entry point for thread startup orientation
- No skill for listing, querying, or filtering open threads
- No skill for archiving or closing a thread
- MCP surface may be missing operations needed to support the above

## What Needs to be Explored

- What does "better interface" mean concretely — which workflows are painful today?
- What should startup orientation look like as a skill vs. automatic behavior?
- What thread management operations belong on the MCP surface vs. the skill surface?
- What does cleanup mean — archiving stale threads, bulk close, something else?

## Next

Full Discovery interview needed to frame the problem areas, constraints, and intended outcomes before Design can start.
