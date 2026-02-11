# Standards Index

**The Standard** | Authoritative operational standards for Truth Engine.

**Authority**: This index is governed by [07_STANDARDS.md](../07_STANDARDS.md)

---

## Quick Reference

| Standard | What It Governs | Status |
|----------|-----------------|--------|
| [NAMING_CONVENTION.md](NAMING_CONVENTION.md) | What to call things | CANONICAL |
| [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) | Universal folder structure for all organisms | CANONICAL |
| [DOCUMENT_FORMAT.md](DOCUMENT_FORMAT.md) | How MD files are structured | CANONICAL |
| [CODE_QUALITY.md](CODE_QUALITY.md) | Type hints, docstrings, linting | CANONICAL |
| [DEPRECATION.md](DEPRECATION.md) | How code is phased out | CANONICAL |
| [ERROR_HANDLING.md](ERROR_HANDLING.md) | Failures, retry, DLQ | CANONICAL |
| [LOGGING.md](LOGGING.md) | Structured event logging | CANONICAL |
| [TESTING.md](TESTING.md) | How code is verified | CANONICAL |
| [CONFIGURATION.md](CONFIGURATION.md) | How settings are managed | CANONICAL |
| [SECURITY.md](SECURITY.md) | How systems are protected | CANONICAL |
| [API_DESIGN.md](API_DESIGN.md) | How interfaces are built | CANONICAL |
| [VERSION_CONTROL.md](VERSION_CONTROL.md) | How code is versioned | CANONICAL |
| [PIPELINE_STANDARD.md](PIPELINE_STANDARD.md) | All pipeline development | CANONICAL |

---

## Canonical Standards

These are THE authoritative standards. When in doubt, these are correct.

### Foundation Standards

| Standard | What It Governs | 06_LAW Pillar |
|----------|-----------------|---------------|
| [NAMING_CONVENTION.md](NAMING_CONVENTION.md) | Names for all artifacts | One Canonical Source |
| [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) | File/folder organization | One Canonical Source |
| [DOCUMENT_FORMAT.md](DOCUMENT_FORMAT.md) | Markdown document structure | No Magic |

### Code Standards

| Standard | What It Governs | 06_LAW Pillar |
|----------|-----------------|---------------|
| [CODE_QUALITY.md](CODE_QUALITY.md) | Type hints, docstrings, static analysis | No Magic |
| [DEPRECATION.md](DEPRECATION.md) | Code phase-out process | Observability |
| [ERROR_HANDLING.md](ERROR_HANDLING.md) | Failure management, DLQ, retry | Fail-Safe |
| [LOGGING.md](LOGGING.md) | Structured logging, tracing | Observability |
| [TESTING.md](TESTING.md) | Code verification, CI/CD | Hardening |
| [CONFIGURATION.md](CONFIGURATION.md) | Settings management | No Magic |
| [SECURITY.md](SECURITY.md) | System protection | Trust/Control |
| [API_DESIGN.md](API_DESIGN.md) | Interface contracts | Identity/Scope |
| [VERSION_CONTROL.md](VERSION_CONTROL.md) | Code versioning | Observability |

---

## Standards with Tooling

These standards include automated enforcement tooling:

### DEPRECATION.md

**Governs**: How code is deprecated and removed safely.

**Tooling**:
- `deprecation/deprecation_utils.py` - `@deprecated` decorator
- `deprecation/deprecation_checker.py` - Pylint enforcement plugin
- `deprecation/test_deprecation.py` - Test suite

---

## Pipeline Standard

| Standard | What It Governs | Status |
|----------|-----------------|--------|
| [PIPELINE_STANDARD.md](PIPELINE_STANDARD.md) | **All pipeline development** - the single source of truth | CANONICAL |

---

## Specifications

These define detailed implementation patterns. They extend (not replace) the canonical standards.

| Specification | What It Defines | Status |
|---------------|-----------------|--------|
| [PRIMITIVE_PATTERN_SPECIFICATION.md](PRIMITIVE_PATTERN_SPECIFICATION.md) | HOLD→AGENT→HOLD for scripts | ACTIVE |

---

## Resources

| Resource | Purpose |
|----------|---------|
| [templates/STANDARD_TEMPLATE.md](templates/STANDARD_TEMPLATE.md) | Template for creating new standards |
| [archive/](archive/) | Superseded documents (historical reference only) |

---

## Folder Structure

```
framework/standards/
├── INDEX.md                    # This file
│
├── # Foundation Standards
├── NAMING_CONVENTION.md        # CANONICAL
├── PROJECT_STRUCTURE.md         # CANONICAL
├── DOCUMENT_FORMAT.md          # CANONICAL
│
├── # Code Standards
├── CODE_QUALITY.md             # CANONICAL (NEW)
├── DEPRECATION.md              # CANONICAL
├── ERROR_HANDLING.md           # CANONICAL
├── LOGGING.md                  # CANONICAL
├── TESTING.md                  # CANONICAL
├── CONFIGURATION.md            # CANONICAL
├── SECURITY.md                 # CANONICAL
├── API_DESIGN.md               # CANONICAL
├── VERSION_CONTROL.md          # CANONICAL
│
├── # Tooling
├── deprecation/
│   ├── __init__.py
│   ├── deprecation_utils.py
│   ├── deprecation_checker.py
│   └── test_deprecation.py
│
├── # Pipeline Standard
├── PIPELINE_STANDARD.md        # CANONICAL - single source of truth for pipelines
│
├── # Specifications
├── PRIMITIVE_PATTERN_SPECIFICATION.md
│
├── # Resources
├── templates/
│   └── STANDARD_TEMPLATE.md
└── archive/
    ├── INDEX.md
    ├── DOCUMENT_SERIES_FRAMEWORK.md
    ├── PRIMITIVE_FOLDER_PATTERN.md
    ├── TRUTH_ENGINE_STANDARDS_RECURSIVE_ASSESSMENT.md
    ├── PIPELINE_PATTERN_SPECIFICATION.md
    └── UNIVERSAL_PIPELINE_PATTERN.md
```

---

## Adding New Standards

1. Use [templates/STANDARD_TEMPLATE.md](templates/STANDARD_TEMPLATE.md)
2. Follow [DOCUMENT_FORMAT.md](DOCUMENT_FORMAT.md) structure
3. Follow [NAMING_CONVENTION.md](NAMING_CONVENTION.md) for naming
4. Map to a 06_LAW pillar (Fail-Safe, No Magic, Observability, Idempotency)
5. Add to this INDEX in appropriate section
6. If automatable, create tooling subfolder
7. Update [07_STANDARDS.md](../07_STANDARDS.md) canonical table

---

## Standards Completeness Checklist

Enterprise-grade standards coverage:

| Domain | Standard | Status |
|--------|----------|--------|
| Naming | NAMING_CONVENTION | ✅ |
| Structure | PROJECT_STRUCTURE | ✅ |
| Documentation | DOCUMENT_FORMAT | ✅ |
| Code Quality | CODE_QUALITY | ✅ |
| Deprecation | DEPRECATION | ✅ |
| Errors | ERROR_HANDLING | ✅ |
| Logging | LOGGING | ✅ |
| Testing | TESTING | ✅ |
| Configuration | CONFIGURATION | ✅ |
| Security | SECURITY | ✅ |
| API Design | API_DESIGN | ✅ |
| Version Control | VERSION_CONTROL | ✅ |
| Pipelines | PIPELINE_STANDARD | ✅ |

---

*Standards index with industry alignment. Complete.*
