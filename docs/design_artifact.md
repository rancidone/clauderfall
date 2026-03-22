---
title: Clauderfall - Design Artifact
doc_type: artifact-spec
status: active
updated: 2026-03-22
summary: Normative schema and validation rules for design outputs consumed by Task.
---

# Clauderfall - Design Artifact

## 1. Scope

This document defines the required structure, metadata, and validation rules for a Design Artifact.

This document is normative.

---

## 2. Artifact Contract

A valid Design Artifact MUST contain these top-level sections:

1. `objective`
2. `scope`
3. `system_structure`
4. `constraints_encoding`
5. `invariants`
6. `decisions`
7. `risks_and_edge_cases`
8. `open_design_questions`
9. `task_decomposition_signals`
10. `traceability`
11. `completion_status`

If any required section is missing, the artifact is invalid.

---

## 3. Section Requirements

### 3.1 `objective`

MUST define:

* the intended outcome
* the user or system effect
* the connection to the discovery problem definition

MUST describe the designed result.

MUST NOT describe task sequencing or implementation steps.

---

### 3.2 `scope`

MUST contain:

* `in_scope`
* `out_of_scope`

MAY contain boundary notes.

Scope MUST be specific enough to constrain downstream Task generation.

---

### 3.3 `system_structure`

MUST define the shape of the solution.

MUST include, where applicable:

* components or modules
* responsibilities
* boundaries
* interfaces and contracts
* data models or state models
* core workflows

`system_structure` MUST be specific enough that downstream Task formation does not require new architecture.

---

### 3.4 `constraints_encoding`

MUST define how discovery constraints are enforced in the design.

Each encoded constraint MUST contain:

* `source_constraint_ref`
* `enforcing_design_element`

Each encoded constraint MAY contain:

* `violation_consequence`

Passive restatement of constraints is insufficient.

---

### 3.5 `invariants`

MUST define conditions that must always hold in the designed system.

Each invariant MUST be explicit and implementation-enforceable.

If an invariant cannot be stated clearly for a design-critical area, the artifact is `not_ready`.

---

### 3.6 `decisions`

MUST record all material design decisions.

Each decision MUST contain:

* `decision_statement`
* `affected_design_area`
* `alternatives_considered`
* `rationale`
* `consequences`
* `trace_links`

If a material design choice is implicit, the artifact is invalid.

---

### 3.7 `risks_and_edge_cases`

MUST list known failure modes, edge conditions, or system risks relevant to task generation or execution context.

Each item MUST identify:

* the condition
* the affected design area
* the expected impact

Each item MAY identify:

* encoded mitigation

---

### 3.8 `open_design_questions`

MUST list unresolved questions that remain after design.

Each question MUST be:

* explicit
* bounded
* tied to affected design areas

Open design questions MUST NOT block task generation unless they are also recorded as blocking gaps.

---

### 3.9 `task_decomposition_signals`

MUST define the cues required for Task partitioning.

MUST include:

* natural work boundaries
* dependency relationships
* acceptance expectations to preserve

MAY include:

* sequencing requirements

If bounded task formation cannot be derived from this section plus `system_structure`, the artifact is `not_ready`.

---

### 3.10 `traceability`

MUST map major design elements to their upstream origins.

Traceability MUST cover:

* discovery inputs
* imported references
* inferred design elements
* encoded constraints

If a major design element has no traceability entry, the artifact is invalid.

---

### 3.11 `completion_status`

MUST contain:

* `readiness_state`
* `blocking_gaps`
* `non_blocking_gaps`
* `justification`

`completion_status` is the authoritative handoff gate for Task.

---

## 4. Enums

### 4.1 `design_element_classification`

Allowed values:

* `grounded`
* `inferred`
* `imported`
* `unresolved`

Rules:

* `grounded` means directly supported by Discovery inputs.
* `inferred` means derived through bounded design reasoning from grounded Discovery inputs.
* `imported` means taken from an explicit external reference.
* `unresolved` means not sufficiently determined to be treated as settled design.

`unresolved` MUST NOT appear as settled structure, interfaces, invariants, or task decomposition signals.

---

### 4.2 `readiness_state`

Allowed values:

* `ready`
* `not_ready`

Rules:

* `not_ready` means one or more blocking gaps exist.
* `ready` means no blocking gaps remain.

Non-blocking gaps MUST NOT change `readiness_state`.

---

## 5. Traceability Rules

Each major design element MUST trace to one or more upstream sources or decisions.

Traceability MUST allow a reviewer to determine:

* what discovery input or external reference supports the element
* whether the element is `grounded`, `inferred`, or `imported`
* what decision introduced the element when applicable
* what constraints or success criteria the element serves

If traceability cannot be preserved, the design element MUST be removed or moved into an uncertainty section.

---

## 6. Decision Rules

A decision record is REQUIRED if any of the following is true:

* multiple viable approaches were considered
* the chosen structure materially affects task boundaries
* the choice encodes a tradeoff against a discovery constraint or success criterion
* the choice materially changes risk, complexity, or operational behavior

Material design choices MUST NOT remain implicit.

---

## 7. Blocking Gap Rules

A gap is blocking if any of the following is true:

* `system_structure` is materially incomplete or internally inconsistent
* interfaces or workflows needed for task formation are missing or unstable
* discovery constraints have not been encoded into enforceable design elements
* `invariants` are missing, ambiguous, or incompatible with the design
* a major design area depends on `unresolved` content
* `task_decomposition_signals` are too weak to form bounded tasks
* task acceptance expectations cannot be derived safely from the design

If any blocking gap exists, `readiness_state` MUST be `not_ready`.

---

## 8. Non-Blocking Gap Rules

A gap is non-blocking only if it does not materially affect:

* design correctness
* task boundary formation
* constraint propagation
* invariant preservation
* task acceptance framing

Non-blocking gaps MUST still be recorded in `completion_status.non_blocking_gaps`.

---

## 9. Invariants

A valid Design Artifact MUST satisfy all of the following:

* all required sections exist
* all major design elements are traceable
* all material design choices are explicit
* no unresolved design-critical content appears as settled design
* no blocking gap is hidden outside `completion_status`
* bounded task formation is possible without new design decisions

---

## 10. Exit Rule

Design MAY hand off to Task only when:

* the artifact is valid
* `completion_status.readiness_state` is `ready`

The Design-to-Task boundary is further constrained by `design_task_contract.md`.
