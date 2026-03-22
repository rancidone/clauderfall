---
title: Clauderfall - Context Engine
doc_type: engine
status: active
updated: 2026-03-22
summary: Context layer for turning task artifacts into minimal, auditable execution packets.
---

# Clauderfall - Context Engine

## Purpose

The Context Engine converts **task artifacts** and **supporting project artifacts** into **bounded execution packets** for a stateless agent.

It does not perform discovery, design, task generation, or execution.

Its goal is to produce a **minimal, complete, and auditable context packet** that gives a downstream runtime everything required to perform one task without widening scope.

---

## Role in System

The Context Engine sits between **Task Engine** and the future **Execution System**.

* **Task Engine** defines what must be executed
* **Context Engine** determines what context is required for safe execution
* the future **Execution System** consumes the assembled packet and performs the task

The Context Engine is the system's **context-compilation layer**.

---

## Core Principle

> Context is assembled by necessity, not by availability.

* Tasks answer: *What must be done?*
* Context assembly answers: *What must be present for that work to be done safely and correctly?*

---

## Inputs

The Context Engine consumes a **Task Artifact**.

It may also consume explicitly referenced supporting artifacts, including:

* discovery artifacts
* design artifacts
* source files
* interface definitions
* acceptance criteria
* prior durable knowledge accepted by a future harvest system

All included inputs must remain **traceable to the task or its upstream artifacts**.

The Task-to-Context handoff contract is defined in `task_context_contract.md`.

---

## Outputs

The Context Engine produces a **Context Packet**.

This packet is the bounded execution input for a stateless agent.

The normative packet schema, validity rules, and handoff gate are defined in `context_packet.md`.

---

## Core Capabilities

### Relevance Filtering

Includes only context that is required to execute the task safely.

Excludes:

* adjacent but unnecessary code
* unrelated design history
* broad repository context
* redundant background material

---

### Sufficiency Checking

Ensures the packet is complete enough for execution.

Detects missing:

* interfaces
* file targets
* constraints
* acceptance conditions
* dependency context

---

### Budget Enforcement

Constrains packet size to preserve a high signal-to-noise ratio inside the model context window.

When budget pressure exists, the assembler must prefer:

* direct task inputs over optional references
* canonical artifacts over duplicated descriptions
* excerpts over full documents when traceability is preserved

---

### Inclusion Justification

Requires every included item to have an explicit reason for inclusion.

No artifact is included solely because it is nearby, available, or historically relevant.

---

### Conflict Detection

Detects contradictions and unstable context before execution.

Includes:

* mismatched interfaces
* conflicting requirements
* stale design references
* overlapping sources with divergent claims

---

### Scope Protection

Prevents execution packets from inviting design drift or task expansion.

The assembler must reject context that:

* introduces new requirements
* suggests unrelated improvements
* expands work beyond the task boundary

---

### Task Backflow Signaling

Detects when a valid context packet cannot be safely assembled from the available task and upstream artifacts.

The engine raises backflow when packet assembly would require inventing task details, tolerating unresolved conflicts, or widening scope to compensate for missing contract inputs. The authoritative backflow contract, including the required high-backflow payload, is defined in `task_context_contract.md`.

---

## Operating Model

The Context Engine operates in five stages:

### 1. Ingest

Load the task artifact and all explicitly referenced upstream material.

---

### 2. Select

Identify the smallest relevant set of supporting artifacts and code surfaces.

---

### 3. Trim

Reduce context to the minimum required form while preserving correctness and traceability.

---

### 4. Stress

Check the packet for missing dependencies, conflicts, ambiguity, and token pressure.

---

### 5. Package

Produce the final context packet for downstream execution.

---

## Exit Condition

Context assembly is complete when the produced packet is valid under `context_packet.md` and the Task-to-Context boundary remains satisfied under `task_context_contract.md`.

The packet validity gate is governed by `context_packet.md`.
