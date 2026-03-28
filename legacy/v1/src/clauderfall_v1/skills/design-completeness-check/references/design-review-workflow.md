## Design Review Workflow Reference

Use this reference when deciding whether the artifact should continue, move to review, or be accepted.

Status and readiness are separate:

* `status` is workflow state
* `readiness` is build relevance

Useful workflow decisions:

* `continue`: keep working the current unit
* `move_to_review`: the unit is stable enough for explicit review
* `accept_not_buildable`: accepted as the current design record, but not ready to build from
* `accept_buildable`: accepted and concrete enough to treat as buildable

Review is justified when:

* the unit boundary is coherent
* the main design is visible and concrete
* readiness can be argued honestly
* remaining uncertainty is explicit rather than hidden
