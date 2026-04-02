# Discovery Brief: Design Status Skill

## Problem

There is no way to quickly orient on where design stands across all units in a project. When a user invokes a design status check — or when an LLM needs to orient at the start of a design-adjacent session — there is no compact, authoritative view of which units exist, what their workflow status is, and what their readiness signals say.

The full design documents are on disk and can be read, but loading them is expensive and unnecessary for orientation. The sidecar metadata already contains the signals needed: status, readiness, readiness rationale, and linkage. The problem is that there is no operation to enumerate all design units and return that metadata in a single call.

## Intended Outcome

A user-invoked skill that returns a compact, structured status view of all design units in the current project. The output serves two audiences without duplication:

- The user, who needs to scan overall progress and identify what is blocked or stale
- The LLM, which may need the same view to orient for a follow-on design session

The skill should require exactly one MCP round-trip.

## Constraints

- Metadata only. No document body content. Readiness and status signals from the sidecar are sufficient.
- Single project scope. No cross-repo enumeration.
- Context budget is the primary output constraint. The response must be compact enough to be included in an LLM context window without crowding out the actual work.
- User-invoked on demand. This is not a startup or background operation.
- No recommendation logic. The skill presents state; it does not prescribe next steps.

## Assumptions

- The sidecar fields available per unit are sufficient for orientation: `title`, `status`, `readiness`, `readiness_rationale`, `linkage` (depends_on, parent, children).
- A `design_list` operation does not currently exist. It must be added to the runtime and MCP surface before this skill can be implemented.
- The skill will be a slash command, consistent with the existing `discovery` and `design` skills.

## Risks and Edge Cases

- If no design units exist yet, the skill should return a clear empty state rather than an error.
- If a unit has a malformed or missing sidecar, the skill should surface it as a warning rather than silently omitting it.
- Linkage data (depends_on, parent, children) could become stale if units are renamed or removed. The skill should present it as-is without attempting validation.

## Ordering Decision

Output groups units by workflow status: `accepted` → `in-review` → `draft`. Within each group, units are ordered by `updated_at` descending. The `design_list` operation should return units unordered; grouping is the skill's responsibility.
