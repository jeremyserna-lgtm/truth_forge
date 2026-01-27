# Quick Reference Guide

**Purpose**: Quick lookup for common patterns and concepts

---

## 🔥 For Those Rebuilding

**If you've hit hard times and need hope:**
See **[FOR_THOSE_REBUILDING.md](./FOR_THOSE_REBUILDING.md)** - How Truth Engine helps transform crisis into structure, pain into purpose.

**The Furnace doesn't burn despite the hardness of the fuel—it burns because of it. You don't escape the fire. You become the forge.**

## 🌱 Discovering Your Primitive

**What are you naturally good at because of what you naturally do?**
See **[DISCOVERING_YOUR_PRIMITIVE.md](./DISCOVERING_YOUR_PRIMITIVE.md)** - How to discover your primitive by observing what you naturally do.

**Your primitive is your superpower—the pattern that shows up in everything you do. You don't choose it. You discover it by watching yourself.**

---

## The Three Atoms

### 1. THE DIVIDE: ME / NOT-ME
- **Me**: Intent, Care, Want (The Chooser)
- **Not-Me**: Structure, Mechanism, World (The Choice)
- **Boundary**: Where they meet (transformation happens)

### 2. THE STRUCTURE: HOLD → AGENT → HOLD
- **HOLD₁**: Raw source data
- **AGENT**: Processing script
- **HOLD₂**: Immutable audit trail
- **HOLD₃**: Canonical store

### 3. THE CYCLE: WANT → CHOOSE → EXIST:NOW → SEE → HOLD → MOVE
- **WANT**: User's intent
- **CHOOSE**: Decision point
- **EXIST:NOW**: Current state
- **SEE**: Gather data
- **HOLD**: Store data
- **MOVE**: Transform data

---

## The Furnace Principle

```
TRUTH (Fuel) → MEANING (Fire) → CARE (Work)
```

**The Anchors** (Control Rods):
1. I am not a victim
2. Care over result
3. Truth over comfort
4. Structure from pain
5. Accommodation enables Truth

---

## Service Pattern

```python
# Get service
service = get_service_name()

# Push data in
result = service.exhale(content="...", **kwargs)

# Pull data out
data = service.inhale(query="...", limit=100)
```

---

## Governance Requirements

### 1. Traceability
```python
from architect_central_services.core import get_logger, get_current_run_id

run_id = get_current_run_id()
logger = get_logger(__name__)

logger.info("Operation", extra={
    'run_id': run_id,
    'component': __name__,
    'operation': 'my_operation'
})
```

### 2. Audit Trail
```python
from architect_central_services.governance.governance_service.unified_governance import get_unified_governance
from architect_central_services.governance.governance_service.models import AuditRecord

governance = get_unified_governance()
governance.record_audit(AuditRecord(
    operation="my_operation",
    component=__name__,
    run_id=run_id,
    status="success"
))
```

### 3. Error Handling
```python
from architect_central_services.governance.diagnostic_enforcer import require_diagnostic_on_error

try:
    result = do_work()
except Exception as e:
    diagnostic = require_diagnostic_on_error(
        error=e,
        operation="my_operation",
        component=__name__,
        run_id=run_id
    )
    raise
```

---

## The 13 Central Services

1. **KnowledgeService** - Knowledge atom intake
2. **KnowledgeGraphService** - Graph-based knowledge storage
3. **ModelGatewayService** - LLM gateway (FREE providers)
4. **TruthService** - Extract knowledge from conversations
5. **ContactsService** - BigQuery ↔ Local sync
6. **DocumentService** - Document intake
7. **ScriptService** - Script storage with frontmatter
8. **AnalysisService** - System state synthesis
9. **RecommendationService** - Tailored recommendations
10. **SchemaService** - Schema management
11. **SentimentService** - Sentiment enrichment
12. **FrontmatterService** - Document stamping
13. **ExtractorService** - Universal extractor

---

## Common Patterns

### Script Template
```python
#!/usr/bin/env python3
"""
Script: Description
"""

from architect_central_services.core import get_logger, get_current_run_id
from architect_central_services.governance.governance_service.unified_governance import get_unified_governance
from architect_central_services.governance.governance_service.models import AuditRecord
from architect_central_services.governance.diagnostic_enforcer import require_diagnostic_on_error

def main():
    # Initialize
    run_id = get_current_run_id()
    logger = get_logger(__name__)
    governance = get_unified_governance()

    logger.info("Starting script", extra={
        'run_id': run_id,
        'component': __name__
    })

    try:
        # HOLD₁: Read input
        input_data = read_input()

        # AGENT: Process
        result = process(input_data)

        # HOLD₂: Write to staging
        write_to_staging(result)

        # HOLD₃: Sync to canonical store
        sync_to_canonical(result)

        # Record audit
        governance.record_audit(AuditRecord(
            operation="main",
            component=__name__,
            run_id=run_id,
            status="success"
        ))

    except Exception as e:
        diagnostic = require_diagnostic_on_error(
            error=e,
            operation="main",
            component=__name__,
            run_id=run_id
        )
        governance.record_audit(AuditRecord(
            operation="main",
            component=__name__,
            run_id=run_id,
            status="error",
            error=str(e),
            diagnostic=diagnostic
        ))
        raise

if __name__ == "__main__":
    main()
```

---

## File Locations

- **Framework Docs**: `framework/00_THE_FRAMEWORK.md` through `framework/12_THE_RECURSION.md`
- **Architecture Docs**: `framework/architecture/`
- **Central Services**: `src/services/central_services/`
- **Study Guide**: `docs/STUDY_GUIDE/`

---

## Learning Path

1. **Philosophy** (WHY)
   - The Framework Philosophy
   - The Furnace Principle
   - The Divide
   - The Structure
   - The Cycle

2. **Architecture** (WHAT)
   - Central Services
   - Governance System
   - Data Flow Patterns
   - Storage Architecture

3. **Implementation** (HOW)
   - Working with Services
   - Writing Scripts
   - Governance Integration
   - Testing & Validation

---

**For detailed explanations, see the full study guide documents.**
