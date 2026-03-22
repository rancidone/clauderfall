---
title: Clauderfall Conversational Drafting Loop
doc_type: design
status: draft
updated: 2026-03-22
summary: Draft design for LLM-driven conversational discovery and design loops that remain artifact-grounded and auditable.
---

# Clauderfall Conversational Drafting Loop

## 1. Purpose

This document defines the intended conversational loop for Discovery and Design work.

It captures how an LLM-driven interaction model can fit Clauderfall without turning chat history into the system of record.

This is a draft design for near-term work that sits on top of the current MVP artifact toolchain.

---

## 2. Core Position

Clauderfall should support a strongly conversational operator experience for Discovery and Design.

However:

* conversation is a refinement mechanism
* persisted artifacts remain the source of truth
* validators and contracts remain authoritative over what may advance

The system MUST NOT treat freeform conversation history as durable project state.

---

## 3. Design Goal

Enable a human to work with an LLM in natural language while the system continuously:

* proposes artifact revisions
* validates them deterministically
* surfaces ambiguity and blockers explicitly
* persists accepted versions append-only
* reloads persisted artifact versions on later turns

This preserves the Clauderfall thesis from [clauderfall.md](/home/maddie/repos/clauderfall/docs/design/clauderfall.md) while making the workflow usable as a real tool.

---

## 4. Loop Model

The conversational loop is:

1. load the current persisted artifact version or initialize a new draft
2. accept one conversational user turn
3. generate a candidate artifact revision
4. validate the candidate artifact
5. either:
   * persist a new version if acceptable, or
   * return structured issues/backflow and continue the conversation
6. repeat from the persisted artifact state rather than relying on prior chat history

The LLM may use short local turn history to interpret the immediate exchange, but persisted artifacts are the durable continuity boundary across turns and sessions.

---

## 5. Drafting Responsibilities

### 5.1 Discovery Loop

The conversational Discovery loop should:

* ask targeted clarifying questions
* convert answers into explicit problem definition, constraints, success criteria, scope, and uncertainty
* preserve provenance and confidence
* refuse silent transition into design when readiness is weak

The authoritative handoff gate remains `discovery_design_contract.md`.

### 5.2 Design Loop

The conversational Design loop should:

* consume an explicit Discovery Artifact version
* propose solution structure, interfaces, invariants, and tradeoffs
* surface missing discovery inputs as explicit backflow
* refuse to invent requirements silently

The authoritative handoff gate remains `design_task_contract.md`.

---

## 6. Runtime Boundary

The conversational layer should be skill-driven.

Python remains responsible for:

* typed artifact models
* deterministic validation
* contract checks
* persistence
* lineage recording
* trace-link indexing

The conversational skill layer is responsible for:

* turn-by-turn questioning
* candidate artifact drafting
* summarizing validation failures for the user
* selecting whether to ask for clarification or propose a revision

This follows the implementation boundary in [implementation_strategy.md](/home/maddie/repos/clauderfall/docs/design/implementation_strategy.md).

---

## 7. Required Runtime Objects

The minimum conversational runtime should introduce:

* `ConversationSession`
  * session id
  * stage (`discovery` or `design`)
  * active artifact lineage id
  * current persisted artifact version
* `DraftProposal`
  * candidate artifact body
  * candidate upstream refs
  * validation result
  * whether the proposal is persistable
* `ConversationTurnRecord`
  * raw user turn
  * assistant response
  * proposal outcome

These are runtime coordination objects, not replacements for persisted artifacts.

---

## 8. Proposed Service Surface

The first useful service/API surface is:

* `start_discovery_session`
* `propose_discovery_revision`
* `validate_discovery_revision`
* `save_discovery_revision`
* `check_discovery_handoff`
* `start_design_session`
* `propose_design_revision`
* `validate_design_revision`
* `save_design_revision`
* `check_design_handoff`

Each `propose_*` operation should return:

* assistant reply text
* candidate artifact body
* validation issues
* whether persistence is allowed
* whether clarification is required

---

## 9. Conversation Invariants

The conversational loop must preserve these invariants:

* chat history is not the durable system of record
* persisted artifact versions remain exact and append-only
* upstream refs must be version-qualified
* transition between stages always uses persisted or explicitly provided artifact versions
* failed validation is visible and actionable, not hidden in assistant prose
* contracts, not prompt style, determine readiness

---

## 10. Skill Model Implications

Discovery and Design should each eventually have a stage-specific skill profile containing:

* persona and tone guidance
* questioning style
* allowed drafting scope
* explicit backflow rules
* tool permissions
* expected artifact output type

Personality is an interaction overlay.

It MUST NOT be the mechanism that enforces correctness.

Correctness remains anchored in validators and contracts.

---

## 11. Out of Scope

This document does not define:

* execution of coding tasks
* post-context runtime orchestration
* validation of produced code
* harvest or memory promotion

Those remain future-state work per [future_state.md](/home/maddie/repos/clauderfall/docs/design/future_state.md).
