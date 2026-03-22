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

---

## Outputs

The Context Engine produces a **Context Packet**.

This packet is the bounded execution input for a stateless agent.

### Context Packet Structure

#### 1. Task Contract

The objective, scope, outputs, constraints, invariants, and acceptance criteria for the task.

---

#### 2. Included Context

The minimal set of artifacts, excerpts, references, and implementation surfaces required for execution.

---

#### 3. Inclusion Justification

An explicit explanation for why each included item is necessary.

---

#### 4. Exclusions

Known related material intentionally omitted to prevent scope expansion or noise.

---

#### 5. Conflict Signals

Known contradictions, ambiguities, stale references, or unresolved tensions present in the assembled context.

---

#### 6. Budget Summary

A summary of packet size, token pressure, and any compression or prioritization decisions.

---

#### 7. Traceability

Mapping between packet contents and their task, design, discovery, or harvested origins.

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

Triggers return to the **Task Engine** or upstream layers when:

* required artifacts are missing
* task references are underspecified
* conflicts cannot be resolved locally
* the packet cannot be made both minimal and complete

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

## Context Packet Invariants

All packets must satisfy:

### Minimal

No unnecessary context is included.

### Complete

All information required for execution is present.

### Auditable

Every inclusion is justified and traceable.

### Deterministic

The same task and artifact set produce materially equivalent packets.

### Bounded

The packet does not authorize scope expansion during execution.

---

## Boundary Rules

The Context Engine must not:

* perform discovery
* make design decisions
* redefine task boundaries
* implement code
* silently resolve contradictory requirements

When contradictions or gaps are material, the engine must signal backflow rather than guess.

---

## Exit Condition

Context assembly is complete when:

* the packet is minimal and complete
* all included material is justified
* important conflicts are surfaced
* token budget is within acceptable bounds
* execution can proceed without reinterpretation or scope expansion

---

## System Relationship

```
Discovery Artifact
    ↓
Design Engine
    ↓
Design Artifact
    ↓
Task Engine
    ↓
Task Artifact
    ↓
Context Engine
    ↓
Context Packet
```

---

## Summary

The Context Engine ensures that:

* execution context is **selected, not accumulated**
* inclusion is **justified, not assumed**
* packets are **minimal, complete, and bounded**

It is the step where explicit work definition becomes executable model context without allowing noise, stale information, or adjacent scope to leak into the agent runtime.
