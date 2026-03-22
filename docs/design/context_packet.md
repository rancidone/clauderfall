---
title: Clauderfall - Context Packet
doc_type: artifact-spec
status: active
updated: 2026-03-22
summary: Normative schema and validation rules for Context Packets.
---

# Clauderfall - Context Packet

## 1. Scope

This document defines the normative structure and validity rules for a Context Packet.

---

## 2. Required Sections

A valid Context Packet MUST contain:

1. `task_contract`
2. `included_context`
3. `inclusion_justification`
4. `exclusions`
5. `conflict_signals`
6. `budget_summary`
7. `traceability`
8. `completion_status`

If any required section is missing, the packet is invalid.

---

## 3. Section Rules

### 3.1 `task_contract`

MUST contain the task contract content required for execution.

`task_contract` MUST include:

* objective
* scope
* outputs
* constraints
* invariants
* acceptance_criteria
* dependencies when relevant to execution safety or order

`task_contract` MUST remain consistent with the source Task Artifact and MUST NOT redefine task scope or intent.

---

### 3.2 `included_context`

MUST contain the minimal set of supporting artifacts, excerpts, references, and implementation surfaces required for safe execution.

Each included item MUST identify:

* the included material
* its type
* its source or origin

Included context MUST be necessary for execution and MUST NOT be selected solely because it is nearby, historically relevant, or broadly informative.

---

### 3.3 `inclusion_justification`

MUST provide an explicit justification for each entry in `included_context`.

Each justification MUST explain why the item is necessary for:

* correctness
* constraint preservation
* invariant preservation
* dependency handling
* acceptance evaluation

If an included item has no justification entry, the packet is invalid.

---

### 3.4 `exclusions`

MUST identify known related material intentionally omitted from the packet.

Each exclusion MUST explain why the material was omitted.

Exclusions MUST be used to document scope protection, not to hide missing required context.

---

### 3.5 `conflict_signals`

MUST record contradictions, ambiguities, stale references, or unresolved tensions present in the assembled packet.

Each conflict signal MUST identify:

* the conflicting elements
* the nature of the conflict
* the impact on safe execution

If a material conflict exists and is not recorded, the packet is invalid.

---

### 3.6 `budget_summary`

MUST summarize packet sizing and reduction decisions.

`budget_summary` MUST include:

* total packet size or equivalent budget measure
* any compression, excerpting, or prioritization decisions that materially shaped the packet

`budget_summary` MUST NOT justify omission of execution-critical context.

---

### 3.7 `traceability`

MUST map packet contents to their upstream origins.

Traceability MUST cover:

* task-contract origin
* included-context origin
* inclusion-justification target mapping
* conflict-signal origin when applicable

If a major packet element has no traceability entry, the packet is invalid.

---

### 3.8 `completion_status`

MUST contain `readiness_state`, `blocking_gaps`, `non_blocking_gaps`, and `justification`.

`completion_status` is the packet readiness record.

---

## 4. Enums

### 4.1 `included_item_type`

Allowed values:

* `artifact`
* `excerpt`
* `reference`
* `source_surface`
* `interface_definition`
* `acceptance_reference`
* `other_explicit_type`

Item types MUST reflect the form of included material and be explicit enough to support auditing.

---

### 4.2 `conflict_severity`

Allowed values:

* `low`
* `medium`
* `high`

If any `high` conflict remains unresolved, `readiness_state` MUST be `not_ready`.

---

### 4.3 `readiness_state`

Allowed values:

* `ready`
* `not_ready`

Non-blocking gaps MUST NOT change `readiness_state`.

---

## 5. Inclusion Rules

An item MAY be included only if:

* it is required to understand or satisfy the task contract
* it is required to preserve a constraint or invariant
* it is required to execute against the correct interface or source surface
* it is required to evaluate acceptance
* it is required to handle an explicit dependency

Context availability alone MUST NOT justify inclusion.

---

## 6. Exclusion Rules

An item SHOULD be excluded if:

* it is adjacent but unnecessary
* it is historically relevant but not execution-relevant
* it duplicates already included information without added execution value
* it invites unrelated improvements or scope expansion

If an excluded item is required for safe execution, the packet is invalid.

---

## 7. Traceability Rules

Each major packet element MUST trace to one or more upstream artifacts or source surfaces.

Traceability MUST allow a reviewer to determine:

* where the packet element came from
* why it was included or recorded
* what task requirement it supports

If traceability cannot be preserved, the packet element MUST be removed or recorded as a gap.

---

## 8. Blocking Gap Rules

A gap is blocking if:

* execution-critical task contract content is missing or inconsistent
* required supporting context cannot be identified
* included context is insufficient for safe execution
* included context cannot be justified item-by-item
* the packet cannot be made minimal without becoming incomplete
* a material conflict prevents safe execution
* scope protection would fail due to missing exclusions or overly broad inclusion

If any blocking gap exists, `readiness_state` MUST be `not_ready`.

---

## 9. Validity Rules

Non-blocking gaps MUST be recorded in `completion_status.non_blocking_gaps` and MUST NOT materially affect:

* execution safety
* task scope protection
* constraint or invariant preservation
* acceptance evaluation
* packet auditability

A valid Context Packet MUST also satisfy:

* all required sections exist
* every included item has an explicit justification
* all major packet elements are traceable
* the packet is minimal relative to the task contract
* the packet is complete enough for safe execution use
* no material conflict is hidden outside `conflict_signals` or `completion_status`
* the packet does not authorize scope expansion
