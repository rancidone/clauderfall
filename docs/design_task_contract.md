---
title: Clauderfall - Design Task Contract
doc_type: contract
status: active
updated: 2026-03-22
summary: Normative handoff and backflow rules between Design and Task.
---

# Clauderfall - Design Task Contract

## 1. Scope

This document defines the Design-to-Task handoff contract and the Task-to-Design backflow contract.

This document is normative.

---

## 2. Ownership

`Design` owns solution structure.

`Task` owns work partitioning.

Neither layer MAY silently absorb the other's responsibility.

---

## 3. Handoff Preconditions

Task generation MAY begin only if all of the following are true:

* a Design Artifact is present
* the artifact satisfies `design_artifact.md`
* `completion_status.readiness_state` is `ready`

If any precondition fails, the handoff is invalid.

---

## 4. Task Input Assumptions

Given a valid handoff, Task MAY assume:

* core solution structure is explicit
* blocking design gaps have been resolved
* interfaces, workflows, and invariants needed for decomposition are settled
* remaining uncertainty appears only in recorded non-blocking gaps, risks, or open design questions

Task MUST NOT assume that missing design detail is intentionally omitted.

---

## 5. Permitted Task Use

Task MAY:

* consume settled design structure directly
* use decomposition signals to form bounded work units
* derive minimal non-structural task details from explicit design inputs
* propagate constraints and invariants into task contracts

Task MUST NOT:

* invent structure, interfaces, or workflows
* resolve open design questions implicitly
* widen scope beyond design boundaries
* replace design decisions with task-local reinterpretation

---

## 6. Backflow Trigger

Task MUST raise backflow if any of the following is true:

* the Design Artifact is invalid or incomplete
* task boundaries cannot be formed without making new design decisions
* interfaces, workflows, or invariants needed for task acceptance are missing or unstable
* constraints are too weakly encoded to propagate into task contracts
* acceptance expectations cannot be made explicit from the design
* dependencies between work units cannot be determined from the design artifact

Backflow is mandatory when triggered.

---

## 7. Backflow Levels

### 7.1 `low`

Conditions:

* task boundaries are clear
* uncertainty is local and non-structural
* task formation does not alter design intent

Behavior:

* continue Task generation
* optionally record local uncertainty

---

### 7.2 `medium`

Conditions:

* decomposition requires limited interpretation of non-structural detail
* non-blocking design uncertainty remains visible
* clarity is affected but task correctness or independence is not

Behavior:

* continue Task generation
* attach caution to affected task areas
* preserve the uncertainty explicitly

`medium` does not reopen Design by itself.

---

### 7.3 `high`

Conditions:

* valid task boundaries depend on missing or unstable design structure
* task acceptance depends on undefined interfaces, invariants, or workflows
* task generation would require invention of new design

Behavior:

* halt affected Task formation
* emit a backflow payload
* return control to Design

`high` backflow invalidates continued Task generation on the affected area until Design resolves the gap.

---

## 8. Backflow Payload

A `high` backflow payload MUST contain:

* `level`
* `summary`
* `blocking_items`
* `affected_task_areas`
* `required_design_work`
* `trace_links`

Rules:

* `level` MUST be `high`
* `summary` MUST state why Task generation cannot proceed safely
* `blocking_items` MUST name specific blocking gaps
* `affected_task_areas` MUST identify blocked features, work boundaries, dependencies, or acceptance areas
* `required_design_work` MUST identify the missing structure, clarification, or decision needed from Design
* `trace_links` MUST reference relevant design elements or missing sections

---

## 9. Backflow Writing Rules

A backflow payload MUST:

* name the exact missing or unstable design input
* distinguish structural blockers from caution-level uncertainty
* remain local to the blocked task area where possible

A backflow payload MUST NOT:

* restate the full Design Artifact
* ask broad exploratory questions without context
* present implementation choices as if they were design requirements
* hide the blocker behind generic wording

---

## 10. Resolution Rule

When Design receives a `high` backflow payload, it MUST do one of the following:

* resolve the blocking gap and issue an updated Design Artifact with `readiness_state = ready`
* determine that the solution is not yet sufficiently specified for Task generation

Task MUST consume the updated artifact and MUST NOT rely on prior session memory as the source of truth.

---

## 11. Invariants

This contract MUST preserve all of the following:

* Design owns solution structure
* Task owns work partitioning
* unresolved design-critical uncertainty is never hidden inside Task formation
* caution-level uncertainty may remain visible without reopening Design
* all return-to-Design actions are explicit and traceable
