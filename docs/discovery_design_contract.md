---
title: Clauderfall - Discovery Design Contract
doc_type: contract
status: active
updated: 2026-03-22
summary: Normative handoff and backflow rules between Discovery and Design.
---

# Clauderfall - Discovery Design Contract

## 1. Scope

This document defines the Discovery-to-Design handoff contract and the Design-to-Discovery backflow contract.

This document is normative.

---

## 2. Ownership

`Discovery` owns problem understanding.

`Design` owns solution structure.

Neither layer MAY silently absorb the other's responsibility.

---

## 3. Handoff Preconditions

Design MAY begin only if all of the following are true:

* a Discovery Artifact is present
* the artifact satisfies `discovery_artifact.md`
* `completion_status.readiness_state` is `ready`

If any precondition fails, the handoff is invalid.

---

## 4. Design Input Assumptions

Given a valid handoff, Design MAY assume:

* core problem understanding is explicit
* blocking discovery gaps have been resolved
* design-critical facts are anchored
* remaining uncertainty appears only in recorded non-blocking gaps, risks, unknowns, or open questions

Design MUST NOT assume that missing information is intentionally omitted.

---

## 5. Permitted Design Use

Design MAY:

* consume explicit and anchored discovery content directly
* derive bounded inferences from grounded discovery content
* encode discovery constraints into design structure
* carry forward non-blocking uncertainty explicitly

Design MUST NOT:

* reinterpret unresolved content as settled fact
* convert assumptions into structural decisions without explicit justification
* widen scope beyond discovery boundaries
* treat design convenience as evidence

---

## 6. Backflow Trigger

Design MUST raise backflow if any of the following is true:

* the Discovery Artifact is invalid or incomplete
* design-critical inputs are `low`, `assumed`, or `floating`
* scope boundaries do not constrain system structure
* success criteria do not support design correctness evaluation
* terminology ambiguity changes interface, workflow, or structural meaning
* design would require invention of requirements, constraints, or problem facts

Backflow is mandatory when triggered.

---

## 7. Backflow Levels

### 7.1 `low`

Conditions:

* uncertainty is local and non-structural
* correctness is not affected

Behavior:

* continue Design
* optionally record local uncertainty

---

### 7.2 `medium`

Conditions:

* bounded inference is required
* non-blocking uncertainty remains visible
* clarity is affected but correctness is not

Behavior:

* continue Design
* attach caution to affected design areas
* preserve the uncertainty explicitly

`medium` does not reopen Discovery by itself.

---

### 7.3 `high`

Conditions:

* core discovery inputs are missing, unstable, or insufficiently grounded
* system structure depends on unresolved problem facts
* correctness depends on invented requirements, constraints, or success criteria

Behavior:

* halt affected Design progression
* emit a backflow payload
* return control to Discovery

`high` backflow invalidates continued Design on the affected area until Discovery resolves the gap.

---

## 8. Backflow Payload

A `high` backflow payload MUST contain:

* `level`
* `summary`
* `blocking_items`
* `affected_design_areas`
* `required_discovery_work`
* `trace_links`

Rules:

* `level` MUST be `high`
* `summary` MUST state why Design cannot proceed safely
* `blocking_items` MUST name specific blocking gaps
* `affected_design_areas` MUST identify blocked components, interfaces, workflows, or decisions
* `required_discovery_work` MUST identify the clarification or grounding required from Discovery
* `trace_links` MUST reference relevant discovery elements or missing sections

---

## 9. Backflow Writing Rules

A backflow payload MUST:

* name the exact missing or unstable input
* distinguish structural blockers from caution-level uncertainty
* remain local to the blocked design area where possible

A backflow payload MUST NOT:

* restate the full Discovery Artifact
* ask broad exploratory questions without context
* present a design proposal as if it were a discovery fact
* hide the blocker behind generic wording

---

## 10. Resolution Rule

When Discovery receives a `high` backflow payload, it MUST do one of the following:

* resolve the blocking gap and issue an updated Discovery Artifact with `readiness_state = ready`
* determine that the problem is not yet sufficiently grounded for Design

Design MUST consume the updated artifact and MUST NOT rely on prior session memory as the source of truth.

---

## 11. Invariants

This contract MUST preserve all of the following:

* Discovery owns problem understanding
* Design owns solution structure
* unresolved discovery-critical uncertainty is never hidden inside Design
* caution-level uncertainty may remain visible without reopening Discovery
* all return-to-Discovery actions are explicit and traceable
