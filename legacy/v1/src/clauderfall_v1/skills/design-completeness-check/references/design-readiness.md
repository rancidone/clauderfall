## Design Readiness Reference

Use this reference when judging whether a design unit is complete enough to build from.

Core rule:

* readiness is a build-relevance signal, not a prose-completeness score

Check:

* boundary clarity
* solution concreteness
* interface dependability where relevant
* constraint and strong-signal edge-case coverage
* dependency posture

Ratings:

* `low`: implementation would need to invent major decisions
* `medium`: design direction is useful, but important build-relevant uncertainty remains
* `high`: implementation should not need to guess at major decisions within the unit boundary

Important reminder:

* a parent unit cannot honestly rate `high` if unresolved child dependencies still determine correctness or viability
