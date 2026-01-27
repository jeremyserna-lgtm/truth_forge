# Hierarchy

**Base → Environment → Local. Later layers override earlier.**

---

## The Rule

Configuration layers from most general to most specific. Later layers override.

---

## Layer Order

```
1. Defaults (in code)
   ↓ overridden by
2. Base config (config/base/)
   ↓ overridden by
3. Environment config (config/environments/{env}.yaml)
   ↓ overridden by
4. Local config (config/local/) [gitignored]
   ↓ overridden by
5. Environment variables
```

---

## Example Hierarchy

```yaml
# 1. Code default: pool_size = 5

# 2. config/base/settings.yaml
database:
  pool_size: 10

# 3. config/environments/production.yaml
database:
  pool_size: 50

# 4. config/local/settings.yaml (developer testing)
database:
  pool_size: 2

# 5. Environment variable (emergency override)
# DATABASE_POOL_SIZE=100

# Result in production: pool_size = 50 (env config)
# Result in local dev: pool_size = 2 (local override)
# Result with env var: pool_size = 100 (env var wins)
```

---

## Deep Merge Implementation

```python
def deep_merge(base: dict, override: dict) -> dict:
    """Merge override into base, recursively for nested dicts."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result
```

---

## Full Loading Example

```python
from pathlib import Path
import os
import yaml

def load_config(environment: str | None = None) -> dict:
    env = environment or os.getenv("ENVIRONMENT", "development")
    config_dir = Path("config")

    # Start with base
    config = yaml.safe_load((config_dir / "base/settings.yaml").read_text())

    # Merge environment-specific
    env_file = config_dir / f"environments/{env}.yaml"
    if env_file.exists():
        config = deep_merge(config, yaml.safe_load(env_file.read_text()))

    # Merge local overrides (gitignored)
    local_file = config_dir / "local/settings.yaml"
    if local_file.exists():
        config = deep_merge(config, yaml.safe_load(local_file.read_text()))

    # Environment variables override everything
    # (handled by Pydantic BaseSettings automatically)

    return config
```

---

## What Goes Where

| Layer | Content | Committed |
|-------|---------|-----------|
| Base | Shared defaults, structure | Yes |
| Environment | Env-specific values | Yes |
| Local | Personal overrides, testing | No |
| Env vars | Secrets, runtime overrides | No (platform-managed) |

---

## Debugging Config

```python
def show_config_sources(key: str) -> None:
    """Show where a config value comes from."""
    sources = []
    if key in base_config:
        sources.append(f"base: {base_config[key]}")
    if key in env_config:
        sources.append(f"env: {env_config[key]}")
    if key in local_config:
        sources.append(f"local: {local_config[key]}")
    if key.upper() in os.environ:
        sources.append(f"env_var: {os.environ[key.upper()]}")

    print(f"{key}: {sources}")
```

---

## Anti-Patterns

```yaml
# WRONG - Production values in base config
# config/base/settings.yaml
database:
  url: postgres://prod-server/db  # Should be in production.yaml

# WRONG - Secrets in any config file
# Should ONLY be in environment variables
```

---

## UP

[INDEX.md](INDEX.md)
