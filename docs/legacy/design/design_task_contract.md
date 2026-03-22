---
title: Clauderfall - Design Task Contract
doc_type: contract
status: active
updated: 2026-03-22
summary: Normative handoff and backflow rules between Design and Task.
---

# Clauderfall - Design Task Contract

## 1. Scope

This document defines the normative Design-to-Task handoff and Task-to-Design backflow contract.

---

## 2. Ownership

`Design` owns solution structure.

`Task` owns work partitioning.

Neither layer MAY silently absorb the other's responsibility.

---

## 3. Handoff Preconditions

Task generation MAY begin only if:

* a Design Artifact is present
* the artifact satisfies `design_artifact.md`
* `completion_status.readiness_state` is `ready`

If any precondition fails, the handoff is invalid.

---

## 4. Permitted Task Use

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

## 5. Backflow Trigger

Task MUST raise backflow if:

* the Design Artifact is invalid or incomplete
* task boundaries cannot be formed without making new design decisions
* interfaces, workflows, or invariants needed for task acceptance are missing or unstable
* constraints are too weakly encoded to propagate into task contracts
* acceptance expectations cannot be made explicit from the design
* dependencies between work units cannot be determined from the design artifact

Backflow is mandatory when triggered.

If the issue is local and non-structural, Task MAY continue while recording it explicitly.

If valid task formation or acceptance would require missing or unstable design structure, backflow is `high` and Task MUST halt the affected area.

---

## 6. High Backflow Payload

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

## 7. Payload Rules

A `high` backflow payload MUST:

* name the exact missing or unstable design input
* distinguish structural blockers from caution-level uncertainty
* remain local to the blocked task area where possible

A `high` backflow payload MUST NOT:

* restate the full Design Artifact
* ask broad exploratory questions without context
* present implementation choices as if they were design requirements
* hide the blocker behind generic wording

---

## 8. Resolution Rule

When Design receives a `high` backflow payload, it MUST:

* resolve the blocking gap and issue an updated Design Artifact with `readiness_state = ready`, or
* determine that the solution is not yet sufficiently specified for Task generation

Task MUST consume the updated artifact and MUST NOT rely on prior session memory as the source of truth.

---

## 9. Invariants

This contract MUST preserve:

* Design owns solution structure
* Task owns work partitioning
* unresolved design-critical uncertainty is never hidden inside Task formation
* caution-level uncertainty may remain visible without reopening Design
* all return-to-Design actions are explicit and traceable
