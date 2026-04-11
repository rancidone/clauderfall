---
status: ready
last_updated: 2026-04-11
---

# Clauderfall Handoff Skill Design

## Design Unit

This design unit covers the Clauderfall handoff skill.

The unit boundary is:

- how `/handoff` derives a continuity record from the current session
- what information the handoff artifact must contain
- how the skill handles empty or completed states
- how the current handoff file and archive are managed
- when the skill may write the persisted handoff artifact

The unit does not cover:

- `/continue` read behavior beyond what `/handoff` must produce for it
- Discovery-stage behavior
- Design-stage behavior
- broad runtime orchestration unless it directly changes `/handoff` behavior

## Problem

The continuity Discovery brief defines why handoff exists and what the artifact broadly needs to do, but the handoff step still needs a tighter skill contract to avoid implementation guesswork.

Without a clearer handoff-skill design, downstream work would still need to guess at:

- whether `/handoff` is interactive or non-interactive
- what sections are mandatory in the artifact
- how completed-work sessions should be represented
- whether references are required or optional
- whether question staleness is maintained later by tooling or judged at write time
- how the current handoff file relates to archived handoffs

## Proposed Solution

`/handoff` should be a non-interactive continuity write workflow.

Its job is to derive a compact handoff draft from the current session state and any small set of relevant durable artifacts, show that draft visibly, and write it only with explicit user authorization.

`/handoff` should not run an interview, broad shutdown questionnaire, or multi-turn elicitation loop.
If the current session does not contain enough grounded information to produce a safe handoff, the skill should say so explicitly rather than inventing continuity state.

The workflow should treat the current session as the primary source for in-flight continuity.
It may inspect durable artifacts selectively to avoid misstatement or include a necessary reference, but it should not encourage re-reading old material that is not relevant to the current objective.

Within the session, `/handoff` needs only a small working state:

- current handoff draft
- whether the draft is safe to write
- any missing required continuity signal

The persisted handoff model is intentionally simple:

- the active handoff lives at `docs/handoff/current.md`
- a new handoff write archives the previous current handoff with a timestamped filename and then writes a new current file
- same-session draft refinement may update the proposed text before write
- the workflow should not model multiple concurrent handoff threads unless that becomes an explicit later design unit

The required handoff contract is:

- `Current Objective`
- `Next Steps`
- `Open Questions`

These section headings are always present.

`Current Objective` may be short prose.
It may also have no entries when there is no active objective because the session completed its work.

`Next Steps` is a compact list when follow-up exists.
It may have no entries when no further action is needed.

`Open Questions` is a compact list when unresolved questions remain.
It may have no entries when nothing material remains unresolved.

Open questions must carry explicit status markers:

- `active`
- `stale`

Question status is judged at handoff generation time from the current session state.
No post-write helper script should reinterpret question status later.

A `References` section is optional.
It should appear only when a small set of durable artifacts is genuinely needed to resume the current objective safely.

## References

- `docs/discovery/session_continuity.md`

## Tradeoffs

- Making `/handoff` non-interactive keeps the workflow predictable and lightweight, but it reduces the skill's ability to recover missing context through questioning.
- Using a single current handoff file simplifies resume behavior, but it assumes one dominant active continuity thread.
- Judging question staleness only at write time keeps tooling simple, but it depends on handoff being written regularly.

## Readiness

Status: ready

Rationale: the handoff skill contract is now concrete enough for implementation. Interactivity, artifact shape, empty-state handling, archive behavior, optional references, and stale-question ownership are explicit.
