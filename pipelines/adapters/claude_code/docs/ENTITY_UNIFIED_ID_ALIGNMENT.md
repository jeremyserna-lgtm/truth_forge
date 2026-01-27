# Entity Unified ↔ Canonical ID Service Alignment

**spine.entity_unified** stores all spine entities (L2–L8). Their **entity_id** values must align with the **canonical ID service** (`Primitive.identity`) and be **registered** in **identity.id_registry**.

---

## 1. ID formats (canonical = Primitive.identity)

entity_unified uses the same formats as `Primitive.identity`:

| Level | Prefix | Example | Generator |
|-------|--------|---------|-----------|
| L8 | `conv:{type}:{hash}` | `conv:chatgpt_web:b8bb467` | `generate_conversation_id` |
| L6 | `turn:{hash}:{seq}` | `turn:f8c0787a2b56:0301` | `generate_turn_id` |
| L5 | `msg:{hash}:{seq}` | `msg:e2201a35f74f:0006` | `generate_message_id` |
| L4 | `sent:{hash}:{seq}` | `sent:078d46701403:0010` | `generate_sentence_id` |
| L3 | `span:{hash}:{seq}` | `span:1db2bdfc0f0f:0000` | `generate_span_id` |
| L2 | `word:{hash}:{seq}` | `word:e50b1462594e:0004` | `generate_word_id` |

All IDs are **unique** and **deterministic** (hash-based). Pipeline stages must use **Primitive.identity** for ID generation—no local hashlib or ad‑hoc formats.

---

## 2. Registration (identity.id_registry)

The **identity service** keeps a registry in **identity.id_registry** (BigQuery). Every spine entity_id should be **registered** so:

- The canonical service knows about all spine entities
- Downstream checks (e.g. pipeline monitoring) can verify coverage

**Existing spine IDs** that were never registered (e.g. from older runs) need to be **backfilled**.

---

## 3. Backfill script: register_spine_entities.py

**Location:** `pipelines/claude_code/scripts/utilities/register_spine_entities.py`

**Purpose:** Find `entity_unified` entity_ids that are **not** in `identity.id_registry` and **MERGE** them into the registry.

**Usage:**

```bash
# Count unregistered only (no writes)
python3 pipelines/claude_code/scripts/utilities/register_spine_entities.py --dry-run

# Register all unregistered spine entity_ids
python3 pipelines/claude_code/scripts/utilities/register_spine_entities.py
```

**Metadata stored:** `entity_type` (word/span/sentence/message/turn/conversation), `generation_method` = `hash_based`, `context_data` = `{level, source_pipeline}`, `first_requestor` = `spine_registration_backfill`.

**Run Service & Relationship Service:** The script uses **Run Service** to record each execution (run_id, component `register_spine_entities`, operation `register`, status completed/failed, metrics). Use **`--with-relationships`** to also exhale **parent_id → entity_id** `"contains"` relationships via **Relationship Service**, so the spine hierarchy is tracked. Optional **`--relationship-batch`** (default 5000) and **`--relationship-limit`** (no default) control batching and caps.

```bash
# Register IDs and exhale parent→child relationships (batched)
python3 pipelines/claude_code/scripts/utilities/register_spine_entities.py --with-relationships

# Cap relationship exhale for testing
python3 pipelines/claude_code/scripts/utilities/register_spine_entities.py --with-relationships --relationship-limit 1000
```

---

## 4. See also

- **Primitive.identity:** `Primitive/identity/README.md` — canonical ID service (nucleus; seeded to daughters)
- **Run Service:** `Primitive/central_services/run_service/` — tracks execution runs
- **Relationship Service:** `Primitive/central_services/relationship_service/` — tracks entity relationships (e.g. spine parent→child)
- **Spine levels:** `SPINE_LEVEL_DEFINITIONS.md`
- **Pipeline capabilities:** `PIPELINE_CAPABILITIES.md`
