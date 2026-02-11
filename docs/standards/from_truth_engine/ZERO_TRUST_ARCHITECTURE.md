# Zero Trust Architecture Standard

**The Standard** | AI agents build architecture. Humans decide limits. No invisible decisions.

**Status**: Active
**Created**: 2026-01-23
**Last Updated**: 2026-01-23
**06_LAW Pillar**: No Magic, Observability

---

## Quick Reference

| Term | Definition |
|------|------------|
| **Zero Trust** | Assume AI-generated code contains invisible decisions until proven otherwise |
| **Invisible Decision** | Any limit, truncation, filter, or default chosen by AI without human approval |
| **Magic Number** | A hardcoded value that constrains behavior (batch_size=100, limit=10, timeout=30) |
| **Silent Reduction** | Removing data without surfacing what was removed |
| **Decision Audit Trail** | Record of who decided each limit and why |

---

## WHY (Theory)

### The Problem

AI agents (Claude, Cursor, etc.) constantly make decisions that should be human decisions:

```python
# AI writes this thinking it's "reasonable"
def process_records(records):
    for batch in chunks(records, size=100):  # WHO DECIDED 100?
        results = query_database(batch)
        return results[:10]  # WHO DECIDED 10?
```

**Jeremy cannot see these decisions.** He's not a coder. He trusts the architecture works. But the AI made invisible choices:
- Batch size of 100 (why not 1000? why not all?)
- Return only top 10 (where did the rest go?)
- Implicit timeout somewhere
- "Reasonable" memory limits

### What Happens Without This Standard

1. **Data Loss**: Records silently dropped, truncated, or filtered
2. **Capacity Blindness**: System "works" but only at AI-chosen scale
3. **Hidden Ceilings**: Performance limited by arbitrary AI decisions
4. **Debugging Hell**: Problems caused by limits Jeremy doesn't know exist
5. **Trust Erosion**: System fails in ways that can't be traced

### The Principle

```
AI BUILDS. HUMAN DECIDES.

Every limit, every truncation, every filter, every default
MUST be either:
1. Explicitly approved by Jeremy, OR
2. Configurable and documented, OR
3. Surfaced visibly when applied
```

### Connection to THE_FRAMEWORK

This standard enforces:
- **ME/NOT-ME**: Decisions are ME (Jeremy). Building is NOT-ME (AI).
- **No Magic**: Every constraint is explicit and traceable
- **Observability**: Every reduction is visible
- **Signal Preservation**: Data is not silently reduced

---

## WHAT (Specification)

### Requirements

#### MUST (Required)

1. **No Magic Numbers** — Every numeric limit must be:
   - Defined as a named constant with documented source
   - Configurable via environment or config file
   - Include comment: `# HUMAN_DECISION: [who] [when] [why]` or `# AI_DEFAULT: [rationale] [configurable: yes/no]`

2. **No Silent Truncation** — When data is reduced:
   - Log what was removed: count, sample, reason
   - Surface total vs returned: `Returning 10 of 5,432 records`
   - Provide mechanism to access full data

3. **No Hidden Filters** — When data is filtered:
   - Document filter criteria explicitly
   - Log filter statistics: `Filtered 234 records (23%): [reason]`
   - Make filter criteria configurable

4. **No Implicit Timeouts** — All timeouts must:
   - Be explicitly declared with named constants
   - Have documented rationale
   - Be configurable
   - Log when triggered: `Timeout after 30s (configured), 5,432 items pending`

5. **Decision Audit Trail** — Every constraining decision must trace to:
   - Human approval (preferred), OR
   - Configurable default with documentation

6. **Full Data Path** — By default, architecture should:
   - Process ALL data unless explicitly limited
   - Return ALL results unless explicitly paginated
   - Preserve ALL signals unless explicitly filtered

7. **Escape Hatch Visibility** — When limits ARE applied:
   - Return metadata showing what was limited
   - Provide `_meta` or similar field with constraint info
   - Never silently apply limits

#### SHOULD (Recommended)

1. **Prefer Streaming** — Stream data rather than loading all to memory, avoiding artificial chunking
2. **Expose Configuration** — Make all limits visible in a central config location
3. **Default to Maximum** — When a limit is needed, default to highest safe value, not "reasonable" value
4. **Log Decisions** — Log when any limit is applied, even if within normal operation

#### MAY (Optional)

1. **Progressive Enhancement** — Start with no limits, add only when empirically needed
2. **Limit Discovery Mode** — Runtime flag that logs all limit applications for audit

#### MUST NOT (Prohibited)

1. **Silent `[:N]` Slicing** — Never slice results without documenting and logging
2. **Hardcoded Pagination** — Never hardcode page sizes without configuration
3. **"Reasonable Defaults"** — Never use phrase "reasonable default" to justify an AI decision
4. **Hidden Deduplication** — Never dedupe without surfacing what was removed
5. **Implicit Memory Guards** — Never limit in-memory collections without documentation
6. **Swallowed Exceptions** — Never catch exceptions and continue without signaling
7. **Sample Mode Without Flag** — Never process a sample while claiming to process all

---

## HOW (Reference)

### Examples

#### Correct Usage

```python
# CORRECT: Explicit, documented, configurable limits

from config import settings

# HUMAN_DECISION: Jeremy 2026-01-23 - Start with no limit, add if memory issues
BATCH_SIZE = settings.get("BATCH_SIZE", None)  # None = no batching
MAX_RESULTS = settings.get("MAX_RESULTS", None)  # None = all results
QUERY_TIMEOUT = settings.get("QUERY_TIMEOUT_SECONDS", 300)  # 5 min default, configurable

def process_records(records: List[Record]) -> ProcessResult:
    """Process records with full transparency.

    Returns:
        ProcessResult with data AND metadata about any limits applied
    """
    total_count = len(records)

    # Process all unless explicitly batched
    if BATCH_SIZE:
        logger.info(f"Batching enabled: {BATCH_SIZE} per batch, {total_count} total")
        batches = list(chunks(records, BATCH_SIZE))
    else:
        batches = [records]  # Single batch = all records

    results = []
    for batch in batches:
        batch_results = query_database(batch, timeout=QUERY_TIMEOUT)
        results.extend(batch_results)

    # Apply limit only if configured, with full transparency
    returned_results = results
    limited = False
    if MAX_RESULTS and len(results) > MAX_RESULTS:
        returned_results = results[:MAX_RESULTS]
        limited = True
        logger.warning(
            f"LIMIT APPLIED: Returning {MAX_RESULTS} of {len(results)} results. "
            f"Configure MAX_RESULTS=None for full results."
        )

    return ProcessResult(
        data=returned_results,
        _meta={
            "total_available": len(results),
            "total_returned": len(returned_results),
            "limited": limited,
            "limit_config": MAX_RESULTS,
            "batch_size_config": BATCH_SIZE,
            "timeout_config": QUERY_TIMEOUT,
        }
    )
```

**Why this is correct:**
- All limits are configurable
- Defaults are None (no limit) or maximum safe value
- Metadata shows exactly what was limited
- Logging surfaces when limits apply
- Human can trace every constraint

#### Incorrect Usage

```python
# WRONG: Invisible decisions everywhere

def process_records(records):
    # WHO DECIDED 100? WHY?
    for batch in chunks(records, 100):
        results = query_database(batch)

    # Silent truncation - data lost forever
    return results[:10]


# WRONG: "Reasonable" defaults hiding decisions
def fetch_users(limit=50):  # Why 50? Who decided?
    return db.query("SELECT * FROM users LIMIT %s", limit)


# WRONG: Hidden filter with no visibility
def get_active_records(records):
    # 40% of records vanish with no trace
    return [r for r in records if r.status == "active"]


# WRONG: Silent timeout
def safe_query(sql):
    try:
        return db.execute(sql, timeout=5)  # 5 seconds? Says who?
    except TimeoutError:
        return []  # SILENT FAILURE - data appears empty
```

**Why this is wrong:**
- Magic numbers with no documentation
- No configuration options
- No logging of limit application
- Silent data loss
- No metadata about what was constrained
- Impossible to debug or trace

---

### Configuration Pattern

```python
# config/limits.py - Central location for all limits

"""
ZERO TRUST CONFIGURATION

Every limit in this file must have:
1. DECISION_SOURCE: Who decided this value
2. RATIONALE: Why this value
3. CONFIGURABLE: Whether it can be overridden
4. DEFAULT_BEHAVIOR: What happens if not set

Prefer None (no limit) as default.
"""

from dataclasses import dataclass
from typing import Optional
import os


@dataclass
class LimitConfig:
    value: Optional[int]
    decision_source: str  # "HUMAN: Jeremy 2026-01-23" or "AI_DEFAULT"
    rationale: str
    env_var: str

    @classmethod
    def from_env(cls, env_var: str, default: Optional[int],
                 decision_source: str, rationale: str) -> 'LimitConfig':
        env_value = os.getenv(env_var)
        return cls(
            value=int(env_value) if env_value else default,
            decision_source=decision_source,
            rationale=rationale,
            env_var=env_var,
        )


# EXAMPLE CONFIGURATIONS

BATCH_SIZE = LimitConfig.from_env(
    env_var="BATCH_SIZE",
    default=None,  # No batching by default
    decision_source="AI_DEFAULT",
    rationale="No batching unless memory requires it. Set BATCH_SIZE env var to enable.",
)

QUERY_TIMEOUT = LimitConfig.from_env(
    env_var="QUERY_TIMEOUT_SECONDS",
    default=300,  # 5 minutes
    decision_source="HUMAN: Jeremy 2026-01-23",
    rationale="5 minutes allows complex queries. Increase if needed.",
)

MAX_RESULTS = LimitConfig.from_env(
    env_var="MAX_RESULTS",
    default=None,  # Return all by default
    decision_source="AI_DEFAULT",
    rationale="Return all results. Set MAX_RESULTS env var to paginate.",
)
```

---

### Metadata Pattern

```python
# Every response that could be limited includes metadata

@dataclass
class QueryResult:
    """Result with full transparency about any limits applied."""

    data: List[Any]

    # ZERO TRUST METADATA - always present
    _meta: dict = field(default_factory=lambda: {
        "zero_trust_version": "1.0",
        "total_available": None,
        "total_returned": None,
        "limits_applied": [],
        "filters_applied": [],
        "truncations_applied": [],
        "timeouts_triggered": [],
        "configuration": {},
    })

    def add_limit(self, limit_type: str, configured_value: Any,
                  items_before: int, items_after: int, reason: str):
        """Record that a limit was applied."""
        self._meta["limits_applied"].append({
            "type": limit_type,
            "configured_value": configured_value,
            "items_before": items_before,
            "items_after": items_after,
            "items_removed": items_before - items_after,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat(),
        })
```

---

### AI Code Review Checklist

When reviewing AI-generated code, check for:

```
ZERO TRUST CODE REVIEW CHECKLIST

[ ] MAGIC NUMBERS
    - Are there any hardcoded numeric limits?
    - Is each limit documented with decision source?
    - Is each limit configurable?

[ ] SLICING
    - Any [:N] or [N:] slicing?
    - Is the slice value configurable?
    - Is the truncation logged?

[ ] LOOPS
    - Any `for i in range(N)` with hardcoded N?
    - Any `while count < limit` with hardcoded limit?
    - Any `break` after N iterations?

[ ] QUERIES
    - Any `LIMIT N` in SQL?
    - Any `.limit(N)` in ORM?
    - Any pagination without surfacing total?

[ ] TIMEOUTS
    - Any hardcoded timeout values?
    - Are timeout triggers logged?
    - Is timeout behavior documented?

[ ] FILTERS
    - Any list comprehensions that filter?
    - Any `.filter()` calls?
    - Are filter statistics logged?

[ ] DEFAULTS
    - Any function parameters with default values that limit?
    - Are defaults documented?
    - Can defaults be overridden?

[ ] ERROR HANDLING
    - Any except blocks that return empty/partial data?
    - Are exceptions logged before handling?
    - Is error-caused data loss visible?
```

---

## Enforcement

### Automated Checks

| Tool | Check | Severity |
|------|-------|----------|
| `zero_trust_linter.py` | Magic number detection | error |
| `zero_trust_linter.py` | Undocumented slice operations | error |
| `zero_trust_linter.py` | Missing limit metadata | warning |
| `zero_trust_linter.py` | Hardcoded timeouts | warning |
| pre-commit hook | Zero trust compliance | blocking |

### Manual Review

Reviewers should:
1. **Trace every limit** — Can you find who decided each constraint?
2. **Check configurability** — Can every limit be changed without code changes?
3. **Verify metadata** — Does the response show what was limited?
4. **Test full data path** — What happens with no limits configured?

---

## Anti-Patterns Registry

### The "Reasonable Default" Anti-Pattern

```python
# AI writes this constantly
def fetch_data(limit=100):  # "100 seems reasonable"
```

**Problem**: "Reasonable" is an AI judgment call. Jeremy didn't decide 100.

**Fix**:
```python
def fetch_data(limit=None):  # Default: all data
    """
    Args:
        limit: Max records to return. Default None returns all.
               Configure via FETCH_LIMIT env var.
    """
```

### The "Safety Batch" Anti-Pattern

```python
# AI writes this "to be safe"
for batch in chunks(data, 1000):  # "batching for memory safety"
```

**Problem**: AI decided 1000 is safe. Maybe 10000 is fine. Maybe Jeremy wants it all.

**Fix**:
```python
batch_size = config.BATCH_SIZE.value  # None if not configured
if batch_size:
    logger.info(f"Batching: {batch_size} (configured via BATCH_SIZE)")
    batches = list(chunks(data, batch_size))
else:
    batches = [data]  # Process all at once
```

### The "Top N" Anti-Pattern

```python
# AI writes this to "show relevant results"
return sorted(results, key=lambda x: x.score)[:10]
```

**Problem**: The other results are gone forever. Jeremy can't see them.

**Fix**:
```python
sorted_results = sorted(results, key=lambda x: x.score)
limit = config.MAX_DISPLAY_RESULTS.value

if limit and len(sorted_results) > limit:
    logger.info(f"Showing top {limit} of {len(sorted_results)}. "
                f"Full results available via get_all_results()")
    return QueryResult(
        data=sorted_results[:limit],
        _meta={"total_available": len(sorted_results), "limited": True}
    )
return QueryResult(data=sorted_results, _meta={"limited": False})
```

### The "Timeout Safety" Anti-Pattern

```python
# AI writes this to "prevent hanging"
try:
    result = slow_operation(timeout=30)
except TimeoutError:
    return None  # Silent failure
```

**Problem**: Data appears empty when it's actually timing out. Jeremy can't tell.

**Fix**:
```python
timeout = config.SLOW_OPERATION_TIMEOUT.value  # Documented, configurable

try:
    result = slow_operation(timeout=timeout)
except TimeoutError as e:
    logger.error(f"TIMEOUT: slow_operation exceeded {timeout}s. "
                 f"Increase SLOW_OPERATION_TIMEOUT or investigate performance.")
    raise OperationTimeoutError(
        f"Operation timed out after {timeout}s",
        timeout_value=timeout,
        config_var="SLOW_OPERATION_TIMEOUT",
    )
```

### The "Dedup for Cleanliness" Anti-Pattern

```python
# AI writes this to "clean up data"
unique_results = list(set(results))
```

**Problem**: Duplicates removed with no visibility. Maybe duplicates matter.

**Fix**:
```python
original_count = len(results)
unique_results = list(dict.fromkeys(results))  # Preserve order
removed_count = original_count - len(unique_results)

if removed_count > 0:
    logger.info(f"DEDUP: Removed {removed_count} duplicates "
                f"({original_count} -> {len(unique_results)})")

return QueryResult(
    data=unique_results,
    _meta={
        "deduplication_applied": removed_count > 0,
        "duplicates_removed": removed_count,
        "original_count": original_count,
    }
)
```

---

## Escape Hatch

When a limit is genuinely needed and human-approved:

```python
# ZERO_TRUST_APPROVED: Jeremy 2026-01-23
# RATIONALE: BigQuery charges per byte scanned. Limit prevents cost explosion.
# REVIEWED: Limit is appropriate for this use case.
# CONFIGURABLE: Yes, via BQ_SCAN_LIMIT_GB env var
BQ_SCAN_LIMIT_GB = 10
```

The escape hatch requires:
1. `ZERO_TRUST_APPROVED:` tag with approver and date
2. `RATIONALE:` explaining why the limit exists
3. `REVIEWED:` confirming human review
4. `CONFIGURABLE:` stating how to override

---

## Integration with AI Certification System

**The Zero Trust Architecture standard is enforced through the AI Certification System.**

### Certification Checklist Addition

Add this to your certification assessment:

```markdown
### Zero Trust Compliance (Must Pass)
- [ ] No magic numbers: All numeric limits are named constants
- [ ] Decision sources documented: Every limit has HUMAN_DECISION or AI_DEFAULT comment
- [ ] Configurability: All limits can be overridden via config/env
- [ ] Metadata transparency: Responses include _meta showing limits applied
- [ ] No silent truncation: Any data reduction is logged and visible
- [ ] No hidden filters: Filter criteria documented and statistics logged
```

### Certification Statement Extension

When certifying code, include Zero Trust compliance:

```markdown
## Certification Statement

**Status:** ✅ CERTIFIED

**Zero Trust Compliance:**
- ✅ No magic numbers (all limits named and documented)
- ✅ Decision sources documented
- ✅ All limits configurable
- ✅ Metadata transparency implemented
- ⚠️ One AI_DEFAULT remaining: BATCH_SIZE (documented, configurable)

**Critical Issues:** None
**Production Readiness:** ✅ All checks passed
```

### Pre-Commit Hook Integration

The `enforce_ai_certification.py` hook should also check for:
- Presence of magic numbers (numeric literals in function calls)
- Missing `HUMAN_DECISION` or `AI_DEFAULT` comments on limits
- Undocumented slicing operations

### Peer Review Checkpoint

**For human reviewers, add this checkpoint:**

```markdown
## Zero Trust Review Checklist

Before approving AI-generated code:

1. [ ] Search for hardcoded numbers (grep for `\d+` in function calls)
2. [ ] Check each limit has documented decision source
3. [ ] Verify limits are configurable
4. [ ] Confirm response metadata shows any limits applied
5. [ ] Test: What happens if I set all limits to None?
```

---

## Industry Standards Alignment

This standard aligns with established industry practices:

### NIST SP 800-207 (Zero Trust Architecture)
- **Principle**: "Never trust, always verify"
- **Application**: Don't trust AI-generated limits; verify each decision source
- [NIST Zero Trust Architecture](https://pages.nist.gov/zero-trust-architecture/VolumeA/ProjectOverview.html)

### SonarSource Code Quality Rules
- **Rule S109**: "Magic numbers should not be used"
- **Application**: All numeric literals must be named constants
- [SonarSource Magic Numbers Rule](https://rules.sonarsource.com/c/rspec-109/)

### Forrester 2026 Technical Debt Predictions
- **Finding**: 75% of tech leaders will face moderate-to-severe technical debt by 2026
- **Cause**: AI generates "good enough" solutions with hidden limits
- **Solution**: This standard prevents invisible AI decisions
- [Qodo State of AI Code Quality](https://www.qodo.ai/reports/state-of-ai-code-quality/)

### MIT Code Review Standards
- **Principle**: Scan for literals not defined or named
- **Application**: Every limit must be traceable to a decision
- [MIT Code Review Reading](https://web.mit.edu/6.031/www/sp17/classes/04-code-review/)

---

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2026-01-23 | Initial standard | Claude (requested by Jeremy) |
| 2026-01-23 | Added AI Certification integration | Claude |
| 2026-01-23 | Added industry standards alignment | Claude |

---

## Related Standards

| Standard | Relationship |
|----------|-------------|
| [CONFIGURATION.md](CONFIGURATION.md) | How settings are managed |
| [LOGGING.md](LOGGING.md) | How limit applications are logged |
| [ERROR_HANDLING.md](ERROR_HANDLING.md) | How timeout/limit errors are handled |

## Related Rules

| Rule | Relationship |
|------|-------------|
| `13_THE_PATTERN_PHILOSOPHY` | Maximum exposure, architectural defense |
| `14_THE_SIGNAL` | Signals are data, preserve them |
| `15_NO_SILENT_FAILURES` | Care means telling |

---

*~500 lines. Zero Trust Architecture Standard. AI builds, humans decide. Complete.*
