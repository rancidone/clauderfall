---
title: Clauderfall - Discovery Artifact
doc_type: artifact-spec
status: active
updated: 2026-03-22
summary: Normative schema and validation rules for discovery outputs consumed by Design.
---

# Clauderfall - Discovery Artifact

## 1. Scope

This document defines the required structure, metadata, and validation rules for a Discovery Artifact.

This document is normative.

---

## 2. Artifact Contract

A valid Discovery Artifact MUST contain these top-level sections:

1. `problem_definition`
2. `constraints`
3. `success_criteria`
4. `scope_boundaries`
5. `risks`
6. `unknowns`
7. `open_questions`
8. `source_register`
9. `provenance_records`
10. `completion_status`

If any required section is missing, the artifact is invalid.

---

## 3. Section Requirements

### 3.1 `problem_definition`

MUST define:

* the user or system need
* the current deficiency or failure
* the desired outcome

MUST describe the problem state.

MUST NOT contain solution structure, architecture decisions, or implementation plans.

---

### 3.2 `constraints`

MUST list conditions that limit acceptable design or execution.

Each constraint MUST be supported by provenance.

Each constraint MUST be actionable by downstream Design.

---

### 3.3 `success_criteria`

MUST define explicit and observable success conditions.

If success cannot be evaluated from the stated criteria, the artifact is `not_ready`.

---

### 3.4 `scope_boundaries`

MUST contain:

* `in_scope`
* `out_of_scope`

MAY contain boundary notes.

Scope boundaries MUST be specific enough to constrain downstream Design.

---

### 3.5 `risks`

MUST list known hazards relevant to correctness, scope, delivery, or interpretation.

Risks MUST NOT be used as a substitute for unknowns or open questions.

---

### 3.6 `unknowns`

MUST list missing information that materially affects understanding of the problem.

Unknowns MUST NOT contain speculative answers.

Unknowns that affect problem definition, constraints, success criteria, or scope boundaries are blocking unless explicitly recorded as non-material.

---

### 3.7 `open_questions`

MUST list targeted questions needed to resolve ambiguity or reduce risk.

Each open question MUST be specific and answerable.

Open questions MUST reference affected artifact sections.

---

### 3.8 `source_register`

MUST list all sources used to construct the artifact.

Each source entry MUST contain:

* `source_id`
* `source_type`
* `origin_ref`

Each source entry MAY contain:

* `authority_level`

`source_id` values MUST be unique within the artifact.

---

### 3.9 `provenance_records`

MUST define provenance for every substantive artifact element.

Each provenance record MUST contain:

* `target_ref`
* `source_classification`
* `confidence`
* `grounding`
* `trace_links`

If a substantive element has no provenance record, the artifact is invalid.

---

### 3.10 `completion_status`

MUST contain:

* `readiness_state`
* `blocking_gaps`
* `non_blocking_gaps`
* `justification`

`completion_status` is the authoritative handoff gate for Design.

---

## 4. Enums

### 4.1 `source_classification`

Allowed values:

* `explicit`
* `derived`
* `assumed`
* `imported`
* `refined`

Rules:

* `explicit` means directly stated in a source.
* `derived` means logically derived from grounded sources.
* `assumed` means provisionally introduced where confirmation is missing.
* `imported` means taken from an explicit external authority.
* `refined` means normalized without semantic change.

`assumed` MUST NOT be used for design-critical facts, core constraints, success criteria, or scope boundaries.

---

### 4.2 `confidence`

Allowed values:

* `high`
* `medium`
* `low`

Rules:

* `high` means clearly and stably supported.
* `medium` means supported but partially ambiguous or indirect.
* `low` means weakly supported, unstable, or assumption-dependent.

Low-confidence design-critical content is blocking unless explicitly shown to be non-material.

---

### 4.3 `grounding`

Allowed values:

* `anchored`
* `floating`

Rules:

* `anchored` requires one or more trace links to supporting sources.
* `floating` means insufficiently tied to a concrete source or stable derivation.

Floating content MUST NOT appear as settled problem facts, constraints, success criteria, or scope boundaries.

Floating content MAY appear only in `risks`, `unknowns`, `open_questions`, or recorded gaps.

---

### 4.4 `readiness_state`

Allowed values:

* `ready`
* `not_ready`

Rules:

* `not_ready` means one or more blocking gaps exist.
* `ready` means no blocking gaps remain.

Non-blocking gaps MUST NOT change `readiness_state`.

---

## 5. Traceability Rules

Each substantive artifact element MUST trace to one or more entries in `source_register`.

Each `trace_link` MUST reference a valid `source_id`.

If traceability cannot be preserved for an element, that element MUST be removed or moved into an uncertainty section.

---

## 6. Blocking Gap Rules

A gap is blocking if any of the following is true:

* `problem_definition` is materially incomplete or internally inconsistent
* a core constraint is missing or weakly grounded
* `success_criteria` are absent, ambiguous, or not observable
* `scope_boundaries` are missing, unstable, or non-constraining
* design-critical content depends on `assumed`, `low`, or `floating` inputs
* key terminology is unresolved and changes interpretation of the problem
* floating claims are presented as settled facts

If any blocking gap exists, `readiness_state` MUST be `not_ready`.

---

## 7. Non-Blocking Gap Rules

A gap is non-blocking only if it does not materially affect:

* problem understanding
* design correctness
* scope enforcement
* constraint interpretation
* success evaluation

Non-blocking gaps MUST still be recorded in `completion_status.non_blocking_gaps`.

---

## 8. Invariants

A valid Discovery Artifact MUST satisfy all of the following:

* all required sections exist
* all substantive elements have provenance
* all substantive elements are traceable
* no settled design decisions are present
* no blocking gap is hidden outside `completion_status`
* no floating content appears as settled fact in design-critical sections

---

## 9. Exit Rule

Discovery MAY hand off to Design only when:

* the artifact is valid
* `completion_status.readiness_state` is `ready`

The Discovery-to-Design boundary is further constrained by `discovery_design_contract.md`.
