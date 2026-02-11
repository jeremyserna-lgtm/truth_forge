# Governance System

**Layer**: Specification (WHAT)
**Purpose**: Understand how universal governance policies ensure system integrity

---

## 🎓 LEARNING: What is Governance?

Governance is not bureaucracy—it's **the structure that prevents chaos**. It's The Furnace's control rods. Without governance, the system would be a bomb instead of a reactor.

### The Core Principle

**All code must follow universal governance policies, NOT pipeline-specific patterns.**

This means:
- Every operation must be traceable
- Every operation must be auditable
- Every operation must be observable
- Every error must be diagnosed

---

## 💡 CONCEPT: The Four Pillars

### 1. Traceability (REQUIRED for ALL operations)

**What it is**: Every operation must be traceable through the system.

**How to implement**:
```python
from architect_central_services.core import get_logger, get_current_run_id, get_correlation_ids

# Get traceability context
run_id = get_current_run_id()
correlation_ids = get_correlation_ids()
logger = get_logger(__name__)

# Include in all logs
logger.info("Processing data", extra={
    'run_id': run_id,
    'correlation_id': correlation_ids.get('correlation_id'),
    'trace_id': correlation_ids.get('trace_id'),
    'component': 'my_service',
    'operation': 'process_data',
    'step': 'transformation'
})
```

**Why it matters**: Without traceability, you can't debug problems or understand system behavior.

---

### 2. Audit Trail (REQUIRED for ALL operations)

**What it is**: Every operation must be recorded in the audit trail.

**How to implement**:
```python
from architect_central_services.governance.governance_service.unified_governance import get_unified_governance
from architect_central_services.governance.governance_service.models import AuditRecord

governance = get_unified_governance()

# Record operation
governance.record_audit(AuditRecord(
    operation="process_data",
    component="my_service",
    run_id=run_id,
    status="success",
    details={"records_processed": 100}
))
```

**Why it matters**: The audit trail is the permanent record of what happened. It's the system's memory.

---

### 3. Structured Logging (REQUIRED for ALL operations)

**What it is**: All logs must be structured and include context.

**How to implement**:
```python
# ✅ GOOD: Structured logging
logger.info("Processing file", extra={
    'run_id': run_id,
    'component': 'file_processor',
    'operation': 'process_file',
    'step': 'reading',
    'file_path': '/path/to/file.jsonl',
    'file_size': 1024
})

# ❌ BAD: Unstructured logging
print(f"Processing file: /path/to/file.jsonl")  # Don't do this!
```

**Why it matters**: Structured logs enable searching, filtering, and analysis. Unstructured logs are noise.

---

### 4. Error Handling (REQUIRED for ALL operations)

**What it is**: All errors must be handled gracefully with diagnostics.

**How to implement**:
```python
from architect_central_services.governance.diagnostic_enforcer import require_diagnostic_on_error

try:
    result = process_data(data)
except Exception as e:
    # Require diagnostic on error
    diagnostic = require_diagnostic_on_error(
        error=e,
        operation="process_data",
        component="my_service",
        run_id=run_id,
        context={"data_size": len(data)}
    )

    # Record to audit trail
    governance.record_audit(AuditRecord(
        operation="process_data",
        component="my_service",
        run_id=run_id,
        status="error",
        error=str(e),
        diagnostic=diagnostic
    ))

    # Re-raise or handle appropriately
    raise
```

**Why it matters**: Errors without diagnostics are mysteries. Diagnostics turn mysteries into solvable problems.

---

## 🎯 PRACTICE: Adding Governance to Your Code

### Step 1: Import Required Modules

```python
from architect_central_services.core import get_logger, get_current_run_id, get_correlation_ids
from architect_central_services.governance.governance_service.unified_governance import get_unified_governance
from architect_central_services.governance.governance_service.models import AuditRecord
from architect_central_services.governance.diagnostic_enforcer import require_diagnostic_on_error
```

### Step 2: Initialize Context

```python
# Get traceability context
run_id = get_current_run_id()
correlation_ids = get_correlation_ids()
logger = get_logger(__name__)
governance = get_unified_governance()
```

### Step 3: Add Logging

```python
logger.info("Starting operation", extra={
    'run_id': run_id,
    'component': __name__,
    'operation': 'my_operation',
    'step': 'start'
})
```

### Step 4: Add Error Handling

```python
try:
    result = do_work()
    logger.info("Operation completed", extra={
        'run_id': run_id,
        'component': __name__,
        'operation': 'my_operation',
        'step': 'complete',
        'result': result
    })
except Exception as e:
    diagnostic = require_diagnostic_on_error(
        error=e,
        operation="my_operation",
        component=__name__,
        run_id=run_id
    )
    governance.record_audit(AuditRecord(
        operation="my_operation",
        component=__name__,
        run_id=run_id,
        status="error",
        error=str(e),
        diagnostic=diagnostic
    ))
    raise
```

### Step 5: Record Audit

```python
governance.record_audit(AuditRecord(
    operation="my_operation",
    component=__name__,
    run_id=run_id,
    status="success",
    details={"records_processed": len(result)}
))
```

---

## ⚠️ WARNING: Common Mistakes

### 1. Using print() Instead of Logging

**Don't do this:**
```python
print("Processing file...")  # ❌ BAD
```

**Do this instead:**
```python
logger.info("Processing file", extra={'file': file_path})  # ✅ GOOD
```

### 2. Skipping Error Diagnostics

**Don't do this:**
```python
try:
    result = process()
except Exception as e:
    logger.error(f"Error: {e}")  # ❌ BAD: No diagnostic
```

**Do this instead:**
```python
try:
    result = process()
except Exception as e:
    diagnostic = require_diagnostic_on_error(error=e, ...)  # ✅ GOOD
    logger.error("Error occurred", extra={'error': str(e), 'diagnostic': diagnostic})
```

### 3. Missing Traceability

**Don't do this:**
```python
logger.info("Processing")  # ❌ BAD: No run_id, no context
```

**Do this instead:**
```python
logger.info("Processing", extra={
    'run_id': run_id,
    'component': __name__,
    'operation': 'process'
})  # ✅ GOOD
```

---

## 🚀 MOMENTUM: Why Governance Matters

Governance is not about slowing you down—it's about:

1. **Preventing problems** - Catch issues before they become disasters
2. **Enabling debugging** - Traceability makes problems solvable
3. **Building trust** - Audit trails prove the system works correctly
4. **Enabling growth** - Structure enables scale

---

## 🧬 Governance Technologies

The governance system is implemented as four interlocking components in `truth_forge.governance`:

### UnifiedGovernance (The Membrane Orchestrator)

The central coordinator that brings all governance together:

```python
from truth_forge.governance import get_governance

gov = get_governance()

# Gate an operation
if gov.gate_operation("write", source="agent", target="hold2"):
    # Proceed with operation
    pass

# Check and record costs
if gov.check_cost("openai", "completion", estimated_cost=0.05):
    result = call_llm(...)
    gov.record_cost("openai", "completion", actual_cost=0.04)
```

### HoldIsolation (Selective Permeability)

Enforces HOLD₁/HOLD₂ boundary integrity:

| Source | Operation | Target | Allowed |
|--------|-----------|--------|---------|
| external | write | HOLD₁ | ✅ |
| agent | read | HOLD₁ | ✅ |
| agent | write | HOLD₂ | ✅ |
| external | write | HOLD₂ | ❌ |
| consumer | write | HOLD₂ | ❌ |

### CostEnforcer (Metabolic Regulation)

Budget gates that protect against runaway costs:

- **Daily limit**: $10.00 default
- **Monthly limit**: $100.00 default  
- **Per-run limit**: $1.00 default
- **Actions**: ALLOW, WARN, DENY, THROTTLE

### AuditTrail (Cellular Memory)

Immutable record of all operations:

- **Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL, VIOLATION
- **Categories**: HOLD_OPERATION, AGENT_ACTION, GOVERNANCE, COST, FEDERATION, SYSTEM

### The `@governed` Decorator

For simple governance enforcement:

```python
from truth_forge.governance import governed

@governed(operation="write", source="agent", target="hold2")
def my_function():
    # Automatically gated by governance
    pass
```

---

## 📚 Next Steps

Now that you understand Governance, read:
- **[Data Flow Patterns](./03_DATA_FLOW.md)** - How governance ensures data integrity
- **[Working with Services](../implementation/01_WORKING_WITH_SERVICES.md)** - How to use services with governance
- **Implementation**: `src/truth_forge/governance/` for the actual code

---

## 🌐 External Agentic Protocols

Beyond internal governance, Truth Forge integrates with three external protocols that enable agent interoperability:

### Protocol Stack

| Layer | Protocol | Purpose | Implementation |
|-------|----------|---------|----------------|
| **Discovery** | MCP (Model Context Protocol) | Tool discovery & invocation | `mcp-servers/truth-engine-mcp/` |
| **Payment** | x402 (Coinbase) | Autonomous USDC micropayments | `src/truth_engine/x402/payments.py` |
| **Credentials** | W3C VC 2.0 | Credential issuance & verification | Credential Atlas design |

### Why These Protocols?

1. **MCP (Anthropic, Nov 2024)**: Universal tool interface adopted by OpenAI, Google, Microsoft. The "USB-C for AI."

2. **x402 (Coinbase, 2025)**: HTTP 402 + USDC on Base enables agent-to-agent payments without accounts or API keys.

3. **W3C VC 2.0 (May 2025)**: Non-blockchain credential standard that interoperates with MIT, EU EBSI, and enterprise ecosystems.

### Integration Pattern

```
External Agent → MCP (discovers tools) → x402 (pays for service) → W3C VC (receives credential)
```

**Deep Dives**:
- `docs/research/deep_dives/01_MCP_Model_Context_Protocol.md`
- `docs/research/deep_dives/02_x402_Agentic_Payments.md`
- `docs/research/deep_dives/06_Integration_Roadmap.md`

---

**Remember**: Governance is The Furnace's control rods. Without it, the system would be chaos. With it, the system transforms truth into structure.
