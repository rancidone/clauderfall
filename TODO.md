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

Current feat: Remove SQLite as the authoritative substrate for Discovery and Design artifacts.

Next slice:

1. Ground the substrate cutover in the active storage docs.
- Read:
  - `docs/discovery/session-state-and-storage-rediscovery.md`
  - `docs/design/artifact_persistence_format.md`
  - `docs/design/artifact_filesystem_layout.md`
  - `docs/design/artifact_checkpoint_semantics.md`
  - `docs/design/artifact_checkpoint_metadata.md`
- Confirm the runtime target is paired Markdown plus YAML with filesystem checkpoint history, not SQLite-backed metadata plus loose Markdown.

2. Design the shared filesystem-backed artifact store shape.
- Replace the current `artifacts` and `artifact_checkpoints` SQLite authority with repo-native artifact directories.
- Keep the current logical contract:
  - current artifact
  - immutable checkpoints
  - structured metadata adjacent to readable Markdown
- Avoid a second migration-only abstraction if the final runtime shape is already clear.

3. Refactor `ArtifactStore` and `StageArtifactRuntime`.
- Remove SQLite authority from:
  - `src/clauderfall/runtime/store.py`
  - `src/clauderfall/runtime/artifacts.py`
- Rebuild read/write/checkpoint/delete behavior on filesystem artifact pairs.
- Preserve current stage-level runtime behavior for Discovery and Design while changing only the persistence substrate.

4. Migrate Discovery and Design artifact persistence.
- Persist current artifact state under the documented filesystem layout.
- Persist immutable checkpoints under the documented checkpoint layout.
- Keep short reads and full reads stable at the MCP boundary if possible.
- Preserve existing validation and transition semantics while changing storage.

5. Add a deliberate migration path from SQLite-backed artifact metadata.
- Read existing `artifacts` / `artifact_checkpoints` rows.
- Materialize filesystem-backed current artifacts and checkpoint history.
- Stop treating SQLite rows as authoritative after migration.
- Keep any fallback import-only and temporary.

6. Update tests around filesystem authority.
- Replace DB-oriented artifact assertions with filesystem assertions.
- Add coverage for:
  - current artifact pair creation
  - checkpoint history creation
  - checkpoint reads
  - delete behavior
  - migration from legacy SQLite-backed artifact metadata

7. Update active docs if implementation changes active design truth.
- Keep the storage story consistent across runtime, MCP, skills, and docs.

Bug notes:
- Discovery write path: `discovery_write_draft` sidecar validation is too easy to violate during normal use. Investigate whether the fix belongs in MCP contract shape, validation error ergonomics, schema design, or discovery skill guidance.

Completed:
- runtime skeleton
- shared artifact runtime
- Discovery runtime
- Design runtime
- session lifecycle runtime
- session storage cutover to markdown/yaml artifacts
- MCP adapter (implementation complete; tests pending)
