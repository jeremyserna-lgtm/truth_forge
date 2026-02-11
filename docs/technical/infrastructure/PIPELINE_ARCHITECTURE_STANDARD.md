# Pipeline Architecture Standard: The Hybrid Tri-Zone Pattern

**AKA**: "The Sandwich Pattern"
**Effective Date**: 2026-01-29
**Applicability**: All data pipelines (Truth Forge, User Processing, Client Data)

---

## 📐 The Core Standard

All data processing pipelines must follow the **Tri-Zone Structure**. This compresses the maintenance surface area by prioritizing SQL/BigQuery for stability and isolating risky complex logic in containers.

## 🌑 Zone 0: The Shaper (The Edge)
**Technology**: Website Backend (Vercel / Node.js)
**Responsibility**: Adapting user uploads.
**Goal**: "Make it fit the pipe."

*   **Characteristics**: Flexible, user-facing.
*   **Role**: Accepts diverse inputs (PDF, Chat Logs, CSV) and "shapes" them into the **Universal Ingestion Schema** before sending to Zone 1.
*   **Edge Enrichment**: Can optionally run `generateSpinalEnrichment` (Gemini) to pre-calculate L5-L8 entities immediately.
*   **Output Target**: `HoldHold1` (BigQuery).

## 🟢 Zone 1: The Ingestion Zone (Pure SQL)
**Technology**: BigQuery (SQL)
**Responsibility**: Structure, Types, Cleaning.
**Goal**: "Get the data ready for the robot."

*   **Characteristics**: Fast, visible, strictly typed.
*   **Allowed Operations**:
    *   `LOAD DATA`
    *   Regex Cleaning (`REGEXP_REPLACE`)
    *   Type Casting (`SAFE_CAST`)
    *   Structural Mapping
*   **Stages**: 0 (Assessment), 1 (Extraction), 2 (Cleaning), 4 (Staging).

## 🔴 Zone 2: The Danger Zone (Containerized Logic)
**Technology**: Cloud Run / Python
**Responsibility**: Identity, AI, NLP, Complex Business Logic.
**Goal**: "Do the hard things we can't do in SQL."

*   **Characteristics**: Isolate, Idempotent, Monitored.
*   **Allowed Operations**:
    *   **Identity Hashing** (The Gate)
    *   **NLP Segmentation** (spaCy)
    *   **LLM Inference** (Gemini/Claude)
    *   **Embedding Generation**
*   **Stages**: 3 (The Gate), 5 (L1 Tokens), 6 (L3 Sentences), 9-13 (Enrichment).

## 🔵 Zone 3: The Unified Zone (Pure SQL)
**Technology**: BigQuery (SQL)
**Responsibility**: Aggregation, Validation, Final Storage.
**Goal**: "assemble the product and put it on the shelf."

*   **Characteristics**: Aggregative, relational, strictly governed.
*   **Allowed Operations**:
    *   `JOIN` logic (Re-assembling parent/child entities)
    *   `GROUP BY` statistics
    *   `ASSERT` validation
    *   Final `INSERT` to Spine
*   **Stages**: 7 (L5 Messages), 8 (L8 Conversations), 14-16 (Finalization).

---

## vocabulary

| Term | Definition |
| :--- | :--- |
| **The Ingestion Zone** | The "Loading Dock". Raw data enters here. SQL only. |
| **The Danger Zone** | The "Reactor". Complex transformation happens here. Python only. |
| **The Unified Zone** | The "Warehouse". Finished entities live here. SQL only. |
| **Handoff Point** | The strict table schema where data moves from SQL ➡️ Python or Python ➡️ SQL. |
| **The Gate** | The specific Danger Zone process that assigns IDs. |

---

## 🔒 The Protocol: HOLD:AGENT:HOLD

The pipeline moves to a strict rhythm to ensure "every single one" is handled safely.

### 1. HOLD 1 (The Deep Freeze)
**Location**: Zone 1 (BigQuery Table: `HoldHold1`)
**Rule**: "User data lands here and STOPS."
*   Data is uploaded (PUT) to this table.
*   It is **Immutable**. We never edit this.
*   It acts as the "Inbox". If the pipeline breaks, the data is safe here.

### 2. AGENT (The Active Processor)
**Action**: The Pipeline triggers (SQL or Python).
*   It reads from `HoldHold1`.
*   It does its work (Cleaning, Identity, Enrichment).
*   It **never** corrupts `HoldHold1`.

### 3. HOLD 2 (The Shelf)
**Location**: Zone 3 (BigQuery Table: `spine.entity_unified`)
**Rule**: "Finished goods sit here."
*   The Agent places the finished entity here.
*   It waits here for the User (Layer 6) to use it.

---

## 🚀 Implementation Rule

When building a new pipeline:
1.  **Maximize Zone 1**: Do as much as possible in SQL first.
2.  **Minimize Zone 2**: Only enter the Danger Zone if BigQuery cannot do it.
3.  **Standardize Zone 3**: Always output to the standard Spine schema.
4.  **Enforce Hold 1**: Never process "on the fly". Always land in `HoldHold1` first.
