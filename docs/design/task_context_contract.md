---
title: Clauderfall - Task Context Contract
doc_type: contract
status: active
updated: 2026-03-22
summary: Normative handoff and backflow rules between Task and Context.
---

# Clauderfall - Task Context Contract

## 1. Scope

This document defines the normative Task-to-Context handoff and Context-to-Task backflow contract.

---

## 2. Ownership

`Task` owns work partitioning and task contract definition.

`Context` owns context selection and packet assembly.

Neither layer MAY silently absorb the other's responsibility.

---

## 3. Handoff Preconditions

Context assembly MAY begin only if:

* a Task Artifact is present
* the artifact satisfies `task_artifact.md`
* `completion_status.readiness_state` is `ready`

If any precondition fails, the handoff is invalid.

---

## 4. Permitted Context Use

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

## 5. Backflow Trigger

Context MUST raise backflow if:

* the Task Artifact is invalid or incomplete
* required task references are underspecified
* required supporting artifacts cannot be identified from the task contract
* the packet cannot be made both minimal and complete
* material conflicts cannot be resolved locally
* execution-critical constraints, invariants, or acceptance conditions are missing from the task contract

Backflow is mandatory when triggered.

If the issue is local and non-material, Context MAY continue while recording it explicitly.

If packet assembly would require missing or unstable task contract content, unresolved execution-critical conditions, or invented scope, backflow is `high` and Context MUST halt the affected area.

---

## 6. High Backflow Payload

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

## 7. Payload Rules

A `high` backflow payload MUST:

* name the exact missing or unstable task input
* distinguish structural blockers from caution-level uncertainty
* remain local to the blocked packet area where possible

A `high` backflow payload MUST NOT:

* restate the full Task Artifact
* ask broad exploratory questions without context
* present context-selection preferences as if they were task requirements
* hide the blocker behind generic wording

---

## 8. Resolution Rule

When Task receives a `high` backflow payload, it MUST:

* resolve the blocking gap and issue an updated Task Artifact with `readiness_state = ready`, or
* determine that the work cannot yet be specified sufficiently for Context assembly

Context MUST consume the updated artifact and MUST NOT rely on prior session memory as the source of truth.

---

## 9. Invariants

This contract MUST preserve:

* Task owns task contract definition
* Context owns context selection and packet assembly
* unresolved task-critical uncertainty is never hidden inside Context
* caution-level uncertainty may remain visible without reopening Task
* all return-to-Task actions are explicit and traceable
