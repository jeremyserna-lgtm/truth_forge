---
title: Automatic Anchor Signal Specification
status: draft
owner: Jeremy Serna / Architect Library
created: 2025-10-30
---

# Automatic Anchor Signal Specification

## 1. Purpose

We need Gemini Pro 2.5 to extend the existing document vacuum so that *anchor documents* are detected and handled automatically. The system must rely on factual signals captured during ingestion instead of Jeremy manually labelling files. Anchors should “shine” because of how they behave in the corpus, not because someone asserted it.

This document defines the requirements Gemini should implement.

## 2. System Context

- **Phase 1 – Vacuum:** `tools/document_vacuum.py` reads Markdown files, validates structure, captures canonical metadata, and either shreds the document into the spine tables or routes it through the `AnchorDocumentProtocol`. It already injects a YAML header with canonical metadata and writes records to BigQuery.
- **Phase 2 – Enrichment:** downstream services enrich the vacuumed content asynchronously and can be rerun.
- **Anchor protocol today:** a heuristic inside `AnchorDocumentProtocol.is_anchor_document()` that treats very large architecture documents as anchors and bypasses shredding. It does **not** look at YAML front matter or other intent markers; detection is purely size/keyword‑based.
- **Goal:** generalise anchor detection so that the vacuum can recognise high-value documents without manual tagging, record *why* they were flagged, and keep the detection auditable.

## 3. Functional Requirements

### 3.1 Detection Inputs
Gemini must extract the following signals while the vacuum still has filesystem access:

| Category | Signals | Notes |
| --- | --- | --- |
| **Structure** | word count, character count, counts of H1/H2/H3/H4, depth ratios, section density | Already computed via `extract_metadata`; may need minor extensions (e.g., paragraphs per section). |
| **Content** | presence of architecture keywords, governance terms, code/SQL blocks, references to schemas (`spine.*`, `enrichment.*`, etc.), presence of AI agent names | Extend the keyword lists in `AnchorDocumentProtocol`. |
| **Connectivity** | number of intra-library references (links to other docs), backlinks (Phase 1 can compute by scanning Markdown links), git statistics (file age, author count), recency of edits | Git stats already accessible via filesystem. Link analysis should be deterministic. |
| **Activity-derived** | how often the doc is opened or vacuumed (available via BigQuery queries) — this must be *captured as metadata* post‑ingest but the detection threshold must execute during vacuum using latest cached stats. |

### 3.2 Feature Engineering
Gemini must implement a deterministic scoring function:

1. Normalise each signal (e.g., scale counts to 0–1).
2. Apply weighted coefficients (documented in code with rationale).
3. Produce `anchor_score` (0–100).
4. If `anchor_score ≥ anchor_threshold` (default 70), mark document as anchor.

Detection must be reproducible: given the same file and configuration, the score is identical.

### 3.3 Metadata Capture
When a document is flagged:

- Append to Phase 1 metadata:
  ```yaml
  anchor_detection:
    is_anchor: true
    score: 82
    threshold: 70
    triggered_signals:
      - size_over_50k_chars
      - architecture_keywords
      - references_spine_schema
      - high_link_degree
    evaluated_at: 2025-10-30T19:42:11Z
  ```
- Persist the same structure to the BigQuery metadata table (`governance.anchor_index` or equivalent).
- Log an audit entry referencing `document_id`, score, threshold, and signals.

### 3.4 Routing Behaviour

- If `is_anchor: true`, process through `AnchorDocumentProtocol` (upload whole file to `genesis-anchors`, do **not** shred into spine).
- If false, continue with normal shredding.
- Manual overrides:
  - If YAML front matter contains `anchor_override: true/false`, apply it **after** computing the score, but record the override in metadata (`override_source: "front_matter"`).
  - Overrides must be auditable and must not erase the calculated score.

### 3.5 Configuration

- Provide a configuration block in `document_vacuum.yaml`:
  ```yaml
  anchor_detection:
    enabled: true
    threshold: 70
    weights:
      size: 0.25
      architecture_keywords: 0.2
      governance_terms: 0.15
      code_density: 0.15
      link_centrality: 0.15
      git_activity: 0.1
  ```
- All weights and thresholds must be overridable via config without code changes.
- Include feature flags to disable detection (`VACUUM_DISABLE_ANCHOR=1`) and to bypass overrides for testing.

## 4. Non-Functional Requirements

1. **Determinism:** Running the vacuum twice with identical inputs must produce identical scores and anchor decisions.
2. **Performance:** Additional scoring logic must not add more than ~100 ms per document on average.
3. **Observability:** Emit structured logs/events when scoring occurs. Include aggregated metrics (mean/median anchor score) for daily reporting.
4. **Testability:** Ship unit tests covering:
   - Score calculation for synthetic documents.
   - Signal extraction functions.
   - Override logic precedence.
5. **Backward compatibility:** Existing manual anchor protocol API (`AnchorDocumentProtocol`) must stay callable. If detection fails or throws, degrade gracefully to current behaviour and log the failure.

## 5. Deliverables for Gemini

1. Updated `tools/document_vacuum.py` with:
   - Signal extraction enhancements.
   - Scoring and metadata injection logic.
   - Config integration.
2. Updated `tools/anchor_document_protocol.py` (if required) to accept score input rather than re‑deriving signals.
3. Config schema additions documenting the new anchor detection block.
4. Unit/integration tests (pytest) covering scoring, overrides, and pipeline routing.
5. Structured documentation (inline docstrings + README update) describing how to tune thresholds and interpret logs.

## 6. References

- `tools/document_vacuum.py`
- `tools/anchor_document_protocol.py`
- BigQuery tables: `governance.anchor_index`, `spine.document`
- Phase separation principle: `docs/analysis/PRE_VACUUM_CHECKLIST_FOR_GEMINI_PRO.md`

---

**Instructions for Gemini Pro 2.5:** Implement the above changes, ensure tests pass, and provide a diff-ready patch. This spec is guaranteed to be used inside the Architect Library vacuum pipeline—no simulated context necessary.
