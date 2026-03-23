---
title: Clauderfall Discovery Brief Artifact
doc_type: design
status: active
updated: 2026-03-22
summary: Defines the canonical Discovery brief artifact as a readable problem-framing document with a small structured sidecar.
---

# Clauderfall Discovery Brief Artifact

## Purpose

This document defines the artifact shape for the Discovery brief.

The goal is to make Discovery's primary output explicit enough to implement and review cleanly without collapsing the stage into schema-first form filling.

The Discovery brief is the canonical Discovery artifact.

It is the source material from which the Design Start Context is derived.

## Design Position

The Discovery brief should be persisted as one logical artifact with two tightly coupled parts:

- a readable Discovery brief document
- a small structured metadata sidecar

The readable document is primary for human understanding and review.

The structured side exists only to support the operations that should not depend on heuristic prose recovery, such as:

- artifact identity
- readiness and transition status
- per-problem confidence lookup
- assumption grounding status
- Design Start Context derivation

If the brief becomes hard to understand without consulting the sidecar, it has become too structure-heavy.

If the system cannot reliably answer readiness, confidence, and assumption-status questions from the sidecar, the artifact has become too prose-heavy.

## Relationship To Other Artifacts

The Discovery brief is the canonical problem-framing record for the Discovery stage.

The Design Start Context is a condensed operational artifact derived from the brief when Discovery is ready to begin Design.

If the Design Start Context and Discovery brief diverge, the Discovery brief remains the source of truth for the original framing.

If Design reentry reveals framing weakness, the system should repair the Discovery brief first, then regenerate the Design Start Context from that repaired brief.

## Canonical Readable Document

The Discovery brief document should be written for an engineer.

It should stay readable as a working brief rather than presenting as raw extracted metadata.

The document should usually contain:

- a short brief overview
- a problem-area section for each major problem/theme
- a cross-cutting section for constraints, assumptions, risks, and open questions that span multiple areas
- a short readiness summary near the end

The document does not need to force one rigid narrative template, but it should preserve enough consistency that Design can reopen it efficiently when needed.

## Required Visible Problem-Area Content

For each materially important problem area, the readable brief should visibly capture:

- the problem statement
- intended outcomes
- constraints
- assumptions
- risks and edge cases
- open questions, when material
- confidence

This is the minimum visible framing Discovery is responsible for before Design starts.

## Cross-Cutting Content

The brief should also support cross-cutting sections for:

- global constraints
- shared assumptions
- systemic risks
- cross-cutting open questions

These sections matter because many early Design decisions are shaped more by cross-cutting pressure than by one isolated problem area.

## Structured Side

The structured side should remain intentionally small.

These fields appear necessary now.

### Core Identity

- `brief_id`
- `title`
- `status`

`brief_id` is the stable artifact identity for the Discovery brief.

`title` is the operator-facing document name and may change over time.

`status` is the workflow state of the brief itself, not the same thing as the Discovery-to-Design approval decision.

The current minimum status set should be:

- `draft`
- `ready_for_design`
- `handed_off`

`draft` means Discovery is still actively framing the problem.

`ready_for_design` means Discovery appears strong enough to begin Design, subject to the normal consensus approval or an explicit override path.

`handed_off` means Design has been explicitly started from this brief lineage.

## Problem-Area Index

- `problem_areas`

Each problem-area entry should carry the minimum structure needed for machine-usable readiness and condensation:

- `problem_area_id`
- `title`
- `confidence`
- `source_section`
- `assumptions`

The system does not need the full prose body duplicated in the sidecar.

The readable document already owns the narrative explanation.

The sidecar exists to preserve the fields later stages need to inspect reliably.

### Problem-Area Assumptions

Each structured assumption entry should include:

- `assumption_id`
- `statement`
- `status`

The current minimum assumption status set should be:

- `confirmed`
- `inferred`
- `unknown`

These statuses match the Design Start Context boundary and preserve whether a claim is stable enough to trust strongly during Design.

## Cross-Cutting Structure

- `cross_cutting`

The sidecar should also carry structured cross-cutting items for:

- `global_constraints`
- `shared_assumptions`
- `systemic_risks`
- `open_questions`
- `source_sections`

Again, this structure is not meant to replace the narrative brief.

It exists so the system can later condense the brief into the Design Start Context without guessing at which assumptions and risks were cross-cutting versus local.

## Readiness Structure

- `readiness`
- `readiness_rationale`
- `blocking_gaps`

`readiness` should use a small stage-level signal:

- `not_ready`
- `ready_for_design`

This is a Discovery-stage recommendation, not a silent transition command.

`readiness_rationale` should stay short and explain the main reason the brief is or is not ready to support Design.

`blocking_gaps` should contain only the important unresolved framing gaps that prevent a normal ready transition into Design.

This field should stay small and operator-meaningful.

## Design Drift Notes

- `design_drift_notes`

Discovery should preserve short notes when the conversation drifted toward design but the resulting content was intentionally held out of the Discovery brief as not-yet-problem-framing truth.

These notes are optional and should stay short.

Their purpose is continuity and interviewer discipline, not archival completeness.

## Proposed Minimal Logical Shape

The current minimum logical shape is:

```yaml
brief_id: string
title: string
status: draft | ready_for_design | handed_off
problem_areas:
  - problem_area_id: string
    title: string
    confidence: low | medium | high
    source_section: string | [string]
    assumptions:
      - assumption_id: string
        statement: string
        status: confirmed | inferred | unknown
cross_cutting:
  global_constraints: [string]
  shared_assumptions:
    - assumption_id: string
      statement: string
      status: confirmed | inferred | unknown
  systemic_risks: [string]
  open_questions: [string]
  source_sections: [string]
readiness: not_ready | ready_for_design
readiness_rationale: string
blocking_gaps: [string]
design_drift_notes: [string]
```

This is a logical shape, not the final persistence schema.

The physical persistence format remains the paired Markdown-plus-YAML model defined in `artifact_persistence_format.md`.

## Deliberately Excluded

The Discovery brief sidecar should not require:

- full problem statements duplicated from the document
- concrete design-unit recommendations
- concrete interfaces
- implementation tasks
- a full citation graph
- a per-turn conversation log
- a long approval history

Those either belong in the readable brief, in the later Design Start Context, or outside the required artifact shape entirely.

## Interaction Model

The system should interact with the Discovery brief in four modes.

### 1. Active Draft

During Discovery, the engine updates the brief as the visible working artifact.

The draft advances by default during the interview.

The system should not require explicit operator approval for every revision before treating the current brief as the active working state.

### 2. Flush Checkpoint

Before context pressure risks losing meaningful progress, the system should flush the current Discovery brief as a new checkpoint under the same `brief_id`.

This preserves revision history without persisting every turn.

### 3. Readiness Evaluation

When Discovery appears strong enough to support Design, the system should evaluate the brief's readiness using:

- problem-area confidence
- explicit assumption status
- visible constraints and risks
- remaining blocking gaps

This supports the normal consensus transition and the weaker override path.

### 4. Design Start Context Generation

When Design begins, the system should derive the Design Start Context from the current ready Discovery brief.

That derivation should be selective and condensed.

The Discovery brief itself remains canonical.

## Open Questions

The main remaining open questions are:

- whether the structured side should carry a separate machine-usable summary for each problem area beyond confidence and assumptions
- whether `status` should remain `handed_off` after Design starts or whether that state should be inferred from related artifacts
- how much design-drift continuity should be surfaced by default versus on demand

These questions do not block adopting the Discovery brief shape above as the current v2 direction.
