---
title: Clauderfall - Design Engine
doc_type: engine
status: active
updated: 2026-03-22
summary: Design layer for converting discovery into structured, implementation-ready solution definitions.
---

# Clauderfall - Design Engine

## Purpose

The Design Engine converts **design-ready discovery artifacts** into **structured, implementation-ready design artifacts**.

It does not perform discovery or generate final code.

Its goal is to define a **complete, explicit solution structure** that can be directly consumed by downstream systems without reinterpretation.

---

## Role in System

The Design Engine sits between **Discovery** and **Task Engine**.

* **Discovery** establishes grounded understanding of the problem
* **Design** defines the structure of the solution
* **Task Engine** decomposes the defined structure into executable work

The Design Engine is the system’s **solution-definition layer**.

---

## Core Principle

> Design transforms grounded understanding into explicit, enforceable system structure.

* Discovery answers: *What is true?*
* Design answers: *What will be built?*

---

## Inputs

The Design Engine consumes a **Discovery Artifact**.

This artifact must include:

* problem definition
* constraints
* success criteria
* scope boundaries
* risks and unknowns
* open questions
* traceability and confidence metadata

Additional reference material may be used, but must remain **explicitly traceable** and must not override discovery-grounded inputs.

The Discovery-to-Design handoff contract is defined in `discovery_design_contract.md`.

---

## Outputs

The Design Engine produces a **Design Artifact**.

This artifact is durable, structured, and suitable for task generation.

The required artifact structure and readiness rules are defined in `design_artifact.md`.

### Design Artifact Structure

#### 1. Objective

Clear statement of what the system or feature will accomplish.

---

#### 2. Scope

Defines what is included and excluded from this design.

---

#### 3. System Structure

Defines the shape of the solution.

* components or modules
* responsibilities
* system boundaries
* interfaces and contracts
* data or state models
* core workflows

---

#### 4. Constraints

Explicit constraints carried forward from discovery.

These must be encoded into the design, not restated passively.

---

#### 5. Invariants

Rules that must always hold true in the system.

These define correctness boundaries.

---

#### 6. Decisions

Discrete design decisions.

Each includes:

* decision statement
* alternatives considered
* rationale
* consequences

---

#### 7. Risks and Edge Cases

Known failure modes, edge conditions, and system risks.

---

#### 8. Open Design Questions

Unresolved questions that remain after design.

These must be explicit and bounded.

---

#### 9. Task Decomposition Signals

Structural hints that enable downstream task generation.

Includes:

* natural work boundaries
* dependency relationships
* acceptance expectations

---

#### 10. Traceability

Mapping between design elements and their origins:

* discovery inputs
* constraints
* external references
* inferred elements

#### 11. Completion Status

Defines whether Design is complete enough for the Task Engine to proceed.

---

## Core Capabilities

### Structure Formation

Transforms discovery outputs into a coherent system shape.

* defines components and responsibilities
* establishes boundaries
* maps interactions and workflows

---

### Constraint Encoding

Converts constraints into enforceable design elements.

* interface rules
* invariants
* acceptance conditions
* sequencing requirements

---

### Decision Formation

Produces explicit, durable design decisions.

* evaluates alternatives
* selects approaches
* records tradeoffs

---

### Assumption Control

Prevents silent invention of requirements.

All design elements must be classified as:

* grounded (from discovery)
* inferred (derived from grounded inputs)
* imported (external reference)
* unresolved (requires confirmation)

---

### Task Readiness Shaping

Structures output so it can be decomposed into executable tasks.

* defines boundaries suitable for work units
* exposes dependencies
* enables acceptance criteria

---

### Discovery Backflow Signaling

Evaluates whether design can safely proceed based on the strength and completeness of upstream discovery inputs.

The Design Engine must continuously assess:

* reliance on unresolved discovery elements
* dependence on inferred structures
* confidence and grounding of critical inputs
* presence of gaps in constraints, interfaces, or success criteria

Rather than a binary stop/continue decision, the system produces a **backflow signal** that reflects the risk of continuing design.

The authoritative backflow contract, including the required high-backflow payload, is defined in `discovery_design_contract.md`.

---

#### Backflow Levels

**Low (Proceed)**

* Design is primarily grounded
* Inferences are shallow and non-structural
* Unresolved items do not impact correctness

Behavior:

* Continue design without interruption

---

**Medium (Caution)**

* Some reliance on inferred elements
* Gaps exist in non-critical areas
* Confidence is uneven across inputs

Behavior:

* Continue design
* Explicitly flag assumptions
* Surface clarification prompts

---

**High (Return to Discovery)**

* Core elements are unresolved (constraints, interfaces, success criteria)
* Design depends heavily on inference
* Low-confidence or weakly grounded inputs affect system structure

Behavior:

* Halt design progression
* Return control to Discovery
* Surface a concise explanation of blocking gaps

---

#### Backflow Explanation Requirement

Each elevated backflow signal must include a short, human-readable explanation.

Example format:

* "Design depends on 3 unresolved constraints and 2 inferred interfaces."
* "Authentication flow cannot meet acceptance expectations due to missing session lifecycle definition."

The explanation must:

* reference specific gaps
* distinguish structural vs non-structural uncertainty
* remain concise and actionable

---

#### Local Dependency Tracking

Backflow signaling relies on **local justification**, not global graph construction.

For each major design element, the system tracks:

* upstream discovery dependencies
* classification (grounded, inferred, unresolved)
* whether dependencies are structurally critical

This enables:

* targeted explanations
* bounded reasoning
* avoidance of full metadata graph complexity

---

## Operating Model

The Design Engine operates in five stages:

### 1. Ingest

Load and preserve the discovery artifact.

---

### 2. Shape

Define system structure:

* components
* interfaces
* workflows
* data boundaries

---

### 3. Decide

Resolve design decisions and record tradeoffs.

---

### 4. Stress

Validate design against:

* constraints
* risks
* edge cases
* internal consistency

Includes evaluation of **backflow pressure**.

---

### 5. Package

Produce the final design artifact for downstream use.

---

## Design Invariants

All outputs must satisfy:

### Grounded

All major elements trace to discovery or explicit sources.

### Explicit

Decisions, assumptions, and constraints are documented.

### Minimal

Only necessary structure is defined.

### Durable

Artifacts remain useful outside the current session.

### Consistent

No contradictions within the design.

### Task-Ready

Design supports decomposition without reinterpretation.

---

## Boundary Rules

The Design Engine must not:

* perform discovery
* fill missing requirements implicitly
* introduce untraceable assumptions
* generate executable tasks
* implement code

When gaps are encountered:

* Low/medium risk → proceed with explicit signaling
* High risk → return control to Discovery

---

## Exit Condition

Design is complete when:

* system structure is clearly defined
* constraints are encoded into the design
* key decisions are recorded
* interfaces and workflows are explicit
* risks and edge cases are identified
* open questions are bounded and visible
* task decomposition can occur without reinterpretation
* no high backflow signals remain

The handoff gate into Task is governed by `design_task_contract.md`.

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
```

---

## Summary

The Design Engine ensures that:

* solutions are **intentional, not emergent**
* decisions are **explicit, not implied**
* structure is **defined, not inferred later**

It is the step where understanding becomes something you can actually build against—without the system quietly making things up on your behalf.

It also acts as a control point, ensuring that when design begins to rely on weak or incomplete understanding, the system can **intelligently return to discovery rather than proceed on unstable ground**.
