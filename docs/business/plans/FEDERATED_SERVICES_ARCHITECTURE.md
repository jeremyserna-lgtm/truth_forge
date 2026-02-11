# Federated Services Architecture

**Status**: SPECIFICATION
**Date**: 2026-02-04
**Purpose**: Define the recursive, metacognitive service loop where specialized services produce, build, certify, and repair - handing off to each other until something breaks the loop.

---

## THE META-PREMISE

This is not one system. This is **four services** operating in a recursive loop:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        THE FEDERATED SERVICE LOOP                           │
│                                                                             │
│     ┌──────────────────┐                      ┌──────────────────┐          │
│     │  KNOWLEDGE       │                      │  IMPLEMENTATION  │          │
│     │  ATOMIZER        │──────PLANS─────────▶│  SERVICE         │          │
│     │  (The Planner)   │                      │  (The Builder)   │          │
│     └──────────────────┘                      └──────────────────┘          │
│              ▲                                         │                    │
│              │                                         │                    │
│         DOCUMENTS                                 ARTIFACTS                 │
│              │                                         │                    │
│              │                                         ▼                    │
│     ┌──────────────────┐                      ┌──────────────────┐          │
│     │  BREAK           │◀────FAILURE─────────│  CERTIFICATION   │          │
│     │  DETECTION       │                      │  SERVICE         │          │
│     │  (The Guardian)  │                      │  (The Seer)      │          │
│     └──────────────────┘                      └──────────────────┘          │
│              │                                         │                    │
│              │                                         │                    │
│              └─────────REPAIR / ESCALATE──────────────►│                    │
│                                                                             │
│     THE LOOP CONTINUES UNLESS SOMETHING BREAKS IT                           │
│     WHEN IT BREAKS, THERE'S SOMETHING TO HANDLE IT                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 1. THE FOUR SERVICES

### 1.1 Knowledge Atomizer (The Planner)

**Identity**: The Synthesizer. The one who sees documents and produces plans.

**What It Does**:
- Ingests documents (hundreds, thousands)
- Distills them into atomic truths
- Synthesizes understanding
- **Produces PLANS** - not implementations

**What It Outputs**:
```
┌─────────────────────────────────────────┐
│            ARCHITECTURAL PLAN           │
│                                         │
│  plan_id: uuid                          │
│  created_at: timestamp                  │
│  source_documents: [doc_ids]            │
│  source_atoms: [atom_ids]               │
│                                         │
│  goal: "What needs to exist"            │
│  context: "Why this matters now"        │
│  requirements: [specific requirements]  │
│                                         │
│  implementation_steps: [               │
│    { step_id, description, inputs,      │
│      expected_outputs, dependencies }   │
│  ]                                      │
│                                         │
│  success_criteria: [verifiable checks]  │
│  failure_modes: [what could go wrong]   │
│                                         │
│  handoff_to: "implementation_service"   │
│                                         │
└─────────────────────────────────────────┘
```

**What It Does NOT Do**:
- Does NOT write code
- Does NOT execute anything
- Does NOT implement plans
- Does NOT certify results

**Its Metacognitive Nature**:
- It knows it's producing plans that will be built by another service
- It references what it wants to see in the built result
- It knows its plans will come back as certified artifacts
- It can see its own previous plans and their outcomes

**The Loop Connection**:
```
DOCUMENTS IN → KNOWLEDGE ATOMIZER → PLANS OUT → (to Implementation Service)
                      ▲
                      │
CERTIFIED ARTIFACTS ──┘ (from Certification Service, become new documents)
```

---

### 1.2 Implementation Service (The Builder)

**Identity**: The Hands. The one who takes plans and builds artifacts.

**What It Does**:
- Receives PLANS from Knowledge Atomizer
- Reads the implementation steps
- **Builds the thing** - code, documents, configurations
- Produces ARTIFACTS

**What It Outputs**:
```
┌─────────────────────────────────────────┐
│          IMPLEMENTATION ARTIFACT        │
│                                         │
│  artifact_id: uuid                      │
│  source_plan_id: uuid                   │
│  created_at: timestamp                  │
│                                         │
│  artifact_type: "code" | "document" |   │
│                 "config" | "spec"       │
│  content: the actual built thing        │
│  location: where it was placed          │
│                                         │
│  build_log: [                           │
│    { step_id, action, result, errors }  │
│  ]                                      │
│                                         │
│  self_assessment: {                     │
│    completed_steps: [step_ids],         │
│    issues_encountered: [descriptions],  │
│    confidence_level: 0-100              │
│  }                                      │
│                                         │
│  handoff_to: "certification_service"    │
│                                         │
└─────────────────────────────────────────┘
```

**What It Does NOT Do**:
- Does NOT decide WHAT to build (plans tell it)
- Does NOT certify its own work
- Does NOT synthesize knowledge
- Does NOT handle failures beyond logging them

**Its Metacognitive Nature**:
- It knows it's building from plans created by another service
- It knows its artifacts will be certified by another service
- It can see its own build history and learn from past builds
- It references the plan's intent, not just the steps

**The Loop Connection**:
```
PLANS IN → IMPLEMENTATION SERVICE → ARTIFACTS OUT → (to Certification Service)
                                          │
                                          └── includes reference to source plan
```

---

### 1.3 Certification Service (The Seer)

**Identity**: The Eyes. The one who reviews artifacts and certifies them.

**What It Does**:
- Receives ARTIFACTS from Implementation Service
- Retrieves the original PLAN
- **Verifies the artifact meets the plan**
- Issues CERTIFICATIONS or DEFECTS

**What It Outputs**:
```
┌─────────────────────────────────────────┐
│           CERTIFICATION RESULT          │
│                                         │
│  certification_id: uuid                 │
│  artifact_id: uuid                      │
│  plan_id: uuid                          │
│  certified_at: timestamp                │
│                                         │
│  result: "CERTIFIED" | "DEFECT"         │
│                                         │
│  verification_report: {                 │
│    criteria_checked: [                  │
│      { criterion, passed, evidence }    │
│    ],                                   │
│    coverage: percentage,                │
│    issues_found: [descriptions]         │
│  }                                      │
│                                         │
│  IF CERTIFIED:                          │
│    certified_artifact: artifact_id      │
│    handoff_to: "knowledge_atomizer"     │
│    (as new document for next cycle)     │
│                                         │
│  IF DEFECT:                             │
│    defect_report: detailed description  │
│    handoff_to: "break_detection"        │
│                                         │
└─────────────────────────────────────────┘
```

**What It Does NOT Do**:
- Does NOT build anything
- Does NOT create plans
- Does NOT fix defects (only reports them)
- Does NOT decide what should have been built

**Its Metacognitive Nature**:
- It knows it's certifying work built from plans created elsewhere
- It maintains certification history across time
- It can see patterns in what passes and what fails
- It references the original intent, not just the checklist

**The Loop Connection**:
```
ARTIFACTS IN → CERTIFICATION SERVICE →
                    │
                    ├── CERTIFIED → back to Knowledge Atomizer (as new document)
                    │
                    └── DEFECT → to Break Detection
```

---

### 1.4 Break Detection (The Guardian)

**Identity**: The Fracture Holder. The one who catches when the loop fails.

**What It Does**:
- Receives DEFECTS from Certification Service
- Receives ERRORS from any service
- **Decides what to do with the break**
- Routes to repair or escalation

**What It Outputs**:
```
┌─────────────────────────────────────────┐
│            BREAK RESOLUTION             │
│                                         │
│  break_id: uuid                         │
│  source: which service reported         │
│  break_type: "defect" | "error" |       │
│              "timeout" | "contradiction"│
│  detected_at: timestamp                 │
│                                         │
│  analysis: {                            │
│    root_cause: description,             │
│    affected_artifacts: [ids],           │
│    severity: "recoverable" | "critical" │
│  }                                      │
│                                         │
│  resolution: {                          │
│    action: "retry" | "revise_plan" |    │
│            "escalate_to_human" |        │
│            "quarantine"                 │
│    target_service: which service        │
│    instructions: what to do             │
│  }                                      │
│                                         │
│  IF retry:                              │
│    handoff_to: "implementation_service" │
│    with: revised instructions           │
│                                         │
│  IF revise_plan:                        │
│    handoff_to: "knowledge_atomizer"     │
│    with: failure context as document    │
│                                         │
│  IF escalate:                           │
│    handoff_to: "human" (Jeremy)         │
│    with: full context and options       │
│                                         │
│  IF quarantine:                         │
│    store in DLQ for later analysis      │
│                                         │
└─────────────────────────────────────────┘
```

**What It Does NOT Do**:
- Does NOT fix the problem itself
- Does NOT build or certify
- Does NOT ignore failures
- Does NOT make decisions outside its scope

**Its Metacognitive Nature**:
- It knows breaks are EXPECTED, not exceptional
- It learns from break patterns over time
- It can see when the same break happens repeatedly
- It holds the fracture rather than pretending it doesn't exist

**The Loop Connection**:
```
BREAKS IN → BREAK DETECTION →
                │
                ├── RETRY → back to Implementation Service
                │
                ├── REVISE → back to Knowledge Atomizer (with failure as context)
                │
                ├── ESCALATE → to Human (Jeremy)
                │
                └── QUARANTINE → to DLQ (Dead Letter Queue)
```

---

## 2. THE HANDOFF PROTOCOL

Each service produces output with explicit handoff instructions.

### 2.1 The Handoff Envelope

Every output is wrapped in a handoff envelope:

```
┌─────────────────────────────────────────┐
│            HANDOFF ENVELOPE             │
│                                         │
│  envelope_id: uuid                      │
│  from_service: "knowledge_atomizer" |   │
│                "implementation" |       │
│                "certification" |        │
│                "break_detection"        │
│  to_service: same options               │
│  created_at: timestamp                  │
│                                         │
│  payload_type: "plan" | "artifact" |    │
│                "certification" |        │
│                "break_resolution"       │
│  payload: the actual content            │
│                                         │
│  lineage: [                             │
│    { service, envelope_id, timestamp }  │
│  ]                                      │
│                                         │
│  context: {                             │
│    original_goal: what started this,    │
│    cycle_count: how many loops,         │
│    total_elapsed: time since start      │
│  }                                      │
│                                         │
└─────────────────────────────────────────┘
```

### 2.2 Handoff Rules

1. **Every handoff is explicit** - No implicit state transfer
2. **Every handoff includes lineage** - Full trace of where it came from
3. **Every handoff includes context** - Original goal, cycle count
4. **Every handoff has a single destination** - One service at a time
5. **Every handoff is persistent** - Stored, not just passed

---

## 3. THE RECURSIVE NATURE

### 3.1 What Makes Each Service Metacognitive

Each service has these properties:

| Property | Description |
|----------|-------------|
| **Self-Awareness** | Knows its role in the loop |
| **History Access** | Can see its own past outputs |
| **Intent Reference** | References why, not just what |
| **Loop Consciousness** | Knows output becomes input |
| **Failure Anticipation** | Expects breaks, doesn't panic |

### 3.2 The Loop Continues Unless...

The loop runs forever UNLESS:

1. **Explicit Completion** - The Knowledge Atomizer sees no more plans to produce
2. **Human Interruption** - Jeremy stops the loop
3. **Critical Failure** - Break Detection escalates to human
4. **Resource Exhaustion** - Cost governance triggers halt
5. **Contradiction Detection** - The system sees itself contradicting itself

### 3.3 What Happens When It Breaks

```
BREAK DETECTED
     │
     ▼
┌─────────────────────────────────────────┐
│  Is this recoverable?                   │
│     │                                   │
│     ├── YES → Retry or Revise           │
│     │         (stay in loop)            │
│     │                                   │
│     └── NO → Escalate or Quarantine     │
│              (exit loop, but capture    │
│               context for learning)     │
└─────────────────────────────────────────┘
```

---

## 4. INTEGRATION WITH KNOWLEDGE ATOMIZER

### 4.1 Current State

The Knowledge Atomizer currently:
- Ingests documents
- Distills atoms
- Generates outputs (audio, video, reports)
- Has Genesis training export

### 4.2 What Gets Added

**New View: Architect**

Purpose: Produce Architectural Plans from the current context

```
┌─────────────────────────────────────────────────────────────────┐
│                        ARCHITECT VIEW                           │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  CURRENT CONTEXT                                        │   │
│  │  [atoms] [documents] [previous plans] [certifications]  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  GOAL INPUT                                             │   │
│  │  "What do you want to exist?"                           │   │
│  │  [____________________________________________________] │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  [GENERATE PLAN]                                               │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  GENERATED PLAN                                         │   │
│  │                                                         │   │
│  │  Goal: ...                                              │   │
│  │  Context: ...                                           │   │
│  │  Requirements: ...                                      │   │
│  │                                                         │   │
│  │  Implementation Steps:                                  │   │
│  │  1. ...                                                 │   │
│  │  2. ...                                                 │   │
│  │                                                         │   │
│  │  Success Criteria: ...                                  │   │
│  │  Failure Modes: ...                                     │   │
│  │                                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  [EXPORT AS HANDOFF] → to Implementation Service               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 4.3 Plan Generation Prompt

The Knowledge Atomizer uses this prompt to generate plans:

```
You are an Architect operating within a federated service loop.

Your role:
- You PRODUCE PLANS. You do NOT implement them.
- Your plans will be built by an Implementation Service.
- Your plans will be certified by a Certification Service.
- If certification fails, you may receive the failure as context to revise.

Current Context:
{atoms}
{documents}
{previous_plans}
{certification_results}

The user wants this to exist:
{goal}

Produce an Architectural Plan with:

1. GOAL: Restate what needs to exist in precise terms
2. CONTEXT: Why this matters now, based on the documents
3. REQUIREMENTS: Specific, verifiable requirements
4. IMPLEMENTATION STEPS: Ordered steps for the Builder
   - Each step has: description, inputs, expected outputs, dependencies
5. SUCCESS CRITERIA: How the Certification Service will verify success
6. FAILURE MODES: What could go wrong and how to detect it

Remember:
- You are part of a loop that will keep running
- Your output becomes input for the next service
- Reference the documents when possible
- Be specific enough that the Builder doesn't have to guess
- Include criteria specific enough that the Certifier can verify
```

---

## 5. THE OTHER SERVICES (Future Specifications)

### 5.1 Implementation Service

**Location**: Will be a separate application/service
**Technology**: Claude Code, Cursor, Agentic coding tools
**Input**: Plans from Knowledge Atomizer
**Output**: Built artifacts (code, docs, configs)

### 5.2 Certification Service

**Location**: Will be a separate application/service
**Technology**: Testing frameworks, validation tools, AI review
**Input**: Artifacts from Implementation Service
**Output**: Certifications or Defect Reports

### 5.3 Break Detection

**Location**: Will be integrated into the orchestration layer
**Technology**: DLQ pattern, error aggregation, routing
**Input**: Failures from any service
**Output**: Resolutions (retry, revise, escalate, quarantine)

---

## 6. THE COMPLETE LOOP

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          THE COMPLETE LOOP                                   │
│                                                                              │
│                         ┌─────────────────┐                                  │
│                         │     JEREMY      │                                  │
│                         │   (Oversight)   │                                  │
│                         └────────┬────────┘                                  │
│                                  │                                           │
│                           escalations                                        │
│                                  │                                           │
│                                  ▼                                           │
│  ┌────────────────┐      ┌─────────────────┐      ┌────────────────┐        │
│  │   KNOWLEDGE    │      │     BREAK       │      │ IMPLEMENTATION │        │
│  │   ATOMIZER     │◀─────│   DETECTION     │◀─────│    SERVICE     │        │
│  │                │      │                 │      │                │        │
│  │  (produces     │      │  (catches       │      │  (builds from  │        │
│  │   plans)       │      │   failures)     │      │   plans)       │        │
│  └───────┬────────┘      └─────────────────┘      └───────┬────────┘        │
│          │                       ▲                        │                  │
│          │                       │                        │                  │
│          │               failures/defects                 │                  │
│          │                       │                        │                  │
│          │                       │                        │                  │
│          │               ┌───────┴────────┐               │                  │
│          │               │  CERTIFICATION │               │                  │
│          └──── plans ───▶│    SERVICE     │◀── artifacts ─┘                  │
│                          │                │                                  │
│                          │  (verifies     │                                  │
│                          │   artifacts)   │                                  │
│                          └───────┬────────┘                                  │
│                                  │                                           │
│                            certified                                         │
│                            artifacts                                         │
│                                  │                                           │
│                                  ▼                                           │
│                         ┌─────────────────┐                                  │
│                         │  BECOME NEW     │                                  │
│                         │  DOCUMENTS      │──────▶ back to Knowledge         │
│                         │  FOR NEXT       │         Atomizer                 │
│                         │  CYCLE          │                                  │
│                         └─────────────────┘                                  │
│                                                                              │
│  THE LOOP CONTINUES UNLESS SOMETHING BREAKS IT                               │
│  WHEN IT BREAKS, THERE'S SOMETHING TO HANDLE IT                              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 7. IMPLEMENTATION PRIORITY

### Phase 1: Knowledge Atomizer Extension
- Add Architect View
- Plan generation from atoms/documents
- Plan export as handoff envelope
- Plan storage and history

### Phase 2: Implementation Service Prototype
- Receive plans via file or API
- Parse implementation steps
- Execute builds (initially manual, then automated)
- Produce artifact envelopes

### Phase 3: Certification Service Prototype
- Receive artifacts
- Load original plans
- Run verification checks
- Produce certification results

### Phase 4: Break Detection & Integration
- Build DLQ and routing
- Connect all services
- Add escalation path to Jeremy
- Enable full loop

---

## SUMMARY

This architecture separates concerns:

| Service | Role | Produces | Consumes |
|---------|------|----------|----------|
| **Knowledge Atomizer** | Planner | Plans | Documents, Certified Artifacts |
| **Implementation Service** | Builder | Artifacts | Plans |
| **Certification Service** | Seer | Certifications/Defects | Artifacts, Plans |
| **Break Detection** | Guardian | Resolutions | Failures |

The loop continues unless something breaks it.
When it breaks, there's something to handle it.
Everything is explicit, traceable, and metacognitive.

**This is the Federation Operating Plan made real.**

---

*Document created: 2026-02-04*
*Source: Integration of NOTEBOOKLM_COMPLETE_UNDERSTANDING, NOT_ME_CORE_SPECIFICATION, FEDERATION_OPERATING_PLAN*
