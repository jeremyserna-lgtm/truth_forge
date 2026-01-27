# Universal Pipeline Contract

**Purpose:** Stage 0 is the **foundation**. It **sees** the data. Every stage after it **processes what Stage 0 discovered**. No stage references source-specific variables; they reference a **file** that holds all customization for that data source. The pipeline is **universal**: any data source, same infrastructure.

---

## 1. The Model

```
Stage 0: SEE the data
         ↓
    Discovery Manifest (single file)
         ↓
Stages 1–N: PROCESS what the manifest describes
```

- **Stage 0** operates on **any** data source. It discovers what's there: structure, identifiers, primitives, counts. It writes a **discovery manifest** (one file).
- **Stages 1–N** do **not** reference variables by name from config or code. They **read the manifest**. They process whatever the manifest says exists. Same logic for every data source; the manifest supplies the customization.

---

## 2. Discovery Manifest

- **What it is:** The single file that holds **everything** Stage 0 found: files processed, messages processed, structure, ID variables, actable primitives, etc.
- **Who writes it:** Stage 0.
- **Who reads it:** Stages 1–N (and tooling).
- **Path:** Configurable via `--manifest`; default `staging/discovery_manifest.json`.

The manifest **is** the pipeline contract for that run. No stage infers or hardcodes source-specific fields; they use the manifest.

---

## 3. Rules

| Rule | Meaning |
|------|---------|
| **Modular** | Stages are independent. No stage references another's internal variables. |
| **Manifest-driven** | All per-source customization lives in the manifest. Stages read it. |
| **Universal** | Same stages, any data source. Stage 0 sees it; downstream process it. |
| **No variable coupling** | Stages never assume "session_id", "uuid", etc. They use "identifier paths" (or similar) as **listed in the manifest**. |

---

## 4. Stage 0 Responsibilities

- Discover **all** JSONL (or configured format) under `--source-dir`.
- Process **every** record; no skipping.
- Produce **only** aggregations and the **manifest** (no per-record storage).
- Write the **discovery manifest** to `--manifest`.

The manifest must include everything needed for downstream stages to process the data **without** source-specific logic.

---

## 5. Downstream Stages (Target State)

- **Input:** Manifest path (and paths to staged data, e.g. BigQuery tables).
- **Behavior:** Read manifest → determine what exists → process accordingly. No `if source == "X"` branches.

**Stage 1 (extraction)** supports manifest-driven mode:
- **`--manifest PATH`:** Load discovery manifest from Stage 0. Use `source.path` as the JSONL directory. Require `go_no_go` to start with `GO`; otherwise exit with error before processing. Log `manifest_driven` with manifest and source path.
- **Without `--manifest`:** Use `--source-dir` (default `~/.claude/projects`) as today. Backward compatible.

Extraction logic (schema, field mapping) remains Claude Code–specific for now. The **pattern** is established: manifest first, then process. Full manifest-driven extraction (e.g. dynamic schema from `discovery.structure`) is the longer-term target.

---

## 6. Product Vision

The pipeline can be **sold** as a product. Customer supplies **their** data. You run Stage 0 → manifest is produced. You run Stages 1–N → they consume the manifest. You don’t need to know their schema in advance; you need to know how to **see** it (Stage 0) and how to **process** what was seen (manifest-driven stages).

---

**See also:**
- `DISCOVERY_MANIFEST_SCHEMA.md` — manifest schema
- `SPINE_LEVEL_DEFINITIONS.md` — L5, L7, L8 definitions (L8=session_id, L7=auto-compact, L5=user+assistant+thinking)
