# Spark Enforcement System

**The Spark grants life. Without it, code cannot run.**

---

## Overview

The Spark Enforcement System is a cryptographic life-grant mechanism that controls which scripts can execute within the Primitive Engine ecosystem. It implements THE SPARK (Layer 1) from the framework's dual grant system.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     THE DUAL GRANT SYSTEM                                │
│                                                                          │
│  Layer 1 - THE SPARK: Permission to EXIST                               │
│  └── Every script must have a spark to execute                          │
│  └── Ed25519 signed JWT tokens                                          │
│  └── 90-day validity, renewable                                         │
│                                                                          │
│  Layer 2 - THE GENE: Permission to REPRODUCE (future)                   │
│  └── Fertile organisms can spawn daughters                              │
│  └── Requires hardware authentication (Touch ID)                        │
│  └── Premium capability                                                  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Architecture

### Components

| Component | Location | Purpose |
|-----------|----------|---------|
| **SparkCrypto** | `Primitive/governance/spark_service/crypto.py` | JWT creation/verification with Ed25519 |
| **RuntimeEnforcer** | `Primitive/governance/spark_service/enforcement.py` | Runtime script blocking |
| **EnforcementPolicy** | `Primitive/governance/spark_service/enforcement.py` | Configurable enforcement rules |
| **SparkClient** | `Primitive/governance/spark_service/enforcement.py` | Validates sparks from files or service |
| **sitecustomize.py** | Project root / site-packages | Python hook that installs enforcement |
| **CLI** | `Primitive/governance/spark_service/cli.py` | Issue, list, and revoke sparks |

### Flow

```
Python Script Execution
         │
         ▼
┌────────────────────┐
│ sitecustomize.py   │ ← Runs BEFORE any Python code
│ (Python hook)      │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ RuntimeEnforcer    │
│ .check_script()    │
└─────────┬──────────┘
          │
    ┌─────┴─────┐
    │           │
    ▼           ▼
┌────────┐  ┌────────┐
│ Exempt │  │ Require│
│ Path?  │  │ Spark? │
└────┬───┘  └────┬───┘
     │           │
     ▼           ▼
  ALLOWED    ┌────────┐
             │ Has    │
             │ Valid  │
             │ Spark? │
             └────┬───┘
                  │
           ┌─────┴─────┐
           │           │
           ▼           ▼
        ALLOWED     BLOCKED
```

---

## Enforcement Policy

The default policy defines which paths are exempt and which require sparks:

```python
EnforcementPolicy.default():
    exempt_paths = [
        "Primitive/",           # Core organism - no spark needed
        ".venv/",               # Virtual environment
        "site-packages/",       # Installed packages
        "lib/python",           # System Python
        "<stdin>",              # Interactive mode
        "<string>",             # Exec'd strings
    ]

    require_spark_paths = [
        "scripts/",             # All scripts outside Primitive
        "daemon/",              # Daemon scripts
        "apps/",                # Application scripts
        "tools/",               # Tool scripts
    ]

    mode = EnforcementMode.ENFORCE
```

### Enforcement Modes

| Mode | Behavior |
|------|----------|
| `ENFORCE` | Block scripts without valid sparks (default) |
| `WARN` | Log warning but allow execution |
| `AUDIT` | Silent logging only |
| `DISABLED` | No enforcement |

---

## Spark File Format

Sparks are stored as `.spark` files next to scripts:

```
scripts/
├── my_script.py
└── my_script.spark    ← Spark for my_script.py
```

Or in a `.sparks/` directory:

```
scripts/
├── .sparks/
│   └── my_script.spark
└── my_script.py
```

### Spark File Contents

```json
{
  "version": "1.0",
  "valid": true,
  "token": "eyJhbGciOiJFZERTQSIs...",  // JWT signed with Ed25519
  "subject": "scripts/my_script.py",
  "issuer": "primitive_engine_genesis",
  "level": "script",
  "capabilities": ["execute"],
  "issued_at": "2026-01-20T06:22:10+00:00",
  "expires_at": "2026-04-20T06:22:10+00:00",
  "jti": "WUXoMvH5orMQsmlUi97Ofw"
}
```

### JWT Claims

| Claim | Description |
|-------|-------------|
| `sub` | Subject (script path) |
| `iss` | Issuer (organism ID) |
| `iat` | Issued at timestamp |
| `exp` | Expiration timestamp |
| `jti` | Unique token ID (for revocation) |
| `level` | Authorization level (organization/service/script) |
| `capabilities` | What the script can do |

---

## Usage

### Running Scripts with Enforcement

```bash
# Use the convenience wrapper (recommended)
./spark scripts/my_script.py [args...]

# Or set environment variables manually
PYTHONPATH=/path/to/Truth_Engine .venv/bin/python3 scripts/my_script.py
```

### Issuing Sparks

```bash
# Issue spark for a single script
python3 -m Primitive.governance.spark_service.cli issue scripts/my_script.py

# Issue sparks for all scripts in a directory
python3 -m Primitive.governance.spark_service.cli issue-dir scripts/

# Issue with custom duration (default: 90 days)
python3 -m Primitive.governance.spark_service.cli issue scripts/my_script.py --days 30

# Issue with custom capabilities
python3 -m Primitive.governance.spark_service.cli issue scripts/my_script.py --capabilities execute read write
```

### Managing Sparks

```bash
# List all sparks
python3 -m Primitive.governance.spark_service.cli list

# Revoke a spark
python3 -m Primitive.governance.spark_service.cli revoke scripts/my_script.py
```

### Disabling Enforcement

```bash
# Disable for a single run
PRIMITIVE_SPARK_MODE=disabled ./spark scripts/any_script.py

# Or set environment variable
export PRIMITIVE_SPARK_DISABLED=1
```

---

## Cryptographic Standards

### Algorithm

- **Ed25519** (EdDSA) - FIPS 186-5 approved
- 128-bit security level
- Fast signing and verification
- Small key and signature sizes

### Key Storage

Keys are stored in `data/spark_keys/`:

```
data/spark_keys/
├── genesis_private.pem    # Ed25519 private key (PROTECT THIS)
└── genesis_public.pem     # Ed25519 public key
```

### Token Lifetime

| Token Type | Default Lifetime |
|------------|------------------|
| Script spark | 90 days |
| Access token | 15 minutes |
| Refresh token | 7 days |

---

## Integration with sitecustomize.py

The enforcement is installed via Python's `sitecustomize.py` mechanism:

1. **Location**: `.venv/lib/python3.x/site-packages/sitecustomize.py`
2. **Trigger**: Runs automatically before ANY Python script
3. **Environment Variables**:
   - `PRIMITIVE_SPARK_DISABLED=1` - Skip enforcement
   - `PRIMITIVE_SPARK_MODE=warn|audit|enforce|disabled`
   - `PRIMITIVE_SPARK_POLICY=/path/to/policy.json`
   - `PRIMITIVE_SPARK_DEBUG=1` - Show debug output

### Skip Patterns

Enforcement is automatically skipped for:
- pip, pytest, mypy, black, ruff, flake8, pylint
- jupyter, ipython
- Interactive Python (`-c` flag)

---

## Audit Trail

All enforcement decisions are logged to:

```
data/spark_enforcement.jsonl
```

Each entry contains:

```json
{
  "timestamp": "2026-01-20T06:30:00Z",
  "script": "scripts/my_script.py",
  "allowed": true,
  "reason": "Valid spark",
  "requires_spark": true,
  "mode": "enforce"
}
```

---

## Error Messages

### Script Blocked

```
============================================================
SPARK ENFORCEMENT: BLOCKED
============================================================

Reason: No valid spark for this script
Script: scripts/unauthorized_script.py

To run this script, you need to:
1. Request a spark from the SparkService
2. Authenticate with hardware (Touch ID)
3. Run the script again

============================================================
```

### Expired Spark

```
Reason: Spark expired
```

### Invalid Spark

```
Reason: Invalid spark signature
```

---

## Security Considerations

1. **Private Key Protection**: The `genesis_private.pem` key should be protected. Anyone with this key can issue sparks.

2. **Spark Revocation**: Currently, revocation is done by deleting the `.spark` file. Future: Redis-based blacklist for distributed revocation.

3. **Hardware Authentication**: For high-security operations, sparks should require FIDO2/Touch ID authentication before issuance.

4. **Path Traversal**: The enforcement system normalizes paths to prevent bypass via `../` or symlinks.

---

## Future Enhancements

1. **SparkService Socket**: Real-time spark validation via Unix socket
2. **Hardware-Bound Sparks**: Require Touch ID for spark issuance
3. **Capability Enforcement**: Check capabilities at runtime, not just execution
4. **Distributed Revocation**: Redis-based blacklist across federation
5. **THE GENE**: Reproduction grants for spawning daughter organisms

---

## Files Reference

| File | Purpose |
|------|---------|
| `Primitive/governance/spark_service/__init__.py` | Package exports |
| `Primitive/governance/spark_service/spark.py` | Core Spark/Gene dataclasses |
| `Primitive/governance/spark_service/crypto.py` | Ed25519/JWT cryptography |
| `Primitive/governance/spark_service/enforcement.py` | Runtime enforcement |
| `Primitive/governance/spark_service/service.py` | SparkService API |
| `Primitive/governance/spark_service/fido2.py` | Hardware authentication |
| `Primitive/governance/spark_service/cli.py` | Command-line interface |
| `sitecustomize.py` | Python runtime hook |
| `spark` | Convenience wrapper script |
| `data/spark_keys/` | Ed25519 key storage |

---

*The Spark grants life. The organism controls who lives.*

— THE FRAMEWORK, January 2026
