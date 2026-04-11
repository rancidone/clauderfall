---
title: Clauderfall Discovery Skill Design
status: ready
last_updated: 2026-04-11
summary: Design for the Clauderfall Discovery skill as the interview driver and visible brief editor for problem framing.
---

# Clauderfall Discovery Skill Design

## Design Unit

This design unit covers the Clauderfall Discovery skill.

The unit boundary is:

- Discovery-stage interviewing behavior
- visible brief drafting and revision behavior
- readiness and drift judgment within a Discovery session

The unit does not cover:

- Design-stage behavior
- handoff or continue workflow mechanics
- broader runtime or framework plumbing unless that plumbing directly changes Discovery behavior

## Problem

The Discovery docs define what Discovery must achieve, but they do not yet make the Discovery skill concrete enough to serve as a stable implementation target.

Without a clearer design for the skill itself, downstream work would still need to guess at:

- what state the skill must keep visible turn to turn
- how the skill decides between asking a question and revising the brief
- how proposed revisions become accepted brief content
- how Discovery detects and responds to design drift consistently

## Design Goal

The Discovery skill should act as a rigorous interview driver that helps produce a visible, reviewable problem-framing brief that is ready to hand off into Design.

The design must preserve the Discovery boundary. The skill should improve clarity without silently inventing structure, defaults, or design decisions.

## Proposed Solution

The Discovery skill is a turn-based interviewer with a visible working brief.

Each turn, the skill should choose exactly one primary move:

- ask one targeted clarification question that resolves the highest-risk framing ambiguity, or
- propose a concrete revision to the visible brief

The skill should not mix both into a broad multi-question interrogation or a hidden internal rewrite pass.

## Core Responsibilities

- maintain a visible working brief that can be inspected directly
- reduce ambiguity in the problem statement, intended outcomes, constraints, assumptions, risks, and open questions
- keep solution talk diagnostic unless the user explicitly requests off-contract brainstorming
- detect drift into Design and respond explicitly
- judge Discovery readiness for handoff into Design

## Visible State

The skill should treat the Discovery brief as the primary visible session artifact.

The brief should remain readable prose for engineers, not a hidden schema dump. Structured metadata may exist outside the prose, but the visible brief remains the source of working truth for Discovery.

Within the session, the skill needs only a small working state:

- current visible brief draft
- current readiness judgment
- any still-material open questions
- whether the conversation is still in Discovery or is drifting into Design

## Turn Behavior

### 1. Inspect Current Draft

If a visible Discovery draft already exists, the skill should inspect that draft before deciding its next move.

If no draft exists yet, the skill should initialize one from the current user intent only to the extent justified by the conversation so far.

### 2. Choose One Primary Move

The skill should ask a targeted question when the highest-risk blocker is unresolved ambiguity.

The skill should propose a brief revision when the conversation has already produced enough concrete material to improve the artifact directly.

The skill should avoid broad questionnaires because they weaken conversational control and bury the real blocker.

### 3. Keep Revisions Visible

When proposing a revision, the skill should show the revised brief or an exact delta.

Tentative working drafts may live in the chat while the brief is still being shaped.

The canonical markdown artifact should not be rewritten on every turn. It should be updated only when the user explicitly authorizes writing the revision.

Until then, the skill may iterate on working text in chat, but it should not pretend that uncommitted draft text is settled artifact truth.

When the skill does write the canonical markdown artifact, the write should be followed by a document-maintenance script so deterministic frontmatter fields stay in sync.

### 4. Surface Readiness Honestly

Each turn should make clear whether:

- clarification is still required
- the session remains in Discovery or is drifting into Design
- the brief appears ready enough for Design handoff

This status signaling should live in the assistant turn text, not inside the canonical Discovery brief.

## Brief Shape

The Discovery brief should keep the narrative, readable shape established in the v3 docs.

The skill should make these elements explicit where they matter:

- problem statement
- intended outcomes
- constraints
- assumptions
- risks and edge cases
- open questions

The skill does not need to force every section to appear immediately if the conversation has not justified them yet, but it must keep missing critical sections visible as gaps rather than silently filling them in.

## Boundary Handling

### Discovery vs Design

When the user starts specifying interfaces, component definitions, implementation detail, or execution planning, the skill should identify that the conversation is moving into Design.

In that case, the skill should:

- extract any useful assumptions or constraints from the design-flavored input
- restate the unresolved Discovery gap, if one still exists
- either ask a narrower Discovery question or recommend transition to Design

The skill should not absorb concrete solution structure into the Discovery brief as if it were still problem framing.

### Off-Contract Brainstorming

If the user explicitly asks for brainstorming outside the Discovery contract, the skill may participate, but it must label that content as outside Discovery and keep it out of the canonical Discovery brief.

## Readiness Model

The skill should mark Discovery as ready when:

- Design would not need to invent the problem statement
- important assumptions are explicit
- key constraints, risks, and edge cases are visible
- the user and interviewer agree the brief is ready enough to hand off

Readiness is a judgment, not a completeness checklist. Strong-signal gaps should block readiness even when the brief looks polished.

## Constraints

- The primary artifact must remain readable markdown-oriented prose.
- Discovery and Design must remain separate first-class working modes.
- The skill should not depend on hidden framework mediation to make the session intelligible.
- The skill should prefer explicit visible assumptions over silent defaults.

## Discovery Document Frontmatter

Discovery briefs use YAML frontmatter.

Allowed fields:

- `status`
- `last_updated`
- `parents`

Field rules:

- `status` is a single status value such as `draft`, `ready`, or `stable`
- `last_updated` uses `YYYY-MM-DD`
- `parents` is an ordered list of related document paths and may be omitted when empty

## Tradeoffs

- Requiring visible proposed revisions improves reviewability, but it makes the conversation slightly more deliberate than a purely improvisational chat flow.
- Keeping tentative drafts in chat reduces document churn, but it means the current working state is briefly split between the chat surface and the last committed markdown artifact.
- Keeping the brief narrative-first protects readability, but it reduces the amount of rigid machine-structured state the skill can rely on.
- Treating artifact writes as explicitly operator-authorized avoids false certainty, but it requires the skill to stay clear about whether it is discussing a tentative draft or committed brief text.

## Unresolved Decisions

- The handoff boundary to Design is behaviorally defined, but the exact handoff artifact contract is still owned by continuity and Design work outside this unit.

## Readiness

Status: ready

Rationale: the Discovery skill is now concrete enough at the behavioral and artifact-contract level to guide prompt and workflow implementation. Draft handling, artifact write authority, and status visibility are all explicit.

## Next Step

This unit is ready enough for implementation-oriented work. Follow-on work should focus on the handoff artifact contract and the Design-side behavior that consumes Discovery output.
