## Discovery Artifact Contract

Use this reference when you need the concrete Discovery rules without relying on repository design docs.

Required sections:

* `problem_definition`
* `constraints`
* `success_criteria`
* `scope_boundaries`
* `risks`
* `unknowns`
* `open_questions`
* `source_register`
* `provenance_records`
* `completion_status`

Section guidance:

* `problem_definition`: describe the need, current deficiency, and desired outcome; do not include design or implementation plans
* `constraints`: list conditions that later stages must enforce
* `success_criteria`: must be explicit and observable
* `scope_boundaries`: must include `in_scope` and `out_of_scope`
* `risks`: known hazards to correctness, scope, delivery, or interpretation
* `unknowns`: missing information that materially affects understanding
* `open_questions`: targeted questions needed to resolve ambiguity or reduce risk
* `source_register`: all sources used to construct the artifact
* `provenance_records`: provenance for each substantive element
* `completion_status`: readiness, blocking gaps, non-blocking gaps, and justification

Blocking conditions:

* materially incomplete or inconsistent problem definition
* missing or weakly grounded core constraints
* absent, ambiguous, or non-observable success criteria
* unstable or non-constraining scope boundaries
* key terminology unresolved in a way that changes interpretation
* assumed, low-confidence, or floating claims used as settled facts in core sections

If any blocking condition exists, set `completion_status.readiness_state` to `not_ready`.

Discovery-to-Design handoff:

* valid Discovery Artifact required
* `completion_status.readiness_state` must be `ready`
* if design would require invented requirements, constraints, or problem facts, Discovery is not done
