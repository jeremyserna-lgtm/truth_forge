# Validation

**Fail at startup, not at runtime. Validate all configuration.**

---

## The Rule

All configuration must be validated when the application starts. Invalid config = immediate failure.

---

## Why Validate at Startup

| Runtime Failure | Startup Failure |
|-----------------|-----------------|
| Happens at 3 AM | Happens at deploy |
| Affects users | Affects deployment |
| Hard to debug | Clear error message |
| Partial state | No state corruption |

---

## Validation with Pydantic

```python
from pydantic import BaseSettings, validator, Field

class DatabaseConfig(BaseSettings):
    url: str = Field(..., env="DATABASE_URL")
    pool_size: int = Field(5, ge=1, le=100)
    timeout_seconds: int = Field(30, ge=1, le=300)

    @validator("url")
    def validate_url(cls, v: str) -> str:
        if not v.startswith(("postgres://", "postgresql://")):
            raise ValueError("DATABASE_URL must be a PostgreSQL URL")
        return v

class Config(BaseSettings):
    environment: str = Field("development", env="ENVIRONMENT")
    database: DatabaseConfig
    debug: bool = Field(False, env="DEBUG")

    @validator("debug")
    def no_debug_in_prod(cls, v: bool, values: dict) -> bool:
        if v and values.get("environment") == "production":
            raise ValueError("DEBUG cannot be true in production")
        return v
```

---

## Startup Validation Pattern

```python
def create_app() -> App:
    # Validate config FIRST - fail fast
    try:
        config = Config()
    except ValidationError as e:
        logger.error("Configuration validation failed", extra={"errors": e.errors()})
        raise SystemExit(1) from e

    # Only proceed if config is valid
    app = App(config=config)
    return app
```

---

## What to Validate

| Category | Validations |
|----------|-------------|
| Required values | Present, not empty |
| Types | Correct type (int, str, etc.) |
| Ranges | Within acceptable bounds |
| Formats | URLs, emails, patterns |
| Combinations | Cross-field dependencies |
| Existence | Files exist, services reachable |

---

## Validation Error Messages

```python
# GOOD - Actionable error
raise ValueError(
    "DATABASE_URL must be a PostgreSQL URL starting with 'postgres://' or "
    "'postgresql://'. Got: 'mysql://...'"
)

# BAD - Unhelpful
raise ValueError("Invalid URL")
```

---

## Health Check for Runtime Config

```python
async def config_health_check() -> dict:
    """Verify config-dependent resources are accessible."""
    checks = {}

    # Database reachable?
    try:
        await db.execute("SELECT 1")
        checks["database"] = "healthy"
    except Exception as e:
        checks["database"] = f"unhealthy: {e}"

    return checks
```

---

## Anti-Patterns

```python
# WRONG - Validate later
def get_db_connection():
    url = os.getenv("DATABASE_URL")  # Might be None!
    return connect(url)  # Fails here, not at startup

# WRONG - Silent defaults
pool_size = int(os.getenv("POOL_SIZE", "invalid"))  # ValueError at runtime
```

---

## UP

[INDEX.md](INDEX.md)
