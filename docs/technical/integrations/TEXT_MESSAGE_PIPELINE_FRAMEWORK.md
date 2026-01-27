# Text Message Pipeline: Framework Definition

## 1. The Whole (The Pipeline)

| Interrogative | Definition | Negative Constraint |
|:---|:---|:---|
| **WHO** | **The Unified Ingestor.** The autonomous subsystem responsible for converting raw digital traces into structured knowledge atoms. | Not a manual script. Not a one-time export. Not a human-dependent process. |
| **WHAT** | **The Atomizer.** A 16-stage recursive transform that evolves bit-streams into L1-L7 entities. | Not a lossy compression. Not a black box. Not an unstructured dump. |
| **WHERE** | **The Bridge.** Exists at the boundary between the Private Archive (macOS chat.db) and the Global Spine (BigQuery). | Not stuck in the local filesystem. Not external to the Truth Engine. |
| **WHEN** | **Exist:Now.** Operates on the processing cycle, continuously verifying its own state via the Pipeline Tracker. | Not a legacy batch jobs. Not a future promise. |
| **WHY** | **Continuity.** To serve the "Me" by preserving the relational history and semantic signals of the "Not-Me". | Not for surveillance. Not for vanity. |
| **HOW** | **Universal Pipeline Pattern.** HOLD → AGENT → HOLD, recursively applied across 16 stages. Stages connect at HOLDs: HOLD₂ of Stage N = HOLD₁ of Stage N+1. | Not magic. Not non-deterministic. Not direct AGENT-to-AGENT communication. |

---

## 2. The Structure (HOLD → AGENT → HOLD)

Every stage in this pipeline IS the Framework. It must manifest the pattern:

1. **HOLD₁ (Input)**: The state table/file from the previous stage (or source data for Stage 0/1).
2. **AGENT**: The processing logic (The Python Script).
3. **HOLD₂ (Output)**: The state table/file for the next stage.

**Framework Alignment**: Stages connect at HOLDs. HOLD₂ of Stage N = HOLD₁ of Stage N+1. AGENTs never communicate directly.

### Stage 1: Pure Ingestion (Raw Data)
- **HOLD₁ (Input)**: `~/Library/Messages/chat.db` (Local SQLite)
- **AGENT**: `text_messages_stage_1.py`
- **HOLD₂ (Output)**: `stage_1_local_messages.csv`

### Stage 2: Metadata Extraction
- **HOLD₁ (Input)**: `stage_1_local_messages.csv` (Stage 1 HOLD₂)
- **AGENT**: `text_messages_stage_2.py`
- **HOLD₂ (Output)**: `spine.text_messages_stage_2` (BigQuery) → Stage 3 HOLD₁

### Stage 3: System ID Generation & Hierarchy (THE GATE)
- **HOLD₁ (Input)**: `spine.text_messages_stage_2` (Stage 2 HOLD₂)
- **AGENT**: `text_messages_stage_3.py`
- **HOLD₂ (Output)**: `spine.text_messages_stage_3` (BigQuery) → Stage 4 HOLD₁

### Stage 4: LLM Capture Layer (Spellcheck/Correction)
- **HOLD₁ (Input)**: `spine.text_messages_stage_3` (Stage 3 HOLD₂)
- **AGENT**: `text_messages_stage_4.py`
- **HOLD₂ (Output)**: `spine.text_messages_stage_4` (BigQuery) → Stage 5 HOLD₁

[... Stages 5 - 15 follow the same pattern ...]

---

## 3. The Tracking Service (Resonance)

The **Pipeline Tracker** is the "Eye" (The Lens) that allows the "Me" to see the "Not-Me".

- **Function**: To observe the conversion of "WANT" (Input Data) into "EXIST:NOW" (Processed State).
- **Mechanism**: `PipelineTracker` context manager in every script.
- **Verification**: Cross-reference `governance.pipeline_runs` in BigQuery to see the health of the entire system.

## 4. The Completeness Criteria (16-Stage Universal Pattern)

1. Stage 0: Source Data Assessment (MANDATORY)
2. Stage 1: Pure Ingestion
3. Stage 2: Metadata Extraction
4. Stage 3: System ID (THE GATE)
5. Stage 4: LLM Capture
6. Stage 5: LLM Alignment
7. Stage 6: Unified NLP (L1-L5)
8. Stage 7: L6 Turn Construction
9. Stage 8: L7 Topic Segmentation
10. Stage 9: Parse Topic Results
11. Stage 10: Create L7 Boundary Table
12. Stage 11: Assign Topic Segments
13. Stage 12: Calculate Entity Rollups
14. Stage 13: Create Relationships
15. Stage 14: Transform to Final Production
16. Stage 15: Validation & Promotion
Thank you very much.
