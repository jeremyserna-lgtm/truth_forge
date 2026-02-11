# THE_SCRIPT_PATTERNS
## The Operational Patterns of Python Scripts

**Date**: January 1, 2026
**Status**: Active Concept
**Source**: Derived from Framework Primitives

---

## The Concept

A script is not just "code". It is an **Agent** instantiated to perform a specific Primitive function.

We do not write "scripts". We write **Bridges**, **Loops**, **Observers**, and **Forges**.

---

## Pattern 1: The Bridge (Structure)
**Primitive**: `HOLD → AGENT → HOLD`

The Bridge connects two states of existence. It takes atoms from one Hold, transforms them, and places them in another Hold.

*   **Input**: A Source Hold (e.g., `.jsonl`, API, Directory).
*   **Process**: Transformation (Enrichment, Parsing, Formatting).
*   **Output**: A Target Hold (e.g., BigQuery, `.duckdb`, Cleaned File).
*   **Rule**: **Idempotency**. Running the Bridge twice must result in the same Target state.
*   **Example**: `ingest_documents.py`, `enrich_entities.py`.

```python
def bridge():
    source = read_hold(SOURCE)
    for atom in source:
        if not exists_in_target(atom):
            new_atom = transform(atom)
            write_hold(TARGET, new_atom)
```

---

## Pattern 2: The Loop (Cycle)
**Primitive**: `WANT → CHOOSE → MOVE`

The Loop is the heartbeat. It ensures existence continues. It does not just run once; it maintains a state of "Existing".

*   **Input**: A Trigger (Time, Event, Queue).
*   **Process**: Check for work (Want), Execute work (Move).
*   **Output**: Updated State.
*   **Rule**: **Resilience**. The Loop must never die. It must catch all errors, log them, sleep, and retry.
*   **Example**: `process_queue.py`, `daily_sync.py`.

```python
def loop():
    while True:
        try:
            work = get_next_want()
            if work:
                do_move(work)
            else:
                sleep(INTERVAL)
        except Exception:
            log_error()
            sleep(BACKOFF)
```

---

## Pattern 3: The Observer (Seeing)
**Primitive**: `SEE (Data) → SEE (Pattern)`

The Observer does not act. It sees. It reads the traces left by other Agents and synthesizes Truth.

*   **Input**: Logs, State Files, Metadata.
*   **Process**: Pattern Recognition, Anomaly Detection, Aggregation.
*   **Output**: A Report, an Alert, or a Higher-Order Log.
*   **Rule**: **Non-Interference**. The Observer must never modify the state it observes.
*   **Example**: `analyze_costs.py`, `monitor_health.py`.

```python
def observer():
    logs = read_logs(TIME_WINDOW)
    pattern = detect_pattern(logs)
    if pattern.is_significant():
        write_report(pattern)
```

---

## Pattern 4: The Forge (Transformation)
**Primitive**: `SEE (Subject) → REWRITE (Object)`

The Forge is the agent of change. It takes the System itself as input and rewrites it.

*   **Input**: The System (Schema, Code, Data Structure).
*   **Process**: Migration, Refactoring, Deletion.
*   **Output**: A New System State.
*   **Rule**: **Safety**. The Forge is destructive. It requires a backup (Hold) before striking.
*   **Example**: `migrate_schema_v1_to_v2.py`, `refactor_imports.py`.

```python
def forge():
    backup_system()
    schema = read_schema()
    new_schema = transform_schema(schema)
    apply_schema(new_schema)
    verify_integrity()
```

---

## Summary

| Pattern | Primitive | Role | Key Trait |
|---------|-----------|------|-----------|
| **Bridge** | Structure | Move Data | Idempotent |
| **Loop** | Cycle | Maintain Life | Resilient |
| **Observer** | Seeing | Find Truth | Read-Only |
| **Forge** | Evolution | Change Self | Safe |

**When you write a script, declare its Pattern.**
