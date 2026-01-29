# Architecture Compliance Fixes - Industry Standards

**Date**: 2026-01-27  
**Status**: FIXES REQUIRED  
**Reviewers**: Auto (Claude Sonnet 4.5), Gemini, Claude Code

---

## THREE-LLM REVIEW REQUIREMENT

**All fixes will be reviewed by THREE LLMs:**
1. **Auto** (Claude Sonnet 4.5) - Primary fixer ✅
2. **Gemini** - Secondary reviewer ⏳
3. **Claude Code** - Final reviewer ⏳

**Standard**: All fixes must meet industry standards. All errors must be surfaced. All anti-patterns must be eliminated.

---

## CRITICAL FIXES REQUIRED

### Fix #1: Stage 3 Identity Service Integration (CRITICAL)

**Current (WRONG)**:
```python
# ❌ ANTI-PATTERN - Manual hashlib fallback
import hashlib
def generate_message_id_from_guid(session_id, message_index, fingerprint):
    content = f"{session_id}:{message_index}:{fingerprint}"
    return f"msg:{hashlib.sha256(content.encode()).hexdigest()[:16]}"

def register_id(entity_id, entity_type, context_data, first_requestor):
    pass  # No-op

def sync_to_bigquery(client):
    pass  # No-op
```

**Required Fix**:
```python
# ✅ CORRECT - Real IdentityService
from truth_forge.services.identity import IdentityService

# Initialize service
identity_service = IdentityService()

def generate_entity_id(session_id: str, message_index: int, fingerprint: str) -> str:
    """Generate entity_id using canonical IdentityService."""
    # First, generate conversation_id from session_id
    conversation_id = identity_service.generate_conversation_id(
        source_type=SOURCE_NAME,
        source_id=session_id
    )
    
    # Generate message_id using canonical service
    entity_id = identity_service.generate_message_id(
        conversation_id=conversation_id,
        index=message_index
    )
    
    # TODO: Register ID in identity.id_registry (separate operation)
    # Registration happens via backfill script or separate registration step
    
    return entity_id
```

**Impact**: 
- ✅ Uses canonical ID format
- ✅ Consistent with other pipelines
- ✅ Enables cross-pipeline deduplication
- ⚠️ Note: ID registration to `identity.id_registry` is separate (backfill script)

**Status**: ⚠️ **REQUIRES FIX**

---

### Fix #2: BigQuery Client Integration (CRITICAL - All Stages)

**Current (WRONG)**:
```python
# ❌ ANTI-PATTERN - Direct client, no protection
def get_bigquery_client():
    """Get BigQuery client (fallback implementation)."""
    return bigquery.Client()  # Bypasses cost protection
```

**Required Fix**:
```python
# ✅ CORRECT - Central services with cost protection
def get_bigquery_client() -> bigquery.Client:
    """Get BigQuery client with cost protection and retry logic."""
    try:
        # Try truth_forge.core first
        from truth_forge.core.bigquery_client import get_bigquery_client as get_bq
        client = get_bq()
        logger.info("Using truth_forge.core BigQuery client (with cost protection)")
        return client.client if hasattr(client, "client") else client
    except ImportError:
        try:
            # Fallback to central_services
            from src.services.central_services.core.config import get_bigquery_client as get_bq
            client = get_bq()
            logger.info("Using central_services BigQuery client (with cost protection)")
            return client.client if hasattr(client, "client") else client
        except ImportError:
            # Final fallback with WARNING
            logger.warning(
                "⚠️  WARNING: Central services not available. Using direct client (NO COST PROTECTION)."
            )
            logger.warning("   Install central services for cost protection and retry logic.")
            print("⚠️  WARNING: Using direct BigQuery client - NO COST PROTECTION")
            print("   Install central services for cost protection and retry logic.")
            return bigquery.Client()
```

**Impact**:
- ✅ Cost protection enabled when available
- ✅ Retry logic enabled when available
- ✅ User warned if fallback used
- ✅ Errors surfaced to user

**Status**: ⚠️ **REQUIRES FIX** (All stages)

---

### Fix #3: PipelineTracker Integration (HIGH - All Stages)

**Current (WRONG)**:
```python
# ❌ ANTI-PATTERN - No-op fallback
@contextmanager
def PipelineTracker(*args, **kwargs):
    """PipelineTracker fallback (simple context manager)."""
    obj = type("obj", (object,), {"update_progress": lambda self, **kw: None})()
    yield obj  # No tracking
```

**Required Fix**:
```python
# ✅ CORRECT - Real PipelineTracker with fallback warning
from contextlib import contextmanager
from typing import Any, Generator

@contextmanager
def PipelineTracker(*args: Any, **kwargs: Any) -> Generator[Any, None, None]:
    """PipelineTracker with real tracking when available."""
    try:
        from src.services.central_services.core.pipeline_tracker import PipelineTracker as RealTracker
        logger.info("Using real PipelineTracker (with progress tracking)")
        with RealTracker(*args, **kwargs) as tracker:
            yield tracker
    except ImportError:
        logger.warning("⚠️  WARNING: PipelineTracker not available. Using no-op fallback.")
        logger.warning("   Install central services for progress tracking.")
        print("⚠️  WARNING: Progress tracking not available")
        obj = type("obj", (object,), {"update_progress": lambda self, **kw: None})()
        yield obj
```

**Impact**:
- ✅ Real tracking when available
- ✅ User warned if fallback used
- ✅ Errors surfaced

**Status**: ⚠️ **REQUIRES FIX** (All stages)

---

### Fix #4: Error Diagnostics Integration (HIGH - All Stages)

**Current (WRONG)**:
```python
# ❌ ANTI-PATTERN - No-op fallback
def require_diagnostic_on_error(error, context):
    """require_diagnostic_on_error fallback (no-op)."""
    pass  # Errors hidden
```

**Required Fix**:
```python
# ✅ CORRECT - Real diagnostics with fallback warning
def require_diagnostic_on_error(error: Exception, context: str) -> None:
    """Require diagnostic on error with real diagnostics when available."""
    try:
        from src.services.central_services.governance.governance import require_diagnostic_on_error as real_diag
        logger.info(f"Using real error diagnostics for: {context}")
        real_diag(error, context)
    except ImportError:
        logger.warning(f"⚠️  WARNING: Error diagnostics not available for: {context}")
        logger.warning("   Install central services for error diagnostics.")
        # Still log error even without diagnostics
        logger.error(
            f"Error in {context}",
            extra={"error": str(error), "context": context},
            exc_info=True
        )
        print(f"⚠️  WARNING: Error diagnostics not available for: {context}")
        print(f"   Error: {str(error)}")
```

**Impact**:
- ✅ Real diagnostics when available
- ✅ User warned if fallback used
- ✅ Errors still logged even without diagnostics

**Status**: ⚠️ **REQUIRES FIX** (All stages)

---

### Fix #5: Error Surfacing (CRITICAL - All Stages)

**Current (WRONG)**:
```python
# ❌ ANTI-PATTERN - Error only logged
try:
    merge_rows_to_table(...)
except Exception as e:
    logger.warning("Unable to merge records, using direct insert instead")
    logger.debug(f"MERGE failed: {e}", exc_info=True)  # Only in debug
    errors = client.insert_rows_json(...)  # User never knows
```

**Required Fix**:
```python
# ✅ CORRECT - Error surfaced to user
try:
    merge_rows_to_table(...)
except Exception as e:
    # Log for debugging
    logger.warning("Unable to merge records, using direct insert instead")
    logger.debug(f"MERGE failed: {e}", exc_info=True)
    
    # SURFACE ERROR TO USER
    print(f"⚠️  WARNING: MERGE operation failed, using direct insert")
    print(f"   Error: {str(e)}")
    print(f"   This may cause duplicates. Check logs for details.")
    
    # Diagnose error
    require_diagnostic_on_error(e, "merge_rows_to_table")
    
    # Try fallback
    try:
        errors = client.insert_rows_json(...)
        if errors:
            # SURFACE INSERT ERRORS TO USER
            print(f"❌ ERROR: Direct insert also failed")
            print(f"   Errors: {errors[:5]}")
            logger.error(f"Insert errors: {errors[:5]}")
            raise ValueError(f"Failed to insert records: {errors[:5]}")
    except Exception as insert_error:
        print(f"❌ ERROR: Direct insert failed: {str(insert_error)}")
        require_diagnostic_on_error(insert_error, "direct_insert_fallback")
        raise
```

**Impact**:
- ✅ User sees all errors
- ✅ User knows about degradation
- ✅ User can take action

**Status**: ⚠️ **REQUIRES FIX** (All stages)

---

### Fix #6: Silent Error Suppression (CRITICAL)

**Current (WRONG)**:
```python
# ❌ ANTI-PATTERN - Silent suppression
try:
    results = bq_client.query(query).result()
    return {row.entity_id for row in results}
except Exception:
    # Table might not exist yet
    return set()  # Hides all errors
```

**Required Fix**:
```python
# ✅ CORRECT - Surface all errors
try:
    results = bq_client.query(query).result()
    return {row.entity_id for row in results}
except Exception as e:
    # Log with full context
    logger.error(
        "Failed to get existing entity IDs",
        extra={"run_id": run_id, "table": table_id, "error": str(e)},
        exc_info=True
    )
    
    # SURFACE ERROR TO USER
    print(f"⚠️  WARNING: Failed to get existing entity IDs")
    print(f"   Error: {str(e)}")
    print(f"   Table: {table_id}")
    print(f"   Returning empty set - may cause duplicates")
    
    # Diagnose
    require_diagnostic_on_error(e, "get_existing_entity_ids")
    
    # Return empty with warning
    return set()
```

**Impact**:
- ✅ All errors surfaced
- ✅ User knows about issues
- ✅ Can take corrective action

**Status**: ⚠️ **REQUIRES FIX** (Multiple locations)

---

## IMPLEMENTATION PLAN

### Phase 1: Critical Fixes (Immediate)

1. ✅ **Fix Stage 3 Identity Service** - Replace hashlib with IdentityService
2. ✅ **Fix All BigQuery Client Fallbacks** - Add cost protection, warnings
3. ✅ **Fix All Error Surfacing** - Print all errors to user
4. ✅ **Fix Silent Error Suppression** - Surface all errors

### Phase 2: High Priority Fixes

5. ✅ **Fix PipelineTracker Fallbacks** - Add real tracking, warnings
6. ✅ **Fix Error Diagnostic Fallbacks** - Add real diagnostics, warnings
7. ✅ **Add Type Hints** - All functions properly typed

### Phase 3: Validation

8. ✅ **Validate Central Services** - Check availability, warn if missing
9. ✅ **Test All Fixes** - Verify fixes work correctly
10. ✅ **Re-certify** - Three-LLM review after fixes

---

## CERTIFICATION STATUS

**Current Status**: ❌ **FAILS INDUSTRY STANDARDS**

**After Fixes**: Will meet industry standards with:
- ✅ Proper central services integration
- ✅ All errors surfaced
- ✅ Cost protection enabled
- ✅ Governance enabled
- ✅ Identity service used correctly

---

**All fixes documented. All errors surfaced. Ready for implementation.**
