# Design: /design-status Skill

## Problem

There is no way to quickly orient on design progress across all units without loading full documents. Users and LLMs both need a compact, single-call view of what exists, what status each unit is in, and how ready it is. At scale (50+ units), a flat full listing is too long to be useful in context.

## Solution

A slash command skill `/design-status` with an optional status filter argument. Default output shows draft units in full plus an accepted count. The filter arg expands to a specific status group.

### Invocation

```
/design-status           # default: active units + accepted count
/design-status accepted  # full accepted list
/design-status draft     # draft only
/design-status all       # all units across all statuses
```

### Skill Behavior

1. Call `design_list` MCP tool — one round-trip, no arguments.
2. Parse the optional argument (none, `accepted`, `draft`, `all`).
3. Apply the view filter (see Output Format).
4. Within each rendered group, sort by `updated_at` descending.
5. If `design_list` returns a warning for a malformed unit, append a `warnings` key.

### Output Format — Default (no arg)

Shows `draft` in full; collapses `accepted` to a count.

```yaml
design_status:
  accepted: 4 units
  draft:
    - unit_id: some-other-unit
      readiness: low
      updated_at: "2026-03-30"
```

### Output Format — Filtered (e.g. `/design-status accepted`)

Shows the requested group in full; omits others entirely.

```yaml
design_status:
  accepted:
    - unit_id: design-list-operation
      readiness: high
      updated_at: "2026-04-01"
```

### Output Format — All (`/design-status all`)

Both groups in full, same structure as filtered but with all groups present.

### Edge Cases

- Empty group renders as `[]`, not omitted.
- No units at all: both groups render as `[]`.
- Malformed units included with a `warnings` key appended to the output.
- Unknown filter arg: return a short error message, list valid args.

### Skill File Location

`~/.claude/skills/design-status/SKILL.md`

No `references/` directory needed.

## Constraints

- Exactly one MCP call (`design_list`). No follow-up reads.
- Output is YAML only — no markdown, no prose wrapping.
- No recommendation logic.
- No linkage, no readiness_rationale in output.

## Dependencies

- Depends on `design-list-operation` being implemented and exposed as an MCP tool.
