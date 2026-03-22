## Clauderfall V2 Product Brief Reference

Use this reference when you need the product-level framing for Discovery.

Core product:

* Clauderfall helps a single senior engineer turn rough software ideas into high-quality design, task, and context artifacts for coding agents.
* The product's primary promise is artifact quality, not traceability for its own sake.

Main failure mode to prevent:

* ordinary LLM interaction jumps into solution structure before the problem is framed well enough

Important downstream failures:

* wrong problem gets solved
* scope drifts or requirements are invented
* architectural realities are missed
* business rules are misunderstood or omitted
* non-functional constraints are under-specified
* later task and context artifacts become unsafe, vague, noisy, or incomplete

Product principles:

* problem framing must stay ahead of solution structure
* assumptions must be explicit and operator-visible
* human review of evolving artifacts is required
* machine-consumable artifacts are the product, but readable drafts are necessary to make them trustworthy
* existing repos or docs are optional evidence sources, not required inputs
