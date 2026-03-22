---
title: Clauderfall - Task Context Contract
doc_type: contract
status: active
updated: 2026-03-22
summary: Normative handoff and backflow rules between Task and Context.
---

# Clauderfall - Task Context Contract

## 1. Scope

This document defines the Task-to-Context handoff contract and the Context-to-Task backflow contract.

This document is normative.

---

## 2. Ownership

`Task` owns work partitioning and task contract definition.

`Context` owns context selection and packet assembly.

Neither layer MAY silently absorb the other's responsibility.

---

## 3. Handoff Preconditions

Context assembly MAY begin only if all of the following are true:

* a Task Artifact is present
* the artifact satisfies `task_artifact.md`
* `completion_status.readiness_state` is `ready`

If any precondition fails, the handoff is invalid.

---

## 4. Context Input Assumptions

Given a valid handoff, Context MAY assume:

* the task is bounded and executable
* blocking task gaps have been resolved
* inputs, outputs, constraints, invariants, and acceptance criteria needed for execution are explicit
* remaining uncertainty appears only in recorded non-blocking gaps

Context MUST NOT assume that missing task detail is intentionally omitted.

---

## 5. Permitted Context Use

Context MAY:

* consume the Task Artifact as the authoritative task contract
* select supporting artifacts required for safe execution
* trim or excerpt supporting material when traceability is preserved
* record exclusions, conflicts, and budget decisions explicitly

Context MUST NOT:

* redefine task scope
* invent missing task requirements
* make new design decisions
* widen execution scope through adjacent or optional context

---

## 6. Backflow Trigger

Context MUST raise backflow if any of the following is true:

* the Task Artifact is invalid or incomplete
* required task references are underspecified
* required supporting artifacts cannot be identified from the task contract
* the packet cannot be made both minimal and complete
* material conflicts cannot be resolved locally
* execution-critical constraints, invariants, or acceptance conditions are missing from the task contract

Backflow is mandatory when triggered.

---

## 7. Backflow Levels

### 7.1 `low`

Conditions:

* required context is identifiable
* uncertainty is local and non-material
* packet assembly does not alter task intent

Behavior:

* continue Context assembly
* optionally record local uncertainty

---

### 7.2 `medium`

Conditions:

* bounded context selection judgment is required
* non-blocking task uncertainty remains visible
* clarity is affected but execution safety and scope are not

Behavior:

* continue Context assembly
* attach caution to affected packet areas
* preserve the uncertainty explicitly

`medium` does not reopen Task by itself.

---

### 7.3 `high`

Conditions:

* valid packet assembly depends on missing or unstable task contract content
* execution safety depends on undefined constraints, invariants, dependencies, or acceptance conditions
* packet assembly would require invention of task requirements or scope

Behavior:

* halt affected Context assembly
* emit a backflow payload
* return control to Task

`high` backflow invalidates continued Context assembly on the affected area until Task resolves the gap.

---

## 8. Backflow Payload

A `high` backflow payload MUST contain:

* `level`
* `summary`
* `blocking_items`
* `affected_packet_areas`
* `required_task_work`
* `trace_links`

Rules:

* `level` MUST be `high`
* `summary` MUST state why Context assembly cannot proceed safely
* `blocking_items` MUST name specific blocking gaps
* `affected_packet_areas` MUST identify blocked packet sections, artifact lookups, or execution surfaces
* `required_task_work` MUST identify the missing task clarification, reference, or contract element needed from Task
* `trace_links` MUST reference relevant task elements or missing sections

---

## 9. Backflow Writing Rules

A backflow payload MUST:

* name the exact missing or unstable task input
* distinguish structural blockers from caution-level uncertainty
* remain local to the blocked packet area where possible

A backflow payload MUST NOT:

* restate the full Task Artifact
* ask broad exploratory questions without context
* present context-selection preferences as if they were task requirements
* hide the blocker behind generic wording

---

## 10. Resolution Rule

When Task receives a `high` backflow payload, it MUST do one of the following:

* resolve the blocking gap and issue an updated Task Artifact with `readiness_state = ready`
* determine that the work cannot yet be specified sufficiently for Context assembly

Context MUST consume the updated artifact and MUST NOT rely on prior session memory as the source of truth.

---

## 11. Invariants

This contract MUST preserve all of the following:

* Task owns task contract definition
* Context owns context selection and packet assembly
* unresolved task-critical uncertainty is never hidden inside Context
* caution-level uncertainty may remain visible without reopening Task
* all return-to-Task actions are explicit and traceable
