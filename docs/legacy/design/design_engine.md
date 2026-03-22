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

The normative artifact schema, validity rules, and handoff gate are defined in `design_artifact.md`.

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

Design elements remain explicitly classified and traceable per `design_artifact.md`.

---

### Task Readiness Shaping

Structures output so it can be decomposed into executable tasks.

* defines boundaries suitable for work units
* exposes dependencies
* enables acceptance criteria

---

### Discovery Backflow Signaling

Evaluates whether design can safely proceed based on the strength and completeness of upstream discovery inputs.

The engine continuously evaluates discovery strength, scope stability, and whether structure would depend on unresolved inputs. The authoritative backflow triggers, levels, and payload requirements are defined in `discovery_design_contract.md`.

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

## Exit Condition

Design is complete when the produced artifact is valid under `design_artifact.md` and the Discovery-to-Design boundary remains satisfied under `discovery_design_contract.md`.

The handoff gate into Task is governed by `design_task_contract.md`.
