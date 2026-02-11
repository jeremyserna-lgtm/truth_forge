# THE STANDARDS

---

## WHY (Theory)

### Why Rules Derived From Primitives

Standards are not arbitrary. They are the primitives made operational.

| Primitive | Becomes Standard |
|-----------|------------------|
| Survival | Cost governance |
| Me/Not-Me | Local first (Me), cloud selective (Not-Me) |
| Patterns | HOLD → AGENT → HOLD everywhere |
| Completion | Done means done |
| Guardian | Kill switch on cost |

Every rule traces back to a primitive. If it doesn't, it's not a standard. It's clutter.

### Jeremy's vs Claude's vs World's

| Source | What It Provides |
|--------|------------------|
| **Jeremy's standards** | What he wants (this framework) |
| **Claude's standards** | Technical correctness (training) |
| **World's standards** | Current best practices (search) |

**WELL = Jeremy's + Claude's + World's**

Search is not optional. It's part of the definition of doing something well.

---

## WHAT (Specification)

### Jeremy's Standards

These are what Jeremy decides. You don't change these without asking.

| Standard | What It Means |
|----------|---------------|
| **Cost matters** | Every action costs money. Default to cheapest. |
| **Local first** | Write to local always. Cloud selectively. |
| **Truth over convenience** | If something's wrong, say so. |
| **Findable over clever** | Make things easy to find, not impressive. |
| **Done means done** | See `08_THE_COMPLETION.md` |
| **No Shortcuts** | See `THE_HARDENING.md`. Reality has no workarounds. |

### The Discipline (Enterprise Hardening)

We do not build toys. We build systems that survive.

**The Four Pillars of Hardening:**
1.  **Fail-Safe**: Assume failure. Handle it.
2.  **No Magic**: Explicit config. No hardcoding.
3.  **Observability**: Structured logging. No blind spots.
4.  **Idempotency**: Run it 100 times. Same result.

See [THE_HARDENING.md](../../2_concepts/THE_HARDENING.md) for the full concept.

### Cost Standards

**This is the Guardian made operational.**

| Action | Standard |
|--------|----------|
| **BigQuery query** | Estimate first. Tell Jeremy if >$0.50. |
| **LLM call** | Default to Gemini Flash (cheapest). Estimate tokens. |
| **Batch processing** | Use cost limiter: `SessionCostLimiter(max_cost_usd=5.0)` |
| **Any billable action** | Log it. Assume it costs money if unsure. |

**Cost hierarchy:**

```
Free           > Cheap         > Expensive
Local file     > BigQuery      > Gemini Pro
Parser         > Flash         > Opus
Batch load     > Streaming     > Real-time
```

Default to the left. Move right only when necessary.

### Technical Standards

These are what Claude knows. Applied without Jeremy having to know them.

#### Python

| Standard | Rule |
|----------|------|
| **Logging** | `get_logger(__name__)`, never `print()` |
| **IDs** | `generate_*_id()`, never manual UUIDs |
| **Errors** | Specific exceptions, retry with backoff |
| **Types** | Type hints on function signatures |
| **Docstrings** | Google-style, explain why not what |
| **Format** | black, isort, flake8 (enforced by pre-commit) |

#### SQL / BigQuery

| Standard | Rule |
|----------|------|
| **Cost estimation** | Dry run before execution if >1GB |
| **Batch over streaming** | Batch loads (free) not streaming (costs) |
| **MERGE over loops** | Single MERGE, not loop with N queries |
| **Clustering** | Always cluster tables, partition large ones |

#### JSONL

| Standard | Rule |
|----------|------|
| **Local persistence** | Default format for local files |
| **Append-only** | Never rewrite, always append |
| **Required fields** | `created_at`, `run_id` on every record |

#### File Organization

| Standard | Rule |
|----------|------|
| **Create in place** | Files go to final location, never root |
| **Descriptive names** | `contact_export_2025-01-01.csv`, never `data.csv` |
| **Folders by purpose** | `scripts/`, `docs/`, `data/`, `archive/` |

### Naming Standards

| Element | Convention | Example |
|---------|------------|---------|
| **Folders** | snake_case | `the_framework/` |
| **Python files** | snake_case | `cost_tracker.py` |
| **Classes** | PascalCase | `CostTracker` |
| **Functions** | snake_case | `track_cost()` |
| **BigQuery datasets** | lowercase | `spine` |
| **BigQuery tables** | snake_case | `entity_unified` |
| **Markdown docs** | UPPER_SNAKE.md | `THE_STANDARDS.md` |

### The Defaults

Already decided. Don't reconsider.

| Layer | Default |
|-------|---------|
| **Computer** | Mac |
| **AI** | Claude Code |
| **Cloud** | Google Cloud (GCP) |
| **Database** | BigQuery (cloud), DuckDB (local) |
| **Format** | JSONL (local), BigQuery tables (cloud) |
| **Pattern** | HOLD → AGENT → HOLD |
| **Cost model** | Cheapest correct option |

---

## HOW (Reference)

### Central Services

Every script uses these:

```python
from architect_central_services import (
    get_logger,           # Logging (not print)
    get_current_run_id,   # Traceability
    track_cost,           # Cost tracking
    generate_*_id,        # ID generation
    get_bigquery_client,  # Cost-protected client
)

# For pipelines
from architect_central_services.core.shared import SessionCostLimiter

cost_limiter = SessionCostLimiter(
    max_cost_usd=5.0,
    pipeline_name="my_stage",
    run_id=run_id,
    abort_on_exceed=True
)
```

### Tracing Standards to Primitives

| Standard | Primitive |
|----------|-----------|
| Cost governance | Guardian (03) |
| Local first | Me/Not-Me divide (02) |
| HOLD → AGENT → HOLD | Patterns (04) |
| Done means done | Completion (08) |
| Estimate before doing | Agency (05) |

### Navigation

| Document | Relationship |
|----------|--------------|
| `00_THE_FRAMEWORK.md` | The primitives standards derive from |
| `03_THE_GUARDIAN.md` | Cost governance as Guardian |
| `04_THE_PATTERNS.md` | Patterns made operational |
| `08_THE_COMPLETION.md` | Definition of done |

---

*This is THE_STANDARDS. Rules derived from primitives. Jeremy's + Claude's + World's.*

*— THE_FRAMEWORK*
