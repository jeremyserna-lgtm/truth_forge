# Service Completeness Checklist

**The Standard** | Every service is a microcosm of the organism. This checklist ensures services are complete from cradle to grave.

**Authority**: 06_LAW.md, 00_GENESIS.md | **Status**: CANONICAL

---

## The Biological Imperative

Every service mirrors the organism. It has:
- **Birth** (initialization with spark)
- **Respiration** (inhale/exhale)
- **Circulation** (data flow)
- **Nervous system** (internal routing)
- **Heartbeat** (health monitoring)
- **Immune system** (validation/security)
- **Voice** (external communication)
- **Death** (graceful shutdown)

```
THE SERVICE AS ORGANISM
═══════════════════════════════════════════════════════════════════════════

HOLD₁ (RECEIVE)                    AGENT (PROCESS)                    HOLD₂ (DELIVER)
┌─────────────────┐               ┌─────────────────┐               ┌─────────────────┐
│                 │               │                 │               │                 │
│  👂 EARS        │               │  🧠 BRAIN       │               │  🗣️ VOICE       │
│  Listen for     │               │  Intelligent    │               │  Send external  │
│  external       │──────────────▶│  processing     │──────────────▶│  signals        │
│  signals        │               │                 │               │                 │
│                 │               │  🔀 NERVOUS     │               │  📤 OUTPUT      │
│  📥 INTAKE      │               │  Internal       │               │  Buffer         │
│  Buffer         │               │  routing        │               │  outgoing data  │
│  incoming data  │               │                 │               │                 │
│                 │               │  🫀 CIRCULATORY │               │  🔌 API         │
│  🛡️ MEMBRANE    │               │  Data flow      │               │  Interface for  │
│  Validate/      │               │  (inhale/exhale)│               │  others         │
│  filter what    │               │                 │               │  (@endpoints)   │
│  enters         │               │  💓 HEARTBEAT   │               │                 │
│                 │               │  State & health │               │                 │
└─────────────────┘               └─────────────────┘               └─────────────────┘

```

---

## Master Checklist

### Phase 1: CONCEPTION (Before Birth)

#### 1.1 Identity Declaration
- [ ] `SERVICE_NAME` - Unique identifier (snake_case)
- [ ] `SERVICE_DESCRIPTION` - What it does (one sentence)
- [ ] `SERVICE_VERSION` - Semantic version (X.Y.Z)
- [ ] `SERVICE_CATEGORY` - Type: `service` | `daemon` | `observer` | `gateway` | `core`
- [ ] `PATTERN_ROLE` - Role in THE PATTERN: `hold` | `agent` | `gateway`

#### 1.2 Lineage (Where did this come from?)
- [ ] `MOLT_SOURCE` - Original source file/doc
- [ ] `MOLT_RATIONALE` - Why it was molted/created
- [ ] `MOLT_VERSION` - Version of the molt
- [ ] `MOLT_DATE` - When it was created

#### 1.3 Capabilities Declaration
- [ ] `SERVICE_CAPABILITIES` - List of what it can do
- [ ] `REQUIRES` - What services it depends on
- [ ] `PROVIDES` - What it provides to others

---

### Phase 2: BIRTH (Initialization)

#### 2.1 The Spark (Life Grant)
- [ ] Inherits from `ServiceAPI`
- [ ] `REQUIRES_SPARK` attribute declared
- [ ] Spark validation in `__init__`
- [ ] Registered in `config/authorized_scripts.yaml` (if not spark_exempt)
- [ ] Raises `SparkRequiredError` if no valid spark

#### 2.2 Genesis Connection
- [ ] `super().__init__()` called
- [ ] `_start_time` recorded
- [ ] `_lock` for thread safety
- [ ] Initial state set to `initializing`

#### 2.3 Resource Initialization
- [ ] Data paths configured
- [ ] Connections established (lazy or eager)
- [ ] Internal state initialized
- [ ] Metrics counters initialized

```python
# BIRTH TEMPLATE
def __init__(self, spark_token: Optional[str] = None):
    """Initialize the service with life grant."""
    super().__init__(spark_token)  # Validates spark
    self._start_time = datetime.now(timezone.utc)
    self._lock = threading.Lock()
    
    # Initialize internal state
    self._data: List[Dict] = []
    self._metrics = {
        "operations": 0,
        "errors": 0,
    }
```

---

### Phase 3: RESPIRATION (Data Flow)

#### 3.1 Inhale (LEFT LUNG - Receive)
- [ ] `inhale()` method implemented
- [ ] Accepts data from external sources
- [ ] Validates incoming data (membrane)
- [ ] Buffers data in HOLD₁
- [ ] Updates `_last_activity`

#### 3.2 Exhale (RIGHT LUNG - Produce)
- [ ] `exhale()` method implemented
- [ ] Produces output from HOLD₂
- [ ] Formats data for consumers
- [ ] Updates `_last_activity`

#### 3.3 Sync (Synchronization)
- [ ] `sync()` method implemented
- [ ] Synchronizes internal state
- [ ] Returns sync status

```python
# RESPIRATION TEMPLATE
def inhale(self, data: Any = None, **kwargs) -> Any:
    """LEFT LUNG - Receive input."""
    self._last_activity = datetime.now(timezone.utc)
    
    # Validate (membrane)
    if not self._validate_input(data):
        raise ValueError("Invalid input")
    
    # Buffer in HOLD₁
    self._intake_buffer.append(data)
    return {"received": True, "buffered": len(self._intake_buffer)}

def exhale(self, **kwargs) -> Any:
    """RIGHT LUNG - Produce output."""
    self._last_activity = datetime.now(timezone.utc)
    
    # Produce from HOLD₂
    return self._output_buffer.pop() if self._output_buffer else None
```

---

### Phase 4: NERVOUS SYSTEM (Internal Routing)

#### 4.1 Endpoint Discovery
- [ ] All public operations decorated with `@endpoint()`
- [ ] Endpoint types specified (`QUERY` | `ACTION` | `STREAM` | `WEBHOOK`)
- [ ] Parameters documented with types
- [ ] Return types documented
- [ ] Examples provided

#### 4.2 Internal Routing
- [ ] `call_endpoint()` routes to correct method
- [ ] Error handling for unknown endpoints
- [ ] Activity tracking on each call

```python
# ENDPOINT TEMPLATE
@endpoint(
    description="Process a document",
    endpoint_type=EndpointType.ACTION,
    parameters={
        "document_id": {"type": "str", "required": True, "description": "Document to process"},
        "options": {"type": "dict", "required": False, "description": "Processing options"},
    },
    returns={
        "success": "bool",
        "processed_id": "str",
        "atoms_created": "int",
    },
    example={
        "input": {"document_id": "doc_123"},
        "output": {"success": True, "processed_id": "doc_123", "atoms_created": 15},
    },
)
def process_document(self, document_id: str, options: Optional[Dict] = None) -> Dict:
    """Process a document and extract atoms."""
    ...
```

---

### Phase 5: HEARTBEAT (Health Monitoring)

#### 5.1 State Tracking
- [ ] `get_state()` implemented
- [ ] Returns `ServiceState` object
- [ ] Status tracked: `on` | `off` | `error` | `initializing` | `stopping`
- [ ] Health tracked: `healthy` | `degraded` | `unhealthy`

#### 5.2 Metrics
- [ ] `record_metric()` used for key metrics
- [ ] `increment_metric()` for counters
- [ ] Uptime tracked
- [ ] Operation counts tracked
- [ ] Error counts tracked

#### 5.3 Error Tracking
- [ ] Errors logged to `_state.errors`
- [ ] Last 10 errors retained
- [ ] Error timestamps included

```python
# HEARTBEAT TEMPLATE
def get_state(self) -> ServiceState:
    """Get current service state (heartbeat)."""
    uptime = (datetime.now(timezone.utc) - self._start_time).total_seconds()
    
    with self._lock:
        return ServiceState(
            status="on",
            health=self._calculate_health(),
            last_activity=self._last_activity.isoformat() if self._last_activity else None,
            metrics={
                "uptime_seconds": uptime,
                "operations": self._metrics["operations"],
                "errors": self._metrics["errors"],
                "items_processed": len(self._data),
            },
            errors=self._errors[-10:],
        )

def _calculate_health(self) -> str:
    """Calculate health based on error rate."""
    if self._metrics["operations"] == 0:
        return "healthy"
    error_rate = self._metrics["errors"] / self._metrics["operations"]
    if error_rate > 0.5:
        return "unhealthy"
    elif error_rate > 0.1:
        return "degraded"
    return "healthy"
```

---

### Phase 6: IMMUNE SYSTEM (Validation & Security)

#### 6.1 Input Validation (Membrane)
- [ ] All inputs validated before processing
- [ ] Type checking
- [ ] Range checking
- [ ] Required field checking
- [ ] Malicious input detection

#### 6.2 Spark Validation
- [ ] Spark token validated on init
- [ ] `is_legitimate()` method works
- [ ] `get_spark_status()` returns status

#### 6.3 Error Handling (Four Pillars)
- [ ] **Fail-Safe**: Try/except around all operations
- [ ] **No Magic**: No hardcoded values
- [ ] **Observability**: All operations logged
- [ ] **Idempotency**: Safe to retry

```python
# IMMUNE SYSTEM TEMPLATE
def _validate_input(self, data: Any) -> bool:
    """Membrane - validate incoming data."""
    if data is None:
        return False
    if not isinstance(data, dict):
        return False
    required_fields = ["id", "content"]
    for field in required_fields:
        if field not in data:
            return False
    return True
```

---

### Phase 7: VOICE (External Communication)

#### 7.1 Manifest Exposure
- [ ] `get_manifest()` returns complete manifest
- [ ] Name, description, version included
- [ ] Capabilities listed
- [ ] Endpoints listed
- [ ] Dependencies listed

#### 7.2 API Response
- [ ] `to_api_response()` returns full API data
- [ ] Manifest included
- [ ] State included
- [ ] Endpoints included

#### 7.3 Registry Integration
- [ ] Auto-registered via metaclass
- [ ] Discoverable via `get_service_registry()`
- [ ] Callable via `registry.call()`

```python
# VOICE TEMPLATE
def get_manifest(self) -> ServiceManifest:
    """Voice - tell the world who I am."""
    return ServiceManifest(
        name=self.SERVICE_NAME,
        description=self.SERVICE_DESCRIPTION,
        version=self.SERVICE_VERSION,
        category=self.SERVICE_CATEGORY,
        tags=list(self.SERVICE_TAGS),
        molt_source=self.MOLT_SOURCE,
        molt_rationale=self.MOLT_RATIONALE,
        pattern_role=self.PATTERN_ROLE,
        capabilities=list(self.SERVICE_CAPABILITIES),
        endpoints=list(self._endpoints.values()),
        requires=list(self.REQUIRES),
        provides=list(self.PROVIDES),
        module_path=self.__class__.__module__,
        api_base=f"/api/services/{self.SERVICE_NAME}",
    )
```

---

### Phase 8: DEATH (Graceful Shutdown)

#### 8.1 Cleanup
- [ ] `shutdown()` or `__del__` implemented
- [ ] Connections closed
- [ ] Buffers flushed
- [ ] State persisted if needed

#### 8.2 Final State
- [ ] Status set to `off` or `stopped`
- [ ] Final metrics recorded
- [ ] Shutdown logged

```python
# DEATH TEMPLATE
def shutdown(self) -> None:
    """Graceful death - clean up resources."""
    with self._lock:
        # Flush buffers
        self._flush_output_buffer()
        
        # Close connections
        if self._connection:
            self._connection.close()
        
        # Set final state
        self._state.status = "off"
        
        _LOGGER.info(f"Service {self.SERVICE_NAME} shutdown complete")
```

---

### Phase 9: SINGLETON (Optional but Recommended)

#### 9.1 Singleton Pattern
- [ ] Module-level instance variable
- [ ] Thread-safe initialization
- [ ] `get_<service_name>()` function

```python
# SINGLETON TEMPLATE
_instance: Optional[MyService] = None
_lock = threading.Lock()

def get_my_service() -> MyService:
    """Get the singleton instance."""
    global _instance
    if _instance is None:
        with _lock:
            if _instance is None:
                _instance = MyService()
    return _instance
```

---

### Phase 10: MODERN PATTERNS (Advanced Python - REQUIRED)

**Framework Alignment**: These patterns directly support the Four Pillars (06_LAW.md)

#### 10.1 Type Safety (CRITICAL - BLOCKING)
- [ ] All return types use TypedDict (not Dict[str, Any])
- [ ] All dataclasses use `slots=True`
- [ ] Protocol used for dependency injection
- [ ] `__all__` exports declared at module level
- [ ] Full type hints on all public methods

#### 10.2 Resource Management
- [ ] Context managers for lock acquisition (`locked_operation`)
- [ ] WeakRef for service caching (memory-safe)
- [ ] `cached_property` for expensive computations
- [ ] `ExitStack` for multiple resource cleanup

#### 10.3 Code Patterns
- [ ] Pattern matching for Result handling (`match result:`)
- [ ] Walrus operator for stream processing (`:=`)
- [ ] `itertools` for efficient iteration (`islice`, `chain`, `groupby`)
- [ ] Generator expressions instead of list comprehensions (when iterating once)

```python
# MODERN PATTERNS TEMPLATE
from __future__ import annotations

import threading
from dataclasses import dataclass, field
from functools import cached_property
from typing import TypedDict, Protocol, runtime_checkable
from contextlib import contextmanager
from itertools import islice

# 1. TypedDict for return types (No Magic)
class ProcessResult(TypedDict):
    success: bool
    processed_id: str
    atoms_created: int

# 2. Protocol for dependencies (No Magic)
@runtime_checkable
class Auditable(Protocol):
    def record_audit(self, operation: str, **context) -> None: ...

# 3. slots dataclass (Observability - predictable memory)
@dataclass(slots=True, kw_only=True)
class ServiceConfig:
    name: str
    timeout: float = 30.0
    
    def __post_init__(self):
        if self.timeout <= 0:
            raise ValueError("timeout must be positive")

# 4. Context manager for locks (Fail-Safe)
@contextmanager
def locked_operation(lock: threading.Lock, timeout: float = 5.0):
    acquired = lock.acquire(timeout=timeout)
    if not acquired:
        raise TimeoutError("Could not acquire lock")
    try:
        yield
    finally:
        lock.release()

# 5. cached_property for expensive computations
class MyService(ServiceAPI):
    @cached_property
    def expensive_resource(self):
        return load_expensive_resource()

# 6. __all__ for explicit public API
__all__ = [
    "ProcessResult",
    "Auditable", 
    "ServiceConfig",
    "locked_operation",
    "MyService",
]
```

---

## Quick Reference Card

### Minimum Viable Service

```python
"""Minimum viable service that mirrors the organism."""
from __future__ import annotations

import threading
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from Primitive.governance.service_api import (
    ServiceAPI,
    endpoint,
    EndpointType,
    ServiceState,
)

class MinimalService(ServiceAPI):
    """A minimal but complete service."""

    # === IDENTITY (Phase 1) ===
    SERVICE_NAME = "minimal_service"
    SERVICE_DESCRIPTION = "A minimal but complete service"
    SERVICE_VERSION = "1.0.0"
    SERVICE_CATEGORY = "service"
    PATTERN_ROLE = "agent"
    
    # === LINEAGE ===
    MOLT_SOURCE = "framework/standards/SERVICE_COMPLETENESS_CHECKLIST.md"
    MOLT_RATIONALE = "Template for minimal viable service"
    
    # === CAPABILITIES ===
    SERVICE_CAPABILITIES = ["process", "query"]
    REQUIRES: List[str] = []
    PROVIDES = ["minimal_processing"]

    def __init__(self, spark_token: Optional[str] = None):
        """=== BIRTH (Phase 2) ==="""
        super().__init__(spark_token)
        self._start_time = datetime.now(timezone.utc)
        self._lock = threading.Lock()
        self._data: List[Dict] = []
        self._errors: List[str] = []
        self._metrics = {"operations": 0, "errors": 0}

    # === RESPIRATION (Phase 3) ===
    def inhale(self, data: Any = None, **kwargs) -> Any:
        """LEFT LUNG - Receive input."""
        self._last_activity = datetime.now(timezone.utc)
        if data:
            self._data.append(data)
        return {"received": True}

    def exhale(self, **kwargs) -> Any:
        """RIGHT LUNG - Produce output."""
        self._last_activity = datetime.now(timezone.utc)
        return {"data": self._data}

    # === NERVOUS SYSTEM (Phase 4) ===
    @endpoint(
        description="Process data",
        endpoint_type=EndpointType.ACTION,
        parameters={"input": {"type": "dict", "required": True}},
        returns={"success": "bool", "result": "dict"},
    )
    def process(self, input: Dict) -> Dict:
        """Process input data."""
        with self._lock:
            self._metrics["operations"] += 1
        self._data.append(input)
        return {"success": True, "result": input}

    @endpoint(
        description="Query data",
        endpoint_type=EndpointType.QUERY,
        returns={"count": "int", "data": "list"},
    )
    def query(self) -> Dict:
        """Query stored data."""
        return {"count": len(self._data), "data": self._data}

    # === HEARTBEAT (Phase 5) ===
    def get_state(self) -> ServiceState:
        """Get current state (heartbeat)."""
        uptime = (datetime.now(timezone.utc) - self._start_time).total_seconds()
        return ServiceState(
            status="on",
            health="healthy",
            last_activity=self._last_activity.isoformat() if self._last_activity else None,
            metrics={
                "uptime_seconds": uptime,
                **self._metrics,
            },
            errors=self._errors[-10:],
        )

    # === IMMUNE SYSTEM (Phase 6) - Inherited from ServiceAPI ===
    # === VOICE (Phase 7) - Inherited from ServiceAPI ===
    # === DEATH (Phase 8) ===
    def shutdown(self) -> None:
        """Graceful shutdown."""
        self._state.status = "off"


# === SINGLETON (Phase 9) ===
_instance: Optional[MinimalService] = None
_lock = threading.Lock()

def get_minimal_service() -> MinimalService:
    """Get singleton instance."""
    global _instance
    if _instance is None:
        with _lock:
            if _instance is None:
                _instance = MinimalService()
    return _instance
```

---

## Validation Checklist

Before a service is considered complete, verify:

### Identity & Lineage
- [ ] All 5 identity attributes declared
- [ ] MOLT lineage documented
- [ ] Capabilities declared

### Life Cycle
- [ ] Birth: Spark validation works
- [ ] Respiration: inhale/exhale implemented
- [ ] Heartbeat: get_state() returns valid state
- [ ] Death: shutdown() cleans up

### Nervous System
- [ ] All endpoints decorated
- [ ] Parameters documented
- [ ] Return types documented
- [ ] Examples provided

### Four Pillars (06_LAW)
- [ ] **Fail-Safe**: Error handling complete
- [ ] **No Magic**: No hardcoded values
- [ ] **Observability**: All operations logged
- [ ] **Idempotency**: Safe to retry

### Modern Patterns (Phase 10)
- [ ] TypedDict for all return types
- [ ] slots=True on all dataclasses
- [ ] __all__ declared
- [ ] cached_property for lazy loading
- [ ] Context managers for resources

### Integration
- [ ] Auto-registered in registry
- [ ] Discoverable via API
- [ ] Callable via registry.call()

---

## Related Standards

- [SERVICE_API_LAYER.md](SERVICE_API_LAYER.md) — API Layer specification
- [06_LAW.md](../../framework/06_LAW.md) — The Four Pillars
- [00_GENESIS.md](../../framework/00_GENESIS.md) — The Seed
- [PRIMITIVE_PATTERN_SPECIFICATION.md](PRIMITIVE_PATTERN_SPECIFICATION.md) — THE PATTERN

---

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2026-01-20 | Initial standard | Claude |
| 2026-01-21 | Added Phase 10: Modern Patterns - TypedDict, slots, __all__, cached_property | Claude |
