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

Current feat: none

Bug notes:
- Discovery write path: `discovery_write_draft` sidecar validation is too easy to violate during normal use. Investigate whether the fix belongs in MCP contract shape, validation error ergonomics, schema design, or discovery skill guidance.

Completed:
- runtime skeleton
- shared artifact runtime
- Discovery runtime
- Design runtime
- session lifecycle runtime
- MCP adapter (implementation complete; tests pending)
