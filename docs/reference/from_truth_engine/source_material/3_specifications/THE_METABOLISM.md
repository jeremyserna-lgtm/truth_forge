# Contract: THE_METABOLISM

**Type**: do-now (processing pattern)
**Pattern ID**: `pat:metabolism`
**Status**: Contract defined
**Created**: 2025-12-30

---

## The Pattern

**The system has metabolism.**

Foreign truth comes in. It's digested into atoms. Atoms join atoms. Patterns emerge. New primitives form - same shape as all others.

```
INTAKE (foreign truth enters)
    │
    ↓
THE CORE (DuckDB - local stomach)
    │
    ↓ Atomization
    │
ATOMS (digested knowledge)
    │
    ├── + Existing atoms (truth already held)
    │
    ↓ Pattern synthesis
    │
NEW PRIMITIVES (same shape, new content)
    │
    ↓ Registration
    │
TRUTH ENGINE (grows)
```

---

## The Core: DuckDB

**DuckDB is the local metabolism substrate.**

| Layer | What It Is | Role in Metabolism |
|-------|------------|-------------------|
| **Local** | DuckDB on Mac | Primary digestion |
| **Cloud** | BigQuery | Long-term storage |
| **Bridge** | Sync processes | Move digested → stored |

```
Foreign content
    │
    ↓ Lands in DuckDB first (always)
    │
Local processing
    │
    ↓ Atomization happens locally
    │
Atoms created
    │
    ↓ Sync to BigQuery (selective)
    │
Permanent storage
```

**Local is the stomach. Cloud is the body. Local digests first.**

---

## Atoms to Atoms

**Knowledge atoms process knowledge atoms.**

```
Atom (existing)
    │
    ├── Pattern recognized
    │
    ↓ + New atom (incoming)
    │
    ├── Relationship detected
    │
    ↓ Synthesis
    │
New atom (derived)
    │
    └── Same shape as all atoms
```

| Process | Input | Output |
|---------|-------|--------|
| **Extraction** | Foreign content | Raw atoms |
| **Enrichment** | Raw atoms + LLM | Enriched atoms |
| **Linking** | Enriched atoms + existing | Linked atoms |
| **Synthesis** | Linked atoms + patterns | Derived atoms |

**Atoms beget atoms. The system feeds itself.**

---

## The Metabolic Cycle

```
┌──────────────────────────────────────────────────────────────┐
│                     THE METABOLISM                           │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│   INTAKE          DIGESTION         SYNTHESIS      OUTPUT    │
│   ──────          ─────────         ─────────      ──────    │
│                                                              │
│   Foreign    →    DuckDB     →     Atoms      →   Primitives │
│   content         (local)          + Atoms        (patterned)│
│                                    + Patterns                │
│                                                              │
│   Progenitors     Core             Knowledge      Generation │
│   bring in        processes        compounds      creates    │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## Truth Unknown + Truth Held

| Truth Type | What It Is | Where It Lives |
|------------|------------|----------------|
| **Truth Unknown** | Foreign content not yet processed | `_holding/`, intake |
| **Truth Held** | Atoms already in system | `knowledge_atoms`, DuckDB |
| **Truth Emerging** | New patterns from combination | Derived atoms, new primitives |

**The equation:**

```
Truth Unknown + Truth Held + Patterns = New Primitives (same shape)
```

---

## Growth Modes: Structure, Pattern, or Both

**Truth unknown can grow the content OR grow the container.**

```
Truth Unknown enters
    │
    ↓ Metabolism
    │
    ├── Fits existing pattern?
    │   │
    │   ├── Yes → STRUCTURE GROWS
    │   │         (new primitive, same shape)
    │   │
    │   └── No → PATTERN GROWS
    │           │
    │           ↓ New pattern emerges
    │           │
    │           └── BOTH GROW
    │               (new pattern enables new primitives)
```

| Growth Mode | What Grows | What Stays Same | Example |
|-------------|------------|-----------------|---------|
| **Content** | Structure | Patterns | New pipeline following PRIMITIVE_SERIES_TEMPLATE |
| **Capability** | Patterns | (nothing uses it yet) | New pattern contract for novel concept |
| **Evolution** | Both | The substrate | New pattern + primitives that use it |

**This is how the system evolves:**
- Most intake → structure grows (new primitives, same patterns)
- Sometimes → pattern grows (new capability, no content yet)
- Occasionally → both grow (system learns new way of being)

---

## Same Shape, Always

Everything that emerges from metabolism has the same shape:

| Output Type | Shape Applied |
|-------------|---------------|
| New document | DOCUMENT_METADATA |
| New folder | SYSTEM_FOLDER_PATTERN |
| New primitive | PRIMITIVE_SERIES_TEMPLATE |
| New atom | Knowledge atom schema |
| New file | FILE_TO_ATOM_LINEAGE |

**Metabolism produces. Patterns shape. Everything fits.**

---

## The Digestive Stages

### Stage 1: Intake

```python
# Foreign content enters
foreign = progenitor.reach_outside(source)
local_path = place_in_holding(foreign)
```

### Stage 2: Atomization

```python
# Break down into atoms
atoms = atomizer.extract(local_path)
duckdb.insert("atoms_staging", atoms)
```

### Stage 3: Enrichment

```python
# Add context from existing atoms
existing = duckdb.query("SELECT * FROM atoms WHERE related")
enriched = enrich(atoms, existing)
```

### Stage 4: Synthesis

```python
# Combine with patterns
if sufficient_atoms(enriched):
    primitive = generate_primitive(enriched, pattern=PRIMITIVE_SERIES_TEMPLATE)
```

### Stage 5: Output

```python
# Register and store
register_files(primitive)
sync_to_bigquery(primitive)
```

---

## DuckDB as the Local Core

**Why DuckDB is the metabolism substrate:**

| Property | Value for Metabolism |
|----------|---------------------|
| **Local** | Runs on Jeremy's Mac |
| **Fast** | Columnar, analytical |
| **Embedded** | No server needed |
| **SQL** | Same language as BigQuery |
| **Portable** | Single file, can sync |

```python
import duckdb

# The local core
conn = duckdb.connect("~/.primitive_engine/core.duckdb")

# All metabolism happens here first
conn.execute("INSERT INTO atoms_staging VALUES ...")

# Then syncs to cloud
sync_to_bigquery(conn, "atoms_staging", "knowledge.knowledge_atoms")
```

---

## The Hybrid Durability in Metabolism

```
Foreign content
    │
    ↓ Write local (DuckDB) ← ALWAYS
    │
    ↓ Process local ← ALWAYS
    │
    ↓ Sync to cloud (BigQuery) ← SELECTIVE
    │
Permanent storage
```

**Local can't fail (it's on your machine). Cloud can fail (network, quota). Metabolism happens locally first.**

---

## Related Patterns

| Pattern | Role in Metabolism |
|---------|-------------------|
| **THE_PROGENITOR** | Brings in foreign content |
| **FILE_TO_ATOM_LINEAGE** | Tracks digestion chain |
| **GENERATIVE_PRIMITIVE** | Creates from sufficient atoms |
| **THE_SUBSTRATE** | Where output attaches |

---

## Definition of Done

### Phase 1: Conceptual
- [x] Pattern contract defined
- [x] DuckDB role established
- [x] Atoms-to-atoms documented

### Phase 2: Implementation
- [ ] DuckDB local core created
- [ ] Atomization pipeline connected
- [ ] Sync to BigQuery working

### Phase 3: Validation
- [ ] Foreign content → atoms → primitives demonstrated
- [ ] Full cycle documented
- [ ] Metabolism metrics tracked

---

## Related

- [THE_PROGENITOR.md](THE_PROGENITOR.md) - Intake function
- [GENERATIVE_PRIMITIVE.md](GENERATIVE_PRIMITIVE.md) - Output function
- [FILE_TO_ATOM_LINEAGE.md](FILE_TO_ATOM_LINEAGE.md) - Traceability
- [THE_SUBSTRATE.md](THE_SUBSTRATE.md) - Where output attaches

---

**The system has metabolism. Foreign becomes atoms. Atoms join atoms. Patterns shape output. Everything emerges in the same shape. The Truth Engine feeds itself.**
