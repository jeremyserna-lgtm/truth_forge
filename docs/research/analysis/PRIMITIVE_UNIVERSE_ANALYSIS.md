# Primitive Universe - Data Model Analysis

**Date**: 2026-01-03
**Purpose**: Analyze the extraction script and data model against framework and industry standards.

---

## Current Data Model

### Table 1: `scripts`
```sql
CREATE TABLE scripts (
    script_id TEXT PRIMARY KEY,
    canonical_name TEXT,
    file_path TEXT UNIQUE,
    file_hash TEXT,
    total_primitives INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    registered_at TIMESTAMP
)
```

### Table 2: `patterns`
```sql
CREATE TABLE patterns (
    pattern_id TEXT PRIMARY KEY,
    pattern_type TEXT,
    pattern_name TEXT,
    pattern_signature TEXT,
    pattern_hash TEXT UNIQUE,
    total_usage_count INT DEFAULT 0,
    script_count INT DEFAULT 0,
    first_seen_in TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### Table 3: `script_has_pattern`
```sql
CREATE TABLE script_has_pattern (
    script_id TEXT,
    pattern_id TEXT,
    count_in_script INT DEFAULT 1,
    first_line INT,
    PRIMARY KEY (script_id, pattern_id)
)
```

### Table 4: `pattern_positions`
```sql
CREATE TABLE pattern_positions (
    script_id TEXT,
    pattern_id TEXT,
    line_number INT,
    col_offset INT,
    parent_pattern_id TEXT,
    nesting_level INT,
    nesting_path TEXT
)
```

### Table 5: `pattern_paths`
```sql
CREATE TABLE pattern_paths (
    path_id TEXT PRIMARY KEY,
    path_signature TEXT,
    path_hash TEXT UNIQUE,
    depth INT,
    frequency INT DEFAULT 1,
    desired TEXT DEFAULT 'unlabeled',
    reason TEXT
)
```

### Table 6: `path_elements`
```sql
CREATE TABLE path_elements (
    path_id TEXT,
    position INT,
    pattern_id TEXT,
    relationship_to_next TEXT,
    PRIMARY KEY (path_id, position)
)
```

---

## Framework Analysis

### HOLD → AGENT → HOLD Pattern

| Component | Current Implementation | Status |
|-----------|----------------------|--------|
| **HOLD₁ (Input)** | Python file on disk | ✓ Correct |
| **AGENT (Process)** | AST parsing + extraction | ✓ Correct |
| **HOLD₂ (Output)** | DuckDB tables | ⚠️ Issues (see below) |

### Issues Identified

#### 1. No Foreign Key Constraints
**Problem**: Tables reference each other but don't enforce referential integrity.

```sql
-- pattern_positions references scripts.script_id but no FK
-- pattern_positions references patterns.pattern_id but no FK
-- path_elements references pattern_paths.path_id but no FK
```

**Industry Standard**: Relational databases should enforce referential integrity.

**Fix Required**:
```sql
ALTER TABLE pattern_positions ADD FOREIGN KEY (script_id) REFERENCES scripts(script_id);
ALTER TABLE pattern_positions ADD FOREIGN KEY (pattern_id) REFERENCES patterns(pattern_id);
ALTER TABLE path_elements ADD FOREIGN KEY (path_id) REFERENCES pattern_paths(path_id);
ALTER TABLE path_elements ADD FOREIGN KEY (pattern_id) REFERENCES patterns(pattern_id);
ALTER TABLE script_has_pattern ADD FOREIGN KEY (script_id) REFERENCES scripts(script_id);
ALTER TABLE script_has_pattern ADD FOREIGN KEY (pattern_id) REFERENCES patterns(pattern_id);
```

#### 2. pattern_positions Has No Primary Key
**Problem**: The table has no unique identifier for rows.

```sql
CREATE TABLE pattern_positions (
    script_id TEXT,
    pattern_id TEXT,
    line_number INT,
    ...
    -- NO PRIMARY KEY
)
```

**Industry Standard**: Every table should have a primary key.

**Fix Required**:
```sql
CREATE TABLE pattern_positions (
    position_id TEXT PRIMARY KEY,  -- Add unique ID
    script_id TEXT NOT NULL,
    pattern_id TEXT NOT NULL,
    line_number INT NOT NULL,
    col_offset INT NOT NULL,
    parent_pattern_id TEXT,
    nesting_level INT NOT NULL,
    nesting_path TEXT NOT NULL,
    UNIQUE (script_id, pattern_id, line_number, col_offset)  -- Composite unique
)
```

#### 3. Missing NOT NULL Constraints
**Problem**: Columns that should never be null don't have constraints.

| Table | Column | Should Be NOT NULL |
|-------|--------|-------------------|
| scripts | file_path | ✓ Yes |
| scripts | file_hash | ✓ Yes |
| patterns | pattern_type | ✓ Yes |
| patterns | pattern_hash | ✓ Yes |
| pattern_positions | script_id | ✓ Yes |
| pattern_positions | pattern_id | ✓ Yes |
| pattern_positions | line_number | ✓ Yes |

#### 4. Missing Indexes
**Problem**: Queries will be slow without proper indexes.

**Current Indexes**:
```sql
idx_patterns_hash ON patterns(pattern_hash)
idx_paths_hash ON pattern_paths(path_hash)
idx_positions_script ON pattern_positions(script_id)
```

**Missing Indexes**:
```sql
-- For pattern lookups
CREATE INDEX idx_patterns_type ON patterns(pattern_type);
CREATE INDEX idx_patterns_name ON patterns(pattern_name);

-- For position lookups
CREATE INDEX idx_positions_pattern ON pattern_positions(pattern_id);
CREATE INDEX idx_positions_line ON pattern_positions(line_number);

-- For path lookups
CREATE INDEX idx_paths_depth ON pattern_paths(depth);
CREATE INDEX idx_paths_desired ON pattern_paths(desired);

-- For script lookups
CREATE INDEX idx_scripts_hash ON scripts(file_hash);
```

#### 5. Normalization Issues

**1st Normal Form (1NF)**: ⚠️ Violation
- `nesting_path` stores a concatenated string (`"A → B → C"`) instead of proper relational reference.
- This duplicates data that's already in `path_elements`.

**Solution**: Remove `nesting_path` from `pattern_positions` - it's already captured in `pattern_paths` and `path_elements`.

**2nd Normal Form (2NF)**: ✓ OK
- All non-key attributes depend on the whole key.

**3rd Normal Form (3NF)**: ⚠️ Violation
- `total_usage_count` and `script_count` in `patterns` are derived values.
- These can be calculated from `script_has_pattern`.

**Solution**:
- Option A: Keep derived columns but document as denormalized for performance.
- Option B: Remove and calculate on query (slower but correct).

---

## Framework Alignment

### THE PATTERN: Local First
```
Write local always → Sync to cloud selectively
(DuckDB/JSONL)       (BigQuery)
```

| Requirement | Status |
|-------------|--------|
| Data stays in DuckDB locally | ✓ Correct |
| No BigQuery writes for patterns | ✓ Correct |
| Script IDs registered to BigQuery | ⚠️ Maybe wrong |

**Issue**: The script registers `script_id` to BigQuery via `register_id()`. This violates "local first" for pattern extraction.

**Question for Jeremy**: Should script IDs be registered to BigQuery, or should this be purely local?

---

## Industry Standards Checklist

| Standard | Status | Issue |
|----------|--------|-------|
| Primary keys on all tables | ❌ | pattern_positions has none |
| Foreign key constraints | ❌ | None defined |
| NOT NULL on required columns | ❌ | Many missing |
| Proper indexing | ⚠️ | Partial |
| 1NF | ⚠️ | nesting_path violates |
| 2NF | ✓ | OK |
| 3NF | ⚠️ | Derived columns |
| Atomic transactions | ✓ | DuckDB handles |
| Hash-based deduplication | ✓ | Correct |

---

## Recommended Fixes

### Priority 1: Critical (Data Integrity)
1. Add PRIMARY KEY to `pattern_positions`
2. Add NOT NULL constraints
3. Add foreign key constraints (DuckDB supports these)

### Priority 2: High (Performance)
1. Add missing indexes
2. Remove duplicate `nesting_path` column (use path_elements instead)

### Priority 3: Medium (Standards)
1. Document or remove derived columns
2. Clarify BigQuery registration requirement

---

## Corrected Schema

```sql
-- Table 1: scripts
CREATE TABLE scripts (
    script_id TEXT PRIMARY KEY,
    canonical_name TEXT,
    file_path TEXT NOT NULL UNIQUE,
    file_hash TEXT NOT NULL,
    total_primitives INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    registered_at TIMESTAMP
);

-- Table 2: patterns (the universe of unique patterns)
CREATE TABLE patterns (
    pattern_id TEXT PRIMARY KEY,
    pattern_type TEXT NOT NULL,
    pattern_name TEXT NOT NULL,
    pattern_signature TEXT NOT NULL,
    pattern_hash TEXT NOT NULL UNIQUE,
    first_seen_in TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
-- Note: total_usage_count and script_count are derived; calculate from script_has_pattern

-- Table 3: script_has_pattern (many-to-many with counts)
CREATE TABLE script_has_pattern (
    script_id TEXT NOT NULL REFERENCES scripts(script_id),
    pattern_id TEXT NOT NULL REFERENCES patterns(pattern_id),
    count_in_script INT NOT NULL DEFAULT 1,
    first_line INT NOT NULL,
    PRIMARY KEY (script_id, pattern_id)
);

-- Table 4: pattern_positions (every occurrence with context)
CREATE TABLE pattern_positions (
    position_id TEXT PRIMARY KEY,
    script_id TEXT NOT NULL REFERENCES scripts(script_id),
    pattern_id TEXT NOT NULL REFERENCES patterns(pattern_id),
    line_number INT NOT NULL,
    col_offset INT NOT NULL,
    parent_pattern_id TEXT REFERENCES patterns(pattern_id),
    nesting_level INT NOT NULL,
    path_id TEXT REFERENCES pattern_paths(path_id),  -- Link to path instead of string
    UNIQUE (script_id, pattern_id, line_number, col_offset)
);

-- Table 5: pattern_paths (unique nesting chains)
CREATE TABLE pattern_paths (
    path_id TEXT PRIMARY KEY,
    path_signature TEXT NOT NULL,  -- Keep for readability
    path_hash TEXT NOT NULL UNIQUE,
    depth INT NOT NULL,
    desired TEXT NOT NULL DEFAULT 'unlabeled',
    reason TEXT
);
-- Note: frequency is derived; calculate from pattern_positions

-- Table 6: path_elements (ordered path components)
CREATE TABLE path_elements (
    path_id TEXT NOT NULL REFERENCES pattern_paths(path_id),
    position INT NOT NULL,
    pattern_id TEXT NOT NULL REFERENCES patterns(pattern_id),
    relationship_to_next TEXT,
    PRIMARY KEY (path_id, position)
);

-- Indexes for performance
CREATE INDEX idx_patterns_type ON patterns(pattern_type);
CREATE INDEX idx_patterns_name ON patterns(pattern_name);
CREATE INDEX idx_patterns_hash ON patterns(pattern_hash);
CREATE INDEX idx_positions_script ON pattern_positions(script_id);
CREATE INDEX idx_positions_pattern ON pattern_positions(pattern_id);
CREATE INDEX idx_positions_line ON pattern_positions(line_number);
CREATE INDEX idx_paths_hash ON pattern_paths(path_hash);
CREATE INDEX idx_paths_depth ON pattern_paths(depth);
CREATE INDEX idx_paths_desired ON pattern_paths(desired);
CREATE INDEX idx_scripts_hash ON scripts(file_hash);
```

---

## Decision Required

Before proceeding:

1. **BigQuery Registration**: Should script IDs be registered to BigQuery, or purely local?
2. **Derived Columns**: Keep `total_usage_count`, `script_count`, `frequency` for performance, or calculate on query?
3. **Migration**: Rebuild database with corrected schema, or patch existing?

---

*Analysis complete. Awaiting direction.*
