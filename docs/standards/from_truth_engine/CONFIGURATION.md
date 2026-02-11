# Configuration

**The Standard** | Every setting is explicit, validated, environment-aware, and never hardcoded.

**Authority**: [07_STANDARDS.md](../07_STANDARDS.md) | **Status**: CANONICAL

---

## Quick Reference

| Requirement | Rule |
|-------------|------|
| Source | Environment variables + config files, never hardcoded |
| Validation | All config validated at startup |
| Secrets | Never in code, never in version control |
| Defaults | Explicit defaults for non-critical settings |
| Documentation | Every config option documented |
| Environments | Clear separation: dev/staging/prod |

---

## WHY (Theory)

### The "No Magic" Imperative

From 06_LAW: *"No magic. Everything explicit."*

Configuration is where magic hides. Hardcoded values, implicit defaults, environment assumptions—these are landmines waiting for deployment day. The standard eliminates magic by making every configuration decision explicit and traceable.

### The Twelve-Factor Alignment

This standard implements Factor III (Config) of the Twelve-Factor App methodology: configuration that varies between deployments should be stored in the environment.

---

## WHAT (Specification)

### Configuration Hierarchy

```
Priority (highest to lowest):
1. Command-line arguments
2. Environment variables
3. Environment-specific config file (.env.production)
4. Default config file (.env.defaults)
5. Application defaults (in code, explicit)
```

### MUST (Required)

1. **No Hardcoded Configuration** — All configurable values MUST come from external sources.

```python
# ✅ Correct
DATABASE_URL = os.environ["DATABASE_URL"]
MAX_CONNECTIONS = int(os.environ.get("MAX_CONNECTIONS", "10"))

# ❌ Wrong - hardcoded
DATABASE_URL = "postgresql://localhost/mydb"
MAX_CONNECTIONS = 10
```

2. **Startup Validation** — All required configuration MUST be validated at startup.

```python
from pydantic import BaseSettings, validator

class Settings(BaseSettings):
    database_url: str
    api_key: str
    max_connections: int = 10
    debug: bool = False

    @validator('database_url')
    def validate_database_url(cls, v):
        if not v.startswith(('postgresql://', 'mysql://')):
            raise ValueError('Invalid database URL scheme')
        return v

    @validator('max_connections')
    def validate_max_connections(cls, v):
        if not 1 <= v <= 100:
            raise ValueError('max_connections must be between 1 and 100')
        return v

    class Config:
        env_file = '.env'

# Application fails fast if config is invalid
settings = Settings()  # Raises at startup if invalid
```

3. **Secrets Separation** — Secrets MUST NOT appear in version control.

```bash
# .gitignore - REQUIRED entries
.env
.env.local
.env.*.local
*.pem
*.key
secrets/
```

```python
# ✅ Correct - secret from environment
API_KEY = os.environ["API_KEY"]

# ❌ Wrong - secret in code
API_KEY = "sk-1234567890abcdef"

# ❌ Wrong - secret in committed file
# config.py checked into git with API_KEY = "..."
```

4. **Explicit Defaults** — Default values MUST be declared explicitly in code.

```python
class Settings(BaseSettings):
    # Required - no default (will fail if not provided)
    database_url: str

    # Optional with explicit default
    log_level: str = "INFO"
    max_retries: int = 3
    timeout_seconds: float = 30.0

    # Optional that can be None
    sentry_dsn: str | None = None
```

5. **Environment Separation** — Configuration MUST distinguish between environments.

```
.env.defaults      # Shared defaults (committed)
.env.development   # Development overrides (not committed, templated)
.env.staging       # Staging overrides (not committed)
.env.production    # Production overrides (not committed)
```

6. **Documentation** — Every configuration option MUST be documented.

```python
class Settings(BaseSettings):
    """Application configuration.

    Attributes:
        database_url: PostgreSQL connection string.
            Format: postgresql://user:pass@host:port/db
            Required in all environments.

        cache_ttl: Cache time-to-live in seconds.
            Default: 300 (5 minutes)
            Increase for read-heavy workloads.

        debug: Enable debug mode.
            Default: False
            WARNING: Never enable in production.
    """
    database_url: str
    cache_ttl: int = 300
    debug: bool = False
```

### SHOULD (Recommended)

1. **Type-Safe Configuration** — Use Pydantic or similar for type validation.

2. **Feature Flags** — Use a dedicated feature flag system for runtime toggles.

```python
class FeatureFlags(BaseSettings):
    enable_new_checkout: bool = False
    enable_dark_mode: bool = False
    max_beta_users: int = 100

    class Config:
        env_prefix = "FF_"  # FF_ENABLE_NEW_CHECKOUT=true
```

3. **Configuration Freezing** — Make config immutable after startup.

```python
from pydantic import BaseSettings

class Settings(BaseSettings):
    class Config:
        frozen = True  # Immutable after creation
```

4. **Health Check Exposure** — Expose non-sensitive config in health endpoints.

```python
@app.get("/health")
def health():
    return {
        "status": "healthy",
        "config": {
            "environment": settings.environment,
            "log_level": settings.log_level,
            "debug": settings.debug,
            # Never expose: database_url, api_key, secrets
        }
    }
```

### MAY (Optional)

1. **Hot Reloading** — Allow config updates without restart for non-critical settings.
2. **Remote Config** — Use remote configuration services (Consul, AWS Parameter Store).
3. **Config Versioning** — Track configuration changes over time.

### MUST NOT (Prohibited)

1. **Never Commit Secrets** — No API keys, passwords, tokens in version control.
2. **Never Use Production Secrets in Dev** — Development uses separate, limited credentials.
3. **Never Default Secrets** — Required secrets have no default; they must be explicitly provided.
4. **Never Trust Client Config** — Configuration from untrusted sources must be validated.

---

## HOW (Reference)

### Standard Configuration Module

```python
# config.py
from functools import lru_cache
from pydantic import BaseSettings, validator, Field
from typing import Literal

class Settings(BaseSettings):
    """Application configuration loaded from environment."""

    # Environment
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = Field(default=False, description="Enable debug mode")

    # Database
    database_url: str = Field(..., description="PostgreSQL connection string")
    database_pool_size: int = Field(default=5, ge=1, le=20)

    # API
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000, ge=1, le=65535)

    # Security
    secret_key: str = Field(..., min_length=32)
    allowed_hosts: list[str] = Field(default=["*"])

    # External Services
    redis_url: str | None = None
    sentry_dsn: str | None = None

    @validator('debug')
    def no_debug_in_production(cls, v, values):
        if v and values.get('environment') == 'production':
            raise ValueError('Debug mode cannot be enabled in production')
        return v

    @validator('allowed_hosts')
    def no_wildcard_in_production(cls, v, values):
        if '*' in v and values.get('environment') == 'production':
            raise ValueError('Wildcard hosts not allowed in production')
        return v

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Usage
settings = get_settings()
```

### Environment File Template

```bash
# .env.template - Commit this file
# Copy to .env and fill in values

# Environment (development, staging, production)
ENVIRONMENT=development

# Debug mode (never true in production)
DEBUG=false

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
DATABASE_POOL_SIZE=5

# API Server
API_HOST=0.0.0.0
API_PORT=8000

# Security (generate with: openssl rand -hex 32)
SECRET_KEY=your-secret-key-here-min-32-chars

# Allowed hosts (comma-separated)
ALLOWED_HOSTS=localhost,127.0.0.1

# External Services (optional)
REDIS_URL=
SENTRY_DSN=
```

### Secrets Management

```python
# For production, use a secrets manager
import boto3
from functools import lru_cache

@lru_cache()
def get_secret(secret_name: str) -> str:
    """Retrieve secret from AWS Secrets Manager."""
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=secret_name)
    return response['SecretString']

class ProductionSettings(Settings):
    """Production settings with secrets manager integration."""

    @validator('secret_key', pre=True, always=True)
    def load_secret_key(cls, v):
        if v and v.startswith('aws:'):
            return get_secret(v[4:])  # aws:secret-name -> lookup
        return v
```

---

## Enforcement

### Automated Checks

| Tool | Check | Severity |
|------|-------|----------|
| git-secrets | No secrets in commits | error |
| detect-secrets | Scan for hardcoded secrets | error |
| Custom linter | No hardcoded URLs/keys | error |
| Startup | Config validation | error |

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/awslabs/git-secrets
    rev: master
    hooks:
      - id: git-secrets
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
```

### Escape Hatch

For local development with simplified config:

```python
# standard:override configuration-secrets - Local development only
if os.environ.get("LOCAL_DEV") == "true":
    settings = Settings(
        database_url="postgresql://localhost/dev",
        secret_key="dev-only-not-for-production-key123"
    )
```

---

## Related Standards

- [SECURITY.md](SECURITY.md) — Secrets classification
- [LOGGING.md](LOGGING.md) — Configuration logging (sanitized)

---

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2025-01-18 | Initial standard | Claude |
