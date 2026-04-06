# Discovery Stub: Session Continuity Management

## Problem

The handoff system now has an initial packaged skill surface and a minimal MCP surface, but the overall session-continuity management experience is still incomplete.

Current gaps still include:

- querying archived continuity records beyond the compact startup view
- filtering or searching archived continuity records interactively
- managing lifecycle cleanup from a richer skill surface
- handling current-state replacement and archive choices more explicitly than write-time overwrite

The current MCP tools (`session_read_startup_view`, `session_read_current`, `session_write_handoff`, `session_archive_current`) are functional but still incomplete as a surface for both LLM-driven and user-driven session continuity management.

## Known Problem Areas

- No list/query/filter tool for archived continuity records beyond startup orientation
- No richer explicit overwrite/archive decision support around replacing current state
- No richer management surface for listing, filtering, or bulk cleanup
- MCP surface may be missing operations needed to support the above

## What Needs to be Explored

- What does "better interface" mean concretely — which workflows are painful today?
- What should startup orientation look like as a skill vs. automatic behavior?
- What session continuity management operations belong on the MCP surface vs. the skill surface?
- What does cleanup mean — archiving stale current state, browsing history, bulk close, something else?

## Next

Full Discovery interview needed to frame the problem areas, constraints, and intended outcomes before Design can start.
