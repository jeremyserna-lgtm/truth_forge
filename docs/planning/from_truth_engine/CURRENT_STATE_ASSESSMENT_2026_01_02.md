# Current State Assessment: Knowledge Architecture & Deduplication
**Date:** January 2, 2026
**Status:** CRITICAL ARCHITECTURAL MISALIGNMENT DETECTED

## Executive Summary
The system is currently in a **split-brain state**. While the `RAGDocumentService` correctly implements the new "Local First" (Intake/Outtake) pattern, the `KnowledgeAtomService` is still operating on the legacy "Direct-to-Cloud" pattern. This means there is currently **no valid local destination** for knowledge atoms, and no mechanism to bridge them to the cloud later.

## 1. Architectural Alignment Check

| Component | Standard (Expected) | Current Reality (Found) | Status |
|-----------|---------------------|-------------------------|--------|
| **RAG Document Service** | **Intake/Outtake**<br>(JSONL → DuckDB → BQ) | **Aligned**<br>Writes to `~/.primitive_engine/rag/documents.jsonl`<br>Reads from `~/.primitive_engine/truth.duckdb` | ✅ **PASS** |
| **Knowledge Atom Service** | **Intake/Outtake**<br>(JSONL → DuckDB → BQ) | **Legacy / Violation**<br>Writes/Reads directly from BigQuery (`knowledge_atoms` dataset).<br>No local DuckDB table exists for atoms. | ❌ **FAIL** |
| **Deduplication** | **Pipeline**<br>(Hash → ID → Similarity → Canonical) | **Missing**<br>Only checks `_is_document_processed(id)` in BigQuery.<br>No content hashing or semantic clustering. | ❌ **FAIL** |
| **The Bridge** | **Sync Daemon**<br>(DuckDB → BigQuery) | **Missing**<br>No code found to sync local DuckDB tables to BigQuery. | ❌ **FAIL** |

## 2. Detailed Findings

### A. The "Hidden" RAG Service
*   **Location**: `architect_central_services/src/architect_central_services/rag/service.py`
*   **State**: It exists and is partially functional.
*   **Data**: It has created `~/.primitive_engine/truth.duckdb` (3.6MB) and `documents.jsonl` (2.0MB).
*   **Issue**: It was not properly registered in `__init__.py` or Service Discovery, making it invisible to the rest of the system.

### B. The Knowledge Atom Service Violation
*   **Location**: `architect_central_services/src/architect_central_services/knowledge_service/service.py`
*   **Violation**: It imports `get_bigquery_client` and executes SQL queries directly against Google Cloud.
*   **Impact**:
    1.  **Cost**: Every extraction check incurs a BQ query cost.
    2.  **Offline Failure**: Cannot run without internet/GCP credentials.
    3.  **Data Silo**: Atoms created locally are sent to the cloud immediately, bypassing the local "Hold" (DuckDB).

### C. The Deduplication Gap
*   **Current Logic**: "Has this `document_id` been seen before?"
*   **The Flaw**: If `file_A.md` and `copy_of_file_A.md` have different filenames, they get different `document_id`s (unless the ID generation is purely content-hash based, which needs verification).
*   **Missing**:
    *   No "Inventory" step to catch exact duplicates before processing.
    *   No "Similarity" step to catch near-duplicates.
    *   No "Canonicalization" step to merge clusters.

## 3. The "Missing Bridge"
Since the architecture changed to "Local First," we are missing the **Sync Layer**.
*   **Current**: Scripts write to JSONL/DuckDB (RAG) OR BigQuery (Atoms).
*   **Required**: A unified mechanism that:
    1.  Watches local DuckDB tables.
    2.  Batches updates.
    3.  Upserts them to BigQuery (The Bridge).

## 4. Immediate Recommendations (Stop & Fix)
1.  **Do NOT run extraction** until `KnowledgeAtomService` is refactored to write to local DuckDB first.
2.  **Do NOT trust existing data** in `truth.duckdb` or BigQuery `knowledge_atoms` as it likely contains duplicates.
3.  **Formalize the Schema**: We need to define the `knowledge_atoms` table in DuckDB to match the BigQuery schema.

---
*This document serves as the "Hold" state. No actions will be taken until this reality is acknowledged.*
