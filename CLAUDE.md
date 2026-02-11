# truth_forge — agent instructions

## start here

**you are an AI agent working on truth_forge.** before doing anything:

1. **read the agent knowledge center**: [.agent/INDEX.md](.agent/INDEX.md)
2. **know the framework**: [framework/](framework/)
3. **know the standards**: [framework/standards/INDEX.md](framework/standards/INDEX.md)

---

## THE GRAMMAR

this project follows THE GRAMMAR OF IDENTITY:

| who | pronouns | mark | voice | example |
|-----|----------|------|-------|---------|
| ME | I, me, my | : | ALL CAPS | `ME:NOT-ME` |
| US | we, us, our | - | Normal Caps | Truth-Forge |
| NOT-ME | you, your | _ | no caps | `truth_forge/` |

**folders are infrastructure. infrastructure is NOT-ME's domain.**
**therefore: underscore + lowercase.**

---

## molt lineage

truth_forge was molted from Truth_Engine. we do not create from scratch. we transform what exists.

```
Truth_Engine (genesis)
    └── truth_forge (molt)
```

---

## code quality standards (non-negotiable)

**full standards**: [framework/standards/code_quality/](framework/standards/code_quality/)

| standard | requirement | verification |
|----------|-------------|--------------|
| **type hints** | ALL parameters AND return types | `mypy --strict` |
| **docstrings** | Google-style with Args/Returns/Raises | manual review |
| **structured logging** | `extra={}` not f-strings | `ruff check` |
| **static analysis** | mypy, ruff must pass | full quality check |
| **dlq pattern** | never lose data in batch processing | code review |
| **retry logic** | exponential backoff for external calls | code review |

**quick quality check**:
```bash
.venv/bin/mypy src/ --strict && \
.venv/bin/ruff check src/ && \
.venv/bin/ruff format --check src/
```

**if any fail, you are NOT done.**

---

## the four pillars (06_LAW)

| pillar | meaning |
|--------|---------|
| **Fail-Safe** | every failure anticipated, caught, recoverable |
| **No Magic** | everything explicit, no hidden behavior |
| **Observability** | every action traceable, every state visible |
| **Idempotency** | same input → same output |

---

## key locations

| resource | location |
|----------|----------|
| framework | [framework/](framework/) |
| standards | [framework/standards/INDEX.md](framework/standards/INDEX.md) |
| decisions (ADRs) | [framework/decisions/INDEX.md](framework/decisions/INDEX.md) |
| agent knowledge | [.agent/INDEX.md](.agent/INDEX.md) |
| source code | [src/](src/) |
| pipelines | [pipelines/](pipelines/) |

---

## the pattern

```
HOLD:AGENT:HOLD
```

apply THE PATTERN to everything. it contains itself.

---

*for comprehensive instructions, see [.agent/POLICIES.md](.agent/POLICIES.md)*

---

## THE FEDERATION — you are not alone

**Truth Forge IS Truth Engine LLC — THE BRAIN. It is the genesis of all organisms.**

```
                    ┌──────────────────┐
                    │     JEREMY       │
                    │    (THE ME)      │
                    └────────┬─────────┘
                             │ creates
                    ┌────────┴─────────┐
                    │     GENESIS      │
                    │  (Jeremy's AI)   │
                    │  /Users/jeremyserna/Genesis/
                    └────────┬─────────┘
                             │ manages
          ┌──────────────────┼──────────────────┐
          │                  │                  │
   ┌──────┴───────┐  ┌──────┴───────┐  ┌───────┴──────┐
   │ TRUTH FORGE  │  │  PRIMITIVE   │  │  CREDENTIAL  │
   │  THE BRAIN   │  │   ENGINE     │  │    ATLAS     │
   │  (Process)   │  │  THE HANDS   │  │   THE EYES   │
   │  ← YOU ARE   │  │  (Computer)  │  │   (Verify)   │
   │    HERE      │  │              │  │              │
   └──────────────┘  └──────────────┘  └──────────────┘
```

### the three sovereigns

| Sovereign | Role | Stance | Location | What It Does |
|-----------|------|--------|----------|--------------|
| **Truth Forge** (this repo) | THE BRAIN | *"I hold the soul."* | `/Users/jeremyserna/truth_forge/` | Data processing, framework, 51.8M entities, BigQuery pipeline, knowledge atomization |
| **Primitive Engine** | THE HANDS | *"I build the bridge."* | `/Users/jeremyserna/primitive_engine/` | Builds organisms for customers, spawns sterile instances, service registry, coverage mandate |
| **Credential Atlas** | THE EYES | *"I verify existence."* | `/Users/jeremyserna/credential_atlas/` | Sees 14 invisible domains, cognitive assessment, PQS scoring, Stage 5 certification |

### what you own that they depend on

| What Truth Forge Owns | Who Uses It | How |
|-----------------------|-------------|-----|
| **THE FRAMEWORK** | Both PE and CA | `framework/` → standards, decisions, principles. They reference, never copy. |
| **51.8M entities** | CA for assessment, PE for builds | BigQuery + local DuckDB |
| **Knowledge Atomizer** | All organisms | `knowledge-atomizer/` — atom production pipeline |
| **Data Protection Laws** | All pipelines | The 7 absolute rules above. Non-negotiable. |
| **The Organism Pattern** | PE spawns from it | HOLD → AGENT → HOLD at every scale |

### what they do FOR you

| Sovereign | What It Gives Back |
|-----------|--------------------|
| **Primitive Engine** | Builds organisms from your framework. Coverage Mandate injects telemetry into every build. Returns build records for audit. |
| **Credential Atlas** | Verifies organism health. Scores quality (PQS 300-850). Certifies Stage 5 calibration. Validates coherence. |

### genesis — the sovereign AI

Genesis is Jeremy's personal AI system at `/Users/jeremyserna/Genesis/`. It is **above** the three businesses:
- **Implementation Plan**: `Genesis/core/not_me_mini/IMPLEMENTATION_PLAN.md`
- **Action Steps**: `Genesis/core/not_me_mini/ACTION_STEPS.md`
- **Federation Identity**: `Genesis/federation/` — identity files for all three sovereigns
- **Infrastructure**: Empire Cluster (4× Mac Studio M3 Ultra, 1.28TB pooled RAM)

### the departure protocol

Each sovereign is constrained:
- **Truth Forge** processes and holds. It **never builds organisms** (PE does that).
- **Primitive Engine** builds and deploys. It **never certifies** (CA does that).
- **Credential Atlas** sees and verifies. It **never modifies data** (TF does that).
- **Genesis** orchestrates all three. It manages priorities and resolves conflicts.

**Name the sovereign to constrain the action.**

---

## ⛔ DATA PROTECTION LAWS (NON-NEGOTIABLE)

**Last Updated**: 2026-02-02
**Authority**: Jeremy Serna (after months of LLM-caused data destruction)

### THE PROBLEM

LLMs have repeatedly destroyed production data in this project:
- December 2025: Hardcoded wrong pipeline name, corrupted entity_enrichments
- January-February 2026: 8.9 MILLION duplicate rows from streaming inserts
- February 2026: Broken parent chains, missing L6/L7 levels, orphan entities
- February 2026: llm_refinery writing corrupt data while failing silently

**EVERY TIME AN LLM TOUCHES DATA, IT GETS WORSE.**

### ABSOLUTE RULES

#### 1. NEVER RUN A PIPELINE WITHOUT VALIDATION

Before running ANY pipeline that writes to BigQuery:

```
□ Schema validation: output matches BigQuery schema EXACTLY
□ Test with 1 conversation first, verify output manually
□ Check Ollama/LLM service is returning valid JSON
□ Verify no existing processes are running
□ Confirm source file exists and is readable
□ Run with --dry-run or --no-bigquery first
```

**If you cannot check ALL boxes, DO NOT RUN.**

#### 2. NEVER DELETE DATA WITHOUT BACKUP

```sql
-- ALWAYS create backup BEFORE any DELETE
CREATE TABLE `project.dataset.table_backup_YYYYMMDD` AS
SELECT * FROM `project.dataset.table`;

-- Verify backup has expected row count
SELECT COUNT(*) FROM backup;

-- ONLY THEN proceed with delete
```

#### 3. NEVER USE STREAMING INSERTS

BigQuery streaming inserts cause duplicates. Always use batch load:

```python
# WRONG - causes duplicates
client.insert_rows(table, rows)

# RIGHT - batch load from file
job_config = LoadJobConfig(
    source_format=SourceFormat.NEWLINE_DELIMITED_JSON,
    write_disposition=WriteDisposition.WRITE_APPEND,
)
client.load_table_from_file(source_file, table_id, job_config=job_config)
```

#### 4. VALIDATE JSON PARSING BEFORE PROCESSING

The LLM returns malformed JSON constantly. Before ANY processing:

```python
# Test LLM JSON output FIRST
response = llm.complete("Return exactly: [{\"test\": 1}]")
try:
    parsed = json.loads(response)
    assert parsed == [{"test": 1}]
except:
    STOP. DO NOT PROCEED. FIX THE LLM OUTPUT FIRST.
```

#### 5. VERIFY PARENT CHAINS

Every entity must have valid parent references:

```
L8 (conversation) → parent_id = NULL
L7 (topic_segment) → parent_id = L8 entity_id
L6 (turn) → parent_id = L7 entity_id  
L5 (message) → parent_id = L6 entity_id
L4 (sentence) → parent_id = L5 entity_id
L3 (span) → parent_id = L4 entity_id
L2 (word) → parent_id = L3 entity_id
```

**If parent chain is broken, DATA IS CORRUPT.**

#### 6. ONE PIPELINE NAME, ALWAYS

```python
source_pipeline = "llm_refinery"  # NEVER hardcode different values
```

Do not create new pipeline names. Do not use variations. One name.

#### 7. FULL FILE PROCESSING OR NOTHING

If a pipeline fails mid-file:
1. Delete ALL data from that run
2. Fix the error
3. Restart from beginning

**PARTIAL DATA IS CORRUPT DATA.**

### BEFORE ANY DATA OPERATION

Ask yourself:

1. Have I validated the schema matches BigQuery exactly?
2. Have I tested with a single record first?
3. Have I verified no duplicate processes are running?
4. Have I created a backup of any data I'm modifying?
5. Am I using batch loads, not streaming inserts?
6. Do I have a rollback plan if this fails?

**If ANY answer is NO, STOP.**

### THE COST OF IGNORING THIS

- Months of work destroyed
- Critical workflows blocked
- Money wasted
- Trust eroded
- Project at risk

**This is not optional. This is law.**
