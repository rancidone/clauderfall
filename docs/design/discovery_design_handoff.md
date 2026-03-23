---
title: Clauderfall Discovery To Design Handoff
doc_type: design
status: active
updated: 2026-03-22
summary: Defines the condensed handoff artifact that carries Discovery output into Design without requiring full brief rereads.
---

# Clauderfall Discovery To Design Handoff

## Purpose

This document defines the handoff artifact between Discovery and Design.

The goal is to give Design a clean, fast-loading input that preserves the parts of Discovery that materially affect design, without requiring the engine or operator to reread the full Discovery brief every session.

## Design Position

The Discovery brief remains the canonical readable record of problem framing.

The handoff artifact is a condensed operational view of that brief.

It exists to support:

- starting Design cleanly
- resuming Design later without rehydrating the full brief
- preserving problem framing boundaries so Design does not invent the problem
- carrying forward assumption status and confidence in a usable way

The handoff artifact should not replace the Discovery brief.

## Relationship To Discovery Brief

The handoff should be derived from the Discovery brief at the point where Discovery is considered ready for Design.

The intended relationship is:

- the Discovery brief is the full readable source
- the handoff is the minimal Design-facing condensation

If the handoff and brief drift apart, the brief remains the source of truth for the problem framing itself.

The handoff should also carry lightweight references back to the canonical Discovery brief at the section-header level.

The purpose of those references is not full traceability. The purpose is quick ambiguity resolution when Design needs to reopen the source material behind a handoff entry.

## Handoff Design Goals

The handoff must be small enough to read quickly at the start of a Design session.

It must still preserve enough structure to let Design:

- recommend the first design unit
- identify the most important unresolved assumptions
- understand which problem areas are strong versus weak
- see the constraints and risks that should shape early design choices

If the handoff cannot support those operations, it is too thin.

If the handoff starts duplicating the whole Discovery brief, it is too heavy.

## Required Handoff Contents

The handoff should contain five parts.

### 1. Handoff Summary

This is a short narrative summary of the problem framing that Design should carry in active memory.

It should answer:

- what problem is being solved
- what outcomes matter
- what constraints dominate the design space

This summary should be short enough to read in under a minute.

### 2. Problem Area Index

The handoff should carry a compact list of the major Discovery problem areas or themes.

Each problem area entry should include:

- `problem_area_id`
- `title`
- `summary`
- `confidence`
- `design_relevance`
- `source_section`

`summary` should be brief. Its role is orientation, not full narrative replacement.

`confidence` should use the existing `low` / `medium` / `high` scale from Discovery.

`design_relevance` should explain why this problem area matters to the Design stage, especially when it is likely to shape early unit sequencing.

This index lets Design reason about where the framing is strong and where early design may need caution.

`source_section` should point to the relevant section header in the canonical Discovery brief.

### 3. Cross-Cutting Constraints And Risks

The handoff should promote the Discovery findings that apply across multiple problem areas.

These should usually include:

- global constraints
- systemic risks
- cross-cutting open questions
- `source_sections`

This section is important because many first design units will be shaped more by cross-cutting pressure than by one isolated problem area.

`source_sections` should point to the relevant cross-cutting section headers in the canonical Discovery brief.

### 4. Assumption Register

The handoff should carry a compact assumption register containing only assumptions that materially affect design.

Each assumption entry should include:

- `assumption_id`
- `statement`
- `status`
- `scope`
- `design_impact`
- `source_section`

`status` should capture the current grounding posture of the assumption.

The current minimum status set should be:

- `confirmed`
- `inferred`
- `unknown`

`confirmed` means the operator has explicitly validated it.

`inferred` means it is a working assumption drawn from the Discovery conversation or available evidence but not explicitly confirmed.

`unknown` means the issue is unresolved and should not be treated as stable truth.

`scope` should identify whether the assumption is:

- tied to a specific problem area
- cross-cutting

`design_impact` should briefly explain why the assumption matters to early design work.

`source_section` should point to the section header in the Discovery brief where the assumption is primarily grounded or discussed.

This is the minimum structure needed to preserve assumption status cleanly across the stage boundary.

### 5. Design Start Recommendation

The handoff should end with a short Design start recommendation.

This should name:

- the recommended first design focus
- the reason that focus should come first
- any caution about weak framing or unresolved risk that may affect the first unit choice

This recommendation is not a rigid next-step command. It is a grounded starting point for the Design engine.

## Deliberately Excluded

The handoff should not attempt to carry:

- the full Discovery brief text
- design-unit definitions
- concrete interfaces
- implementation tasks
- a full dependency graph
- every minor note or conversational detail from Discovery

Including those would turn the handoff into either a design artifact or a noisy archive.

## Proposed Minimal Logical Shape

The minimum logical shape is:

```yaml
handoff_metadata:
  regenerated_after_reentry: boolean
handoff_summary: string
problem_areas:
  - problem_area_id: string
    title: string
    summary: string
    confidence: low | medium | high
    design_relevance: string
    source_section: string | [string]
cross_cutting:
  global_constraints: [string]
  systemic_risks: [string]
  open_questions: [string]
  source_sections: [string]
assumptions:
  - assumption_id: string
    statement: string
    status: confirmed | inferred | unknown
    scope: cross_cutting | problem_area_id
    design_impact: string
    source_section: string | [string]
design_start_recommendation:
  focus: string
  rationale: string
  caution: string | null
```

This is a logical shape, not a final persistence format.

`handoff_metadata.regenerated_after_reentry` should default to `false`.

If Discovery repair occurs during Design reentry and a new handoff is generated from the repaired brief, this field should be set to `true`.

This is continuity metadata, not a new artifact type and not a separate workflow gate.

## Reference Rule

Section-header references should be lightweight and human-legible.

They should usually identify:

- the Discovery brief document
- the relevant section header

This is enough to let Design reopen the source material without introducing brittle line-level references or claim-level citation machinery.

If a handoff entry genuinely draws from multiple brief sections, it may carry a small list of section-header references. That should be the exception, not the default.

## Reload Rule

A resumed Design session should normally start by loading:

- the Discovery-to-Design handoff
- the active design-unit artifacts

The full Discovery brief should only need to be reopened when:

- the handoff appears insufficient for the current design question
- Design discovers a contradiction in the original framing
- the operator explicitly wants to inspect the fuller Discovery narrative

This is the main performance and clarity win of the handoff model.

## Handoff Creation Rule

The handoff should be created when Discovery is explicitly handed off to Design, either by:

- the normal consensus transition
- an operator override into early Design

In the override case, the handoff should still be created, but it should make the weakness explicit by preserving:

- low-confidence problem areas
- unresolved assumptions with weak status
- a caution in the Design start recommendation

This lets Design proceed without hiding the costs of the override.

## Failure Modes To Avoid

The handoff design should avoid:

- collapsing the entire Discovery brief into a dense structured dump
- losing assumption grounding status at the stage boundary
- summarizing problem areas so vaguely that Design still has to rediscover the problem
- turning the Design start recommendation into a hidden design decision
- forcing a full brief reread for ordinary session resumes

## Open Questions

The main remaining questions are:

- whether `design_relevance` should later become more structured than a short explanation
- whether the handoff should persist a brief stage-level readiness rationale in addition to the existing Discovery readiness decision

These do not block adopting the handoff shape above as the current design direction.
