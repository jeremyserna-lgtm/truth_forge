# THE REDUCTION

**Version**: 1.0
**Status**: Living Document

---

## Document Structure

- **Theory**: Why sprawl happens and how to fix it
- **Specification**: The full reduction pipeline
- **Reference**: How to use the tools

---

# THEORY

## The Problem

Sprawl happens naturally:
- Copy a script to modify it → two scripts
- Can't find something → write it again
- Different people → different versions
- Time passes → cruft accumulates

**Sprawl costs:**
- Search time (where is the thing?)
- Confusion (which version is right?)
- Maintenance (fixing the same bug N times)
- Cognitive load (keeping it all in your head)

## The Solution

```
SPRAWL → HASH → CLUSTER → DEDUPE → CANONICALIZE → ARCHIVE → CORE → ATOMS
```

1. **Hash everything** - exact match detection
2. **Embed everything** - similarity detection
3. **Cluster** - group related files
4. **Dedupe** - remove exact duplicates
5. **Canonicalize** - identify the "one true version"
6. **Archive** - move similar/duplicate to cold storage
7. **What remains = Core**
8. **Organize core into atoms** - fundamental units

## The Insight

**Hash + Embed = Dedup + Similarity**

- **Hash** (SHA256): Exact byte-for-byte match
- **Embed** (BGE-large): Semantic similarity

Together they catch:
- Exact copies (hash match)
- Near copies (>95% similarity)
- Similar purpose (>85% similarity)
- Related code (>70% similarity)

---

# SPECIFICATION

## Phase 1: Scan

Hash all files, register centrally.

```bash
python sprawl_reducer.py scan /path/to/codebase
```

**What it does:**
- Walks directory tree
- Skips: `.git`, `venv`, `node_modules`, `__pycache__`
- Hashes each file (normalized)
- Records: path, hash, size, lines, modified, type

**Output:**
```
~/.primitive_engine/sprawl_reduction/scan_results.jsonl
```

## Phase 2: Embed

Generate embeddings for similarity search.

```bash
python sprawl_reducer.py embed
```

**What it does:**
- Loads BGE-large model
- Embeds each file's content
- Stores in numpy format for fast search

**Output:**
```
~/.primitive_engine/sprawl_reduction/embeddings.npz
```

## Phase 3: Cluster

Group by similarity.

```bash
python sprawl_reducer.py cluster
```

**Thresholds:**
| Similarity | Category |
|------------|----------|
| 1.0 | Exact duplicate |
| >0.95 | Near duplicate |
| >0.85 | High similarity |
| >0.70 | Moderate similarity |

**Output:**
```
~/.primitive_engine/sprawl_reduction/clusters.json
```

## Phase 4: Canonicalize

Identify the "one true version" per cluster.

```bash
python sprawl_reducer.py canonicalize
```

**Heuristics (scored):**
1. Location: `/scripts/` or `/pipelines/` → +100
2. Location: `/architect_central_services/` → +50
3. Location: `/tests/` → -50
4. Location: `/archive/` or `/old/` → -100
5. Completeness: more lines → +1 per line (capped)
6. Recency: more recent → small bonus
7. Naming: `temp`, `test`, `old` → -50

**Highest score wins.**

## Phase 5: Archive

Move non-canonical files to cold storage.

```bash
# Preview
python sprawl_reducer.py archive --dry-run

# Execute locally
python sprawl_reducer.py archive --execute

# Execute to GCS
python sprawl_reducer.py archive --gcs-bucket my-bucket --execute
```

**Actions:**
| File Type | Action |
|-----------|--------|
| Canonical | Keep |
| Exact duplicate | Delete |
| Near duplicate | Archive |
| Similar | Archive |

**Output:**
```
~/.primitive_engine/sprawl_reduction/archive_manifest.jsonl
~/.primitive_engine/sprawl_reduction/archive/  (local)
gs://bucket/sprawl_archive/YYYYMMDD/  (GCS)
```

## Phase 6: Atoms

Organize core into fundamental units.

```bash
python atom_organizer.py analyze /path/to/core
python atom_organizer.py dependencies
python atom_organizer.py categorize
python atom_organizer.py suggest
```

**Atom categories:**
| Category | Purpose |
|----------|---------|
| core | Central business logic |
| io | Input/output, file handling |
| transform | Data transformation |
| validate | Validation, checking |
| config | Configuration |
| util | Utilities |
| test | Testing |

**Output:**
```
~/.primitive_engine/atoms/atoms.json
~/.primitive_engine/atoms/dependencies.json
~/.primitive_engine/atoms/suggestions.json
```

---

# REFERENCE

## Full Pipeline

```bash
# One command for everything (dry run)
python sprawl_reducer.py execute /path/to/codebase --dry-run

# Actually do it
python sprawl_reducer.py execute /path/to/codebase --confirm

# Then organize atoms
python atom_organizer.py analyze /path/to/codebase
python atom_organizer.py suggest
```

## Reports

```bash
# Sprawl report
python sprawl_reducer.py report

# Atom report
python atom_organizer.py report
```

## Example Report

```
══════════════════════════════════════════════════════════════════════
SPRAWL REDUCTION REPORT
══════════════════════════════════════════════════════════════════════

Files scanned:      847
Clusters found:     156
Exact duplicates:   89
Near duplicates:    67
Similar files:      134
──────────────────
Files to archive:   290
Core files:         557
Reduction:          34.2%

Size savings:       12.4 MB

Top clusters:
  cluster_0001: 12 files, 8 exact dupes
    → canonical: process_data.py
  cluster_0002: 8 files, 3 exact dupes
    → canonical: utils.py
══════════════════════════════════════════════════════════════════════
```

## Files

| File | Purpose |
|------|---------|
| `scripts/sprawl_reducer.py` | Sprawl reduction pipeline |
| `scripts/atom_organizer.py` | Atom extraction and organization |
| `~/.primitive_engine/sprawl_reduction/` | All sprawl data |
| `~/.primitive_engine/atoms/` | All atom data |

## Integration with Enforcement

After reduction:
1. Core files are registered in script registry
2. New files checked against core for similarity
3. Similar → blocked (use existing)
4. New → enforcement flow
5. Approved → registered

```
Sprawl Reduction (one-time) → Core
                               ↓
                         Script Registry
                               ↓
                    Enforcement (ongoing)
```

---

## The Principle

**Sprawl → Core → Atoms**

1. Hash everything
2. Cluster by similarity
3. Delete exact duplicates
4. Archive near duplicates
5. What remains = canonical core
6. Extract atoms (functions, classes)
7. Organize atoms by purpose
8. Enforce going forward

**First clean the house. Then keep it clean.**

---

*This document follows THE_FRAMEWORK structure: Theory, Specification, Reference.*
*— THE_REDUCTION*
