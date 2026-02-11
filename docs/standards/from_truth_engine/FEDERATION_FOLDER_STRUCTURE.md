# Federation Folder Structure Standard

> Universal folder structure for all organisms in the federation

**Version**: 1.0.0  
**Status**: CANONICAL  
**Authority**: [07_STANDARDS.md](../07_STANDARDS.md)  
**Propagation**: All organisms must follow this structure

---

## Overview

This standard defines the **universal folder structure** that all organisms in the Truth Engine federation must follow. It is based on industry best practices (2025) and designed for:

- **Feature-based organization** (domain-driven, not just technical layers)
- **Shallow hierarchies** (2-3 levels maximum)
- **Co-located files** (related files together)
- **Scalability** (works from small to large codebases)
- **Consistency** (same structure across all organisms)

---

## Core Principles

### 1. Feature-Based Organization

Organize by **business capability/domain**, not just technical layers.

**✅ Good**:
```
src/
├── auth/          # Authentication domain
├── users/         # User management domain
└── analytics/     # Analytics domain
```

**❌ Bad**:
```
src/
├── controllers/   # Technical layer
├── services/      # Technical layer
└── models/        # Technical layer
```

### 2. Shallow Hierarchies

Maximum **3 levels** within `src/`. Avoid deep nesting.

**✅ Good**:
```
src/
└── auth/
    ├── __init__.py
    ├── service.py
    └── models.py
```

**❌ Bad**:
```
src/
└── features/
    └── auth/
        └── services/
            └── authentication/
                └── service.py  # Too deep!
```

### 3. Co-Located Files

Keep files that change together in the same folder.

**✅ Good**:
```
auth/
├── service.py
├── models.py
├── tests/
│   └── test_service.py
└── README.md
```

**❌ Bad**:
```
src/
├── auth/
│   └── service.py
└── tests/
    └── test_auth_service.py  # Separated
```

### 4. Descriptive Naming

Use **snake_case**, full words, no abbreviations.

**✅ Good**: `user_management`, `authentication_service`  
**❌ Bad**: `usr_mgmt`, `authSvc`, `user-mgmt`

---

## Universal Structure

**Every organism follows this structure:**

```
{organism_root}/
├── .primitive/              # Organism root (if deployed in target)
│   └── [same structure]
│
├── src/                     # Source code (REQUIRED)
│   ├── __init__.py          # Organism identity
│   ├── main.py              # Entry point
│   │
│   ├── core/                # Core infrastructure (REQUIRED)
│   │   ├── __init__.py
│   │   ├── base_service.py  # Base service class
│   │   ├── governance.py    # Governance enforcement
│   │   ├── observability.py # Logging, metrics
│   │   └── resilience.py    # Retry, circuit breaker
│   │
│   ├── central_services/    # Domain services (REQUIRED)
│   │   ├── __init__.py
│   │   └── {service_name}/  # Feature-based services
│   │       ├── __init__.py
│   │       ├── service.py   # Main service
│   │       ├── models.py    # Data models
│   │       └── tests/       # Service tests
│   │
│   ├── {biological_systems}/ # Biological systems (REQUIRED)
│   │   ├── vitals/          # Heartbeat, pulse, survival
│   │   ├── membrane/        # Input/output filtering
│   │   ├── consciousness/   # Journal, memory
│   │   └── identity/        # Self-model, lineage
│   │
│   ├── {domain_features}/   # Domain-specific features
│   │   └── {feature_name}/  # Feature folder
│   │       ├── __init__.py
│   │       ├── service.py
│   │       ├── models.py
│   │       └── tests/
│   │
│   └── {shared}/            # Shared utilities (optional)
│       ├── utils/
│       ├── types/
│       └── constants/
│
├── config/                  # Configuration (REQUIRED)
│   ├── federation.yaml      # Federation settings
│   ├── governance.yaml     # Governance limits
│   └── reproduction_rights.yaml  # Reproduction config
│
├── docs/                    # Documentation (REQUIRED)
│   ├── README.md            # Organism overview
│   ├── ARCHITECTURE.md      # Architecture docs
│   └── {feature_docs}/     # Feature documentation
│
├── tests/                   # Integration tests (REQUIRED)
│   ├── __init__.py
│   ├── test_core.py
│   └── test_services.py
│
├── scripts/                 # Utility scripts (OPTIONAL)
│   └── deploy.sh
│
├── data/                    # Data storage (REQUIRED)
│   ├── holds/               # HOLD storage
│   ├── atoms/               # Knowledge atoms
│   └── metrics/             # Metrics data
│
├── logs/                    # Log files (REQUIRED)
│   └── organism.jsonl
│
├── .seed/                   # Lineage tracking (REQUIRED)
│   └── lineage.json
│
├── .env                     # Environment config (REQUIRED)
├── requirements.txt         # Dependencies (REQUIRED)
├── README.md                # Project overview (REQUIRED)
└── pyproject.toml           # Project config (OPTIONAL)
```

---

## Required Directories

### 1. `src/` - Source Code

**Purpose**: All source code

**Structure**:
```
src/
├── __init__.py          # Organism identity, PRIMITIVE_PATTERN_SPECIFICATION
├── main.py              # Entry point
├── core/                # Core infrastructure (REQUIRED)
├── central_services/   # Domain services (REQUIRED)
└── {biological_systems}/ # Biological systems (REQUIRED)
```

**Rules**:
- Maximum 3 levels deep
- Feature-based organization
- Co-located tests

### 2. `config/` - Configuration

**Purpose**: All configuration files

**Required Files**:
- `federation.yaml` - Federation connection settings
- `governance.yaml` - Cost limits, authority levels
- `reproduction_rights.yaml` - Reproduction configuration

**Rules**:
- YAML format
- Environment-specific overrides via `.env`

### 3. `docs/` - Documentation

**Purpose**: All documentation

**Required Files**:
- `README.md` - Organism overview
- `ARCHITECTURE.md` - Architecture documentation

**Structure**:
```
docs/
├── README.md
├── ARCHITECTURE.md
└── {feature_name}/  # Feature-specific docs
    └── README.md
```

### 4. `tests/` - Tests

**Purpose**: Integration and system tests

**Structure**:
```
tests/
├── __init__.py
├── test_core.py          # Core infrastructure tests
├── test_services.py     # Service tests
└── fixtures/            # Test fixtures
```

**Rules**:
- Unit tests co-located with code (`src/{feature}/tests/`)
- Integration tests in `tests/`

### 5. `data/` - Data Storage

**Purpose**: Persistent data storage

**Structure**:
```
data/
├── holds/               # HOLD storage (JSONL)
├── atoms/               # Knowledge atoms (DuckDB/JSONL)
└── metrics/             # Metrics data (JSONL)
```

**Rules**:
- Use JSONL for append-only data
- Use DuckDB for queryable data
- Never commit sensitive data

### 6. `logs/` - Log Files

**Purpose**: Application logs

**Structure**:
```
logs/
└── organism.jsonl       # Structured JSON logs
```

**Rules**:
- JSONL format (structured logging)
- Rotate logs (size/time-based)
- Never commit logs to version control

### 7. `.seed/` - Lineage Tracking

**Purpose**: Organism lineage and identity

**Required Files**:
- `lineage.json` - Lineage information

**Rules**:
- JSON format
- Tracks genesis, parent, generation

---

## Service Structure

**Every service follows this pattern:**

```
{service_name}/
├── __init__.py          # Exports, SERVICE_MANIFEST
├── service.py           # Main service class
├── models.py            # Data models (if needed)
├── tests/               # Service tests
│   ├── __init__.py
│   └── test_service.py
└── README.md            # Service documentation (optional)
```

**Example**:
```
central_services/
└── analysis_service/
    ├── __init__.py
    ├── service.py
    ├── models.py
    └── tests/
        └── test_service.py
```

---

## Feature Structure

**Every feature follows this pattern:**

```
{feature_name}/
├── __init__.py
├── service.py           # Feature service
├── models.py            # Feature models
├── types.py             # Type definitions (if needed)
├── tests/               # Feature tests
│   ├── __init__.py
│   └── test_service.py
└── README.md            # Feature documentation
```

**Example**:
```
src/
└── federation/
    ├── __init__.py
    ├── learning_sharer.py
    ├── knowledge_synthesizer.py
    ├── pattern_propagator.py
    └── tests/
        └── test_federation.py
```

---

## Biological Systems Structure

**Every biological system follows this pattern:**

```
{system_name}/
├── __init__.py          # Exports, SERVICE_MANIFEST
├── {component}.py       # System components
└── tests/
    └── test_{component}.py
```

**Example**:
```
vitals/
├── __init__.py
├── heartbeat.py
├── pulse.py
└── survival.py
```

---

## Naming Conventions

### Folders

- **Format**: `snake_case`
- **Style**: Full words, descriptive
- **Examples**: `user_management`, `authentication_service`, `federation_learning`

### Files

- **Python**: `snake_case.py`
- **Config**: `snake_case.yaml`
- **Docs**: `UPPER_SNAKE_CASE.md` or `Title_Case.md`

### Services

- **Format**: `{domain}_{service}.py`
- **Examples**: `analysis_service.py`, `federation_service.py`

---

## Depth Guidelines

### Maximum Depths

| Level | Maximum Depth | Example |
|-------|---------------|---------|
| Root | 1 | `{organism_root}/` |
| Source | 3 | `src/central_services/analysis_service/service.py` |
| Config | 2 | `config/federation.yaml` |
| Docs | 3 | `docs/federation/learning/README.md` |
| Tests | 3 | `src/feature/tests/test_service.py` |

### Anti-Pattern: Deep Nesting

**❌ Bad**:
```
src/
└── features/
    └── domain/
        └── subdomain/
            └── service/
                └── implementation/
                    └── service.py  # 6 levels!
```

**✅ Good**:
```
src/
└── domain_service/  # 2 levels
    └── service.py
```

---

## File Organization Rules

### 1. Co-Location

Keep related files together:

```
auth/
├── service.py        # Service implementation
├── models.py         # Data models
├── types.py          # Type definitions
├── tests/            # Tests
│   └── test_service.py
└── README.md         # Documentation
```

### 2. Separation of Concerns

Separate by domain, not by technical layer:

**✅ Good** (Feature-based):
```
src/
├── auth/
│   ├── service.py
│   └── models.py
└── users/
    ├── service.py
    └── models.py
```

**❌ Bad** (Layer-based):
```
src/
├── services/
│   ├── auth_service.py
│   └── user_service.py
└── models/
    ├── auth_model.py
    └── user_model.py
```

### 3. Shared Code

Place shared utilities in `src/shared/` or `src/utils/`:

```
src/
└── shared/
    ├── utils/
    │   ├── validation.py
    │   └── formatting.py
    ├── types/
    │   └── common.py
    └── constants/
        └── defaults.py
```

---

## Genesis-Specific Structure

**Truth_Engine (Genesis) has additional directories:**

```
Truth_Engine/
├── Primitive/              # Core framework
│   ├── central_services/   # Genesis services
│   ├── seed/              # Organism templates
│   └── ...
├── framework/             # Framework documentation
├── docs/                  # Comprehensive documentation
├── governance/            # Governance data
└── ...
```

**Note**: Genesis structure is more complex but organisms follow the standard structure above.

---

## Organism-Specific Structure

**Organisms deployed in target codebases:**

```
target_codebase/
└── .primitive/            # Organism root
    └── [standard structure]
```

**Note**: Organisms are self-contained in `.primitive/` to avoid conflicts.

---

## Validation Rules

### 1. Required Directories

Every organism **MUST** have:
- `src/`
- `config/`
- `docs/`
- `tests/`
- `data/`
- `logs/`
- `.seed/`

### 2. Required Files

Every organism **MUST** have:
- `src/__init__.py` (with PRIMITIVE_PATTERN_SPECIFICATION)
- `src/main.py`
- `src/core/` (with base_service.py, governance.py, etc.)
- `config/federation.yaml`
- `config/governance.yaml`
- `config/reproduction_rights.yaml`
- `README.md`
- `requirements.txt`
- `.env` (template)

### 3. Depth Validation

- Source code: Maximum 3 levels
- Documentation: Maximum 3 levels
- Tests: Co-located or in `tests/`

### 4. Naming Validation

- Folders: `snake_case` only
- Files: `snake_case.py` or `UPPER_SNAKE_CASE.md`
- No hyphens, no PascalCase, no abbreviations

---

## Propagation Mechanism

### 1. Template-Based

Organism templates include this structure:
- `Primitive/seed/templates/{organism}/` follows this standard
- New organisms inherit structure from template

### 2. Validation

Genesis validates organism structure:
- Pre-deployment validation
- Structure compliance checks
- Non-compliant organisms rejected

### 3. Enforcement

- Framework standards enforce structure
- Service API layer requires structure
- Documentation generation uses structure

---

## Migration Guide

### For Existing Organisms

1. **Audit current structure**
2. **Identify non-compliant areas**
3. **Plan migration** (gradual is OK)
4. **Update gradually** (one feature at a time)
5. **Validate** after each change

### Migration Checklist

- [ ] All required directories exist
- [ ] All required files exist
- [ ] Depth ≤ 3 levels
- [ ] Naming follows conventions
- [ ] Tests co-located or in `tests/`
- [ ] Documentation in `docs/`

---

## Examples

### Example 1: Simple Organism

```
zulip_organism/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   │   ├── base_service.py
│   │   └── governance.py
│   └── central_services/
│       └── analysis_service/
│           ├── service.py
│           └── tests/
│               └── test_service.py
├── config/
│   ├── federation.yaml
│   └── governance.yaml
├── docs/
│   └── README.md
├── tests/
│   └── test_core.py
├── data/
│   └── holds/
├── logs/
└── requirements.txt
```

### Example 2: Complex Organism

```
atlas_organism/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   │   ├── base_service.py
│   │   ├── governance.py
│   │   ├── observability.py
│   │   └── resilience.py
│   ├── central_services/
│   │   ├── analysis_service/
│   │   ├── federation_service/
│   │   └── conversion_service/
│   ├── vitals/
│   │   ├── heartbeat.py
│   │   └── pulse.py
│   ├── membrane/
│   │   └── service.py
│   ├── consciousness/
│   │   └── journal.py
│   ├── identity/
│   │   └── organism_identity.py
│   └── federation/
│       ├── learning_sharer.py
│       └── pattern_propagator.py
├── config/
│   ├── federation.yaml
│   ├── governance.yaml
│   └── reproduction_rights.yaml
├── docs/
│   ├── README.md
│   ├── ARCHITECTURE.md
│   └── federation/
│       └── README.md
├── tests/
│   ├── test_core.py
│   └── test_services.py
├── data/
│   ├── holds/
│   ├── atoms/
│   └── metrics/
├── logs/
├── .seed/
│   └── lineage.json
├── .env
├── requirements.txt
└── README.md
```

---

## Anti-Patterns

### 1. Deep Nesting

**❌ Bad**:
```
src/features/domain/subdomain/service/implementation/service.py
```

**✅ Good**:
```
src/domain_service/service.py
```

### 2. Layer-Based Organization

**❌ Bad**:
```
src/
├── controllers/
├── services/
└── models/
```

**✅ Good**:
```
src/
├── auth/
│   ├── service.py
│   └── models.py
└── users/
    ├── service.py
    └── models.py
```

### 3. Inconsistent Naming

**❌ Bad**:
```
AuthService/
auth-service/
auth_svc/
```

**✅ Good**:
```
auth_service/
```

### 4. Root-Level Files

**❌ Bad**:
```
organism_root/
├── service.py
├── models.py
└── utils.py
```

**✅ Good**:
```
organism_root/
└── src/
    └── feature/
        ├── service.py
        ├── models.py
        └── utils.py
```

---

## Industry Standards Alignment

This standard aligns with:

1. **Feature-Based Organization** (2025 best practice)
2. **Shallow Hierarchies** (2-3 levels max)
3. **Co-Located Files** (related files together)
4. **Domain-Driven Design** (organize by domain)
5. **Python PEP Standards** (snake_case, module structure)

---

## References

- **Industry Research**: 2025 folder structure best practices
- **Python Standards**: PEP 8, PEP 420
- **Domain-Driven Design**: Feature-based organization
- **Truth Engine Framework**: PRIMITIVE_PATTERN_SPECIFICATION

---

## Enforcement

### Pre-Deployment Validation

Genesis validates organism structure before deployment:
- Required directories present
- Required files present
- Depth compliance
- Naming compliance

### Runtime Validation

Organisms validate their own structure on startup:
- Structure integrity checks
- Missing directory warnings
- Non-compliance errors

### Documentation Generation

Structure-aware documentation:
- Auto-generates from structure
- Validates structure compliance
- Reports non-compliance

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-21 | Initial standard based on industry research |

---

## The Principle

> **Every folder has a purpose. Every purpose has a home. Every organism follows the same structure.**

This standard ensures consistency, scalability, and maintainability across the entire federation.

---

*Federation Folder Structure Standard v1.0.0*  
*Propagates to all organisms in the Truth Engine federation*
