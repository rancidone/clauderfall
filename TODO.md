# TODO

Process feats in order, one at a time.

For the current feat:
- read the referenced docs first
- inspect the existing code before editing
- implement the smallest end-to-end slice that satisfies the feat
- add or update tests with the code changes
- update docs only if implementation changes active design truth
- treat the existing implementation as v1 reference unless the feat explicitly chooses to reuse part of it
- stop and surface any real design gap that blocks implementation; do not invent missing design
- stop, summarize progress, and hand off when remaining context reaches about 60%

Current feat: Replace session lifecycle active-thread continuity with the single-current carry-forward model defined in the updated session docs.

Next slice:

1. Remove or archive superseded active-thread assumptions after implementation lands.
- Review runtime comments, helper names, and any remaining compatibility wording to ensure the normal surface is consistently single-current.
- Decide whether `thread_markdown` should remain the persisted field name or be renamed in a later cleanup slice.
- Keep `TODO.md` aligned with the repo’s actual remaining work.

Bug notes:
- Discovery and Design MCP validation now gives clearer errors for stringified object or array fields.
- Session continuity docs changed materially on 2026-04-05: active threads were superseded by a single-current carry-forward model. Runtime, MCP, packaged skills, and core tests now match the new surface.

Completed:
- runtime skeleton
- shared artifact runtime
- Discovery runtime
- Design runtime
- session storage cutover to markdown/yaml artifacts
- storage docs reviewed for artifact cutover target:
  - `docs/discovery/session-state-and-storage-rediscovery.md`
  - `docs/design/artifact_persistence_format.md`
  - `docs/design/artifact_filesystem_layout.md`
  - `docs/design/artifact_checkpoint_semantics.md`
  - `docs/design/artifact_checkpoint_metadata.md`
- `ArtifactStore` refactored to use filesystem-backed current artifacts and checkpoint history
- Discovery and Design artifact persistence moved to paired Markdown plus YAML files under the documented filesystem layout
- legacy artifact migration added from SQLite-backed `artifacts` / `artifact_checkpoints` rows into filesystem authority
- migration edge cases covered:
  - legacy stage directories no longer suppress migration incorrectly
  - legacy current rows without checkpoint-history rows still materialize correctly
- filesystem-authority tests added and updated for:
  - current artifact pair creation
  - checkpoint history creation
  - checkpoint reads
  - delete behavior
  - migration from legacy SQLite-backed artifact metadata
- stale DB-oriented session assertions removed from runtime tests
- Discovery write validation hardened for nested sidecar shape errors, with clearer runtime/MCP failure detail
- Design and session handoff validation hardened for stringified payload-shape errors
- artifact deletion metadata shifted toward filesystem-shaped semantics, with temporary DB-shaped compatibility aliases retained
- checkpoint metadata coverage added for:
  - `created_at`
  - `flush_reason`
  - `is_current`
  - current-checkpoint flip after later writes
- session lifecycle docs rewritten for the single-current carry-forward model:
  - `docs/design/session_lifecycle.md`
  - `docs/design/session_recent_state_artifact.md`
  - `docs/design/session_handoff_write_update_flow.md`
  - `docs/design/session_start_drill_in_flow.md`
  - `docs/design/session_archive_transition_mechanics.md`
  - `docs/design/session_lifecycle_runtime_interface.md`
  - `docs/design/session_lifecycle_mcp_interface.md`
  - `docs/design/session_continuity_skill_surface.md`
  - `docs/design/session_lifecycle_backend_service.md`
  - `docs/design/session_lifecycle_operation_runner.md`
- session lifecycle runtime surface replaced with the single-current model:
  - one current carry-forward record under `session/current`
  - archived history under `session/history`
  - startup projection rebuilt from current plus recent completed history
- session lifecycle MCP surface replaced:
  - `session_read_thread` -> `session_read_current`
  - `session_archive_thread` -> `session_archive_current`
  - `session_write_handoff` no longer takes `thread_id`
- packaged session continuity skills updated to stop reasoning about multiple active threads or thread identity
- session runtime and MCP tests updated for current/history startup semantics and new tool names
