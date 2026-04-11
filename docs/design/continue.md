---
status: ready
last_updated: 2026-04-11
---

# Clauderfall Continue Skill Design

## Design Unit

This design unit covers the Clauderfall continue skill.

The unit boundary is:

- how `/continue` reads the latest handoff artifact
- how it restores continuity into the new session without polluting startup state
- what visible output `/continue` should produce for the operator
- how the skill handles stale, empty, or completed handoff states
- what read-only relationship `/continue` has to handoff artifacts and durable docs

The unit does not cover:

- how `/handoff` writes the handoff artifact beyond the existing handoff contract
- Discovery-stage behavior
- Design-stage behavior
- broad runtime orchestration unless it directly changes continue behavior

## Problem

The continuity Discovery brief says `/continue` should use the latest handoff as its primary resume surface and remain read-only with respect to handoff artifacts.

That is not yet concrete enough to implement safely.

Without a clearer `/continue` skill design, downstream work would still need to guess at:

- what `/continue` actually returns to the operator
- how strongly it trusts the handoff versus selectively checking referenced durable artifacts
- how it behaves when the latest handoff records completed work rather than an active objective
- whether it silently injects continuity into the session or exposes it visibly for review
- how it handles stale open questions without re-authoring the handoff

## Proposed Solution

`/continue` should be a non-interactive continuity read workflow.

Its job is to read `docs/handoff/current.md`, treat that artifact as the primary resume surface, and produce a visible resume message for the new session.

`/continue` should not write, rewrite, or mutate handoff artifacts.
It should not auto-run at startup.
It should run only when the operator explicitly invokes it.

The skill should keep the resume surface visible and compact.
It should not silently inject broad continuity context into the session as hidden state.

The skill should read the current handoff first.
It may inspect a small number of durable artifacts only when the handoff explicitly references them or when that is necessary to avoid materially misleading the operator about the current objective.

Within the session, `/continue` needs only a small working state:

- the current handoff contents
- the current resume message
- any detected continuity risk that should be surfaced explicitly

The visible output should be a short narrative resume message rather than a structured multi-section brief.

That resume message should:

- summarize the current objective, next steps, and open questions only to the extent needed for fast orientation
- make clear when the handoff describes completed work rather than an active objective
- mention any small set of references only when they are genuinely needed to resume safely
- end by asking how to proceed rather than starting work automatically
- include a few concrete suggestions for likely next moves

Those suggestions do not need to be limited to literal restatement of the handoff.
Some open-ended interpretation is acceptable when it is still well grounded in the current handoff and any clearly relevant referenced artifacts.

The skill should not use that freedom to invent a new objective, over-read stale context, or silently commit to a course of action.

If the handoff shows no active objective, `/continue` should say so explicitly rather than inventing one.
If the handoff is missing, malformed, or too weak to resume safely, `/continue` should say that directly and identify the continuity gap.

`/continue` may call out stale questions as stale, but it should not remove, rewrite, or reclassify them in the artifact.
Status judgment inside the artifact remains owned by `/handoff`.

If `docs/handoff/current.md` does not exist, `/continue` should say explicitly that there is no current continuity record.

In that state, it should not attempt to reconstruct continuity from repo state, old docs, or broad context inference.

It should give a short narrative message explaining that no handoff is available and ask how to proceed.

## References

- `docs/discovery/session_continuity.md`
- `docs/design/handoff.md`

## Tradeoffs

- Making `/continue` visible and read-only preserves operator control, but it means continuity recovery is less automatic.
- Trusting the handoff as the primary resume surface keeps the workflow compact, but it depends on handoff quality.
- Limiting artifact reads avoids dragging old context back in, but it can leave nuance behind unless references are chosen carefully.

## Readiness

Status: ready

Rationale: the continue skill contract is concrete enough for implementation. Read behavior, output shape, non-interactivity, suggestion scope, completed-work handling, and missing-handoff behavior are explicit.
