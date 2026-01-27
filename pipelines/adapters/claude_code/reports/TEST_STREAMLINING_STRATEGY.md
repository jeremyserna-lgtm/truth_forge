# Test Streamlining Strategy — Reduce Test Count by 60-70%

**Date**: 2026-01-27  
**Goal**: Reduce from 500-900 tests to **150-300 tests** while maintaining 90% coverage

---

## Current Problem

**Original Estimate**: 500-900 individual tests needed
- Too many repetitive tests
- Same patterns tested 17 times (one per stage)
- Duplicate test logic across similar functions

---

## Streamlining Strategies

### 1. Parameterized Tests for Common Patterns (60-70% reduction)

**Instead of**: 17 separate test files with 15-25 tests each = **255-425 tests**

**Use**: 1 parameterized test file covering common patterns = **~50-80 tests**

**Common Patterns Across All Stages**:
- ✅ `create_stage_N_table()` - Same pattern, different stage
- ✅ `main()` function - Same structure, different stage
- ✅ BigQuery client usage - Same pattern
- ✅ Error handling - Same patterns
- ✅ Input validation - Same patterns
- ✅ Logging - Same patterns

**Example**:
```python
@pytest.mark.parametrize("stage_num", range(17))
def test_stage_create_table(stage_num):
    # Test all stages with one function
    ...
```

**Savings**: ~200-350 tests → **50-80 tests**

---

### 2. Shared Test Fixtures (30-40% reduction)

**Instead of**: Each test file sets up its own mocks

**Use**: Centralized fixtures in `conftest.py`

**Already Done**: ✅ `conftest.py` exists with global mocks

**Additional Fixtures Needed**:
- `mock_bigquery_client` - Reusable across all stage tests
- `mock_stage_config` - Reusable configuration
- `sample_stage_data` - Reusable test data

**Savings**: ~50-100 duplicate setup lines → **Reusable fixtures**

---

### 3. Test Generators for Similar Functions (40-50% reduction)

**Instead of**: Individual tests for each `generate_*` function

**Use**: Generator that tests all `generate_*` functions

**Pattern**:
```python
def test_all_generate_functions():
    for stage in range(17):
        # Find all generate_* functions
        # Test them with same pattern
        ...
```

**Savings**: ~100-150 individual tests → **20-30 generator tests**

---

### 4. Focus on Unique Code Paths (Target 90% coverage efficiently)

**Strategy**: 
- Use parameterized tests for common patterns (covers 60-70% of code)
- Add targeted tests only for unique logic (covers remaining 20-30%)

**Example**:
- Stage 1: Has `discover_session_files()` - unique, needs specific test
- Stage 3: Has `generate_entity_id()` - unique, needs specific test
- Stage 9: Has `generate_embeddings_batch()` - unique, needs specific test
- But `create_stage_N_table()` - same pattern, use parameterized test

**Savings**: Focus on 20-30% unique code vs 100% individual tests

---

### 5. Integration Tests Instead of Unit Tests (10-20% reduction)

**Instead of**: Testing every function in isolation

**Use**: Integration tests that test multiple functions together

**Example**:
```python
def test_stage_5_full_flow():
    # Tests: create_table + process + load_to_bigquery
    # Instead of 3 separate tests
```

**Savings**: ~30-50 tests → **10-15 integration tests**

---

## Revised Test Count Estimate

### Original Estimate
- Stage Scripts: 300-400 tests
- Utility Scripts: 200-300 tests
- Shared Modules: 80-110 tests
- **Total**: 580-810 tests

### Streamlined Estimate

| Category | Original | Streamlined | Reduction |
|----------|----------|-------------|-----------|
| **Stage Scripts** | 300-400 | **80-120** | 70% reduction |
| **Utility Scripts** | 200-300 | **60-100** | 70% reduction |
| **Shared Modules** | 80-110 | **40-60** | 50% reduction |
| **TOTAL** | **580-810** | **180-280** | **70% reduction** |

### Breakdown

**Stage Scripts (80-120 tests)**:
- Parameterized common patterns: 50-80 tests
- Unique function tests: 30-40 tests

**Utility Scripts (60-100 tests)**:
- Parameterized patterns: 30-50 tests
- Unique logic tests: 30-50 tests

**Shared Modules (40-60 tests)**:
- Already well-structured: 40-60 tests

---

## Implementation Plan

### Phase 1: Create Parameterized Test Framework (Week 1)
1. ✅ Create `test_stage_common_patterns.py` with parameterized tests
2. Create `test_utility_common_patterns.py` for utility scripts
3. Create shared fixtures in `conftest.py`

### Phase 2: Replace Individual Tests (Week 1-2)
1. Replace stage-specific table creation tests with parameterized version
2. Replace stage-specific main() tests with parameterized version
3. Keep only unique function tests

### Phase 3: Add Targeted Tests (Week 2)
1. Add tests only for unique logic paths
2. Focus on achieving 90% coverage efficiently
3. Verify coverage with pytest-cov

---

## Expected Results

### Test Count
- **Before**: 580-810 tests
- **After**: 180-280 tests
- **Reduction**: 70% fewer tests

### Coverage
- **Target**: 90% coverage maintained
- **Efficiency**: Same coverage with 70% fewer tests

### Maintenance
- **Before**: 17 separate test files to maintain
- **After**: 3-5 parameterized test files + targeted tests
- **Benefit**: Easier to maintain, update once affects all stages

---

## Example: Before vs After

### Before (Individual Tests)
```python
# test_stage_1.py
def test_stage_1_create_table(): ...
def test_stage_1_main(): ...
def test_stage_1_process(): ...

# test_stage_2.py  
def test_stage_2_create_table(): ...
def test_stage_2_main(): ...
def test_stage_2_process(): ...

# ... 15 more files with same patterns
# Total: 17 files × 15 tests = 255 tests
```

### After (Parameterized Tests)
```python
# test_stage_common_patterns.py
@pytest.mark.parametrize("stage_num", range(17))
def test_stage_create_table(stage_num): ...

@pytest.mark.parametrize("stage_num", range(17))
def test_stage_main(stage_num): ...

# Total: 2 parameterized tests = 34 test cases (17 stages × 2 patterns)
# Plus: 30-40 unique function tests
# Total: ~70 tests instead of 255
```

---

## Benefits

1. **70% Fewer Tests**: 180-280 tests instead of 580-810
2. **Easier Maintenance**: Update once, affects all stages
3. **Faster Execution**: Parameterized tests run efficiently
4. **Same Coverage**: Still achieve 90% coverage
5. **Better Patterns**: Forces consistent patterns across stages

---

*Strategy complete. Implementation reduces test count by 70% while maintaining 90% coverage.*

**Status**: 📊 Strategy Defined | 🎯 Target: 180-280 tests | ⏳ Implementation: Ready to Start
