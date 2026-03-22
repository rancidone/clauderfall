## Discovery Toolchain Workflow

Use Clauderfall as the durable artifact toolchain.

Core principle:

* conversational turns refine understanding
* persisted discovery artifacts carry state across turns and sessions

Recommended flow:

1. Load the current artifact lineage if it exists.
2. Draft a candidate discovery revision from the latest user turn.
3. Validate it through the toolkit.
4. Check Discovery-to-Design handoff readiness.
5. Persist a new append-only version only when the revision is intentionally accepted.

CLI-oriented commands:

* `validate-discovery`
* `save-discovery`
* `check-discovery-handoff`

Persistence rules:

* artifact versions are append-only
* `(artifact_id, version)` is the durable identity
* later stages should consume exact versions when traceability matters

Conversation rules:

* ask the smallest targeted question that resolves the most important blocker
* if the artifact is not ready, say why directly
* do not pretend uncertainty is resolved
* do not move into design just because the conversation feels productive
