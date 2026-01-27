# Molt Architectural Recommendations

**Purpose:** Transform from amateur coder patterns to mature AI orchestrator architecture.

**Analysis Date:** January 20, 2026

**Principle:** Every pattern improvement must enable the next molt to be easier.

---

## Executive Summary

Analysis of the Truth Engine codebase reveals a mixed maturity level. Some patterns are professional (centralized constants with validation, audit trails), while others are amateur (scattered hardcodes, copy-paste boilerplate, silent failures). This document provides specific recommendations for the next molt.

### Maturity Assessment

| Area | Current State | Target State | Priority |
|------|---------------|--------------|----------|
| Configuration Management | ⭐ Scattered | ⭐⭐⭐⭐ Pydantic Settings | P0 |
| Service Construction | ⭐⭐ Boilerplate | ⭐⭐⭐⭐ Factory + Protocol | P0 |
| Authorization Registry | ⭐ Hardcoded Dict | ⭐⭐⭐⭐ YAML + Schema | P1 |
| Dependency Injection | ⭐ None | ⭐⭐⭐ Constructor Injection | P1 |
| Error Handling | ⭐⭐ Inconsistent | ⭐⭐⭐⭐ Result Types | P1 |
| Dead Code | ⭐ Present | ⭐⭐⭐⭐⭐ Eliminated | P0 |

---

## Part 1: Current State Analysis

### 1.1 Hardcoded Variables (CRITICAL)

**Problem:** The same values appear in 15+ locations.

| Value | Occurrences | Files |
|-------|-------------|-------|
| `flash-clover-464719-g1` | 15+ | daemon/*.py, pipelines/*/*.py, scripts/*.py |
| `/tmp/hold1.jsonl` | 3 | cost_service, version_service, search_service |
| AUTHORIZED_SCRIPTS dict | 1 (but should be config) | spark_manager.py |

**Current Pattern (Amateur):**
```python
# In pipelines/claude_code/scripts/assessment/run_assessment.py
PROJECT_ID = "flash-clover-464719-g1"
DATASET_ID = "spine"

# In pipelines/claude_code/scripts/assessment/assess_text_quality.py
PROJECT_ID = "flash-clover-464719-g1"  # DUPLICATED
DATASET_ID = "spine"                    # DUPLICATED
```

**Good Pattern Already Exists (Unused):**
```python
# In pipelines/claude_code/scripts/shared/constants.py
PROJECT_ID: str = os.environ.get("BIGQUERY_PROJECT_ID", "flash-clover-464719-g1")
DATASET_ID: str = os.environ.get("BIGQUERY_DATASET", "spine")

def _validate_config() -> None:
    """Validate configuration on import. Fail fast on misconfiguration."""
    if not PROJECT_ID:
        raise ValueError("PROJECT_ID not configured")
```

### 1.2 Service Construction (BOILERPLATE)

**Problem:** Every service has identical `__init__` boilerplate.

```python
# This pattern is COPY-PASTED in cost_service, version_service, search_service:
def __init__(self, base_path: Optional[Path] = None):
    if base_path is None:
        base_path = Path(__file__).parent.parent.parent / "system_elements" / "holds" / "{name}"

    intake_dir = base_path / "intake"
    processed_dir = base_path / "processed"
    intake_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    jsonl1_path = intake_dir / "hold1.jsonl"
    duckdb1_path = intake_dir / "hold1.duckdb"
    jsonl2_path = processed_dir / "hold2.jsonl"
    duckdb2_path = processed_dir / "hold2.duckdb"

    config = PrimitivePatternConfig(...)
    self._pattern = PrimitivePattern(config)
```

**Dead Code in Every Service:**
```python
# Lines 35-36 in EVERY service - NEVER USED
hold1_path = Path("/tmp/hold1.jsonl")
hold2_path = Path("/tmp/hold2.duckdb")
```

### 1.3 Error Handling (INCONSISTENT)

**Silent Failures (Bad):**
```python
# cost_service/service.py
def _agent_logic(self, record, context):
    if not record.get("service") or not record.get("operation"):
        logger.warning("Invalid cost record")
        return None  # Consuming code can't distinguish invalid from skip
```

**Explicit Failures (Good):**
```python
# spark_manager.py
except Exception as e:
    import sys
    print(f"⚠ CRITICAL: Failed to log authorization event: {e}", file=sys.stderr)
    print(f"  Event: {log_entry.to_dict()}", file=sys.stderr)
```

---

## Part 2: Industry Best Practices (2025-2026)

### 2.1 Configuration Management

**Recommendation:** [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) or [Dynaconf](https://github.com/dynaconf/dynaconf)

From [Best Practices for Python Configuration Management in 2025](https://toxigon.com/best-practices-for-python-configuration-management):

> pydantic-settings has emerged as one of the most elegant, type-safe, and production-ready solutions to manage configuration.

**Why Pydantic Settings:**
- Type-safe configuration with validation
- Environment variable support built-in
- `SecretStr` type for sensitive values
- Integrates with existing Pydantic models
- Layered settings (env → file → defaults)

### 2.2 Service Architecture

**Recommendation:** Protocol-based interfaces + Factory pattern

From [Modern Python Interfaces: ABC, Protocol, or Both?](https://tconsta.medium.com/python-interfaces-abc-protocol-or-both-3c5871ea6642):

> Protocols belong to the "structural" world — you are something if you look like it.

From [Python Registry Pattern](https://dev.to/dentedlogic/stop-writing-giant-if-else-chains-master-the-python-registry-pattern-ldm):

> The registry design pattern provides a way to organize modular functionalities dynamically and achieve a unified, reusable, and interchangeable interface.

### 2.3 Dependency Injection

**Recommendation:** Constructor injection (simple) or [Dependency Injector](https://python-dependency-injector.ets-labs.org/)

From [Python Dependency Injection Guide](https://www.datacamp.com/tutorial/python-dependency-injection):

> Dependency Injection involves injecting a class's dependencies rather than letting the class generate them on its own. This facilitates easy code management and testing and loose coupling.

### 2.4 AI Orchestration Patterns

**Recommendation:** Graph-based state machines (LangGraph pattern)

From [AI Agent Orchestration Frameworks 2025](https://www.getmaxim.ai/articles/top-5-ai-agent-frameworks-in-2025-a-practical-guide-for-ai-builders/):

> LangGraph builds on LangChain to provide a graph-based orchestration layer. It is designed to manage long-running, stateful agents with complex branching and workflow dependencies.

Key insight: Your HOLD → AGENT → HOLD pattern is already graph-based. The improvement is making it explicit with typed edges and state.

---

## Part 3: Specific Recommendations

### 3.1 Configuration System (P0)

**Create:** `Primitive/config/settings.py`

```python
"""
Centralized configuration using Pydantic Settings.

All configuration flows through here. No more scattered hardcodes.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class BigQuerySettings(BaseSettings):
    """BigQuery configuration."""

    model_config = SettingsConfigDict(
        env_prefix="BIGQUERY_",
        env_file=".env",
        extra="ignore",
    )

    project_id: str = Field(
        default="flash-clover-464719-g1",
        description="GCP project ID",
    )
    dataset: str = Field(
        default="spine",
        description="BigQuery dataset name",
    )
    location: str = Field(default="US")


class SparkSettings(BaseSettings):
    """Spark enforcement configuration."""

    model_config = SettingsConfigDict(
        env_prefix="PRIMITIVE_SPARK_",
        env_file=".env",
        extra="ignore",
    )

    mode: str = Field(
        default="permissive",
        description="Enforcement mode: disabled, permissive, enforcing",
    )
    disabled: bool = Field(default=False)
    registry_path: Path = Field(default=Path("data/spark_registry.json"))
    # Authorized scripts loaded from YAML, not hardcoded
    authorized_scripts_path: Path = Field(
        default=Path("config/authorized_scripts.yaml")
    )


class DaemonSettings(BaseSettings):
    """Daemon configuration."""

    model_config = SettingsConfigDict(
        env_prefix="DAEMON_",
        env_file=".env",
        extra="ignore",
    )

    port: int = Field(default=8000)
    host: str = Field(default="0.0.0.0")
    log_level: str = Field(default="INFO")


class OrganismSettings(BaseSettings):
    """Root settings for the organism."""

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    # Nested settings
    bigquery: BigQuerySettings = Field(default_factory=BigQuerySettings)
    spark: SparkSettings = Field(default_factory=SparkSettings)
    daemon: DaemonSettings = Field(default_factory=DaemonSettings)

    # Paths
    project_root: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent.parent
    )
    holds_root: Path = Field(default=Path("data/holds"))

    @property
    def full_table_id(self) -> str:
        """Convenience for BigQuery table IDs."""
        return f"{self.bigquery.project_id}.{self.bigquery.dataset}"


@lru_cache
def get_settings() -> OrganismSettings:
    """Get cached settings instance."""
    return OrganismSettings()


# Usage:
# from Primitive.config import get_settings
# settings = get_settings()
# print(settings.bigquery.project_id)
```

**Migration Path:**
1. Create `Primitive/config/settings.py`
2. Add `pydantic-settings` to requirements
3. Update services to use `get_settings()`
4. Remove hardcoded values one file at a time
5. Run tests after each migration

### 3.2 Authorized Scripts Registry (P1)

**Create:** `config/authorized_scripts.yaml`

```yaml
# Authorized Scripts Registry
#
# Scripts listed here are granted sparks.
# Schema validates on load. Add new scripts here, not in Python code.
#
# Format:
#   path: Purpose description

version: "1.0"
last_updated: "2026-01-20"

scripts:
  # Root-level entry points
  organism_cli.py:
    purpose: "Organism control CLI"
    added: "2026-01-15"

  # Daemon scripts
  daemon/truth_engine_daemon.py:
    purpose: "Main daemon server"
    added: "2026-01-01"

  daemon/autonomous_life_engine.py:
    purpose: "Organism lifecycle manager"
    added: "2026-01-10"

  daemon/care_emotion_system.py:
    purpose: "Relationship tracking"
    added: "2026-01-15"

  # Pipeline scripts (can be added programmatically)
  pipelines/claude_code/scripts/stage_1/stage_1.py:
    purpose: "Pipeline stage 1"
    added: "2026-01-20"

  # Add more scripts as needed...

# Exemptions (tools that skip spark checks)
exempt_patterns:
  - pip
  - pytest
  - python-build
  - setuptools
  - wheel
  - mypy
  - black
  - ruff
  - flake8
  - pylint
  - jupyter
  - ipython
```

**Schema Validation:** `config/schemas/authorized_scripts.schema.yaml`

```yaml
# Yamale schema for authorized_scripts.yaml
version: str()
last_updated: str()

scripts: map(include('script_entry'))
exempt_patterns: list(str())

---
script_entry:
  purpose: str()
  added: str()
  deprecated: str(required=False)
```

**Loader:**

```python
# Primitive/governance/spark_service/registry.py
from pathlib import Path
from typing import Dict, Set
import yaml

from Primitive.config import get_settings


def load_authorized_scripts() -> Dict[str, str]:
    """Load authorized scripts from YAML registry."""
    settings = get_settings()
    registry_path = settings.spark.authorized_scripts_path

    if not registry_path.exists():
        # Fallback for migration period
        from .spark_manager import AUTHORIZED_SCRIPTS
        return AUTHORIZED_SCRIPTS

    with open(registry_path) as f:
        data = yaml.safe_load(f)

    return {
        path: entry["purpose"]
        for path, entry in data.get("scripts", {}).items()
    }


def load_exempt_patterns() -> Set[str]:
    """Load exempt patterns from YAML registry."""
    settings = get_settings()
    registry_path = settings.spark.authorized_scripts_path

    if not registry_path.exists():
        return {"pip", "pytest", "setuptools", "wheel", "mypy", "black", "ruff"}

    with open(registry_path) as f:
        data = yaml.safe_load(f)

    return set(data.get("exempt_patterns", []))
```

### 3.3 Service Factory Pattern (P0)

**Create:** `Primitive/core/service_factory.py`

```python
"""
Service Factory - Eliminates boilerplate in service construction.

Instead of copy-pasting __init__ in every service, use this factory.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Any, Optional, Protocol, TypeVar

from Primitive.canonical.scripts.primitive_pattern import (
    PrimitivePattern,
    PrimitivePatternConfig,
)
from Primitive.config import get_settings
from Primitive.system_elements.service_registry.registry import register_service


class ServiceProtocol(Protocol):
    """Protocol that all services must satisfy."""

    def inhale(self, **kwargs) -> Any:
        """Receive input."""
        ...

    def exhale(self, **kwargs) -> Any:
        """Produce output."""
        ...

    def _agent_logic(self, record: Dict[str, Any], context: Any) -> Optional[Dict[str, Any]]:
        """Transform a single record."""
        ...


@dataclass
class ServiceConfig:
    """Configuration for creating a service."""
    name: str
    pattern_name: str
    dedupe_column: str
    description: str = ""
    version: str = "v1"

    # Optional overrides
    base_path: Optional[Path] = None
    intake_subdir: str = "intake"
    processed_subdir: str = "processed"


class ServiceFactory:
    """Factory for creating services with THE_PATTERN."""

    def __init__(self):
        self.settings = get_settings()

    def create_pattern(
        self,
        config: ServiceConfig,
        agent_func: Callable,
    ) -> PrimitivePattern:
        """Create a configured PrimitivePattern for a service."""

        # Determine base path
        if config.base_path:
            base_path = config.base_path
        else:
            base_path = (
                self.settings.project_root
                / "Primitive"
                / "system_elements"
                / "holds"
                / config.name
            )

        # Create directories
        intake_dir = base_path / config.intake_subdir
        processed_dir = base_path / config.processed_subdir
        intake_dir.mkdir(parents=True, exist_ok=True)
        processed_dir.mkdir(parents=True, exist_ok=True)

        # Build pattern config
        pattern_config = PrimitivePatternConfig(
            jsonl1_path=intake_dir / "hold1.jsonl",
            duckdb1_path=intake_dir / "hold1.duckdb",
            jsonl2_path=processed_dir / "hold2.jsonl",
            duckdb2_path=processed_dir / "hold2.duckdb",
            agent_func=agent_func,
            pattern_name=config.pattern_name,
            dedupe_column=config.dedupe_column,
        )

        return PrimitivePattern(pattern_config)

    def register(self, config: ServiceConfig) -> None:
        """Register service in the service registry."""
        service_id = f"{config.name}_{config.version}"
        register_service(
            service_id=service_id,
            service_name=config.name,
            version=config.version,
            description=config.description,
            pattern=config.pattern_name,
        )


# Convenience function
def create_service(
    name: str,
    agent_func: Callable,
    dedupe_column: str,
    description: str = "",
    **kwargs,
) -> PrimitivePattern:
    """Create a service pattern with minimal boilerplate."""
    factory = ServiceFactory()
    config = ServiceConfig(
        name=name,
        pattern_name=name,
        dedupe_column=dedupe_column,
        description=description,
        **kwargs,
    )
    factory.register(config)
    return factory.create_pattern(config, agent_func)
```

**New Service Pattern (After):**

```python
# Primitive/central_services/cost_service/service.py
"""Cost Service - Track and manage costs across the organism."""
from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any, Dict, Optional

from Primitive.core import get_logger
from Primitive.core.service_factory import create_service, ServiceProtocol

logger = get_logger(__name__)


class CostService:
    """Service for tracking costs."""

    def __init__(self, base_path=None):
        self._pattern = create_service(
            name="cost_service",
            agent_func=self._agent_logic,
            dedupe_column="cost_id",
            description="Track and aggregate costs across services",
            base_path=base_path,
        )

    def inhale(self, **kwargs):
        return self._pattern.inhale(**kwargs)

    def exhale(self, **kwargs):
        return self._pattern.exhale(**kwargs)

    def _agent_logic(self, record: Dict[str, Any], context) -> Optional[Dict[str, Any]]:
        # Only the unique logic - no boilerplate
        if not record.get("service") or not record.get("operation"):
            logger.warning("Invalid cost record", extra={"record": record})
            return None

        try:
            cost_usd = Decimal(str(record.get("cost_usd", "0.00")))
        except (InvalidOperation, ValueError):
            logger.warning("Invalid cost_usd", extra={"record": record})
            return None

        return {
            "cost_id": record.get("cost_id"),
            "service": record["service"],
            "operation": record["operation"],
            "cost_usd": str(cost_usd),
            # ... rest of transformation
        }
```

**Lines Saved Per Service:** ~30 lines (from ~80 to ~50)

### 3.4 Result Type for Error Handling (P1)

**Create:** `Primitive/core/result.py`

```python
"""
Result type for explicit error handling.

Replaces silent `return None` with explicit success/failure distinction.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar, Union, Optional

T = TypeVar("T")
E = TypeVar("E", bound=Exception)


@dataclass
class Ok(Generic[T]):
    """Successful result."""
    value: T

    def is_ok(self) -> bool:
        return True

    def is_err(self) -> bool:
        return False

    def unwrap(self) -> T:
        return self.value

    def unwrap_or(self, default: T) -> T:
        return self.value


@dataclass
class Err(Generic[E]):
    """Error result."""
    error: E
    message: str = ""

    def is_ok(self) -> bool:
        return False

    def is_err(self) -> bool:
        return True

    def unwrap(self) -> None:
        raise self.error

    def unwrap_or(self, default):
        return default


Result = Union[Ok[T], Err[E]]


# Skip is different from Error
@dataclass
class Skip:
    """Intentional skip (not an error)."""
    reason: str


AgentResult = Union[Ok[dict], Err[Exception], Skip]


# Usage:
def _agent_logic(self, record, context) -> AgentResult:
    if not record.get("service"):
        return Skip(reason="Missing service field")  # Intentional skip

    try:
        cost = Decimal(record["cost_usd"])
    except InvalidOperation as e:
        return Err(e, message="Invalid cost_usd")  # Error

    return Ok({"processed": True, "cost": str(cost)})  # Success
```

### 3.5 Dead Code Removal (P0)

**Remove from ALL services:**

```python
# DELETE these lines from cost_service, version_service, search_service:
hold1_path = Path("/tmp/hold1.jsonl")
hold2_path = Path("/tmp/hold2.duckdb")
```

**Files to clean:**
- `Primitive/central_services/cost_service/service.py` (lines 35-36)
- `Primitive/central_services/version_service/service.py` (lines 35-36)
- `Primitive/central_services/search_service/service.py` (lines 35-36)

---

## Part 4: Implementation Priority

### Phase 1: Foundation (This Molt)

| Task | Impact | Effort | Status |
|------|--------|--------|--------|
| Remove dead `/tmp` code | High | Low | TODO |
| Create `Primitive/config/settings.py` | High | Medium | TODO |
| Create `authorized_scripts.yaml` | Medium | Low | TODO |
| Add `pydantic-settings` dependency | Medium | Low | TODO |

### Phase 2: Service Refactoring (Next Sprint)

| Task | Impact | Effort | Status |
|------|--------|--------|--------|
| Create `ServiceFactory` | High | Medium | TODO |
| Refactor `cost_service` | Medium | Low | TODO |
| Refactor `version_service` | Medium | Low | TODO |
| Refactor `search_service` | Medium | Low | TODO |
| Create `Result` type | Medium | Low | TODO |

### Phase 3: Enforcement (After Services)

| Task | Impact | Effort | Status |
|------|--------|--------|--------|
| Migrate all hardcodes to settings | High | High | TODO |
| Add pre-commit hook for hardcode detection | Medium | Low | TODO |
| Switch spark_manager to YAML registry | Medium | Medium | TODO |

---

## Part 5: Preemptive Surfaces Created

| Surface | What It Enables |
|---------|-----------------|
| `Primitive/config/settings.py` | Any new config is one addition, not scattered edits |
| `config/authorized_scripts.yaml` | Adding scripts without code changes |
| `ServiceFactory` | New services are 50 lines instead of 80 |
| `Result` type | Explicit error handling across all services |
| Schema validation | Catch config errors at load time, not runtime |

---

## Part 6: What NOT to Change

Some "amateur" patterns are actually appropriate:

1. **`Path(__file__).parent.parent.parent`** - This is actually fine. The Service Factory abstracts it away.

2. **`try/except` import fallbacks** - Keep these during migration:
   ```python
   try:
       from Primitive.core import get_logger
   except Exception:
       from src.services.central_services.core import get_logger
   ```

3. **THE_PATTERN (HOLD → AGENT → HOLD)** - This is already a mature pattern. Don't replace it with LangGraph - enhance it with typed state.

4. **Service registration** - The current `register_service()` pattern is fine. Just centralize it in the factory.

---

## Sources

### Configuration Management
- [Pydantic Settings Documentation](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [Dynaconf GitHub](https://github.com/dynaconf/dynaconf)
- [Python Configuration Best Practices 2025](https://toxigon.com/best-practices-for-python-configuration-management)

### Service Architecture
- [Python Registry Pattern](https://dev.to/dentedlogic/stop-writing-giant-if-else-chains-master-the-python-registry-pattern-ldm)
- [Registry-Factory PyPI](https://pypi.org/project/registry-factory/)
- [Factory Method Pattern (Real Python)](https://realpython.com/factory-method-python/)

### Protocol/Interface Patterns
- [Modern Python Interfaces: ABC, Protocol, or Both?](https://tconsta.medium.com/python-interfaces-abc-protocol-or-both-3c5871ea6642)
- [Python Protocol (Real Python)](https://realpython.com/python-protocol/)
- [PEP 544 - Protocols](https://peps.python.org/pep-0544/)

### Dependency Injection
- [Dependency Injector Documentation](https://python-dependency-injector.ets-labs.org/)
- [Python Dependency Injection Guide (DataCamp)](https://www.datacamp.com/tutorial/python-dependency-injection)

### AI Orchestration
- [AI Agent Frameworks 2025](https://www.getmaxim.ai/articles/top-5-ai-agent-frameworks-in-2025-a-practical-guide-for-ai-builders/)
- [LangGraph vs AutoGen vs CrewAI](https://www.datacamp.com/tutorial/crewai-vs-langgraph-vs-autogen)

---

*Document created: January 20, 2026*
*For: Next molt transformation*
*Principle: Shake off amateur patterns, embrace mature AI orchestrator architecture*
