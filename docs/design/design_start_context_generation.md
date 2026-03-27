---
title: Clauderfall Design Start Context Generation
doc_type: design
status: active
updated: 2026-03-22
summary: Defines the derivation rules that condense a Discovery brief into a Design Start Context artifact.
---

# Clauderfall Design Start Context Generation

## Purpose

This document defines the derivation contract from the Discovery brief to the Design Start Context.

The goal is to make Design Start Context creation precise enough that:

- the artifact can be generated coherently from the current Discovery brief
- the result can be reviewed against the source brief without guesswork
- Design can rely on the condensation without treating it as new source truth
- Discovery repair can regenerate the context cleanly under the same artifact identity

## Design Position

Design Start Context generation is a selective derivation, not a second round of Discovery and not the beginning of Design itself.

The generator should:

- condense the current canonical Discovery brief
- preserve design-relevant weakness rather than smoothing it away
- add short Design-facing orientation where the artifact needs it
- avoid inventing requirements, interfaces, or design decisions

If the generated context reads like a shorter copy of the full brief, the derivation is too heavy.

If it hides the uncertainty, constraints, or assumption status that should shape Design, it is too thin.

## Source Of Truth

The source material for generation is the current Discovery brief artifact:

- the readable Discovery brief document
- the Discovery brief structured sidecar

The readable brief remains the canonical source for problem framing.

The structured sidecar exists to ensure generation does not depend on unreliable prose extraction for:

- problem-area identity
- confidence
- assumption status
- cross-cutting grouping
- readiness state
- blocking gaps

If the readable brief and structured sidecar appear inconsistent, the readable brief remains canonical for narrative meaning, but the inconsistency should be treated as a brief-quality problem to repair rather than silently normalized during generation.

## Generation Trigger

The system should generate or regenerate the Design Start Context only when one of these events occurs:

- Design begins after a normal consensus transition
- Design begins through explicit operator override
- Discovery is repaired after Design-to-Discovery reentry and Design must resume against updated framing

The system should not regenerate the Design Start Context on every Discovery brief edit while Discovery is still in progress.

## Preconditions

Generation requires all of the following:

- a persisted current Discovery brief checkpoint
- a readable brief that contains the sections the generated references will point back to
- a structured sidecar with the minimum fields defined in `discovery_brief_artifact.md`

Normal consensus generation should happen from a brief with:

- `status: handed_off`
- `readiness: ready_for_design`

Override generation may happen from a brief with:

- `status: handed_off`
- `readiness: not_ready`

That weaker path is valid only when the operator has explicitly chosen to begin Design anyway.

## Derivation Principles

All generation should follow these principles.

### Preserve Boundaries

The generated context must preserve the problem-framing boundary defined by Discovery.

It must not introduce:

- new requirements
- new constraints
- new problem areas
- design-unit boundaries
- concrete interfaces
- implementation tasks

### Preserve Weak Signal

Low-confidence areas, unresolved assumptions, and open questions that materially affect Design must stay visible.

Generation must not rewrite weak framing into stronger-sounding language just because Design is beginning.

### Condense By Design Relevance

Generation should prefer the parts of the brief that are most likely to affect:

- first-unit recommendation
- early design sequencing
- major structural tradeoffs
- reentry risk

Information that is interesting but not likely to shape early Design should usually remain in the Discovery brief only.

### Preserve Reopenability

Every generated item that may later need ambiguity resolution should carry a lightweight section-header reference back to the Discovery brief.

### Add Orientation, Not New Truth

The Design Start Context may add short orientation fields such as:

- `summary`
- `design_relevance`
- `design_impact`
- `design_start_recommendation`

Those fields are derived framing aids.

They must explain why existing Discovery material matters to Design, not add new factual claims.

## Section-Level Derivation Rules

The generated Design Start Context should be derived section by section.

### 1. Context Summary

`context_summary` should be written from the Discovery brief's overview, problem-area introductions, and cross-cutting constraints.

It should answer, in condensed form:

- what problem is being solved
- what outcomes matter
- what constraints dominate the design space

Generation rule:

- produce a short narrative summary
- prefer the brief's already-stated framing over fresh wording where possible
- include only the dominant constraints and outcomes
- omit secondary detail that does not shape the likely first design move

The summary should stay short enough that an engineer can read it in under a minute.

### 2. Problem Area Index

Each Design Start Context problem-area entry must come from an existing Discovery brief problem area.

There is a one-to-one identity mapping for retained entries:

- `problem_area_id` is copied directly from the Discovery brief sidecar
- `title` is copied or lightly normalized from the brief
- `confidence` is copied directly from the sidecar
- `source_section` points to the corresponding brief section header

The generated fields are:

- `summary`
- `design_relevance`

`summary` derivation rule:

- condense the problem statement, intended outcomes, and dominant local constraints for that area
- stay brief
- do not restate full risks, assumption lists, or long narrative context unless needed to understand the area

`design_relevance` derivation rule:

- explain why this area matters to Design now
- usually point to one of: architectural leverage, dependency criticality, unresolved risk concentration, or strong effect on early sequencing
- avoid recommending an actual design-unit decomposition here

Retention rule:

- retain every materially important problem area from the Discovery brief
- do not drop a problem area merely because its confidence is low
- if a problem area is genuinely peripheral to likely Design work, it may be summarized more lightly, but it should still remain visible if the brief treats it as materially important

### 3. Cross-Cutting Constraints And Risks

`cross_cutting.global_constraints`, `cross_cutting.systemic_risks`, and `cross_cutting.open_questions` should be derived from the Discovery brief cross-cutting section and sidecar.

`cross_cutting.source_sections` should point to the relevant cross-cutting section headers.

Generation rule:

- carry forward items that shape multiple problem areas or materially bound the design space
- merge duplicates when multiple brief sections express the same constraint or risk
- preserve explicit unresolved questions when they could affect early Design choices
- omit minor notes that do not materially affect early design reasoning

The generated cross-cutting section should stay compact, but it must not hide the sources of systemic design pressure.

### 4. Assumption Register

The Design Start Context assumption register is selective rather than exhaustive.

An assumption should be included if it is likely to affect:

- the first-unit recommendation
- a major architectural choice
- whether Design can proceed safely without reentry
- interpretation of a major constraint or outcome

Each retained assumption should derive as follows:

- `assumption_id`: copied from the Discovery brief sidecar
- `statement`: copied or lightly normalized for readability
- `status`: copied directly from the Discovery brief sidecar
- `scope`: set to the originating `problem_area_id` for local assumptions, or `cross_cutting` for shared assumptions
- `source_section`: set to the primary brief section where the assumption is grounded

`design_impact` derivation rule:

- explain briefly what design decision, risk, or sequencing concern this assumption affects
- describe impact, not a proposed solution

Selection rule:

- include all `unknown` assumptions that materially affect design
- include `inferred` assumptions when Design is likely to rely on them soon
- include `confirmed` assumptions when they strongly constrain the solution space
- omit assumptions that are too minor to shape early Design

The generator must not change assumption status.

### 5. Design Start Recommendation

`design_start_recommendation` is derived from the full generated context, not from one source field in the Discovery brief.

It should contain:

- `focus`
- `rationale`
- `caution`

`focus` derivation rule:

- name the most defensible first design focus implied by the current Discovery framing
- prefer a boundary suggested by design pressure, not by implementation order
- keep the focus broad enough to remain a recommendation rather than a precommitted design unit schema

`rationale` derivation rule:

- explain why this focus should come first
- ground the reason in the generated problem-area confidence, cross-cutting pressure, and assumption register

`caution` derivation rule:

- name the most important framing weakness or unresolved risk that should temper the first design move
- set to `null` only when no meaningful caution needs explicit carry-forward

This recommendation may orient first-unit selection, but it must not pretend the first unit has already been designed.

## Condensation Rules

The following rules govern what gets preserved versus dropped.

### Must Be Preserved

- every materially important problem area
- confidence for each retained problem area
- materially important cross-cutting constraints
- materially important systemic risks
- materially important open questions that could affect early Design
- design-relevant assumptions and their statuses
- section-header references needed to reopen the brief quickly
- visible weakness from override or incomplete framing

### Usually Drop

- conversational detail
- repeated narrative explanation across multiple brief sections
- minor edge cases that do not affect early design choices
- design drift notes that do not clarify actual problem framing
- low-impact assumptions that are unlikely to matter during early Design

### Never Infer Silently

The generator must not silently:

- combine multiple weak claims into one stronger claim
- upgrade confidence
- upgrade assumption status
- convert an open question into an assumption or resolved fact
- invent a first-unit recommendation that cannot be justified from the preserved context

## Reference Rules

The Design Start Context should preserve lightweight human-legible references only.

Generation should:

- point each problem area to its Discovery brief section header
- point each retained assumption to the primary section where it is grounded
- point the cross-cutting section to the relevant cross-cutting headers

When one generated entry genuinely depends on multiple brief sections, a small list of section-header references is acceptable.

Generation should avoid:

- line-number references
- claim-level citation graphs
- brittle references to transient document formatting

## Transition-Path Differences

The derivation contract is mostly the same for consensus transition and override transition.

The difference is how weak signal is carried.

### Consensus Transition

When the source brief is `ready_for_design`, generation should still preserve bounded uncertainty, but the resulting context will usually have:

- fewer blocking gaps carried as active caution
- fewer low-confidence areas affecting the start recommendation

### Override Transition

When Design begins through explicit override from a `not_ready` brief, generation must be stricter about preserving weakness.

It should explicitly carry forward:

- low-confidence problem areas that affect likely early Design work
- unresolved assumptions with `unknown` or materially important `inferred` status
- blocking gaps from the Discovery brief when they still affect design viability or sequencing

In this path, `design_start_recommendation.caution` should normally be non-null.

Override generation must not disguise an incomplete brief as normal Design readiness.

## Relationship To Discovery Readiness

The Design Start Context is downstream of the Discovery readiness judgment, but it does not replace it.

Generation should therefore read the brief's readiness state and rationale as context for condensation, especially when deciding:

- how much caution to carry into the start recommendation
- whether blocking gaps must remain explicit in the generated context

The Design Start Context should not become a second independent readiness authority for Discovery.

## Reentry Regeneration Rule

After Design-to-Discovery reentry:

- repair the canonical Discovery brief first
- persist a new Discovery brief checkpoint
- regenerate the Design Start Context from that repaired brief
- persist a new checkpoint for the same Design Start Context artifact identity
- set `design_start_context_metadata.regenerated_after_reentry` to `true`

Regeneration after reentry should replace outdated condensation with a fresh condensation from the repaired brief.

It should not create:

- a separate repair artifact
- a forked Design Start Context lineage
- hand-maintained edits that bypass the source brief

## Validation Rules

The derivation should be checkable with simple review questions.

### Source Coverage Checks

A reviewer should be able to confirm:

- every Design Start Context problem area maps to an existing Discovery problem area
- every retained assumption maps to an existing Discovery assumption
- every reference points to a real readable brief section

### Fidelity Checks

A reviewer should be able to confirm:

- no problem-area confidence was changed during derivation
- no assumption status was changed during derivation
- low-confidence or weak-signal items that materially affect Design were not omitted
- generated orientation fields do not introduce factual claims missing from the brief

### Usefulness Checks

A reviewer should be able to answer, from the Design Start Context alone:

- what problem Design is solving
- which problem areas matter most to early Design
- what constraints and risks shape the design space
- which assumptions are most dangerous to rely on
- what first design focus is currently recommended and why

If those answers are not available, the generated context is too thin.

If answering them requires rereading most of the Discovery brief, the generated context is too weakly condensed.

## Failure Modes To Avoid

The generation design should avoid:

- treating condensation as a lossy rewrite of the problem
- hiding low-confidence framing because Design has already started
- copying the full Discovery brief into a smaller wrapper
- producing a start recommendation that is disconnected from the retained evidence
- allowing manual Design Start Context edits to become a shadow source of truth

## Current Design Boundaries

This derivation contract intentionally does not define:

- the exact physical YAML schema for persisted files
- scoring formulas for first-focus recommendation
- richer regeneration history beyond the existing boolean metadata marker

Those can evolve later without changing the core rule that the Design Start Context is a selective, reviewable derivation of the canonical Discovery brief.
