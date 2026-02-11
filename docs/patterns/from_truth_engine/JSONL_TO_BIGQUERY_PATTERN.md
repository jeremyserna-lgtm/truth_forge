# JSONL → BigQuery Pattern

**Version**: 1.0
**Date**: 2025-12-27
**Status**: Canonical Pattern Definition
**Location**: `docs/patterns/JSONL_TO_BIGQUERY_PATTERN.md`

---

## Executive Summary

This pattern describes how data flows from local JSONL files to BigQuery tables. It's used throughout Truth Engine for intake systems, logging, cost tracking, and pipeline staging.

**The Pattern**:
```
Write locally (JSONL) → Sync periodically (fingerprint-based) → Query remotely (BigQuery)
```

**Why this pattern exists**:
1. **Claude has no memory** - Append-only JSONL gives Claude frictionless write
2. **Local is fast** - No network round-trip for capture
3. **BigQuery is queryable** - Once synced, data is analyzable
4. **Fingerprints prevent duplicates** - Idempotent sync, run as often as needed

---

## Part 1: The Pattern Definition

### 1.1 Core Components

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        JSONL → BigQuery PATTERN                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐              │
│  │    WRITE     │      │     SYNC     │      │    QUERY     │              │
│  │              │      │              │      │              │              │
│  │  Append to   │ ───> │  Fingerprint │ ───> │  BigQuery    │              │
│  │  .jsonl file │      │  + Insert    │      │  SELECT      │              │
│  │              │      │              │      │              │              │
│  └──────────────┘      └──────────────┘      └──────────────┘              │
│        │                      │                      │                      │
│        v                      v                      v                      │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐              │
│  │ No reading   │      │ State file   │      │ LLM can      │              │
│  │ No context   │      │ tracks what  │      │ analyze,     │              │
│  │ Just append  │      │ synced       │      │ manage       │              │
│  └──────────────┘      └──────────────┘      └──────────────┘              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Required Files

| File | Purpose | Example |
|------|---------|---------|
| `{type}.jsonl` | Append-only data store | `backlog.jsonl` |
| `.{type}_sync_state.json` | Tracks synced fingerprints | `.backlog_sync_state.json` |
| BigQuery table | Queryable storage | `governance.backlog_items` |

### 1.3 The Contract

**WRITE phase**:
- Append one JSON line per entry
- Include `created_at` timestamp
- Include `run_id` for traceability
- Never read the file during write

**SYNC phase**:
- Compute fingerprint (content + timestamp hash)
- Skip already-synced entries (idempotent)
- Add `synced_at` timestamp
- Mark `needs_management: true` for LLM processing
- Update sync state file

**QUERY phase**:
- Query BigQuery for analysis
- Filter by `needs_management` for LLM jobs
- Update `needs_management = false` after processing

---

## Part 2: Implementation Reference

### 2.1 Write Function Template

```python
def write_to_jsonl(
    jsonl_path: Path,
    content: str,
    **metadata
) -> str:
    """Append one entry to JSONL file. Never read.

    Args:
        jsonl_path: Path to the JSONL file
        content: Main content to store
        **metadata: Additional fields (priority, category, etc.)

    Returns:
        Confirmation with entry ID
    """
    from datetime import datetime, timezone
    from architect_central_services import get_current_run_id
    from architect_central_services.core.identity_service import generate_intake_id

    entry = {
        "id": generate_intake_id(jsonl_path.stem),
        "content": content,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "run_id": get_current_run_id(),
        **metadata
    }

    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    with open(jsonl_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    return f"[{jsonl_path.stem}] {content[:50]}... [{entry['id']}]"
```

### 2.2 Sync Function Template

```python
def sync_jsonl_to_bigquery(
    jsonl_path: Path,
    table_id: str,
    *,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """Sync JSONL to BigQuery with fingerprint-based deduplication.

    Args:
        jsonl_path: Path to source JSONL file
        table_id: BigQuery table ID
        dry_run: If True, report what would sync

    Returns:
        Sync result summary
    """
    import hashlib
    from architect_central_services import get_bigquery_client

    # Load sync state
    state_file = jsonl_path.parent / f".{jsonl_path.stem}_sync_state.json"
    synced = set(json.loads(state_file.read_text()).get("synced_hashes", [])) if state_file.exists() else set()

    # Find new entries
    to_sync = []
    with open(jsonl_path) as f:
        for line in f:
            if not line.strip():
                continue
            entry = json.loads(line)
            fingerprint = hashlib.sha256(
                f"{entry.get('content', '')}|{entry.get('created_at', '')}".encode()
            ).hexdigest()[:16]

            if fingerprint not in synced:
                to_sync.append((entry, fingerprint))

    if dry_run:
        return {"status": "dry_run", "would_sync": len(to_sync)}

    if not to_sync:
        return {"status": "up_to_date", "synced": 0}

    # Prepare rows with needs_management flag
    rows = []
    new_fingerprints = []
    for entry, fp in to_sync:
        rows.append({
            **entry,
            "synced_at": datetime.now(timezone.utc).isoformat(),
            "needs_management": True,
            "fingerprint": fp,
        })
        new_fingerprints.append(fp)

    # Insert to BigQuery
    client = get_bigquery_client()
    errors = client.insert_rows_json(table_id, rows)

    if errors:
        return {"status": "error", "errors": errors}

    # Update sync state
    synced.update(new_fingerprints)
    state_file.write_text(json.dumps({
        "synced_hashes": list(synced),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }))

    return {"status": "success", "synced": len(rows)}
```

### 2.3 Query Pattern

```python
def get_items_needing_management(table_id: str, limit: int = 100) -> List[Dict]:
    """Get items that need LLM management."""
    from architect_central_services import get_bigquery_client

    client = get_bigquery_client()
    query = f"""
        SELECT *
        FROM `{table_id}`
        WHERE needs_management = TRUE
        ORDER BY created_at DESC
        LIMIT {limit}
    """
    return [dict(row) for row in client.query(query)]


def mark_as_managed(table_id: str, ids: List[str]) -> None:
    """Mark items as managed after LLM processing."""
    from architect_central_services import get_bigquery_client

    client = get_bigquery_client()
    query = f"""
        UPDATE `{table_id}`
        SET needs_management = FALSE,
            managed_at = CURRENT_TIMESTAMP()
        WHERE id IN UNNEST(@ids)
    """
    client.query(query, job_config=bigquery.QueryJobConfig(
        query_parameters=[bigquery.ArrayQueryParameter("ids", "STRING", ids)]
    ))
```

---

## Part 3: Known Instances

### 3.1 Intake System (Canonical Implementation)

| Instance | JSONL File | Table | Status |
|----------|------------|-------|--------|
| Backlog | `governance/intake/backlog.jsonl` | `governance.backlog_items` | Sync exists, needs running |
| See | `governance/intake/see.jsonl` | `governance.intake_events` | Sync exists |
| Moment | `governance/intake/moment.jsonl` | `governance.intake_events` | Sync exists |
| Changelog | `governance/intake/changelog.jsonl` | `governance.intake_events` | Sync exists |

**Implementation**: `governance/intake/universal_sync.py`

### 3.2 Logging System

| Instance | JSONL File | Table | Status |
|----------|------------|-------|--------|
| Central logs | `logs/architect_central.jsonl` | `observability.logs` | Unknown |
| Cost tracking | `logs/costs/cost_tracking.jsonl` | `governance.process_costs` | Partial |
| Hook observations | `logs/hooks/transcript_observations.jsonl` | ? | Unknown |

### 3.3 Pipeline Staging

| Instance | JSONL File | Table | Status |
|----------|------------|-------|--------|
| Zoom chats | `data/zoom_chats/*.jsonl` | `spine.zoom_*` | Per-pipeline |
| System events | `data/system_events.jsonl` | ? | Unknown |

### 3.4 Truth Service

| Instance | JSONL File | Table | Status |
|----------|------------|-------|--------|
| Claude Code | `~/.claude/projects/**/*.jsonl` | `spine.claude_code_*` | Read-only (external) |
| Codex | `~/.codex/sessions/*.jsonl` | `spine.codex_*` | Read-only (external) |

---

## Part 4: Pattern Compliance Checklist

When implementing or auditing a JSONL → BigQuery instance:

### Write Phase

- [ ] **Append-only**: Never reads the file during write
- [ ] **Atomic entries**: Each line is valid JSON
- [ ] **Required fields**: `created_at`, `run_id` present
- [ ] **ID generation**: Uses `generate_*_id()` from identity_service
- [ ] **Central services**: Uses `get_logger()`, not `print()`

### Sync Phase

- [ ] **Fingerprint-based**: Uses content+timestamp hash for dedup
- [ ] **State file**: `.{type}_sync_state.json` exists
- [ ] **Idempotent**: Running twice produces same result
- [ ] **needs_management**: Flag set for LLM processing
- [ ] **synced_at**: Timestamp added during sync
- [ ] **Error handling**: Graceful failure, no data loss

### Query Phase

- [ ] **BigQuery table**: Schema matches JSONL structure
- [ ] **Clustered**: Table is clustered by appropriate key
- [ ] **needs_management**: Query filters by this flag
- [ ] **Mark managed**: Updates flag after processing

### Infrastructure

- [ ] **Documented**: README or doc file explains the instance
- [ ] **Discoverable**: Listed in pattern registry
- [ ] **Tested**: At least one test verifies flow
- [ ] **Monitored**: Health check can detect if broken

---

## Part 5: Anti-Patterns

### Don't Read During Write

```python
# WRONG - Reads file to check duplicates
def write_item(content):
    with open(jsonl_path) as f:
        existing = [json.loads(l) for l in f]
    if content not in [e["content"] for e in existing]:
        # write...

# RIGHT - Dedup happens at sync time
def write_item(content):
    # Just append, let sync handle dedup
    with open(jsonl_path, "a") as f:
        f.write(json.dumps(entry) + "\n")
```

### Don't Skip Fingerprinting

```python
# WRONG - Relies on ID uniqueness
if entry["id"] not in synced_ids:
    sync(entry)

# RIGHT - Content-based fingerprint
fingerprint = hash(content + timestamp)
if fingerprint not in synced_fingerprints:
    sync(entry)
```

### Don't Sync Without State

```python
# WRONG - No tracking, syncs duplicates
for entry in jsonl:
    client.insert_rows_json(table, [entry])

# RIGHT - State file prevents re-sync
synced = load_state()
new_entries = [e for e in jsonl if fingerprint(e) not in synced]
client.insert_rows_json(table, new_entries)
save_state(synced | new_fingerprints)
```

---

## Part 6: When to Use This Pattern

### Use When

- Claude needs to capture data without context loading
- Data needs eventual consistency (not real-time)
- Local capture speed matters more than immediate queryability
- Batch sync is acceptable (minutes to hours delay)
- LLM will process the data later

### Don't Use When

- Real-time queries are required
- Data volume is very high (>100K entries/day)
- Strict transactional consistency needed
- Data must be immediately available for other systems

### Alternatives

| Scenario | Alternative Pattern |
|----------|---------------------|
| Real-time queries | Direct BigQuery streaming insert |
| High volume | Cloud Pub/Sub → Dataflow → BigQuery |
| Transactional | Cloud SQL with sync to BigQuery |
| Multi-system | Event-driven with Cloud Tasks |

---

## Part 7: Migration Guide

### Adding Sync to Existing JSONL

1. **Create table**: Design schema matching JSONL structure
2. **Add sync function**: Use template from Part 2.2
3. **Initialize state**: First sync will process all historical entries
4. **Add to health check**: Monitor sync freshness
5. **Add to scheduled job**: Run sync periodically

### Converting Direct Insert to Pattern

1. **Create JSONL file**: Replace `insert_rows_json` with file append
2. **Create sync**: Add fingerprint-based sync function
3. **Add state tracking**: Create `.{type}_sync_state.json`
4. **Schedule sync**: Run periodically (cron, Cloud Scheduler)
5. **Update queries**: May need to handle sync delay

---

## Part 8: Related Patterns

| Pattern | Document | Relationship |
|---------|----------|--------------|
| Atomic Intake | `REGISTRY_PATTERN.md` | Uses this pattern for storage |
| Pipeline Stages | `UNIVERSAL_PIPELINE_PATTERN.md` | May use for stage artifacts |
| LLM Management | `THE_LLM_LAYER.md` | Consumes synced data |
| Truth Service | `THE_TRUTH.md` | Special case (external JSONL) |

---

## Changelog

### v1.0 (2025-12-27)
- Initial pattern definition
- Documented 4 instance categories (intake, logging, pipeline, truth)
- Created compliance checklist
- Added implementation templates
- Documented anti-patterns
