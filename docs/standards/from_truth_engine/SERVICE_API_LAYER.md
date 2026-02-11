# Service API Layer Standard

**The Standard** | Every service exposes a self-describing API for discovery, communication, and no-code interaction.

**Authority**: [08_THE_API_LAYER.md](../../docs/business/the_framework/08_THE_API_LAYER.md) | **Status**: CANONICAL

---

## Quick Reference

| Requirement | Rule |
|-------------|------|
| ServiceAPI Base | All services MUST inherit from ServiceAPI |
| Manifest | All services MUST expose a manifest |
| Endpoints | All operations MUST be decorated as endpoints |
| State | All services MUST expose current state |
| Registry | All services auto-register via metaclass |
| Pattern Role | All services MUST declare HOLD/AGENT/GATEWAY role |

---

## WHY (Theory)

### The No-Code Imperative

Jeremy codes by speaking. Apps need to discover services. Services need to communicate. The ServiceAPI Layer enables all of this without writing code.

From THE_FRAMEWORK:
> "If it doesn't have an API Layer, it doesn't exist."

### The Visibility Principle

The API Layer IS the visibility layer. Every service that exists must be discoverable, callable, and observable through its API.

### The Molt Inheritance

When organisms molt, they inherit the ServiceAPI pattern. Every daughter organism has full API visibility into its services.

---

## WHAT (Specification)

### Service API Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        SERVICE API LAYER                                 │
│                                                                          │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐       │
│  │    MANIFEST      │  │    ENDPOINTS     │  │     STATE        │       │
│  │                  │  │                  │  │                  │       │
│  │  name            │  │  @endpoint()     │  │  status          │       │
│  │  description     │  │  name            │  │  health          │       │
│  │  version         │  │  description     │  │  uptime          │       │
│  │  category        │  │  type            │  │  metrics         │       │
│  │  capabilities    │  │  parameters      │  │  last_action     │       │
│  │  pattern_role    │  │  returns         │  │                  │       │
│  │  molt_source     │  │  example         │  │                  │       │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘       │
│                                                                          │
│                              │                                           │
│                              ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    SERVICE REGISTRY                              │    │
│  │                                                                   │    │
│  │  list_services() → [service1, service2, ...]                     │    │
│  │  get_service(name) → service                                     │    │
│  │  call(service, endpoint, **kwargs) → result                      │    │
│  │  get_api_map() → complete discovery data                         │    │
│  └─────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
```

### MUST (Required)

#### 1. Inherit from ServiceAPI

Every service MUST inherit from `ServiceAPI`:

```python
from Primitive.governance.service_api import ServiceAPI, endpoint, EndpointType

class CostService(ServiceAPI):
    """Cost tracking and governance service."""

    SERVICE_NAME = "cost_service"
    SERVICE_DESCRIPTION = "Tracks and enforces cost governance"
    SERVICE_VERSION = "1.0.0"
    SERVICE_CATEGORY = "service"  # service, daemon, observer, gateway
    MOLT_SOURCE = "daemon/cost_tracker.py"
    PATTERN_ROLE = "agent"  # hold, agent, gateway
```

#### 2. Expose Manifest

Every service MUST have a complete manifest:

```python
@dataclass
class ServiceManifest:
    name: str                    # Unique identifier
    description: str             # What it does
    version: str                 # Semantic version
    category: str                # service, daemon, observer, gateway
    capabilities: List[str]      # What it can do
    endpoints: List[Endpoint]    # Callable operations
    molt_source: Optional[str]   # Origin in MOLT
    pattern_role: str            # hold, agent, gateway
    lineage: Dict[str, Any]      # MOLT lineage
```

#### 3. Decorate Endpoints

Every callable operation MUST be an endpoint:

```python
@endpoint(
    description="Get cost tracking summary",
    endpoint_type=EndpointType.QUERY,
    parameters={
        "since": {"type": "datetime", "required": False, "description": "Start time"},
        "category": {"type": "str", "required": False, "description": "Cost category"}
    },
    returns={
        "total_usd": {"type": "float", "description": "Total cost in USD"},
        "by_category": {"type": "dict", "description": "Breakdown by category"},
        "count": {"type": "int", "description": "Number of cost entries"}
    },
    example={
        "input": {"since": "2026-01-01T00:00:00Z"},
        "output": {"total_usd": 1.23, "by_category": {"api": 0.50}, "count": 15}
    }
)
def get_summary(self, since: Optional[datetime] = None, category: Optional[str] = None) -> Dict:
    """Get cost tracking summary."""
    ...
```

#### 4. Endpoint Types

| Type | Use Case | Side Effects |
|------|----------|--------------|
| `QUERY` | Read-only operations | None |
| `ACTION` | Operations that change state | Yes |
| `STREAM` | Continuous data flow | Ongoing |
| `WEBHOOK` | External event triggers | External |

#### 5. Expose State

Every service MUST expose current state:

```python
def get_state(self) -> ServiceState:
    return ServiceState(
        status="on",                    # on, off, error, initializing
        health="healthy",               # healthy, degraded, unhealthy
        uptime_seconds=self._uptime(),
        last_action=self._last_action,
        error_message=None,
        metrics={
            "requests_handled": self._request_count,
            "errors": self._error_count
        }
    )
```

#### 6. Pattern Role

Every service MUST declare its role in THE PATTERN:

| Role | Description | Examples |
|------|-------------|----------|
| `hold` | Receives/stores data | staging, DuckDB, queues |
| `agent` | Processes/transforms | extractors, enrichers |
| `gateway` | Bridges internal/external | APIs, webhooks |

#### 7. Auto-Registration

Services auto-register via metaclass:

```python
class ServiceAPIMeta(type):
    """Metaclass that auto-registers services when defined."""
    _registry: Dict[str, Type["ServiceAPI"]] = {}

    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        if name != "ServiceAPI":  # Don't register base class
            service_name = namespace.get("SERVICE_NAME", name.lower())
            mcs._registry[service_name] = cls
        return cls
```

### SHOULD (Recommended)

#### 1. Provide Examples

Endpoints SHOULD include examples:

```python
@endpoint(
    ...,
    example={
        "input": {"query": "what is my cost today?"},
        "output": {"total_usd": 1.23, "categories": ["api", "embedding"]}
    }
)
```

#### 2. Define Capabilities

Services SHOULD declare capabilities:

```python
SERVICE_CAPABILITIES = [
    "track_cost",
    "enforce_budget",
    "alert_threshold",
    "generate_report"
]
```

#### 3. Include MOLT Lineage

Services SHOULD include MOLT source:

```python
MOLT_SOURCE = "daemon/cost_tracker.py"
MOLT_RATIONALE = "Cost tracking molted from daemon to central service"
```

### MUST NOT (Prohibited)

1. **Never bypass the registry** — All service access through registry
2. **Never hide operations** — Every callable must be an endpoint
3. **Never omit state** — Services must expose current state
4. **Never create unregistered services** — Metaclass handles registration

---

## HOW (Reference)

### Complete Service Implementation

```python
"""
cost_service.py - Cost Governance Service

MOLT:
- Source: daemon/cost_tracker.py
- Rationale: Central cost tracking with API visibility
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from Primitive.governance.service_api import (
    ServiceAPI,
    endpoint,
    EndpointType,
    ServiceState,
)

class CostService(ServiceAPI):
    """Cost tracking and governance service."""

    # Required class attributes
    SERVICE_NAME = "cost_service"
    SERVICE_DESCRIPTION = "Tracks API costs, enforces budgets, generates reports"
    SERVICE_VERSION = "1.0.0"
    SERVICE_CATEGORY = "service"
    PATTERN_ROLE = "agent"
    MOLT_SOURCE = "daemon/cost_tracker.py"

    SERVICE_CAPABILITIES = [
        "track_cost",
        "get_summary",
        "enforce_budget",
        "set_budget_limit",
    ]

    def __init__(self):
        super().__init__()
        self._costs: List[Dict] = []
        self._budget_limit_usd: float = 50.0
        self._start_time = datetime.now(timezone.utc)

    @endpoint(
        description="Track a cost entry",
        endpoint_type=EndpointType.ACTION,
        parameters={
            "amount_usd": {"type": "float", "required": True},
            "category": {"type": "str", "required": True},
            "description": {"type": "str", "required": False},
        },
        returns={"success": "bool", "total_usd": "float"},
    )
    def track_cost(
        self,
        amount_usd: float,
        category: str,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Track a cost entry."""
        entry = {
            "amount_usd": amount_usd,
            "category": category,
            "description": description,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._costs.append(entry)
        total = sum(c["amount_usd"] for c in self._costs)
        return {"success": True, "total_usd": total}

    @endpoint(
        description="Get cost summary",
        endpoint_type=EndpointType.QUERY,
        parameters={
            "since": {"type": "datetime", "required": False},
        },
        returns={
            "total_usd": "float",
            "by_category": "dict",
            "count": "int",
        },
        example={
            "input": {},
            "output": {"total_usd": 1.23, "by_category": {"api": 1.23}, "count": 5},
        },
    )
    def get_summary(self, since: Optional[datetime] = None) -> Dict[str, Any]:
        """Get cost summary."""
        costs = self._costs
        if since:
            costs = [c for c in costs if c["timestamp"] >= since.isoformat()]

        total = sum(c["amount_usd"] for c in costs)
        by_category: Dict[str, float] = {}
        for c in costs:
            cat = c["category"]
            by_category[cat] = by_category.get(cat, 0) + c["amount_usd"]

        return {
            "total_usd": total,
            "by_category": by_category,
            "count": len(costs),
        }

    @endpoint(
        description="Set budget limit",
        endpoint_type=EndpointType.ACTION,
        parameters={
            "limit_usd": {"type": "float", "required": True},
        },
        returns={"success": "bool", "new_limit": "float"},
    )
    def set_budget_limit(self, limit_usd: float) -> Dict[str, Any]:
        """Set the budget limit."""
        self._budget_limit_usd = limit_usd
        return {"success": True, "new_limit": limit_usd}

    # Override to provide custom state
    def get_state(self) -> ServiceState:
        """Get current service state."""
        uptime = (datetime.now(timezone.utc) - self._start_time).total_seconds()
        total_cost = sum(c["amount_usd"] for c in self._costs)

        return ServiceState(
            status="on",
            health="healthy" if total_cost < self._budget_limit_usd else "degraded",
            uptime_seconds=uptime,
            last_action=self._costs[-1]["timestamp"] if self._costs else None,
            error_message=None,
            metrics={
                "total_cost_usd": total_cost,
                "budget_limit_usd": self._budget_limit_usd,
                "cost_entries": len(self._costs),
            },
        )
```

### Using the Registry

```python
from Primitive.governance.service_api import get_service_registry

# Get the singleton registry
registry = get_service_registry()

# List all services
services = registry.list_services()
# Returns: [{"name": "cost_service", "description": "...", "category": "service"}, ...]

# Get a specific service
cost_service = registry.get_service("cost_service")

# Call an endpoint
result = registry.call("cost_service", "get_summary")
# Returns: {"total_usd": 1.23, ...}

# Get complete API map for apps
api_map = registry.get_api_map()
# Returns: Complete discovery data for UI rendering
```

### App Integration (TypeScript)

```typescript
// Fetch the API map
const response = await fetch('/api/service-registry');
const apiMap = await response.json();

// Render service list
apiMap.services.forEach(service => {
  console.log(`${service.name}: ${service.description}`);

  // Show endpoints
  service.endpoints.forEach(endpoint => {
    console.log(`  - ${endpoint.name} (${endpoint.type})`);
  });

  // Show state
  console.log(`  Status: ${service.state.status}`);
});

// Call an endpoint
const result = await fetch('/api/call', {
  method: 'POST',
  body: JSON.stringify({
    service: 'cost_service',
    endpoint: 'get_summary',
    params: {}
  })
});
```

---

## Enforcement

### Validation Checks

| Check | What It Validates | Severity |
|-------|-------------------|----------|
| Inheritance | Service inherits from ServiceAPI | error |
| Manifest | Required fields present | error |
| Endpoints | All public methods decorated | warning |
| State | get_state() implemented | error |
| Registration | Service in registry | error |

### Validation Script

```python
from Primitive.governance.service_api import ServiceAPI, get_service_registry

def validate_service(service_class: type) -> List[str]:
    """Validate a service class for API compliance."""
    errors = []

    # Must inherit from ServiceAPI
    if not issubclass(service_class, ServiceAPI):
        errors.append("Must inherit from ServiceAPI")

    # Must have required attributes
    required = ["SERVICE_NAME", "SERVICE_DESCRIPTION", "SERVICE_VERSION"]
    for attr in required:
        if not hasattr(service_class, attr):
            errors.append(f"Missing required attribute: {attr}")

    # Must be in registry
    registry = get_service_registry()
    if service_class.SERVICE_NAME not in [s["name"] for s in registry.list_services()]:
        errors.append("Service not registered")

    return errors
```

---

## Related Standards

- [08_THE_API_LAYER.md](../../docs/business/the_framework/08_THE_API_LAYER.md) — Theory
- [API_DESIGN.md](API_DESIGN.md) — HTTP API design (external)
- [PRIMITIVE_PATTERN_SPECIFICATION.md](PRIMITIVE_PATTERN_SPECIFICATION.md) — THE PATTERN

---

## Implementation Location

| Component | Location |
|-----------|----------|
| ServiceAPI base class | `Primitive/governance/service_api/base.py` |
| Service Registry | `Primitive/governance/service_api/registry.py` |
| Package init | `Primitive/governance/service_api/__init__.py` |

---

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2026-01-19 | Initial standard | Claude |
