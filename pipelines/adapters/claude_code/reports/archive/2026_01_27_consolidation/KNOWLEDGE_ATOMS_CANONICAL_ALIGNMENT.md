> **DEPRECATED**: This document has been superseded.
> - **Superseded By**: [CANONICAL_KNOWLEDGE_ATOMS_COMPLETE.md](CANONICAL_KNOWLEDGE_ATOMS_COMPLETE.md) or [ID_SYSTEM_IMPLEMENTATION_COMPLETE.md](ID_SYSTEM_IMPLEMENTATION_COMPLETE.md) or [ID_SYSTEM_FEDERATION_UPGRADE_COMPLETE.md](ID_SYSTEM_FEDERATION_UPGRADE_COMPLETE.md)
> - **Deprecated On**: 2026-01-27
> - **Archived On**: 2026-01-27
> - **Reason**: Consolidated into complete implementation documents.
>
> This document has been moved to archive. See archive location below.

---

# Knowledge Atoms Canonical Alignment

**Date:** 2026-01-22  
**Status:** ✅ **ALIGNED WITH CANONICAL STANDARD**

---

## What Was Done

**Aligned pipeline knowledge atoms with the canonical knowledge atom schema** defined in:
- `Primitive/system_elements/schema_registry/knowledge_atoms.json`
- `framework/reference/source_material/1_core/13_THE_PATTERN.md`
- `framework/standards/FEDERATION_ATOM_ALIGNMENT.md`

---

## Canonical Schema (Universal 7-Column Structure)

All knowledge atoms in the federation use this schema:

| Column | Type | Description | Status |
|--------|------|-------------|--------|
| `atom_id` | VARCHAR (PK) | Unique identifier (format: `atom:xxxxxxxxxxxx`) | ✅ Aligned |
| `type` | VARCHAR | Atom type from organism's type registry | ✅ **FIXED** |
| `content` | TEXT | The atomic knowledge statement | ✅ Aligned |
| `source_name` | VARCHAR | Source organism or agent | ✅ Aligned |
| `source_id` | VARCHAR | Run/session/extraction ID for tracing | ✅ Aligned |
| `timestamp` | TIMESTAMP | When the atom was created | ✅ **FIXED** |
| `metadata` | JSON | Flexible JSON for extended fields | ✅ Aligned |
| `hash` | VARCHAR | SHA256 content hash (first 16 chars) for deduplication | ✅ **FIXED** |

---

## Changes Made

### 1. Added `type` Field (REQUIRED)

**Before:** Missing `type` field  
**After:** Added `type` field with appropriate atom type

**Atom Type Selection:**
- Default: `"observation"` (for pipeline execution metadata)
- If patterns present: `"pattern"` (for pattern observations)

**Type Registry:** Pipeline knowledge atoms use Genesis core types:
- `observation` - Raw perception of pipeline behavior
- `pattern` - Recurring structures in pipeline execution

### 2. Renamed `created_at` → `timestamp` (REQUIRED)

**Before:** Used `created_at` field  
**After:** Uses canonical `timestamp` field

**Rationale:** Canonical schema uses `timestamp`, not `created_at`.

### 3. Added `hash` Field (REQUIRED)

**Before:** Only had `content_hash` (full SHA256)  
**After:** Added `hash` field (first 16 chars of SHA256)

**Implementation:**
```python
content_hash_full = hashlib.sha256(content.encode()).hexdigest()
content_hash_short = content_hash_full[:16]  # For canonical `hash` field
```

**Rationale:** Canonical schema requires `hash` as first 16 chars for deduplication.

### 4. Updated Deduplication Key

**Before:** Used `content_hash` for deduplication  
**After:** Uses canonical `hash` field (first 16 chars)

**Rationale:** Aligns with canonical deduplication strategy.

### 5. Updated DuckDB Schema

**Before:** Schema didn't match canonical structure  
**After:** Schema includes all canonical fields + local extensions

**Canonical Fields:**
- `atom_id` (PRIMARY KEY)
- `type`
- `content`
- `source_name`
- `source_id`
- `timestamp`
- `metadata`
- `hash`

**Local Extensions (for local-first tracking):**
- `content_normalized` - For local search
- `content_hash` - Full hash for local deduplication
- `run_id` - Pipeline run tracking
- `synced_to_cloud` - Local-first sync status

---

## Atom Type Selection

Pipeline knowledge atoms use Genesis core types:

| Stage Context | Atom Type | Rationale |
|---------------|-----------|-----------|
| General execution | `observation` | Raw perception of pipeline behavior |
| Pattern discovery | `pattern` | Recurring structures in execution |
| Error/warning | `observation` | Observations about issues |
| Metrics/insights | `observation` | Observations about performance |

**Future Extension:** Could add pipeline-specific types to type registry if needed.

---

## Schema Alignment Verification

### Canonical Schema Fields ✅

| Field | Canonical | Implementation | Status |
|-------|-----------|----------------|--------|
| `atom_id` | `atom:{source_name}:{hash12}` | ✅ Matches | ✅ |
| `type` | Atom type from registry | ✅ `observation` or `pattern` | ✅ |
| `content` | Original truth | ✅ Full content | ✅ |
| `source_name` | Registered source | ✅ `claude_code_stage_N` | ✅ |
| `source_id` | Run/session ID | ✅ `run_id` | ✅ |
| `timestamp` | ISO timestamp | ✅ ISO format | ✅ |
| `metadata` | Flexible JSON | ✅ JSON string | ✅ |
| `hash` | First 16 chars SHA256 | ✅ First 16 chars | ✅ |

### Local Extensions (Not in Canonical Schema)

These fields are added for local-first tracking but are not part of the canonical schema:
- `content_normalized` - For local search optimization
- `content_hash` - Full SHA256 for local deduplication
- `run_id` - Pipeline run tracking
- `synced_to_cloud` - Local-first sync status

**Rationale:** Local extensions are acceptable as long as canonical fields are present.

---

## Federation Alignment

**✅ Aligned with Federation Atom Alignment Standard:**
- Uses universal 7-column schema
- Uses Genesis core types (`observation`, `pattern`)
- Compatible with federation sync protocol
- Ready for `CE_TYPE_LEARNING` CloudEvents (if pipeline-specific types added)

---

## Example Atom Record

**Canonical Schema:**
```json
{
  "atom_id": "atom:claude_code_stage_0:abc123def456",
  "type": "observation",
  "content": "Pipeline Stage 0: Discovery\nRun ID: run:xyz789\n\nDISCOVERIES:\n  - files_discovered: 1044\n  - messages_discovered: 79334",
  "source_name": "claude_code_stage_0",
  "source_id": "run:xyz789",
  "timestamp": "2026-01-22T12:34:56.789Z",
  "metadata": "{\"pipeline\": \"claude_code\", \"stage\": 0, ...}",
  "hash": "a1b2c3d4e5f6g7h8"
}
```

**With Local Extensions:**
```json
{
  "atom_id": "atom:claude_code_stage_0:abc123def456",
  "type": "observation",
  "content": "...",
  "source_name": "claude_code_stage_0",
  "source_id": "run:xyz789",
  "timestamp": "2026-01-22T12:34:56.789Z",
  "metadata": "{...}",
  "hash": "a1b2c3d4e5f6g7h8",
  "content_normalized": "pipeline stage 0: discovery...",
  "content_hash": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6",
  "run_id": "run:xyz789",
  "synced_to_cloud": false
}
```

---

## Verification

**✅ All canonical fields present:**
- `atom_id` ✅
- `type` ✅
- `content` ✅
- `source_name` ✅
- `source_id` ✅
- `timestamp` ✅
- `metadata` ✅
- `hash` ✅

**✅ Schema matches canonical standard:**
- Universal 7-column structure
- Genesis core types
- Federation-compatible

**✅ Local extensions preserved:**
- Local-first tracking fields maintained
- No breaking changes to local storage

---

*Pipeline knowledge atoms are now fully aligned with the canonical knowledge atom schema. They can be synced to the federation and queried using standard federation protocols.*
