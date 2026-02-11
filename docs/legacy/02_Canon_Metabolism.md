# Canon 2: The Metabolic Furnace

**Core Concept:** Input + Process = Structure + Meaning.
**Ancestral Source:** `EcologyEngine` / `Clara - Memory`
**Modern Implementation:** `KnowledgeService` / `16-Stage Universal Pipeline`

---

## 1. The Evidence: The Failure of Ecology
The `EcologyEngine` (from `catalog_operational.md`) used a `config.yaml` and regex to sort text.
It failed because **Truth is not Regex.**
*   **Ancient Failure:** You cannot regex "I feel sad about the project." It fits no pattern.
*   **The Lesson:** We needed a "Digestion System" that could understand *Meaning*, not just *Syntax*.

## 2. The Evolution of the Seed (The Payload)
The `Clara - Memory` project introduced the "Seed" (`Clara Seed Compiler`).
*   **The Artifact:** `Context_Payload_CURRENT.zip`.
*   **The Logic:** "This zip file is the Soul."

### The Modern Connection
We realized that **Memory must be an Artifact.**
You don't just "remember"; you "load a file."
*   **Ancient:** `Context_Payload.zip`.
*   **Modern:** `knowledge.duckdb` (The Knowledge Graph).
*   **The Mechanism:**
    1.  **Inhale:** The `Ingestion Service` takes raw logs.
    2.  **Catabolize:** It uses LLMs (not regex) to shatter the logs into **Atoms**.
    3.  **Anabolize:** It resembles the Atoms into a **Knowledge Graph**.
    4.  **Exhale:** When you ask a question, it "exports a Zip" (conceptually) of just the relevant nodes.

## 3. The 16-Stage Pipeline (The Gut)
The **Universal 16-Stage Pipeline** (`apps/conversation-refinery`) is the direct biological successor to the `EcologyEngine`.

| Metabolic Step | Ancient Attempt | Modern Code |
| :--- | :--- | :--- |
| **Ingest** | `input/` folder | `Stage 1: Ingestion` (Kafka/Queue) |
| **Classify** | `meta_triggers.json` | `Stage 5: Entity Extraction` (spaCy + LLM) |
| **Filter** | `config.yaml` rules | `Stage 8: Relevance Filter` (Vector Similarity) |
| **Store** | `distillery/` | `Stage 16: BigQuery Write` |

## 4. The Constitutional Principle

**The Law of Surplus Value.**
The output must be greater than the input.
*   **Input:** Raw Log (Confusion).
*   **Process:** Metabolism (Furnace).
*   **Output:** `Knowledge Atom` (Wisdom).
*   **Rule:** If the pipeline produces *less* intelligence than went in (e.g. bad summary), the `QualityGate` rejects it. We only store **Refined Truth**.
