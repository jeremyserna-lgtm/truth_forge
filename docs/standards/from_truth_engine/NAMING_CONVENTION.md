# Naming Convention

**The Standard** | Everything has one name. One pattern. No exceptions.

**Authority**: [07_STANDARDS.md](../07_STANDARDS.md) | **Status**: CANONICAL

---

## Quick Reference

| Element | Convention | Example |
|---------|------------|---------|
| **Datasets** | lowercase, single word | `spine`, `enrichment`, `governance` |
| **Tables** | snake_case | `entity_unified`, `document_blocks` |
| **Fields** | snake_case + pattern suffix | `document_id`, `created_at`, `word_count` |
| **Folders (code)** | snake_case | `embedding_service/`, `the_framework/` |
| **Folders (docs)** | snake_case | `docs/standards/` |
| **Code files** | snake_case.py | `service.py`, `naming_conventions.py` |
| **Classes** | PascalCase | `EmbeddingService`, `TruthService` |
| **Test files** | test_ prefix | `test_service.py` |
| **Documentation** | UPPERCASE_WITH_UNDERSCORES.md | `NAMING_CONVENTION.md` |
| **Scripts** | snake_case.py | `analyze_patterns.py` |

---

## The Rules

### 1. Datasets (BigQuery)

**Pattern**: `^[a-z]+$` (lowercase, single word, no underscores)

```
✅ spine
✅ enrichment
✅ governance
✅ identity

❌ Spine           (uppercase)
❌ spine_data      (has underscore)
❌ spine-data      (has hyphen)
```

### 2. Tables (BigQuery)

**Pattern**: `^[a-z][a-z0-9_]*[a-z0-9]$` (snake_case)

```
✅ document
✅ entity_unified
✅ document_blocks
✅ chatgpt_web_stage_5

❌ Document        (uppercase)
❌ documentBlocks  (camelCase)
❌ document-blocks (kebab-case)
```

### 3. Fields (BigQuery)

**Pattern**: snake_case with semantic suffix

| Suffix | Pattern | Examples |
|--------|---------|----------|
| `_id` | `{entity}_id` | `document_id`, `message_id` |
| `_at` | `{event}_at` | `created_at`, `ingested_at` |
| `_ts` | `{event}_ts` | `start_ts`, `end_ts` |
| `_count` | `{entity}_count` | `word_count`, `message_count` |
| `_hash` | `{entity}_hash` | `content_hash` |
| `_score` | `{metric}_score` | `sentiment_score` |
| `_index` | `{entity}_index` | `word_index` |
| `_type` | `{entity}_type` | `block_type`, `source_type` |
| `is_` | `is_{condition}` | `is_active`, `is_formative` |
| `has_` | `has_{entity}` | `has_embedding` |

```
✅ document_id
✅ created_at
✅ word_count

❌ documentId      (camelCase)
❌ created_time    (wrong suffix)
❌ count           (too generic)
```

### 4. Folders

**Pattern**: snake_case (lowercase with underscores)

```
✅ embedding_service/
✅ the_framework/
✅ docs/standards/

❌ EmbeddingService/   (PascalCase)
❌ the-framework/      (kebab-case)
❌ TheFramework/       (PascalCase)
```

### 5. Code Files

**Pattern**: snake_case.py

```
✅ service.py
✅ naming_conventions.py
✅ cost_tracker.py

❌ Service.py          (PascalCase)
❌ namingConventions.py (camelCase)
```

### 6. Classes

**Pattern**: PascalCase

```
✅ EmbeddingService
✅ TruthService
✅ CostTracker

❌ embedding_service   (snake_case)
❌ embeddingService    (camelCase)
```

### 7. Test Files

**Pattern**: test_{what_is_tested}.py

```
✅ test_service.py
✅ test_naming_conventions.py
✅ test_cost_tracker.py

❌ service_test.py     (suffix not prefix)
❌ TestService.py      (PascalCase)
```

### 8. Documentation Files

**Pattern**: UPPERCASE_WITH_UNDERSCORES.md

```
✅ NAMING_CONVENTION.md
✅ FOLDER_STRUCTURE.md
✅ THE_FRAMEWORK.md

❌ naming_convention.md  (lowercase)
❌ NamingConvention.md   (PascalCase)
❌ naming-convention.md  (kebab-case)
```

### 9. Scripts

**Pattern**: snake_case.py (descriptive action)

| Type | Pattern | Example |
|------|---------|---------|
| Analysis | `analyze_{subject}.py` | `analyze_patterns.py` |
| Migration | `migrate_{source}_to_{target}.py` | `migrate_data_to_v2.py` |
| Stage | `{pipeline}_stage_{N}.py` | `chatgpt_web_stage_5.py` |
| Utility | `{action}_{subject}.py` | `validate_schema.py` |

---

## Enforcement

These conventions are enforced at multiple layers:

| Layer | Mechanism | Location |
|-------|-----------|----------|
| Code | `NamingConventionValidator` | `core/schema/naming_conventions.py` |
| Pre-commit | Hooks | `.pre-commit-config.yaml` |
| Review | Checklist | `.claude/rules/04-code-review.md` |

---

## Sources (Consolidated From)

| Document | What It Covered | Status |
|----------|-----------------|--------|
| `naming_conventions.py` | BigQuery enforcement code | Remains (code) |
| `BIGQUERY_SCHEMA_NAMING_GUIDE.md` | BigQuery detailed docs | Deprecated by this |
| `ORGANIZATIONAL_PATTERN_STANDARD.md` | Files, folders, scripts | Remains (detailed ops) |
| `PRIMITIVE_FOLDER_PATTERN.md` | Code folder patterns | Remains (code structure) |

**This document is THE naming convention standard.** The detailed references above provide implementation-specific details.

---

## The Principle

> **One name. One pattern. No exceptions.**

If you're unsure what to name something, this document tells you. If it's not covered here, propose an addition.

---

*~180 lines. The naming convention. Complete.*
