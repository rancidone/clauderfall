# TODO FEAT: Design Runtime

Goal: ship the Design runtime surface with explicit review and acceptance transitions.

Read first:
- `docs/design/design_runtime_mcp_interface.md`
- `docs/design/design_review_workflow.md`
- `docs/design/design_unit_readiness.md`

TODO:
- implement a v2 Design service with `read`, `write_draft`, `to_review`, and `accept`
- support short and full reads with workflow status, readiness, rationale, scope summary, and linkage metadata
- make `write_draft` persist `draft` and `in_review` revisions without silently accepting the artifact
- make `to_review` and `accept` enforce only the mechanical transition rules, including documented override paths
- preserve the rule that reopening is just a later checkpoint written back into `draft`
- add tests for review transition, acceptance, draft override acceptance, and reopen-after-acceptance
