# TODO FEAT: Session Lifecycle Runtime

Goal: implement recent-session lifecycle operations and bounded recovery on the same v2 runtime substrate.

Read first:
- `docs/design/session_recent_state_artifact.md`
- `docs/design/session_lifecycle_runtime_interface.md`
- `docs/design/session_lifecycle_backend_service.md`
- `docs/design/session_lifecycle_operation_runner.md`

TODO:
- implement the recent-session artifact models and persistence shape needed for repo index, active threads, and archived history
- implement the lifecycle service methods for startup view, active-thread read, handoff write, index rebuild, and archive transition
- add a bounded operation runner for multi-step execute, verify, and recover flows where lifecycle invariants need it
- keep the repo index as a deterministic projection of authoritative thread metadata rather than a second editable source of truth
- enforce the strict active-versus-history boundary during archive transitions
- add tests for startup rebuild, handoff projection refresh, successful archive, and recoverable partial-failure paths
