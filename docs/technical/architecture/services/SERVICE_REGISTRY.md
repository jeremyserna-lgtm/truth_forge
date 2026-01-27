# SERVICE REGISTRY: The Maximally Structured System

**Purpose**: Definitive catalog of all system services and their alignment with The Primitive Pattern.
**Generated**: 2026-01-06
**Pattern**: `HOLD₁ (Input) → AGENT (Transformation) → HOLD₂ (Output)`

---

## 1. THE FOUNDATION (The Walls)

These services enforce the structure. They must be present for anything else to exist.

| Service | Status | Purpose | Holds |
|---------|--------|---------|-------|
| **builder_service** | ✅ Compliant | **The Gatekeeper**. Enforces structure on new code. | `holds/builder/intake` → `processed` |
| **schema_service** | ✅ Compliant | **The Law**. Defines what data looks like. | `Metadata` (Registry) |
| **verification_service** | ✅ Compliant | **The Truth**. Checks if outputs match promises. | `holds/verification/intake` → `processed` |

---

## 2. THE CORE (The System)

These services operate the Cycle (`WANT → CHOOSE → ACT`).

| Service | Status | Purpose | Holds |
|---------|--------|---------|-------|
| **analysis_service** | ✅ Compliant | **The Brain**. Synthesizes system state into metrics. | `AGGREGATE` → `analysis.duckdb` |
| **truth_service** | ✅ Compliant | **The Stomach**. Digests raw text into Knowledge Atoms. | `truth_atoms.jsonl` → `truth_atoms.duckdb` |
| **knowledge_graph_service** | ✅ Compliant | **The Memory**. Stores nodes and edges. | `statements.jsonl` → `graph.duckdb` |
| **contacts** | ✅ Compliant | **The Network**. Syncs BigQuery contacts to local. | `contacts/intake` → `contacts.duckdb` |
| **script_service** | ✅ Compliant | **The Hands**. Intake for executable scripts. | `scripts/intake` → `scripts.duckdb` |

---

## 3. THE UTILITIES (The Tools)

These services provide capabilities to the Core or Foundation.

| Service | Status | Purpose | Holds |
|---------|--------|---------|-------|
| **model_gateway_service** | ✅ Compliant | **The Voice**. Routes prompts to LLMs (Ollama/Claude). | `model_gateway/intake` → `processed` |
| **sentiment_service** | ✅ Compliant | GoEmotions enrichment via Ollama. | `knowledge_atoms` → `sentiment.duckdb` |
| **frontmatter_service** | ✅ Compliant | YAML metadata stamping. | `RAW_FILES` → `frontmatter.duckdb` |
| **extractor_service** | ⚠️ Partial | Extracts content from sources. | `N/A` |

---

## 4. LEGACY / DEPRECATED

**Warning**: These locations have been **DELETED**.

*   `ai_cognitive_services/` (Deleted 2026-01-06)
*   `Primitive/central_services/` (Deleted 2026-01-06)

---

## AUDIT SUMMARY

*   **Total Services**: 12 tracked
*   **Compliant**: 11 (92%)
*   **Partial/Stub**: 1

**Maximal Structure Status**:
The Foundation, Core, and Utilities are now almost fully compliant with The Primitive Pattern.
