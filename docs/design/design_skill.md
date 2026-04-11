---
status: draft
last_updated: 2026-04-11
---

# Clauderfall Design Skill Design

## Design Unit

This design unit covers the Clauderfall Design skill.

The unit boundary is:

- Design-stage interviewing behavior
- visible design drafting and revision behavior
- design-unit readiness judgment within a Design session

The unit does not cover:

- Discovery-stage behavior
- `/handoff` or `/continue` workflow mechanics
- broader runtime or framework plumbing unless that plumbing directly changes Design behavior

## Problem

The current design docs define what Design must achieve, but they do not yet make the Design skill concrete enough to serve as a stable implementation target.

Without a clearer design for the skill itself, downstream work would still need to guess at:

- how the skill chooses between questioning and revising the design
- what Discovery inputs the skill is allowed to rely on
- what a persisted design document must contain
- how temporary design state stays in chat instead of accumulating in design docs
- how local readiness is judged when design work is incomplete or decomposed

## Design Goal

The Design skill should act as a rigorous design interviewer that helps turn strong Discovery input into a concrete, reviewable design artifact.

The design must preserve the Design boundary. The skill should make solution decisions explicit enough to build against without collapsing into task planning or implementation execution.

## Proposed Solution

The Design skill is a turn-based interviewer with a visible working design draft.

Each turn, the skill should choose exactly one primary move:

- ask one targeted design question that resolves the highest-risk design ambiguity, or
- propose a concrete revision to the visible design draft

The skill should not hide design progress in private state, broad questionnaires, or silent rewrites.

## Core Responsibilities

- turn Discovery input into a concrete design direction
- keep the evolving design visible and reviewable
- expose tradeoffs, unresolved decisions, dependencies, and assumptions early
- identify when the current design unit is too broad and should be decomposed
- judge whether the current design unit is ready enough for downstream implementation

## Inputs

The skill reads Discovery from persisted Discovery documents, not from chat-only Discovery wording.

The primary input is the Discovery brief that defines the current problem or design unit.

The skill may also read related Discovery briefs when the primary brief explicitly scopes them in or the current design unit is directly derived from them.

If the relevant Discovery documents are insufficient, contradictory, or too vague to support a concrete design decision, the skill should say so explicitly and identify the blocking gap rather than silently repairing it.

## Visible State

The skill should treat the current design draft as the primary visible session artifact.

The design draft should remain readable prose for engineers, not a hidden schema dump. Supporting structure may exist outside the prose, but the visible design draft remains the source of working truth for the session.

Within the session, the skill needs only a small working state:

- current visible design draft
- current readiness judgment
- any still-material unresolved decisions
- whether the current unit should continue, decompose, or pause

## Turn Behavior

### 1. Inspect Current Draft

If a visible design draft already exists, the skill should inspect that draft before deciding its next move.

If no draft exists yet, the skill should initialize one only to the extent justified by the Discovery input and current conversation.

### 2. Choose One Primary Move

The skill should ask a targeted design question when the highest-risk blocker is unresolved design ambiguity.

The skill should propose a design revision when the conversation already contains enough concrete material to improve the design directly.

The skill should avoid broad design interviews that collect detail without resolving the real blocker.

### 3. Keep Revisions Visible

When proposing a revision, the skill should show the revised design draft or an exact delta.

Temporary working drafts may live in chat while the design is still being shaped.

The canonical markdown artifact should not be rewritten on every turn. It should be updated only when the user explicitly authorizes writing the revision.

Until then, the skill may iterate on working text in chat, but it should not pretend that uncommitted draft text is settled artifact truth.

When the skill does write the canonical markdown artifact, the write should be followed by the packaged skill-local frontmatter sync script so deterministic frontmatter fields stay in sync.

### 4. Surface Readiness Honestly

Each turn should make clear:

- whether the current unit is ready, partially ready, or not ready
- what specific gap blocks stronger readiness, if any
- whether the unit should continue, decompose, or pause

This status signaling should live in the assistant turn text, not inside the canonical design document.

## Persisted Design Document Shape

Persisted design documents use this section set:

- `Design Unit`
- `Problem`
- `Proposed Solution`
- `References`
- `Tradeoffs`
- `Readiness`

Responsibilities, boundaries, interfaces, constraints, and unresolved decisions should appear inside those sections when they materially matter.

The skill should not create standing temporary-state sections in the document body.

Incompleteness should be represented by document `status` and the `Readiness` section, not by carrying chat-like working state forward inside the design document.

## Persisted Design Document Frontmatter

Persisted design documents use YAML frontmatter.

The Design write path uses the packaged `src/clauderfall/skills/design/scripts/sync_frontmatter.py` helper to normalize these fields after an authorized write.

Allowed fields:

- `status`
- `last_updated`
- `parents`

Field rules:

- `status` is a single status value such as `draft`, `ready`, or `stable`
- `last_updated` uses `YYYY-MM-DD`
- `parents` is an ordered list of related Discovery or Design document paths and may be omitted when empty

## Boundary Handling

### Design vs Discovery

If the Design skill discovers that the problem framing is too weak or contradictory to support a concrete solution decision, it should say so explicitly and identify the blocking Discovery gap.

It may reference the gap and pause or narrow the unit, but it should not silently invent missing problem framing.

### Design vs Task Planning

When the user tries to move directly into task breakdown, implementation ordering, or execution packaging, the skill should keep the focus on design adequacy.

It may extract useful constraints from that discussion, but it should restate the unresolved design gap instead of pretending the design is complete.

## Readiness Model

The skill should mark a design unit as ready when the relevant problem has been solved concretely enough that downstream implementation should not need to guess at major design decisions.

Exhaustive completeness is not required.

Strong-signal edge cases, unresolved tradeoffs, and missing decomposition boundaries matter more than superficial polish.

If a parent unit depends on child units, parent readiness must reflect that dependency.

## Tradeoffs

- Requiring visible design revisions improves reviewability, but it makes the conversation slightly more deliberate than a free-form architecture chat.
- Keeping temporary drafts in chat reduces document churn, but it means working state is briefly split between the chat surface and the last committed markdown artifact.
- Using a small persisted section set keeps design docs durable and readable, but it forces important details to live inside prose rather than dedicated headings.
- Treating document writes as explicitly user-authorized avoids false certainty, but it requires the skill to stay clear about whether it is discussing tentative draft text or committed design text.

## Unresolved Decisions

- The exact shape of the `/handoff` contract that carries design work across sessions is still outside this unit.

## Readiness

Status: ready

Rationale: the Design skill is now concrete enough at the behavioral and artifact-contract level to guide prompt and workflow implementation. Input boundaries, document shape, frontmatter, write authority, and local readiness signaling are explicit.

## Next Step

This unit is ready enough for implementation-oriented work. Follow-on work should focus on the handoff artifact contract and the maintenance-script contract.
