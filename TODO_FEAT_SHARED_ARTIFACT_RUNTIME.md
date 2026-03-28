# TODO FEAT: Shared Artifact Runtime

Goal: implement the shared artifact-level runtime beneath stage-specific services.

Read first:
- `docs/design/stage_artifact_runtime_interface.md`
- `docs/design/shared_stage_runtime_substrate.md`
- `docs/design/stage_runtime_mcp_pattern.md`

TODO:
- implement shared v2 operations for `read_artifact`, `write_artifact_checkpoint`, and `transition_artifact_status`
- support current-checkpoint lookup plus explicit checkpoint reads
- make checkpoint writes durable and structured rather than stage-specific ad hoc saves
- standardize the shared result envelope: `result`, `warnings`, `artifacts`, `metadata`
- keep stage policy out of this layer; this code should execute decisions, not make them
- add tests that prove checkpoint creation, current-pointer updates, and reopen-via-later-checkpoint behavior
