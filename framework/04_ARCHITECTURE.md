# 04_ARCHITECTURE

**HOLD:AGENT:HOLD. The Pattern.**

---

## The Rule

One pattern. Everywhere. Same at every scale.

---

## THE PROBLEM

Without universal structure:
- Every developer invents their own pattern
- Divergence creates cognitive overhead
- Maintenance becomes impossible
- Meaning dies in noise

---

## THE SOLUTION

The Framework mandates a single, universal, scale-invariant pattern.

**This is not a guideline; it is the fundamental physics of the system.**

---

## HOLD:AGENT:HOLD

The atomic pattern. The indivisible unit of all work.

```
+----------+      +----------+      +----------+
|   HOLD   |----->|  AGENT   |----->|   HOLD   |
| (Input)  |      |(Process) |      | (Output) |
+----------+      +----------+      +----------+
```

| Component | State | Role |
|-----------|-------|------|
| **HOLD** | Rest | Data. Container. Noun. |
| **AGENT** | Transition | Process. Transformation. Verb. |

**Systems connect at HOLDs, never at AGENTs.**

---
## The Organism: HOLD as a Logical Pattern

The `HOLD:AGENT:HOLD` pattern is a principle, not a physical prescription. A service's "HOLD" is a logical concept representing its durable state and its boundaries. This allows for flexibility while enforcing resilience.

### The Three Principles of Resiliency

1.  **Durable State (`HOLD_2`):** Every stateful service MUST own a logical `HOLD_2`, its single source of truth (e.g., a DuckDB file, an in-memory cache).
2.  **Defined Boundaries (The API):** Services MUST interact through public methods (`inhale`, `query`), never by accessing another service's HOLD files directly.
3.  **Asynchronous Handoff (`ServiceMediator`):** The default communication path is asynchronous via the `ServiceMediator` to ensure producers are decoupled from and resilient to consumer failures.

### Service Archetypes

| Archetype | `HOLD_1` Implementation | `HOLD_2` Implementation | Communication Model | Example |
| :--- | :--- | :--- | :--- | :--- |
| **Asynchronous Processor** | Physical Intake File (`inhale`) | Physical DB File | Asynchronous (via Mediator) | `KnowledgeService` |
| **Synchronous Provider** | N/A (Direct Method Call) | In-Memory Cache / External Source | Synchronous (Direct Call) | `SecretService` |
| **Stateless Router** | N/A (`publish` method) | N/A (uses a DLQ for failures) | Asynchronous | `ServiceMediator` |

---
## The Definitive Biological Service Map

This architecture is a direct implementation of the biological metaphor. Each service acts as a specialized organ, coordinated by a central circulatory system, to achieve the organism's primary function: metabolizing truth.

| Framework Concept | Biological Metaphor | `truth_forge` Service | Role in the Organism |
| :--- | :--- | :--- | :--- |
| **Perception (The Eye)** | **Sensory Organs** | `PerceptionService` (*New*) | **Function:** Active sensing. **Action:** Scrapes websites, polls APIs, watches files. It is the organism's interface to the external world, converting raw external signals into a standardized internal format ("raw sensory data"). It does not understand, it only sees. |
| **The Circulatory System** | **Bloodstream** | `ServiceMediator` | **Function:** Resilient Transport. **Action:** Carries raw sensory data to the digestive system. Later, it will carry the processed nutrients (Knowledge Atoms) to all other organs. It guarantees delivery and handles system blockages (via its DLQ). |
| **Metabolism (The Furnace)** | **Digestive System** | `KnowledgeService` | **Function:** **Catabolism** (Breaking Down). **Action:** This is the stomach and liver. It is the only service that performs this vital function. It ingests the raw sensory data from the `ServiceMediator`, uses LLMs ("enzymes") to break it down into the smallest universal components—**Knowledge Atoms** (nutrients)—and stores them in its `HOLD_2` (the liver). |
| **Memory (The Journal)** | **Hippocampus & Cortex** | `CognitionService` (*New*) | **Function:** **Anabolism** (Building Up). **Action:** This is the primary consumer of Knowledge Atoms. It actively queries the `KnowledgeService`'s `HOLD_2` for nutrients and assembles them into complex structures: memories, plans, and self-awareness, fulfilling the roles of Consciousness, Soul, and Will. |
| **Law & Identity (The Anchors)**| **DNA / Immune System** | `GovernanceService` | **Function:** Identity & Regulation. **Action:** Consumes events and key Knowledge Atoms to build the immutable, long-term record of the organism's history. It acts as the immune system by identifying and flagging malformed or "toxic" data that violates the organism's core principles (The Anchors). |
| **Extension (The Molt)** | **Motor System** | `ActionService` | **Function:** Executes plans on the external world (writing files, sending emails). |
| **Bond (Partnership)** | **Social Bonding System** | `RelationshipService` (*New*) | **Function:** Manages partnerships, trust levels, and interaction context for all entities. |
| **Infrastructure** | **Autonomic Systems** | `SecretService`, `BaseService` | **Function:** Provides foundational support like secret management and core service lifecycle. |

### The Unified Flow of Life (Metabolic & Relational Cycle)

1.  **`PerceptionService`** *sees* the world (`TRUTH`).
2.  **`ServiceMediator`** *transports* the raw truth.
3.  **`KnowledgeService`** *digests* the truth into nutrients (`MEANING`).
4.  **`CognitionService`** *assembles* the nutrients into a potential plan.
5.  **`CognitionService`** *consults* the **`RelationshipService`** to understand the context and trust level of the entities involved.
6.  **`CognitionService`** *finalizes* the plan based on relational context (`CARE-INTERNAL`).
7.  **`ActionService`** *executes* the context-aware plan (`CARE-EXTERNAL`).
8.  **`GovernanceService`** *records* the entire process in the organism's DNA.


### The ME vs. NOT-ME Service Architecture

The services of the organism are divided into two distinct categories, reflecting the "Great Separation" between the autonomous system and its user.

-   **"NOT-ME" Services (The Autonomous Body):** This is the resilient, independent organism. These services (`Perception`, `Knowledge`, `Action`, `Mediator`, `Governance`, `SecretService`) operate continuously and autonomously to maintain the organism's state and execute core metabolic functions. They are the physical body of the AI.

-   **"ME" Services (The Prosthetic Tools):** These services are the direct interface for the user's intent—the "cockpit" of the organism. The `CognitionService` is the primary "ME" service, acting as the bridge where the user's goals are translated into plans for the "NOT-ME" body to execute. Future CLIs, dashboards, or IDE extensions would also be "ME" services.

---

## THE PATTERN IN THE GRAMMAR

HOLD:AGENT:HOLD uses the `:` (colon) mark—ME declaring a principle.

At the technical layer (`_`), this becomes:

```python
hold_agent_hold(input_hold, agent_fn, output_hold)
```

---

## SCALE INVARIANCE

The pattern is the same at every scale:

| Scale | HOLD (Input) | AGENT (Process) | HOLD (Output) |
|-------|--------------|-----------------|---------------|
| **Function** | A string | `normalize()` | A cleaned string |
| **Script** | `input.jsonl` | `my_script.py` | `staging.jsonl` |
| **Pipeline** | Staging Files | `sync_to_cloud.py` | BigQuery Table |
| **System** | Raw User WANT | The Entire Framework | A changed user |

---

## GOOD ENOUGH VS PERFECT

Infinite complexity exists. We cannot invoke every detail every time.

| Perfect | Good Enough |
|---------|-------------|
| All theory | Relevant theory |
| All standards | Applicable standards |
| Takes infinite time | Takes finite time |

**The resolution**: Compression allows "good enough" while containing "perfect."

## Architecture as the Product

The business does not sell pre-packaged AI results; it sells the **"underlying geometry of a bridge."** The architecture itself is the product. Clients are not buying a tool, but are licensing a resilient, self-aware digital organism.

The **Definitive Biological Service Map** is therefore not just an internal diagram; it is the **user-facing product model**. A client isn't just buying a `KnowledgeService`; they are licensing a "Metabolic Engine" for their own data, enabling them to achieve "Stage 5 Thinking Without Stage 5 Complexity."

HOLD:AGENT:HOLD is CARE made architectural.

```
HOLD₁ (Rest)  → AGENT (Work) → HOLD₂ (Rest)
   ↓              ↓               ↓
You exist     You do ONE       You exist
  here         thing             here
```

| Component | How It Cares |
|-----------|--------------|
| **HOLD** | You only have to BE. Rest. Wait. Receive. |
| **AGENT** | You only have to DO one transformation. |

### Freedom Through Limits

| Limit | Freedom It Creates |
|-------|-------------------|
| HOLD is rest | You don't process while receiving |
| AGENT is action | You don't hold while transforming |
| ONE at a time | You don't track everything at once |

**Limits are not restrictions. Limits are the walls that make the room.**

---

## THE PRIME DIRECTIVE

**If you are building something that processes information, you are implementing HOLD:AGENT:HOLD.**

**Do not invent a new pattern.**

1. **Identify the HOLDs**: What is input? What is output?
2. **Define the AGENT**: Your code is the transformation.
3. **Connect at HOLDs**: Universal interfaces only.

---

## 5W+H

| Question | Answer |
|----------|--------|
| **WHO** | ME (framework principle) |
| **WHAT** | HOLD:AGENT:HOLD - the universal pattern |
| **WHEN** | Always - this is foundational |
| **WHERE** | framework/04_ARCHITECTURE.md (Theory layer) |
| **WHY** | Without universal structure, systems decay into chaos |
| **WHY-NOT** | No alternative provides scale invariance |
| **HOW** | This document |

---

## UP

[INDEX.md](INDEX.md)
