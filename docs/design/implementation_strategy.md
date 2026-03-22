---
title: Clauderfall - Implementation Strategy
doc_type: design
status: active
updated: 2026-03-22
summary: Concrete MVP implementation decisions for code layout, Python responsibilities, storage, access patterns, and MCP exposure.
---

# Clauderfall - Implementation Strategy

## 1. Purpose

This document turns the current design set into an implementation plan for the MVP.

It answers the open code-shape questions called out in the handoff:

* what is implemented in Python
* what remains skill or prompt-policy driven
* what is persisted
* how persisted state is accessed
* whether MCP is part of the initial implementation

This document stays inside the current MVP boundary:

* Discovery Artifact
* Design Artifact
* Task Artifact
* Context Packet

It does NOT pull deferred future-state components into scope:

* Execution System
* Validation Layer for code execution outputs
* Harvest System

---

## 2. Primary Decisions

### 2.1 Language and Tooling

The MVP implementation should be Python-first and managed with `uv`.

Rationale:

* the core work is structured document modeling, validation, orchestration, and storage access
* Python has mature libraries for typed schema handling, SQLite access, and CLI tooling
* `uv` keeps local setup and iteration simple

### 2.2 Representation

The MVP should use both:

* typed in-memory models
* persisted artifacts

Typed models are required because the docs define strict schemas, enums, and validity rules.

Persisted artifacts are required because the system is explicitly artifact-driven, traceable, auditable, and session-independent.

### 2.3 Canonical Persistence Shape

The canonical persisted record should be:

* artifact metadata in database storage
* full artifact body stored as structured JSON in database storage

The implementation MAY later add filesystem export for inspection, but database persistence should be treated as canonical for the MVP runtime.

This keeps the source of truth queryable while preserving the full normative document body without lossy decomposition.

### 2.4 Engine Boundary

The engines split into two classes:

* deterministic Python components
* skill-driven generation components

Python owns:

* artifact types
* validators
* handoff precondition checks
* backflow payload validation
* persistence
* traceability indexing
* packet assembly mechanics
* CLI and API surfaces

Skill-driven logic owns:

* artifact drafting from user and project inputs
* ambiguity resolution prompts
* design synthesis prompts
* task decomposition prompts
* context selection heuristics before deterministic validation

The important boundary is that skills may propose artifact content, but Python decides whether that content is valid and persistable.

### 2.5 MCP Position

MCP should be added, but not as the first implementation step.

The initial order should be:

1. Python library
2. local CLI
3. narrow MCP server on top of the same application services

This avoids building protocol surface area before the core artifact and validation model is stable.

---

## 3. What Needs Python

## 3.1 Shared Artifact Models

Python should define first-class models for:

* `DiscoveryArtifact`
* `DesignArtifact`
* `TaskArtifact`
* `ContextPacket`
* high-backflow payloads for each contract boundary
* shared enums such as readiness and provenance classifications

These models should encode:

* required sections
* enum values
* structural constraints
* common identifiers and references

### 3.2 Validators

Python validators should own normative correctness.

There should be two validation layers:

* schema validation
* semantic validation

Schema validation checks:

* required fields
* field types
* enum membership

Semantic validation checks:

* prohibited field usage
* readiness rules
* traceability coverage
* contract preconditions
* backflow payload completeness

### 3.3 Contract Gates

Python should enforce the boundary contracts directly.

Examples:

* Design cannot start from a Discovery Artifact with `readiness_state != ready`
* Task cannot start from an invalid Design Artifact
* Context cannot assemble from an underspecified Task Artifact

These gates should be deterministic, testable application services, not prompt instructions alone.

### 3.4 Persistence and Retrieval

Python should own artifact storage and retrieval because:

* traceability queries are structural
* readiness and validity must be auditable
* session memory is explicitly not the source of truth

### 3.5 Context Assembly

Context selection policy can be assisted by prompts, but packet assembly itself should be a Python service that:

* resolves referenced artifacts
* constructs `included_context`
* records inclusion justifications
* computes exclusions and budget summary
* validates the final packet against `context_packet.md`

### 3.6 Operator Surfaces

Python should provide:

* a local CLI for development and debugging
* an importable application library
* a later MCP server

---

## 4. What Should Be Skill-Based

Skill-based behavior is appropriate where the work is judgment-heavy and text-generative rather than deterministic.

## 4.1 Discovery Skill

The Discovery skill should:

* interrogate raw user input
* identify ambiguity
* draft grounded artifact sections
* request targeted clarification

It should not decide readiness on its own.

## 4.2 Design Skill

The Design skill should:

* transform grounded discovery into candidate system structure
* propose decisions and tradeoffs
* surface design-specific ambiguity

It should not bypass contract or artifact validation.

## 4.3 Task Skill

The Task skill should:

* propose bounded task units
* carry design constraints forward
* draft acceptance criteria and dependencies

It should not invent missing design structure.

## 4.4 Context Skill

The Context skill should:

* propose relevant supporting material
* explain why context is needed
* identify likely exclusions and conflicts

Final packet shape, traceability, and readiness still belong to Python validation.

## 4.5 Skill Packaging

Skills should be versioned assets in the repository, not ad hoc prompt strings buried in code.

For the MVP, skills can be stored as:

* prompt templates
* engine-specific instructions
* optional few-shot examples

The Python runtime should treat them as inputs to generation, not as the enforcement layer.

---

## 5. What Should Be Stored in Database Storage

The database should store durable system state required for artifact-driven operation.

## 5.1 Required MVP Tables

### `artifacts`

Stores one row per durable artifact or packet version.

Recommended fields:

* `artifact_id`
* `artifact_kind` (`discovery`, `design`, `task`, `context_packet`)
* `version`
* `readiness_state`
* `status`
* `created_at`
* `updated_at`
* `body_json`
* `source_artifact_ids`

`body_json` stores the full canonical artifact content.

### `trace_links`

Stores queryable lineage edges.

Recommended fields:

* `trace_id`
* `from_artifact_id`
* `from_path`
* `to_artifact_id` or `to_source_ref`
* `link_type`

This table exists to support inspection, debugging, and future lineage tooling without reparsing every JSON body.

### `engine_runs`

Stores execution records for generation or validation attempts.

Recommended fields:

* `run_id`
* `engine_kind`
* `input_artifact_ids`
* `output_artifact_id`
* `run_status`
* `backflow_level`
* `created_at`
* `notes_json`

This is operational state, not the source of truth for artifacts.

### `source_register_entries`

Stores normalized external or project-local sources referenced by Discovery.

Recommended fields:

* `source_entry_id`
* `artifact_id`
* `source_id`
* `source_type`
* `origin_ref`
* `authority_level`

This avoids having provenance lookup depend on deep JSON traversal.

## 5.2 What Should Not Be in the Database Yet

Do not add future-state execution storage in the MVP, including:

* code patch outputs
* test run outputs for downstream execution
* harvested memory
* long-lived conversational session memory

Those belong to deferred systems, not the current MVP.

---

## 6. How Database Storage Is Accessed

## 6.1 Access Pattern

Database access should go through a Python repository layer.

Do not let skills or MCP handlers write SQL directly.

Recommended layers:

1. models
2. validators
3. application services
4. repositories
5. CLI and MCP adapters

This keeps contract enforcement and persistence logic in one place.

## 6.2 Database Choice

Use SQLite for the MVP.

Rationale:

* local-first workflow
* zero service dependency
* enough structure for artifact metadata and traceability indexing
* compatible with later migration to Postgres if needed

## 6.3 ORM vs Raw SQL

Use a light relational layer rather than hand-written SQL everywhere.

A practical MVP choice is:

* `pydantic` for artifact models
* `sqlalchemy` or `sqlmodel` for persistence models

The code should keep persisted row models separate from normative artifact models.

Do not collapse the artifact spec directly into ORM tables field-by-field. The artifact body should remain a structured document.

---

## 7. MCP Tools

## 7.1 Recommendation

Add MCP after the core library and CLI exist.

MCP is a useful integration surface because Clauderfall is meant to support agents, but the protocol wrapper should stay thin.

## 7.2 Initial MCP Tool Set

The initial MCP server should expose only deterministic, high-value operations:

* `artifact.validate`
* `artifact.get`
* `artifact.list`
* `artifact.create_or_update`
* `contract.check_handoff`
* `context.assemble`
* `traceability.get_links`

These tools should call the same Python application services used by the CLI.

## 7.3 What MCP Should Not Own

MCP should not be the first place where:

* validation rules are implemented
* persistence rules are implemented
* engine prompts are defined

Those belong in the core Python package.

---

## 8. Recommended Python Package Layout

The initial layout should stay small:

```text
pyproject.toml
src/clauderfall/
  artifacts/
    discovery.py
    design.py
    task.py
    context.py
    common.py
  contracts/
    discovery_design.py
    design_task.py
    task_context.py
  validation/
    discovery.py
    design.py
    task.py
    context.py
    contracts.py
  engines/
    discovery.py
    design.py
    task.py
    context.py
  persistence/
    db.py
    models.py
    repositories.py
  services/
    artifact_service.py
    contract_service.py
    context_service.py
  skills/
    loader.py
  cli/
    main.py
  mcp/
    server.py
tests/
```

Notes:

* `artifacts/` contains normative typed models
* `validation/` contains deterministic rule enforcement
* `engines/` orchestrate generation and validation, not just prompting
* `persistence/` isolates storage mechanics
* `services/` are the shared application surface for CLI and MCP

---

## 9. Thin Vertical Slice Order

The handoff recommendation is correct and should be followed with one refinement: persist artifacts from the first slice.

Recommended order:

1. Create the `uv` project and package skeleton.
2. Implement shared enums and common artifact primitives.
3. Implement `DiscoveryArtifact` typed model.
4. Implement Discovery validation.
5. Implement Discovery-to-Design contract gate.
6. Add SQLite persistence for artifact versions and validation results.
7. Expose the slice via CLI.
8. Repeat for Design, then Task, then Context.
9. Add MCP on top of the stable services.

This gives an immediately testable slice without overcommitting to later engine orchestration.

---

## 10. Immediate Next Docs and Code

The next implementation-facing artifacts should be:

1. `pyproject.toml` using `uv`
2. package skeleton under `src/clauderfall/`
3. artifact model docstrings aligned to the spec names
4. a short persistence schema doc once table names are finalized

The first code milestone should prove:

* a Discovery Artifact can be created as a typed object
* it can be validated deterministically
* it can be persisted and reloaded
* the Discovery-to-Design gate can accept or reject it correctly

That is enough to validate the implementation direction before building later engines.
