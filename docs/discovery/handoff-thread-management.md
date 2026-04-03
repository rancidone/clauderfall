# Discovery Stub: Handoff Thread Management

## Problem

The handoff system now has an initial packaged skill surface and a minimal MCP surface, but the overall thread-management experience is still incomplete.

Current gaps still include:

- querying open threads beyond the compact startup view
- filtering or searching active threads interactively
- managing lifecycle cleanup from a richer skill surface
- handling new-thread identity more explicitly than write-time upsert

The current MCP tools (`session_read_thread`, `session_read_startup_view`, `session_write_handoff`, `session_archive_thread`) are functional but still incomplete as a surface for both LLM-driven and user-driven thread management.

## Known Problem Areas

- No list/query/filter tool for open threads beyond startup orientation
- No explicit create-thread primitive or stronger thread identity flow
- No richer management surface for listing, filtering, or bulk cleanup
- MCP surface may be missing operations needed to support the above

## What Needs to be Explored

- What does "better interface" mean concretely — which workflows are painful today?
- What should startup orientation look like as a skill vs. automatic behavior?
- What thread management operations belong on the MCP surface vs. the skill surface?
- What does cleanup mean — archiving stale threads, bulk close, something else?

## Next

Full Discovery interview needed to frame the problem areas, constraints, and intended outcomes before Design can start.
