# Custom Exceptions

**Domain-specific exceptions with clear hierarchy.**

---

## Exception Hierarchy

```python
# src/core/exceptions.py

class TruthEngineError(Exception):
    """Base exception for all Truth Engine errors."""
    pass

class ConfigurationError(TruthEngineError):
    """Configuration is missing or invalid."""
    pass

class ValidationError(TruthEngineError):
    """Data validation failed."""
    pass

class ExternalServiceError(TruthEngineError):
    """External service call failed."""
    pass

class CostLimitExceeded(TruthEngineError):
    """Operation would exceed cost budget."""
    pass

class IdempotencyViolation(TruthEngineError):
    """Operation is not idempotent as required."""
    pass
```

---

## User-Facing Errors

```python
class UserFacingError(TruthEngineError):
    """Error safe to show to users."""

    def __init__(
        self,
        message: str,
        error_code: str,
        internal_details: str | None = None,
    ) -> None:
        super().__init__(message)
        self.error_code = error_code
        self.internal_details = internal_details  # Logged, not shown

# Usage
raise UserFacingError(
    message="Unable to save your document. Please try again.",
    error_code="DOC_SAVE_001",
    internal_details=f"SQL: {sql_query}, Error: {db_error}"
)
```

---

## Anti-Patterns

```python
# WRONG - Exposes internals
raise Exception(f"SQL error: {sql_query} failed with {db_error}")

# WRONG - Generic exception
try:
    process()
except Exception:  # Too broad
    pass

# CORRECT - Specific, safe, logged
try:
    process()
except ValidationError as e:
    logger.warning("Validation failed", extra={"error": str(e)})
    raise UserFacingError("Invalid input", "VAL_001", str(e))
```

---

## UP

[error_handling/INDEX.md](INDEX.md)
