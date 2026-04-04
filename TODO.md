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

Current feat: Close out the Discovery/Design artifact storage cutover and choose the next implementation target.

Next slice:

1. Decide whether active docs need a small clarification pass after the cutover.
- Focus only on docs that still imply DB-shaped runtime semantics for Discovery/Design artifacts.
- Do not churn docs if the implementation already matches active design truth closely enough.

2. Decide whether to remove temporary compatibility aliases from artifact deletion metadata.
- Current runtime code now prefers filesystem-shaped deletion metadata.
- Old DB-shaped alias keys still exist for compatibility and should be removed only when no longer needed.

3. Replace this closeout feat with the next real implementation target once the doc/cleanup decision is made.
- Keep `TODO.md` aligned with the repo’s actual remaining work.

Bug notes:
- Discovery write path validation was tightened in runtime validation/error reporting.
- If normal skill usage still produces avoidable shape errors, inspect skill guidance before changing the MCP contract.

Completed:
- runtime skeleton
- shared artifact runtime
- Discovery runtime
- Design runtime
- session lifecycle runtime
- session storage cutover to markdown/yaml artifacts
- MCP adapter (implementation complete; tests pending)
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
- artifact deletion metadata shifted toward filesystem-shaped semantics, with temporary DB-shaped compatibility aliases retained
- checkpoint metadata coverage added for:
  - `created_at`
  - `flush_reason`
  - `is_current`
  - current-checkpoint flip after later writes
- current full-suite verification status:
  - `73 passed, 7 skipped`
