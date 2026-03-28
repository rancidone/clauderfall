# TODO FEAT: Discovery Runtime

Goal: ship the minimal Discovery runtime surface on top of the shared artifact runtime.

Read first:
- `docs/design/discovery_runtime_mcp_interface.md`
- `docs/design/discovery_readiness_and_transition.md`
- `docs/design/design_start_context_generation.md`

TODONE:
- implement a v2 Discovery service with `read`, `write_draft`, and `to_design`
- make `read` support short and full views over authoritative persisted state
- make `write_draft` persist Discovery status, readiness, rationale, and the readable brief body as one checkpointed state update
- make `to_design` enforce only mechanical handoff preconditions, including the explicit override path from `draft`
- create the Design start-context derivation where it best fits the v2 implementation boundary
- add tests covering normal handoff, blocked handoff, and override handoff behavior
