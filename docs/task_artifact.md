---
title: Clauderfall - Task Artifact
doc_type: artifact-spec
status: active
updated: 2026-03-22
summary: Normative schema and validation rules for task outputs consumed by Context.
---

# Clauderfall - Task Artifact

## 1. Scope

This document defines the required structure, metadata, and validation rules for a Task Artifact.

This document is normative.

---

## 2. Artifact Contract

A valid Task Artifact MUST contain these top-level sections:

1. `objective`
2. `scope`
3. `inputs`
4. `outputs`
5. `constraints`
6. `invariants`
7. `acceptance_criteria`
8. `dependencies`
9. `traceability`
10. `completion_status`

If any required section is missing, the artifact is invalid.

---

## 3. Section Requirements

### 3.1 `objective`

MUST define the single implementable feature or work unit represented by the task.

MUST describe the result to be produced.

MUST NOT embed multiple unrelated feature objectives.

---

### 3.2 `scope`

MUST contain:

* `in_scope`
* `out_of_scope`

MAY contain boundary notes.

Scope MUST be specific enough to prevent task-local scope expansion.

---

### 3.3 `inputs`

MUST reference the design elements required for execution.

Inputs MUST include relevant references to:

* components
* interfaces
* data models
* workflows

Each input MUST be traceable to the Design Artifact.

---

### 3.4 `outputs`

MUST define the expected execution result.

Outputs MUST be concrete and observable.

If the expected result cannot be observed or evaluated, the artifact is `not_ready`.

---

### 3.5 `constraints`

MUST list inherited design constraints that execution must preserve.

Each constraint MUST be actionable at task scope.

Constraints MUST NOT introduce new design requirements.

---

### 3.6 `invariants`

MUST list conditions that must continue to hold after execution.

Each invariant MUST be explicit and testable at task scope.

If a task-critical invariant cannot be stated clearly, the artifact is `not_ready`.

---

### 3.7 `acceptance_criteria`

MUST define explicit and testable success checks for the task.

Acceptance criteria MUST be derivable from design intent without introducing new design.

If acceptance cannot be stated without reinterpretation, the artifact is `not_ready`.

---

### 3.8 `dependencies`

MUST identify prerequisite tasks or design elements required before execution.

Each dependency MUST be explicit.

Dependencies MUST NOT be implied only by task ordering convention.

---

### 3.9 `traceability`

MUST map each major task element to its design origin.

Traceability MUST cover:

* objective origin
* input origin
* constraints origin
* invariants origin
* acceptance origin

If a major task element has no traceability entry, the artifact is invalid.

---

### 3.10 `completion_status`

MUST contain:

* `readiness_state`
* `blocking_gaps`
* `non_blocking_gaps`
* `justification`

`completion_status` is the authoritative handoff gate for Context.

---

## 4. Enums

### 4.1 `task_element_classification`

Allowed values:

* `grounded`
* `inferred`
* `unresolved`

Rules:

* `grounded` means directly supported by Design inputs.
* `inferred` means derived through bounded, non-structural task reasoning from Design.
* `unresolved` means not sufficiently determined to be treated as settled task contract content.

`inferred` MUST remain minimal and MUST NOT introduce new design.

`unresolved` MUST NOT appear as settled scope, inputs, outputs, constraints, invariants, or acceptance criteria.

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

Each major task element MUST trace to one or more design elements.

Traceability MUST allow a reviewer to determine:

* what design element supports the task element
* whether the task element is `grounded` or `inferred`
* what constraint, invariant, or decision the task preserves when applicable

If traceability cannot be preserved, the task element MUST be removed or moved into an uncertainty section.

---

## 6. Boundary Rules

A Task Artifact MUST represent a bounded unit of work.

A Task Artifact MUST NOT:

* require new architecture
* require new interface design
* require reinterpretation of design structure
* span multiple unrelated features
* prescribe execution methodology

If any of the above is required, the artifact is invalid.

---

## 7. Blocking Gap Rules

A gap is blocking if any of the following is true:

* task scope is materially incomplete or internally inconsistent
* required inputs are missing or unstable
* outputs are not concrete or observable
* constraints or invariants needed for execution are missing or ambiguous
* acceptance criteria cannot be stated explicitly
* dependencies are required but not identifiable
* any major task element depends on `unresolved` content
* valid execution would require new design decisions

If any blocking gap exists, `readiness_state` MUST be `not_ready`.

---

## 8. Non-Blocking Gap Rules

A gap is non-blocking only if it does not materially affect:

* task executability
* task acceptance
* scope enforcement
* constraint preservation
* dependency correctness

Non-blocking gaps MUST still be recorded in `completion_status.non_blocking_gaps`.

---

## 9. Invariants

A valid Task Artifact MUST satisfy all of the following:

* all required sections exist
* all major task elements are traceable
* the task is bounded to a single implementable feature or work unit
* no unresolved task-critical content appears as settled contract content
* no blocking gap is hidden outside `completion_status`
* execution can proceed without new design decisions

---

## 10. Exit Rule

Task MAY hand off to Context only when:

* the artifact is valid
* `completion_status.readiness_state` is `ready`

The Task-to-Context boundary is further constrained by `task_context_contract.md`.
