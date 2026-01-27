# Risk Analysis & Mitigation Plan

**Created**: 2026-01-26
**Status**: CRITICAL - Must address before migration
**Total Risks Identified**: 28
**Critical Risks**: 8
**High Risks**: 11
**Medium Risks**: 9

---

## Executive Summary

Analysis of Truth_Engine revealed **critical blockers** that will cause migration failure if not addressed:

| Category | Critical | High | Medium | Total |
|----------|----------|------|--------|-------|
| Code Dependencies | 2 | 4 | 2 | 8 |
| Hardcoded Paths | 2 | 3 | 1 | 6 |
| Data Integrity | 2 | 2 | 2 | 6 |
| Configuration | 1 | 1 | 2 | 4 |
| Architecture | 1 | 1 | 2 | 4 |
| **TOTAL** | **8** | **11** | **9** | **28** |

---

## CRITICAL RISKS (Must Fix Before Migration)

### RISK-001: Corrupted DuckDB Files
**Severity**: CRITICAL
**Impact**: 8 services cannot be migrated
**Category**: Data Integrity

**Problem**: 8 DuckDB files are stored as directories instead of files:
- `governance_service/hold2/governance.duckdb/`
- `identity_service/hold2/identity.duckdb/`
- `logging_service/hold2/logs.duckdb/`
- `pattern_monitor/hold2/pattern_analysis.duckdb/`
- `pattern_monitor/hold2/pattern_scan.duckdb/`
- `primitives_service/hold2/primitives.duckdb/`
- `testing_service/hold2/pattern_analysis_test.duckdb/`
- `truth_service/hold2/truth.duckdb/`

**Mitigation**:
```bash
# Phase 0 - Pre-Migration Check
for db in governance identity logging pattern_monitor primitives testing truth; do
    path="Truth_Engine/data/services/${db}_service/hold2/"
    if [ -d "${path}*.duckdb" ]; then
        echo "CRITICAL: ${db} has corrupted DuckDB (directory)"
        # Check if it's a broken symlink
        ls -la "${path}"
        # Attempt recovery from archive
    fi
done
```

**Recovery Options**:
1. Check if these are broken symlinks → fix symlinks
2. Restore from `data/archive/migrated_originals_20260121/`
3. Rebuild from hold1/ JSONL files via sync()

---

### RISK-002: Hardcoded User Paths
**Severity**: CRITICAL
**Impact**: Code will fail on any machine except Jeremy's
**Category**: Hardcoded Paths

**Problem**: 13+ locations hardcode `/Users/jeremyserna/`:
- `universal_resonance_service.py:17-18`
- `care_service.py:23`
- `resident_watch_service.py:9,93`
- `resident_service/service.py:337`
- `reality_extractor_service/service.py:234,239`
- `universal_data_watcher.py:10`
- `verification_service/service.py:62`

**Mitigation**:
```python
# Create src/truth_forge/core/paths.py
from pathlib import Path
import os

def get_project_root() -> Path:
    """Get project root, works on any machine."""
    # Try environment variable first
    if root := os.getenv("TRUTH_FORGE_ROOT"):
        return Path(root)

    # Find root by looking for pyproject.toml
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "pyproject.toml").exists():
            return parent

    raise RuntimeError("Cannot determine project root")

PROJECT_ROOT = get_project_root()
DATA_ROOT = PROJECT_ROOT / "data"
SERVICES_ROOT = DATA_ROOT / "services"
```

**Search & Replace Pattern**:
```bash
# Find all occurrences
grep -r "/Users/jeremyserna" Truth_Engine/src/ --include="*.py" -l

# Replace with PROJECT_ROOT
# from /Users/jeremyserna/Truth_Engine → PROJECT_ROOT
# from /Users/jeremyserna/credential_atlas → CREDENTIAL_ATLAS_ROOT
```

---

### RISK-003: Circular Dependency URS ↔ CareService
**Severity**: CRITICAL
**Impact**: Runtime import errors
**Category**: Code Dependencies

**Problem**: Universal Resonance Service imports CareService at module level, creating fragile import chain.

**Location**: `universal_resonance_service.py:14,29`

**Mitigation**:
```python
# Option A: Lazy import (quick fix)
class UniversalResonanceService:
    def __init__(self):
        self._care_service = None

    @property
    def care_service(self):
        if self._care_service is None:
            from truth_forge.services.care import CareService
            self._care_service = CareService()
        return self._care_service

# Option B: Dependency injection (proper fix)
class UniversalResonanceService:
    def __init__(self, care_service: "CareService | None" = None):
        self._care_service = care_service

    @property
    def care_service(self):
        if self._care_service is None:
            from truth_forge.services.care import get_care_service
            self._care_service = get_care_service()
        return self._care_service
```

---

### RISK-004: Non-Compliant Service Schemas
**Severity**: CRITICAL
**Impact**: 24 services have wrong schema, blocking standardized processing
**Category**: Data Integrity

**Problem**: Services use initialization schema instead of DATA_PATTERN schema.

**Current** (wrong):
```json
{"event_type": "hold1_initialized", "service": "...", "timestamp": "..."}
```

**Required** (per DATA_PATTERN.md):
```json
{"id": "uuid", "data": {...}, "created_at": "ISO-8601", "run_id": "..."}
```

**Mitigation**:
```python
# Add schema validation to service base class
from truth_forge.schema import Event, EventType, create_event

class BaseService:
    def inhale(self, data: dict) -> str:
        """Write to HOLD₁ with validated schema."""
        event = create_event(
            event_type=EventType.RECORD_CREATED,
            aggregate_type=self.name,
            data=data,
            service=self.name,
        )

        with open(self.hold1_path, "a") as f:
            f.write(event.to_jsonl() + "\n")

        return event.id
```

---

### RISK-005: /tmp/ Paths for HOLD Files
**Severity**: CRITICAL
**Impact**: Data loss on system reboot
**Category**: Hardcoded Paths

**Problem**: Core modules use `/tmp/` for HOLD files:
- `core/holds.py:26-27` → `/tmp/hold1.jsonl`, `/tmp/hold2.duckdb`
- `core/responses.py:46-47` → same
- `core/error_handling.py:24-25` → same
- `core/ml.py:26-27` → same
- `document_service/__init__.py:72-73` → `/tmp/documents/`

**Mitigation**:
```python
# Replace all /tmp/ references with proper paths
# Before:
HOLD1_PATH = Path("/tmp/hold1.jsonl")

# After:
from truth_forge.core.paths import SERVICES_ROOT

def get_hold1_path(service_name: str) -> Path:
    return SERVICES_ROOT / service_name / "hold1" / f"{service_name}_intake.jsonl"
```

---

### RISK-006: Missing HOLD₂ Data
**Severity**: CRITICAL
**Impact**: 14 services have no queryable data
**Category**: Data Integrity

**Problem**: These services have hold1/ data but empty hold2/:
- analytics_service, builder_service, care_service, cost_service
- document_service, federation_service, hold_service, quality_service
- relationship_service, run_service, search_service, spark_service
- version_service, workflow_service

**Mitigation**:
```python
# Add sync verification to quality gates
def verify_hold_sync(service_name: str) -> bool:
    """Verify HOLD₁ → HOLD₂ sync is working."""
    hold1 = SERVICES_ROOT / service_name / "hold1"
    hold2 = SERVICES_ROOT / service_name / "hold2"

    hold1_count = sum(1 for _ in open(hold1 / f"{service_name}_intake.jsonl"))

    # Check if hold2 DuckDB exists and has data
    db_path = hold2 / f"{service_name}.duckdb"
    if not db_path.exists():
        return False

    import duckdb
    conn = duckdb.connect(str(db_path))
    hold2_count = conn.execute(f"SELECT COUNT(*) FROM {service_name}_records").fetchone()[0]

    # Allow some lag, but most data should be synced
    return hold2_count >= hold1_count * 0.9
```

---

### RISK-007: No Rollback Strategy
**Severity**: CRITICAL
**Impact**: Cannot recover from failed migration
**Category**: Architecture

**Problem**: No backup or rollback mechanism defined.

**Mitigation**:
```bash
# Pre-Migration Backup Script (add to Phase 0)
#!/bin/bash
BACKUP_DIR="backups/pre_migration_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup critical data
cp -r Truth_Engine/data/services/ "$BACKUP_DIR/services/"
cp -r Truth_Engine/.truth_engine/ "$BACKUP_DIR/truth_engine_hidden/"
cp -r Truth_Engine/data/archive/ "$BACKUP_DIR/archive/"

# Backup source code state
git stash
git branch -c main pre_migration_backup
git stash pop

echo "Backup complete: $BACKUP_DIR"
echo "Git branch: pre_migration_backup"
```

```python
# Rollback function for each phase
def rollback_phase(phase: int, backup_dir: Path) -> None:
    """Rollback a failed phase."""
    logger.warning(f"Rolling back phase {phase}")

    # Restore from backup
    shutil.rmtree(SERVICES_ROOT)
    shutil.copytree(backup_dir / "services", SERVICES_ROOT)

    # Reset git
    subprocess.run(["git", "checkout", "pre_migration_backup"])
```

---

### RISK-008: Thread-Unsafe Singletons
**Severity**: CRITICAL
**Impact**: Race conditions in production
**Category**: Code Dependencies

**Problem**: Multiple services use non-thread-safe singleton pattern:
```python
_service_instance = None

def get_service():
    global _service_instance
    if _service_instance is None:  # Race condition here
        _service_instance = Service()
    return _service_instance
```

**Affected Services**: WisdomDirectionService, DuckDBFlushService, BigQueryArchiveService, CircuitBreaker

**Mitigation**:
```python
import threading
from functools import lru_cache

# Option A: Thread-safe singleton with lock
_service_lock = threading.Lock()
_service_instance = None

def get_service():
    global _service_instance
    if _service_instance is None:
        with _service_lock:
            if _service_instance is None:  # Double-check
                _service_instance = Service()
    return _service_instance

# Option B: Use lru_cache (simpler, GIL-protected)
@lru_cache(maxsize=1)
def get_service() -> Service:
    return Service()
```

---

## HIGH RISKS

### RISK-009: 48 Scattered Environment Variables
**Severity**: HIGH
**Impact**: Inconsistent configuration, hard to manage
**Category**: Configuration

**Problem**: 48 unique environment variables with no central schema.

**Mitigation**: Create centralized config with Pydantic.

```python
# src/truth_forge/config/settings.py
from pydantic_settings import BaseSettings

class TruthForgeSettings(BaseSettings):
    """Centralized configuration with validation."""

    # GCP
    gcp_project: str = "flash-clover-464719-g1"
    bigquery_location: str = "US"

    # API Keys
    google_api_key: str | None = None
    anthropic_api_key: str | None = None
    gemini_api_key: str | None = None

    # Limits
    gemini_max_calls_per_session: int = 1000
    gemini_max_cost_per_session: float = 10.0
    bigquery_max_rows: int = 1_000_000

    # Paths
    truth_forge_root: str | None = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = TruthForgeSettings()
```

---

### RISK-010: Mixed Import Styles
**Severity**: HIGH
**Impact**: Inconsistent behavior, hard to maintain
**Category**: Code Dependencies

**Problem**: Same functionality imported differently:
- `from truth_forge.logger import get_logger`
- `from src.services.central_services.core.get_logger import get_logger`

**Mitigation**: Standardize all imports to `truth_forge.*` pattern.

```bash
# Find all old import patterns
grep -r "from src\." Truth_Engine/src/ --include="*.py" -l | wc -l
grep -r "from Primitive\." Truth_Engine/src/ --include="*.py" -l | wc -l
grep -r "from central_services\." Truth_Engine/src/ --include="*.py" -l | wc -l

# Create import map for migration
```

---

### RISK-011: Data in Deprecated .truth_engine/
**Severity**: HIGH
**Impact**: Critical data not in standard location
**Category**: Data Integrity

**Problem**: 87.5 MB of data still in deprecated hidden directory:
- `atom1.duckdb` (47.9 MB)
- `atom1.jsonl` (37.8 MB)
- `atoms.duckdb` (1.8 MB)
- `atoms_cloud.duckdb` (1.8 MB)

**Mitigation**:
```bash
# Migrate .truth_engine data to standard location
mkdir -p data/services/primitives_service/hold1
mkdir -p data/services/primitives_service/hold2

mv .truth_engine/primitive/atom1.jsonl data/services/primitives_service/hold1/primitives_intake.jsonl
mv .truth_engine/primitive/atom1.duckdb data/services/primitives_service/hold2/primitives.duckdb
```

---

### RISK-012: Delayed Imports Mask Dependencies
**Severity**: HIGH
**Impact**: Hidden circular dependencies
**Category**: Code Dependencies

**Problem**: Some services import inside methods to avoid circular imports:
- `organism_evolution_service/service.py:331,730`

**Mitigation**: Make dependencies explicit via dependency injection.

---

### RISK-013: Hardcoded GCP Project ID
**Severity**: HIGH
**Impact**: Wrong billing, wrong data location
**Category**: Configuration

**Problem**: `"flash-clover-464719-g1"` hardcoded in 6+ locations as fallback.

**Mitigation**: Remove all hardcoded defaults, require explicit configuration.

---

### RISK-014: No Validation Checkpoints
**Severity**: HIGH
**Impact**: May proceed with broken state
**Category**: Architecture

**Problem**: No intermediate validation between phases.

**Mitigation**: Add checkpoint validation after each phase.

```python
# src/truth_forge/migration/checkpoints.py
def validate_checkpoint(phase: int) -> dict:
    """Validate state after completing a phase."""
    checks = {
        0: validate_foundation,
        1: validate_core,
        2: validate_infrastructure,
        # ... etc
    }

    validator = checks.get(phase)
    if validator:
        return validator()
    return {"status": "ok"}

def validate_foundation() -> dict:
    """Phase 0 validation."""
    issues = []

    # Check directories exist
    required_dirs = [
        "src/truth_forge",
        "data/services",
        "framework/standards",
    ]
    for d in required_dirs:
        if not Path(d).exists():
            issues.append(f"Missing directory: {d}")

    # Check pyproject.toml valid
    try:
        import tomllib
        tomllib.load(open("pyproject.toml", "rb"))
    except Exception as e:
        issues.append(f"Invalid pyproject.toml: {e}")

    return {"status": "fail" if issues else "ok", "issues": issues}
```

---

### RISK-015: Import Path Reference to Non-Existent Directory
**Severity**: HIGH
**Impact**: Worker will fail immediately
**Category**: Code Dependencies

**Problem**: `atom_embedder/worker.py` references `/architect_central/` which doesn't exist.

**Mitigation**: Fix import path or remove dead code.

---

### RISK-016: Private Function Import
**Severity**: HIGH
**Impact**: Fragile dependency on internal API
**Category**: Code Dependencies

**Problem**: `knowledge_service.py:54-59` imports `_embed` (private function).

**Mitigation**: Make `_embed` public or create proper API.

---

### RISK-017: LRU Cache Singletons
**Severity**: HIGH
**Impact**: Cannot clear/reset for testing
**Category**: Code Dependencies

**Problem**: 11+ services use `@lru_cache(maxsize=1)` for singletons.

**Mitigation**: Add cache clearing for tests.

```python
def get_service():
    ...

# For testing
def clear_service_cache():
    get_service.cache_clear()
```

---

### RISK-018: No Service Health Verification
**Severity**: HIGH
**Impact**: Services marked complete but not functional
**Category**: Architecture

**Mitigation**: Add health check to each service.

```python
class BaseService:
    def health_check(self) -> dict:
        """Verify service is operational."""
        return {
            "service": self.name,
            "hold1_exists": self.hold1.exists(),
            "hold2_exists": self.hold2.exists(),
            "can_inhale": self._test_inhale(),
            "can_exhale": self._test_exhale(),
        }
```

---

### RISK-019: Environment Variable Mutation
**Severity**: HIGH
**Impact**: Unpredictable behavior
**Category**: Configuration

**Problem**: Services mutate `os.environ` at runtime:
- `duckdb_flush_service/service.py:57-58`
- `bigquery_archive_service/service.py:74-75`

**Mitigation**: Never mutate environment. Use explicit config.

---

## MEDIUM RISKS

### RISK-020: 116 Uses of Path.home()
**Severity**: MEDIUM
**Impact**: Assumes user home structure
**Category**: Hardcoded Paths

**Mitigation**: Replace with PROJECT_ROOT detection.

---

### RISK-021: Empty Initialized Directories
**Severity**: MEDIUM
**Impact**: Clutter, confusion
**Category**: Data Integrity

**Problem**: 9 empty directories created but never used.

**Mitigation**: Remove or populate during migration.

---

### RISK-022: Orphaned Data Files
**Severity**: MEDIUM
**Impact**: Data not accessible via services
**Category**: Data Integrity

**Problem**: CSV files and browser data outside HOLD pattern.

**Mitigation**: Create import pipelines or archive.

---

### RISK-023: Browser History in Staging
**Severity**: MEDIUM
**Impact**: 37 JSONL files need integration
**Category**: Data Integrity

**Mitigation**: Create browser_history_service or archive.

---

### RISK-024: No Dependency Graph Validation
**Severity**: MEDIUM
**Impact**: May migrate in wrong order
**Category**: Architecture

**Mitigation**: Generate and validate dependency graph.

```python
# Generate import graph
import ast
from pathlib import Path

def get_imports(file_path: Path) -> set[str]:
    """Extract imports from Python file."""
    with open(file_path) as f:
        tree = ast.parse(f.read())

    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module)

    return imports
```

---

### RISK-025: Module Federation Version Mismatch
**Severity**: MEDIUM
**Impact**: Web apps may fail to load shared components
**Category**: Architecture

**Mitigation**: Lock shared dependency versions.

```json
// package.json - shared versions
{
  "resolutions": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  }
}
```

---

### RISK-026: primitive-slot-builder Merge May Break
**Severity**: MEDIUM
**Impact**: Chat functionality degraded
**Category**: Architecture

**Mitigation**: Test merge in isolation before full migration.

---

### RISK-027: Test Coverage May Not Transfer
**Severity**: MEDIUM
**Impact**: Tests pass but functionality broken
**Category**: Architecture

**Mitigation**: Run integration tests after migration, not just unit tests.

---

### RISK-028: MCP Server Compatibility
**Severity**: MEDIUM
**Impact**: Claude integration may break
**Category**: Code Dependencies

**Mitigation**: Test MCP server after migration.

---

## Mitigation Summary by Phase

### Phase 0 (Pre-Migration)

**MUST DO:**
1. Create full backup (RISK-007)
2. Fix corrupted DuckDB files (RISK-001)
3. Create paths.py abstraction (RISK-002)
4. Create centralized settings.py (RISK-009)
5. Validate all 8 critical risks have mitigation code ready

### Phase 1-4 (Core + Services)

**MUST DO:**
1. Fix all hardcoded paths before copying (RISK-002, RISK-005)
2. Fix circular dependencies (RISK-003)
3. Add schema validation (RISK-004)
4. Fix thread-unsafe singletons (RISK-008)
5. Run checkpoint validation after each phase (RISK-014)

### Phase 5-9 (Modules + Pipelines)

**MUST DO:**
1. Standardize all imports (RISK-010)
2. Migrate .truth_engine data (RISK-011)
3. Add service health checks (RISK-018)

### Phase 10-11 (Apps + MCP)

**MUST DO:**
1. Test Module Federation locally (RISK-025)
2. Test primitive-slot-builder merge (RISK-026)
3. Test MCP server (RISK-028)

### Phase 12-15 (Tests + Validation)

**MUST DO:**
1. Integration tests, not just unit tests (RISK-027)
2. Full health check all services (RISK-018)
3. Verify HOLD sync working (RISK-006)

---

## Rollback Triggers

Abort and rollback if ANY of these occur:

| Trigger | Action |
|---------|--------|
| >10% of imports fail | Rollback to pre_migration_backup |
| Any DuckDB corruption detected | Rollback, investigate |
| Service health check fails | Rollback that phase |
| Test coverage drops >5% | Investigate before proceeding |
| Cost exceeds $10 | Pause, review |

---

## Risk Checklist

Before starting each phase, verify:

- [ ] Backup completed and verified
- [ ] Rollback script tested
- [ ] Checkpoint validation ready
- [ ] Known risks for this phase mitigated
- [ ] Health checks ready

---

*Risk analysis v1.0 - No migration proceeds until all CRITICAL risks have mitigations implemented.*

— Risk Analysis, 2026-01-26
